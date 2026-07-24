"""Solver-specific scalar local error quantities."""

from __future__ import annotations

import math
from dataclasses import dataclass

from fewstep_regularities.analysis.affine_flow import (
    exact_transition_factor,
    scalar_affine_quantities,
    scalar_drift,
)


@dataclass(frozen=True)
class ScalarPropagation:
    """Numerical scalar propagation and local defects."""

    factor: float
    exact_factor: float
    local_log_defects: tuple[float, ...]
    local_factor_defects: tuple[float, ...]
    transported_local_contributions: tuple[float, ...]


def evaluations_per_step(solver_name: str) -> int:
    """Return fixed field evaluations per step."""
    values = {"euler": 1, "heun": 2, "rk4": 4}
    if solver_name not in values:
        raise ValueError(f"Unsupported solver {solver_name!r}")
    return values[solver_name]


def scalar_step_factor(
    path_name: str,
    solver_name: str,
    eigenvalue: float,
    time: float,
    step_size: float,
) -> float:
    """Return one numerical step factor for ``x' = a(t) x``."""
    a1 = scalar_drift(path_name, eigenvalue, time)
    if solver_name == "euler":
        return 1.0 + step_size * a1
    if solver_name == "heun":
        predictor = 1.0 + step_size * a1
        a2 = scalar_drift(path_name, eigenvalue, time + step_size)
        return 1.0 + 0.5 * step_size * (a1 + a2 * predictor)
    if solver_name == "rk4":
        half = 0.5 * step_size
        a2 = scalar_drift(path_name, eigenvalue, time + half)
        a4 = scalar_drift(path_name, eigenvalue, time + step_size)
        k1 = a1
        k2 = a2 * (1.0 + half * k1)
        k3 = a2 * (1.0 + half * k2)
        k4 = a4 * (1.0 + step_size * k3)
        return 1.0 + (step_size / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    raise ValueError(f"Unsupported solver {solver_name!r}")


def propagate_scalar_mode(
    path_name: str,
    solver_name: str,
    eigenvalue: float,
    requested_nfe: int,
) -> ScalarPropagation:
    """Propagate one eigenmode and retain each exact local defect."""
    evals = evaluations_per_step(solver_name)
    if requested_nfe <= 0 or requested_nfe % evals != 0:
        raise ValueError("requested_nfe is incompatible with solver")
    n_steps = requested_nfe // evals
    step_size = 1.0 / n_steps
    factor = 1.0
    log_defects: list[float] = []
    factor_defects: list[float] = []
    numerical_steps: list[float] = []
    exact_steps: list[float] = []
    for step in range(n_steps):
        time = step * step_size
        numerical = scalar_step_factor(
            path_name,
            solver_name,
            eigenvalue,
            time,
            step_size,
        )
        exact = exact_transition_factor(
            path_name,
            eigenvalue,
            time,
            time + step_size,
        )
        if numerical == 0.0:
            raise ArithmeticError("zero numerical step factor")
        factor *= numerical
        numerical_steps.append(numerical)
        exact_steps.append(exact)
        log_defects.append(math.log(abs(numerical)) - math.log(exact))
        factor_defects.append(numerical - exact)
    transported: list[float] = []
    for index in range(n_steps):
        before = math.prod(numerical_steps[:index])
        after = math.prod(exact_steps[index + 1 :])
        transported.append(
            before * (numerical_steps[index] - exact_steps[index]) * after
        )
    return ScalarPropagation(
        factor=factor,
        exact_factor=math.sqrt(eigenvalue),
        local_log_defects=tuple(log_defects),
        local_factor_defects=tuple(factor_defects),
        transported_local_contributions=tuple(transported),
    )


def leading_local_coefficient(
    path_name: str,
    solver_name: str,
    eigenvalue: float,
    time: float,
) -> float:
    """Return the leading exact-minus-method local error coefficient."""
    values = scalar_affine_quantities(path_name, eigenvalue, time)
    a = values.drift
    ap = values.drift_derivative
    app = values.drift_second_derivative
    if solver_name == "euler":
        return 0.5 * (ap + a**2)
    if solver_name == "heun":
        return -(1.0 / 12.0) * app + (1.0 / 6.0) * a**3
    if solver_name == "rk4":
        step = 1e-3
        numerical = scalar_step_factor(
            path_name,
            solver_name,
            eigenvalue,
            time,
            step,
        )
        exact = exact_transition_factor(
            path_name,
            eigenvalue,
            time,
            time + step,
        )
        return (exact - numerical) / step**5
    raise ValueError(f"Unsupported solver {solver_name!r}")


def material_derivative_eigenvalue(
    path_name: str,
    eigenvalue: float,
    time: float,
) -> float:
    """Return ``a'(t) + a(t)^2`` for one eigenmode."""
    values = scalar_affine_quantities(path_name, eigenvalue, time)
    return values.drift_derivative + values.drift**2
