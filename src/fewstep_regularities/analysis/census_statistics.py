"""Census summaries and the one legitimate inferential interval in the paper."""

from __future__ import annotations

from collections.abc import Sequence

from scipy.stats import binomtest


def clopper_pearson(
    successes: int,
    n: int,
    *,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Return an exact Clopper--Pearson interval for a binomial proportion.

    Inputs: integer successes and trials; confidence level in (0, 1).
    Outputs: ``(low, high)`` bounds in [0, 1].
    Units: dimensionless proportion of geometries.
    Precision: SciPy ``binomtest`` exact method; no Wald approximation.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= successes <= n:
        raise ValueError("successes must lie in [0, n]")
    result = binomtest(successes, n)
    interval = result.proportion_ci(confidence_level=confidence, method="exact")
    return float(interval.low), float(interval.high)


def kendall_tau_from_flags(inverted: Sequence[bool]) -> float:
    """Return (n_agree - n_invert) / n on a complete two-path census."""
    n = len(inverted)
    if n <= 0:
        raise ValueError("need at least one block")
    n_invert = sum(bool(flag) for flag in inverted)
    n_agree = n - n_invert
    return (n_agree - n_invert) / n
