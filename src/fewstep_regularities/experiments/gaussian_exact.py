"""Phase 1 exact Gaussian fixed-NFE experiment."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from omegaconf import DictConfig, OmegaConf

from fewstep_regularities.artifacts.manifest import ArtifactRecord, RunManifest
from fewstep_regularities.artifacts.writer import FilesystemArtifactWriter
from fewstep_regularities.distributions.gaussian import standard_gaussian
from fewstep_regularities.experiments.factories import (
    build_device,
    build_dtype,
    build_evaluator,
    build_field,
    build_gaussian,
    build_metric,
    build_path,
    build_solver,
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
from fewstep_regularities.utils.hashing import sha256_text


def _repo_root(cfg: DictConfig) -> Path:
    configured = OmegaConf.select(cfg, "compute.repo_root")
    if configured:
        return Path(str(configured)).resolve()
    return Path(__file__).resolve().parents[3]


def _make_record(
    *,
    artifact_id: str,
    run_id: str,
    git: str,
    config_hash: str,
    code_status: str,
    env_hash: str,
    seeds: list[int],
    path: Path,
    kind: str,
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
        software_environment_hash=env_hash,
        random_seeds=seeds,
        output_checksum="",
        path=str(path),
        kind=kind,
    )


def pushforward_gaussian_moments(
    field: Any,
    source: Any,
    t1: float = 1.0,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return exact endpoint marginal moments for an exact Gaussian field."""
    if not (hasattr(field, "mean_t") and hasattr(field, "cov_t")):
        raise TypeError(
            "Field must expose mean_t and cov_t for exact Gaussian pushforward moments"
        )
    t = torch.tensor(t1, dtype=source.dtype, device=source.device)
    return field.mean_t(t), field.cov_t(t)


def run_gaussian_exact(cfg: DictConfig) -> Path:
    """Run Phase 1 exact Gaussian fixed-NFE validation experiment."""
    start = datetime.now(UTC)
    root = _repo_root(cfg)
    run_id = str(cfg.experiment.run_id)
    output_dir = Path(str(cfg.artifact_policy.output_dir))
    if not output_dir.is_absolute():
        output_dir = (root / output_dir).resolve()
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    unresolved_path = run_dir / "unresolved_config.yaml"
    resolved_path = run_dir / "resolved_config.yaml"
    unresolved_path.write_text(OmegaConf.to_yaml(cfg, resolve=False), encoding="utf-8")
    resolved_path.write_text(OmegaConf.to_yaml(cfg, resolve=True), encoding="utf-8")
    config_hash = sha256_text(OmegaConf.to_yaml(cfg, resolve=True))

    dtype = build_dtype(cfg)
    device = build_device(cfg)
    seeds = [int(s) for s in cfg.experiment.seeds]
    dims = [int(d) for d in cfg.experiment.dimensions]
    nfe_budgets = [int(n) for n in cfg.experiment.nfe_budgets]
    n_particles = int(OmegaConf.select(cfg, "experiment.n_particles", default=4096))

    writer = FilesystemArtifactWriter()
    artifact_records: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []

    git = git_commit(root)
    code_status = git_code_status(root)
    env_hash = software_environment_hash()
    stamp = datetime.now(UTC).isoformat()

    target_names = list(
        OmegaConf.select(cfg, "experiment.target_names", default=["anisotropic_gaussian"])
    )
    path_names = list(OmegaConf.select(cfg, "experiment.path_names", default=["linear"]))
    solver_names = list(OmegaConf.select(cfg, "experiment.solver_names", default=["euler"]))

    for dim in dims:
        for target_name in target_names:
            for path_name in path_names:
                for solver_name in solver_names:
                    for seed in seeds[:1]:  # one seed for particle sampling; fields are exact
                        gen = torch.Generator(device=device).manual_seed(seed)
                        source = standard_gaussian(dim, dtype=dtype, device=device)
                        # Build target from named config overrides.
                        if target_name == "anisotropic_gaussian":
                            target_cfg = {
                                "name": "anisotropic_gaussian",
                                "anisotropy": float(
                                    OmegaConf.select(
                                        cfg, "distribution.anisotropy", default=4.0
                                    )
                                ),
                            }
                        elif target_name == "low_rank_gaussian":
                            target_cfg = {
                                "name": "low_rank_gaussian",
                                "rank": int(
                                    OmegaConf.select(cfg, "distribution.rank", default=2)
                                ),
                                "noise_variance": float(
                                    OmegaConf.select(
                                        cfg, "distribution.noise_variance", default=0.05
                                    )
                                ),
                            }
                        else:
                            raise ValueError(f"Unsupported target {target_name}")
                        target = build_gaussian(
                            target_cfg, dim, dtype, device, generator=gen
                        )
                        path_cfg = {"name": path_name}
                        if path_name == "lipschitz_guided":
                            path_cfg["m"] = float(
                                OmegaConf.select(cfg, "path.m", default=0.0) or 0.0
                            )
                            if path_cfg["m"] <= 0:
                                del path_cfg["m"]
                        path = build_path(path_cfg, source, target, dtype)
                        field = build_field(path_cfg, source, target, path, dtype)
                        solver = build_solver({"name": solver_name})
                        evaluator = build_evaluator(cfg.evaluator, dtype)
                        metric = build_metric(cfg.metric, dtype)

                        metric_result = metric.compute(field)
                        exact_mean, exact_cov = pushforward_gaussian_moments(field, source)

                        for nfe in nfe_budgets:
                            # Skip NFE incompatible with multistage solvers.
                            evals = solver.evals_per_step
                            if nfe % evals != 0:
                                continue
                            x0 = source.sample(n_particles, generator=gen)
                            result = solver.solve(field, x0, 0.0, 1.0, requested_nfe=nfe)
                            x1 = result.trajectory[-1]
                            emp_mean = x1.mean(dim=0)
                            centered = x1 - emp_mean.unsqueeze(0)
                            emp_cov = (centered.T @ centered) / max(n_particles - 1, 1)
                            # Primary: W2 between numerical endpoint Gaussian moments
                            # and analytical target.
                            eval_num = evaluator.compute(
                                {"mean": emp_mean, "covariance": emp_cov},
                                {
                                    "mean": target.mean(),
                                    "covariance": target.covariance(),
                                },
                            )
                            # Reference: exact pushforward vs target (should be ~0
                            # for paths that end at the target law).
                            eval_exact = evaluator.compute(
                                {"mean": exact_mean, "covariance": exact_cov},
                                {
                                    "mean": target.mean(),
                                    "covariance": target.covariance(),
                                },
                            )
                            rows.append(
                                {
                                    "dim": dim,
                                    "target": target_name,
                                    "path": path_name,
                                    "solver": solver_name,
                                    "seed": seed,
                                    "nfe": nfe,
                                    "actual_nfe": result.actual_nfe,
                                    "n_steps": result.n_steps,
                                    "w2_numerical": float(eval_num.primary.item()),
                                    "w2_exact_pushforward": float(
                                        eval_exact.primary.item()
                                    ),
                                    "mean_error": float(
                                        eval_num.auxiliaries["mean_error"].item()
                                    ),
                                    "cov_frobenius_error": float(
                                        eval_num.auxiliaries[
                                            "covariance_frobenius_error"
                                        ].item()
                                    ),
                                    "metric_name": metric.name,
                                    "metric_value": float(metric_result.value.item()),
                                    "metric_is_exact": bool(metric_result.is_exact),
                                    "wall_clock_s": result.wall_clock_s,
                                }
                            )

    table_path = run_dir / "results_table.json"
    record = _make_record(
        artifact_id=f"{run_id}:results_table",
        run_id=run_id,
        git=git,
        config_hash=config_hash,
        code_status=code_status,
        env_hash=env_hash,
        seeds=seeds,
        path=table_path,
        kind="table",
        timestamp=stamp,
    )
    saved = writer.save_table({"rows": rows}, table_path, record)
    artifact_records.append(saved.to_dict())

    end = datetime.now(UTC)
    manifest = RunManifest(
        run_id=run_id,
        git_commit=git,
        config_hash=config_hash,
        code_status=code_status,
        software_environment_hash=env_hash,
        random_seeds=seeds,
        start_time=start.isoformat(),
        end_time=end.isoformat(),
        runtime_s=(end - start).total_seconds(),
        artifact_manifest=artifact_records,
        resolved_config_path=str(resolved_path),
        unresolved_config_path=str(unresolved_path),
        command_line=" ".join(sys.argv),
        python_version=python_version(),
        package_lock_hash=package_lock_hash(root),
        cuda_version=cuda_version(),
        gpu_name=gpu_name(),
        release_ready=bool(cfg.artifact_policy.release_ready),
        extras={
            "mode": "gaussian_exact",
            "n_rows": len(rows),
            "phase": 1,
        },
    )
    manifest_path = run_dir / "manifest.json"
    writer.save_manifest(manifest, manifest_path)
    summary = {"manifest_path": str(manifest_path), "n_rows": len(rows)}
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    return manifest_path
