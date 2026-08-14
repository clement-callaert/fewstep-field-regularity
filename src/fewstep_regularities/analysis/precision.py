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
    if path_name == "log_covariance":
        return mpmath.exp(time * mpmath.log(eigenvalue))
    raise ValueError(f"Unsupported path {path_name!r}")


def _drift(
    path_name: str,
    eigenvalue: mpmath.mpf,
    time: mpmath.mpf,
) -> mpmath.mpf:
    if path_name == "log_covariance":
        return mpmath.mpf("0.5") * mpmath.log(eigenvalue)
    variance = _variance(path_name, eigenvalue, time)
    if path_name == "linear":
        return ((1 + eigenvalue) * time - 1) / variance
    if path_name == "variance_preserving":
        return (
            mpmath.pi * (eigenvalue - 1) * mpmath.sin(mpmath.pi * time) / (4 * variance)
        )
    raise ValueError(f"Unsupported path {path_name!r}")


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


def _alpha_sigma(
    path_name: str,
    time: mpmath.mpf,
) -> tuple[mpmath.mpf, mpmath.mpf, mpmath.mpf, mpmath.mpf]:
    """Return ``alpha, sigma, alpha', sigma'`` for a scalar schedule."""
    if path_name == "linear":
        return 1 - time, time, mpmath.mpf(-1), mpmath.mpf(1)
    if path_name == "variance_preserving":
        angle = mpmath.pi * time / 2
        half_pi = mpmath.pi / 2
        return (
            mpmath.cos(angle),
            mpmath.sin(angle),
            -half_pi * mpmath.sin(angle),
            half_pi * mpmath.cos(angle),
        )
    raise ValueError(f"Unsupported path {path_name!r}")


def _affine_mode_field(
    path_name: str,
    eigenvalue: mpmath.mpf,
    source_mean: mpmath.mpf,
    target_mean: mpmath.mpf,
    time: mpmath.mpf,
    state: mpmath.mpf,
) -> mpmath.mpf:
    """Evaluate the non-centered modal drift ``a(t) x + c(t)``."""
    drift = _drift(path_name, eigenvalue, time)
    alpha, sigma, dalpha, dsigma = _alpha_sigma(path_name, time)
    mode_mean = alpha * source_mean + sigma * target_mean
    mode_mean_velocity = dalpha * source_mean + dsigma * target_mean
    offset = mode_mean_velocity - drift * mode_mean
    return drift * state + offset


def _affine_mode_step(
    path_name: str,
    solver_name: str,
    eigenvalue: mpmath.mpf,
    source_mean: mpmath.mpf,
    target_mean: mpmath.mpf,
    state: mpmath.mpf,
    time: mpmath.mpf,
    step_size: mpmath.mpf,
) -> mpmath.mpf:
    """Advance one solver step of the non-centered modal ODE."""

    def field(t: mpmath.mpf, x: mpmath.mpf) -> mpmath.mpf:
        return _affine_mode_field(path_name, eigenvalue, source_mean, target_mean, t, x)

    if solver_name == "euler":
        return state + step_size * field(time, state)
    if solver_name == "heun":
        k1 = field(time, state)
        predictor = state + step_size * k1
        k2 = field(time + step_size, predictor)
        return state + step_size * (k1 + k2) / 2
    if solver_name == "rk4":
        half = step_size / 2
        k1 = field(time, state)
        k2 = field(time + half, state + half * k1)
        k3 = field(time + half, state + half * k2)
        k4 = field(time + step_size, state + step_size * k3)
        return state + step_size * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    raise ValueError(f"Unsupported solver {solver_name!r}")


def high_precision_noncentered_mode(
    path_name: str,
    solver_name: str,
    eigenvalue: float,
    source_mean: float,
    target_mean: float,
    requested_nfe: int,
    *,
    decimal_digits: int = 80,
) -> tuple[mpmath.mpf, mpmath.mpf]:
    """Return the modal endpoint affine map ``(factor, offset)``."""
    evals = {"euler": 1, "heun": 2, "rk4": 4}[solver_name]
    if requested_nfe <= 0 or requested_nfe % evals != 0:
        raise ValueError("requested_nfe is incompatible with solver")
    with mpmath.workdps(decimal_digits):
        lam = mpmath.mpf(str(eigenvalue))
        mu0 = mpmath.mpf(str(source_mean))
        mu1 = mpmath.mpf(str(target_mean))
        n_steps = requested_nfe // evals
        step_size = mpmath.mpf(1) / n_steps
        zero_probe = mpmath.mpf(0)
        unit_probe = mpmath.mpf(1)
        for step in range(n_steps):
            time = mpmath.mpf(step) * step_size
            zero_probe = _affine_mode_step(
                path_name, solver_name, lam, mu0, mu1, zero_probe, time, step_size
            )
            unit_probe = _affine_mode_step(
                path_name, solver_name, lam, mu0, mu1, unit_probe, time, step_size
            )
        return +(unit_probe - zero_probe), +zero_probe


def high_precision_noncentered_gaussian_w2(
    path_name: str,
    solver_name: str,
    eigenvalues: Sequence[float],
    source_means: Sequence[float],
    target_means: Sequence[float],
    requested_nfe: int,
    *,
    decimal_digits: int = 80,
) -> mpmath.mpf:
    """Return Gaussian W2 for the non-centered commuting family.

    Inputs: path and solver names; modal eigenvalues and means; ``requested_nfe``; ``decimal_digits``.
    Outputs: high-precision scalar W2.
    Units: state-space W2.
    Precision: mpmath with ``decimal_digits`` (plan default in docs/WORKSHOP_EXTERNAL_VALIDATION_PLAN.md); equal-NFE modal steps.
    """
    if not len(eigenvalues) == len(source_means) == len(target_means):
        raise ValueError("modal sequences must have equal length")
    with mpmath.workdps(decimal_digits):
        total = mpmath.mpf(0)
        for eigenvalue, mu0, mu1 in zip(
            eigenvalues, source_means, target_means, strict=True
        ):
            factor, offset = high_precision_noncentered_mode(
                path_name,
                solver_name,
                eigenvalue,
                mu0,
                mu1,
                requested_nfe,
                decimal_digits=decimal_digits,
            )
            lam = mpmath.mpf(str(eigenvalue))
            endpoint_mean = factor * mpmath.mpf(str(mu0)) + offset
            total += (endpoint_mean - mpmath.mpf(str(mu1))) ** 2
            total += (abs(factor) - mpmath.sqrt(lam)) ** 2
        return +mpmath.sqrt(total)


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
