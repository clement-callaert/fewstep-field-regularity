"""Integration tests for Phase 2 smoke and calibration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fewstep_regularities.cli.main import run_from_overrides


@pytest.mark.integration
def test_phase2_smoke(tmp_path: Path) -> None:
    run_id = "phase2_smoke_test"
    out = tmp_path / "outputs"
    path = run_from_overrides(
        [
            "experiment=phase2_smoke",
            f"experiment.run_id={run_id}",
            f"artifact_policy.output_dir={out}",
            "experiment.seeds=[0,1]",
            "experiment.n_particles=32",
            "artifact_policy.release_ready=false",
        ]
    )
    assert path.is_file()
    assert (path.parent / "results_table.json").is_file()
    resolved = (path.parent / "resolved_config.yaml").read_text(encoding="utf-8")
    assert "name: sliced_wasserstein" in resolved
    assert "name: two_mode_gmm" in resolved
    rows = json.loads((path.parent / "results_table.json").read_text())["rows"]
    assert {row["seed"] for row in rows} == {0, 1}
    import validate_artifacts

    errors = validate_artifacts.validate_path(path.parent)
    assert errors == []


@pytest.mark.integration
def test_phase2_calibration_smoke(tmp_path: Path) -> None:
    run_id = "phase2_calibration_test"
    out = tmp_path / "outputs"
    path = run_from_overrides(
        [
            "experiment=phase2_calibration",
            f"experiment.run_id={run_id}",
            f"artifact_policy.output_dir={out}",
            "experiment.seeds=[0,1]",
            "experiment.sample_sizes=[32]",
            "experiment.discrete_n=16",
            "experiment.n_projections=16",
            "artifact_policy.release_ready=false",
        ]
    )
    assert path.is_file()
    table = json.loads((path.parent / "calibration_table.json").read_text())
    assert table["rows"]
    assert all("projected_w2" in row for row in table["rows"])
    assert all("discrete_empirical_w2" in row for row in table["rows"])
    gaussian_rows = [row for row in table["rows"] if row["family"] == "gaussian"]
    assert all(row["entropic_row_residual"] <= 1e-5 for row in gaussian_rows)
    manifest = json.loads(path.read_text())
    assert len(manifest["artifact_manifest"]) == 2
    import validate_artifacts

    errors = validate_artifacts.validate_path(path.parent)
    assert errors == []
