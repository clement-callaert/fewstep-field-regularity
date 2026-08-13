"""Catch truncated PDFs, folio overprints, unused figures, and Type 3 fonts."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_pack():
    path = ROOT / "scripts" / "pack_arxiv_source.py"
    spec = importlib.util.spec_from_file_location("pack_arxiv_source", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_fonts():
    path = ROOT / "scripts" / "check_pdf_fonts.py"
    spec = importlib.util.spec_from_file_location("check_pdf_fonts", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.analytical
def test_arxiv_pdf_last_page_contains_source_url() -> None:
    pack = _load_pack()
    pdf = ROOT / "paper" / "arxiv" / "main.pdf"
    assert pdf.is_file()
    pack.check_document_complete(pdf, pack.ARXIV_TAIL_MARK)


@pytest.mark.analytical
def test_workshop_pdf_last_page_contains_certificate_close() -> None:
    pack = _load_pack()
    pdf = ROOT / "paper" / "gddl2026" / "main.pdf"
    assert pdf.is_file()
    pack.check_document_complete(pdf, pack.WORKSHOP_TAIL_MARK)


@pytest.mark.analytical
def test_folios_not_overprinted_on_either_pdf() -> None:
    pack = _load_pack()
    pack.check_folio_not_overprinted(ROOT / "paper" / "arxiv" / "main.pdf")
    pack.check_folio_not_overprinted(ROOT / "paper" / "gddl2026" / "main.pdf")


@pytest.mark.analytical
def test_both_compiled_pdfs_have_embedded_fonts_no_type3() -> None:
    fonts = _load_fonts()
    fonts.check_embedded_fonts(ROOT / "paper" / "arxiv" / "main.pdf")
    fonts.check_embedded_fonts(ROOT / "paper" / "gddl2026" / "main.pdf")


@pytest.mark.analytical
def test_fig1_conceptual_not_shipped() -> None:
    for rel in (
        "paper/arxiv/figures/fig1_conceptual.pdf",
        "paper/gddl2026/figures/fig1_conceptual.pdf",
    ):
        assert not (ROOT / rel).exists(), rel


@pytest.mark.analytical
def test_arxiv_pack_omits_unreferenced_figures() -> None:
    pack = _load_pack()
    names = {name for _path, name, _data in pack.collect_members()}
    packed = {name.split("/", 1)[1] for name in names if name.startswith("figures/")}
    tex = (ROOT / "paper" / "arxiv" / "main.tex").read_text(encoding="utf-8")
    used = {Path(p).name for p in pack.includegraphics_paths(tex)}
    assert packed == used
    assert "fig1_conceptual.pdf" not in packed
    assert "fig2_inversions.pdf" not in packed


@pytest.mark.analytical
def test_every_figures_pdf_is_included() -> None:
    pack = _load_pack()
    for rel, tex_rel in (
        ("paper/arxiv/figures", "paper/arxiv/main.tex"),
        ("paper/gddl2026/figures", "paper/gddl2026/main.tex"),
    ):
        tex = (ROOT / tex_rel).read_text(encoding="utf-8")
        used = {Path(p).name for p in pack.includegraphics_paths(tex)}
        on_disk = {p.name for p in (ROOT / rel).glob("*.pdf")}
        extra = sorted(on_disk - used)
        assert extra == [], f"unreferenced PDFs under {rel}: {extra}"


@pytest.mark.analytical
def test_live_tex_has_no_enlargethispage() -> None:
    for rel in ("paper/arxiv/main.tex", "paper/gddl2026/main.tex"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert r"\enlargethispage" not in text, rel
