"""Lipman conditional Gaussian vector field (Theorem 3)."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_shape


@dataclass(frozen=True)
class LipmanConditionalOTField:
    """Conditional OT path field from Lipman eqs. (20)-(21).

    ``mu_t = t x_1``, ``sigma_t = 1 - (1 - sigma_min) t``,
    ``u_t(x | x_1) = (x_1 - (1 - sigma_min) x) / (1 - (1 - sigma_min) t)``.

    This is conditional OT between endpoint Gaussians, not global OT.
    """

    sigma_min: float = 1e-4
    dtype: torch.dtype = DEFAULT_DTYPE

    def evaluate_conditional(self, t: Tensor, x: Tensor, x1: Tensor) -> Tensor:
        """Evaluate conditional velocity of shape ``(n, d)``."""
        assert_dtype(x, self.dtype, "x")
        assert_dtype(x1, self.dtype, "x1")
        assert_shape(x, (None, None), "x")
        assert_shape(x1, x.shape, "x1")
        n = x.shape[0]
        if t.ndim == 0:
            t_col = t.expand(n, 1)
        elif t.ndim == 1:
            t_col = t.unsqueeze(1)
        else:
            t_col = t
        denom = 1.0 - (1.0 - self.sigma_min) * t_col
        return (x1 - (1.0 - self.sigma_min) * x) / denom

    def evaluate(self, t: Tensor, x: Tensor) -> Tensor:
        """Not available without ``x_1``; raise."""
        del t, x
        raise RuntimeError(
            "LipmanConditionalOTField.evaluate requires x1; use evaluate_conditional"
        )

    def jacobian(self, t: Tensor, x: Tensor) -> Tensor:
        """Spatial Jacobian of the conditional field given fixed ``x_1``.

        ``du/dx = -(1 - sigma_min) / denom * I``.
        Requires broadcasting a single time.
        """
        assert_dtype(x, self.dtype, "x")
        n, d = x.shape
        if t.ndim == 0:
            ts = t
        elif t.ndim == 1:
            ts = t[0]
            if not torch.allclose(t, t[0]):
                raise ValueError("jacobian requires constant t in batch")
        else:
            ts = t[0, 0]
        denom = 1.0 - (1.0 - self.sigma_min) * ts
        scale = -(1.0 - self.sigma_min) / denom
        eye = torch.eye(d, dtype=self.dtype, device=x.device)
        return (scale * eye).unsqueeze(0).expand(n, -1, -1).contiguous()

    def time_derivative(self, t: Tensor, x: Tensor) -> Tensor | None:
        """Unavailable without ``x_1``."""
        del t, x
        return None
