"""Shared fixed-NFE ODE solver utilities."""

from __future__ import annotations

import time
from dataclasses import dataclass

import torch
from torch import Tensor

from fewstep_regularities.fields.base import VelocityField
from fewstep_regularities.solvers.base import SolverResult
from fewstep_regularities.utils.shapes import assert_shape


@dataclass
class CountingField:
    """Wrap a velocity field and count ``evaluate`` calls."""

    field: VelocityField
    nfe: int = 0

    def evaluate(self, t: Tensor, x: Tensor) -> Tensor:
        """Count and forward ``evaluate``."""
        self.nfe += 1
        return self.field.evaluate(t, x)

    def jacobian(self, t: Tensor, x: Tensor) -> Tensor:
        """Forward jacobian without counting as NFE."""
        return self.field.jacobian(t, x)

    def time_derivative(self, t: Tensor, x: Tensor) -> Tensor | None:
        """Forward time derivative without counting as NFE."""
        return self.field.time_derivative(t, x)


def n_steps_from_nfe(requested_nfe: int, evals_per_step: int) -> int:
    """Convert an NFE budget to a step count.

    Requires exact divisibility.
    """
    if requested_nfe <= 0:
        raise ValueError("requested_nfe must be positive")
    if evals_per_step <= 0:
        raise ValueError("evals_per_step must be positive")
    if requested_nfe % evals_per_step != 0:
        msg = (
            f"requested_nfe={requested_nfe} is not divisible by "
            f"evals_per_step={evals_per_step}"
        )
        raise ValueError(msg)
    steps = requested_nfe // evals_per_step
    if steps < 1:
        raise ValueError("n_steps must be at least 1")
    return steps


def build_time_grid(
    t0: float,
    t1: float,
    n_steps: int,
    dtype: torch.dtype,
    device: torch.device | None = None,
) -> Tensor:
    """Uniform grid of shape ``(n_steps + 1,)``."""
    return torch.linspace(t0, t1, n_steps + 1, dtype=dtype, device=device)


@dataclass
class FixedStepSolver:
    """Base fixed-step solver with equal-NFE accounting."""

    name: str
    evals_per_step: int
    _nfe: int = 0

    def function_evaluations(self) -> int:
        """Return counted field evaluations."""
        return self._nfe

    def step(
        self,
        field: VelocityField,
        t: Tensor,
        x: Tensor,
        dt: Tensor,
    ) -> Tensor:
        """Advance one step. Implemented by subclasses."""
        raise NotImplementedError

    def solve(
        self,
        field: VelocityField,
        x0: Tensor,
        t0: float,
        t1: float,
        requested_nfe: int,
    ) -> SolverResult:
        """Integrate with a fixed NFE budget."""
        assert_shape(x0, (None, None), "x0")
        n_steps = n_steps_from_nfe(requested_nfe, self.evals_per_step)
        dtype = x0.dtype
        times = build_time_grid(t0, t1, n_steps, dtype, x0.device)
        wrapped = CountingField(field=field, nfe=0)
        x = x0
        traj = [x0]
        start = time.perf_counter()
        for i in range(n_steps):
            t = times[i]
            dt = times[i + 1] - times[i]
            x = self._step_impl(wrapped, t, x, dt)
            traj.append(x)
        wall = time.perf_counter() - start
        self._nfe = wrapped.nfe
        return SolverResult(
            trajectory=torch.stack(traj, dim=0),
            times=times,
            requested_nfe=requested_nfe,
            actual_nfe=wrapped.nfe,
            n_steps=n_steps,
            wall_clock_s=wall,
            endpoint_handling="inclusive_uniform_grid",
        )

    def _step_impl(
        self,
        field: CountingField,
        t: Tensor,
        x: Tensor,
        dt: Tensor,
    ) -> Tensor:
        raise NotImplementedError
