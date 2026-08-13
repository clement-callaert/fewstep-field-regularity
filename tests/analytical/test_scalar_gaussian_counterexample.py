"""Tests for the certified scalar Gaussian Heun counterexample."""

from __future__ import annotations

import math
from fractions import Fraction

import mpmath as mp
import pytest
from scipy.integrate import quad

from fewstep_regularities.analysis.affine_flow import scalar_drift, scalar_variance
from fewstep_regularities.analysis.local_error import evaluations_per_step
from fewstep_regularities.analysis.scalar_gaussian_counterexample import (
    EXACT_ENDPOINT_FACTOR,
    LAMBDA,
    LINEAR_HEUN_FACTOR,
    N_STEPS,
    NFE,
    PI_UPPER,
    R_VP_UPPER,
    SQRT2_UPPER,
    W2_LINEAR_UPPER,
    W2_VP_LOWER,
    all_vp_heun_poly_coefficients_nonnegative,
    arctan_taylor_partial,
    certify,
    completed_square_linear_variance,
    evaluate_poly,
    float64_crosscheck,
    heun_factor,
    high_precision_crosscheck,
    linear_drift,
    linear_heun_endpoint_factor,
    linear_heun_step_factors,
    linear_regularity,
    linear_variance,
    machin_pi_upper_bound,
    machin_pi_upper_bound_integer_certificate,
    mpmath_version,
    sqrt2_upper_integer_certificate,
    vp_grid_drifts,
    vp_heun_endpoint_interval,
    vp_heun_factors_positive,
    vp_heun_integer_certificate,
    vp_heun_product_poly,
    vp_heun_product_records,
    vp_heun_rational_upper_bound,
    vp_regularity,
)


@pytest.mark.analytical
def test_nfe_accounting() -> None:
    assert evaluations_per_step("heun") == 2
    assert NFE == 8
    assert N_STEPS == 4
    assert NFE % evaluations_per_step("heun") == 0


@pytest.mark.analytical
def test_linear_and_vp_drift_formulas() -> None:
    for time in (0.0, 0.25, 0.5, 0.75, 1.0):
        q = (1.0 - time) ** 2 + LAMBDA * time**2
        assert scalar_variance("linear", float(LAMBDA), time) == pytest.approx(q)
        expected = ((1.0 + LAMBDA) * time - 1.0) / q
        assert scalar_drift("linear", float(LAMBDA), time) == pytest.approx(expected)
        assert float(linear_drift(Fraction(time).limit_denominator())) == pytest.approx(
            expected, rel=1e-12, abs=1e-12
        )


@pytest.mark.analytical
def test_vp_weierstrass_identity() -> None:
    def integrand(u: float) -> float:
        return math.sin(u) ** 2 / (5.0 - 3.0 * math.cos(u)) ** 2

    value, err = quad(integrand, 0.0, math.pi, epsabs=1e-14)
    assert math.isfinite(err)
    assert value == pytest.approx(math.pi / 36.0, rel=0.0, abs=1e-12)
    assert (9.0 * math.pi / 4.0) * value == pytest.approx(
        vp_regularity(), rel=0.0, abs=1e-12
    )


@pytest.mark.analytical
def test_exact_regularity_identities() -> None:
    def a_lin(time: float) -> float:
        return ((5.0 * time - 1.0) / ((1.0 - time) ** 2 + 4.0 * time**2)) ** 2

    def a_vp(time: float) -> float:
        variance = (
            math.cos(math.pi * time / 2) ** 2 + 4.0 * math.sin(math.pi * time / 2) ** 2
        )
        drift = (3.0 * math.pi / 4.0) * math.sin(math.pi * time) / variance
        return drift**2

    lin_quad, lin_err = quad(a_lin, 0.0, 1.0, epsabs=1e-14)
    vp_quad, vp_err = quad(a_vp, 0.0, 1.0, epsabs=1e-14)
    assert lin_err < 1e-10
    assert vp_err < 1e-8
    assert lin_quad == pytest.approx(linear_regularity(), rel=0.0, abs=1e-12)
    assert vp_quad == pytest.approx(vp_regularity(), rel=0.0, abs=1e-12)
    assert linear_regularity() == pytest.approx(5.0 * math.pi / 8.0 - 1.0)
    assert vp_regularity() == pytest.approx(math.pi**2 / 16.0)
    assert linear_regularity() > vp_regularity()


@pytest.mark.analytical
def test_exact_linear_heun_factor() -> None:
    factors = linear_heun_step_factors()
    assert all(factor > 0 for factor in factors)
    assert linear_heun_endpoint_factor() == LINEAR_HEUN_FACTOR
    assert Fraction(6797469, 3559400) == LINEAR_HEUN_FACTOR
    w2 = abs(LINEAR_HEUN_FACTOR - EXACT_ENDPOINT_FACTOR)
    assert w2 == Fraction(321331, 3559400)
    assert w2 < W2_LINEAR_UPPER
    # Independent reconstruction of the four rational steps.
    h = Fraction(1, 4)
    t0 = Fraction(0)
    rebuilt = Fraction(1)
    for _ in range(4):
        rebuilt *= heun_factor(linear_drift(t0), linear_drift(t0 + h), h)
        t0 += h
    assert rebuilt == LINEAR_HEUN_FACTOR


@pytest.mark.analytical
def test_completed_square_expands_to_linear_variance() -> None:
    # 5[(t-1/5)^2 + (2/5)^2] = 5(t-1/5)^2 + 4/5 = 1 - 2t + 5t^2.
    t2_coeff = Fraction(5)
    t1_coeff = 5 * Fraction(-2, 5)
    t0_coeff = 5 * (Fraction(1, 25) + Fraction(4, 25))
    assert (t2_coeff, t1_coeff, t0_coeff) == (5, -2, 1)
    for time in (
        Fraction(0),
        Fraction(1, 5),
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(3, 4),
        Fraction(1),
        Fraction(2, 7),
    ):
        completed = completed_square_linear_variance(time)
        expanded = 1 - 2 * time + 5 * time**2
        assert completed == expanded
        assert completed == linear_variance(time)


@pytest.mark.analytical
def test_vp_grid_drifts_exact_algebraic_values() -> None:
    a0, a_quarter, a_half, a_three_quarter, a1 = vp_grid_drifts()
    assert a0 == {}
    assert a1 == {}
    assert a_quarter == {(1, 0): Fraction(9, 82), (1, 1): Fraction(15, 82)}
    assert a_half == {(1, 0): Fraction(3, 10)}
    assert a_three_quarter == {(1, 0): Fraction(-9, 82), (1, 1): Fraction(15, 82)}
    # 15 sqrt(2) > 9 because 15^2 * 2 - 9^2 = 369 > 0, so a(3/4) > 0.
    assert 15**2 * 2 - 9**2 == 369
    assert vp_heun_factors_positive()


@pytest.mark.analytical
def test_vp_heun_product_is_nonnegative_in_pi_sqrt2() -> None:
    product = vp_heun_product_poly()
    assert all_vp_heun_poly_coefficients_nonnegative(product)
    records = vp_heun_product_records(product)
    assert len(records) == 12
    assert all(row["numerator"] > 0 for row in records)
    assert (0, 0) in product
    assert product[(0, 0)] == 1


@pytest.mark.analytical
def test_rational_and_integer_vp_certificate() -> None:
    left, right = sqrt2_upper_integer_certificate()
    assert left - right == 1
    machin_left, machin_right = machin_pi_upper_bound_integer_certificate()
    assert machin_left < machin_right
    assert machin_pi_upper_bound() < PI_UPPER
    # Odd/even Leibniz remainders: 7 terms upper-bound arctan(1/5).
    x5 = Fraction(1, 5)
    assert arctan_taylor_partial(x5, 7) > arctan_taylor_partial(x5, 8)
    bound = vp_heun_rational_upper_bound()
    assert bound == evaluate_poly(vp_heun_product_poly(), PI_UPPER, SQRT2_UPPER)
    assert bound < R_VP_UPPER
    int_left, int_right = vp_heun_integer_certificate()
    assert int_left < int_right
    assert int_left == 100 * bound.numerator
    assert int_right == 187 * bound.denominator
    # r_VP < 187/100 and r_VP > 0 imply W2_VP = 2 - r_VP > 13/100.
    assert Fraction(2) - bound > W2_VP_LOWER
    assert Fraction(187, 100) == R_VP_UPPER
    assert Fraction(13, 100) == W2_VP_LOWER


@pytest.mark.analytical
def test_certified_vp_interval_is_independent_crosscheck() -> None:
    result = certify(dps=40)
    assert result.ranking_inverted
    assert result.all_heun_factors_positive
    assert result.vp_rational_upper < R_VP_UPPER
    assert result.vp_integer_left < result.vp_integer_right
    assert result.mpmath_version == mpmath_version() == mp.__version__
    low = mp.mpf(result.vp_factor_interval[0])
    high = mp.mpf(result.vp_factor_interval[1])
    assert 0 < low <= high < EXACT_ENDPOINT_FACTOR
    w_low = mp.mpf(result.vp_w2_interval[0])
    w_high = mp.mpf(result.vp_w2_interval[1])
    assert w_low > mp.mpf("0.130")
    assert w_low <= w_high
    assert result.linear_w2 < W2_LINEAR_UPPER < W2_VP_LOWER
    interval = vp_heun_endpoint_interval(dps=40)
    assert interval.a > 0
    with mp.workdps(40):
        assert (
            mp.mpf("1.8696263416613175")
            < interval.a
            <= interval.b
            < mp.mpf("1.8696263416613176")
        )


@pytest.mark.analytical
def test_float64_and_80digit_crosscheck() -> None:
    values = float64_crosscheck()
    hp = high_precision_crosscheck(dps=80)
    assert values["linear_factor"] == pytest.approx(
        float(LINEAR_HEUN_FACTOR), rel=0.0, abs=1e-14
    )
    assert values["linear_w2"] < 0.091
    assert values["vp_w2"] > 0.130
    assert float(hp["linear_w2"]) < 0.091
    assert float(hp["vp_w2"]) > 0.130
    assert abs(float(hp["vp_factor"]) - values["vp_factor"]) < 1e-14
