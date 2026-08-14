"""Require embedded fonts and forbid Type 3 in compiled PDFs.

Used for both the arXiv preprint and the GDDL workshop PDF. The arXiv
packer also calls ``check_embedded_fonts`` on a clean-directory rebuild.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDFS = (
    ROOT / "paper" / "arxiv" / "main.pdf",
    ROOT / "paper" / "gddl2026" / "main.pdf",
)


def check_embedded_fonts(pdf: Path) -> None:
    """Require embedded fonts and forbid Type 3. Do not compare PDF hashes."""
    raw = subprocess.check_output(["pdffonts", str(pdf)], text=True, errors="replace")
    lines = [line for line in raw.splitlines() if line.strip()]
    if len(lines) < 3:
        raise RuntimeError(f"pdffonts produced no font table for {pdf}")
    type3 = []
    unembedded = []
    trail = re.compile(
        r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", re.IGNORECASE
    )
    for line in lines[2:]:
        if re.search(r"Type\s*3", line, flags=re.IGNORECASE):
            type3.append(line.strip())
        match = trail.search(line)
        if match and match.group(1).lower() == "no":
            unembedded.append(line.strip())
    if type3:
        raise RuntimeError(f"Type 3 font in PDF {pdf}: " + type3[0])
    if unembedded:
        raise RuntimeError(f"unembedded font in PDF {pdf}: " + unembedded[0])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdfs",
        nargs="*",
        type=Path,
        help="PDF files to check (default: arXiv and GDDL main.pdf).",
    )
    args = parser.parse_args()
    pdfs = [Path(p) for p in args.pdfs] if args.pdfs else list(DEFAULT_PDFS)
    for pdf in pdfs:
        if not pdf.is_file():
            raise SystemExit(f"missing PDF: {pdf}")
        check_embedded_fonts(pdf)
        print("fonts ok (embedded, no Type 3):", pdf)


if __name__ == "__main__":
    main()
