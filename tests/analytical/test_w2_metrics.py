"""Tests for Gaussian W2 and affine regularity metrics."""

from __future__ import annotations

import pytest
import torch

from fewstep_regularities.distributions.gaussian import (
    anisotropic_gaussian,
    standard_gaussian,
)
from fewstep_regularities.evaluation.gaussian_w2 import GaussianW2Evaluator, gaussian_w2
from fewstep_regularities.fields.gaussian_affine import GaussianAffineField
from fewstep_regularities.metrics.affine_gaussian import (
    AveragedSquaredLipschitzProxy,
    MaxSampledSpectralJacobianNorm,
)
from fewstep_regularities.paths.linear import LinearPath


@pytest.mark.analytical
def test_identical_gaussians_w2_zero() -> None:
    g = standard_gaussian(4)
    w2 = gaussian_w2(g.mean(), g.covariance(), g.mean(), g.covariance())
    assert w2.item() == pytest.approx(0.0, abs=1e-12)


@pytest.mark.analytical
def test_1d_gaussian_w2() -> None:
    # W2 between N(0,1) and N(2,4) is sqrt(4 + (1-2)^2) = sqrt(5) for 1D:
    # Bures^2 = (sqrt(s1)-sqrt(s0))^2 for 1D.
    m0 = torch.tensor([0.0], dtype=torch.float64)
    m1 = torch.tensor([2.0], dtype=torch.float64)
    s0 = torch.tensor([[1.0]], dtype=torch.float64)
    s1 = torch.tensor([[4.0]], dtype=torch.float64)
    w2 = gaussian_w2(m0, s0, m1, s1)
    expected = (4.0 + (1.0 - 2.0) ** 2) ** 0.5  # mean^2 + (1-2)^2 = 4+1=5
    assert w2.item() == pytest.approx(expected, rel=1e-10)


@pytest.mark.analytical
def test_evaluator_analytical() -> None:
    src = standard_gaussian(3)
    tgt = anisotropic_gaussian(3, anisotropy=4.0)
    ev = GaussianW2Evaluator()
    result = ev.compute(
        {"mean": src.mean(), "covariance": src.covariance()},
        {"mean": tgt.mean(), "covariance": tgt.covariance()},
    )
    assert result.metadata["is_exact"] is True
    assert result.primary.item() > 0


@pytest.mark.analytical
def test_avg_lip_positive() -> None:
    src = standard_gaussian(4)
    tgt = anisotropic_gaussian(4, anisotropy=9.0)
    field = GaussianAffineField(source=src, target=tgt, schedule=LinearPath())
    metric = AveragedSquaredLipschitzProxy(n_time=32)
    result = metric.compute(field)
    assert result.is_exact is False
    assert result.value.item() > 0


@pytest.mark.analytical
def test_max_jacobian_finite() -> None:
    src = standard_gaussian(2)
    tgt = anisotropic_gaussian(2, anisotropy=4.0)
    field = GaussianAffineField(source=src, target=tgt, schedule=LinearPath())
    result = MaxSampledSpectralJacobianNorm(n_time=16).compute(field)
    assert torch.isfinite(result.value)
