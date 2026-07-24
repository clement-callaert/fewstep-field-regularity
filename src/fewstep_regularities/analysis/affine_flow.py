"""Scalar eigenmode formulas for centered Gaussian affine flows."""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import Tensor


@dataclass(frozen=True)
class ScalarAffineQuantities:
    """Scalar variance, drift, and drift derivatives."""

    variance: float
    drift: float
    drift_derivative: float
    drift_second_derivative: float
    drift_third_derivative: float


def scalar_variance(path_name: str, eigenvalue: float, time: float) -> float:
    """Return the path covariance eigenvalue at one time."""
    if eigenvalue <= 0.0:
        raise ValueError("eigenvalue must be positive")
    if not 0.0 <= time <= 1.0:
        raise ValueError("time must be in [0, 1]")
    if path_name == "linear":
        return (1.0 - time) ** 2 + eigenvalue * time**2
    if path_name == "variance_preserving":
        angle = 0.5 * math.pi * time
        return math.cos(angle) ** 2 + eigenvalue * math.sin(angle) ** 2
    raise ValueError(f"Unsupported path {path_name!r}")


def scalar_drift(path_name: str, eigenvalue: float, time: float) -> float:
    """Return the affine drift eigenvalue ``q'(t) / (2 q(t))``."""
    variance = scalar_variance(path_name, eigenvalue, time)
    if path_name == "linear":
        numerator = (1.0 + eigenvalue) * time - 1.0
        return numerator / variance
    numerator = 0.25 * math.pi * (eigenvalue - 1.0) * math.sin(math.pi * time)
    return numerator / variance


def exact_transition_factor(
    path_name: str,
    eigenvalue: float,
    start: float,
    end: float,
) -> float:
    """Return the exact scalar state transition between two times."""
    if end < start:
        raise ValueError("end must not precede start")
    start_variance = scalar_variance(path_name, eigenvalue, start)
    end_variance = scalar_variance(path_name, eigenvalue, end)
    return math.sqrt(end_variance / start_variance)


def scalar_affine_quantities(
    path_name: str,
    eigenvalue: float,
    time: float,
) -> ScalarAffineQuantities:
    """Evaluate the drift and three time derivatives with autograd."""
    if eigenvalue <= 0.0:
        raise ValueError("eigenvalue must be positive")
    t = torch.tensor(time, dtype=torch.float64, requires_grad=True)
    lam = torch.tensor(eigenvalue, dtype=torch.float64)
    if path_name == "linear":
        variance = (1.0 - t) ** 2 + lam * t**2
        drift = ((1.0 + lam) * t - 1.0) / variance
    elif path_name == "variance_preserving":
        angle = 0.5 * torch.pi * t
        variance = torch.cos(angle) ** 2 + lam * torch.sin(angle) ** 2
        drift = 0.25 * torch.pi * (lam - 1.0) * torch.sin(torch.pi * t) / variance
    else:
        raise ValueError(f"Unsupported path {path_name!r}")
    first = torch.autograd.grad(drift, t, create_graph=True)[0]
    second = torch.autograd.grad(first, t, create_graph=True)[0]
    third = torch.autograd.grad(second, t)[0]
    return ScalarAffineQuantities(
        variance=float(variance.detach().item()),
        drift=float(drift.detach().item()),
        drift_derivative=float(first.detach().item()),
        drift_second_derivative=float(second.detach().item()),
        drift_third_derivative=float(third.detach().item()),
    )


def sorted_covariance_eigenvalues(covariance: Tensor) -> list[float]:
    """Return sorted covariance eigenvalues as Python floats."""
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("covariance must be square")
    values = torch.linalg.eigvalsh(covariance)
    if bool(torch.any(values <= 0.0)):
        raise ValueError("covariance must be positive definite")
    return [float(value.item()) for value in values]
