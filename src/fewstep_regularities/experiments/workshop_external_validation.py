"""Pre-registered workshop external validation on a non-centered family.

Implements the frozen plan in docs/WORKSHOP_EXTERNAL_VALIDATION_PLAN.md:
one shifted anisotropic Gaussian family with nonzero source and target
means, dimensions 2 and 8, linear and variance-preserving paths, Euler,
Heun, and RK4 at NFE 8, 16, and 32, float64, CPU only.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from omegaconf import DictConfig, OmegaConf

from fewstep_regularities.analysis.precision import (
    high_precision_noncentered_gaussian_w2,
)
from fewstep_regularities.analysis.propagation import (
    propagate_gaussian_moments,
    recover_affine_solver_map,
)
from fewstep_regularities.artifacts.manifest import ArtifactRecord, RunManifest
from fewstep_regularities.artifacts.writer import FilesystemArtifactWriter
from fewstep_regularities.distributions.gaussian import Gaussian
from fewstep_regularities.evaluation.gaussian_w2 import GaussianW2Evaluator
from fewstep_regularities.experiments.factories import (
    build_device,
    build_dtype,
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
from fewstep_regularities.utils.hashing import sha256_text

FROZEN_DIMENSIONS = (2, 8)
FROZEN_NFE_BUDGETS = (8, 16, 32)
FROZEN_PATHS = ("linear", "variance_preserving")
FROZEN_SOLVERS = ("euler", "heun", "rk4")
FROZEN_ANISOTROPY = 6.0
FROZEN_SOURCE_MEAN_SCALE = 0.75
FROZEN_TARGET_MEAN_BASE = 1.0
FROZEN_TARGET_MEAN_SLOPE = 0.25
MARGIN_TOLERANCE = 1.0e-9
ENDPOINT_TOLERANCE = 1.0e-9
PRECISION_TOLERANCE = 2.0e-9
MARGIN_TO_PRECISION_RATIO = 100.0
PRECISION_DIGITS = 80


def frozen_source_mean(dim: int, dtype: torch.dtype, device: torch.device) -> Any:
    """Frozen source mean ``mu0_i = 0.75 * (-1)^i``."""
    signs = torch.tensor(
        [1.0 if i % 2 == 0 else -1.0 for i in range(dim)],
        dtype=dtype,
        device=device,
    )
    return FROZEN_SOURCE_MEAN_SCALE * signs


def frozen_target_mean(dim: int, dtype: torch.dtype, device: torch.device) -> Any:
    """Frozen target mean ``mu1_i = 1.0 + 0.25 * i``."""
    index = torch.arange(dim, dtype=dtype, device=device)
    return FROZEN_TARGET_MEAN_BASE + FROZEN_TARGET_MEAN_SLOPE * index


def frozen_target_eigenvalues(
    dim: int, dtype: torch.dtype, device: torch.device
) -> Any:
    """Geometric eigenvalues from ``6^{-1/2}`` to ``6^{1/2}``."""
    anisotropy = torch.tensor(FROZEN_ANISOTROPY, dtype=dtype, device=device)
    if dim == 1:
        return torch.ones(1, dtype=dtype, device=device)
    log_min = -0.5 * torch.log(anisotropy)
    log_max = 0.5 * torch.log(anisotropy)
    return torch.exp(torch.linspace(log_min, log_max, dim, dtype=dtype, device=device))


def build_family(
    dim: int, dtype: torch.dtype, device: torch.device
) -> tuple[Gaussian, Gaussian]:
    """Build the frozen shifted anisotropic source and target."""
    source = Gaussian(
        mean_vec=frozen_source_mean(dim, dtype, device),
        cov=torch.eye(dim, dtype=dtype, device=device),
        _dtype=dtype,
        _device=device,
    )
    target = Gaussian(
        mean_vec=frozen_target_mean(dim, dtype, device),
        cov=torch.diag(frozen_target_eigenvalues(dim, dtype, device)),
        _dtype=dtype,
        _device=device,
    )
    return source, target


def _validate_config(cfg: DictConfig) -> None:
    if str(cfg.experiment.mode) != "workshop_external_validation":
        raise ValueError("Unexpected external validation mode")
    if str(cfg.precision.dtype) != "float64":
        raise TypeError("External validation requires float64")
    if str(cfg.compute.device) != "cpu":
        raise ValueError("External validation requires CPU")
    if float(cfg.experiment.runtime.hard_stop_minutes) > 10.0:
        raise ValueError("External validation hard stop exceeds 10 minutes")
    if [int(v) for v in cfg.experiment.dimensions] != list(FROZEN_DIMENSIONS):
        raise ValueError("External validation dimensions changed")
    if [int(v) for v in cfg.experiment.nfe_budgets] != list(FROZEN_NFE_BUDGETS):
        raise ValueError("External validation NFE budgets changed")
    if [str(v) for v in cfg.experiment.paths] != list(FROZEN_PATHS):
        raise ValueError("External validation path list changed")
    if [str(v) for v in cfg.experiment.solvers] != list(FROZEN_SOLVERS):
        raise ValueError("External validation solver list changed")
    family = cfg.experiment.family
    if (
        float(family.anisotropy) != FROZEN_ANISOTROPY
        or float(family.source_mean_scale) != FROZEN_SOURCE_MEAN_SCALE
        or float(family.target_mean_base) != FROZEN_TARGET_MEAN_BASE
        or float(family.target_mean_slope) != FROZEN_TARGET_MEAN_SLOPE
    ):
        raise ValueError("External validation family parameters changed")
    expected = (
        len(FROZEN_DIMENSIONS)
        * len(FROZEN_PATHS)
        * len(FROZEN_SOLVERS)
        * len(FROZEN_NFE_BUDGETS)
    )
    if int(cfg.experiment.expected_counts.endpoint_configurations) != expected:
        raise ValueError("Expected endpoint count does not match the frozen grid")


def _release_state(cfg: DictConfig, code_status: str) -> None:
    if not bool(cfg.artifact_policy.release_ready):
        raise ValueError("External validation requires release-ready artifacts")
    if code_status != "clean":
        raise RuntimeError("External validation requires a clean worktree")


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
) -> ArtifactRecord:
    return ArtifactRecord(
        artifact_id=artifact_id,
        producing_run_id=run_id,
        git_commit=git,
        config_hash=config_hash,
        code_status=code_status,
        input_artifact_hashes={},
        creation_timestamp=timestamp,
        software_environment_hash=environment_hash,
        random_seeds=seeds,
        output_checksum="",
        path=str(path),
        kind="table",
    )


def _row_diagnostics(matrix: Any, covariance: Any) -> dict[str, float | bool]:
    eigenvalues = torch.linalg.eigvalsh(covariance)
    symmetry = torch.linalg.matrix_norm(covariance - covariance.T, ord="fro")
    return {
        "matrix_condition_number": float(torch.linalg.cond(matrix).item()),
        "covariance_symmetry_residual": float(symmetry.item()),
        "minimum_covariance_eigenvalue": float(eigenvalues.min().item()),
        "maximum_covariance_eigenvalue": float(eigenvalues.max().item()),
        "covariance_is_psd": bool(eigenvalues.min().item() >= -1e-12),
    }


def run_workshop_external_validation(cfg: DictConfig) -> Path:
    """Run the frozen external validation once and audit inversions."""
    start = datetime.now(UTC)
    configured_root = OmegaConf.select(cfg, "compute.repo_root")
    root = (
        Path(str(configured_root)).resolve()
        if configured_root
        else Path(__file__).resolve().parents[3]
    )
    _validate_config(cfg)
    code_status = git_code_status(root)
    _release_state(cfg, code_status)

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
    evaluator = GaussianW2Evaluator(dtype=dtype)
    endpoint_time = torch.tensor(1.0, dtype=dtype, device=device)
    result_rows: list[dict[str, Any]] = []
    metric_by_dim_path: dict[tuple[int, str], float] = {}
    endpoint_consistency: list[float] = []
    offset_supremum: dict[tuple[int, str], float] = {}

    for dim in FROZEN_DIMENSIONS:
        source, target = build_family(dim, dtype, device)
        for path_name in FROZEN_PATHS:
            path_cfg = {"name": path_name}
            path = build_path(path_cfg, source, target, dtype)
            field = GaussianAffineField(
                source=source, target=target, schedule=path, dtype=dtype
            )
            metric = build_metric(cfg.experiment.metric, dtype)
            metric_value = float(metric.compute(field).value.item())
            metric_by_dim_path[(dim, path_name)] = metric_value
            exact_endpoint = evaluator.compute(
                {
                    "mean": field.mean_t(endpoint_time),
                    "covariance": field.cov_t(endpoint_time),
                },
                {"mean": target.mean(), "covariance": target.covariance()},
            )
            endpoint_consistency.append(float(exact_endpoint.primary.item()))
            # Record the drift offset magnitude c(t) on a grid: the frozen
            # family must be genuinely non-centered.
            offsets = []
            for t_value in torch.linspace(0.0, 1.0, 21, dtype=dtype, device=device):
                jac = field.jacobian_matrix(t_value)
                mean_velocity = field.mean_velocity(t_value)
                mean_state = field.mean_t(t_value.reshape(()))
                offsets.append(
                    float(
                        torch.linalg.vector_norm(
                            mean_velocity - jac @ mean_state
                        ).item()
                    )
                )
            offset_supremum[(dim, path_name)] = max(offsets)
            for solver_name in FROZEN_SOLVERS:
                for nfe in FROZEN_NFE_BUDGETS:
                    solver = build_solver({"name": solver_name})
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
                    result_rows.append(
                        {
                            "target_family": "shifted_anisotropic_gaussian",
                            "dim": dim,
                            "path": path_name,
                            "solver": solver_name,
                            "nfe": nfe,
                            "actual_nfe": affine_map.actual_nfe,
                            "n_steps": affine_map.n_steps,
                            "affine_matrix": affine_map.matrix.tolist(),
                            "affine_offset": affine_map.offset.tolist(),
                            "mean": mean.tolist(),
                            "covariance": covariance.tolist(),
                            "gaussian_w2": float(evaluation.primary.item()),
                            "gaussian_w2_is_exact_from_moments": True,
                            "mean_error": float(
                                evaluation.auxiliaries["mean_error"].item()
                            ),
                            "baseline_metric": metric_value,
                            "continuous_endpoint_w2": float(
                                exact_endpoint.primary.item()
                            ),
                            "wall_clock_s": affine_map.wall_clock_s,
                            **_row_diagnostics(affine_map.matrix, covariance),
                        }
                    )

    expected_rows = (
        len(FROZEN_DIMENSIONS)
        * len(FROZEN_PATHS)
        * len(FROZEN_SOLVERS)
        * len(FROZEN_NFE_BUDGETS)
    )
    if len(result_rows) != expected_rows:
        raise RuntimeError("External validation produced an unexpected row count")

    rows_by_key = {
        (row["dim"], row["path"], row["solver"], row["nfe"]): row for row in result_rows
    }
    inversion_rows: list[dict[str, Any]] = []
    precision_rows: list[dict[str, Any]] = []
    for dim in FROZEN_DIMENSIONS:
        eigenvalues = [
            float(v) for v in frozen_target_eigenvalues(dim, dtype, device).tolist()
        ]
        source_means = [float(v) for v in frozen_source_mean(dim, dtype, device)]
        target_means = [float(v) for v in frozen_target_mean(dim, dtype, device)]
        for solver_name in FROZEN_SOLVERS:
            for nfe in FROZEN_NFE_BUDGETS:
                linear_row = rows_by_key[(dim, "linear", solver_name, nfe)]
                vp_row = rows_by_key[(dim, "variance_preserving", solver_name, nfe)]
                metric_delta = float(linear_row["baseline_metric"]) - float(
                    vp_row["baseline_metric"]
                )
                w2_delta = float(linear_row["gaussian_w2"]) - float(
                    vp_row["gaussian_w2"]
                )
                is_inversion = (
                    metric_delta * w2_delta < 0.0
                    and abs(metric_delta) > MARGIN_TOLERANCE
                    and abs(w2_delta) > MARGIN_TOLERANCE
                )
                block = {
                    "dim": dim,
                    "solver": solver_name,
                    "nfe": nfe,
                    "metric_delta_linear_minus_vp": metric_delta,
                    "w2_delta_linear_minus_vp": w2_delta,
                    "is_inversion": is_inversion,
                    "audited": False,
                    "audit_passed": False,
                }
                if is_inversion:
                    max_difference = 0.0
                    mp_values: dict[str, float] = {}
                    for path_name, row in (
                        ("linear", linear_row),
                        ("variance_preserving", vp_row),
                    ):
                        mp_w2 = high_precision_noncentered_gaussian_w2(
                            path_name,
                            solver_name,
                            eigenvalues,
                            source_means,
                            target_means,
                            nfe,
                            decimal_digits=PRECISION_DIGITS,
                        )
                        difference = abs(float(mp_w2) - float(row["gaussian_w2"]))
                        max_difference = max(max_difference, difference)
                        mp_values[path_name] = float(mp_w2)
                        precision_rows.append(
                            {
                                "dim": dim,
                                "path": path_name,
                                "solver": solver_name,
                                "nfe": nfe,
                                "float64_w2": float(row["gaussian_w2"]),
                                "mp80_w2": float(mp_w2),
                                "absolute_difference": difference,
                                "decimal_digits": PRECISION_DIGITS,
                            }
                        )
                    mp_margin = mp_values["linear"] - mp_values["variance_preserving"]
                    block["audited"] = True
                    block["audit_max_absolute_difference"] = max_difference
                    block["audit_passed"] = (
                        max_difference <= PRECISION_TOLERANCE
                        and abs(w2_delta)
                        > MARGIN_TO_PRECISION_RATIO * max(max_difference, 1e-300)
                        and mp_margin * w2_delta > 0.0
                    )
                inversion_rows.append(block)

    flagged = [row for row in inversion_rows if row["is_inversion"]]
    audited_pass = [row for row in flagged if row["audit_passed"]]
    equal_nfe = all(row["nfe"] == row["actual_nfe"] for row in result_rows)
    covariance_valid = all(
        row["covariance_is_psd"] and float(row["covariance_symmetry_residual"]) <= 1e-12
        for row in result_rows
    )
    endpoint_valid = all(value <= ENDPOINT_TOLERANCE for value in endpoint_consistency)
    offset_nonzero = all(value > 1e-6 for value in offset_supremum.values())
    audits_valid = all(row["audit_passed"] for row in flagged)
    validation = {
        "row_count": len(result_rows),
        "expected_row_count": expected_rows,
        "comparison_block_count": len(inversion_rows),
        "equal_nfe_validated": equal_nfe,
        "covariance_validated": covariance_valid,
        "continuous_endpoint_validated": endpoint_valid,
        "continuous_endpoint_tolerance": ENDPOINT_TOLERANCE,
        "drift_offset_nonzero_validated": offset_nonzero,
        "max_drift_offset_by_dim_path": {
            f"dim{dim}:{path_name}": value
            for (dim, path_name), value in offset_supremum.items()
        },
        "inversion_count": len(flagged),
        "audited_inversion_count": len(audited_pass),
        "all_flagged_inversions_pass_audit": audits_valid,
        "margin_tolerance": MARGIN_TOLERANCE,
        "precision_tolerance": PRECISION_TOLERANCE,
        "margin_to_precision_ratio_required": MARGIN_TO_PRECISION_RATIO,
        "all_checks_passed": (
            equal_nfe
            and covariance_valid
            and endpoint_valid
            and offset_nonzero
            and audits_valid
        ),
    }
    if not validation["all_checks_passed"]:
        raise RuntimeError("External validation checks failed")

    writer = FilesystemArtifactWriter()
    git = git_commit(root)
    environment_hash = software_environment_hash()
    seeds = [int(value) for value in cfg.experiment.seeds]
    timestamp = datetime.now(UTC).isoformat()

    def _save(name: str, payload: dict[str, Any]) -> ArtifactRecord:
        path = run_dir / f"{name}.json"
        return writer.save_table(
            payload,
            path,
            _artifact_record(
                artifact_id=f"{run_id}:{name}",
                run_id=run_id,
                git=git,
                config_hash=config_hash,
                code_status=code_status,
                environment_hash=environment_hash,
                seeds=seeds,
                path=path,
                timestamp=timestamp,
            ),
        )

    saved = [
        _save(
            "results",
            {
                "family": {
                    "name": "shifted_anisotropic_gaussian",
                    "anisotropy": FROZEN_ANISOTROPY,
                    "source_mean_rule": "0.75 * (-1)^i",
                    "target_mean_rule": "1.0 + 0.25 * i",
                    "geometry_seed_note": "recorded only; no randomness consumed",
                },
                "quantity_status": {
                    "gaussian_w2": "exact from analytical numerical-map moments",
                    "baseline_metric": "numerical time quadrature",
                },
                "rows": result_rows,
            },
        ),
        _save("inversions", {"rows": inversion_rows}),
        _save(
            "precision",
            {
                "decimal_digits": PRECISION_DIGITS,
                "note": "audit rows exist only for flagged inversions",
                "rows": precision_rows,
            },
        ),
        _save("validation", validation),
    ]

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
        artifact_manifest=[record.to_dict() for record in saved],
        resolved_config_path=str(resolved_path),
        unresolved_config_path=str(unresolved_path),
        command_line=" ".join(sys.argv),
        python_version=python_version(),
        package_lock_hash=package_lock_hash(root),
        cuda_version=cuda_version(),
        gpu_name=gpu_name(),
        release_ready=bool(cfg.artifact_policy.release_ready),
        extras={
            "mode": "workshop_external_validation",
            "plan": "docs/WORKSHOP_EXTERNAL_VALIDATION_PLAN.md",
            "precision": str(cfg.precision.dtype),
            "device": str(cfg.compute.device),
            "target_geometry_seed": int(cfg.experiment.target_geometry_seed),
            "expected_runtime_minutes": float(cfg.experiment.runtime.expected_minutes),
            "hard_stop_minutes": float(cfg.experiment.runtime.hard_stop_minutes),
        },
    )
    manifest_path = run_dir / "manifest.json"
    writer.save_manifest(manifest, manifest_path)
    return manifest_path
