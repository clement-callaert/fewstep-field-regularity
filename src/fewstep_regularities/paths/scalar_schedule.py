"""Generic scalar schedule adapter and transfer formula."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import torch
from torch import Tensor

from fewstep_regularities.paths.schedules import as_time, validate_path_batch
from fewstep_regularities.utils.precision import DEFAULT_DTYPE

ScheduleFn = Callable[[Tensor], Tensor]


@dataclass(frozen=True)
class ScalarScheduleAdapter:
    """Adapter wrapping arbitrary scalar ``(alpha, sigma)`` schedules.

    Coupling class: schedule reparameterization / independent bridge depending
    on how samples are drawn.
    """

    alpha_fn: ScheduleFn
    sigma_fn: ScheduleFn
    alpha_deriv_fn: ScheduleFn
    sigma_deriv_fn: ScheduleFn
    dtype: torch.dtype = DEFAULT_DTYPE
    coupling: str = "schedule_adapter"

    def alpha(self, t: Tensor) -> Tensor:
        """Evaluate ``alpha(t)``."""
        return self.alpha_fn(as_time(t, self.dtype))

    def sigma(self, t: Tensor) -> Tensor:
        """Evaluate ``sigma(t)``."""
        return self.sigma_fn(as_time(t, self.dtype))

    def alpha_derivative(self, t: Tensor) -> Tensor:
        """Evaluate ``alpha'(t)``."""
        return self.alpha_deriv_fn(as_time(t, self.dtype))

    def sigma_derivative(self, t: Tensor) -> Tensor:
        """Evaluate ``sigma'(t)``."""
        return self.sigma_deriv_fn(as_time(t, self.dtype))

    def marginal_sample(
        self,
        t: Tensor,
        x0: Tensor,
        x1: Tensor,
        noise: Tensor | None = None,
    ) -> Tensor:
        """Sample ``x_t = alpha(t) x_0 + sigma(t) x_1``."""
        del noise
        t_col, x0, x1 = validate_path_batch(t, x0, x1, self.dtype)
        return self.alpha(t_col) * x0 + self.sigma(t_col) * x1

    def conditional_velocity(
        self,
        t: Tensor,
        x: Tensor,
        x0: Tensor,
        x1: Tensor,
    ) -> Tensor:
        """Conditional velocity ``alpha' x_0 + sigma' x_1``."""
        del x
        t_col, x0, x1 = validate_path_batch(t, x0, x1, self.dtype)
        return self.alpha_derivative(t_col) * x0 + self.sigma_derivative(t_col) * x1

    def marginal_velocity(self, t: Tensor, x: Tensor) -> Tensor | None:
        """Marginal velocity unavailable without endpoint laws."""
        del t, x
        return None


def transfer_time(alpha_t: Tensor, sigma_t: Tensor) -> Tensor:
    """Map schedule time to linear-reference time ``t^†``.

    Lipschitz Prop 3.1: ``t^† = 1 / (1 + α_t / β_t)`` with ``β = sigma``.
    """
    ratio = alpha_t / sigma_t.clamp(min=1e-32)
    return 1.0 / (1.0 + ratio)


def transfer_drift(
    x: Tensor,
    alpha_t: Tensor,
    sigma_t: Tensor,
    alpha_dot: Tensor,
    sigma_dot: Tensor,
    ref_drift_fn: Callable[[Tensor, Tensor], Tensor],
) -> Tensor:
    """Apply the transfer formula (3.1) from a linear-reference drift.

    Args:
        x: States ``(n, d)``.
        alpha_t: ``α_t`` broadcastable to ``(n, 1)``.
        sigma_t: ``β_t`` broadcastable to ``(n, 1)``.
        alpha_dot: ``α'_t``.
        sigma_dot: ``β'_t``.
        ref_drift_fn: ``(t_dagger, x_ref) -> b^†``.

    Returns:
        Transferred drift of shape ``(n, d)``.
    """
    if alpha_t.ndim == 1:
        alpha_t = alpha_t.unsqueeze(1)
    if sigma_t.ndim == 1:
        sigma_t = sigma_t.unsqueeze(1)
    if alpha_dot.ndim == 1:
        alpha_dot = alpha_dot.unsqueeze(1)
    if sigma_dot.ndim == 1:
        sigma_dot = sigma_dot.unsqueeze(1)
    t_dag = transfer_time(alpha_t, sigma_t)
    x_ref = (t_dag / sigma_t) * x
    b_ref = ref_drift_fn(t_dag.squeeze(1), x_ref)
    coeff = sigma_dot - alpha_dot * sigma_t / alpha_t.clamp(min=1e-32)
    return (alpha_dot / alpha_t.clamp(min=1e-32)) * x + coeff * (
        (1.0 - t_dag) * b_ref + (t_dag / sigma_t) * x
    )
