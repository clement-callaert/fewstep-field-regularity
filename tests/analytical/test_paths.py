"""Analytical tests for probability paths."""

from __future__ import annotations

import pytest
import torch

from fewstep_regularities.distributions.gaussian import (
    anisotropic_gaussian,
    standard_gaussian,
)
from fewstep_regularities.paths.gaussian_ot import GaussianOTPath, gaussian_ot_map
from fewstep_regularities.paths.linear import LinearPath
from fewstep_regularities.paths.lipschitz_guided import LipschitzGuidedPath
from fewstep_regularities.paths.variance_preserving import VariancePreservingTrigPath


@pytest.mark.analytical
def test_linear_endpoints() -> None:
    path = LinearPath()
    t0 = torch.tensor(0.0, dtype=torch.float64)
    t1 = torch.tensor(1.0, dtype=torch.float64)
    assert path.alpha(t0).item() == pytest.approx(1.0)
    assert path.sigma(t0).item() == pytest.approx(0.0)
    assert path.alpha(t1).item() == pytest.approx(0.0)
    assert path.sigma(t1).item() == pytest.approx(1.0)


@pytest.mark.analytical
def test_trig_vp_identity() -> None:
    path = VariancePreservingTrigPath()
    t = torch.linspace(0, 1, 21, dtype=torch.float64)
    a = path.alpha(t)
    s = path.sigma(t)
    assert torch.allclose(a * a + s * s, torch.ones_like(t), atol=1e-12)


@pytest.mark.analytical
def test_schedule_derivatives_fd() -> None:
    path = VariancePreservingTrigPath()
    t = torch.tensor([0.3, 0.7], dtype=torch.float64)
    eps = 1e-6
    a_fd = (path.alpha(t + eps) - path.alpha(t - eps)) / (2 * eps)
    s_fd = (path.sigma(t + eps) - path.sigma(t - eps)) / (2 * eps)
    assert torch.allclose(path.alpha_derivative(t), a_fd, rtol=1e-6, atol=1e-8)
    assert torch.allclose(path.sigma_derivative(t), s_fd, rtol=1e-6, atol=1e-8)


@pytest.mark.analytical
def test_lipschitz_guided_endpoints_and_fd() -> None:
    path = LipschitzGuidedPath(m=4.0)
    t0 = torch.tensor(0.0, dtype=torch.float64)
    t1 = torch.tensor(1.0, dtype=torch.float64)
    assert path.alpha(t0).item() == pytest.approx(1.0, abs=1e-10)
    assert path.sigma(t0).item() == pytest.approx(0.0, abs=1e-10)
    assert path.alpha(t1).item() == pytest.approx(0.0, abs=1e-10)
    assert path.sigma(t1).item() == pytest.approx(1.0, abs=1e-10)
    t = torch.tensor([0.25, 0.5, 0.75], dtype=torch.float64)
    eps = 1e-7
    a_fd = (path.alpha(t + eps) - path.alpha(t - eps)) / (2 * eps)
    assert torch.allclose(path.alpha_derivative(t), a_fd, rtol=1e-5, atol=1e-6)


@pytest.mark.analytical
def test_gaussian_covariance_evolution_linear() -> None:
    path = LinearPath()
    src = standard_gaussian(4)
    tgt = anisotropic_gaussian(4, anisotropy=4.0)
    t = 0.3
    a = path.alpha(torch.tensor(t, dtype=torch.float64)).item()
    s = path.sigma(torch.tensor(t, dtype=torch.float64)).item()
    cov_t = (a**2) * src.covariance() + (s**2) * tgt.covariance()
    # Monte Carlo check
    gen = torch.Generator().manual_seed(0)
    x0 = src.sample(50_000, generator=gen)
    x1 = tgt.sample(50_000, generator=torch.Generator().manual_seed(1))
    tt = torch.full((50_000,), t, dtype=torch.float64)
    xt = path.marginal_sample(tt, x0, x1)
    emp = torch.cov(xt.T)
    assert torch.allclose(emp, cov_t, atol=0.05, rtol=0.05)


@pytest.mark.analytical
def test_gaussian_ot_pushforward_moments() -> None:
    src = standard_gaussian(3)
    tgt = anisotropic_gaussian(3, anisotropy=5.0)
    path = GaussianOTPath(source=src, target=tgt)
    gen = torch.Generator().manual_seed(0)
    x0 = src.sample(80_000, generator=gen)
    x1 = path.transport(x0)
    emp_mean = x1.mean(0)
    emp_cov = torch.cov(x1.T)
    assert torch.allclose(emp_mean, tgt.mean(), atol=0.03)
    assert torch.allclose(emp_cov, tgt.covariance(), atol=0.05, rtol=0.05)


@pytest.mark.analytical
def test_gaussian_ot_map_matches_helper() -> None:
    src = standard_gaussian(2)
    tgt = anisotropic_gaussian(2, anisotropy=3.0)
    x = src.sample(5, generator=torch.Generator().manual_seed(3))
    path = GaussianOTPath(source=src, target=tgt)
    assert torch.allclose(path.transport(x), gaussian_ot_map(x, src, tgt))
