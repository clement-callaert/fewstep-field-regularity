"""Hygiene checks for the arXiv release tree."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_placeholder_module():
    path = ROOT / "scripts" / "check_arxiv_placeholder.py"
    spec = importlib.util.spec_from_file_location("check_arxiv_placeholder", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.analytical
def test_arxiv_tree_has_no_commit_placeholder() -> None:
    module = _load_placeholder_module()
    remaining = module.remaining_placeholders()
    assert remaining == []


@pytest.mark.analytical
def test_gddl_workshop_source_is_anonymous() -> None:
    root = ROOT / "paper" / "gddl2026"
    assert root.is_dir()
    forbidden = (
        "Clément",
        "Callaert",
        "callaert.clement",
        "clement-callaert",
        "under review",
        "github.com/clement",
    )
    hits: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".tex", ".bib", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in forbidden:
            if token in text:
                hits.append(f"{path.relative_to(ROOT)}: {token}")
    assert hits == []
    main = (root / "main.tex").read_text(encoding="utf-8")
    assert "dblblindworkshop" in main
    assert "[final]" not in main
    assert "neuripsfinal" not in main.lower()


@pytest.mark.analytical
def test_nfe_accounting_in_compact_centered_blocks() -> None:
    import json

    payload = json.loads(
        (ROOT / "paper/arxiv/artifacts/centered_blocks.json").read_text(
            encoding="utf-8"
        )
    )
    stages = {"euler": 1, "heun": 2, "rk4": 4}
    for block in payload["blocks"]:
        nfe = int(block["nfe"])
        assert nfe in {8, 16, 32}
        assert nfe % stages[block["solver"]] == 0
