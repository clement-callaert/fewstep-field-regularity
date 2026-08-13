"""Pack and preflight the arXiv LaTeX source archive.

arXiv compiles the uploaded source. It does not run BibTeX. This script is
the executable form of the five preflight checks:

1. main.bbl is in the archive.
2. The archived main.tex starts with \\pdfoutput=1.
3. Figures are PDF, with relative paths that stay inside the archive.
4. No .aux, .log, .out, or .synctex.gz files are packed.
5. Compiling the archive in a clean directory yields the same page count
   as paper/arxiv/main.pdf, no '??' in the PDF text, embedded fonts, and
   no Type 3 fonts. Bitwise PDF hashes are not compared across TeX
   versions; semantic identity (page count, extracted text, fonts) is.

Usage:
  python scripts/pack_arxiv_source.py
  python scripts/pack_arxiv_source.py --skip-compile
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "paper" / "arxiv"
ZIP_PATH = SRC / "arxiv-source.zip"
PDF_OUTPUT_LINE = r"\pdfoutput=1"
FORBIDDEN_SUFFIXES = (
    ".aux",
    ".log",
    ".out",
    ".blg",
    ".toc",
    ".fls",
    ".fdb_latexmk",
    ".synctex.gz",
)
INCLUDEGRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def _run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, check=True, text=True, capture_output=True)


def ensure_pdfoutput(tex: str) -> str:
    stripped = tex.lstrip("\ufeff")
    if stripped.startswith(PDF_OUTPUT_LINE):
        return stripped
    return PDF_OUTPUT_LINE + "\n" + stripped


def includegraphics_paths(tex: str) -> list[str]:
    return INCLUDEGRAPHICS_RE.findall(tex)


def validate_tex_paths(tex: str) -> None:
    for raw in includegraphics_paths(tex):
        path = raw.strip()
        if path.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", path):
            raise ValueError(f"absolute graphics path: {path}")
        if ".." in Path(path).parts:
            raise ValueError(f"graphics path escapes the archive: {path}")
        if not path.lower().endswith(".pdf"):
            raise ValueError(f"non-PDF figure: {path}")


def collect_members() -> list[tuple[Path, str, bytes | None]]:
    """Return (source path, archive name, optional replacement bytes)."""
    tex_path = SRC / "main.tex"
    bbl_path = SRC / "main.bbl"
    bib_path = SRC / "references.bib"
    for path in (tex_path, bbl_path, bib_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    tex = ensure_pdfoutput(tex_path.read_text(encoding="utf-8"))
    validate_tex_paths(tex)

    members: list[tuple[Path, str, bytes | None]] = [
        (tex_path, "main.tex", tex.encode("utf-8")),
        (bbl_path, "main.bbl", None),
        (bib_path, "references.bib", None),
    ]
    for path in sorted((SRC / "generated").glob("*.tex")):
        members.append((path, f"generated/{path.name}", None))
    used_figures = {Path(p).name for p in includegraphics_paths(tex)}
    dead = SRC / "figures" / "fig1_conceptual.pdf"
    if dead.is_file():
        raise RuntimeError(
            "fig1_conceptual.pdf is not referenced by main.tex and must not "
            "be shipped under paper/arxiv/figures/"
        )
    for path in sorted((SRC / "figures").glob("*.pdf")):
        if path.name not in used_figures:
            continue
        members.append((path, f"figures/{path.name}", None))

    names = [name for _path, name, _data in members]
    if "main.bbl" not in names:
        raise RuntimeError("archive plan is missing main.bbl")
    for name in names:
        lowered = name.lower()
        if lowered.endswith(FORBIDDEN_SUFFIXES) or lowered.endswith(".synctex.gz"):
            raise RuntimeError(f"refusing to pack {name}")
        if name.startswith("/") or ".." in Path(name).parts:
            raise RuntimeError(f"unsafe archive name {name}")
    missing = used_figures - {Path(name).name for name in names if name.startswith("figures/")}
    if missing:
        raise FileNotFoundError(f"figures referenced but not packed: {sorted(missing)}")
    return members


def write_zip(path: Path | None = None) -> Path:
    target = path or ZIP_PATH
    members = collect_members()
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for source, arcname, data in members:
            if data is None:
                zf.write(source, arcname)
            else:
                zf.writestr(arcname, data)
    return target


def archive_page_count() -> int:
    info = subprocess.check_output(["pdfinfo", str(SRC / "main.pdf")], text=True)
    for line in info.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1])
    raise RuntimeError("pdfinfo did not report Pages")


ARXIV_TAIL_MARK = "fewstep-field-regularity"
WORKSHOP_TAIL_MARK = "cross-check, not the proof"


def pdf_page_count(pdf: Path) -> int:
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    for line in info.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1])
    raise RuntimeError(f"pdfinfo did not report Pages for {pdf}")


def pdf_page_text(pdf: Path, page: int) -> str:
    return subprocess.check_output(
        ["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
        text=True,
        errors="replace",
    )


def last_nonempty_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("extracted PDF text is empty")
    return lines[-1]


def check_document_complete(pdf: Path, needle: str) -> None:
    """Fail if the last page of ``pdf`` does not contain ``needle``.

    Catches mid-sentence truncation from ``\\enlargethispage`` stretching
    material past the physical page edge (no Overfull box is emitted).
    """
    pages = pdf_page_count(pdf)
    last = pdf_page_text(pdf, pages)
    if needle not in last:
        preview = last_nonempty_line(last) if last.strip() else "<empty>"
        raise RuntimeError(
            f"{pdf} last page is missing {needle!r}; last nonempty line is "
            f"{preview!r}. The PDF may be truncated."
        )


def check_folio_not_overprinted(pdf: Path) -> None:
    """Fail if body text overlaps the footer folio or extends past the page.

    ``pdftotext -bbox`` emits HTML coordinates (origin at the top-left, y
    downward) and, on current poppler, ``<page>`` tags with no number
    attribute. Pages are counted in document order. The running folio is
    the bottom-most word whose text equals the 1-based page index and that
    sits in the footer band. Glyphs with ``yMax`` past the page height are
    the ``\\enlargethispage`` truncation signature: LaTeX emits no Overfull
    box while still typesetting off the paper.
    """
    raw = subprocess.check_output(
        ["pdftotext", "-bbox", str(pdf), "-"],
        text=True,
        errors="replace",
    )
    page_chunks = [chunk for chunk in re.split(r"(?=<page )", raw) if chunk.startswith("<page")]
    word_re = re.compile(
        r'<word xMin="([^"]+)" yMin="([^"]+)" xMax="([^"]+)" yMax="([^"]+)">([^<]*)</word>'
    )
    collisions: list[str] = []
    for index, chunk in enumerate(page_chunks, start=1):
        height_match = re.search(r'height="([^"]+)"', chunk)
        if height_match is None:
            continue
        height = float(height_match.group(1))
        page_no = str(index)
        words = [
            (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5))
            for m in word_re.finditer(chunk)
        ]
        for x0, y0, x1, y1, text in words:
            if y1 > height + 0.5:
                collisions.append(
                    f"page {page_no}: {text!r} extends past the page edge "
                    f"(yMax={y1:.1f} > height={height:.1f})"
                )
                break
        folios = [w for w in words if w[4] == page_no]
        if not folios:
            continue
        # Bottom-most matching glyph; skip in-body numerals (equation
        # numbers, citations). The running folio sits in the footer band.
        folio = max(folios, key=lambda w: w[1])
        if folio[1] < 0.88 * height:
            continue
        fx0, fy0, fx1, fy1, _ = folio
        for x0, y0, x1, y1, text in words:
            if text == page_no and abs(y0 - fy0) < 1.0:
                continue
            vertical = not (y1 < fy0 - 0.4 or y0 > fy1 + 0.4)
            horizontal = not (x1 < fx0 - 2.0 or x0 > fx1 + 2.0)
            if vertical and horizontal:
                collisions.append(f"page {page_no}: {text!r} overlaps folio")
    if collisions:
        raise RuntimeError("folio overprint: " + "; ".join(collisions[:6]))


def check_embedded_fonts(pdf: Path) -> None:
    """Require embedded fonts and forbid Type 3. Do not compare PDF hashes."""
    import importlib.util

    path = Path(__file__).with_name("check_pdf_fonts.py")
    spec = importlib.util.spec_from_file_location("check_pdf_fonts", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check_pdf_fonts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.check_embedded_fonts(pdf)


def verify_clean_compile(archive: Path) -> None:
    expected_pages = archive_page_count()
    with tempfile.TemporaryDirectory(prefix="arxiv-pack-") as raw:
        tmp = Path(raw)
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
            if "main.bbl" not in names:
                raise RuntimeError("archive is missing main.bbl")
            for name in names:
                lowered = name.lower()
                if lowered.endswith(FORBIDDEN_SUFFIXES) or lowered.endswith(".synctex.gz"):
                    raise RuntimeError(f"archive contains forbidden file {name}")
            zf.extractall(tmp)
        _run(
            [
                "latexmk",
                "-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "main.tex",
            ],
            cwd=tmp,
        )
        built = tmp / "main.pdf"
        if not built.is_file():
            raise RuntimeError("clean compile did not produce main.pdf")
        info = subprocess.check_output(["pdfinfo", str(built)], text=True)
        pages = None
        for line in info.splitlines():
            if line.startswith("Pages:"):
                pages = int(line.split(":", 1)[1])
        if pages != expected_pages:
            raise RuntimeError(f"clean compile has {pages} pages, expected {expected_pages}")
        text = subprocess.check_output(
            ["pdftotext", str(built), "-"],
            text=True,
            errors="replace",
        )
        if "??" in text:
            raise RuntimeError("clean compile PDF contains '??'")
        check_embedded_fonts(built)
        check_document_complete(built, ARXIV_TAIL_MARK)
        check_folio_not_overprinted(built)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-compile",
        action="store_true",
        help="Pack the zip without a clean-directory compile.",
    )
    args = parser.parse_args()
    archive = write_zip()
    print("wrote", archive, "files", len(collect_members()))
    if args.skip_compile:
        return
    verify_clean_compile(archive)
    print("clean compile passed:", archive_page_count(), "pages, embedded fonts, no Type 3")


if __name__ == "__main__":
    main()
