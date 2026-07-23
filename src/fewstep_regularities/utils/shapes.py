"""Shape and dtype validators for module boundaries."""

from __future__ import annotations

from collections.abc import Sequence

import torch
from torch import Tensor


def assert_shape(
    tensor: Tensor,
    expected: Sequence[int | None],
    name: str = "tensor",
) -> None:
    """Validate tensor rank and selected dimensions.

    Args:
        tensor: Input tensor.
        expected: Expected shape. Use ``None`` for a free dimension.
        name: Name used in the error message.
    """
    if tensor.ndim != len(expected):
        msg = f"{name} has rank {tensor.ndim}, expected {len(expected)}"
        raise ValueError(msg)
    for axis, (got, want) in enumerate(zip(tensor.shape, expected, strict=True)):
        if want is not None and got != want:
            msg = f"{name} dim {axis} is {got}, expected {want}"
            raise ValueError(msg)


def assert_device(tensor: Tensor, device: torch.device, name: str = "tensor") -> None:
    """Validate tensor device."""
    if tensor.device != device:
        msg = f"{name} is on {tensor.device}, expected {device}"
        raise ValueError(msg)


def assert_finite(tensor: Tensor, name: str = "tensor") -> None:
    """Require all entries to be finite."""
    if not torch.isfinite(tensor).all():
        msg = f"{name} contains non-finite values"
        raise ValueError(msg)
