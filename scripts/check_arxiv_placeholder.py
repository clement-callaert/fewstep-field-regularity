"""Fail if the retired arXiv commit placeholder remains in publication files."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = "_".join(("ARXIV_RELEASE_COMMIT", "TO_BE_FILLED_AFTER_USER_COMMIT"))
SCAN_ROOTS = (
    ROOT / "paper" / "arxiv",
    ROOT / "scripts",
    ROOT / "tests" / "analytical",
    ROOT / "audit",
)
TEXT_SUFFIXES = {".tex", ".md", ".json", ".py", ".txt", ".bbl", ".bib"}


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
                continue
            files.append(path)
    return files


def remaining_placeholders() -> list[str]:
    remaining: list[str] = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        if FORBIDDEN in text:
            remaining.append(str(path.relative_to(ROOT)))
    return remaining


def main() -> None:
    remaining = remaining_placeholders()
    if remaining:
        raise SystemExit(
            "Forbidden commit placeholder still present in:\n  "
            + "\n  ".join(remaining)
        )
    print("no commit placeholder remains")


if __name__ == "__main__":
    main()
