"""Gaussian OT McCann displacement velocity field."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

from fewstep_regularities.distributions.gaussian import Gaussian
from fewstep_regularities.paths.gaussian_ot import gaussian_ot_matrix
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_finite, assert_shape


@dataclass
class GaussianOTField:
    """Eulerian velocity for McCann displacement between Gaussians.

    Field ID: ``gaussian_ot_displacement``.

    Along rays ``X_t = (1-t) X_0 + t T(X_0)``, velocity is ``T(X_0) - X_0``.
    In Eulerian coordinates for Gaussian endpoints this is the affine field

    ``b_t(x) = ṁ_t + J_t (x - m_t)``

    with ``m_t = (1-t) m_0 + t m_1`` and
    ``S_t = (1-t) I + t A``, ``Σ_t = S_t Σ_0 S_t^T``,
    ``J_t = (A - I) S_t^{-1}`` (constant-speed McCann).

    References: Peyré (2.40); docs/MATHEMATICAL_NOTES.md.
    """

    source: Gaussian
    target: Gaussian
    dtype: torch.dtype = DEFAULT_DTYPE

    def __post_init__(self) -> None:
        if self.source.dim != self.target.dim:
            raise ValueError("dims must match")
        self._a = gaussian_ot_matrix(self.source.covariance(), self.target.covariance())
        self._eye = torch.eye(self.source.dim, dtype=self.dtype, device=self.source.device)

    @property
    def dim(self) -> int:
        """Ambient dimension."""
        return self.source.dim

    def _s_t(self, t: Tensor) -> Tensor:
        """``S_t = (1-t) I + t A``."""
        return (1.0 - t) * self._eye + t * self._a

    def mean_t(self, t: Tensor) -> Tensor:
        """Marginal mean."""
        return (1.0 - t) * self.source.mean() + t * self.target.mean()

    def cov_t(self, t: Tensor) -> Tensor:
        """Marginal covariance ``S_t Σ_0 S_t^T``."""
        s = self._s_t(t)
        return s @ self.source.covariance() @ s.transpose(0, 1)

    def jacobian_matrix(self, t: Tensor) -> Tensor:
        """``J_t = (A - I) S_t^{-1}``."""
        s = self._s_t(t)
        out: Tensor = (self._a - self._eye) @ torch.linalg.inv(s)
        return out

    def evaluate(self, t: Tensor, x: Tensor) -> Tensor:
        """Evaluate OT displacement velocity.

        ``b_t(x) = (m_1 - m_0) + J_t (x - m_t)`` with ``J_t = (A - I) S_t^{-1}``.
        """
        assert_dtype(x, self.dtype, "x")
        assert_shape(x, (None, self.dim), "x")
        n = x.shape[0]
        mv = self.target.mean() - self.source.mean()

        def one(ts: Tensor, xi: Tensor) -> Tensor:
            m = self.mean_t(ts)
            j = self.jacobian_matrix(ts)
            return mv + j @ (xi - m)

        if t.ndim == 0:
            ts = t.to(dtype=self.dtype)
            j = self.jacobian_matrix(ts)
            m = self.mean_t(ts)
            out = mv.unsqueeze(0) + (x - m.unsqueeze(0)) @ j.transpose(0, 1)
        elif t.ndim == 1:
            if torch.allclose(t, t[0]):
                ts = t[0].to(dtype=self.dtype)
                j = self.jacobian_matrix(ts)
                m = self.mean_t(ts)
                out = mv.unsqueeze(0) + (x - m.unsqueeze(0)) @ j.transpose(0, 1)
            else:
                out = torch.stack(
                    [one(t[i].to(dtype=self.dtype), x[i]) for i in range(n)],
                    dim=0,
                )
        else:
            ts = t[0, 0].to(dtype=self.dtype)
            j = self.jacobian_matrix(ts)
            m = self.mean_t(ts)
            out = mv.unsqueeze(0) + (x - m.unsqueeze(0)) @ j.transpose(0, 1)
        assert_finite(out, "velocity")
        return out

    def jacobian(self, t: Tensor, x: Tensor) -> Tensor:
        """Jacobian batch ``(n, d, d)``."""
        assert_shape(x, (None, self.dim), "x")
        n = x.shape[0]
        if t.ndim == 0:
            j = self.jacobian_matrix(t.to(dtype=self.dtype))
            return j.unsqueeze(0).expand(n, -1, -1).contiguous()
        if t.ndim == 1 and torch.allclose(t, t[0]):
            j = self.jacobian_matrix(t[0].to(dtype=self.dtype))
            return j.unsqueeze(0).expand(n, -1, -1).contiguous()
        return torch.stack(
            [self.jacobian_matrix(t[i].to(dtype=self.dtype)) for i in range(n)],
            dim=0,
        )

    def time_derivative(self, t: Tensor, x: Tensor) -> Tensor | None:
        """FD estimate of ``∂_t v``."""
        n = x.shape[0]
        if t.ndim == 0:
            t_vec = t.expand(n)
        elif t.ndim == 1:
            t_vec = t
        else:
            t_vec = t.squeeze(1)
        eps = 1e-6
        tp = (t_vec + eps).clamp(0.0, 1.0)
        tm = (t_vec - eps).clamp(0.0, 1.0)
        dt = (tp - tm).clamp(min=1e-12)
        return (self.evaluate(tp, x) - self.evaluate(tm, x)) / dt.unsqueeze(1)
