"""Tests for the per-mode log-covariance schedule and ranking grids."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from fewstep_regularities.analysis.affine_flow import scalar_drift, scalar_variance
from fewstep_regularities.analysis.ranking_grids import (
    HEUN_BUDGETS,
    linear_endpoint_drifts,
    linear_vp_inversion,
    log_covariance_cauchy_schwarz,
    path_regularity,
    path_w2,
    three_path_scores,
    vp_never_changes_sign,
)

ROOT = Path(__file__).resolve().parents[2]
GEOMETRIES = ROOT / "paper" / "arxiv" / "artifacts" / "geometries.json"

AUDITOR_HEUN8_INVERT = (0.25, 0.5, 3.0, 4.0, 6.0)
AUDITOR_HEUN8_NO_INVERT = (0.05, 0.1, 0.9, 1.5, 2.0, 9.0, 16.0, 36.0, 100.0)


@pytest.mark.analytical
def test_log_covariance_is_constant_drift_and_cs_minimizer() -> None:
    eigenvalue = 4.0
    integral, regularity = log_covariance_cauchy_schwarz(eigenvalue)
    assert integral == pytest.approx(0.5 * math.log(4.0), abs=0.0, rel=1e-15)
    assert regularity == pytest.approx(integral**2, abs=0.0, rel=1e-15)
    for time in (0.0, 0.25, 0.5, 1.0):
        assert scalar_drift("log_covariance", eigenvalue, time) == pytest.approx(
            integral, abs=0.0, rel=1e-15
        )
        assert scalar_variance("log_covariance", eigenvalue, time) == pytest.approx(
            eigenvalue**time, rel=1e-12, abs=1e-12
        )
    assert path_regularity("log_covariance", [eigenvalue]) == pytest.approx(
        regularity, abs=0.0, rel=1e-15
    )
    assert path_regularity("linear", [eigenvalue]) > regularity
    assert path_regularity("variance_preserving", [eigenvalue]) > regularity


@pytest.mark.analytical
def test_linear_forced_sign_change_and_vp_no_sign_change() -> None:
    for eigenvalue in (0.05, 4.0, 100.0):
        start, end = linear_endpoint_drifts(eigenvalue)
        assert start == pytest.approx(-1.0, abs=1e-15)
        assert end == pytest.approx(1.0, abs=1e-15)
        assert vp_never_changes_sign(eigenvalue)


@pytest.mark.analytical
def test_heun_nfe8_inversion_control_points() -> None:
    for value in AUDITOR_HEUN8_INVERT:
        assert linear_vp_inversion([value], "heun", 8), value
    for value in AUDITOR_HEUN8_NO_INVERT:
        assert not linear_vp_inversion([value], "heun", 8), value
    # Euler inverts at some extreme λ on this control set (0.05, 0.1, 9, 16, 36).
    euler_hits = [
        value
        for value in AUDITOR_HEUN8_INVERT + AUDITOR_HEUN8_NO_INVERT
        if linear_vp_inversion([value], "euler", 8)
    ]
    assert euler_hits == [0.05, 0.1, 9.0, 16.0, 36.0]


@pytest.mark.analytical
def test_heun_lambda4_inverts_at_every_tested_budget() -> None:
    for nfe in HEUN_BUDGETS:
        assert linear_vp_inversion([4.0], "heun", nfe), nfe
        assert not linear_vp_inversion([4.0], "euler", nfe), nfe


@pytest.mark.analytical
def test_rk4_lambda4_except_nfe_8_and_12() -> None:
    assert not linear_vp_inversion([4.0], "rk4", 8)
    assert not linear_vp_inversion([4.0], "rk4", 12)
    for nfe in (4, 16, 24, 32, 64):
        assert linear_vp_inversion([4.0], "rk4", nfe), nfe


@pytest.mark.analytical
def test_log_covariance_has_smallest_r_and_often_smallest_w2() -> None:
    payload = json.loads(GEOMETRIES.read_text(encoding="utf-8"))
    eigs = payload["low_rank_d2"]["eigenvalues"]
    scores = three_path_scores(eigs, "heun", 8)
    assert scores["log_covariance"].regularity <= min(
        scores["linear"].regularity, scores["variance_preserving"].regularity
    )
    # Existence: the R-minimizer is a third path, not a copy of linear or VP.
    assert scores["log_covariance"].path == "log_covariance"
    assert path_w2("log_covariance", "heun", eigs, 8) == pytest.approx(
        scores["log_covariance"].w2, rel=0.0, abs=1e-15
    )


@pytest.mark.analytical
def test_centered_geometry_solver_cells() -> None:
    payload = json.loads(
        (ROOT / "paper" / "arxiv" / "artifacts" / "centered_blocks.json").read_text(
            encoding="utf-8"
        )
    )
    cells: dict[tuple[str, int, str], list[bool]] = {}
    for block in payload["blocks"]:
        key = (block["family"], int(block["dim"]), block["solver"])
        cells.setdefault(key, []).append(bool(block["inversion_R"]))
    assert len(cells) == 12
    any_invert = sum(any(flags) for flags in cells.values())
    all_invert = sum(all(flags) for flags in cells.values())
    assert any_invert == 5
    assert all_invert == 4
