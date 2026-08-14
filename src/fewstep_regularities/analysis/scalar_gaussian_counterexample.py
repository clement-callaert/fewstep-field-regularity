"""Certified one-dimensional Gaussian Heun ranking counterexample.

Centered independent interpolant with source N(0,1) and target N(0,4).
Heun at NFE 8 uses four uniform steps of size 1/4.

Regularity integrals are exact. The linear Heun product is rational.
The VP product is an element of Q[pi, sqrt(2)] with all nonnegative
coefficients; substituting the rational bounds sqrt(2) < 99/70 and
pi < 355/113 therefore yields a strict rational upper bound.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

import mpmath as mp

from fewstep_regularities.analysis.affine_flow import scalar_drift
from fewstep_regularities.analysis.local_error import (
    evaluations_per_step,
    propagate_scalar_mode,
    scalar_step_factor,
)

LAMBDA = 4
NFE = 8
HEUN_STAGES = 2
N_STEPS = NFE // HEUN_STAGES
STEP = Fraction(1, N_STEPS)
EXACT_ENDPOINT_FACTOR = 2  # sqrt(LAMBDA)

LINEAR_REGULARITY = Fraction(5, 8) * math.pi - 1
VP_REGULARITY = (math.pi**2) / 16

LINEAR_HEUN_FACTOR = Fraction(6797469, 3559400)
LINEAR_W2 = abs(LINEAR_HEUN_FACTOR - EXACT_ENDPOINT_FACTOR)

W2_LINEAR_UPPER = Fraction(91, 1000)  # 0.091
W2_VP_LOWER = Fraction(13, 100)  # 0.130
R_VP_UPPER = Fraction(187, 100)  # 1.87; W2_VP > 0.130 iff r_VP < 1.87

# Classical rational enclosures. sqrt(2) < 99/70 because 99^2 - 2*70^2 = 1.
# pi < 355/113 is proved below from Machin's formula with an alternating remainder.
SQRT2_UPPER = Fraction(99, 70)
PI_UPPER = Fraction(355, 113)

Poly = dict[tuple[int, int], Fraction]

# Displayed four-step VP Heun product in Q[pi, sqrt(2)], reduced with
# sqrt(2)^2 = 2. Keys are (power of pi, power of sqrt(2) in {0, 1}).
DISPLAYED_VP_HEUN_PRODUCT: Poly = {
    (0, 0): Fraction(1),
    (1, 0): Fraction(3, 40),
    (1, 1): Fraction(15, 164),
    (2, 0): Fraction(78579, 10758400),
    (2, 1): Fraction(45, 5248),
    (3, 0): Fraction(11421, 17213440),
    (3, 1): Fraction(4671, 17213440),
    (4, 0): Fraction(5103, 275415040),
    (4, 1): Fraction(567, 55083008),
    (5, 0): Fraction(243, 2203320320),
    (5, 1): Fraction(729, 2203320320),
    (6, 0): Fraction(729, 176265625600),
}


def linear_variance(time: Fraction) -> Fraction:
    """Return q_lin(t) = (1-t)^2 + 4 t^2."""
    return (1 - time) ** 2 + LAMBDA * time**2


def completed_square_linear_variance(time: Fraction) -> Fraction:
    """Return 5[(t-1/5)^2 + (2/5)^2] = 5(t-1/5)^2 + 4/5."""
    shift = time - Fraction(1, 5)
    return 5 * (shift**2 + Fraction(2, 5) ** 2)


def linear_drift(time: Fraction) -> Fraction:
    """Return a_lin(t) = q'(t)/(2 q(t)) = (5t-1)/q(t)."""
    return (5 * time - 1) / linear_variance(time)


def heun_factor(a1: Fraction, a2: Fraction, step: Fraction) -> Fraction:
    """Return the exact Heun factor 1 + (h/2)(a1 + a2(1+h a1))."""
    return 1 + (step / 2) * (a1 + a2 * (1 + step * a1))


def linear_heun_step_factors() -> tuple[Fraction, ...]:
    """Return the four exact rational Heun factors on the uniform grid."""
    factors: list[Fraction] = []
    for index in range(N_STEPS):
        t0 = index * STEP
        a1 = linear_drift(t0)
        a2 = linear_drift(t0 + STEP)
        factor = heun_factor(a1, a2, STEP)
        if factor <= 0:
            raise ArithmeticError("non-positive linear Heun factor")
        factors.append(factor)
    return tuple(factors)


def linear_heun_endpoint_factor() -> Fraction:
    """Return the exact rational linear Heun endpoint factor."""
    product = Fraction(1)
    for factor in linear_heun_step_factors():
        product *= factor
    return product


def linear_regularity() -> float:
    """Return R_lin = 5 pi/8 - 1."""
    return float(LINEAR_REGULARITY)


def vp_regularity() -> float:
    """Return R_VP = pi^2/16."""
    return float(VP_REGULARITY)


def _poly_clean(terms: Mapping[tuple[int, int], Fraction]) -> Poly:
    return {key: value for key, value in terms.items() if value != 0}


def _poly_add(left: Poly, right: Poly) -> Poly:
    out: Poly = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, Fraction(0)) + value
    return _poly_clean(out)


def _poly_mul(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for (p1, s1), c1 in left.items():
        for (p2, s2), c2 in right.items():
            power_pi = p1 + p2
            power_s = s1 + s2
            coeff = c1 * c2
            extra, power_s = divmod(power_s, 2)
            coeff *= 2**extra
            key = (power_pi, power_s)
            out[key] = out.get(key, Fraction(0)) + coeff
    return _poly_clean(out)


def _poly_const(value: Fraction) -> Poly:
    return {(0, 0): Fraction(value)} if value != 0 else {}


def _poly_scale(terms: Poly, scale: Fraction) -> Poly:
    return _poly_clean({key: scale * value for key, value in terms.items()})


def evaluate_poly(terms: Poly, pi_val: Fraction, sqrt2_val: Fraction) -> Fraction:
    """Evaluate an element of Q[pi, sqrt(2)] at rational arguments."""
    total = Fraction(0)
    for (power_pi, power_s), coeff in terms.items():
        total += coeff * (pi_val**power_pi) * (sqrt2_val**power_s)
    return total


def vp_heun_product_records(terms: Poly | None = None) -> list[dict[str, int]]:
    """Return sorted coefficient records of the VP Heun product."""
    product = vp_heun_product_poly() if terms is None else terms
    rows: list[dict[str, int]] = []
    for power_pi, power_s in sorted(product):
        coeff = product[(power_pi, power_s)]
        rows.append(
            {
                "pi_power": power_pi,
                "sqrt2_power": power_s,
                "numerator": coeff.numerator,
                "denominator": coeff.denominator,
            }
        )
    return rows


def vp_grid_drifts() -> tuple[Poly, Poly, Poly, Poly, Poly]:
    """Return exact a_VP at t = 0, 1/4, 1/2, 3/4, 1 as elements of Q[pi, sqrt(2)]."""
    zero: Poly = {}
    a_quarter = {(1, 0): Fraction(9, 82), (1, 1): Fraction(15, 82)}
    a_half = {(1, 0): Fraction(3, 10)}
    a_three_quarter = {(1, 0): Fraction(-9, 82), (1, 1): Fraction(15, 82)}
    return zero, a_quarter, a_half, a_three_quarter, zero


def _heun_poly(a1: Poly, a2: Poly) -> Poly:
    """Heun factor 1 + (h/2)(a1 + a2(1 + h a1)) with h = 1/4."""
    one = _poly_const(Fraction(1))
    h = _poly_const(STEP)
    half = _poly_const(STEP / 2)
    inner = _poly_add(a1, _poly_mul(a2, _poly_add(one, _poly_mul(h, a1))))
    return _poly_add(one, _poly_mul(half, inner))


def vp_heun_step_polys() -> tuple[Poly, Poly, Poly, Poly]:
    """Return the four VP Heun factors as elements of Q[pi, sqrt(2)]."""
    a0, a1, a2, a3, a4 = vp_grid_drifts()
    return (
        _heun_poly(a0, a1),
        _heun_poly(a1, a2),
        _heun_poly(a2, a3),
        _heun_poly(a3, a4),
    )


def vp_heun_product_poly() -> Poly:
    """Return the exact four-step VP Heun product in Q[pi, sqrt(2)]."""
    factors = vp_heun_step_polys()
    product = _poly_const(Fraction(1))
    for factor in factors:
        product = _poly_mul(product, factor)
    return product


def all_vp_heun_poly_coefficients_nonnegative(terms: Poly | None = None) -> bool:
    """Return True if every coefficient of the VP product is nonnegative."""
    product = vp_heun_product_poly() if terms is None else terms
    return all(value >= 0 for value in product.values()) and (0, 0) in product


def arctan_taylor_partial(x: Fraction, n_terms: int) -> Fraction:
    """Return the first n_terms of the arctan Taylor series at a rational x.

    arctan x = sum_{k>=0} (-1)^k x^{2k+1}/(2k+1) for |x|<1. For 0<x<1 the
    Leibniz remainder implies: an odd number of terms is an upper bound, and
    an even number of terms is a lower bound.
    """
    if n_terms < 1:
        raise ValueError("n_terms must be at least 1")
    total = Fraction(0)
    for k in range(n_terms):
        total += ((-1) ** k) * (x ** (2 * k + 1)) / (2 * k + 1)
    return total


def machin_pi_upper_bound() -> Fraction:
    """Return a rational upper bound for pi from Machin's formula.

    pi = 16 arctan(1/5) - 4 arctan(1/239). Seven Taylor terms (odd) upper-bound
    arctan(1/5); four Taylor terms (even) lower-bound arctan(1/239).
    """
    arctan5_upper = arctan_taylor_partial(Fraction(1, 5), 7)
    arctan239_lower = arctan_taylor_partial(Fraction(1, 239), 4)
    return 16 * arctan5_upper - 4 * arctan239_lower


def machin_pi_upper_bound_integer_certificate() -> tuple[int, int]:
    """Return (113 * numerator, 355 * denominator) of the Machin upper bound.

    The comparison left < right is equivalent to the bound being < 355/113.
    """
    bound = machin_pi_upper_bound()
    return 113 * bound.numerator, 355 * bound.denominator


def sqrt2_upper_integer_certificate() -> tuple[int, int]:
    """Return (99^2, 2*70^2); the difference 1 proves 99/70 > sqrt(2)."""
    return 99**2, 2 * 70**2


def vp_heun_rational_upper_bound() -> Fraction:
    """Return the VP Heun product evaluated at pi=355/113, sqrt(2)=99/70."""
    product = vp_heun_product_poly()
    if not all_vp_heun_poly_coefficients_nonnegative(product):
        raise ArithmeticError("VP product has a negative coefficient")
    total = Fraction(0)
    for (power_pi, power_s), coeff in product.items():
        total += coeff * (PI_UPPER**power_pi) * (SQRT2_UPPER**power_s)
    return total


def vp_heun_integer_certificate() -> tuple[int, int]:
    """Return (100 * numerator, 187 * denominator) of the rational upper bound.

    The comparison 100 * n < 187 * d is equivalent to bound < 187/100.
    """
    bound = vp_heun_rational_upper_bound()
    return 100 * bound.numerator, 187 * bound.denominator


def vp_heun_factors_positive() -> bool:
    """Return True if each algebraic VP Heun factor is strictly positive.

    a(1/4)>0 is immediate. a(3/4)>0 because 15 sqrt(2) > 9 iff 50 > 9 after
    squaring the positive quantities 5 sqrt(2) and 3.
    The remaining two factors are 1 plus a combination of those drifts with
    positive Heun weights, hence > 1.
    """
    _a0, a1, _a2, a3, _a4 = vp_grid_drifts()
    if a1[(1, 0)] <= 0 or a1[(1, 1)] <= 0:
        return False
    if a3[(1, 1)] <= 0:
        return False
    # 15^2 * 2 - 9^2 = 450 - 81 = 369 > 0 proves 15 sqrt(2) > 9.
    if 15**2 * 2 - 9**2 <= 0:
        return False
    factors = vp_heun_step_polys()
    constants = [factor.get((0, 0), Fraction(0)) for factor in factors]
    return all(const >= 1 for const in constants)


def _vp_drift_iv(time: mp.iv.mpf) -> mp.iv.mpf:
    variance = (
        mp.iv.cos(mp.iv.pi * time / 2) ** 2
        + LAMBDA * mp.iv.sin(mp.iv.pi * time / 2) ** 2
    )
    return (mp.iv.pi * (LAMBDA - 1) / 4) * mp.iv.sin(mp.iv.pi * time) / variance


def vp_heun_endpoint_interval(*, dps: int = 40) -> mp.iv.mpf:
    """Independent interval enclosure of the VP Heun product (not the proof)."""
    with mp.workdps(dps):
        mp.iv.dps = dps
        step = mp.iv.mpf("0.25")
        product = mp.iv.mpf("1")
        for index in range(N_STEPS):
            t0 = mp.iv.mpf(index) * step
            a1 = _vp_drift_iv(t0)
            a2 = _vp_drift_iv(t0 + step)
            factor = 1 + (step / 2) * (a1 + a2 * (1 + step * a1))
            if factor.a <= 0:
                raise ArithmeticError(
                    "VP Heun factor interval is not strictly positive"
                )
            product *= factor
        return product


def _interval_end_strings(value: mp.iv.mpf) -> tuple[str, str]:
    """Return decimal strings for the lower and upper ends of an iv.mpf."""
    low = str(value.a).strip("[]").split(",")[0].strip()
    high = str(value.b).strip("[]").split(",")[-1].strip()
    return low, high


def mpmath_version() -> str:
    """Return the installed mpmath version string."""
    return str(getattr(mp, "__version__", "unknown"))


@dataclass(frozen=True)
class ScalarGaussianCounterexample:
    """Certified ranking reversal for the scalar Gaussian Heun example."""

    nfe: int
    n_steps: int
    step_size: Fraction
    linear_regularity: float
    vp_regularity: float
    linear_factor: Fraction
    linear_w2: Fraction
    vp_rational_upper: Fraction
    vp_integer_left: int
    vp_integer_right: int
    ranking_inverted: bool
    all_heun_factors_positive: bool
    software: str
    mpmath_version: str
    interval_dps: int
    vp_factor_interval: tuple[str, str]
    vp_w2_interval: tuple[str, str]


def certify(*, dps: int = 40) -> ScalarGaussianCounterexample:
    """Derive and certify the ranking reversal by exact rationals.

    Interval arithmetic is recorded only as an independent cross-check.
    """
    if evaluations_per_step("heun") != HEUN_STAGES:
        raise RuntimeError("Heun stage count changed")
    if NFE % HEUN_STAGES != 0:
        raise RuntimeError("NFE is not divisible by Heun stages")
    factors = linear_heun_step_factors()
    linear_factor = linear_heun_endpoint_factor()
    if linear_factor != LINEAR_HEUN_FACTOR:
        raise RuntimeError(f"unexpected linear Heun product {linear_factor}")
    linear_w2 = abs(linear_factor - EXACT_ENDPOINT_FACTOR)
    if not (linear_w2 < W2_LINEAR_UPPER):
        raise RuntimeError("linear W2 is not strictly below 0.091")
    machin_left, machin_right = machin_pi_upper_bound_integer_certificate()
    if not (machin_left < machin_right):
        raise RuntimeError("Machin integer comparison does not prove pi < 355/113")
    if machin_pi_upper_bound() >= PI_UPPER:
        raise RuntimeError("Machin upper bound does not prove pi < 355/113")
    left, right = sqrt2_upper_integer_certificate()
    if left <= right:
        raise RuntimeError("99^2 <= 2*70^2; sqrt(2) bound failed")
    if not vp_heun_factors_positive():
        raise RuntimeError("a VP Heun factor is not certified positive")
    bound = vp_heun_rational_upper_bound()
    int_left, int_right = vp_heun_integer_certificate()
    if not (int_left < int_right):
        raise RuntimeError("integer certificate r_VP < 187/100 failed")
    if bound >= R_VP_UPPER:
        raise RuntimeError("rational VP upper bound is not below 187/100")
    inverted = (
        linear_regularity() > vp_regularity()
        and linear_w2 < W2_LINEAR_UPPER
        and bound < R_VP_UPPER
    )
    vp_factor = vp_heun_endpoint_interval(dps=dps)
    vp_distance = EXACT_ENDPOINT_FACTOR - vp_factor
    vp_low, vp_high = _interval_end_strings(vp_factor)
    dist_low, dist_high = _interval_end_strings(vp_distance)
    return ScalarGaussianCounterexample(
        nfe=NFE,
        n_steps=N_STEPS,
        step_size=STEP,
        linear_regularity=linear_regularity(),
        vp_regularity=vp_regularity(),
        linear_factor=linear_factor,
        linear_w2=linear_w2,
        vp_rational_upper=bound,
        vp_integer_left=int_left,
        vp_integer_right=int_right,
        ranking_inverted=inverted,
        all_heun_factors_positive=all(factor > 0 for factor in factors),
        software=(
            f"Python fractions.Fraction; Machin pi bound; "
            f"mpmath {mpmath_version()} interval cross-check"
        ),
        mpmath_version=mpmath_version(),
        interval_dps=dps,
        vp_factor_interval=(vp_low, vp_high),
        vp_w2_interval=(dist_low, dist_high),
    )


def float64_crosscheck() -> dict[str, float]:
    """Return the package float64 Heun factors and W2 values."""
    linear = propagate_scalar_mode("linear", "heun", float(LAMBDA), NFE)
    vp = propagate_scalar_mode("variance_preserving", "heun", float(LAMBDA), NFE)
    return {
        "linear_factor": linear.factor,
        "vp_factor": vp.factor,
        "linear_w2": abs(abs(linear.factor) - EXACT_ENDPOINT_FACTOR),
        "vp_w2": abs(abs(vp.factor) - EXACT_ENDPOINT_FACTOR),
        "linear_step0": scalar_step_factor("linear", "heun", float(LAMBDA), 0.0, 0.25),
        "vp_drift_formula": scalar_drift("variance_preserving", float(LAMBDA), 0.25),
    }


def high_precision_crosscheck(*, dps: int = 80) -> dict[str, str]:
    """Return 80-digit Heun products from mpmath (not the certificate)."""
    with mp.workdps(dps):
        step = mp.mpf("0.25")

        def a_lin(time: mp.mpf) -> mp.mpf:
            return (5 * time - 1) / (1 - 2 * time + 5 * time**2)

        def a_vp(time: mp.mpf) -> mp.mpf:
            variance = (
                mp.cos(mp.pi * time / 2) ** 2 + LAMBDA * mp.sin(mp.pi * time / 2) ** 2
            )
            return (mp.pi * (LAMBDA - 1) / 4) * mp.sin(mp.pi * time) / variance

        def product(drift: Callable[[Any], Any]) -> Any:
            value = mp.mpf("1")
            for index in range(N_STEPS):
                t0 = index * step
                a1 = drift(t0)
                a2 = drift(t0 + step)
                value *= 1 + (step / 2) * (a1 + a2 * (1 + step * a1))
            return value

        linear = product(a_lin)
        vp = product(a_vp)
        return {
            "linear_factor": str(linear),
            "vp_factor": str(vp),
            "linear_w2": str(abs(linear - EXACT_ENDPOINT_FACTOR)),
            "vp_w2": str(abs(vp - EXACT_ENDPOINT_FACTOR)),
        }
