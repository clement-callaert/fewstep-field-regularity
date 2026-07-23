"""Trigonometric variance-preserving probability path."""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import Tensor

from fewstep_regularities.paths.schedules import as_time, validate_path_batch
from fewstep_regularities.utils.precision import DEFAULT_DTYPE


@dataclass(frozen=True)
class VariancePreservingTrigPath:
    """Independent coupling with trigonometric VP schedule.

    ``alpha(t) = cos(π t / 2)``, ``sigma(t) = sin(π t / 2)``.
    Satisfies ``alpha^2 + sigma^2 = 1``.

    Coupling class: independent.
    Distinct from Lipman VP diffusion path (eq. 18).
    """

    dtype: torch.dtype = DEFAULT_DTYPE
    coupling: str = "independent"

    def alpha(self, t: Tensor) -> Tensor:
        """Noise/source coefficient."""
        t = as_time(t.to(dtype=self.dtype))
        return torch.cos(0.5 * math.pi * t)

    def sigma(self, t: Tensor) -> Tensor:
        """Target coefficient."""
        t = as_time(t.to(dtype=self.dtype))
        return torch.sin(0.5 * math.pi * t)

    def alpha_derivative(self, t: Tensor) -> Tensor:
        """Derivative of ``alpha``."""
        t = as_time(t.to(dtype=self.dtype))
        return -0.5 * math.pi * torch.sin(0.5 * math.pi * t)

    def sigma_derivative(self, t: Tensor) -> Tensor:
        """Derivative of ``sigma``."""
        t = as_time(t.to(dtype=self.dtype))
        return 0.5 * math.pi * torch.cos(0.5 * math.pi * t)

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
