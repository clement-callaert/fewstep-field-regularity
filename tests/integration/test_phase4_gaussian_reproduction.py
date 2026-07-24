"""Integration tests for the focused Phase 4 reproduction."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from hydra import compose, initialize_config_dir
from omegaconf import DictConfig

from fewstep_regularities.cli.main import run_from_overrides
from fewstep_regularities.experiments.phase4_gaussian_reproduction import (
    validate_release_state,
)


def _phase4_config() -> DictConfig:
    root = Path(__file__).resolve().parents[2]
    with initialize_config_dir(
        version_base=None,
        config_dir=str(root / "configs"),
    ):
        return compose(
            config_name="config",
            overrides=[
                "experiment=phase4_gaussian_reproduction",
                "artifact_policy=phase4_release_ready",
            ],
        )


def test_phase4_release_ready_rejects_dirty_code() -> None:
    cfg = _phase4_config()
    with pytest.raises(RuntimeError, match="clean worktree"):
        validate_release_state(cfg, "dirty")


@pytest.mark.integration
def test_phase4_reproduction_writes_valid_focused_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    manifest_path = run_from_overrides(
        [
            "experiment=phase4_gaussian_reproduction",
            "artifact_policy=strict",
            "experiment.run_id=phase4_gaussian_reproduction_test",
            "experiment.release_ready_required=false",
            "experiment.allow_dirty_code=true",
            f"artifact_policy.output_dir={output_dir}",
        ]
    )
    run_dir = manifest_path.parent
    results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    comparison = json.loads(
        (run_dir / "phase3_comparison.json").read_text(encoding="utf-8")
    )
    validation = json.loads((run_dir / "validation.json").read_text(encoding="utf-8"))
    assert len(results["rows"]) == 72
    assert len(comparison["rows"]) == 72
    assert validation["equal_nfe_validated"] is True
    assert validation["covariance_validated"] is True
    assert validation["phase3_comparison_validated"] is True
    assert validation["all_checks_passed"] is True

    import validate_artifacts

    assert validate_artifacts.validate_path(run_dir) == []
