"""Hydra CLI entry point for dry-run and future experiments."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hydra import compose, initialize_config_dir
from omegaconf import DictConfig, OmegaConf

from fewstep_regularities.artifacts.manifest import RunManifest
from fewstep_regularities.artifacts.writer import FilesystemArtifactWriter
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


def default_repo_root() -> Path:
    """Return repository root from package location."""
    # Package lives at src/fewstep_regularities.
    return Path(__file__).resolve().parents[3]


def default_config_dir() -> Path:
    """Return absolute Hydra config directory."""
    return default_repo_root() / "configs"


def repo_root_from_config(cfg: DictConfig) -> Path:
    """Resolve repository root from config without using cwd implicitly."""
    configured = OmegaConf.select(cfg, "compute.repo_root")
    if configured:
        return Path(str(configured)).resolve()
    return default_repo_root()


def build_dry_run_manifest(
    cfg: DictConfig, start: datetime, end: datetime
) -> RunManifest:
    """Build a dry-run manifest from the resolved config."""
    root = repo_root_from_config(cfg)
    resolved = OmegaConf.to_container(cfg, resolve=True)
    resolved_text = OmegaConf.to_yaml(cfg, resolve=True)
    config_hash = sha256_text(resolved_text)
    seeds = list(cfg.experiment.seeds)
    run_id = str(cfg.experiment.run_id)
    output_dir = Path(str(cfg.artifact_policy.output_dir))
    if not output_dir.is_absolute():
        output_dir = (root / output_dir).resolve()
    run_dir = output_dir / run_id
    return RunManifest(
        run_id=run_id,
        git_commit=git_commit(root),
        config_hash=config_hash,
        code_status=git_code_status(root),
        software_environment_hash=software_environment_hash(),
        random_seeds=seeds,
        start_time=start.isoformat(),
        end_time=end.isoformat(),
        runtime_s=(end - start).total_seconds(),
        artifact_manifest=[],
        resolved_config_path=str(run_dir / "resolved_config.yaml"),
        unresolved_config_path=str(run_dir / "unresolved_config.yaml"),
        command_line=" ".join(sys.argv),
        python_version=python_version(),
        package_lock_hash=package_lock_hash(root),
        cuda_version=cuda_version(),
        gpu_name=gpu_name(),
        release_ready=bool(cfg.artifact_policy.release_ready),
        extras={
            "mode": str(cfg.experiment.mode),
            "hypotheses": list(cfg.experiment.hypotheses),
            "decision_gate": str(cfg.experiment.decision_gate),
            "resolved_config": resolved,
        },
    )


def write_dry_run(cfg: DictConfig) -> Path:
    """Resolve config and write a dry-run manifest. No benchmark is run."""
    start = datetime.now(UTC)
    root = repo_root_from_config(cfg)
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

    end = datetime.now(UTC)
    manifest = build_dry_run_manifest(cfg, start, end)
    writer = FilesystemArtifactWriter()
    manifest_path = run_dir / "manifest.json"
    writer.save_manifest(manifest, manifest_path)
    return manifest_path


def run_from_overrides(overrides: list[str] | None = None) -> Path:
    """Compose config from absolute config dir and execute dry-run."""
    config_dir = str(default_config_dir())
    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(config_name="config", overrides=overrides or [])
    mode = str(cfg.experiment.mode)
    if mode != "dry_run":
        msg = (
            f"Unsupported mode {mode!r}. Phase 0 only supports dry_run. "
            "Do not launch the gate or full benchmark yet."
        )
        raise RuntimeError(msg)
    return write_dry_run(cfg)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point.

    Phase 0 supports ``experiment.mode=dry_run`` only.
    Remaining argv tokens are Hydra-style overrides.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    path = run_from_overrides(args)
    summary: dict[str, Any] = {"manifest_path": str(path), "mode": "dry_run"}
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
