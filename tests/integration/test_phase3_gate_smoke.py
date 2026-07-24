"""Integration test for the registered Phase 3 gate smoke."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from omegaconf import OmegaConf

from fewstep_regularities.cli.main import run_from_overrides


@pytest.mark.integration
def test_phase3_gate_smoke_writes_valid_manifest(tmp_path: Path) -> None:
    run_id = "phase3_gate_smoke_test"
    output_dir = tmp_path / "outputs"
    calibration_path = tmp_path / "calibration_table.json"
    calibration_path.write_text('{"rows": []}', encoding="utf-8")
    manifest_path = run_from_overrides(
        [
            "experiment=phase3_gate",
            f"experiment.run_id={run_id}",
            "experiment.smoke=true",
            "experiment.n_particles=16",
            "experiment.n_projections=8",
            "experiment.metric_n_time=4",
            "experiment.primary_metric_estimator_budget=8",
            "+experiment.inputs.calibration.artifact_id="
            "phase2_calibration:calibration_table",
            f"+experiment.inputs.calibration.path={calibration_path}",
            f"artifact_policy.output_dir={output_dir}",
            "artifact_policy.release_ready=false",
        ]
    )
    run_dir = manifest_path.parent
    data = json.loads((run_dir / "gate_results.json").read_text(encoding="utf-8"))
    observations = data["observations"]
    assert observations
    assert {row["target_family"] for row in observations} == {
        "anisotropic_gaussian",
        "two_mode_gmm",
    }
    assert {row["solver"] for row in observations} == {"euler", "heun", "rk4"}
    assert all(row["actual_nfe"] == row["nfe"] for row in observations)
    resolved = OmegaConf.load(run_dir / "resolved_config.yaml")
    assert list(resolved.experiment.seeds) == [0]
    assert list(resolved.experiment.dimensions) == [2]
    assert list(resolved.experiment.target_names) == [
        "anisotropic_gaussian",
        "two_mode_gmm",
    ]
    assert list(resolved.experiment.path_names) == ["linear"]
    assert list(resolved.experiment.nfe_budgets) == [8]
    assert list(resolved.experiment.metric_estimator_budgets) == [8]
    assert list(resolved.experiment.wasserstein_projection_budgets) == [8]

    import validate_artifacts

    assert validate_artifacts.validate_path(run_dir) == []
