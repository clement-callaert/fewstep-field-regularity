"""Phase 2 Wasserstein estimator calibration experiment."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from omegaconf import DictConfig, OmegaConf

from fewstep_regularities.artifacts.manifest import ArtifactRecord, RunManifest
from fewstep_regularities.artifacts.writer import FilesystemArtifactWriter
from fewstep_regularities.distributions.gaussian import (
    anisotropic_gaussian,
    standard_gaussian,
)
from fewstep_regularities.distributions.gaussian_mixture import two_mode_gmm
from fewstep_regularities.evaluation.gaussian_w2 import gaussian_w2
from fewstep_regularities.evaluation.projected_sliced import (
    DiscreteOTEvaluator,
    EntropicOTEvaluator,
    ProjectedW2Evaluator,
    SlicedWassersteinEvaluator,
)
from fewstep_regularities.experiments.factories import build_device, build_dtype
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


def run_estimator_calibration(cfg: DictConfig) -> Path:
    """Calibrate empirical W2 estimators against exact Gaussian W2 and each other."""
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
    sample_sizes = [
        int(n)
        for n in OmegaConf.select(cfg, "experiment.sample_sizes", default=[64, 256])
    ]
    n_proj = int(OmegaConf.select(cfg, "experiment.n_projections", default=64))
    projected_n_proj = int(
        OmegaConf.select(cfg, "experiment.projected_n_projections", default=1)
    )
    epsilon = float(OmegaConf.select(cfg, "experiment.epsilon", default=0.05))
    entropic_max_iter = int(
        OmegaConf.select(cfg, "experiment.entropic_max_iter", default=10000)
    )
    entropic_tol = float(
        OmegaConf.select(cfg, "experiment.entropic_tol", default=1e-5)
    )
    discrete_n = int(OmegaConf.select(cfg, "experiment.discrete_n", default=32))
    if discrete_n < 1:
        raise ValueError("discrete_n must be positive")

    writer = FilesystemArtifactWriter()
    rows: list[dict[str, Any]] = []
    git = git_commit(root)
    code_status = git_code_status(root)
    env_hash = software_environment_hash()
    stamp = datetime.now(UTC).isoformat()

    for dim in dims:
        source = standard_gaussian(dim, dtype=dtype, device=device)
        target_g = anisotropic_gaussian(dim, anisotropy=4.0, dtype=dtype, device=device)
        exact = float(
            gaussian_w2(
                source.mean(),
                source.covariance(),
                target_g.mean(),
                target_g.covariance(),
            ).item()
        )
        for n in sample_sizes:
            for seed in seeds:
                gen = torch.Generator(device=device).manual_seed(seed)
                x = source.sample(n, generator=gen)
                y = target_g.sample(n, generator=gen)
                sw = SlicedWassersteinEvaluator(
                    n_projections=n_proj, dtype=dtype, seed=seed
                ).compute(x, y)
                projected = ProjectedW2Evaluator(
                    n_projections=projected_n_proj, dtype=dtype, seed=seed
                ).compute(x, y)
                ent = EntropicOTEvaluator(
                    epsilon=epsilon,
                    dtype=dtype,
                    max_iter=entropic_max_iter,
                    tol=entropic_tol,
                ).compute(x, y)
                row = {
                    "family": "gaussian",
                    "dim": dim,
                    "n": n,
                    "seed": seed,
                    "exact_w2": exact,
                    "projected_w2": float(projected.primary.item()),
                    "sliced_w2": float(sw.primary.item()),
                    "entropic_sqrt_cost": float(ent.primary.item()),
                    "entropic_regularized_objective": float(
                        ent.auxiliaries["regularized_objective"].item()
                    ),
                    "entropic_iterations": int(ent.metadata["iterations"]),
                    "entropic_row_residual": float(
                        ent.auxiliaries["row_marginal_residual"].item()
                    ),
                    "entropic_column_residual": float(
                        ent.auxiliaries["column_marginal_residual"].item()
                    ),
                    "projected_minus_exact_reference": (
                        float(projected.primary.item()) - exact
                    ),
                    "sliced_minus_exact_reference": float(sw.primary.item()) - exact,
                    "entropic_minus_exact_reference": (
                        float(ent.primary.item()) - exact
                    ),
                }
                n_discrete = min(n, discrete_n)
                disc = DiscreteOTEvaluator(max_points=discrete_n, dtype=dtype).compute(
                    x[:n_discrete], y[:n_discrete]
                )
                row["discrete_n"] = n_discrete
                row["discrete_empirical_w2"] = float(disc.primary.item())
                row["discrete_minus_exact_reference"] = (
                    float(disc.primary.item()) - exact
                )
                rows.append(row)

        # GMM vs GMM sliced / discrete agreement (no exact W2).
        mix_a = two_mode_gmm(dim, separation=2.0, dtype=dtype, device=device)
        mix_b = two_mode_gmm(dim, separation=1.0, dtype=dtype, device=device)
        for n in sample_sizes:
            for seed in seeds:
                gen = torch.Generator(device=device).manual_seed(seed + 1000)
                x = mix_a.sample(n, generator=gen)
                y = mix_b.sample(n, generator=gen)
                sw = SlicedWassersteinEvaluator(
                    n_projections=n_proj, dtype=dtype, seed=seed
                ).compute(x, y)
                projected = ProjectedW2Evaluator(
                    n_projections=projected_n_proj, dtype=dtype, seed=seed
                ).compute(x, y)
                row = {
                    "family": "gmm",
                    "dim": dim,
                    "n": n,
                    "seed": seed,
                    "projected_w2": float(projected.primary.item()),
                    "sliced_w2": float(sw.primary.item()),
                    "sliced_uncertainty": (
                        None if sw.uncertainty is None else float(sw.uncertainty.item())
                    ),
                }
                n_discrete = min(n, discrete_n)
                disc = DiscreteOTEvaluator(max_points=discrete_n, dtype=dtype).compute(
                    x[:n_discrete], y[:n_discrete]
                )
                row["discrete_n"] = n_discrete
                row["discrete_empirical_w2"] = float(disc.primary.item())
                row["abs_diff_sliced_discrete"] = abs(
                    float(sw.primary.item()) - float(disc.primary.item())
                )
                rows.append(row)

    # Stability summary for Spearman readiness (not a gate amendment).
    gauss_rows = [
        r
        for r in rows
        if r["family"] == "gaussian" and "sliced_minus_exact_reference" in r
    ]
    summary: dict[str, Any] = {
        "n_rows": len(rows),
        "gaussian_exact_reference": "Peyre Bures W2",
        "comparison_note": (
            "Differences from Gaussian W2 combine finite-sample error and "
            "estimator or distance mismatch; they are not universal bias estimates."
        ),
        "criteria_note": ("Calibration criteria live here, not in DECISION_GATE.md"),
    }
    if gauss_rows:
        sliced_diffs = [
            abs(r["sliced_minus_exact_reference"]) for r in gauss_rows
        ]
        summary["sliced_abs_difference_mean"] = sum(sliced_diffs) / len(
            sliced_diffs
        )
        summary["sliced_abs_difference_max"] = max(sliced_diffs)
        summary["sliced_diagnostic_within_tolerance"] = (
            summary["sliced_abs_difference_mean"] < 0.5
        )
        entropic_diffs = [
            abs(r["entropic_minus_exact_reference"]) for r in gauss_rows
        ]
        summary["entropic_abs_difference_mean"] = sum(entropic_diffs) / len(
            entropic_diffs
        )
        summary["entropic_abs_difference_max"] = max(entropic_diffs)
        summary["entropic_max_row_residual"] = max(
            r["entropic_row_residual"] for r in gauss_rows
        )
        projected_diffs = [
            abs(r["projected_minus_exact_reference"]) for r in gauss_rows
        ]
        summary["projected_abs_difference_mean"] = sum(projected_diffs) / len(
            projected_diffs
        )
    gmm_comp = [
        r for r in rows if r["family"] == "gmm" and "abs_diff_sliced_discrete" in r
    ]
    if gmm_comp:
        diffs = [r["abs_diff_sliced_discrete"] for r in gmm_comp]
        summary["gmm_sliced_discrete_abs_diff_mean"] = sum(diffs) / len(diffs)
        summary["gmm_diagnostic_within_tolerance"] = (
            summary["gmm_sliced_discrete_abs_diff_mean"] < 1.0
        )

    table_path = run_dir / "calibration_table.json"
    record = _record(
        artifact_id=f"{run_id}:calibration_table",
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
    saved = writer.save_table({"rows": rows, "summary": summary}, table_path, record)
    summary_path = run_dir / "calibration_summary.json"
    summary_record = _record(
        artifact_id=f"{run_id}:calibration_summary",
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
    saved_summary = writer.save_table(summary, summary_path, summary_record)
    artifact_records = [saved.to_dict(), saved_summary.to_dict()]

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
        extras={"mode": "estimator_calibration", "phase": 2, "summary": summary},
    )
    manifest_path = run_dir / "manifest.json"
    writer.save_manifest(manifest, manifest_path)
    return manifest_path
