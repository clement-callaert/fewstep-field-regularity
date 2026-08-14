"""Publication checks for the arXiv compact tree and both manuscripts.

Default mode verifies compact checksums (including the canonical manifest
self-hash), figure sidecars, canonical title, unresolved placeholders,
PDF page counts when PDFs exist, workshop anonymity, and the absence of a
live workshop supplement. Tag existence is a manual owner gate: pass
``--require-tag`` only after creating ``arxiv-v1``.

Any mismatch raises SystemExit. The script never prints a global success
message while skipping a failed item.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
from pathlib import Path

from fewstep_regularities.metadata import (
    CANONICAL_TITLE,
    PLACEHOLDER_TOKENS,
    RETIRED_TITLES,
)
from fewstep_regularities.utils.hashing import sha256_file, sha256_manifest

ROOT = Path(__file__).resolve().parents[1]
RELEASE_TAG = "arxiv-v1"
ARTIFACTS = ROOT / "paper" / "arxiv" / "artifacts"
MANIFEST = ARTIFACTS / "manifest.json"
ARXIV_TEX = ROOT / "paper" / "arxiv" / "main.tex"
ARXIV_PDF = ROOT / "paper" / "arxiv" / "main.pdf"
GDDL_TEX = ROOT / "paper" / "gddl2026" / "main.tex"
GDDL_PDF = ROOT / "paper" / "gddl2026" / "main.pdf"
GDDL_DIR = ROOT / "paper" / "gddl2026"
ARXIV_FIG = ROOT / "paper" / "arxiv" / "figures"
GDDL_FIG = ROOT / "paper" / "gddl2026" / "figures"
LOCKFILE = ROOT / "requirements-lock.txt"

# Long-track GDDL body is 5--9 pages excluding references. The compiled
# PDF also contains the bibliography and the VP-certificate appendix.
GDDL_PDF_PAGE_MIN = 6
GDDL_PDF_PAGE_MAX = 12
ARXIV_PDF_PAGE_MIN = 10
ARXIV_PDF_PAGE_MAX = 28

PUBLICATION_SCAN_ROOTS = (
    ROOT / "README.md",
    ROOT / "CITATION.cff",
    ROOT / "paper" / "arxiv",
    ROOT / "paper" / "gddl2026",
    ROOT / "scripts",
)
SCAN_SUFFIXES = {".tex", ".md", ".json", ".py", ".txt", ".bbl", ".bib", ".cff"}
TITLE_SCAN_FILES = (
    ROOT / "README.md",
    ROOT / "CITATION.cff",
    ROOT / "paper" / "arxiv" / "README.md",
    ROOT / "paper" / "arxiv" / "ARXIV_METADATA.md",
    ROOT / "paper" / "arxiv" / "main.tex",
    ROOT / "paper" / "gddl2026" / "main.tex",
    ROOT / "paper" / "gddl2026" / "README.md",
)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", f"safe.directory={ROOT}", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def pdf_page_count(path: Path) -> int:
    raw = subprocess.check_output(["pdfinfo", str(path)], text=True, errors="replace")
    match = re.search(r"^Pages:\s+(\d+)", raw, flags=re.M)
    if match is None:
        raise RuntimeError(f"pdfinfo produced no page count for {path}")
    return int(match.group(1))


def check_checksums() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return ["missing paper/arxiv/artifacts/manifest.json"]
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = payload.get("files", {})
    if not isinstance(files, dict) or not files:
        return ["compact manifest missing files"]
    for name, expected in files.items():
        if name == "manifest.json":
            actual = sha256_manifest(payload)
            if actual != expected:
                errors.append(
                    f"canonical self-hash mismatch for manifest.json: {actual}"
                )
            continue
        path = ARTIFACTS / name
        if not path.is_file():
            errors.append(f"missing compact artefact {name}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(f"checksum mismatch for {name}: {actual}")
    if payload.get("planned_release_tag") != RELEASE_TAG:
        errors.append("manifest planned_release_tag is not arxiv-v1")
    return errors


def check_figure_sidecars() -> list[str]:
    errors: list[str] = []
    for directory in (ARXIV_FIG, GDDL_FIG):
        if not directory.is_dir():
            errors.append(f"missing figure directory {directory}")
            continue
        for pdf in sorted(directory.glob("*.pdf")):
            sidecar = pdf.with_suffix(pdf.suffix + ".json")
            if not sidecar.is_file():
                errors.append(f"missing figure sidecar {sidecar.relative_to(ROOT)}")
                continue
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
            recorded = payload.get("figure_checksum_sha256")
            actual = sha256_file(pdf)
            if recorded != actual:
                errors.append(
                    f"sidecar hash mismatch for {pdf.name}: recorded "
                    f"{recorded} actual {actual}"
                )
            if (
                payload.get("working_tree_dirty") is None
                and "git_status" not in payload
            ):
                errors.append(f"{sidecar.name} missing source-state dirty flag")
            if (
                payload.get("git_status") == "dirty (regenerate after committing)"
                and payload.get("working_tree_dirty") is not True
            ):
                errors.append(
                    f"{sidecar.name} uses a stale dirty-git slogan without "
                    "working_tree_dirty=true"
                )
    return errors


def check_canonical_title() -> list[str]:
    errors: list[str] = []
    for path in TITLE_SCAN_FILES:
        if not path.is_file():
            errors.append(f"missing title file {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if CANONICAL_TITLE not in text.replace("\n", " ").replace("\\", ""):
            # TeX titles may break the line. Compare collapsed forms.
            collapsed = re.sub(r"\s+", " ", text.replace("\\", ""))
            if CANONICAL_TITLE not in collapsed:
                errors.append(f"canonical title missing from {path.relative_to(ROOT)}")
        for retired in RETIRED_TITLES:
            if retired in text:
                errors.append(
                    f"retired title still present in {path.relative_to(ROOT)}"
                )
    return errors


def _iter_publication_files() -> list[Path]:
    files: list[Path] = []
    for root in PUBLICATION_SCAN_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            # Checker scripts mention placeholder tokens as detection strings.
            if path.name.startswith("check_") and path.suffix == ".py":
                continue
            files.append(path)
    return files


def check_placeholders() -> list[str]:
    errors: list[str] = []
    for path in _iter_publication_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in PLACEHOLDER_TOKENS:
            if token in text:
                errors.append(
                    f"unresolved placeholder {token} in {path.relative_to(ROOT)}"
                )
        if re.search(r"date-released:\s*TODO", text):
            errors.append(f"placeholder date-released in {path.relative_to(ROOT)}")
    return errors


def remaining_placeholders() -> list[str]:
    path = Path(__file__).with_name("check_arxiv_placeholder.py")
    spec = importlib.util.spec_from_file_location("check_arxiv_placeholder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check_arxiv_placeholder.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.remaining_placeholders()


def check_pdf_pages() -> list[str]:
    errors: list[str] = []
    if ARXIV_PDF.is_file():
        pages = pdf_page_count(ARXIV_PDF)
        if not ARXIV_PDF_PAGE_MIN <= pages <= ARXIV_PDF_PAGE_MAX:
            errors.append(
                f"arXiv PDF has {pages} pages; expected "
                f"{ARXIV_PDF_PAGE_MIN}--{ARXIV_PDF_PAGE_MAX}"
            )
    else:
        errors.append("missing paper/arxiv/main.pdf")
    if GDDL_PDF.is_file():
        pages = pdf_page_count(GDDL_PDF)
        if not GDDL_PDF_PAGE_MIN <= pages <= GDDL_PDF_PAGE_MAX:
            errors.append(
                f"workshop PDF has {pages} pages; expected "
                f"{GDDL_PDF_PAGE_MIN}--{GDDL_PDF_PAGE_MAX}"
            )
        # The live workshop file must not claim an 8-page build if it is not.
        gddl_readme = (GDDL_DIR / "README.md").read_text(encoding="utf-8")
        if (
            "eight-page" in gddl_readme.lower() or "8-page" in gddl_readme.lower()
        ) and pages != 8:
            errors.append(
                f"workshop README mentions an 8-page build but PDF has {pages} pages"
            )
    else:
        errors.append("missing paper/gddl2026/main.pdf")
    return errors


def check_workshop_anonymity() -> list[str]:
    errors: list[str] = []
    forbidden = (
        "Clément",
        "Callaert",
        "callaert.clement",
        "clement-callaert",
        "under review",
        "github.com/clement",
    )
    for path in GDDL_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {
            ".tex",
            ".bib",
            ".json",
            ".md",
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in forbidden:
            if token in text:
                errors.append(
                    f"deanonymizing token {token!r} in {path.relative_to(ROOT)}"
                )
    if (GDDL_DIR / "supplement.tex").is_file() or (
        GDDL_DIR / "supplement.pdf"
    ).is_file():
        errors.append(
            "live workshop directory contains supplement.tex/pdf; "
            "GDDL 2026 has no supplement field"
        )
    if GDDL_TEX.is_file():
        tex = GDDL_TEX.read_text(encoding="utf-8")
        if "pdfauthor={Cl" in tex or "pdfauthor={Clement" in tex:
            errors.append("workshop TeX sets a non-empty pdfauthor")
        if "dblblindworkshop" not in tex:
            errors.append("workshop TeX is not dblblindworkshop")
    return errors


def check_lockfile() -> list[str]:
    if not LOCKFILE.is_file():
        return ["missing requirements-lock.txt"]
    text = LOCKFILE.read_text(encoding="utf-8")
    if "torch==" not in text and "torch@" not in text:
        return ["requirements-lock.txt does not pin torch"]
    return []


def check_metadata_files() -> list[str]:
    errors: list[str] = []
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if "TODO" in citation:
        errors.append("CITATION.cff still contains TODO")
    if "date-released:" in citation:
        errors.append(
            "CITATION.cff has date-released; omit it until a real date exists"
        )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "arxiv.org/abs/TODO" in readme:
        errors.append("README.md contains a broken placeholder arXiv URL")
    return errors


def tag_exists() -> bool:
    result = _git("tag", "-l", RELEASE_TAG)
    return result.returncode == 0 and RELEASE_TAG in result.stdout.split()


def collect_errors() -> list[str]:
    errors: list[str] = []
    errors.extend(remaining_placeholders())
    errors.extend(check_placeholders())
    errors.extend(check_checksums())
    errors.extend(check_figure_sidecars())
    errors.extend(check_canonical_title())
    errors.extend(check_metadata_files())
    errors.extend(check_workshop_anonymity())
    errors.extend(check_lockfile())
    errors.extend(check_pdf_pages())
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-tag",
        action="store_true",
        help="Fail if the arxiv-v1 tag is absent (manual publication gate).",
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Skip PDF page-count checks (for pre-build source checks).",
    )
    args = parser.parse_args()

    errors = collect_errors()
    if args.skip_pdf:
        errors = [
            err for err in errors if "main.pdf" not in err and "PDF has" not in err
        ]
    tag_present = tag_exists()
    if args.require_tag and not tag_present:
        errors.append(
            f"release tag {RELEASE_TAG} does not exist; create it on the "
            "final scientific commit before submitting to arXiv"
        )
    if errors:
        raise SystemExit("release check failed:\n  " + "\n  ".join(errors))
    if tag_present:
        print(f"release checks passed; tag {RELEASE_TAG} exists")
    else:
        print(
            "scientific release checks passed; tag "
            f"{RELEASE_TAG} is the remaining manual publication gate"
        )


if __name__ == "__main__":
    main()
