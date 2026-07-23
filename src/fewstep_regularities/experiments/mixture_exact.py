"""Phase 2 exact mixture fixed-NFE smoke experiment."""

from __future__ import annotations

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
    build_distribution,
    build_dtype,
    build_evaluator,
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
from fewstep_regularities.utils.hashing import sha256_text


def _repo_root(cfg: DictConfig) -> Path:
    configured = OmegaConf.select(cfg, "compute.repo_root")
    if configured:
        return Path(str(configured)).resolve()
    return Path(__file__).resolve().parents[3]


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


def run_mixture_exact(cfg: DictConfig) -> Path:
    """Run Phase 2 mixture fixed-NFE validation on a small grid."""
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
    n_particles = int(OmegaConf.select(cfg, "experiment.n_particles", default=256))

    writer = FilesystemArtifactWriter()
    rows: list[dict[str, Any]] = []
    git = git_commit(root)
    code_status = git_code_status(root)
    env_hash = software_environment_hash()
    stamp = datetime.now(UTC).isoformat()

    target_names = list(
        OmegaConf.select(
            cfg,
            "experiment.target_names",
            default=[str(cfg.distribution.name)],
        )
    )
    path_names = list(
        OmegaConf.select(cfg, "experiment.path_names", default=[str(cfg.path.name)])
    )
    solver_names = list(
        OmegaConf.select(cfg, "experiment.solver_names", default=[str(cfg.solver.name)])
    )

    for dim in dims:
        for target_name in target_names:
            for path_name in path_names:
                for solver_name in solver_names:
                    for seed in seeds:
                        gen = torch.Generator(device=device).manual_seed(seed)
                        source = standard_gaussian(dim, dtype=dtype, device=device)
                        configured_target = cfg.distribution
                        target_cfg: Any = {"name": target_name}
                        if str(cfg.distribution.name) == target_name:
                            target_cfg = configured_target
                        target = build_distribution(
                            target_cfg, dim, dtype, device, generator=gen
                        )
                        path_cfg: Any = {"name": path_name}
                        if str(cfg.path.name) == path_name:
                            path_cfg = cfg.path
                        path = build_path(path_cfg, source, target, dtype)
                        field = build_field(path_cfg, source, target, path, dtype)
                        solver_cfg: Any = {"name": solver_name}
                        if str(cfg.solver.name) == solver_name:
                            solver_cfg = cfg.solver
                        solver = build_solver(solver_cfg)
                        evaluator = build_evaluator(cfg.evaluator, dtype)
                        metric = build_metric(cfg.metric, dtype)
                        metric_result = dispatch_metric_compute(metric, field)

                        for nfe in nfe_budgets:
                            if nfe % solver.evals_per_step != 0:
                                continue
                            x0 = source.sample(n_particles, generator=gen)
                            result = solver.solve(
                                field, x0, 0.0, 1.0, requested_nfe=nfe
                            )
                            x1 = result.trajectory[-1]
                            y = target.sample(n_particles, generator=gen)
                            eval_res = evaluator.compute(x1, y)
                            mean_err = torch.linalg.vector_norm(
                                x1.mean(0) - target.mean()
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
                                    "primary_error": float(eval_res.primary.item()),
                                    "evaluator": evaluator.name,
                                    "mean_error": float(mean_err.item()),
                                    "metric_name": metric.name,
                                    "metric_value": float(metric_result.value.item()),
                                    "metric_is_exact": bool(metric_result.is_exact),
                                    "wall_clock_s": result.wall_clock_s,
                                }
                            )

    table_path = run_dir / "results_table.json"
    record = _record(
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
    summary_path = run_dir / "summary.json"
    summary_record = _record(
        artifact_id=f"{run_id}:summary",
        run_id=run_id,
        git=git,
        config_hash=config_hash,
        code_status=code_status,
        env_hash=env_hash,
        seeds=seeds,
        path=summary_path,
        kind="table",
        timestamp=stamp,
    )
    saved_summary = writer.save_table(
        {"n_rows": len(rows), "status": "numerically_checked"},
        summary_path,
        summary_record,
    )

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
        artifact_manifest=[saved.to_dict(), saved_summary.to_dict()],
        resolved_config_path=str(resolved_path),
        unresolved_config_path=str(unresolved_path),
        command_line=" ".join(sys.argv),
        python_version=python_version(),
        package_lock_hash=package_lock_hash(root),
        cuda_version=cuda_version(),
        gpu_name=gpu_name(),
        release_ready=bool(cfg.artifact_policy.release_ready),
        extras={"mode": "mixture_exact", "phase": 2, "n_rows": len(rows)},
    )
    manifest_path = run_dir / "manifest.json"
    writer.save_manifest(manifest, manifest_path)
    return manifest_path
