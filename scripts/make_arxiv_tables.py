"""Generate arXiv numerical macros and inversion tables.

This entry point is an alias of ``make_arxiv_compact_artifacts``. Headline
macros use the continuous integral R, not the historical 24-node estimator.
Running this script must not restore R24 values into ``numbers.tex``.
"""

from __future__ import annotations

import runpy
from pathlib import Path


def main() -> None:
    """Delegate to the compact-artifact generator."""
    runpy.run_path(
        str(Path(__file__).resolve().with_name("make_arxiv_compact_artifacts.py")),
        run_name="__main__",
    )


if __name__ == "__main__":
    main()
