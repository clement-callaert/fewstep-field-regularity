"""Deterministic ranking grids for linear, VP, and log-covariance paths."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from fewstep_regularities.analysis.affine_flow import scalar_drift
from fewstep_regularities.analysis.continuous_regularity import continuous_regularity
from fewstep_regularities.analysis.local_error import propagate_scalar_mode

PATHS = ("linear", "variance_preserving", "log_covariance")
SOLVERS = ("euler", "heun", "rk4")
PRIMARY_NFE = (8, 16, 32)
HEUN_BUDGETS = (4, 8, 12, 16, 24, 32, 64, 128, 256)


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


def path_regularity(path_name: str, eigenvalues: Sequence[float]) -> float:
    """Return continuous spectral R, with a closed form for log-covariance."""
    if path_name == "log_covariance":
        return max(0.5 * abs(math.log(float(value))) for value in eigenvalues) ** 2
    value, _error = continuous_regularity(path_name, eigenvalues)
    return value


def path_w2(
    path_name: str,
    solver_name: str,
    eigenvalues: Sequence[float],
    nfe: int,
) -> float:
    """Return centered Gaussian W2 from exact-moment modal factors."""
    factors = [
        propagate_scalar_mode(path_name, solver_name, float(value), nfe).factor
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
