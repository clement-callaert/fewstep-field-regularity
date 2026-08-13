"""Grid-aware Euler non-implication for scalar linear ODEs.

For every L>0 and integer N>=1, the constant field a0(t)=L uniquely
minimizes integrated squared regularity among scalar fields with integral
L, yet left-endpoint N-step Euler has strictly larger endpoint error for
a0 than for a cosine competitor aligned to that grid.

The competitor is constructed as a function of the solver resolution.
This module also records how the exact aliasing disappears under phase,
frequency, and node perturbations.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

Field = Callable[[float], float]


def epsilon_n(L: float, n_steps: int) -> float:
    """Return N(e^{L/N}-1)-L, strictly positive for L>0 and N>=1."""
    if L <= 0:
        raise ValueError("L must be positive")
    if n_steps < 1:
        raise ValueError("N must be a positive integer")
    return n_steps * (math.exp(L / n_steps) - 1.0) - L


def constant_field(L: float) -> Field:
    return lambda _t: L


def oscillatory_field(
    L: float,
    n_steps: int,
    *,
    phase: float = 0.0,
    frequency: float | None = None,
) -> Field:
    """Return a_{1,N}(t)=L+eps_N cos(2 pi f t + phase).

    Default frequency is the grid frequency N. Changing the frequency or
    phase keeps the same amplitude eps_N(L,N) used in the aligned theorem.
    """
    eps = epsilon_n(L, n_steps)
    freq = float(n_steps if frequency is None else frequency)

    def field(time: float) -> float:
        return L + eps * math.cos(2.0 * math.pi * freq * time + phase)

    return field


def integrate_field(field: Field, *, n_quad: int = 20001) -> float:
    """Composite trapezoid integral of a field on [0,1]."""
    h = 1.0 / (n_quad - 1)
    total = 0.5 * (field(0.0) + field(1.0))
    for index in range(1, n_quad - 1):
        total += field(index * h)
    return total * h


def integrated_squared(field: Field, *, n_quad: int = 20001) -> float:
    return integrate_field(lambda t: field(t) ** 2, n_quad=n_quad)


def euler_endpoint(
    field: Field,
    n_steps: int,
    *,
    theta: float = 0.0,
    x0: float = 1.0,
) -> float:
    """N-step explicit Euler for x'=a(t)x on [0,1].

    ``theta=0`` samples left endpoints t_n=n/N. ``theta in (0,1]`` samples
    interior or right points t_n+theta h. The step size remains 1/N.
    """
    if n_steps < 1:
        raise ValueError("N must be a positive integer")
    if not 0.0 <= theta <= 1.0:
        raise ValueError("theta must lie in [0,1]")
    step = 1.0 / n_steps
    value = x0
    for index in range(n_steps):
        time = (index + theta) * step
        value *= 1.0 + step * field(time)
    return value


def heun_endpoint(field: Field, n_steps: int, *, x0: float = 1.0) -> float:
    """N-step explicit Heun for x'=a(t)x on [0,1]."""
    if n_steps < 1:
        raise ValueError("N must be a positive integer")
    step = 1.0 / n_steps
    value = x0
    for index in range(n_steps):
        t0 = index * step
        a1 = field(t0)
        a2 = field(t0 + step)
        value *= 1.0 + 0.5 * step * (a1 + a2 * (1.0 + step * a1))
    return value


def exact_endpoint(field: Field, *, n_quad: int = 20001, x0: float = 1.0) -> float:
    return x0 * math.exp(integrate_field(field, n_quad=n_quad))


def class_s_embedding(
    field: Field,
    L: float,
    time: float,
    *,
    n_quad: int = 4001,
) -> tuple[float, float, float]:
    """Return (q(t), alpha(t), sigma(t)) for the trigonometric Class-S lift.

    q(t)=exp(2 int_0^t a), lambda=e^{2L},
    alpha=sqrt(q) cos(pi t/2), sigma=sqrt(q/lambda) sin(pi t/2).
    """
    if time < 0.0 or time > 1.0:
        raise ValueError("time must lie in [0,1]")
    if time == 0.0:
        integral = 0.0
    else:
        n_nodes = max(3, int(n_quad * max(time, 1e-12)))
        if n_nodes % 2 == 0:
            n_nodes += 1
        h = time / (n_nodes - 1)
        total = 0.5 * (field(0.0) + field(time))
        for index in range(1, n_nodes - 1):
            total += field(index * h)
        integral = total * h
    variance = math.exp(2.0 * integral)
    scale = math.exp(2.0 * L)
    alpha = math.sqrt(variance) * math.cos(math.pi * time / 2.0)
    sigma = math.sqrt(variance / scale) * math.sin(math.pi * time / 2.0)
    return variance, alpha, sigma


@dataclass(frozen=True)
class GridAwareRecord:
    """One robustness cell for the grid-aware construction."""

    L: float
    n_steps: int
    phase: float
    frequency: float
    theta: float
    solver: str
    epsilon: float
    R0: float
    R1: float
    exact0: float
    exact1: float
    numerical0: float
    numerical1: float
    error0: float
    error1: float
    endpoints_match: bool
    euler_exact_on_oscillation: bool
    ranking_inverted: bool


def _numerical_endpoint(
    field: Field,
    n_steps: int,
    solver: str,
    theta: float,
) -> float:
    if solver == "euler":
        return euler_endpoint(field, n_steps, theta=theta)
    if solver == "heun":
        if theta != 0.0:
            raise ValueError("Heun robustness uses the standard left/right stages")
        return heun_endpoint(field, n_steps)
    raise ValueError(f"unsupported solver {solver!r}")


def evaluate_cell(
    L: float,
    n_steps: int,
    *,
    phase: float = 0.0,
    frequency: float | None = None,
    theta: float = 0.0,
    solver: str = "euler",
    n_quad: int = 20001,
    match_tol: float = 1e-10,
) -> GridAwareRecord:
    """Evaluate one aligned or perturbed grid-aware comparison."""
    freq = float(n_steps if frequency is None else frequency)
    a0 = constant_field(L)
    a1 = oscillatory_field(L, n_steps, phase=phase, frequency=freq)
    exact0 = exact_endpoint(a0, n_quad=n_quad)
    exact1 = exact_endpoint(a1, n_quad=n_quad)
    num0 = _numerical_endpoint(a0, n_steps, solver, theta)
    num1 = _numerical_endpoint(a1, n_steps, solver, theta)
    err0 = abs(num0 - exact0)
    err1 = abs(num1 - exact1)
    endpoints_match = abs(exact0 - exact1) <= match_tol * max(1.0, abs(exact0))
    return GridAwareRecord(
        L=L,
        n_steps=n_steps,
        phase=phase,
        frequency=freq,
        theta=theta,
        solver=solver,
        epsilon=epsilon_n(L, n_steps),
        R0=integrated_squared(a0, n_quad=n_quad),
        R1=integrated_squared(a1, n_quad=n_quad),
        exact0=exact0,
        exact1=exact1,
        numerical0=num0,
        numerical1=num1,
        error0=err0,
        error1=err1,
        endpoints_match=endpoints_match,
        euler_exact_on_oscillation=solver == "euler" and err1 <= match_tol * max(1.0, abs(exact1)),
        ranking_inverted=err0 > err1 + match_tol and endpoints_match,
    )


def theorem_holds(L: float, n_steps: int, *, n_quad: int = 20001) -> bool:
    """Return True if the aligned left-Euler theorem holds at (L,N)."""
    cell = evaluate_cell(L, n_steps, n_quad=n_quad)
    aligned = (
        cell.phase == 0.0
        and cell.frequency == float(n_steps)
        and cell.theta == 0.0
        and cell.solver == "euler"
    )
    return (
        aligned
        and cell.epsilon > 0.0
        and cell.R1 > cell.R0
        and cell.endpoints_match
        and cell.euler_exact_on_oscillation
        and cell.error0 > 0.0
        and cell.ranking_inverted
    )


DEFAULT_ROBUSTNESS_SPEC: tuple[dict[str, Any], ...] = (
    {"n_steps": 4, "solver": "euler"},
    {"n_steps": 8, "solver": "euler"},
    {"n_steps": 16, "solver": "euler"},
    {"n_steps": 4, "solver": "euler", "phase": 0.5 * math.pi},
    {"n_steps": 4, "solver": "euler", "phase": math.pi},
    {"n_steps": 8, "solver": "euler", "phase": 0.25 * math.pi},
    {"n_steps": 4, "solver": "euler", "frequency": 4.5},
    {"n_steps": 8, "solver": "euler", "frequency": 7.0},
    {"n_steps": 8, "solver": "euler", "frequency": 9.0},
    {"n_steps": 8, "solver": "euler", "theta": 0.5},
    {"n_steps": 4, "solver": "heun"},
    {"n_steps": 8, "solver": "heun"},
)


def robustness_census(
    L: float = math.log(2.0),
    spec: tuple[dict[str, Any], ...] | None = None,
) -> list[GridAwareRecord]:
    """Return the default perturbation census used in the manuscript."""
    rows = spec if spec is not None else DEFAULT_ROBUSTNESS_SPEC
    return [evaluate_cell(L, **row) for row in rows]


def records_as_dicts(records: list[GridAwareRecord]) -> list[dict[str, Any]]:
    return [asdict(row) for row in records]
