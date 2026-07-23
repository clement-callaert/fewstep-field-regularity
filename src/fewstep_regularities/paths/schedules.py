"""Shared schedule helpers for scalar probability paths."""

from __future__ import annotations

import torch
from torch import Tensor

from fewstep_regularities.utils.precision import assert_dtype
from fewstep_regularities.utils.shapes import assert_finite


def as_time(t: Tensor, dtype: torch.dtype | None = None) -> Tensor:
    """Validate and return a time tensor."""
    if dtype is not None:
        assert_dtype(t, dtype, "t")
    assert_finite(t, "t")
    return t


def broadcast_pair(t: Tensor, alpha: Tensor, sigma: Tensor) -> tuple[Tensor, Tensor]:
    """Broadcast schedule values to the shape of ``t``."""
    return alpha.expand_as(t), sigma.expand_as(t)


def validate_path_batch(
    t: Tensor,
    x0: Tensor,
    x1: Tensor,
    dtype: torch.dtype,
) -> tuple[Tensor, Tensor, Tensor]:
    """Validate endpoint batch shapes and dtypes.

    Args:
        t: Times of shape ``(n,)`` or ``(n, 1)``.
        x0: Source samples ``(n, d)``.
        x1: Target samples ``(n, d)``.
        dtype: Required dtype.

    Returns:
        ``(t_col, x0, x1)`` with ``t_col`` shape ``(n, 1)``.
    """
    assert_dtype(x0, dtype, "x0")
    assert_dtype(x1, dtype, "x1")
    assert_dtype(t, dtype, "t")
    if x0.ndim != 2 or x1.ndim != 2:
        raise ValueError("x0 and x1 must have shape (n, d)")
    if x0.shape != x1.shape:
        raise ValueError("x0 and x1 must share shape")
    n = x0.shape[0]
    if t.ndim == 1:
        if t.shape[0] != n:
            raise ValueError("t length must match batch size")
        t_col = t.unsqueeze(1)
    elif t.ndim == 2 and t.shape == (n, 1):
        t_col = t
    else:
        raise ValueError("t must have shape (n,) or (n, 1)")
    return t_col, x0, x1
