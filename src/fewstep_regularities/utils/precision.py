"""Precision policy helpers.

Analytical experiments default to float64.
Do not silently cast precision at module boundaries.
"""

from __future__ import annotations

import torch
from torch import Tensor

DEFAULT_DTYPE = torch.float64


def resolve_dtype(name: str) -> torch.dtype:
    """Map a config dtype name to a torch dtype.

    Args:
        name: One of ``float64``, ``float32``, ``float16``, ``bfloat16``.

    Returns:
        Corresponding ``torch.dtype``.
    """
    mapping = {
        "float64": torch.float64,
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    if name not in mapping:
        msg = f"Unsupported dtype name: {name}"
        raise ValueError(msg)
    return mapping[name]


def assert_dtype(tensor: Tensor, expected: torch.dtype, name: str = "tensor") -> None:
    """Raise if a tensor does not match the expected dtype.

    Args:
        tensor: Input tensor.
        expected: Required dtype.
        name: Name used in the error message.
    """
    if tensor.dtype != expected:
        msg = f"{name} has dtype {tensor.dtype}, expected {expected}"
        raise TypeError(msg)
