"""Nested correlation and paired bootstrap utilities."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.stats import spearmanr

FloatArray = NDArray[np.float64]


def _validate_vector(values: FloatArray, name: str) -> None:
    if not isinstance(values, np.ndarray):
        raise TypeError(f"{name} must be a numpy array")
    if values.dtype != np.float64:
        raise TypeError(f"{name} must have dtype float64")
    if values.ndim != 1:
        raise ValueError(f"{name} must have shape (n,)")
    if values.size < 2:
        raise ValueError(f"{name} must contain at least two values")
    if not np.isfinite(values).all():
        raise ValueError(f"{name} must contain only finite values")


def spearman_correlation(predictor: FloatArray, outcome: FloatArray) -> float:
    """Compute signed Spearman rank correlation on CPU.

    Args:
        predictor: Float64 predictor values with shape ``(n,)``.
        outcome: Float64 outcome values with shape ``(n,)``.

    Returns:
        Scalar signed Spearman correlation. A constant input returns zero.

    Dtype:
        Both inputs must be float64. No cast is made.

    Device:
        NumPy CPU arrays only.

    Mathematical definition:
        Pearson correlation of average ranks, with ties assigned their average
        rank.

    References:
        Spearman rank correlation coefficient.
    """
    _validate_vector(predictor, "predictor")
    _validate_vector(outcome, "outcome")
    if predictor.shape != outcome.shape:
        raise ValueError("predictor and outcome must have the same shape")
    if np.unique(predictor).size == 1 or np.unique(outcome).size == 1:
        return 0.0
    result = spearmanr(predictor, outcome)
    value = float(result.statistic)
    if not np.isfinite(value):
        return 0.0
    return value


def _stratified_statistic(
    baseline: FloatArray,
    alternative: FloatArray,
    outcome: FloatArray,
    strata: Sequence[str],
    indices_by_stratum: dict[str, NDArray[np.int64]],
) -> float:
    improvements = []
    for name in sorted(indices_by_stratum):
        indices = indices_by_stratum[name]
        if indices.size < 3:
            continue
        improvements.append(
            spearman_correlation(alternative[indices], outcome[indices])
            - spearman_correlation(baseline[indices], outcome[indices])
        )
    if not improvements:
        raise ValueError("No stratum contains at least three sampling units")
    return float(np.mean(np.asarray(improvements, dtype=np.float64)))


def paired_bootstrap_improvement(
    baseline: FloatArray,
    alternative: FloatArray,
    outcome: FloatArray,
    strata: Sequence[str],
    *,
    n_bootstrap: int,
    seed: int,
    confidence_level: float = 0.95,
) -> dict[str, float | int]:
    """Estimate a paired stratified CI for Spearman improvement on CPU.

    Args:
        baseline: Baseline metric values with shape ``(n,)`` and float64 dtype.
        alternative: Alternative values paired to baseline, shape ``(n,)``.
        outcome: Outcome values paired to both metrics, shape ``(n,)``.
        strata: Target-family label for each configuration sampling unit.
        n_bootstrap: Positive number of bootstrap replicates.
        seed: NumPy random seed.
        confidence_level: Open-interval confidence level.

    Returns:
        Mapping with the observed mean per-stratum improvement, lower and upper
        percentile limits, replicate count, and count of sampling units.

    Dtype:
        Numerical inputs must be float64. Bootstrap arrays are float64.

    Device:
        NumPy CPU arrays only.

    Mathematical definition:
        Within each stratum, configuration indices are sampled with
        replacement. The same indices are used for both metrics. Each
        replicate is the mean over stratum-level differences
        ``rho(alternative, outcome) - rho(baseline, outcome)``.

    References:
        Paired nonparametric bootstrap with stratified resampling.
    """
    _validate_vector(baseline, "baseline")
    _validate_vector(alternative, "alternative")
    _validate_vector(outcome, "outcome")
    if baseline.shape != alternative.shape or baseline.shape != outcome.shape:
        raise ValueError("All numerical inputs must have the same shape")
    if len(strata) != baseline.size:
        raise ValueError("strata must have one label per sampling unit")
    if n_bootstrap < 1:
        raise ValueError("n_bootstrap must be positive")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between zero and one")

    labels = np.asarray(list(strata), dtype=np.str_)
    indices_by_stratum = {
        str(label): np.flatnonzero(labels == label).astype(np.int64, copy=False)
        for label in np.unique(labels)
    }
    observed = _stratified_statistic(
        baseline,
        alternative,
        outcome,
        strata,
        indices_by_stratum,
    )
    generator = np.random.default_rng(seed)
    samples = np.empty(n_bootstrap, dtype=np.float64)
    names = sorted(indices_by_stratum)
    for replicate in range(n_bootstrap):
        resampled: dict[str, NDArray[np.int64]] = {}
        for name in names:
            indices = indices_by_stratum[name]
            resampled[name] = generator.choice(indices, size=indices.size, replace=True)
        samples[replicate] = _stratified_statistic(
            baseline,
            alternative,
            outcome,
            strata,
            resampled,
        )
    alpha = (1.0 - confidence_level) / 2.0
    lower, upper = np.quantile(samples, [alpha, 1.0 - alpha])
    return {
        "improvement": observed,
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "n_bootstrap": n_bootstrap,
        "n_sampling_units": int(baseline.size),
    }
