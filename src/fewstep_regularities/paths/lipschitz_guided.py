"""Lipschitz-guided scalar schedule for Gaussian variance ratio M."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

from fewstep_regularities.paths.schedules import as_time, validate_path_batch
from fewstep_regularities.utils.precision import DEFAULT_DTYPE


def lipschitz_guided_beta_sq(t: Tensor, m: float) -> Tensor:
    """Return ``β_t^2`` for the log-covariance schedule.

    From Lipschitz-guided Ex. 3.3: ``log Cov(I_t)`` is linear in ``t``,
    with ``α^2 + β^2 = 1`` and ``Cov(I_0)=1``, ``Cov(I_1)=M``,

    ``β_t^2 = (M^t - 1) / (M - 1)`` for ``M ≠ 1``.
    """
    if m <= 0:
        raise ValueError("M must be positive")
    if abs(m - 1.0) < 1e-12:
        raise ValueError("M must differ from 1 for Lipschitz-guided schedule")
    m_t = torch.tensor(m, dtype=t.dtype, device=t.device)
    return (torch.pow(m_t, t) - 1.0) / (m - 1.0)


@dataclass(frozen=True)
class LipschitzGuidedPath:
    """Schedule reparameterization minimizing avg-Lip² for scalar Gaussian M.

    Coupling class: schedule reparameterization (one-sided SI form).
    Uses ``α_t^2 = 1 - β_t^2``, ``β_t^2 = (M^t - 1)/(M - 1)``.

    For anisotropic targets, pass an effective scalar ``M`` (documented
    approximation; exact multi-eigenvalue design is out of Phase 1 scope).
    """

    m: float
    dtype: torch.dtype = DEFAULT_DTYPE
    coupling: str = "schedule_reparameterization"

    def alpha(self, t: Tensor) -> Tensor:
        """Noise coefficient ``α_t = sqrt(1 - β_t^2)``."""
        t = as_time(t, self.dtype)
        beta_sq = lipschitz_guided_beta_sq(t, self.m)
        alpha_sq = (1.0 - beta_sq).clamp(min=0.0)
        return torch.sqrt(alpha_sq)

    def sigma(self, t: Tensor) -> Tensor:
        """Data coefficient ``β_t``."""
        t = as_time(t, self.dtype)
        beta_sq = lipschitz_guided_beta_sq(t, self.m).clamp(min=0.0)
        return torch.sqrt(beta_sq)

    def alpha_derivative(self, t: Tensor) -> Tensor:
        """Time derivative of ``alpha`` via analytic chain rule."""
        t = as_time(t, self.dtype)
        beta_sq = lipschitz_guided_beta_sq(t, self.m).clamp(min=0.0)
        # d/dt β^2 = M^t log(M) / (M - 1)
        log_m = math_log(self.m, t.dtype, t.device)
        m_t = torch.pow(torch.tensor(self.m, dtype=t.dtype, device=t.device), t)
        d_beta_sq = m_t * log_m / (self.m - 1.0)
        alpha = torch.sqrt((1.0 - beta_sq).clamp(min=1e-32))
        # α' = -0.5 (β^2)' / α
        return -0.5 * d_beta_sq / alpha

    def sigma_derivative(self, t: Tensor) -> Tensor:
        """Time derivative of ``sigma`` via analytic chain rule."""
        t = as_time(t, self.dtype)
        beta_sq = lipschitz_guided_beta_sq(t, self.m).clamp(min=0.0)
        log_m = math_log(self.m, t.dtype, t.device)
        m_t = torch.pow(torch.tensor(self.m, dtype=t.dtype, device=t.device), t)
        d_beta_sq = m_t * log_m / (self.m - 1.0)
        beta = torch.sqrt(beta_sq.clamp(min=1e-32))
        # β' = 0.5 (β^2)' / β
        return 0.5 * d_beta_sq / beta

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


def math_log(value: float, dtype: torch.dtype, device: torch.device) -> Tensor:
    """Natural log as a tensor scalar."""
    return torch.log(torch.tensor(value, dtype=dtype, device=device))
