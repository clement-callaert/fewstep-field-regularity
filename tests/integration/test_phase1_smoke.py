"""Integration test for Phase 1 Gaussian smoke experiment."""

from __future__ import annotations

import pytest

from fewstep_regularities.cli.main import run_from_overrides


@pytest.mark.integration
def test_phase1_smoke_writes_valid_manifest() -> None:
    path = run_from_overrides(["experiment=phase1_smoke"])
    assert path.is_file()
    run_dir = path.parent
    assert (run_dir / "resolved_config.yaml").is_file()
    assert (run_dir / "results_table.json").is_file()

    # Validate with the project script.
    import validate_artifacts

    errors = validate_artifacts.validate_path(run_dir)
    assert errors == []
