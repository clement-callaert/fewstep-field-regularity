"""Registered Phase 3 decision-gate benchmark."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from omegaconf import DictConfig, OmegaConf
from torch import Tensor

from fewstep_regularities.analysis.propagation import (
    propagate_gaussian_moments,
    recover_affine_solver_map,
)
from fewstep_regularities.artifacts.manifest import ArtifactRecord, RunManifest
from fewstep_regularities.artifacts.writer import FilesystemArtifactWriter
from fewstep_regularities.distributions.gaussian import Gaussian, standard_gaussian
from fewstep_regularities.distributions.gaussian_mixture import GaussianMixture
from fewstep_regularities.evaluation.gaussian_w2 import GaussianW2Evaluator
from fewstep_regularities.evaluation.projected_sliced import (
    SlicedWassersteinEvaluator,
)
from fewstep_regularities.experiments.factories import (
    build_device,
    build_distribution,
    build_dtype,
    build_field,
    build_metric,
    build_path,
    build_solver,
)
from fewstep_regularities.metrics.mixture_mc import dispatch_metric_compute
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
from fewstep_regularities.utils.precision import assert_dtype
from fewstep_regularities.utils.shapes import assert_device, assert_shape


def numerical_gaussian_moments(
    field: Any,
    solver: Any,
    source_mean: Tensor,
    source_covariance: Tensor,
    requested_nfe: int,
) -> tuple[Tensor, Tensor, int, int, float]:
    """Propagate Gaussian moments through an affine numerical solver map.

    Args:
        field: Affine velocity field on vectors of shape ``(dim,)``.
        solver: Fixed-step solver whose stages preserve affine state maps.
        source_mean: Source mean with shape ``(dim,)``.
        source_covariance: Source covariance with shape ``(dim, dim)``.
        requested_nfe: Positive field evaluation budget divisible by the
            solver evaluation count.

    Returns:
        Endpoint mean with shape ``(dim,)``, endpoint covariance with shape
        ``(dim, dim)``, actual NFE, step count, and wall time.

    Dtype:
        Inputs and outputs keep the source floating dtype. No cast is made.

    Device:
        Probe states and outputs stay on the source device.

    Mathematical definition:
        If the numerical endpoint map is ``x -> A x + b``, the returned
        moments are ``A m + b`` and ``A C A^T``. The map is recovered from
        its values at zero and the coordinate basis.

    References:
        Affine transformation rule for multivariate Gaussian moments.
    """
    if not source_mean.is_floating_point() or not source_covariance.is_floating_point():
        raise TypeError("Gaussian moments must have a floating dtype")
    assert_dtype(source_covariance, source_mean.dtype, "source_covariance")
    assert_device(source_covariance, source_mean.device, "source_covariance")
    assert_shape(source_mean, (None,), "source_mean")
    dim = source_mean.shape[0]
    assert_shape(source_covariance, (dim, dim), "source_covariance")
    if requested_nfe < 1:
        raise ValueError("requested_nfe must be positive")

    affine_map = recover_affine_solver_map(
        field,
        solver,
        dim=dim,
        dtype=source_mean.dtype,
        device=source_mean.device,
        requested_nfe=requested_nfe,
    )
    mean, covariance = propagate_gaussian_moments(
        affine_map,
        source_mean,
        source_covariance,
    )
    return (
        mean,
        covariance,
        affine_map.actual_nfe,
        affine_map.n_steps,
        affine_map.wall_clock_s,
    )


def _repo_root(cfg: DictConfig) -> Path:
    configured = OmegaConf.select(cfg, "compute.repo_root")
    if configured:
        return Path(str(configured)).resolve()
    return Path(__file__).resolve().parents[3]


def _target_config(name: str) -> dict[str, Any]:
    configs: dict[str, dict[str, Any]] = {
        "anisotropic_gaussian": {
            "name": "anisotropic_gaussian",
            "anisotropy": 4.0,
        },
        "low_rank_gaussian": {
            "name": "low_rank_gaussian",
            "rank": 2,
            "noise_variance": 0.05,
        },
        "two_mode_gmm": {
            "name": "two_mode_gmm",
            "separation": 2.0,
            "component_std": 0.5,
        },
        "imbalanced_gmm": {
            "name": "imbalanced_gmm",
            "weight_ratio": 9.0,
            "separation": 2.0,
            "component_std": 0.5,
        },
    }
    if name not in configs:
        raise ValueError(f"Unsupported gate target {name!r}")
    return configs[name]


def _validate_gate_config(cfg: DictConfig) -> None:
    if str(cfg.experiment.gate_version) != "2026-07-23-v1":
        raise ValueError("Unexpected gate version")
    paths = [str(v) for v in cfg.experiment.path_names]
    targets = [str(v) for v in cfg.experiment.target_names]
    if "gaussian_ot" in paths and any("gmm" in target for target in targets):
        raise ValueError("gaussian_ot is refused for mixture targets")
    solvers = [build_solver({"name": str(v)}) for v in cfg.experiment.solver_names]
    for nfe in cfg.experiment.nfe_budgets:
        if any(int(nfe) % solver.evals_per_step != 0 for solver in solvers):
            raise ValueError(f"NFE {nfe} is not valid for every registered solver")
    if [int(seed) for seed in cfg.experiment.seeds] != list(range(10)):
        raise ValueError("The registered seeds must be 0 through 9")
    if build_dtype(cfg) is not torch.float64:
        raise TypeError("The registered gate requires float64")


def _record(
    *,
    artifact_id: str,
    run_id: str,
    git: str,
    config_hash: str,
    code_status: str,
    env_hash: str,
    seeds: list[int],
    path: Path,
    timestamp: str,
    inputs: dict[str, str] | None = None,
) -> ArtifactRecord:
    return ArtifactRecord(
        artifact_id=artifact_id,
        producing_run_id=run_id,
        git_commit=git,
        config_hash=config_hash,
        code_status=code_status,
        input_artifact_hashes=inputs or {},
        creation_timestamp=timestamp,
        software_environment_hash=env_hash,
        random_seeds=seeds,
        output_checksum="",
        path=str(path),
        kind="table",
    )


def _metric_rows(
    *,
    cfg: DictConfig,
    target_name: str,
    dim: int,
    path_name: str,
    source: Gaussian,
    target: Gaussian | GaussianMixture,
    dtype: torch.dtype,
    stochastic_seeds: list[int],
) -> list[dict[str, Any]]:
    path_cfg = {"name": path_name}
    path = build_path(path_cfg, source, target, dtype)
    field = build_field(path_cfg, source, target, path, dtype)
    rows: list[dict[str, Any]] = []
    is_mixture = isinstance(target, GaussianMixture)
    seeds = stochastic_seeds if is_mixture else [-1]
    budgets = (
        [int(v) for v in cfg.experiment.metric_estimator_budgets]
        if is_mixture
        else [int(cfg.experiment.primary_metric_estimator_budget)]
    )
    for metric_name in cfg.experiment.metric_names:
        for budget in budgets:
            for seed in seeds:
                metric = build_metric(
                    {
                        "name": str(metric_name),
                        "n_time": int(cfg.experiment.metric_n_time),
                    },
                    dtype,
                )
                metric.n_samples = budget
                metric.seed = seed
                result = dispatch_metric_compute(metric, field)
                rows.append(
                    {
                        "target_family": target_name,
                        "path": path_name,
                        "dim": dim,
                        "seed": seed,
                        "metric_name": str(metric_name),
                        "metric_value": float(result.value.item()),
                        "metric_is_exact": bool(result.is_exact),
                        "metric_estimator_budget": budget,
                        "metric_metadata": dict(result.metadata),
                    }
                )
    return rows


def _gaussian_outcomes(
    *,
    cfg: DictConfig,
    target_name: str,
    dim: int,
    path_name: str,
    source: Gaussian,
    target: Gaussian,
    dtype: torch.dtype,
) -> list[dict[str, Any]]:
    path_cfg = {"name": path_name}
    path = build_path(path_cfg, source, target, dtype)
    field = build_field(path_cfg, source, target, path, dtype)
    evaluator = GaussianW2Evaluator(dtype=dtype)
    rows: list[dict[str, Any]] = []
    for solver_name in cfg.experiment.solver_names:
        solver = build_solver({"name": str(solver_name)})
        for nfe_value in cfg.experiment.nfe_budgets:
            nfe = int(nfe_value)
            mean, covariance, actual_nfe, n_steps, wall = numerical_gaussian_moments(
                field,
                solver,
                source.mean(),
                source.covariance(),
                nfe,
            )
            result = evaluator.compute(
                {"mean": mean, "covariance": covariance},
                {"mean": target.mean(), "covariance": target.covariance()},
            )
            rows.append(
                {
                    "target_family": target_name,
                    "path": path_name,
                    "solver": str(solver_name),
                    "dim": dim,
                    "nfe": nfe,
                    "actual_nfe": actual_nfe,
                    "n_steps": n_steps,
                    "seed": -1,
                    "error": float(result.primary.item()),
                    "evaluator": evaluator.name,
                    "evaluator_is_exact": True,
                    "evaluator_budget": 0,
                    "evaluator_metadata": {
                        "definition": "exact Gaussian W2 on analytical moments"
                    },
                    "wall_clock_s": wall,
                }
            )
    return rows


def _mixture_outcomes(
    *,
    cfg: DictConfig,
    target_name: str,
    dim: int,
    path_name: str,
    source: Gaussian,
    target: GaussianMixture,
    dtype: torch.dtype,
    device: torch.device,
    stochastic_seeds: list[int],
) -> list[dict[str, Any]]:
    path_cfg = {"name": path_name}
    path = build_path(path_cfg, source, target, dtype)
    field = build_field(path_cfg, source, target, path, dtype)
    rows: list[dict[str, Any]] = []
    n_particles = int(cfg.experiment.n_particles)
    projection_budgets = [int(v) for v in cfg.experiment.wasserstein_projection_budgets]
    for solver_name in cfg.experiment.solver_names:
        solver = build_solver({"name": str(solver_name)})
        for nfe_value in cfg.experiment.nfe_budgets:
            nfe = int(nfe_value)
            for seed in stochastic_seeds:
                generator = torch.Generator(device=device).manual_seed(seed)
                x0 = source.sample(n_particles, generator=generator)
                target_sample = target.sample(n_particles, generator=generator)
                solved = solver.solve(field, x0, 0.0, 1.0, requested_nfe=nfe)
                endpoint = solved.trajectory[-1]
                for projections in projection_budgets:
                    evaluator = SlicedWassersteinEvaluator(
                        n_projections=projections,
                        dtype=dtype,
                        seed=seed,
                    )
                    result = evaluator.compute(endpoint, target_sample)
                    rows.append(
                        {
                            "target_family": target_name,
                            "path": path_name,
                            "solver": str(solver_name),
                            "dim": dim,
                            "nfe": nfe,
                            "actual_nfe": solved.actual_nfe,
                            "n_steps": solved.n_steps,
                            "seed": seed,
                            "error": float(result.primary.item()),
                            "evaluator": evaluator.name,
                            "evaluator_is_exact": False,
                            "evaluator_budget": projections,
                            "evaluator_metadata": {
                                **dict(result.metadata),
                                "n_particles": n_particles,
                                "calibration_artifact": (
                                    "phase2_calibration:calibration_table"
                                ),
                            },
                            "wall_clock_s": solved.wall_clock_s,
                        }
                    )
    return rows


def _join_observations(
    outcomes: list[dict[str, Any]],
    metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    metric_index: dict[tuple[str, str, int, int], list[dict[str, Any]]] = {}
    for row in metrics:
        key = (
            str(row["target_family"]),
            str(row["path"]),
            int(row["dim"]),
            int(row["seed"]),
        )
        metric_index.setdefault(key, []).append(row)
    joined: list[dict[str, Any]] = []
    for outcome in outcomes:
        seed = int(outcome["seed"])
        key = (
            str(outcome["target_family"]),
            str(outcome["path"]),
            int(outcome["dim"]),
            seed,
        )
        for metric in metric_index[key]:
            joined.append({**outcome, **metric})
    return joined


def run_gate_benchmark(cfg: DictConfig) -> Path:
    """Run the frozen Phase 3 grid and save immutable outcome artifacts."""
    _validate_gate_config(cfg)
    start = datetime.now(UTC)
    root = _repo_root(cfg)
    run_id = str(cfg.experiment.run_id)
    output_dir = Path(str(cfg.artifact_policy.output_dir))
    if not output_dir.is_absolute():
        output_dir = (root / output_dir).resolve()
    run_dir = output_dir / run_id
    if (run_dir / "manifest.json").exists():
        raise FileExistsError(f"Refusing to overwrite completed run {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)

    unresolved_path = run_dir / "unresolved_config.yaml"
    resolved_path = run_dir / "resolved_config.yaml"
    unresolved_text = OmegaConf.to_yaml(cfg, resolve=False)

    dtype = build_dtype(cfg)
    device = build_device(cfg)
    seeds = [int(v) for v in cfg.experiment.seeds]
    dimensions = [int(v) for v in cfg.experiment.dimensions]
    targets = [str(v) for v in cfg.experiment.target_names]
    paths = [str(v) for v in cfg.experiment.path_names]
    if bool(OmegaConf.select(cfg, "experiment.smoke", default=False)):
        seeds = seeds[:1]
        dimensions = dimensions[:1]
        targets = [targets[0], next(v for v in targets if "gmm" in v)]
        paths = paths[:1]
        cfg.experiment.nfe_budgets = [int(cfg.experiment.nfe_budgets[0])]
        cfg.experiment.metric_estimator_budgets = [
            int(cfg.experiment.primary_metric_estimator_budget)
        ]
        cfg.experiment.wasserstein_projection_budgets = [
            int(cfg.experiment.n_projections)
        ]
        cfg.experiment.seeds = seeds
        cfg.experiment.dimensions = dimensions
        cfg.experiment.target_names = targets
        cfg.experiment.path_names = paths

    unresolved_path.write_text(unresolved_text, encoding="utf-8")
    resolved_text = OmegaConf.to_yaml(cfg, resolve=True)
    resolved_path.write_text(resolved_text, encoding="utf-8")
    config_hash = sha256_text(resolved_text)

    geometry_seed = int(cfg.experiment.target_geometry_seed)
    metric_rows: list[dict[str, Any]] = []
    outcome_rows: list[dict[str, Any]] = []
    for dim in dimensions:
        for target_name in targets:
            geometry_generator = torch.Generator(device=device).manual_seed(
                geometry_seed
            )
            source = standard_gaussian(dim, dtype=dtype, device=device)
            target = build_distribution(
                _target_config(target_name),
                dim,
                dtype,
                device,
                generator=geometry_generator,
            )
            for path_name in paths:
                metric_rows.extend(
                    _metric_rows(
                        cfg=cfg,
                        target_name=target_name,
                        dim=dim,
                        path_name=path_name,
                        source=source,
                        target=target,
                        dtype=dtype,
                        stochastic_seeds=seeds,
                    )
                )
                if isinstance(target, Gaussian):
                    outcome_rows.extend(
                        _gaussian_outcomes(
                            cfg=cfg,
                            target_name=target_name,
                            dim=dim,
                            path_name=path_name,
                            source=source,
                            target=target,
                            dtype=dtype,
                        )
                    )
                else:
                    outcome_rows.extend(
                        _mixture_outcomes(
                            cfg=cfg,
                            target_name=target_name,
                            dim=dim,
                            path_name=path_name,
                            source=source,
                            target=target,
                            dtype=dtype,
                            device=device,
                            stochastic_seeds=seeds,
                        )
                    )
    observations = _join_observations(outcome_rows, metric_rows)
    if any(int(row["actual_nfe"]) != int(row["nfe"]) for row in observations):
        raise RuntimeError("Equal-NFE validation failed")

    writer = FilesystemArtifactWriter()
    git = git_commit(root)
    status = git_code_status(root)
    env_hash = software_environment_hash()
    stamp = datetime.now(UTC).isoformat()
    table_path = run_dir / "gate_results.json"
    calibration_cfg = OmegaConf.select(cfg, "experiment.inputs.calibration")
    if calibration_cfg is None:
        calibration_artifact_id = "phase2_calibration:calibration_table"
        calibration_path = Path("outputs/phase2_calibration/calibration_table.json")
    else:
        calibration_artifact_id = str(calibration_cfg.artifact_id)
        calibration_path = Path(str(calibration_cfg.path))
    if not calibration_path.is_absolute():
        calibration_path = (root / calibration_path).resolve()
    if not calibration_path.is_file():
        raise FileNotFoundError("Phase 2 calibration artifact is missing")
    table_record = _record(
        artifact_id=f"{run_id}:gate_results",
        run_id=run_id,
        git=git,
        config_hash=config_hash,
        code_status=status,
        env_hash=env_hash,
        seeds=seeds,
        path=table_path,
        timestamp=stamp,
        inputs={
            calibration_artifact_id: sha256_file(calibration_path),
        },
    )
    saved_table = writer.save_table(
        {
            "gate_version": str(cfg.experiment.gate_version),
            "sampling_unit": [
                "target_family",
                "path",
                "solver",
                "dim",
                "nfe",
            ],
            "observations": observations,
        },
        table_path,
        table_record,
    )
    summary_path = run_dir / "run_summary.json"
    summary_record = _record(
        artifact_id=f"{run_id}:run_summary",
        run_id=run_id,
        git=git,
        config_hash=config_hash,
        code_status=status,
        env_hash=env_hash,
        seeds=seeds,
        path=summary_path,
        timestamp=stamp,
    )
    saved_summary = writer.save_table(
        {
            "n_observations": len(observations),
            "n_outcomes": len(outcome_rows),
            "n_metric_estimates": len(metric_rows),
            "equal_nfe_validated": True,
            "smoke": bool(OmegaConf.select(cfg, "experiment.smoke", default=False)),
        },
        summary_path,
        summary_record,
    )
    end = datetime.now(UTC)
    manifest = RunManifest(
        run_id=run_id,
        git_commit=git,
        config_hash=config_hash,
        code_status=status,
        software_environment_hash=env_hash,
        random_seeds=seeds,
        start_time=start.isoformat(),
        end_time=end.isoformat(),
        runtime_s=(end - start).total_seconds(),
        artifact_manifest=[saved_table.to_dict(), saved_summary.to_dict()],
        resolved_config_path=str(resolved_path),
        unresolved_config_path=str(unresolved_path),
        command_line=" ".join(sys.argv),
        python_version=python_version(),
        package_lock_hash=package_lock_hash(root),
        cuda_version=cuda_version(),
        gpu_name=gpu_name(),
        release_ready=bool(cfg.artifact_policy.release_ready),
        extras={
            "mode": "gate_benchmark",
            "phase": 3,
            "gate_version": str(cfg.experiment.gate_version),
            "analysis_plan": str(cfg.experiment.analysis_plan),
            "timing": {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "runtime_s": (end - start).total_seconds(),
            },
        },
    )
    manifest_path = run_dir / "manifest.json"
    writer.save_manifest(manifest, manifest_path)
    return manifest_path
