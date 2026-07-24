"""Focused Phase 4 affine audit runs."""

from __future__ import annotations

import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import mpmath
import torch
from omegaconf import DictConfig, OmegaConf

from fewstep_regularities.analysis.affine_flow import (
    scalar_affine_quantities,
    scalar_drift,
    scalar_variance,
    sorted_covariance_eigenvalues,
)
from fewstep_regularities.analysis.local_error import (
    evaluations_per_step,
    leading_local_coefficient,
    propagate_scalar_mode,
)
from fewstep_regularities.analysis.precision import high_precision_gaussian_w2
from fewstep_regularities.artifacts.manifest import ArtifactRecord, RunManifest
from fewstep_regularities.artifacts.writer import FilesystemArtifactWriter
from fewstep_regularities.distributions.gaussian import Gaussian, standard_gaussian
from fewstep_regularities.experiments.factories import (
    build_distribution,
)
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


def _plain(node: Any, label: str) -> dict[str, Any]:
    value = OmegaConf.to_container(node, resolve=True)
    if not isinstance(value, dict):
        raise TypeError(f"{label} must resolve to a mapping")
    return {str(key): item for key, item in value.items()}


def _validate_run_state(cfg: DictConfig, root: Path) -> str:
    if int(cfg.experiment.phase) != 4:
        raise ValueError("Unexpected phase")
    if str(cfg.precision.dtype) != "float64":
        raise TypeError("Phase 4 affine audit requires float64")
    if str(cfg.compute.device) != "cpu":
        raise ValueError("Phase 4 affine audit requires CPU")
    code_status = git_code_status(root)
    if bool(cfg.artifact_policy.release_ready) and code_status != "clean":
        raise RuntimeError("Release-ready Phase 4 run requires a clean worktree")
    if not bool(cfg.experiment.allow_dirty_code) and code_status != "clean":
        raise RuntimeError("Phase 4 affine audit requires a clean worktree")
    hard_stop = float(cfg.experiment.runtime.hard_stop_minutes)
    if hard_stop > 120.0:
        raise ValueError("Phase 4 hard stop exceeds two hours")
    return code_status


def _input_paths(
    cfg: DictConfig,
    root: Path,
) -> tuple[dict[str, Path], dict[str, str]]:
    paths: dict[str, Path] = {}
    hashes: dict[str, str] = {}
    for name, item in _plain(cfg.experiment.inputs, "inputs").items():
        if not isinstance(item, dict):
            raise TypeError("Each input must be a mapping")
        path = Path(str(item["path"]))
        if not path.is_absolute():
            path = (root / path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Missing Phase 4 input: {path}")
        artifact_id = str(item["artifact_id"])
        actual = sha256_file(path)
        expected = item.get("sha256")
        if expected is not None and actual != str(expected):
            raise ValueError(f"Input checksum mismatch: {artifact_id}")
        paths[name] = path
        hashes[artifact_id] = actual
    return paths, hashes


def _target_config(family: str, perturbation: float = 0.0) -> dict[str, Any]:
    if family == "anisotropic_gaussian":
        return {
            "name": family,
            "anisotropy": 4.0 * (1.0 + perturbation),
        }
    if family == "low_rank_gaussian":
        return {
            "name": family,
            "rank": 2,
            "noise_variance": 0.05 * (1.0 + perturbation),
        }
    raise ValueError(f"Unsupported family {family!r}")


def _eigenvalues(
    family: str,
    dim: int,
    geometry_seed: int,
    *,
    perturbation: float = 0.0,
) -> list[float]:
    dtype = torch.float64
    device = torch.device("cpu")
    source = standard_gaussian(dim, dtype=dtype, device=device)
    del source
    generator = torch.Generator(device=device).manual_seed(geometry_seed)
    target = build_distribution(
        _target_config(family, perturbation),
        dim,
        dtype,
        device,
        generator=generator,
    )
    if not isinstance(target, Gaussian):
        raise TypeError("Phase 4 affine audit accepts Gaussian targets only")
    return sorted_covariance_eigenvalues(target.covariance())


def _load_run1_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != 72:
        raise ValueError("Run 1 input must contain 72 rows")
    return [dict(row) for row in rows]


def _precision_table(
    cfg: DictConfig,
    input_paths: dict[str, Path],
) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = _load_run1_rows(input_paths["run1_results"])
    digits = int(cfg.experiment.decimal_digits)
    geometry_seed = int(cfg.experiment.target_geometry_seed)
    output_rows: list[dict[str, Any]] = []
    for row in rows:
        eigenvalues = _eigenvalues(
            str(row["target_family"]),
            int(row["dim"]),
            geometry_seed,
        )
        reference = high_precision_gaussian_w2(
            str(row["path"]),
            str(row["solver"]),
            eigenvalues,
            int(row["nfe"]),
            decimal_digits=digits,
        )
        float_reference = float(reference)
        float64_error = float(row["gaussian_w2"])
        output_rows.append(
            {
                "target_family": row["target_family"],
                "dim": row["dim"],
                "path": row["path"],
                "solver": row["solver"],
                "nfe": row["nfe"],
                "float64_gaussian_w2": float64_error,
                "high_precision_gaussian_w2": mpmath.nstr(reference, digits),
                "absolute_reference_delta": abs(float64_error - float_reference),
                "target_eigenvalues": eigenvalues,
                "decimal_digits": digits,
            }
        )
    maximum_delta = max(row["absolute_reference_delta"] for row in output_rows)
    validation = {
        "row_count": len(output_rows),
        "decimal_digits": digits,
        "maximum_absolute_reference_delta": maximum_delta,
        "reference_tolerance": float(cfg.experiment.reference_tolerance),
        "all_checks_passed": maximum_delta <= float(cfg.experiment.reference_tolerance),
    }
    return {"rows": output_rows}, validation


def _decomposition_table(
    cfg: DictConfig,
    input_paths: dict[str, Path],
) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = _load_run1_rows(input_paths["run1_results"])
    geometry_seed = int(cfg.experiment.target_geometry_seed)
    output_rows: list[dict[str, Any]] = []
    maximum_delta = 0.0
    for row in rows:
        eigenvalues = _eigenvalues(
            str(row["target_family"]),
            int(row["dim"]),
            geometry_seed,
        )
        modes: list[dict[str, Any]] = []
        squared_contributions: list[float] = []
        for index, eigenvalue in enumerate(eigenvalues):
            propagation = propagate_scalar_mode(
                str(row["path"]),
                str(row["solver"]),
                eigenvalue,
                int(row["nfe"]),
            )
            standard_deviation_error = abs(propagation.factor) - math.sqrt(eigenvalue)
            squared = standard_deviation_error**2
            squared_contributions.append(squared)
            modes.append(
                {
                    "mode_index": index,
                    "target_eigenvalue": eigenvalue,
                    "numerical_factor": propagation.factor,
                    "exact_factor": propagation.exact_factor,
                    "covariance_eigenvalue": propagation.factor**2,
                    "covariance_eigenvalue_error": propagation.factor**2 - eigenvalue,
                    "w2_squared_contribution": squared,
                    "signed_local_log_defect_sum": sum(propagation.local_log_defects),
                    "absolute_local_log_defect_sum": sum(
                        abs(value) for value in propagation.local_log_defects
                    ),
                    "local_log_defects": list(propagation.local_log_defects),
                    "transported_local_contributions": list(
                        propagation.transported_local_contributions
                    ),
                    "transported_contribution_sum": sum(
                        propagation.transported_local_contributions
                    ),
                }
            )
        reconstructed = math.sqrt(sum(squared_contributions))
        delta = abs(reconstructed - float(row["gaussian_w2"]))
        maximum_delta = max(maximum_delta, delta)
        dominant = max(
            range(len(modes)), key=lambda index: squared_contributions[index]
        )
        output_rows.append(
            {
                "target_family": row["target_family"],
                "dim": row["dim"],
                "path": row["path"],
                "solver": row["solver"],
                "nfe": row["nfe"],
                "mean_error": 0.0,
                "run1_gaussian_w2": row["gaussian_w2"],
                "reconstructed_gaussian_w2": reconstructed,
                "reconstruction_delta": delta,
                "dominant_mode_index": dominant,
                "dominant_mode_fraction": squared_contributions[dominant]
                / max(sum(squared_contributions), 1e-300),
                "modes": modes,
            }
        )
    tolerance = float(cfg.experiment.reconstruction_tolerance)
    validation = {
        "row_count": len(output_rows),
        "maximum_reconstruction_delta": maximum_delta,
        "reconstruction_tolerance": tolerance,
        "all_checks_passed": maximum_delta <= tolerance,
    }
    return {"rows": output_rows}, validation


def _trapezoid(values: list[float], step_size: float) -> float:
    return step_size * (0.5 * values[0] + sum(values[1:-1]) + 0.5 * values[-1])


def _path_diagnostics(
    path_name: str,
    eigenvalues: list[float],
    n_time: int,
) -> dict[str, float]:
    times = [index / (n_time - 1) for index in range(n_time)]
    step_size = 1.0 / (n_time - 1)
    jacobian_norm: list[float] = []
    temporal_norm: list[float] = []
    material_norm: list[float] = []
    expected_material_norm: list[float] = []
    for time in times:
        quantities = [
            scalar_affine_quantities(path_name, eigenvalue, time)
            for eigenvalue in eigenvalues
        ]
        jacobian_norm.append(max(abs(value.drift) for value in quantities))
        temporal_norm.append(max(abs(value.drift_derivative) for value in quantities))
        material = [value.drift_derivative + value.drift**2 for value in quantities]
        material_norm.append(max(abs(value) for value in material))
        expected_material_norm.append(
            math.sqrt(
                sum(
                    material[index] ** 2
                    * scalar_variance(path_name, eigenvalues[index], time)
                    for index in range(len(eigenvalues))
                )
            )
        )
    return {
        "integrated_squared_jacobian_norm": _trapezoid(
            [value**2 for value in jacobian_norm],
            step_size,
        ),
        "maximum_temporal_jacobian_norm": max(temporal_norm),
        "integrated_temporal_jacobian_norm": _trapezoid(
            temporal_norm,
            step_size,
        ),
        "integrated_material_derivative_norm": _trapezoid(
            material_norm,
            step_size,
        ),
        "integrated_expected_material_derivative_norm": _trapezoid(
            expected_material_norm,
            step_size,
        ),
    }


def _solver_proxy(
    path_name: str,
    solver_name: str,
    eigenvalues: list[float],
    nfe: int,
) -> dict[str, float]:
    evals = evaluations_per_step(solver_name)
    n_steps = nfe // evals
    step_size = 1.0 / n_steps
    leading_errors: list[float] = []
    exact_local_errors: list[float] = []
    endpoint_errors: list[float] = []
    for eigenvalue in eigenvalues:
        leading = 0.0
        for step in range(n_steps):
            time = step * step_size
            coefficient = leading_local_coefficient(
                path_name,
                solver_name,
                eigenvalue,
                time,
            )
            order = {"euler": 2, "heun": 3, "rk4": 5}[solver_name]
            remaining = math.sqrt(
                eigenvalue
                / scalar_variance(
                    path_name,
                    eigenvalue,
                    time + step_size,
                )
            )
            leading += coefficient * step_size**order * remaining
        propagation = propagate_scalar_mode(
            path_name,
            solver_name,
            eigenvalue,
            nfe,
        )
        exact_local = sum(abs(value) for value in propagation.local_log_defects)
        leading_errors.append(leading)
        exact_local_errors.append(exact_local)
        endpoint_errors.append(abs(propagation.factor) - math.sqrt(eigenvalue))
    return {
        "leading_local_error_proxy": math.sqrt(
            sum(value**2 for value in leading_errors)
        ),
        "absolute_local_log_defect_proxy": math.sqrt(
            sum(value**2 for value in exact_local_errors)
        ),
        "eigenmode_endpoint_reconstruction": math.sqrt(
            sum(value**2 for value in endpoint_errors)
        ),
    }


def _diagnostic_table(
    cfg: DictConfig,
    input_paths: dict[str, Path],
) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = _load_run1_rows(input_paths["run1_results"])
    geometry_seed = int(cfg.experiment.target_geometry_seed)
    n_time = int(cfg.experiment.n_time)
    path_cache: dict[tuple[str, int, str], dict[str, float]] = {}
    output_rows: list[dict[str, Any]] = []
    maximum_reconstruction_delta = 0.0
    for row in rows:
        family = str(row["target_family"])
        dim = int(row["dim"])
        path_name = str(row["path"])
        eigenvalues = _eigenvalues(family, dim, geometry_seed)
        cache_key = (family, dim, path_name)
        if cache_key not in path_cache:
            path_cache[cache_key] = _path_diagnostics(
                path_name,
                eigenvalues,
                n_time,
            )
        solver_values = _solver_proxy(
            path_name,
            str(row["solver"]),
            eigenvalues,
            int(row["nfe"]),
        )
        reconstruction_delta = abs(
            solver_values["eigenmode_endpoint_reconstruction"]
            - float(row["gaussian_w2"])
        )
        maximum_reconstruction_delta = max(
            maximum_reconstruction_delta,
            reconstruction_delta,
        )
        output_rows.append(
            {
                "target_family": family,
                "dim": dim,
                "path": path_name,
                "solver": row["solver"],
                "nfe": row["nfe"],
                "gaussian_w2": row["gaussian_w2"],
                "baseline_metric": row["baseline_metric"],
                **path_cache[cache_key],
                **solver_values,
                "reconstruction_delta": reconstruction_delta,
                "diagnostic_status": "post-hoc",
            }
        )
    tolerance = float(cfg.experiment.reconstruction_tolerance)
    validation = {
        "row_count": len(output_rows),
        "maximum_reconstruction_delta": maximum_reconstruction_delta,
        "reconstruction_tolerance": tolerance,
        "all_checks_passed": maximum_reconstruction_delta <= tolerance,
    }
    return {"rows": output_rows}, validation


def _baseline_metric(
    path_name: str,
    eigenvalues: list[float],
    n_time: int = 24,
) -> float:
    times = [index / (n_time - 1) for index in range(n_time)]
    values = [
        max(
            abs(scalar_drift(path_name, eigenvalue, time)) for eigenvalue in eigenvalues
        )
        ** 2
        for time in times
    ]
    return _trapezoid(values, 1.0 / (n_time - 1))


def _robustness_table(
    cfg: DictConfig,
) -> tuple[dict[str, Any], dict[str, Any]]:
    geometry_seed = int(cfg.experiment.target_geometry_seed)
    perturbations = [float(value) for value in cfg.experiment.perturbations]
    primary_nfe = [int(value) for value in cfg.experiment.primary_nfe_budgets]
    optional_nfe = [int(value) for value in cfg.experiment.optional_nfe_budgets]
    rows: list[dict[str, Any]] = []
    for family in ["anisotropic_gaussian", "low_rank_gaussian"]:
        for dim in [2, 8]:
            for perturbation in perturbations:
                eigenvalues = _eigenvalues(
                    family,
                    dim,
                    geometry_seed,
                    perturbation=perturbation,
                )
                budgets = (
                    primary_nfe if perturbation != 0.0 else primary_nfe + optional_nfe
                )
                for path_name in ["linear", "variance_preserving"]:
                    metric = _baseline_metric(path_name, eigenvalues)
                    for solver_name in ["euler", "heun", "rk4"]:
                        for nfe in budgets:
                            factors = [
                                propagate_scalar_mode(
                                    path_name,
                                    solver_name,
                                    eigenvalue,
                                    nfe,
                                ).factor
                                for eigenvalue in eigenvalues
                            ]
                            error = math.sqrt(
                                sum(
                                    (abs(factor) - math.sqrt(eigenvalue)) ** 2
                                    for factor, eigenvalue in zip(
                                        factors,
                                        eigenvalues,
                                        strict=True,
                                    )
                                )
                            )
                            rows.append(
                                {
                                    "target_family": family,
                                    "dim": dim,
                                    "perturbation": perturbation,
                                    "path": path_name,
                                    "solver": solver_name,
                                    "nfe": nfe,
                                    "gaussian_w2": error,
                                    "baseline_metric": metric,
                                }
                            )
    groups: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = {}
    for row in rows:
        key = (
            row["target_family"],
            row["dim"],
            row["perturbation"],
            row["solver"],
            row["nfe"],
        )
        groups.setdefault(key, {})[str(row["path"])] = row
    preference_rows: list[dict[str, Any]] = []
    for key, values in sorted(groups.items()):
        linear = values["linear"]
        vp = values["variance_preserving"]
        metric_sign = math.copysign(
            1.0,
            float(linear["baseline_metric"]) - float(vp["baseline_metric"]),
        )
        error_sign = math.copysign(
            1.0,
            float(linear["gaussian_w2"]) - float(vp["gaussian_w2"]),
        )
        preference_rows.append(
            {
                "target_family": key[0],
                "dim": key[1],
                "perturbation": key[2],
                "solver": key[3],
                "nfe": key[4],
                "preferred_path": (
                    "linear"
                    if float(linear["gaussian_w2"]) < float(vp["gaussian_w2"])
                    else "variance_preserving"
                ),
                "inversion": metric_sign * error_sign < 0.0,
                "inversion_margin": abs(
                    float(linear["gaussian_w2"]) - float(vp["gaussian_w2"])
                ),
            }
        )
    validation = {
        "row_count": len(rows),
        "preference_block_count": len(preference_rows),
        "all_errors_finite": all(
            math.isfinite(float(row["gaussian_w2"])) for row in rows
        ),
        "low_rank_preference_pattern_stable": all(
            (
                row["preferred_path"] == "variance_preserving"
                if row["solver"] == "euler"
                else row["preferred_path"] == "linear"
            )
            for row in preference_rows
            if row["target_family"] == "low_rank_gaussian"
        ),
    }
    validation["all_checks_passed"] = bool(
        validation["all_errors_finite"]
        and validation["low_rank_preference_pattern_stable"]
    )
    return {"rows": rows, "preferences": preference_rows}, validation


def _final_table(
    input_paths: dict[str, Path],
) -> tuple[dict[str, Any], dict[str, Any]]:
    input_validations: dict[str, dict[str, Any]] = {}
    all_passed = True
    for name, path in input_paths.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        input_validations[name] = payload
        if path.name == "validation.json":
            all_passed = all_passed and bool(payload.get("all_checks_passed"))
    table = {
        "input_validations": input_validations,
        "focused_validation_passed": all_passed,
        "phase4_success_requires_scientific_review": True,
        "claim_status_policy": "No new claim is supported from one run.",
    }
    validation = {
        "input_count": len(input_paths),
        "all_input_validations_passed": all_passed,
        "all_checks_passed": all_passed,
    }
    return table, validation


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


def run_phase4_affine_audit(cfg: DictConfig) -> Path:
    """Run one immutable focused Phase 4 affine audit."""
    start = datetime.now(UTC)
    root = _repo_root(cfg)
    code_status = _validate_run_state(cfg, root)
    input_paths, input_hashes = _input_paths(cfg, root)
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

    audit_kind = str(cfg.experiment.audit_kind)
    if audit_kind == "precision":
        table, validation = _precision_table(cfg, input_paths)
    elif audit_kind == "decomposition":
        table, validation = _decomposition_table(cfg, input_paths)
    elif audit_kind == "diagnostics":
        table, validation = _diagnostic_table(cfg, input_paths)
    elif audit_kind == "robustness":
        table, validation = _robustness_table(cfg)
    elif audit_kind == "final_validation":
        table, validation = _final_table(input_paths)
    else:
        raise ValueError(f"Unsupported Phase 4 audit kind {audit_kind!r}")
    if not bool(validation["all_checks_passed"]):
        raise RuntimeError(f"Phase 4 {audit_kind} validation failed")

    writer = FilesystemArtifactWriter()
    git = git_commit(root)
    environment_hash = software_environment_hash()
    seeds = [int(value) for value in cfg.experiment.seeds]
    timestamp = datetime.now(UTC).isoformat()
    table_path = run_dir / "table.json"
    validation_path = run_dir / "validation.json"
    common_metadata = {
        "source_run_ids": [
            str(item["artifact_id"]).split(":")[0]
            for item in _plain(cfg.experiment.inputs, "inputs").values()
            if isinstance(item, dict)
        ],
        "exact_row_selection": _plain(
            cfg.experiment.row_selection,
            "row_selection",
        ),
        "creation_script": (
            "src/fewstep_regularities/experiments/phase4_affine_audit.py"
        ),
        "analysis_status": ("registered" if audit_kind == "precision" else "post-hoc"),
    }
    table = {**common_metadata, **table}
    saved_table = writer.save_table(
        table,
        table_path,
        _artifact_record(
            artifact_id=str(cfg.experiment.outputs.table.artifact_id),
            run_id=run_id,
            git=git,
            config_hash=config_hash,
            code_status=code_status,
            environment_hash=environment_hash,
            seeds=seeds,
            path=table_path,
            timestamp=timestamp,
            input_hashes=input_hashes,
        ),
    )
    saved_validation = writer.save_table(
        validation,
        validation_path,
        _artifact_record(
            artifact_id=str(cfg.experiment.outputs.validation.artifact_id),
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
        artifact_manifest=[saved_table.to_dict(), saved_validation.to_dict()],
        resolved_config_path=str(resolved_path),
        unresolved_config_path=str(unresolved_path),
        command_line=" ".join(sys.argv),
        python_version=python_version(),
        package_lock_hash=package_lock_hash(root),
        cuda_version=cuda_version(),
        gpu_name=gpu_name(),
        release_ready=bool(cfg.artifact_policy.release_ready),
        extras={
            "mode": "phase4_affine_audit",
            "phase": 4,
            "audit_kind": audit_kind,
            "precision": str(cfg.precision.dtype),
            "device": str(cfg.compute.device),
            "input_artifacts": input_hashes,
            "hard_stop_minutes": float(cfg.experiment.runtime.hard_stop_minutes),
        },
    )
    manifest_path = run_dir / "manifest.json"
    writer.save_manifest(manifest, manifest_path)
    return manifest_path
