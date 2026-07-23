"""Tests for fixed-step ODE solvers."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
import torch
from torch import Tensor

from fewstep_regularities.solvers.euler import EulerSolver
from fewstep_regularities.solvers.heun import HeunSolver
from fewstep_regularities.solvers.rk4 import RK4Solver


@dataclass
class LinearDecayField:
    """``v(t, x) = -x``, solution ``x(t) = x0 exp(-(t-t0))``."""

    def evaluate(self, t: Tensor, x: Tensor) -> Tensor:
        del t
        return -x

    def jacobian(self, t: Tensor, x: Tensor) -> Tensor:
        del t
        n, d = x.shape
        eye = torch.eye(d, dtype=x.dtype, device=x.device)
        return (-eye).unsqueeze(0).expand(n, -1, -1).contiguous()

    def time_derivative(self, t: Tensor, x: Tensor) -> Tensor | None:
        del t, x
        return None


@pytest.mark.analytical
@pytest.mark.parametrize(
    ("solver", "nfe", "evals"),
    [
        (EulerSolver(), 16, 1),
        (HeunSolver(), 16, 2),
        (RK4Solver(), 16, 4),
    ],
)
def test_nfe_accounting(solver: EulerSolver, nfe: int, evals: int) -> None:
    field = LinearDecayField()
    x0 = torch.ones(4, 2, dtype=torch.float64)
    result = solver.solve(field, x0, 0.0, 1.0, requested_nfe=nfe)
    assert result.actual_nfe == nfe
    assert result.n_steps == nfe // evals
    assert result.requested_nfe == nfe


@pytest.mark.analytical
def test_euler_converges_on_linear_ode() -> None:
    field = LinearDecayField()
    x0 = torch.ones(1, 1, dtype=torch.float64)
    exact = torch.exp(torch.tensor(-1.0, dtype=torch.float64))
    errs = []
    for nfe in [8, 16, 32, 64]:
        out = EulerSolver().solve(field, x0, 0.0, 1.0, requested_nfe=nfe)
        errs.append((out.trajectory[-1] - exact).abs().item())
    # Error should decrease as NFE increases.
    assert errs[-1] < errs[0]


@pytest.mark.analytical
def test_rk4_more_accurate_than_euler_equal_nfe() -> None:
    field = LinearDecayField()
    x0 = torch.ones(1, 1, dtype=torch.float64)
    exact = torch.exp(torch.tensor(-1.0, dtype=torch.float64))
    nfe = 64
    e_err = (
        EulerSolver().solve(field, x0, 0.0, 1.0, requested_nfe=nfe).trajectory[-1] - exact
    ).abs().item()
    r_err = (
        RK4Solver().solve(field, x0, 0.0, 1.0, requested_nfe=nfe).trajectory[-1] - exact
    ).abs().item()
    assert r_err < e_err


@pytest.mark.analytical
def test_reject_indivisible_nfe() -> None:
    with pytest.raises(ValueError, match="divisible"):
        HeunSolver().solve(
            LinearDecayField(),
            torch.ones(1, 1, dtype=torch.float64),
            0.0,
            1.0,
            requested_nfe=5,
        )
