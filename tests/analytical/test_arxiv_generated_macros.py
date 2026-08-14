"""Regression checks for generated arXiv macros and compact artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
NUMBERS = ROOT / "paper" / "arxiv" / "generated" / "numbers.tex"
CENTERED = ROOT / "paper" / "arxiv" / "artifacts" / "centered_blocks.json"
SCALAR = ROOT / "paper" / "arxiv" / "artifacts" / "scalar_counterexample.json"
ROBUST = ROOT / "paper" / "arxiv" / "artifacts" / "robustness_lowrank.json"
NONCENTERED = ROOT / "paper" / "arxiv" / "artifacts" / "noncentered_blocks.json"
QUADRATURE = ROOT / "paper" / "arxiv" / "generated" / "quadrature_comparison.tex"


def _macro(name: str) -> str:
    text = NUMBERS.read_text(encoding="utf-8")
    match = re.search(r"\\newcommand{\\" + re.escape(name) + r"}{(.+)}", text)
    assert match is not None, name
    return match.group(1)


@pytest.mark.analytical
def test_generated_macros_use_continuous_r() -> None:
    assert NUMBERS.is_file()
    strong = _macro("strongRlin")
    assert strong.startswith("2.944")
    assert not strong.startswith("2.947")
    assert _macro("nInversions") == "14"
    assert _macro("nBlocks") == "36"
    assert _macro("nInversionCells") == "5"
    assert _macro("nGeometrySolverCells") == "12"
    assert _macro("nAllNFEInvertCells") == "4"
    assert _macro("arxivReleaseTag") == "arxiv-v1"
    assert _macro("vpHeunBoundNum").isdigit()
    assert _macro("vpHeunIntLeft").isdigit()
    text = NUMBERS.read_text(encoding="utf-8")
    forbidden = "_".join(("ARXIV_RELEASE_COMMIT", "TO_BE_FILLED_AFTER_USER_COMMIT"))
    assert forbidden not in text
    assert "arxivCommitPlaceholder" not in text


@pytest.mark.analytical
def test_compact_centered_inversions() -> None:
    payload = json.loads(CENTERED.read_text(encoding="utf-8"))
    assert payload["n_blocks"] == 36
    assert payload["n_inversions_continuous_R"] == 14
    assert payload["n_inversions_R24"] == 14
    assert all(block["same_R_sign_as_R24"] for block in payload["blocks"])


@pytest.mark.analytical
def test_compact_scalar_certificate() -> None:
    payload = json.loads(SCALAR.read_text(encoding="utf-8"))
    assert payload["ranking_inverted"] is True
    assert payload["r_linear"] == "6797469/3559400"
    assert payload["nfe"] == 8
    assert payload["n_steps"] == 4
    assert payload["evals_per_step"] == 2
    assert payload["planned_release_tag"] == "arxiv-v1"
    assert payload["ranking_inverted"] is True
    left = payload["r_vp_integer_certificate"]["left"]
    right = payload["r_vp_integer_certificate"]["right"]
    assert int(left) < int(right)
    assert len(payload["vp_heun_product_poly"]) == 12


@pytest.mark.analytical
def test_compact_robustness_count() -> None:
    payload = json.loads(ROBUST.read_text(encoding="utf-8"))
    assert payload["n_blocks"] == 66
    assert payload["status"] == "post-hoc"
    assert payload["solver_path_pattern_holds"] is True
    assert len(payload["blocks"]) == 66


@pytest.mark.analytical
def test_compact_noncentered_signed_deltas_and_quadrature_row() -> None:
    payload = json.loads(NONCENTERED.read_text(encoding="utf-8"))
    assert payload["n_blocks"] == 18
    assert payload["n_inversions_continuous_R"] == 11
    for block in payload["blocks"]:
        assert "delta_mean" in block
        assert "delta_cov" in block
        assert "delta_total" in block
        total = block["delta_mean"] + block["delta_cov"]
        assert total == pytest.approx(block["delta_total"], rel=0.0, abs=1e-15)
        assert block["nfe"] in {8, 16, 32}
        assert block["nfe"] % {"euler": 1, "heun": 2, "rk4": 4}[block["solver"]] == 0
    quad = QUADRATURE.read_text(encoding="utf-8")
    assert "non-centered anisotropic" in quad
    assert "1.093537" in quad or "1.093536" in quad
