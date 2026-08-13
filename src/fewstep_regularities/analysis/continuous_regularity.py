"""Continuous spectral regularity R = int_0^1 ||A(t)||_2^2 dt."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.integrate import quad

from fewstep_regularities.analysis.affine_flow import scalar_drift


def spectral_integrand(
    path_name: str, eigenvalues: Sequence[float], time: float
) -> float:
    """Return ||A(t)||_2^2 = max_i a_i(t)^2 for a commuting modal field."""
    return (
        max(abs(scalar_drift(path_name, float(value), time)) for value in eigenvalues)
        ** 2
    )


def trapezoidal_regularity(
    path_name: str,
    eigenvalues: Sequence[float],
    n_time: int = 24,
) -> float:
    """Return the n_time-node trapezoidal estimator hat R_n."""
    if n_time < 2:
        raise ValueError("n_time must be at least 2")
    times = np.linspace(0.0, 1.0, n_time)
    values = [spectral_integrand(path_name, eigenvalues, float(time)) for time in times]
    return float(np.trapezoid(values, times))


def continuous_regularity(
    path_name: str,
    eigenvalues: Sequence[float],
    *,
    epsabs: float = 1e-12,
) -> tuple[float, float]:
    """Return (R, estimated_absolute_error) from adaptive quadrature."""

    def integrand(time: float) -> float:
        return spectral_integrand(path_name, eigenvalues, time)

    value, error = quad(integrand, 0.0, 1.0, epsabs=epsabs, limit=800)
    return float(value), float(error)


def regularity_report(
    path_name: str,
    eigenvalues: Sequence[float],
    node_counts: Sequence[int] = (24, 48, 96, 192),
) -> dict[str, float | dict[int, float]]:
    """Return continuous R, quadrature error, and trapezoidal estimates."""
    value, error = continuous_regularity(path_name, eigenvalues)
    hats = {
        int(count): trapezoidal_regularity(path_name, eigenvalues, count)
        for count in node_counts
    }
    hat24 = float(hats[24])
    return {
        "R": value,
        "quadrature_abs_error": error,
        "R24": hat24,
        "abs_R_minus_R24": abs(value - hat24),
        "rel_R_minus_R24": abs(value - hat24) / max(abs(value), 1e-16),
        "trapezoidal": hats,
    }
