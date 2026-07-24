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
from fewstep_regularities.utils.hashing import sha256_file


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


def _build_phase3_test_inputs(tmp_path: Path) -> dict[str, Path]:
    calibration_path = tmp_path / "calibration_table.json"
    calibration_path.write_text('{"rows": []}', encoding="utf-8")
    phase3_output = tmp_path / "phase3_outputs"
    manifest_path = run_from_overrides(
        [
            "experiment=phase3_gate",
            "experiment.run_id=phase3_gaussian_reference_test",
            "experiment.target_names=[anisotropic_gaussian,low_rank_gaussian]",
            "experiment.metric_names=[averaged_squared_lipschitz_proxy]",
            "experiment.metric_estimator_budgets=[128]",
            "+experiment.inputs.calibration.artifact_id="
            "phase2_calibration:calibration_table",
            f"+experiment.inputs.calibration.path={calibration_path}",
            f"artifact_policy.output_dir={phase3_output}",
            "artifact_policy.release_ready=false",
        ]
    )
    gate_path = manifest_path.parent / "gate_results.json"
    inversion_path = tmp_path / "inversions.json"
    interaction_path = tmp_path / "interactions.json"
    inversion_path.write_text("{}", encoding="utf-8")
    interaction_path.write_text("{}", encoding="utf-8")
    return {
        "gate": gate_path,
        "inversions": inversion_path,
        "interactions": interaction_path,
    }


@pytest.mark.integration
def test_phase4_reproduction_writes_valid_focused_artifacts(tmp_path: Path) -> None:
    inputs = _build_phase3_test_inputs(tmp_path)
    output_dir = tmp_path / "outputs"
    manifest_path = run_from_overrides(
        [
            "experiment=phase4_gaussian_reproduction",
            "artifact_policy=strict",
            "experiment.run_id=phase4_gaussian_reproduction_test",
            "experiment.release_ready_required=false",
            "experiment.allow_dirty_code=true",
            f"experiment.inputs.phase3_gate.path={inputs['gate']}",
            f"experiment.inputs.phase3_gate.sha256={sha256_file(inputs['gate'])}",
            f"experiment.inputs.phase3_inversions.path={inputs['inversions']}",
            "experiment.inputs.phase3_inversions.sha256="
            f"{sha256_file(inputs['inversions'])}",
            f"experiment.inputs.phase3_interactions.path={inputs['interactions']}",
            "experiment.inputs.phase3_interactions.sha256="
            f"{sha256_file(inputs['interactions'])}",
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
