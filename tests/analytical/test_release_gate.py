"""Publication-token gate. Skipped unless FEWSTEP_RELEASE_GATE=1."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from check_release_gate import (
    ARXIV_ABSTRACT_LIMIT,
    submission_abstract,
    unresolved_tokens,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.analytical
def test_arxiv_source_archive_plan_includes_bbl() -> None:
    import pack_arxiv_source as pack

    names = [name for _path, name, _data in pack.collect_members()]
    assert "main.bbl" in names
    assert names[0] == "main.tex"
    assert any(name.startswith("figures/") and name.endswith(".pdf") for name in names)
    assert not any(name.lower().endswith(pack.FORBIDDEN_SUFFIXES) for name in names)


@pytest.mark.analytical
def test_arxiv_submission_abstract_within_form_limit() -> None:
    abstract = submission_abstract()
    assert abstract
    assert len(abstract) <= ARXIV_ABSTRACT_LIMIT, len(abstract)
    metadata = (ROOT / "paper" / "arxiv" / "ARXIV_METADATA.md").read_text(
        encoding="utf-8"
    )
    meta_abs = metadata.split("## Abstract (plain text, for the abstract field)")[1]
    meta_abs = meta_abs.split("## Categories")[0].strip()
    assert abstract == meta_abs


@pytest.mark.analytical
def test_release_tokens_resolved_after_notification() -> None:
    if os.environ.get("FEWSTEP_RELEASE_GATE") != "1":
        pytest.skip("set FEWSTEP_RELEASE_GATE=1 after the GDDL notification")
    leftover = unresolved_tokens()
    assert leftover == [], leftover
