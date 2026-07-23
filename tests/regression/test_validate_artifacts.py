"""Regression tests for artifact validation."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_artifacts import validate_path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_valid_fixture_passes() -> None:
    errors = validate_path(FIXTURES / "valid_run")
    assert errors == []


def test_dirty_release_ready_rejected() -> None:
    errors = validate_path(FIXTURES / "dirty_release_ready")
    assert any("release-ready" in err for err in errors)


def test_missing_hashes_rejected() -> None:
    errors = validate_path(FIXTURES / "missing_hashes")
    assert any("missing hash" in err for err in errors)


def test_paper_manifest_schema() -> None:
    root = Path(__file__).resolve().parents[2]
    manifest_path = root / "papers" / "manifest.json"
    assert manifest_path.is_file()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "papers" in data
    assert len(data["papers"]) >= 10
    for paper in data["papers"]:
        assert "title" in paper
        assert "source_url" in paper
        assert "retrieval_status" in paper
