"""Gaussian optimal transport displacement path."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

from fewstep_regularities.distributions.gaussian import Gaussian
from fewstep_regularities.paths.schedules import as_time, validate_path_batch
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_shape


def matrix_sqrt_psd(matrix: Tensor) -> Tensor:
    """Symmetric square root of a PSD matrix via eigen-decomposition."""
    evals, evecs = torch.linalg.eigh(_sym(matrix))
    evals = evals.clamp(min=0.0)
    out: Tensor = (evecs * torch.sqrt(evals).unsqueeze(0)) @ evecs.transpose(0, 1)
    return out


def _sym(matrix: Tensor) -> Tensor:
    return 0.5 * (matrix + matrix.transpose(-1, -2))


def gaussian_ot_matrix(cov0: Tensor, cov1: Tensor) -> Tensor:
    """Return the Brenier OT matrix ``A`` from Peyré (2.40).

    ``A = Σ0^{-1/2} (Σ0^{1/2} Σ1 Σ0^{1/2})^{1/2} Σ0^{-1/2}``.
    """
    assert_shape(cov0, (None, None), "cov0")
    assert_shape(cov1, cov0.shape, "cov1")
    s0 = matrix_sqrt_psd(cov0)
    s0_inv = torch.linalg.inv(s0)
    mid = matrix_sqrt_psd(s0 @ cov1 @ s0)
    out: Tensor = s0_inv @ mid @ s0_inv
    return out


def gaussian_ot_map(x: Tensor, source: Gaussian, target: Gaussian) -> Tensor:
    """Apply the Gaussian OT map ``T(x) = m1 + A (x - m0)``."""
    assert_dtype(x, source.dtype, "x")
    a = gaussian_ot_matrix(source.covariance(), target.covariance())
    return target.mean() + (x - source.mean()) @ a.transpose(0, 1)


@dataclass
class GaussianOTPath:
    """McCann displacement interpolation between two Gaussians.

    Coupling class: Gaussian optimal transport.
    ``X_t = (1-t) X_0 + t T(X_0)`` with ``T`` from Peyré (2.40).

    Protocol ``alpha``/``sigma`` follow the McCann time weights ``1-t`` and ``t``.
    """

    source: Gaussian
    target: Gaussian
    dtype: torch.dtype = DEFAULT_DTYPE
    coupling: str = "gaussian_ot"

    def __post_init__(self) -> None:
        if self.source.dim != self.target.dim:
            raise ValueError("source and target dims must match")
        if self.source.dtype != self.dtype or self.target.dtype != self.dtype:
            raise TypeError("source/target dtype must match path dtype")
        self._a = gaussian_ot_matrix(self.source.covariance(), self.target.covariance())

    def alpha(self, t: Tensor) -> Tensor:
        """McCann weight on identity: ``1 - t``."""
        t = as_time(t.to(dtype=self.dtype))
        return 1.0 - t

    def sigma(self, t: Tensor) -> Tensor:
        """McCann weight on OT map: ``t``."""
        t = as_time(t.to(dtype=self.dtype))
        return t

    def alpha_derivative(self, t: Tensor) -> Tensor:
        """Derivative of ``alpha``."""
        t = as_time(t.to(dtype=self.dtype))
        return torch.full_like(t, -1.0)

    def sigma_derivative(self, t: Tensor) -> Tensor:
        """Derivative of ``sigma``."""
        t = as_time(t.to(dtype=self.dtype))
        return torch.ones_like(t)

    def transport(self, x0: Tensor) -> Tensor:
        """OT map applied to ``x0`` of shape ``(n, d)``."""
        return gaussian_ot_map(x0, self.source, self.target)

    def marginal_sample(
        self,
        t: Tensor,
        x0: Tensor,
        x1: Tensor,
        noise: Tensor | None = None,
    ) -> Tensor:
        """Sample displacement interpolant from ``x0`` (``x1`` ignored).

        Uses ``T(x0)`` so the coupling is the OT coupling, not ``(x0, x1)``.
        """
        del noise, x1
        t_col, x0, _ = validate_path_batch(
            t, x0, torch.zeros_like(x0), self.dtype
        )
        tx = self.transport(x0)
        return self.alpha(t_col) * x0 + self.sigma(t_col) * tx

    def conditional_velocity(
        self,
        t: Tensor,
        x: Tensor,
        x0: Tensor,
        x1: Tensor,
    ) -> Tensor:
        """Velocity along OT rays: ``T(x0) - x0``."""
        del t, x, x1
        return self.transport(x0) - x0

    def marginal_velocity(self, t: Tensor, x: Tensor) -> Tensor | None:
        """Exact marginal OT velocity via affine Gaussian field formula.

        For McCann Gaussian displacement, ``X_t ~ N(m_t, Σ_t)`` with
        ``m_t = (1-t) m0 + t m1`` and ``Σ_t = ((1-t) I + t A) Σ0 ((1-t)I + t A)^T``.
        The velocity is implemented by ``GaussianAffineField``; return None here
        to avoid circular imports. Use the field module for ODE integration.
        """
        del t, x
        return None
