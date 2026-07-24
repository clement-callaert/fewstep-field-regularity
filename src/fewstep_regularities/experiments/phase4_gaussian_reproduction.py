"""Focused Phase 4 Gaussian reproduction."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from omegaconf import DictConfig, OmegaConf

from fewstep_regularities.analysis.propagation import (
    propagate_gaussian_moments,
    recover_affine_solver_map,
)
from fewstep_regularities.artifacts.manifest import ArtifactRecord, RunManifest
from fewstep_regularities.artifacts.writer import FilesystemArtifactWriter
from fewstep_regularities.distributions.gaussian import Gaussian, standard_gaussian
from fewstep_regularities.evaluation.gaussian_w2 import GaussianW2Evaluator
from fewstep_regularities.experiments.factories import (
    build_device,
    build_distribution,
    build_dtype,
    build_field,
    build_metric,
    build_path,
    build_solver,
)
from fewstep_regularities.fields.gaussian_affine import GaussianAffineField
from fewstep_regularities.utils.environment import (
    cuda_version,
    git_code_status,
    git_commit,
    gpu_name,
    package_lock_hash,
    python_version,
    software_environment_hash,
)
from fewstep_regularities.utils.hashing import sha256_file, sha256_text


def _repo_root(cfg: DictConfig) -> Path:
    configured = OmegaConf.select(cfg, "compute.repo_root")
    if configured:
        return Path(str(configured)).resolve()
    return Path(__file__).resolve().parents[3]


def _plain_mapping(node: Any, label: str) -> dict[str, Any]:
    value = OmegaConf.to_container(node, resolve=True)
    if not isinstance(value, dict):
        raise TypeError(f"{label} must resolve to a mapping")
    return {str(key): item for key, item in value.items()}


def validate_release_state(cfg: DictConfig, code_status: str) -> None:
    """Reject a dirty or unknown release-ready run."""
    release_ready = bool(cfg.artifact_policy.release_ready)
    release_required = bool(cfg.experiment.release_ready_required)
    allow_dirty = bool(cfg.experiment.allow_dirty_code)
    if release_required and not release_ready:
        raise ValueError("Phase 4 reproduction requires release-ready artifacts")
    if release_ready and code_status != "clean":
        raise RuntimeError("Release-ready Phase 4 run requires a clean worktree")
    if not allow_dirty and code_status != "clean":
        raise RuntimeError("Phase 4 reproduction requires a clean worktree")


def _validate_grid(cfg: DictConfig) -> None:
    if str(cfg.experiment.mode) != "phase4_gaussian_reproduction":
        raise ValueError("Unexpected Phase 4 mode")
    if int(cfg.experiment.phase) != 4:
        raise ValueError("Unexpected phase")
    if str(cfg.precision.dtype) != "float64":
        raise TypeError("Phase 4 reproduction requires float64")
    if str(cfg.compute.device) != "cpu":
        raise ValueError("Phase 4 reproduction requires CPU")
    if float(cfg.experiment.runtime.hard_stop_minutes) > 45.0:
        raise ValueError("Run 1 hard stop exceeds 45 minutes")

    dimensions = [int(value) for value in cfg.experiment.dimensions]
    nfe_budgets = [int(value) for value in cfg.experiment.nfe_budgets]
    targets = [_plain_mapping(value, "target") for value in cfg.experiment.targets]
    paths = [_plain_mapping(value, "path") for value in cfg.experiment.paths]
    solvers = [_plain_mapping(value, "solver") for value in cfg.experiment.solvers]
    if dimensions != [2, 8]:
        raise ValueError("Run 1 dimensions must be 2 and 8")
    if nfe_budgets != [8, 16, 32]:
        raise ValueError("Run 1 NFE budgets must be 8, 16, and 32")
    if [item["name"] for item in targets] != [
        "anisotropic_gaussian",
        "low_rank_gaussian",
    ]:
        raise ValueError("Run 1 target list changed")
    if [item["name"] for item in paths] != ["linear", "variance_preserving"]:
        raise ValueError("Run 1 path list changed")
    if [item["name"] for item in solvers] != ["euler", "heun", "rk4"]:
        raise ValueError("Run 1 solver list changed")
    for solver_cfg in solvers:
        solver = build_solver(solver_cfg)
        configured = int(solver_cfg["evaluations_per_step"])
        if configured != solver.evals_per_step:
            raise ValueError("Configured solver NFE count is incorrect")
        if any(nfe % solver.evals_per_step != 0 for nfe in nfe_budgets):
            raise ValueError("NFE budget is incompatible with a solver")
    expected = (
        len(dimensions) * len(targets) * len(paths) * len(solvers) * len(nfe_budgets)
    )
    if expected != 72:
        raise ValueError("Run 1 grid must contain 72 endpoint configurations")
    if int(cfg.experiment.expected_counts.endpoint_configurations) != expected:
        raise ValueError("Expected endpoint count does not match the grid")


def _validate_inputs(cfg: DictConfig, root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    inputs = _plain_mapping(cfg.experiment.inputs, "inputs")
    for item in inputs.values():
        if not isinstance(item, dict):
            raise TypeError("Each input must be a mapping")
        artifact_id = str(item["artifact_id"])
        path = Path(str(item["path"]))
        if not path.is_absolute():
            path = (root / path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Missing Phase 4 input: {path}")
        actual = sha256_file(path)
        if actual != str(item["sha256"]):
            raise ValueError(f"Input checksum mismatch: {artifact_id}")
        hashes[artifact_id] = actual
    return hashes


def _load_phase3_rows(
    cfg: DictConfig, root: Path
) -> dict[tuple[Any, ...], dict[str, Any]]:
    gate_cfg = cfg.experiment.inputs.phase3_gate
    gate_path = Path(str(gate_cfg.path))
    if not gate_path.is_absolute():
        gate_path = (root / gate_path).resolve()
    payload = json.loads(gate_path.read_text(encoding="utf-8"))
    index: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in payload["observations"]:
        if row["target_family"] not in {
            "anisotropic_gaussian",
            "low_rank_gaussian",
        }:
            continue
        if row["metric_name"] != "averaged_squared_lipschitz_proxy":
            continue
        key = (
            str(row["target_family"]),
            int(row["dim"]),
            str(row["path"]),
            str(row["solver"]),
            int(row["nfe"]),
        )
        if key in index:
            raise ValueError(f"Duplicate Phase 3 Gaussian row: {key}")
        index[key] = row
    if len(index) != 72:
        raise ValueError("Phase 3 comparison input must contain 72 Gaussian rows")
    return index


def _artifact_record(
    *,
    artifact_id: str,
    run_id: str,
    git: str,
    config_hash: str,
    code_status: str,
    environment_hash: str,
    seeds: list[int],
    path: Path,
    timestamp: str,
    input_hashes: dict[str, str],
) -> ArtifactRecord:
    return ArtifactRecord(
        artifact_id=artifact_id,
        producing_run_id=run_id,
        git_commit=git,
        config_hash=config_hash,
        code_status=code_status,
        input_artifact_hashes=input_hashes,
        creation_timestamp=timestamp,
        software_environment_hash=environment_hash,
        random_seeds=seeds,
        output_checksum="",
        path=str(path),
        kind="table",
    )


def _output_path(run_dir: Path, output_cfg: Any) -> Path:
    configured = Path(str(output_cfg.path))
    if configured.name not in {
        "results.json",
        "phase3_comparison.json",
        "validation.json",
    }:
        raise ValueError("Unexpected Phase 4 output filename")
    return run_dir / configured.name


def _row_diagnostics(
    matrix: torch.Tensor,
    covariance: torch.Tensor,
) -> dict[str, float | bool]:
    eigenvalues = torch.linalg.eigvalsh(covariance)
    symmetry = torch.linalg.matrix_norm(covariance - covariance.T, ord="fro")
    return {
        "matrix_condition_number": float(torch.linalg.cond(matrix).item()),
        "covariance_symmetry_residual": float(symmetry.item()),
        "minimum_covariance_eigenvalue": float(eigenvalues.min().item()),
        "maximum_covariance_eigenvalue": float(eigenvalues.max().item()),
        "covariance_is_psd": bool(eigenvalues.min().item() >= -1e-12),
    }


def run_phase4_gaussian_reproduction(cfg: DictConfig) -> Path:
    """Run the focused clean Gaussian reproduction."""
    start = datetime.now(UTC)
    root = _repo_root(cfg)
    _validate_grid(cfg)
    code_status = git_code_status(root)
    validate_release_state(cfg, code_status)
    input_hashes = _validate_inputs(cfg, root)
    phase3_rows = _load_phase3_rows(cfg, root)

    run_id = str(cfg.experiment.run_id)
    output_root = Path(str(cfg.artifact_policy.output_dir))
    if not output_root.is_absolute():
        output_root = (root / output_root).resolve()
    run_dir = output_root / run_id
    if (run_dir / "manifest.json").exists():
        raise FileExistsError(f"Refusing to overwrite completed run {run_dir}")
    if run_dir.exists() and any(run_dir.iterdir()):
        raise FileExistsError(f"Refusing to use nonempty run directory {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)

    unresolved_path = run_dir / "unresolved_config.yaml"
    resolved_path = run_dir / "resolved_config.yaml"
    unresolved_path.write_text(OmegaConf.to_yaml(cfg, resolve=False), encoding="utf-8")
    resolved_text = OmegaConf.to_yaml(cfg, resolve=True)
    resolved_path.write_text(resolved_text, encoding="utf-8")
    config_hash = sha256_text(resolved_text)

    dtype = build_dtype(cfg)
    device = build_device(cfg)
    geometry_seed = int(cfg.experiment.target_geometry_seed)
    evaluator = GaussianW2Evaluator(dtype=dtype)
    comparison_tolerance = float(cfg.experiment.comparison.absolute_tolerance)
    result_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []

    dimensions = [int(value) for value in cfg.experiment.dimensions]
    target_configs = [
        _plain_mapping(value, "target") for value in cfg.experiment.targets
    ]
    path_configs = [_plain_mapping(value, "path") for value in cfg.experiment.paths]
    solver_configs = [
        _plain_mapping(value, "solver") for value in cfg.experiment.solvers
    ]
    nfe_budgets = [int(value) for value in cfg.experiment.nfe_budgets]
    for dim in dimensions:
        for target_cfg in target_configs:
            generator = torch.Generator(device=device).manual_seed(geometry_seed)
            source = standard_gaussian(dim, dtype=dtype, device=device)
            target = build_distribution(
                target_cfg,
                dim,
                dtype,
                device,
                generator=generator,
            )
            if not isinstance(target, Gaussian):
                raise TypeError("Phase 4 reproduction accepts Gaussian targets only")
            for path_cfg in path_configs:
                path = build_path(path_cfg, source, target, dtype)
                field = build_field(path_cfg, source, target, path, dtype)
                if not isinstance(field, GaussianAffineField):
                    raise TypeError("Phase 4 reproduction requires an affine field")
                metric = build_metric(cfg.experiment.metric, dtype)
                metric_result = metric.compute(field)
                endpoint_time = torch.tensor(1.0, dtype=dtype, device=device)
                exact_mean = field.mean_t(endpoint_time)
                exact_covariance = field.cov_t(endpoint_time)
                endpoint_check = evaluator.compute(
                    {"mean": exact_mean, "covariance": exact_covariance},
                    {"mean": target.mean(), "covariance": target.covariance()},
                )
                for solver_cfg in solver_configs:
                    solver_name = str(solver_cfg["name"])
                    for nfe in nfe_budgets:
                        solver = build_solver(solver_cfg)
                        affine_map = recover_affine_solver_map(
                            field,
                            solver,
                            dim=dim,
                            dtype=dtype,
                            device=device,
                            requested_nfe=nfe,
                        )
                        mean, covariance = propagate_gaussian_moments(
                            affine_map,
                            source.mean(),
                            source.covariance(),
                        )
                        evaluation = evaluator.compute(
                            {"mean": mean, "covariance": covariance},
                            {"mean": target.mean(), "covariance": target.covariance()},
                        )
                        key = (
                            str(target_cfg["name"]),
                            dim,
                            str(path_cfg["name"]),
                            solver_name,
                            nfe,
                        )
                        phase3 = phase3_rows[key]
                        error = float(evaluation.primary.item())
                        metric_value = float(metric_result.value.item())
                        error_delta = error - float(phase3["error"])
                        metric_delta = metric_value - float(phase3["metric_value"])
                        diagnostics = _row_diagnostics(
                            affine_map.matrix,
                            covariance,
                        )
                        result_rows.append(
                            {
                                "target_family": str(target_cfg["name"]),
                                "dim": dim,
                                "path": str(path_cfg["name"]),
                                "solver": solver_name,
                                "nfe": nfe,
                                "actual_nfe": affine_map.actual_nfe,
                                "n_steps": affine_map.n_steps,
                                "affine_matrix": affine_map.matrix.tolist(),
                                "affine_offset": affine_map.offset.tolist(),
                                "mean": mean.tolist(),
                                "covariance": covariance.tolist(),
                                "gaussian_w2": error,
                                "gaussian_w2_is_exact_from_moments": True,
                                "baseline_metric": metric_value,
                                "baseline_metric_is_exact": bool(
                                    metric_result.is_exact
                                ),
                                "continuous_endpoint_w2": float(
                                    endpoint_check.primary.item()
                                ),
                                "wall_clock_s": affine_map.wall_clock_s,
                                **diagnostics,
                            }
                        )
                        comparison_rows.append(
                            {
                                "target_family": str(target_cfg["name"]),
                                "dim": dim,
                                "path": str(path_cfg["name"]),
                                "solver": solver_name,
                                "nfe": nfe,
                                "phase3_error": float(phase3["error"]),
                                "phase4_error": error,
                                "error_delta": error_delta,
                                "phase3_metric": float(phase3["metric_value"]),
                                "phase4_metric": metric_value,
                                "metric_delta": metric_delta,
                                "within_tolerance": bool(
                                    abs(error_delta) <= comparison_tolerance
                                    and abs(metric_delta) <= comparison_tolerance
                                ),
                            }
                        )

    if len(result_rows) != 72 or len(comparison_rows) != 72:
        raise RuntimeError("Phase 4 reproduction produced an unexpected row count")
    equal_nfe = all(row["nfe"] == row["actual_nfe"] for row in result_rows)
    covariance_valid = all(
        row["covariance_is_psd"] and float(row["covariance_symmetry_residual"]) <= 1e-12
        for row in result_rows
    )
    comparison_valid = all(row["within_tolerance"] for row in comparison_rows)
    validation = {
        "row_count": len(result_rows),
        "expected_row_count": 72,
        "equal_nfe_validated": equal_nfe,
        "covariance_validated": covariance_valid,
        "phase3_comparison_validated": comparison_valid,
        "comparison_absolute_tolerance": comparison_tolerance,
        "all_checks_passed": equal_nfe and covariance_valid and comparison_valid,
    }
    if not validation["all_checks_passed"]:
        raise RuntimeError("Phase 4 reproduction validation failed")

    writer = FilesystemArtifactWriter()
    git = git_commit(root)
    environment_hash = software_environment_hash()
    seeds = [int(value) for value in cfg.experiment.seeds]
    timestamp = datetime.now(UTC).isoformat()
    outputs = cfg.experiment.outputs
    results_path = _output_path(run_dir, outputs.results)
    comparison_path = _output_path(run_dir, outputs.comparison)
    validation_path = _output_path(run_dir, outputs.validation)
    saved_results = writer.save_table(
        {
            "quantity_status": {
                "gaussian_w2": "exact from analytical numerical-map moments",
                "baseline_metric": "numerical time quadrature",
            },
            "rows": result_rows,
        },
        results_path,
        _artifact_record(
            artifact_id=str(outputs.results.artifact_id),
            run_id=run_id,
            git=git,
            config_hash=config_hash,
            code_status=code_status,
            environment_hash=environment_hash,
            seeds=seeds,
            path=results_path,
            timestamp=timestamp,
            input_hashes=input_hashes,
        ),
    )
    saved_comparison = writer.save_table(
        {
            "source_artifact_id": str(cfg.experiment.inputs.phase3_gate.artifact_id),
            "exact_row_selection": {
                "target_families": [
                    "anisotropic_gaussian",
                    "low_rank_gaussian",
                ],
                "metric_name": "averaged_squared_lipschitz_proxy",
                "dimensions": [2, 8],
                "paths": ["linear", "variance_preserving"],
                "solvers": ["euler", "heun", "rk4"],
                "nfe_budgets": [8, 16, 32],
            },
            "rows": comparison_rows,
        },
        comparison_path,
        _artifact_record(
            artifact_id=str(outputs.comparison.artifact_id),
            run_id=run_id,
            git=git,
            config_hash=config_hash,
            code_status=code_status,
            environment_hash=environment_hash,
            seeds=seeds,
            path=comparison_path,
            timestamp=timestamp,
            input_hashes=input_hashes,
        ),
    )
    saved_validation = writer.save_table(
        validation,
        validation_path,
        _artifact_record(
            artifact_id=str(outputs.validation.artifact_id),
            run_id=run_id,
            git=git,
            config_hash=config_hash,
            code_status=code_status,
            environment_hash=environment_hash,
            seeds=seeds,
            path=validation_path,
            timestamp=timestamp,
            input_hashes=input_hashes,
        ),
    )
    end = datetime.now(UTC)
    manifest = RunManifest(
        run_id=run_id,
        git_commit=git,
        config_hash=config_hash,
        code_status=code_status,
        software_environment_hash=environment_hash,
        random_seeds=seeds,
        start_time=start.isoformat(),
        end_time=end.isoformat(),
        runtime_s=(end - start).total_seconds(),
        artifact_manifest=[
            saved_results.to_dict(),
            saved_comparison.to_dict(),
            saved_validation.to_dict(),
        ],
        resolved_config_path=str(resolved_path),
        unresolved_config_path=str(unresolved_path),
        command_line=" ".join(sys.argv),
        python_version=python_version(),
        package_lock_hash=package_lock_hash(root),
        cuda_version=cuda_version(),
        gpu_name=gpu_name(),
        release_ready=bool(cfg.artifact_policy.release_ready),
        extras={
            "mode": "phase4_gaussian_reproduction",
            "phase": 4,
            "precision": str(cfg.precision.dtype),
            "device": str(cfg.compute.device),
            "input_artifacts": input_hashes,
            "expected_runtime_minutes": float(cfg.experiment.runtime.expected_minutes),
            "hard_stop_minutes": float(cfg.experiment.runtime.hard_stop_minutes),
        },
    )
    manifest_path = run_dir / "manifest.json"
    writer.save_manifest(manifest, manifest_path)
    return manifest_path
