"""Fixed-step Heun (improved Euler) solver."""

from __future__ import annotations

from dataclasses import dataclass

from torch import Tensor

from fewstep_regularities.fields.base import VelocityField
from fewstep_regularities.solvers.common import CountingField, FixedStepSolver


@dataclass
class HeunSolver(FixedStepSolver):
    """Heun / improved Euler: 2 field evaluations per step."""

    name: str = "heun"
    evals_per_step: int = 2

    def step(
        self,
        field: VelocityField,
        t: Tensor,
        x: Tensor,
        dt: Tensor,
    ) -> Tensor:
        """Heun step."""
        k1 = field.evaluate(t, x)
        x_pred = x + dt * k1
        k2 = field.evaluate(t + dt, x_pred)
        return x + 0.5 * dt * (k1 + k2)

    def _step_impl(
        self,
        field: CountingField,
        t: Tensor,
        x: Tensor,
        dt: Tensor,
    ) -> Tensor:
        k1 = field.evaluate(t, x)
        x_pred = x + dt * k1
        k2 = field.evaluate(t + dt, x_pred)
        return x + 0.5 * dt * (k1 + k2)
