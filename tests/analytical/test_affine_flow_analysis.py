"""Analytical tests for Phase 4 scalar affine formulas."""

from __future__ import annotations

import math

import pytest

from fewstep_regularities.analysis.affine_flow import (
    exact_transition_factor,
    scalar_affine_quantities,
    scalar_drift,
    scalar_variance,
)
from fewstep_regularities.analysis.local_error import (
    leading_local_coefficient,
    material_derivative_eigenvalue,
    propagate_scalar_mode,
    scalar_step_factor,
)
from fewstep_regularities.analysis.precision import high_precision_mode_factor


@pytest.mark.analytical
@pytest.mark.parametrize("path_name", ["linear", "variance_preserving"])
def test_scalar_drift_is_half_log_variance_derivative(path_name: str) -> None:
    eigenvalue = 3.5
    time = 0.37
    step = 1e-6
    finite_difference = (
        math.log(scalar_variance(path_name, eigenvalue, time + step))
        - math.log(scalar_variance(path_name, eigenvalue, time - step))
    ) / (2.0 * step)
    assert 2.0 * scalar_drift(path_name, eigenvalue, time) == pytest.approx(
        finite_difference, rel=1e-9, abs=1e-9
    )


@pytest.mark.analytical
@pytest.mark.parametrize("path_name", ["linear", "variance_preserving"])
def test_exact_transition_factor_composes(path_name: str) -> None:
    eigenvalue = 0.2
    left = exact_transition_factor(path_name, eigenvalue, 0.0, 0.4)
    right = exact_transition_factor(path_name, eigenvalue, 0.4, 1.0)
    assert left * right == pytest.approx(math.sqrt(eigenvalue), abs=1e-14)


@pytest.mark.analytical
def test_material_derivative_agrees_with_finite_difference() -> None:
    path_name = "linear"
    eigenvalue = 4.0
    time = 0.31
    step = 1e-6
    derivative = (
        scalar_drift(path_name, eigenvalue, time + step)
        - scalar_drift(path_name, eigenvalue, time - step)
    ) / (2.0 * step)
    expected = derivative + scalar_drift(path_name, eigenvalue, time) ** 2
    assert material_derivative_eigenvalue(path_name, eigenvalue, time) == pytest.approx(
        expected, rel=1e-9, abs=1e-9
    )


@pytest.mark.analytical
@pytest.mark.parametrize("solver_name", ["euler", "heun", "rk4"])
def test_local_defects_sum_to_endpoint_log_error(solver_name: str) -> None:
    result = propagate_scalar_mode(
        "variance_preserving",
        solver_name,
        eigenvalue=0.05,
        requested_nfe=16,
    )
    endpoint_log_error = math.log(abs(result.factor)) - math.log(result.exact_factor)
    assert sum(result.local_log_defects) == pytest.approx(
        endpoint_log_error,
        abs=2e-15,
    )
    assert sum(result.transported_local_contributions) == pytest.approx(
        result.factor - result.exact_factor,
        abs=2e-15,
    )


@pytest.mark.analytical
@pytest.mark.parametrize("solver_name", ["euler", "heun"])
def test_leading_local_coefficient_matches_small_step(solver_name: str) -> None:
    path_name = "linear"
    eigenvalue = 2.0
    time = 0.27
    step = 2e-4
    numerical = scalar_step_factor(
        path_name,
        solver_name,
        eigenvalue,
        time,
        step,
    )
    exact = exact_transition_factor(
        path_name,
        eigenvalue,
        time,
        time + step,
    )
    order = 2 if solver_name == "euler" else 3
    observed = (exact - numerical) / step**order
    expected = leading_local_coefficient(
        path_name,
        solver_name,
        eigenvalue,
        time,
    )
    assert observed == pytest.approx(expected, rel=3e-3, abs=2e-5)


@pytest.mark.analytical
def test_autograd_drift_derivatives_are_finite() -> None:
    values = scalar_affine_quantities(
        "variance_preserving",
        eigenvalue=5.0,
        time=0.42,
    )
    assert all(
        math.isfinite(value)
        for value in (
            values.variance,
            values.drift,
            values.drift_derivative,
            values.drift_second_derivative,
            values.drift_third_derivative,
        )
    )


@pytest.mark.analytical
def test_high_precision_factor_agrees_with_float64() -> None:
    result = propagate_scalar_mode(
        "linear",
        "rk4",
        eigenvalue=7.0,
        requested_nfe=32,
    )
    high_precision = high_precision_mode_factor(
        "linear",
        "rk4",
        eigenvalue=7.0,
        requested_nfe=32,
        decimal_digits=80,
    )
    assert result.factor == pytest.approx(float(high_precision), abs=2e-15)


@pytest.mark.analytical
def test_euler_nonimplication_construction() -> None:
    endpoint_log_factor = 1.0
    n_steps = 8
    epsilon = n_steps * (math.exp(endpoint_log_factor / n_steps) - 1.0)
    epsilon -= endpoint_log_factor
    constant_metric = endpoint_log_factor**2
    oscillatory_metric = constant_metric + 0.5 * epsilon**2
    constant_factor = (1.0 + endpoint_log_factor / n_steps) ** n_steps
    oscillatory_factor = (1.0 + (endpoint_log_factor + epsilon) / n_steps) ** n_steps
    exact_factor = math.exp(endpoint_log_factor)
    assert oscillatory_metric > constant_metric
    assert abs(oscillatory_factor - exact_factor) < abs(constant_factor - exact_factor)
