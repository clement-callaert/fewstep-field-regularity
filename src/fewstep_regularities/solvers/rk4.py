"""Classical RK4 solver."""

from __future__ import annotations

from dataclasses import dataclass

from torch import Tensor

from fewstep_regularities.fields.base import VelocityField
from fewstep_regularities.solvers.common import CountingField, FixedStepSolver


@dataclass
class RK4Solver(FixedStepSolver):
    """Classical Runge-Kutta 4: 4 field evaluations per step."""

    name: str = "rk4"
    evals_per_step: int = 4

    def step(
        self,
        field: VelocityField,
        t: Tensor,
        x: Tensor,
        dt: Tensor,
    ) -> Tensor:
        """Classical RK4 step."""
        k1 = field.evaluate(t, x)
        k2 = field.evaluate(t + 0.5 * dt, x + 0.5 * dt * k1)
        k3 = field.evaluate(t + 0.5 * dt, x + 0.5 * dt * k2)
        k4 = field.evaluate(t + dt, x + dt * k3)
        return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    def _step_impl(
        self,
        field: CountingField,
        t: Tensor,
        x: Tensor,
        dt: Tensor,
    ) -> Tensor:
        k1 = field.evaluate(t, x)
        k2 = field.evaluate(t + 0.5 * dt, x + 0.5 * dt * k1)
        k3 = field.evaluate(t + 0.5 * dt, x + 0.5 * dt * k2)
        k4 = field.evaluate(t + dt, x + dt * k3)
        return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
