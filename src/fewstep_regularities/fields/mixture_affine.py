"""Exact mixture marginal velocity under independent scalar schedules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import torch
from torch import Tensor

from fewstep_regularities.distributions.gaussian import Gaussian, standard_gaussian
from fewstep_regularities.distributions.gaussian_mixture import GaussianMixture
from fewstep_regularities.fields.gaussian_affine import GaussianAffineField, _time_col
from fewstep_regularities.utils.precision import DEFAULT_DTYPE, assert_dtype
from fewstep_regularities.utils.shapes import assert_device, assert_finite, assert_shape


class ScalarSchedule(Protocol):
    """Minimal schedule interface used by the mixture field."""

    def alpha(self, t: Tensor) -> Tensor: ...

    def sigma(self, t: Tensor) -> Tensor: ...

    def alpha_derivative(self, t: Tensor) -> Tensor: ...

    def sigma_derivative(self, t: Tensor) -> Tensor: ...


@dataclass
class MixtureAffineField:
    """Exact marginal velocity for GMM targets under independent coupling.

    Field ID: ``mixture_affine_marginal``.

    Mathematical definition:
        Marginal law at time ``t`` is a GMM with
        ``μ_{k,t} = σ_t μ_k``, ``Σ_{k,t} = α_t² I + σ_t² Σ_k``
        (standard Gaussian source). Velocity is
        ``b_t(x) = ∑_k r_{k,t}(x) b_{k,t}(x)``.

    References:
        docs/MATHEMATICAL_NOTES.md (original derivation).
        Per-component fields match ``gaussian_affine_marginal``.
    """

    source: Gaussian
    target: GaussianMixture
    schedule: ScalarSchedule
    dtype: torch.dtype = DEFAULT_DTYPE

    def __post_init__(self) -> None:
        if self.source.dim != self.target.dim:
            raise ValueError("source and target dims must match")
        if self.source.dtype != self.dtype or self.target.dtype != self.dtype:
            raise TypeError("dtype mismatch")
        if self.source.device != self.target.device:
            raise ValueError("source and target devices must match")
        # Independent coupling derivation assumes N(0, I) source.
        eye = torch.eye(self.source.dim, dtype=self.dtype, device=self.source.device)
        if not torch.allclose(self.source.mean(), torch.zeros_like(self.source.mean())):
            raise ValueError("mixture field requires zero-mean Gaussian source")
        if not torch.allclose(self.source.covariance(), eye):
            raise ValueError("mixture field requires identity source covariance")

    @property
    def dim(self) -> int:
        """Ambient dimension."""
        return self.source.dim

    def marginal_mixture(self, t_scalar: float | Tensor) -> GaussianMixture:
        """Time-``t`` marginal GMM parameters."""
        if isinstance(t_scalar, Tensor):
            assert_dtype(t_scalar, self.dtype, "t")
            assert_device(t_scalar, self.target.device, "t")
            t = t_scalar.reshape(())
        else:
            t = torch.tensor(t_scalar, dtype=self.dtype, device=self.target.device)
        a = self.schedule.alpha(t)
        s = self.schedule.sigma(t)
        means = s * self.target.means
        eye = torch.eye(self.dim, dtype=self.dtype, device=self.target.device)
        covs = (a**2) * eye.unsqueeze(0) + (s**2) * self.target.covs
        return GaussianMixture(
            weights=self.target.weights,
            means=means,
            covs=covs,
            _dtype=self.dtype,
            _device=self.target.device,
        )

    def _component_field(self, index: int) -> GaussianAffineField:
        return GaussianAffineField(
            source=self.source,
            target=self.target.component(index),
            schedule=self.schedule,
            dtype=self.dtype,
        )

    def evaluate(self, t: Tensor, x: Tensor) -> Tensor:
        """Evaluate ``b_t(x)`` of shape ``(n, d)``."""
        assert_dtype(x, self.dtype, "x")
        assert_device(x, self.target.device, "x")
        assert_shape(x, (None, self.dim), "x")
        n = x.shape[0]
        t_col = _time_col(t, n, self.dtype)
        assert_device(t_col, x.device, "t")
        if not torch.allclose(t_col, t_col[0:1]):
            outs = [self.evaluate(t_col[i, 0], x[i : i + 1])[0] for i in range(n)]
            return torch.stack(outs, dim=0)
        ts = t_col[0, 0]
        marg = self.marginal_mixture(ts)
        resp = marg.responsibilities(x)
        out = torch.zeros_like(x)
        for k in range(self.target.n_components):
            b_k = self._component_field(k).evaluate(ts, x)
            out = out + resp[:, k : k + 1] * b_k
        assert_finite(out, "mixture velocity")
        return out

    def jacobian(self, t: Tensor, x: Tensor) -> Tensor:
        """State-dependent Jacobian of shape ``(n, d, d)``.

        ``J = ∑_k r_k J_k + ∑_k outer(b_k, ∇r_k)`` with
        ``∇r_k = r_k (score_k - score)``.
        """
        assert_dtype(x, self.dtype, "x")
        assert_device(x, self.target.device, "x")
        assert_shape(x, (None, self.dim), "x")
        n = x.shape[0]
        t_col = _time_col(t, n, self.dtype)
        assert_device(t_col, x.device, "t")
        if not torch.allclose(t_col, t_col[0:1]):
            return torch.stack(
                [self.jacobian(t_col[i, 0], x[i : i + 1])[0] for i in range(n)], dim=0
            )
        ts = t_col[0, 0]
        marg = self.marginal_mixture(ts)
        resp = marg.responsibilities(x)
        score = marg.score(x)
        jac = torch.zeros(n, self.dim, self.dim, dtype=self.dtype, device=x.device)
        for k in range(self.target.n_components):
            field_k = self._component_field(k)
            j_k = field_k.jacobian_matrix(ts)
            b_k = field_k.evaluate(ts, x)
            score_k = marg.component(k).score(x)
            grad_r = resp[:, k : k + 1] * (score_k - score)
            jac = jac + resp[:, k].view(n, 1, 1) * j_k.unsqueeze(0)
            jac = jac + b_k.unsqueeze(2) * grad_r.unsqueeze(1)
        assert_finite(jac, "mixture jacobian")
        return jac

    def time_derivative(self, t: Tensor, x: Tensor) -> Tensor | None:
        """Finite-difference ``∂_t b`` at fixed ``x``."""
        assert_dtype(x, self.dtype, "x")
        assert_device(x, self.target.device, "x")
        n = x.shape[0]
        t_col = _time_col(t, n, self.dtype)
        assert_device(t_col, x.device, "t")
        eps = torch.tensor(1e-6, dtype=self.dtype, device=x.device)
        t_plus = (t_col.squeeze(1) + eps).clamp(0.0, 1.0)
        t_minus = (t_col.squeeze(1) - eps).clamp(0.0, 1.0)
        dt = (t_plus - t_minus).clamp(min=1e-12)
        vp = self.evaluate(t_plus, x)
        vm = self.evaluate(t_minus, x)
        return (vp - vm) / dt.unsqueeze(1)

    def sample_marginal(
        self,
        t_scalar: float | Tensor,
        n: int,
        generator: torch.Generator | None = None,
    ) -> Tensor:
        """Sample from the exact time-``t`` marginal GMM."""
        return self.marginal_mixture(t_scalar).sample(n, generator=generator)


def build_standard_source(
    dim: int,
    dtype: torch.dtype = DEFAULT_DTYPE,
    device: torch.device | None = None,
) -> Gaussian:
    """Convenience wrapper for the standard source."""
    return standard_gaussian(dim, dtype=dtype, device=device)
