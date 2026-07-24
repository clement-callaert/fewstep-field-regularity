"""Analytical tests for mixture affine fields."""

from __future__ import annotations

import pytest
import torch

from fewstep_regularities.distributions.gaussian import standard_gaussian
from fewstep_regularities.distributions.gaussian_mixture import (
    GaussianMixture,
    eight_mode_gmm,
    imbalanced_gmm,
    two_mode_gmm,
)
from fewstep_regularities.fields.mixture_affine import MixtureAffineField
from fewstep_regularities.paths.linear import LinearPath
from fewstep_regularities.paths.lipschitz_guided import LipschitzGuidedPath
from fewstep_regularities.paths.variance_preserving import VariancePreservingTrigPath


@pytest.mark.analytical
def test_marginal_is_gmm_at_endpoints() -> None:
    source = standard_gaussian(2)
    target = two_mode_gmm(2)
    field = MixtureAffineField(source=source, target=target, schedule=LinearPath())
    m0 = field.marginal_mixture(0.0)
    assert torch.allclose(m0.means, torch.zeros_like(m0.means), atol=1e-12)
    m1 = field.marginal_mixture(1.0)
    assert torch.allclose(m1.means, target.means)
    assert torch.allclose(m1.covs, target.covs)


@pytest.mark.analytical
def test_jacobian_matches_autograd() -> None:
    source = standard_gaussian(2)
    target = two_mode_gmm(2, separation=1.5)
    field = MixtureAffineField(source=source, target=target, schedule=LinearPath())
    t = torch.tensor(0.4, dtype=torch.float64)
    x = field.sample_marginal(t, 8, generator=torch.Generator().manual_seed(0))
    x = x.detach().requires_grad_(True)

    # Per-row Jacobian via autograd.
    jac_ad = []
    for i in range(x.shape[0]):
        xi = x[i : i + 1].detach().requires_grad_(True)
        vi = field.evaluate(t, xi)[0]
        rows = []
        for j in range(2):
            g = torch.autograd.grad(vi[j], xi, retain_graph=True)[0][0]
            rows.append(g)
        jac_ad.append(torch.stack(rows, dim=0))
    jac_ad_t = torch.stack(jac_ad, dim=0)
    jac = field.jacobian(t, x.detach())
    assert torch.allclose(jac, jac_ad_t, rtol=1e-6, atol=1e-6)


def _full_covariance_gmm() -> GaussianMixture:
    weights = torch.tensor([0.3, 0.7], dtype=torch.float64)
    means = torch.tensor([[-1.0, 0.5], [1.5, -0.25]], dtype=torch.float64)
    covs = torch.tensor(
        [[[1.2, 0.35], [0.35, 0.8]], [[0.7, -0.2], [-0.2, 1.4]]],
        dtype=torch.float64,
    )
    return GaussianMixture(weights=weights, means=means, covs=covs)


@pytest.mark.analytical
@pytest.mark.parametrize(
    "schedule",
    [LinearPath(), VariancePreservingTrigPath(), LipschitzGuidedPath(m=4.0)],
)
def test_full_covariance_jacobian_matches_autograd(
    schedule: LinearPath | VariancePreservingTrigPath | LipschitzGuidedPath,
) -> None:
    field = MixtureAffineField(
        source=standard_gaussian(2),
        target=_full_covariance_gmm(),
        schedule=schedule,
    )
    t = torch.tensor(0.37, dtype=torch.float64)
    x = torch.tensor([[-1.1, 0.2], [0.0, -0.7], [1.3, 0.9]], dtype=torch.float64)

    jac_ad = torch.stack(
        [
            torch.func.jacrev(lambda point: field.evaluate(t, point[None])[0])(point)
            for point in x
        ]
    )
    assert torch.allclose(field.jacobian(t, x), jac_ad, rtol=2e-10, atol=2e-10)


@pytest.mark.analytical
@pytest.mark.parametrize(
    "target",
    [
        two_mode_gmm(2),
        eight_mode_gmm(2),
        imbalanced_gmm(2),
        _full_covariance_gmm(),
    ],
)
@pytest.mark.parametrize(
    "schedule",
    [LinearPath(), VariancePreservingTrigPath(), LipschitzGuidedPath(m=4.0)],
)
@pytest.mark.parametrize("time", [0.19, 0.53, 0.81])
def test_pointwise_continuity_equation(
    target: GaussianMixture,
    schedule: LinearPath | VariancePreservingTrigPath | LipschitzGuidedPath,
    time: float,
) -> None:
    """Check ∂t log p + div(b) + b·∇log p = 0 at fixed points."""
    field = MixtureAffineField(
        source=standard_gaussian(2),
        target=target,
        schedule=schedule,
    )
    points = torch.tensor(
        [[-2.1, 0.4], [-0.3, -1.2], [0.8, 0.1], [2.4, 1.7]],
        dtype=torch.float64,
    )

    for point in points:
        t = torch.tensor(time, dtype=torch.float64, requires_grad=True)
        x = point.detach().requires_grad_(True)
        log_p = field.marginal_mixture(t).log_prob(x[None])[0]
        dt_log_p = torch.autograd.grad(log_p, t, create_graph=True)[0]
        velocity = field.evaluate(t, x[None])[0]
        divergence = sum(
            torch.autograd.grad(velocity[j], x, retain_graph=True, create_graph=True)[
                0
            ][j]
            for j in range(field.dim)
        )
        score = torch.autograd.grad(log_p, x, retain_graph=True)[0]
        residual = dt_log_p + divergence + torch.dot(velocity, score)
        assert residual.item() == pytest.approx(0.0, abs=2e-9)


@pytest.mark.analytical
def test_moment_evolution_mc() -> None:
    """MC mean of velocity matches derivative of marginal mean."""
    source = standard_gaussian(2)
    target = two_mode_gmm(2, separation=2.0)
    field = MixtureAffineField(source=source, target=target, schedule=LinearPath())
    t = 0.3
    marg = field.marginal_mixture(t)
    # Analytical mean velocity of marginal mean: d/dt (sigma(t) m_1) = sigma' m_1
    # for zero-mean source; target mean is 0 for equal two-mode, so mean stays 0.
    assert torch.allclose(marg.mean(), torch.zeros(2, dtype=torch.float64), atol=1e-12)
    gen = torch.Generator().manual_seed(2)
    x = field.sample_marginal(t, 20_000, generator=gen)
    v = field.evaluate(torch.tensor(t, dtype=torch.float64), x)
    assert torch.allclose(v.mean(0), torch.zeros(2, dtype=torch.float64), atol=0.05)


@pytest.mark.analytical
def test_rejects_gaussian_ot_factory() -> None:
    from fewstep_regularities.experiments.factories import build_field, build_path

    source = standard_gaussian(2)
    target = two_mode_gmm(2)
    with pytest.raises(ValueError, match="gaussian_ot"):
        build_path({"name": "gaussian_ot"}, source, target, torch.float64)
    path = build_path({"name": "linear"}, source, target, torch.float64)
    with pytest.raises(ValueError, match="mixture"):
        build_field({"name": "gaussian_ot"}, source, target, path, torch.float64)


@pytest.mark.analytical
@pytest.mark.parametrize(
    "metric_name",
    [
        "averaged_squared_lipschitz_proxy",
        "max_sampled_spectral_jacobian_norm",
        "path_weighted_expected_jacobian_norm",
        "expected_squared_jacobian_norm",
        "temporal_field_derivative_norm",
        "jacobian_temporal_variation",
        "lagrangian_acceleration",
        "spatial_temporal_stiffness",
    ],
)
def test_all_registered_metrics_dispatch_for_mixture(metric_name: str) -> None:
    from fewstep_regularities.experiments.factories import build_metric
    from fewstep_regularities.metrics.mixture_mc import dispatch_metric_compute

    source = standard_gaussian(2)
    target = two_mode_gmm(2)
    field = MixtureAffineField(source=source, target=target, schedule=LinearPath())
    metric = build_metric({"name": metric_name, "n_time": 3}, torch.float64)
    result = dispatch_metric_compute(metric, field)
    assert torch.isfinite(result.value)
    assert result.is_exact is False
