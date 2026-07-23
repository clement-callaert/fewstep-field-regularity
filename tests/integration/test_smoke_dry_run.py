"""Integration smoke: dry-run CLI writes a valid manifest."""

from __future__ import annotations

from pathlib import Path

from hydra import compose, initialize_config_dir
from scripts.validate_artifacts import validate_path

from fewstep_regularities.cli.main import write_dry_run


def test_dry_run_writes_valid_manifest(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    config_dir = str(root / "configs")
    run_id = "phase0_integration_smoke"
    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(
            config_name="config",
            overrides=[
                "experiment=smoke",
                f"experiment.run_id={run_id}",
                f"artifact_policy.output_dir={tmp_path}",
                f"compute.repo_root={root}",
            ],
        )
    manifest_path = write_dry_run(cfg)
    assert manifest_path.is_file()
    assert (tmp_path / run_id / "resolved_config.yaml").is_file()
    assert (tmp_path / run_id / "unresolved_config.yaml").is_file()
    errors = validate_path(manifest_path.parent)
    assert errors == []
