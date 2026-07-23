"""Fixed-step Euler solver."""

from __future__ import annotations

from dataclasses import dataclass

from torch import Tensor

from fewstep_regularities.fields.base import VelocityField
from fewstep_regularities.solvers.common import CountingField, FixedStepSolver


@dataclass
class EulerSolver(FixedStepSolver):
    """Forward Euler: 1 field evaluation per step."""

    name: str = "euler"
    evals_per_step: int = 1

    def step(
        self,
        field: VelocityField,
        t: Tensor,
        x: Tensor,
        dt: Tensor,
    ) -> Tensor:
        """``x + dt * v(t, x)``."""
        return x + dt * field.evaluate(t, x)

    def _step_impl(
        self,
        field: CountingField,
        t: Tensor,
        x: Tensor,
        dt: Tensor,
    ) -> Tensor:
        return x + dt * field.evaluate(t, x)
