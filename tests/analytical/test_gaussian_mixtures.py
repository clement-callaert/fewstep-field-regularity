"""Analytical tests for Gaussian mixtures."""

from __future__ import annotations

import pytest
import torch

from fewstep_regularities.distributions.gaussian_mixture import (
    GaussianMixture,
    eight_mode_gmm,
    imbalanced_gmm,
    two_mode_gmm,
)


@pytest.mark.analytical
def test_weights_normalized() -> None:
    m = two_mode_gmm(4)
    assert abs(float(m.weights.sum().item()) - 1.0) < 1e-12
    imb = imbalanced_gmm(4, weight_ratio=9.0)
    assert abs(float(imb.weights.sum().item()) - 1.0) < 1e-12
    assert abs(float(imb.weights[0] / imb.weights[1]) - 9.0) < 1e-10


@pytest.mark.analytical
def test_analytical_moments_two_mode() -> None:
    m = two_mode_gmm(3, separation=2.0, component_std=0.5)
    mean = m.mean()
    assert torch.allclose(mean, torch.zeros(3, dtype=torch.float64), atol=1e-12)
    # Var along axis 0: E[x^2] = 0.5*((-2)^2+2^2) + 0.25 = 4 + 0.25
    cov = m.covariance()
    assert cov[0, 0].item() == pytest.approx(4.25, rel=1e-10)
    assert cov[1, 1].item() == pytest.approx(0.25, rel=1e-10)


@pytest.mark.analytical
def test_score_matches_autograd() -> None:
    m = two_mode_gmm(5, separation=1.5)
    x = m.sample(32, generator=torch.Generator().manual_seed(0))
    x = x.detach().requires_grad_(True)
    logp = m.log_prob(x)
    grad = torch.autograd.grad(logp.sum(), x)[0]
    score = m.score(x.detach())
    assert torch.allclose(score, grad, rtol=1e-7, atol=1e-7)


@pytest.mark.analytical
def test_log_prob_and_responsibilities_match_definition() -> None:
    mixture = imbalanced_gmm(3, weight_ratio=7.0)
    x = torch.randn(11, 3, dtype=torch.float64)
    log_joint = mixture.component_log_probs(x) + torch.log(mixture.weights)
    expected_log_prob = torch.logsumexp(log_joint, dim=1)
    expected_responsibilities = torch.exp(log_joint - expected_log_prob.unsqueeze(1))
    assert torch.allclose(mixture.log_prob(x), expected_log_prob)
    assert torch.allclose(
        mixture.responsibilities(x), expected_responsibilities, rtol=1e-12, atol=1e-12
    )
    assert torch.allclose(
        mixture.responsibilities(x).sum(dim=1),
        torch.ones(x.shape[0], dtype=torch.float64),
    )


@pytest.mark.analytical
def test_constructor_rejects_silent_dtype_cast() -> None:
    with pytest.raises(TypeError, match="dtype"):
        GaussianMixture(
            weights=torch.tensor([0.5, 0.5], dtype=torch.float32),
            means=torch.zeros(2, 1, dtype=torch.float32),
            covs=torch.ones(2, 1, 1, dtype=torch.float32),
        )


@pytest.mark.analytical
def test_score_finite_low_density() -> None:
    m = eight_mode_gmm(2)
    x = torch.tensor([[20.0, 20.0]], dtype=torch.float64)
    s = m.score(x)
    assert torch.isfinite(s).all()
    assert torch.isfinite(m.log_prob(x)).all()


@pytest.mark.analytical
def test_sampling_moments() -> None:
    m = two_mode_gmm(2, separation=1.0, component_std=0.4)
    gen = torch.Generator().manual_seed(1)
    x = m.sample(80_000, generator=gen)
    emp_mean = x.mean(dim=0)
    emp_cov = torch.cov(x.T)
    assert torch.allclose(emp_mean, m.mean(), atol=0.05)
    assert torch.allclose(emp_cov, m.covariance(), atol=0.08)


@pytest.mark.analytical
def test_eight_mode_dims() -> None:
    for d in (2, 8):
        m = eight_mode_gmm(d)
        assert m.n_components == 8
        assert m.dim == d
        assert abs(float(m.weights.sum().item()) - 1.0) < 1e-12
