"""Unit tests for registered nested correlation analysis."""

from __future__ import annotations

import numpy as np

from fewstep_regularities.analysis.correlation import (
    paired_bootstrap_improvement,
)
from fewstep_regularities.experiments.gate_analysis import (
    _aggregate_configurations,
    _geometry_explanation,
    _inversion_table,
)


def test_configuration_aggregation_keeps_seeds_nested() -> None:
    observations = []
    for seed, error in [(0, 1.0), (1, 3.0)]:
        observations.append(
            {
                "target_family": "two_mode_gmm",
                "path": "linear",
                "solver": "euler",
                "dim": 2,
                "nfe": 8,
                "seed": seed,
                "error": error,
                "evaluator_is_exact": False,
                "evaluator_budget": 64,
                "metric_name": "averaged_squared_lipschitz_proxy",
                "metric_value": error + 1.0,
                "metric_estimator_budget": 128,
            }
        )
    rows = _aggregate_configurations(
        observations,
        metric_budget=128,
        projection_budget=64,
    )
    assert len(rows) == 1
    assert rows[0]["error"] == 2.0
    assert rows[0]["metric_value"] == 3.0
    assert rows[0]["n_nested_seeds"] == 2


def test_paired_bootstrap_detects_metric_improvement() -> None:
    outcome = np.asarray(
        [0.0, 1.0, 2.0, 3.0, 4.0, 5.0] * 2,
        dtype=np.float64,
    )
    baseline = np.ones(12, dtype=np.float64)
    alternative = outcome.copy()
    strata = ["family_a"] * 6 + ["family_b"] * 6
    result = paired_bootstrap_improvement(
        baseline,
        alternative,
        outcome,
        strata,
        n_bootstrap=500,
        seed=17,
    )
    assert result["improvement"] == 1.0
    assert float(result["ci_lower"]) > 0.0


def test_geometry_explanation_matches_family_types() -> None:
    gaussian = _geometry_explanation({"anisotropic_gaussian", "low_rank_gaussian"})
    mixed = _geometry_explanation({"anisotropic_gaussian", "two_mode_gmm"})
    mixtures = _geometry_explanation({"two_mode_gmm", "imbalanced_gmm"})
    assert "covariance spectra" in gaussian
    assert "state-dependent Jacobians" in mixed
    assert "responsibility gradients" in mixtures


def test_inversion_decision_excludes_uncalibrated_mixture_dimension() -> None:
    observations = []
    for dim in (2, 8):
        for seed in range(10):
            for path, metric, error in (
                ("linear", 2.0, 1.0),
                ("variance_preserving", 1.0, 2.0),
            ):
                for metric_budget in (32, 128):
                    for projection_budget in (32, 64, 128):
                        observations.append(
                            {
                                "target_family": "two_mode_gmm",
                                "path": path,
                                "solver": "heun",
                                "dim": dim,
                                "nfe": 8,
                                "seed": seed,
                                "metric_name": ("averaged_squared_lipschitz_proxy"),
                                "metric_value": metric,
                                "metric_estimator_budget": metric_budget,
                                "error": error,
                                "evaluator_budget": projection_budget,
                            }
                        )
    result = _inversion_table(
        observations,
        baseline="averaged_squared_lipschitz_proxy",
        calibration_ready_mixture_dimensions={2},
    )
    assert len(result["stable_blocks"]) == 2
    assert len(result["decision_blocks"]) == 1
    assert result["decision_blocks"][0]["dim"] == 2
