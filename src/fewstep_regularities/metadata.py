"""Canonical publication metadata.

A single source for the title used in PDFs, README, CITATION.cff, and
release checks. Do not invent an arXiv identifier, DOI, or release date.
"""

from __future__ import annotations

CANONICAL_TITLE = (
    "Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching "
    "Schedules: A Certified Gaussian Counterexample"
)

# Historical title retained only so checkers can flag stale copies.
RETIRED_TITLES = (
    "Few-Step Flow-Matching Error Can Be Misranked by Averaged Jacobian "
    "Regularity: A Certified Gaussian Counterexample",
)

PLACEHOLDER_TOKENS = (
    "TODO-ARXIV-ID",
    "TODO-ORCID",
    "FIXME",
    "TBD",
)
