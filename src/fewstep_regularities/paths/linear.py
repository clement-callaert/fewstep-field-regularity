"""Linear independent-coupling probability path."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

from fewstep_regularities.paths.schedules import as_time, validate_path_batch
from fewstep_regularities.utils.precision import DEFAULT_DTYPE


@dataclass(frozen=True)
class LinearPath:
    """Independent coupling with ``x_t = (1-t) x_0 + t x_1``.

    Coupling class: independent.
    References: Liu eq. (1); Albergo Fig. 2; Lipschitz reference schedule.
    Protocol map: ``alpha(t)=1-t``, ``sigma(t)=t``.
    """

    dtype: torch.dtype = DEFAULT_DTYPE
    coupling: str = "independent"

    def alpha(self, t: Tensor) -> Tensor:
        """Source coefficient ``1 - t``."""
        t = as_time(t, self.dtype)
        return 1.0 - t

    def sigma(self, t: Tensor) -> Tensor:
        """Target coefficient ``t``."""
        t = as_time(t, self.dtype)
        return t

    def alpha_derivative(self, t: Tensor) -> Tensor:
        """Derivative of ``alpha``: ``-1``."""
        t = as_time(t, self.dtype)
        return torch.full_like(t, -1.0)

    def sigma_derivative(self, t: Tensor) -> Tensor:
        """Derivative of ``sigma``: ``+1``."""
        t = as_time(t, self.dtype)
        return torch.ones_like(t)

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
        a = self.alpha(t_col)
        s = self.sigma(t_col)
        return a * x0 + s * x1

    def conditional_velocity(
        self,
        t: Tensor,
        x: Tensor,
        x0: Tensor,
        x1: Tensor,
    ) -> Tensor:
        """Conditional velocity ``x_1 - x_0`` (constant in time)."""
        del t, x
        if x0.shape != x1.shape:
            raise ValueError("x0 and x1 must share shape")
        return x1 - x0

    def marginal_velocity(self, t: Tensor, x: Tensor) -> Tensor | None:
        """Marginal velocity unavailable without endpoint laws."""
        del t, x
        return None
