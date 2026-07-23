"""ODE solver protocol with explicit NFE accounting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from torch import Tensor

from fewstep_regularities.fields.base import VelocityField


@dataclass(frozen=True)
class SolverResult:
    """Output of a fixed-budget ODE solve.

    Attributes:
        trajectory: States of shape ``(n_steps + 1, n, d)`` or endpoint only.
        times: Time grid of shape ``(n_steps + 1,)``.
        requested_nfe: Requested model function evaluations.
        actual_nfe: Counted model function evaluations.
        n_steps: Number of accepted steps.
        wall_clock_s: Wall-clock runtime in seconds.
        endpoint_handling: Description of endpoint treatment.
    """

    trajectory: Tensor
    times: Tensor
    requested_nfe: int
    actual_nfe: int
    n_steps: int
    wall_clock_s: float
    endpoint_handling: str


@runtime_checkable
class ODESolver(Protocol):
    """Fixed-step ODE solver.

    Compare methods at equal NFE, not equal step count.
    Do not count derivative-free bookkeeping as a field evaluation.
    """

    @property
    def name(self) -> str:
        """Solver identifier (for example ``euler``, ``heun``, ``rk4``)."""
        ...

    def function_evaluations(self) -> int:
        """Return the number of velocity-field evaluations so far.

        Returns:
            Non-negative integer NFE count.
        """
        ...

    def step(
        self,
        field: VelocityField,
        t: Tensor,
        x: Tensor,
        dt: Tensor,
    ) -> Tensor:
        """Advance one solver step.

        Args:
            field: Velocity field.
            t: Current times of shape ``(n,)`` or scalar tensor.
            x: Current states of shape ``(n, d)``.
            dt: Step size, scalar or shape broadcastable to ``t``.

        Returns:
            Next states of shape ``(n, d)``, same dtype and device as ``x``.

        Mathematical definition:
            Method-specific one-step map.
        """
        ...

    def solve(
        self,
        field: VelocityField,
        x0: Tensor,
        t0: float,
        t1: float,
        requested_nfe: int,
    ) -> SolverResult:
        """Integrate from ``t0`` to ``t1`` under a fixed NFE budget.

        Args:
            field: Velocity field.
            x0: Initial states of shape ``(n, d)``.
            t0: Start time.
            t1: End time.
            requested_nfe: Requested field evaluations.

        Returns:
            ``SolverResult`` with trajectory, NFE counts, and metadata.

        Mathematical definition:
            Approximate the ODE ``dx/dt = v(t, x)``.
        """
        ...
