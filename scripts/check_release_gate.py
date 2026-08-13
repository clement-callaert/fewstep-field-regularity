"""Fail if publication tokens are still unresolved.

Optional fields that cannot be filled honestly (arXiv id, release date)
must be omitted rather than left as TODO. ORCID is recorded when known.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CITATION = ROOT / "CITATION.cff"
SUBMISSION = ROOT / "docs" / "ARXIV_SUBMISSION.md"

TODO_ARXIV = "TODO-ARXIV-ID"
TODO_ORCID = "TODO-ORCID"
ABSTRACT_BEGIN = "<!-- BEGIN ARXIV ABSTRACT -->"
ABSTRACT_END = "<!-- END ARXIV ABSTRACT -->"
ARXIV_ABSTRACT_LIMIT = 1920


def unresolved_tokens() -> list[str]:
    errors: list[str] = []
    readme = README.read_text(encoding="utf-8")
    citation = CITATION.read_text(encoding="utf-8")
    if TODO_ARXIV in readme or TODO_ARXIV in citation:
        errors.append(f"{TODO_ARXIV} is still present in README.md or CITATION.cff")
    if TODO_ORCID in citation:
        errors.append(f"{TODO_ORCID} is still present in CITATION.cff")
    if "arxiv.org/abs/TODO" in readme:
        errors.append("README.md contains a broken placeholder arXiv URL")
    for line in citation.splitlines():
        if line.strip().startswith("date-released") and "TODO" in line:
            errors.append("CITATION.cff date-released is still TODO")
    return errors


def submission_abstract() -> str:
    text = SUBMISSION.read_text(encoding="utf-8")
    if ABSTRACT_BEGIN not in text or ABSTRACT_END not in text:
        raise ValueError("docs/ARXIV_SUBMISSION.md is missing abstract markers")
    body = text.split(ABSTRACT_BEGIN, 1)[1].split(ABSTRACT_END, 1)[0]
    return body.strip()


def main() -> None:
    if os.environ.get("FEWSTEP_RELEASE_GATE") != "1":
        leftover = unresolved_tokens()
        print("release gate is idle (set FEWSTEP_RELEASE_GATE=1 to enforce)")
        if leftover:
            print("unresolved tokens:")
            for item in leftover:
                print(" ", item)
        return
    leftover = unresolved_tokens()
    if leftover:
        raise SystemExit("release gate failed:\n  " + "\n  ".join(leftover))
    print("release gate passed")


if __name__ == "__main__":
    main()
