"""Pack and preflight the arXiv LaTeX source archive.

arXiv compiles the uploaded source. It does not run BibTeX. This script is
the executable form of the five preflight checks:

1. main.bbl is in the archive.
2. The archived main.tex starts with \\pdfoutput=1.
3. Figures are PDF, with relative paths that stay inside the archive.
4. No .aux, .log, .out, or .synctex.gz files are packed.
5. Compiling the archive in a clean directory yields the same page count
   as paper/arxiv/main.pdf and no '??' in the PDF text.

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
    print("clean compile passed:", archive_page_count(), "pages, no '??'")


if __name__ == "__main__":
    main()
