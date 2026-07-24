"""Analytical tests for the frozen workshop external-validation family."""

from __future__ import annotations

import math

import pytest
import torch

from fewstep_regularities.analysis.precision import (
    high_precision_noncentered_gaussian_w2,
    high_precision_noncentered_mode,
)
from fewstep_regularities.analysis.propagation import (
    propagate_gaussian_moments,
    recover_affine_solver_map,
)
from fewstep_regularities.evaluation.gaussian_w2 import GaussianW2Evaluator
from fewstep_regularities.experiments.factories import build_path, build_solver
from fewstep_regularities.experiments.workshop_external_validation import (
    build_family,
    frozen_source_mean,
    frozen_target_eigenvalues,
    frozen_target_mean,
)
from fewstep_regularities.fields.gaussian_affine import GaussianAffineField

DTYPE = torch.float64
DEVICE = torch.device("cpu")


@pytest.mark.analytical
@pytest.mark.parametrize("dim", [2, 8])
def test_frozen_family_matches_plan(dim: int) -> None:
    source, target = build_family(dim, DTYPE, DEVICE)
    expected_source = [0.75 * ((-1.0) ** i) for i in range(dim)]
    expected_target = [1.0 + 0.25 * i for i in range(dim)]
    assert source.mean().tolist() == pytest.approx(expected_source, abs=0.0)
    assert target.mean().tolist() == pytest.approx(expected_target, abs=0.0)
    assert torch.equal(source.covariance(), torch.eye(dim, dtype=DTYPE))
    eigenvalues = frozen_target_eigenvalues(dim, DTYPE, DEVICE)
    assert float(eigenvalues.min()) == pytest.approx(6.0 ** (-0.5), rel=1e-14)
    assert float(eigenvalues.max()) == pytest.approx(6.0**0.5, rel=1e-14)
    ratio = float(eigenvalues.max() / eigenvalues.min())
    assert ratio == pytest.approx(6.0, rel=1e-12)


@pytest.mark.analytical
@pytest.mark.parametrize("path_name", ["linear", "variance_preserving"])
def test_drift_offset_is_nonzero(path_name: str) -> None:
    source, target = build_family(2, DTYPE, DEVICE)
    path = build_path({"name": path_name}, source, target, DTYPE)
    field = GaussianAffineField(
        source=source, target=target, schedule=path, dtype=DTYPE
    )
    t = torch.tensor(0.5, dtype=DTYPE)
    offset = field.mean_velocity(t) - field.jacobian_matrix(t) @ field.mean_t(t)
    assert float(torch.linalg.vector_norm(offset)) > 1e-3


@pytest.mark.analytical
@pytest.mark.parametrize("path_name", ["linear", "variance_preserving"])
@pytest.mark.parametrize("solver_name", ["euler", "heun", "rk4"])
def test_noncentered_precision_matches_float64(
    path_name: str, solver_name: str
) -> None:
    dim = 2
    nfe = 8
    source, target = build_family(dim, DTYPE, DEVICE)
    path = build_path({"name": path_name}, source, target, DTYPE)
    field = GaussianAffineField(
        source=source, target=target, schedule=path, dtype=DTYPE
    )
    solver = build_solver({"name": solver_name})
    affine_map = recover_affine_solver_map(
        field, solver, dim=dim, dtype=DTYPE, device=DEVICE, requested_nfe=nfe
    )
    mean, covariance = propagate_gaussian_moments(
        affine_map, source.mean(), source.covariance()
    )
    evaluator = GaussianW2Evaluator(dtype=DTYPE)
    w2 = float(
        evaluator.compute(
            {"mean": mean, "covariance": covariance},
            {"mean": target.mean(), "covariance": target.covariance()},
        ).primary
    )
    eigenvalues = [float(v) for v in frozen_target_eigenvalues(dim, DTYPE, DEVICE)]
    mp_w2 = high_precision_noncentered_gaussian_w2(
        path_name,
        solver_name,
        eigenvalues,
        [float(v) for v in frozen_source_mean(dim, DTYPE, DEVICE)],
        [float(v) for v in frozen_target_mean(dim, DTYPE, DEVICE)],
        nfe,
        decimal_digits=80,
    )
    assert w2 == pytest.approx(float(mp_w2), abs=2e-9)


@pytest.mark.analytical
def test_noncentered_mode_reduces_to_centered_case() -> None:
    factor, offset = high_precision_noncentered_mode(
        "linear", "euler", 2.5, 0.0, 0.0, 8, decimal_digits=60
    )
    assert float(offset) == pytest.approx(0.0, abs=0.0)
    # With zero means the modal factor must match the centered helper.
    from fewstep_regularities.analysis.precision import high_precision_mode_factor

    centered = high_precision_mode_factor("linear", "euler", 2.5, 8, decimal_digits=60)
    assert float(factor) == pytest.approx(float(centered), rel=1e-30, abs=1e-30)


@pytest.mark.analytical
def test_exact_continuous_endpoint_reaches_target() -> None:
    dim = 8
    source, target = build_family(dim, DTYPE, DEVICE)
    for path_name in ("linear", "variance_preserving"):
        path = build_path({"name": path_name}, source, target, DTYPE)
        field = GaussianAffineField(
            source=source, target=target, schedule=path, dtype=DTYPE
        )
        t1 = torch.tensor(1.0, dtype=DTYPE)
        mean_gap = float(torch.linalg.vector_norm(field.mean_t(t1) - target.mean()))
        cov_gap = float(torch.linalg.matrix_norm(field.cov_t(t1) - target.covariance()))
        assert mean_gap <= 1e-12
        assert cov_gap <= 1e-12


@pytest.mark.analytical
def test_modal_w2_matches_bures_for_diagonal_case() -> None:
    dim = 2
    _, target = build_family(dim, DTYPE, DEVICE)
    evaluator = GaussianW2Evaluator(dtype=DTYPE)
    factors = torch.tensor([0.9, 1.4], dtype=DTYPE)
    mean = torch.tensor([1.1, 0.7], dtype=DTYPE)
    covariance = torch.diag(factors**2)
    w2 = float(
        evaluator.compute(
            {"mean": mean, "covariance": covariance},
            {"mean": target.mean(), "covariance": target.covariance()},
        ).primary
    )
    eigenvalues = frozen_target_eigenvalues(dim, DTYPE, DEVICE)
    modal = math.sqrt(
        float(torch.sum((mean - target.mean()) ** 2))
        + float(torch.sum((factors.abs() - eigenvalues.sqrt()) ** 2))
    )
    assert w2 == pytest.approx(modal, abs=1e-12)
