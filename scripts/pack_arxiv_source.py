"""Build paper/arxiv/arxiv-source.zip from portable TeX sources."""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "paper" / "arxiv"
ZIP_PATH = SRC / "arxiv-source.zip"

INCLUDE = [
    SRC / "main.tex",
    SRC / "main.bbl",
    SRC / "references.bib",
]


def main() -> None:
    members: list[tuple[Path, str]] = []
    for path in INCLUDE:
        if not path.is_file():
            raise FileNotFoundError(path)
        members.append((path, path.name))
    for path in sorted((SRC / "generated").glob("*.tex")):
        members.append((path, f"generated/{path.name}"))
    for path in sorted((SRC / "figures").glob("*.pdf")):
        members.append((path, f"figures/{path.name}"))

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, arcname in members:
            zf.write(path, arcname)
    print("wrote", ZIP_PATH, "files", len(members))


if __name__ == "__main__":
    main()
