"""Deterministic ranking grids for linear, VP, and log-covariance paths."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from fewstep_regularities.analysis.affine_flow import (
    shared_logcov_path,
    scalar_drift,
)
from fewstep_regularities.analysis.continuous_regularity import continuous_regularity
from fewstep_regularities.analysis.local_error import propagate_scalar_mode

PATHS = ("linear", "variance_preserving", "log_covariance")
FOUR_PATHS = (
    "linear",
    "variance_preserving",
    "log_covariance_scalar",
    "log_covariance",
)
SOLVERS = ("euler", "heun", "rk4")
PRIMARY_NFE = (8, 16, 32)
HEUN_BUDGETS = (4, 8, 12, 16, 24, 32, 64, 128, 256)
GEOM_KEYS = (
    ("anisotropic_d2", "anisotropic", 2),
    ("anisotropic_d8", "anisotropic", 8),
    ("low_rank_d2", "low-rank", 2),
    ("low_rank_d8", "low-rank", 8),
)


def family_display_label(family: str, dim: int | None = None) -> str:
    """Return a reader-facing family name for tables and captions.

    Internal artifact keys such as ``low_rank_d2`` are unchanged. At
    ``d=2`` the factor rank equals the ambient dimension, so that case
    is not called low-rank.
    """
    key = str(family).replace("_gaussian", "").replace("_", "-")
    if key in {"low-rank", "low-rank-gaussian"}:
        if dim == 8:
            return r"rank-2 factor+noise"
        return r"factor+noise"
    if key.startswith("anisotropic"):
        return "anisotropic"
    return str(family)


@dataclass(frozen=True)
class PathScores:
    """Regularity and endpoint W2 for one path on one geometry."""

    path: str
    regularity: float
    w2: float


def centered_modal_w2(eigenvalues: Sequence[float], factors: Sequence[float]) -> float:
    """Return Gelbrich W2 for a centered commuting Gaussian endpoint."""
    if len(eigenvalues) != len(factors):
        raise ValueError("eigenvalues and factors must have the same length")
    total = 0.0
    for eigenvalue, factor in zip(eigenvalues, factors, strict=True):
        total += (abs(factor) - math.sqrt(eigenvalue)) ** 2
    return math.sqrt(total)


def encoded_path(path_name: str, eigenvalues: Sequence[float]) -> str:
    """Return a path name, encoding ``M=λ_max`` for the shared Ex. 3.3 schedule."""
    if path_name == "log_covariance_scalar":
        return shared_logcov_path(max(float(value) for value in eigenvalues))
    return path_name


def path_regularity(path_name: str, eigenvalues: Sequence[float]) -> float:
    """Return continuous spectral R, with a closed form for log-covariance."""
    encoded = encoded_path(path_name, eigenvalues)
    if path_name == "log_covariance":
        return max(0.5 * abs(math.log(float(value))) for value in eigenvalues) ** 2
    value, _error = continuous_regularity(encoded, eigenvalues)
    return value


def path_w2(
    path_name: str,
    solver_name: str,
    eigenvalues: Sequence[float],
    nfe: int,
) -> float:
    """Return centered Gaussian W2 from exact-moment modal factors."""
    encoded = encoded_path(path_name, eigenvalues)
    factors = [
        propagate_scalar_mode(encoded, solver_name, float(value), nfe).factor
        for value in eigenvalues
    ]
    return centered_modal_w2(eigenvalues, factors)


def ranking_inversion(r_a: float, r_b: float, w_a: float, w_b: float) -> bool:
    """Return True if R and W2 strictly disagree on a two-path comparison."""
    if r_a == r_b or w_a == w_b:
        return False
    return (r_a - r_b) * (w_a - w_b) < 0.0


def linear_vp_inversion(
    eigenvalues: Sequence[float], solver_name: str, nfe: int
) -> bool:
    """Return whether linear vs VP invert R versus W2."""
    r_lin = path_regularity("linear", eigenvalues)
    r_vp = path_regularity("variance_preserving", eigenvalues)
    w_lin = path_w2("linear", solver_name, eigenvalues, nfe)
    w_vp = path_w2("variance_preserving", solver_name, eigenvalues, nfe)
    return ranking_inversion(r_lin, r_vp, w_lin, w_vp)


def vp_scalar_logcov_inversion(
    eigenvalues: Sequence[float], solver_name: str, nfe: int
) -> bool:
    """Return whether VP vs shared Chen Ex. 3.3 invert R versus W2."""
    r_vp = path_regularity("variance_preserving", eigenvalues)
    r_sc = path_regularity("log_covariance_scalar", eigenvalues)
    w_vp = path_w2("variance_preserving", solver_name, eigenvalues, nfe)
    w_sc = path_w2("log_covariance_scalar", solver_name, eigenvalues, nfe)
    return ranking_inversion(r_vp, r_sc, w_vp, w_sc)


def three_path_scores(
    eigenvalues: Sequence[float], solver_name: str, nfe: int
) -> dict[str, PathScores]:
    """Return R and W2 for linear, VP, and the per-mode log-covariance path."""
    scores: dict[str, PathScores] = {}
    for path in PATHS:
        scores[path] = PathScores(
            path=path,
            regularity=path_regularity(path, eigenvalues),
            w2=path_w2(path, solver_name, eigenvalues, nfe),
        )
    return scores


def four_path_scores(
    eigenvalues: Sequence[float], solver_name: str, nfe: int
) -> dict[str, PathScores]:
    """Return R and W2 for linear, VP, shared Ex. 3.3, and per-mode log-cov."""
    scores: dict[str, PathScores] = {}
    for path in FOUR_PATHS:
        scores[path] = PathScores(
            path=path,
            regularity=path_regularity(path, eigenvalues),
            w2=path_w2(path, solver_name, eigenvalues, nfe),
        )
    return scores


def paired_concordance_score_from_counts(n_agree: int, n_invert: int) -> float:
    """Return (n_agree - n_invert) / n for a complete two-path census.

    Each block contributes +1 if R and W2 agree and -1 if they invert.
    This is a paired concordance score, not Kendall's tau and not a test.
    """
    total = n_agree + n_invert
    if total <= 0:
        raise ValueError("need at least one block")
    return (n_agree - n_invert) / total


def lowest_name(scores: dict[str, PathScores], field: str) -> str:
    """Return the path name with the strictly smallest field value."""
    ordered = sorted(scores.values(), key=lambda row: getattr(row, field))
    return ordered[0].path


def log_covariance_cauchy_schwarz(eigenvalue: float) -> tuple[float, float]:
    """Return (integral of a, R) for the constant-drift schedule on one mode."""
    integral = 0.5 * math.log(eigenvalue)
    regularity = integral**2
    return integral, regularity


def linear_endpoint_drifts(eigenvalue: float) -> tuple[float, float]:
    """Return a_lin(0) and a_lin(1) for an independent linear interpolant."""
    return (
        scalar_drift("linear", eigenvalue, 0.0),
        scalar_drift("linear", eigenvalue, 1.0),
    )


def log_lebesgue_inversion_measure(
    solver_name: str,
    nfe: int,
    *,
    lam_min: float = 0.05,
    lam_max: float = 100.0,
    n_nodes: int = 1281,
) -> tuple[float, float]:
    """Return (log-Lebesgue measure, fraction of [ln lam_min, ln lam_max]).

    Each geomspace node is assigned the Voronoi width in ``log λ``, clipped
    to the declared interval. This is a quadrature of an indicator, not a
    count of inverted grid points.
    """
    if n_nodes < 2:
        raise ValueError("n_nodes must be at least 2")
    if not (lam_min > 0.0 and lam_max > lam_min):
        raise ValueError("need 0 < lam_min < lam_max")
    ratio = (lam_max / lam_min) ** (1.0 / (n_nodes - 1))
    log_min = math.log(lam_min)
    log_max = math.log(lam_max)
    log_span = log_max - log_min
    half = 0.5 * math.log(ratio)
    measure = 0.0
    for index in range(n_nodes):
        value = lam_min * (ratio**index)
        if not linear_vp_inversion([float(value)], solver_name, nfe):
            continue
        left = log_min if index == 0 else math.log(value) - half
        right = log_max if index == n_nodes - 1 else math.log(value) + half
        measure += right - left
    return measure, measure / log_span


def vp_never_changes_sign(eigenvalue: float, n_times: int = 401) -> bool:
    """Return True if a_VP does not change sign on a uniform grid."""
    if eigenvalue == 1.0:
        return True
    sign = math.copysign(1.0, eigenvalue - 1.0)
    for index in range(n_times):
        time = index / (n_times - 1)
        drift = scalar_drift("variance_preserving", eigenvalue, time)
        if time in {0.0, 1.0}:
            continue
        if math.copysign(1.0, drift) != sign:
            return False
    return True
