"""Tests for affine map and Gaussian moment propagation."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
import torch
from torch import Tensor

from fewstep_regularities.analysis.propagation import (
    propagate_gaussian_moments,
    recover_affine_solver_map,
)
from fewstep_regularities.solvers.euler import EulerSolver


@dataclass(frozen=True)
class ConstantAffineField:
    """Constant affine field used for one-step map checks."""

    matrix: Tensor
    offset: Tensor

    def evaluate(self, t: Tensor, x: Tensor) -> Tensor:
        del t
        return x @ self.matrix.T + self.offset

    def jacobian(self, t: Tensor, x: Tensor) -> Tensor:
        del t
        return self.matrix.unsqueeze(0).expand(x.shape[0], -1, -1).contiguous()

    def time_derivative(self, t: Tensor, x: Tensor) -> Tensor | None:
        del t, x
        return None


@pytest.mark.analytical
def test_recover_one_step_euler_affine_map() -> None:
    matrix = torch.tensor([[0.5, 0.0], [0.0, -0.25]], dtype=torch.float64)
    offset = torch.tensor([1.0, -2.0], dtype=torch.float64)
    recovered = recover_affine_solver_map(
        ConstantAffineField(matrix, offset),
        EulerSolver(),
        dim=2,
        dtype=torch.float64,
        device=torch.device("cpu"),
        requested_nfe=1,
    )
    assert torch.allclose(
        recovered.matrix,
        torch.eye(2, dtype=torch.float64) + matrix,
    )
    assert torch.allclose(recovered.offset, offset)
    assert recovered.actual_nfe == 1
    assert recovered.n_steps == 1


@pytest.mark.analytical
def test_propagate_gaussian_moments() -> None:
    matrix = torch.tensor([[2.0, 0.0], [0.0, 0.5]], dtype=torch.float64)
    offset = torch.tensor([1.0, -1.0], dtype=torch.float64)
    recovered = recover_affine_solver_map(
        ConstantAffineField(matrix - torch.eye(2, dtype=torch.float64), offset),
        EulerSolver(),
        dim=2,
        dtype=torch.float64,
        device=torch.device("cpu"),
        requested_nfe=1,
    )
    mean = torch.tensor([2.0, 4.0], dtype=torch.float64)
    covariance = torch.tensor([[3.0, 1.0], [1.0, 2.0]], dtype=torch.float64)
    out_mean, out_covariance = propagate_gaussian_moments(
        recovered,
        mean,
        covariance,
    )
    assert torch.allclose(out_mean, matrix @ mean + offset)
    assert torch.allclose(out_covariance, matrix @ covariance @ matrix.T)
    assert torch.allclose(out_covariance, out_covariance.T)
