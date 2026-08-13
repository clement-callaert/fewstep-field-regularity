"""Registered statistical analysis utilities.

Imports are lazy so the scalar certificate can run without torch, hydra,
or scipy. Submodules still import what they need.
"""

from __future__ import annotations

from typing import Any

__all__ = ["paired_bootstrap_improvement", "spearman_correlation"]


def __getattr__(name: str) -> Any:
    if name in {"paired_bootstrap_improvement", "spearman_correlation"}:
        from fewstep_regularities.analysis.correlation import (
            paired_bootstrap_improvement,
            spearman_correlation,
        )

        values = {
            "paired_bootstrap_improvement": paired_bootstrap_improvement,
            "spearman_correlation": spearman_correlation,
        }
        return values[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
