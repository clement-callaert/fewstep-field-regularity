"""Tests for the restructured arXiv manuscript and in-family census."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_structure():
    path = ROOT / "scripts" / "check_arxiv_structure.py"
    spec = importlib.util.spec_from_file_location("check_arxiv_structure", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.analytical
def test_arxiv_section_skeleton() -> None:
    module = _load_structure()
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    body, appendix = module.body_and_appendix(text)
    positions = []
    for pattern in module.REQUIRED_SECTIONS:
        match = __import__("re").search(pattern, body)
        assert match is not None, pattern
        positions.append(match.start())
    assert positions == sorted(positions)
    for pattern in module.APPENDIX_SECTIONS:
        assert __import__("re").search(pattern, appendix), pattern
    assert body.count(r"\section{") == 7
    assert r"\section{Reproducibility statement}" not in body
    assert r"\section{Limitations}" in body
    assert body.rfind(r"\section{Conclusion}") < body.rfind(r"\section{Limitations}")


@pytest.mark.analytical
def test_arxiv_body_has_no_pipeline_tokens() -> None:
    module = _load_structure()
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    body, _appendix = module.body_and_appendix(text)
    for token in module.BODY_FORBIDDEN:
        assert token not in body, token


@pytest.mark.analytical
def test_arxiv_abstract_length_and_plain_macros() -> None:
    module = _load_structure()
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    abstract = module.abstract_text(text)
    plain = module.strip_tex(abstract)
    assert len(plain) <= 1920, len(plain)
    metadata = (ROOT / "paper" / "arxiv" / "ARXIV_METADATA.md").read_text(
        encoding="utf-8"
    )
    meta_abs = metadata.split("## Abstract (plain text, for the abstract field)")[1]
    meta_abs = meta_abs.split("## Categories")[0].strip()
    assert len(meta_abs) <= 1920, len(meta_abs)
    assert module.custom_macros_in_abstract(abstract) == []
    assert 165 <= module.abstract_word_count(abstract) <= 190
    assert "disclaimer" not in plain.lower()
    assert "no venue" not in plain.lower()
    assert "Lipschitz constant of the marginal" not in abstract
    assert "probability flow ODE" not in abstract.lower() or "score-based" in abstract.lower()


@pytest.mark.analytical
def test_arxiv_forbidden_phrasing_absent() -> None:
    module = _load_structure()
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    assert module.forbidden_phrase_hits(text) == []
    assert r"\alpha^2,\sigma^2\in C^1([0,1])" in text
    assert r"\alpha^2\ge 0" in text
    assert r"When $M=1$" in text
    assert "confirmatory Phase~4" in text
    assert "Reserve ``pre-registered''" in text
    assert "low-rank $d=8$, Euler, NFE~$8$" in text
    assert "on the same block" not in text


@pytest.mark.analytical
def test_arxiv_search_phrases_in_abstract_and_intro() -> None:
    module = _load_structure()
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    abstract = module.strip_tex(module.abstract_text(text)).lower()
    intro = module.strip_tex(module.intro_text(text)).lower()
    traffic = (
        "flow matching",
        "stochastic interpolants",
        "few-step sampling",
        "schedule design",
        "Lipschitz",
    )
    for phrase in traffic:
        assert phrase.lower() in abstract, phrase
    for phrase in module.SEARCH_PHRASES:
        assert phrase.lower() in abstract or phrase.lower() in intro, phrase


@pytest.mark.analytical
def test_arxiv_thirtysix_restriction() -> None:
    module = _load_structure()
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    bad = module.thirty_six_without_restriction(text)
    assert bad == []


@pytest.mark.analytical
def test_arxiv_not_shared_needs_eigenvalue_hypothesis() -> None:
    module = _load_structure()
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    bad = module.not_shared_without_eigenvalue_hypothesis(text)
    assert bad == []


@pytest.mark.analytical
def test_arxiv_contributions_at_most_four_with_refs() -> None:
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    intro = text.split(r"\section{Background}")[0]
    items = intro.split(r"\begin{itemize}")[1].split(r"\end{itemize}")[0]
    n_items = items.count(r"\item")
    assert n_items <= 4
    assert n_items == 4
    assert items.count(r"\ref{") >= 4


@pytest.mark.analytical
def test_arxiv_body_float_budget() -> None:
    module = _load_structure()
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    body, appendix = module.body_and_appendix(text)
    n_fig, n_tab = module.body_floats(body)
    assert n_fig <= 4
    assert n_tab <= 2
    assert n_fig == 4
    assert n_tab == 2
    assert r"\begin{figure}" in appendix
    assert r"\begin{table}" in appendix


@pytest.mark.analytical
def test_arxiv_no_pvalue_or_significance_theatre() -> None:
    module = _load_structure()
    text = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    body, appendix = module.body_and_appendix(text)
    lowered = body.lower()
    assert "p-value" not in lowered
    assert "pvalue" not in lowered
    assert "significant" not in lowered
    assert "error bar" not in lowered
    assert "wald" not in lowered
    assert "clopper" in body.lower() or "clopper" in appendix.lower()


@pytest.mark.analytical
def test_in_family_vp_vs_scalar_census() -> None:
    import json

    from fewstep_regularities.analysis.ranking_grids import (
        GEOM_KEYS,
        PRIMARY_NFE,
        SOLVERS,
        vp_scalar_logcov_inversion,
    )

    payload = json.loads(
        (ROOT / "paper" / "arxiv" / "artifacts" / "geometries.json").read_text(
            encoding="utf-8"
        )
    )
    expected = {
        ("anisotropic", 2, "euler", 16),
        ("anisotropic", 2, "euler", 32),
        ("anisotropic", 8, "euler", 8),
        ("anisotropic", 8, "euler", 16),
        ("anisotropic", 8, "euler", 32),
        ("low-rank", 2, "euler", 8),
        ("low-rank", 2, "heun", 8),
        ("low-rank", 2, "heun", 16),
        ("low-rank", 2, "heun", 32),
    }
    found: set[tuple[str, int, str, int]] = set()
    cells: dict[tuple[str, int, str], list[bool]] = {}
    for key, family, dim in GEOM_KEYS:
        eigs = payload[key]["eigenvalues"]
        for solver in SOLVERS:
            flags: list[bool] = []
            for nfe in PRIMARY_NFE:
                flag = vp_scalar_logcov_inversion(eigs, solver, nfe)
                flags.append(flag)
                if flag:
                    found.add((family, dim, solver, nfe))
            cells[(family, dim, solver)] = flags
    assert found == expected
    assert sum(any(flags) for flags in cells.values()) == 4


@pytest.mark.analytical
def test_shared_logcov_matches_per_mode_when_m_equals_lambda() -> None:
    import math

    from fewstep_regularities.analysis.affine_flow import (
        scalar_drift,
        scalar_variance,
        shared_logcov_path,
    )

    for lam, time in ((4.0, 0.0), (4.0, 0.5), (0.25, 0.3)):
        encoded = shared_logcov_path(lam)
        assert scalar_variance(encoded, lam, time) == pytest.approx(
            scalar_variance("log_covariance", lam, time), rel=0.0, abs=1e-12
        )
        assert scalar_drift(encoded, lam, time) == pytest.approx(
            0.5 * math.log(lam), rel=0.0, abs=1e-12
        )


@pytest.mark.analytical
def test_clopper_pearson_fifty_of_fifty() -> None:
    from fewstep_regularities.analysis.census_statistics import clopper_pearson

    low, high = clopper_pearson(50, 50)
    assert high == pytest.approx(1.0)
    assert low == pytest.approx(0.9288782635357954, rel=0.0, abs=1e-9)


@pytest.mark.analytical
def test_compact_in_family_artifact_counts() -> None:
    import json

    payload = json.loads(
        (ROOT / "paper" / "arxiv" / "artifacts" / "in_family_blocks.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["n_blocks"] == 36
    assert payload["n_inversions"] == 9
    assert payload["n_cells"] == 4
    assert payload["status"] == "post-hoc"
