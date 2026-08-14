"""Scalar eigenmode formulas for centered Gaussian affine flows."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from torch import Tensor


LOG_COVARIANCE_SCALAR = "log_covariance_scalar"


@dataclass(frozen=True)
class ScalarAffineQuantities:
    """Scalar variance, drift, and drift derivatives."""

    variance: float
    drift: float
    drift_derivative: float
    drift_second_derivative: float
    drift_third_derivative: float


def canonical_path_name(path_name: str) -> str:
    """Return the path family, stripping an optional encoded schedule M."""
    return path_name.split("|", 1)[0]


def shared_logcov_path(schedule_m: float) -> str:
    """Return the encoded shared Chen Ex. 3.3 interpolant with ratio ``M``."""
    if schedule_m <= 0.0:
        raise ValueError("schedule_m must be positive")
    if abs(schedule_m - 1.0) < 1e-12:
        raise ValueError("schedule_m must differ from 1")
    return f"{LOG_COVARIANCE_SCALAR}|{schedule_m:.16g}"


def path_schedule_m(path_name: str, eigenvalue: float) -> float:
    """Return the shared log-covariance ratio, defaulting to the eigenmode."""
    family = canonical_path_name(path_name)
    if family != LOG_COVARIANCE_SCALAR:
        raise ValueError(f"path {path_name!r} has no shared schedule M")
    if "|" in path_name:
        return float(path_name.split("|", 1)[1])
    return float(eigenvalue)


def shared_logcov_variance(eigenvalue: float, time: float, schedule_m: float) -> float:
    """Return ``α(t)^2 + λ σ(t)^2`` for Chen Ex. 3.3 with shared ``M=λ_max``.

    The interpolant is the one-sided schedule with ``α^2+σ^2=1`` and
    ``σ^2=(M^t-1)/(M-1)``, so ``q_λ(t)=1+(λ-1)(M^t-1)/(M-1)``.
    """
    if schedule_m <= 0.0 or abs(schedule_m - 1.0) < 1e-12:
        raise ValueError("schedule_m must be positive and differ from 1")
    beta_sq = (math.pow(schedule_m, time) - 1.0) / (schedule_m - 1.0)
    return 1.0 + (eigenvalue - 1.0) * beta_sq


def shared_logcov_drift(eigenvalue: float, time: float, schedule_m: float) -> float:
    """Return ``q'(t)/(2q(t))`` for the shared Chen Ex. 3.3 interpolant."""
    if schedule_m <= 0.0 or abs(schedule_m - 1.0) < 1e-12:
        raise ValueError("schedule_m must be positive and differ from 1")
    m_t = math.pow(schedule_m, time)
    numerator = (eigenvalue - 1.0) * m_t * math.log(schedule_m)
    denominator = 2.0 * ((eigenvalue - 1.0) * m_t + (schedule_m - eigenvalue))
    return numerator / denominator


def scalar_variance(path_name: str, eigenvalue: float, time: float) -> float:
    """Return the path covariance eigenvalue at one time."""
    if eigenvalue <= 0.0:
        raise ValueError("eigenvalue must be positive")
    if not 0.0 <= time <= 1.0:
        raise ValueError("time must be in [0, 1]")
    family = canonical_path_name(path_name)
    if family == "linear":
        return (1.0 - time) ** 2 + eigenvalue * time**2
    if family == "variance_preserving":
        angle = 0.5 * math.pi * time
        return math.cos(angle) ** 2 + eigenvalue * math.sin(angle) ** 2
    if family == "log_covariance":
        # Chen et al. Ex. 3.3 per mode: q(t) = lambda^t.
        return math.exp(time * math.log(eigenvalue))
    if family == LOG_COVARIANCE_SCALAR:
        return shared_logcov_variance(
            eigenvalue, time, path_schedule_m(path_name, eigenvalue)
        )
    raise ValueError(f"Unsupported path {path_name!r}")


def scalar_drift(path_name: str, eigenvalue: float, time: float) -> float:
    """Return the affine drift eigenvalue ``q'(t) / (2 q(t))``."""
    family = canonical_path_name(path_name)
    if family == "log_covariance":
        return 0.5 * math.log(eigenvalue)
    if family == LOG_COVARIANCE_SCALAR:
        return shared_logcov_drift(
            eigenvalue, time, path_schedule_m(path_name, eigenvalue)
        )
    variance = scalar_variance(path_name, eigenvalue, time)
    if family == "linear":
        numerator = (1.0 + eigenvalue) * time - 1.0
        return numerator / variance
    if family == "variance_preserving":
        numerator = 0.25 * math.pi * (eigenvalue - 1.0) * math.sin(math.pi * time)
        return numerator / variance
    raise ValueError(f"Unsupported path {path_name!r}")


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
    import torch

    if eigenvalue <= 0.0:
        raise ValueError("eigenvalue must be positive")
    t = torch.tensor(time, dtype=torch.float64, requires_grad=True)
    lam = torch.tensor(eigenvalue, dtype=torch.float64)
    family = canonical_path_name(path_name)
    if family == "linear":
        variance = (1.0 - t) ** 2 + lam * t**2
        drift = ((1.0 + lam) * t - 1.0) / variance
    elif family == "variance_preserving":
        angle = 0.5 * torch.pi * t
        variance = torch.cos(angle) ** 2 + lam * torch.sin(angle) ** 2
        drift = 0.25 * torch.pi * (lam - 1.0) * torch.sin(torch.pi * t) / variance
    elif family == "log_covariance":
        variance = torch.exp(t * torch.log(lam))
        drift = 0.5 * torch.log(lam) + 0.0 * t
    elif family == LOG_COVARIANCE_SCALAR:
        schedule_m = path_schedule_m(path_name, eigenvalue)
        m_t = torch.tensor(schedule_m, dtype=torch.float64)
        m_pow = torch.pow(m_t, t)
        variance = 1.0 + (lam - 1.0) * (m_pow - 1.0) / (m_t - 1.0)
        drift = (
            (lam - 1.0)
            * m_pow
            * torch.log(m_t)
            / (2.0 * ((lam - 1.0) * m_pow + (m_t - lam)))
        )
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
    import torch

    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("covariance must be square")
    values = torch.linalg.eigvalsh(covariance)
    if bool(torch.any(values <= 0.0)):
        raise ValueError("covariance must be positive definite")
    return [float(value.item()) for value in values]
