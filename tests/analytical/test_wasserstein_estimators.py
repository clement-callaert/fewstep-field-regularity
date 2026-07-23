"""Tests for empirical Wasserstein estimators."""

from __future__ import annotations

import pytest
import torch

from fewstep_regularities.distributions.gaussian import (
    anisotropic_gaussian,
    standard_gaussian,
)
from fewstep_regularities.evaluation.gaussian_w2 import gaussian_w2
from fewstep_regularities.evaluation.projected_sliced import (
    DiscreteOTEvaluator,
    EntropicOTEvaluator,
    ProjectedW2Evaluator,
    SlicedWassersteinEvaluator,
    projected_w2_squared_1d,
)


@pytest.mark.analytical
def test_1d_w2_identity() -> None:
    u = torch.tensor([0.0, 1.0, 2.0], dtype=torch.float64)
    assert projected_w2_squared_1d(u, u).item() == pytest.approx(0.0)


@pytest.mark.analytical
def test_1d_w2_unequal_empirical_sizes() -> None:
    u = torch.tensor([0.0, 10.0], dtype=torch.float64)
    v = torch.tensor([0.0, 0.0, 10.0], dtype=torch.float64)
    assert projected_w2_squared_1d(u, v).item() == pytest.approx(100.0 / 6.0)


@pytest.mark.analytical
def test_sliced_one_projection_matches_projected() -> None:
    gen = torch.Generator().manual_seed(0)
    x = torch.randn(50, 3, dtype=torch.float64, generator=gen)
    y = torch.randn(50, 3, dtype=torch.float64, generator=gen)
    sw = SlicedWassersteinEvaluator(
        n_projections=1, dtype=torch.float64, seed=0
    ).compute(x, y)
    pr = ProjectedW2Evaluator(n_projections=1, dtype=torch.float64, seed=0).compute(
        x, y
    )
    assert torch.allclose(sw.primary, pr.primary, rtol=1e-10, atol=1e-10)


@pytest.mark.analytical
def test_discrete_ot_identical_zero() -> None:
    x = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]], dtype=torch.float64)
    out = DiscreteOTEvaluator(max_points=8, dtype=torch.float64).compute(x, x)
    assert float(out.primary.item()) == pytest.approx(0.0, abs=1e-8)


@pytest.mark.analytical
def test_discrete_ot_nonzero_empirical_case_and_scope() -> None:
    x = torch.tensor([[0.0], [2.0]], dtype=torch.float64)
    y = torch.tensor([[1.0], [3.0]], dtype=torch.float64)
    evaluator = DiscreteOTEvaluator(max_points=4, dtype=torch.float64)
    out = evaluator.compute(x, y)
    assert float(out.primary.item()) == pytest.approx(1.0)
    assert evaluator.metadata()["is_exact_w2"] is False
    assert evaluator.metadata()["is_exact_empirical_w2"] is True


@pytest.mark.analytical
def test_entropic_not_labeled_exact() -> None:
    generator = torch.Generator().manual_seed(11)
    x = torch.randn(16, 2, dtype=torch.float64, generator=generator)
    y = torch.randn(16, 2, dtype=torch.float64, generator=generator)
    ev = EntropicOTEvaluator(epsilon=0.1, dtype=torch.float64)
    assert ev.metadata()["is_exact_w2"] is False
    out = ev.compute(x, y)
    assert torch.isfinite(out.primary)
    assert out.metadata["epsilon"] == 0.1
    assert out.metadata["converged"] is True
    assert out.metadata["primary_quantity"] == "sqrt_transport_component"
    assert out.auxiliaries["row_marginal_residual"].item() <= ev.tol
    assert out.auxiliaries["column_marginal_residual"].item() <= ev.tol
    expected_objective = out.auxiliaries["transport_cost"] - (
        ev.epsilon * out.auxiliaries["entropy"]
    )
    assert torch.allclose(
        out.auxiliaries["regularized_objective"], expected_objective
    )


@pytest.mark.analytical
def test_entropic_refuses_nonconverged_plan() -> None:
    generator = torch.Generator().manual_seed(5)
    x = torch.randn(16, 2, dtype=torch.float64, generator=generator)
    y = 2.0 + torch.randn(16, 2, dtype=torch.float64, generator=generator)
    evaluator = EntropicOTEvaluator(
        epsilon=0.01, max_iter=1, tol=1e-12, dtype=torch.float64
    )
    with pytest.raises(RuntimeError, match="did not converge"):
        evaluator.compute(x, y)


@pytest.mark.analytical
def test_sliced_near_exact_gaussian_large_n() -> None:
    source = standard_gaussian(2)
    target = anisotropic_gaussian(2, anisotropy=4.0)
    exact = gaussian_w2(
        source.mean(), source.covariance(), target.mean(), target.covariance()
    )
    gen = torch.Generator().manual_seed(3)
    x = source.sample(2000, generator=gen)
    y = target.sample(2000, generator=gen)
    sw = SlicedWassersteinEvaluator(
        n_projections=256, dtype=torch.float64, seed=3
    ).compute(x, y)
    # Loose tolerance: sliced is not Bures W2.
    assert abs(float(sw.primary.item()) - float(exact.item())) < 1.0


@pytest.mark.analytical
def test_dtype_hard_fail() -> None:
    x = torch.randn(8, 2, dtype=torch.float32)
    y = torch.randn(8, 2, dtype=torch.float32)
    with pytest.raises(TypeError):
        SlicedWassersteinEvaluator(dtype=torch.float64).compute(x, y)
