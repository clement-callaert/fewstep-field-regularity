"""Analytical tests for exact Gaussian velocity fields."""

from __future__ import annotations

import pytest
import torch

from fewstep_regularities.distributions.gaussian import (
    anisotropic_gaussian,
    standard_gaussian,
)
from fewstep_regularities.fields.conditional import LipmanConditionalOTField
from fewstep_regularities.fields.gaussian_affine import GaussianAffineField
from fewstep_regularities.fields.gaussian_ot_field import GaussianOTField
from fewstep_regularities.paths.gaussian_ot import GaussianOTPath
from fewstep_regularities.paths.linear import LinearPath
from fewstep_regularities.paths.variance_preserving import VariancePreservingTrigPath


@pytest.mark.analytical
def test_affine_jacobian_matches_ad() -> None:
    src = standard_gaussian(4)
    tgt = anisotropic_gaussian(4, anisotropy=4.0)
    field = GaussianAffineField(source=src, target=tgt, schedule=LinearPath())
    t = torch.tensor(0.4, dtype=torch.float64)
    x = src.sample(8, generator=torch.Generator().manual_seed(0))
    x = x.detach().requires_grad_(True)

    def f(xx: torch.Tensor) -> torch.Tensor:
        return field.evaluate(t, xx)

    # Build Jacobian via autograd for first sample.
    j_ad = torch.autograd.functional.jacobian(
        lambda z: f(z.unsqueeze(0)).squeeze(0), x[0].detach()
    )
    j = field.jacobian(t, x.detach())[0]
    assert torch.allclose(j, j_ad, rtol=1e-8, atol=1e-8)


@pytest.mark.analytical
def test_affine_moment_ode_linear() -> None:
    """Mean ODE: ṁ = E[b_t(I_t)] must match schedule mean derivative."""
    src = standard_gaussian(3)
    tgt = anisotropic_gaussian(3, anisotropy=3.0)
    # Shift target mean to make ṁ nontrivial.
    tgt = type(tgt)(
        mean_vec=torch.tensor([1.0, -2.0, 0.5], dtype=torch.float64),
        cov=tgt.covariance(),
        _dtype=torch.float64,
        _device=torch.device("cpu"),
    )
    path = LinearPath()
    field = GaussianAffineField(source=src, target=tgt, schedule=path)
    t = 0.35
    m_dot = field.mean_velocity(t)
    expected = (
        path.alpha_derivative(torch.tensor(t, dtype=torch.float64)) * src.mean()
        + path.sigma_derivative(torch.tensor(t, dtype=torch.float64)) * tgt.mean()
    )
    assert torch.allclose(m_dot, expected)


@pytest.mark.analytical
def test_affine_mc_velocity_matches() -> None:
    src = standard_gaussian(2)
    tgt = anisotropic_gaussian(2, anisotropy=4.0)
    path = VariancePreservingTrigPath()
    field = GaussianAffineField(source=src, target=tgt, schedule=path)
    t = 0.4
    gen0 = torch.Generator().manual_seed(0)
    gen1 = torch.Generator().manual_seed(1)
    z = src.sample(100_000, generator=gen0)
    x1 = tgt.sample(100_000, generator=gen1)
    tt = torch.full((100_000,), t, dtype=torch.float64)
    xt = path.marginal_sample(tt, z, x1)
    # Conditional velocity averaged should match marginal field at samples.
    v_cond = path.conditional_velocity(tt, xt, z, x1)
    v_field = field.evaluate(torch.tensor(t, dtype=torch.float64), xt)
    # Compare means of velocities (Monte Carlo consistency).
    assert torch.allclose(v_cond.mean(0), v_field.mean(0), atol=0.05)


@pytest.mark.analytical
def test_ot_field_matches_ray_velocity() -> None:
    src = standard_gaussian(3)
    tgt = anisotropic_gaussian(3, anisotropy=5.0)
    path = GaussianOTPath(source=src, target=tgt)
    field = GaussianOTField(source=src, target=tgt)
    x0 = src.sample(32, generator=torch.Generator().manual_seed(4))
    t = 0.3
    xt = path.marginal_sample(
        torch.full((32,), t, dtype=torch.float64),
        x0,
        torch.zeros_like(x0),
    )
    v_ray = path.conditional_velocity(
        torch.full((32,), t, dtype=torch.float64),
        xt,
        x0,
        torch.zeros_like(x0),
    )
    v_field = field.evaluate(torch.tensor(t, dtype=torch.float64), xt)
    assert torch.allclose(v_ray, v_field, rtol=1e-6, atol=1e-6)


@pytest.mark.analytical
def test_lipman_conditional_formula() -> None:
    field = LipmanConditionalOTField(sigma_min=1e-3)
    t = torch.tensor(0.5, dtype=torch.float64)
    x = torch.randn(5, 2, dtype=torch.float64)
    x1 = torch.randn(5, 2, dtype=torch.float64)
    u = field.evaluate_conditional(t, x, x1)
    denom = 1.0 - (1.0 - 1e-3) * 0.5
    expected = (x1 - (1.0 - 1e-3) * x) / denom
    assert torch.allclose(u, expected)
