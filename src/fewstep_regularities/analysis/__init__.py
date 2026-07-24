"""Registered statistical analysis utilities."""

from fewstep_regularities.analysis.correlation import (
    paired_bootstrap_improvement,
    spearman_correlation,
)

__all__ = ["paired_bootstrap_improvement", "spearman_correlation"]
