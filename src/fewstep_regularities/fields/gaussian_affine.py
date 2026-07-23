"""Exact affine Gaussian marginal velocity fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import torch
from torch import Tensor

from fewstep_regularities.distributions.gaussian import Gaussian
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_device, assert_finite, assert_shape


class ScalarSchedule(Protocol):
    """Minimal schedule interface used by the affine field."""

    def alpha(self, t: Tensor) -> Tensor: ...

    def sigma(self, t: Tensor) -> Tensor: ...

    def alpha_derivative(self, t: Tensor) -> Tensor: ...

    def sigma_derivative(self, t: Tensor) -> Tensor: ...


def _time_col(t: Tensor, n: int, dtype: torch.dtype) -> Tensor:
    """Normalize time to shape ``(n, 1)``."""
    assert_dtype(t, dtype, "t")
    if t.ndim == 0:
        return t.expand(n, 1)
    if t.ndim == 1:
        if t.shape[0] == 1:
            return t.expand(n).unsqueeze(1)
        if t.shape[0] != n:
            raise ValueError("t length must match batch size")
        return t.unsqueeze(1)
    if t.ndim == 2 and t.shape == (n, 1):
        return t
    raise ValueError("t must be scalar or shape (n,) / (n, 1)")


@dataclass
class GaussianAffineField:
    """Exact marginal velocity for Gaussian endpoints under a scalar schedule.

    Field ID: ``gaussian_affine_marginal``.

    Mathematical definition:
        ``I_t = α_t z + β_t x_1`` with independent Gaussians,
        ``b_t(x) = ṁ_t + C_t Σ_t^{-1} (x - m_t)``,
        ``C_t = α' α Σ_0 + β' β Σ_1``,
        ``Σ_t = α^2 Σ_0 + β^2 Σ_1``.

    References:
        Lipschitz-guided Example 3.3 (isotropic) generalized; see
        docs/MATHEMATICAL_NOTES.md.
    """

    source: Gaussian
    target: Gaussian
    schedule: ScalarSchedule
    dtype: torch.dtype = DEFAULT_DTYPE

    def __post_init__(self) -> None:
        if self.source.dim != self.target.dim:
            raise ValueError("source and target dims must match")
        if self.source.dtype != self.dtype or self.target.dtype != self.dtype:
            raise TypeError("dtype mismatch")

    @property
    def dim(self) -> int:
        """Ambient dimension."""
        return self.source.dim

    def mean_t(self, t: Tensor) -> Tensor:
        """Marginal mean ``m_t`` of shape ``(n, d)`` or ``(d,)``."""
        a = self.schedule.alpha(t)
        s = self.schedule.sigma(t)
        while a.ndim < self.source.mean().ndim + (0 if t.ndim == 0 else 1):
            a = a.unsqueeze(-1)
            s = s.unsqueeze(-1)
        if t.ndim == 0:
            return a * self.source.mean() + s * self.target.mean()
        if a.ndim == 1:
            a = a.unsqueeze(1)
            s = s.unsqueeze(1)
        return a * self.source.mean() + s * self.target.mean()

    def cov_t(self, t_scalar: float | Tensor) -> Tensor:
        """Marginal covariance ``Σ_t`` of shape ``(d, d)`` at a scalar time."""
        if isinstance(t_scalar, Tensor):
            assert_dtype(t_scalar, self.dtype, "t")
            assert_device(t_scalar, self.source.device, "t")
            t = t_scalar.reshape(())
        else:
            t = torch.tensor(t_scalar, dtype=self.dtype, device=self.source.device)
        a = self.schedule.alpha(t)
        s = self.schedule.sigma(t)
        return (a**2) * self.source.covariance() + (s**2) * self.target.covariance()

    def cross_cov_t(self, t_scalar: float | Tensor) -> Tensor:
        """``C_t = Cov(İ_t, I_t)`` of shape ``(d, d)``."""
        if isinstance(t_scalar, Tensor):
            assert_dtype(t_scalar, self.dtype, "t")
            assert_device(t_scalar, self.source.device, "t")
            t = t_scalar.reshape(())
        else:
            t = torch.tensor(t_scalar, dtype=self.dtype, device=self.source.device)
        a = self.schedule.alpha(t)
        s = self.schedule.sigma(t)
        ap = self.schedule.alpha_derivative(t)
        sp = self.schedule.sigma_derivative(t)
        return ap * a * self.source.covariance() + sp * s * self.target.covariance()

    def jacobian_matrix(self, t_scalar: float | Tensor) -> Tensor:
        """State-independent Jacobian ``J_t = C_t Σ_t^{-1}`` of shape ``(d, d)``."""
        c = self.cross_cov_t(t_scalar)
        sigma = self.cov_t(t_scalar)
        out: Tensor = torch.linalg.solve(sigma.transpose(0, 1), c.transpose(0, 1)).transpose(
            0, 1
        )
        return out

    def mean_velocity(self, t_scalar: float | Tensor) -> Tensor:
        """``ṁ_t`` of shape ``(d,)``."""
        if isinstance(t_scalar, Tensor):
            assert_dtype(t_scalar, self.dtype, "t")
            assert_device(t_scalar, self.source.device, "t")
            t = t_scalar.reshape(())
        else:
            t = torch.tensor(t_scalar, dtype=self.dtype, device=self.source.device)
        ap = self.schedule.alpha_derivative(t)
        sp = self.schedule.sigma_derivative(t)
        return ap * self.source.mean() + sp * self.target.mean()

    def evaluate(self, t: Tensor, x: Tensor) -> Tensor:
        """Evaluate ``b_t(x)`` of shape ``(n, d)``."""
        assert_dtype(x, self.dtype, "x")
        assert_device(x, self.source.device, "x")
        assert_shape(x, (None, self.dim), "x")
        n = x.shape[0]
        t_col = _time_col(t, n, self.dtype)
        assert_device(t_col, x.device, "t")
        # Use per-row times when they differ; otherwise one solve.
        if torch.allclose(t_col, t_col[0:1]):
            ts = t_col[0, 0]
            m = self.mean_t(ts)
            j = self.jacobian_matrix(ts)
            mv = self.mean_velocity(ts)
            out = mv.unsqueeze(0) + (x - m.unsqueeze(0)) @ j.transpose(0, 1)
        else:
            outs = []
            for i in range(n):
                ts = t_col[i, 0]
                m = self.mean_t(ts)
                j = self.jacobian_matrix(ts)
                mv = self.mean_velocity(ts)
                outs.append(mv + j @ (x[i] - m))
            out = torch.stack(outs, dim=0)
        assert_finite(out, "velocity")
        return out

    def jacobian(self, t: Tensor, x: Tensor) -> Tensor:
        """Jacobian batch of shape ``(n, d, d)``."""
        assert_dtype(x, self.dtype, "x")
        assert_device(x, self.source.device, "x")
        assert_shape(x, (None, self.dim), "x")
        n = x.shape[0]
        t_col = _time_col(t, n, self.dtype)
        assert_device(t_col, x.device, "t")
        if torch.allclose(t_col, t_col[0:1]):
            j = self.jacobian_matrix(t_col[0, 0])
            return j.unsqueeze(0).expand(n, -1, -1).contiguous()
        return torch.stack([self.jacobian_matrix(t_col[i, 0]) for i in range(n)], dim=0)

    def time_derivative(self, t: Tensor, x: Tensor) -> Tensor | None:
        """Finite-difference ``∂_t b`` at fixed ``x`` (documented FD estimator)."""
        assert_dtype(x, self.dtype, "x")
        assert_device(x, self.source.device, "x")
        n = x.shape[0]
        t_col = _time_col(t, n, self.dtype)
        assert_device(t_col, x.device, "t")
        eps = torch.tensor(1e-6, dtype=self.dtype, device=x.device)
        t_plus = (t_col + eps).clamp(0.0, 1.0).squeeze(1)
        t_minus = (t_col - eps).clamp(0.0, 1.0).clamp_max(1.0).squeeze(1)
        # Recompute clamp for lower bound.
        t_minus = (t_col.squeeze(1) - eps).clamp(min=0.0, max=1.0)
        dt = (t_plus - t_minus).clamp(min=1e-12)
        vp = self.evaluate(t_plus, x)
        vm = self.evaluate(t_minus, x)
        return (vp - vm) / dt.unsqueeze(1)
