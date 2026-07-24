"""Higher-precision scalar propagation for commuting Gaussian flows."""

from __future__ import annotations

from collections.abc import Sequence

import mpmath


def _variance(
    path_name: str,
    eigenvalue: mpmath.mpf,
    time: mpmath.mpf,
) -> mpmath.mpf:
    if path_name == "linear":
        return (1 - time) ** 2 + eigenvalue * time**2
    if path_name == "variance_preserving":
        angle = mpmath.pi * time / 2
        return mpmath.cos(angle) ** 2 + eigenvalue * mpmath.sin(angle) ** 2
    raise ValueError(f"Unsupported path {path_name!r}")


def _drift(
    path_name: str,
    eigenvalue: mpmath.mpf,
    time: mpmath.mpf,
) -> mpmath.mpf:
    variance = _variance(path_name, eigenvalue, time)
    if path_name == "linear":
        return ((1 + eigenvalue) * time - 1) / variance
    return mpmath.pi * (eigenvalue - 1) * mpmath.sin(mpmath.pi * time) / (4 * variance)


def _step_factor(
    path_name: str,
    solver_name: str,
    eigenvalue: mpmath.mpf,
    time: mpmath.mpf,
    step_size: mpmath.mpf,
) -> mpmath.mpf:
    a1 = _drift(path_name, eigenvalue, time)
    if solver_name == "euler":
        return 1 + step_size * a1
    if solver_name == "heun":
        predictor = 1 + step_size * a1
        a2 = _drift(path_name, eigenvalue, time + step_size)
        return 1 + step_size * (a1 + a2 * predictor) / 2
    if solver_name == "rk4":
        half = step_size / 2
        a2 = _drift(path_name, eigenvalue, time + half)
        a4 = _drift(path_name, eigenvalue, time + step_size)
        k1 = a1
        k2 = a2 * (1 + half * k1)
        k3 = a2 * (1 + half * k2)
        k4 = a4 * (1 + step_size * k3)
        return 1 + step_size * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    raise ValueError(f"Unsupported solver {solver_name!r}")


def high_precision_mode_factor(
    path_name: str,
    solver_name: str,
    eigenvalue: float,
    requested_nfe: int,
    *,
    decimal_digits: int = 80,
) -> mpmath.mpf:
    """Return one endpoint factor at arbitrary decimal precision."""
    evals = {"euler": 1, "heun": 2, "rk4": 4}[solver_name]
    if requested_nfe <= 0 or requested_nfe % evals != 0:
        raise ValueError("requested_nfe is incompatible with solver")
    with mpmath.workdps(decimal_digits):
        lam = mpmath.mpf(str(eigenvalue))
        n_steps = requested_nfe // evals
        step_size = mpmath.mpf(1) / n_steps
        factor = mpmath.mpf(1)
        for step in range(n_steps):
            time = mpmath.mpf(step) * step_size
            factor *= _step_factor(
                path_name,
                solver_name,
                lam,
                time,
                step_size,
            )
        return +factor


def high_precision_gaussian_w2(
    path_name: str,
    solver_name: str,
    eigenvalues: Sequence[float],
    requested_nfe: int,
    *,
    decimal_digits: int = 80,
) -> mpmath.mpf:
    """Return Gaussian W2 from arbitrary-precision eigenmode factors."""
    with mpmath.workdps(decimal_digits):
        total = mpmath.mpf(0)
        for eigenvalue in eigenvalues:
            lam = mpmath.mpf(str(eigenvalue))
            factor = high_precision_mode_factor(
                path_name,
                solver_name,
                eigenvalue,
                requested_nfe,
                decimal_digits=decimal_digits,
            )
            total += (abs(factor) - mpmath.sqrt(lam)) ** 2
        return +mpmath.sqrt(total)
