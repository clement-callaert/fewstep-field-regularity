"""Tests for the grid-aware Euler construction and Class-S embedding."""

from __future__ import annotations

import math

import pytest

from fewstep_regularities.analysis.grid_aware import (
    class_s_embedding,
    epsilon_n,
    evaluate_cell,
    oscillatory_field,
    theorem_holds,
)


@pytest.mark.analytical
@pytest.mark.parametrize("n_steps", [1, 2, 4, 8, 16])
@pytest.mark.parametrize("L", [math.log(2.0), 0.25, 1.5])
def test_aligned_theorem_holds(L: float, n_steps: int) -> None:
    assert epsilon_n(L, n_steps) > 0.0
    assert theorem_holds(L, n_steps)


@pytest.mark.analytical
def test_epsilon_identity_makes_euler_exact() -> None:
    L = math.log(2.0)
    n_steps = 4
    eps = epsilon_n(L, n_steps)
    step = 1.0 / n_steps
    factor = 1.0 + step * (L + eps)
    assert factor == pytest.approx(math.exp(L / n_steps), rel=0.0, abs=1e-15)
    assert factor**n_steps == pytest.approx(math.exp(L), rel=0.0, abs=1e-14)


@pytest.mark.analytical
def test_constant_euler_is_strictly_inexact() -> None:
    L = 0.75
    n_steps = 8
    cell = evaluate_cell(L, n_steps)
    assert cell.numerical0 == pytest.approx((1.0 + L / n_steps) ** n_steps)
    assert cell.numerical0 < cell.exact0
    assert cell.error0 > 0.0


@pytest.mark.analytical
def test_phase_offset_destroys_euler_exactness_but_keeps_endpoints() -> None:
    cell = evaluate_cell(math.log(2.0), 8, phase=0.5 * math.pi)
    assert cell.endpoints_match
    assert cell.R1 > cell.R0
    assert not cell.euler_exact_on_oscillation
    assert cell.error1 > 1e-8


@pytest.mark.analytical
def test_off_grid_integer_frequency_keeps_endpoints_breaks_aliasing() -> None:
    """Integer frequencies still integrate to L, so exact endpoints match.

    Aliasing at left Euler nodes fails when f is not the grid frequency N,
    so the ranking inversion of the aligned theorem disappears.
    """
    cell = evaluate_cell(math.log(2.0), 8, frequency=7.0)
    assert cell.endpoints_match
    assert not cell.euler_exact_on_oscillation
    assert not cell.ranking_inverted


@pytest.mark.analytical
def test_noninteger_frequency_with_nonzero_mean_breaks_endpoint_match() -> None:
    """If sin(2 pi f) is nonzero, the cosine perturbation changes the integral."""
    cell = evaluate_cell(math.log(2.0), 8, frequency=7.25)
    assert not cell.endpoints_match
    assert not cell.ranking_inverted


@pytest.mark.analytical
def test_shifted_nodes_break_aliasing() -> None:
    cell = evaluate_cell(math.log(2.0), 8, theta=0.5)
    assert cell.endpoints_match
    assert not cell.euler_exact_on_oscillation


@pytest.mark.analytical
def test_heun_is_not_exact_on_the_aligned_oscillation() -> None:
    cell = evaluate_cell(math.log(2.0), 8, solver="heun")
    assert cell.endpoints_match
    assert not cell.euler_exact_on_oscillation
    assert cell.error1 > 1e-8


@pytest.mark.analytical
def test_class_s_embedding_endpoints_and_no_simultaneous_zero() -> None:
    L = math.log(2.0)
    field = oscillatory_field(L, 4)
    q0, alpha0, sigma0 = class_s_embedding(field, L, 0.0)
    q1, alpha1, sigma1 = class_s_embedding(field, L, 1.0)
    assert q0 == pytest.approx(1.0, abs=1e-12)
    assert alpha0 == pytest.approx(1.0, abs=1e-12)
    assert sigma0 == pytest.approx(0.0, abs=1e-12)
    assert q1 == pytest.approx(math.exp(2.0 * L), rel=1e-8)
    assert alpha1 == pytest.approx(0.0, abs=1e-8)
    assert sigma1 == pytest.approx(1.0, abs=1e-8)
    for time in (0.0, 0.25, 0.5, 0.75, 1.0):
        variance, alpha, sigma = class_s_embedding(field, L, time)
        assert variance > 0.0
        assert not (abs(alpha) < 1e-12 and abs(sigma) < 1e-12)
        reconstructed = alpha**2 + math.exp(2.0 * L) * sigma**2
        assert reconstructed == pytest.approx(variance, rel=1e-8, abs=1e-10)
