"""Analytical tests for Gaussian distributions."""

from __future__ import annotations

import pytest
import torch

from fewstep_regularities.distributions.gaussian import (
    anisotropic_gaussian,
    low_rank_gaussian,
    standard_gaussian,
)


@pytest.mark.analytical
def test_standard_gaussian_moments() -> None:
    g = standard_gaussian(4)
    assert torch.allclose(g.mean(), torch.zeros(4, dtype=torch.float64))
    assert torch.allclose(g.covariance(), torch.eye(4, dtype=torch.float64))


@pytest.mark.analytical
def test_anisotropic_condition_number() -> None:
    a = 9.0
    g = anisotropic_gaussian(8, anisotropy=a)
    ev = torch.linalg.eigvalsh(g.covariance())
    cond = (ev.max() / ev.min()).item()
    assert abs(cond - a) < 1e-10


@pytest.mark.analytical
def test_score_matches_autograd() -> None:
    g = anisotropic_gaussian(5, anisotropy=4.0)
    x = g.sample(16)
    x = x.detach().requires_grad_(True)
    logp = g.log_prob(x)
    grad = torch.autograd.grad(logp.sum(), x)[0]
    score = g.score(x.detach())
    assert torch.allclose(score, grad, rtol=1e-8, atol=1e-8)


@pytest.mark.analytical
def test_sampling_moments() -> None:
    g = standard_gaussian(3)
    gen = torch.Generator().manual_seed(0)
    x = g.sample(200_000, generator=gen)
    emp_mean = x.mean(dim=0)
    emp_cov = torch.cov(x.T)
    assert torch.allclose(emp_mean, g.mean(), atol=0.02)
    assert torch.allclose(emp_cov, g.covariance(), atol=0.03)


@pytest.mark.analytical
def test_score_finite_far_away() -> None:
    g = low_rank_gaussian(6, rank=2, noise_variance=0.1, generator=torch.Generator().manual_seed(1))
    x = g.mean() + 20.0 * torch.ones(1, 6, dtype=torch.float64)
    s = g.score(x)
    assert torch.isfinite(s).all()


@pytest.mark.analytical
def test_low_rank_positive_definite() -> None:
    g = low_rank_gaussian(8, rank=2, noise_variance=0.05, generator=torch.Generator().manual_seed(2))
    ev = torch.linalg.eigvalsh(g.covariance())
    assert (ev > 0).all()
