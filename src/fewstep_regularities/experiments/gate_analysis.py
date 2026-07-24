"""Registered analysis for the Phase 3 decision gate."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from numpy.typing import NDArray
from omegaconf import DictConfig, OmegaConf
from scipy.stats import rankdata

from fewstep_regularities.analysis.correlation import (
    paired_bootstrap_improvement,
    spearman_correlation,
)
from fewstep_regularities.artifacts.manifest import ArtifactRecord, RunManifest
from fewstep_regularities.artifacts.writer import FilesystemArtifactWriter
from fewstep_regularities.utils.environment import (
    cuda_version,
    git_code_status,
    git_commit,
    gpu_name,
    package_lock_hash,
    python_version,
    software_environment_hash,
)
from fewstep_regularities.utils.hashing import sha256_file, sha256_text

ConfigKey = tuple[str, str, str, int, int]


def _repo_root(cfg: DictConfig) -> Path:
    configured = OmegaConf.select(cfg, "compute.repo_root")
    if configured:
        return Path(str(configured)).resolve()
    return Path(__file__).resolve().parents[3]


def _absolute(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return data


def _config_key(row: Mapping[str, Any]) -> ConfigKey:
    return (
        str(row["target_family"]),
        str(row["path"]),
        str(row["solver"]),
        int(row["dim"]),
        int(row["nfe"]),
    )


def _is_primary_error(row: Mapping[str, Any], projection_budget: int) -> bool:
    return bool(row["evaluator_is_exact"]) or int(row["evaluator_budget"]) == (
        projection_budget
    )


def _is_calibration_ready(
    row: Mapping[str, Any],
    mixture_dimensions: set[int],
) -> bool:
    return bool(row["evaluator_is_exact"]) or int(row["dim"]) in mixture_dimensions


def _aggregate_configurations(
    observations: list[dict[str, Any]],
    *,
    metric_budget: int,
    projection_budget: int,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[ConfigKey, str], list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        if int(row["metric_estimator_budget"]) != metric_budget and not bool(
            row["evaluator_is_exact"]
        ):
            continue
        if not _is_primary_error(row, projection_budget):
            continue
        grouped[(_config_key(row), str(row["metric_name"]))].append(row)
    output = []
    for (key, metric_name), rows in sorted(grouped.items()):
        output.append(
            {
                "target_family": key[0],
                "path": key[1],
                "solver": key[2],
                "dim": key[3],
                "nfe": key[4],
                "metric_name": metric_name,
                "metric_value": float(
                    median(float(row["metric_value"]) for row in rows)
                ),
                "error": float(median(float(row["error"]) for row in rows)),
                "n_nested_seeds": len({int(row["seed"]) for row in rows}),
            }
        )
    return output


def _rho(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    selected = list(rows)
    if len(selected) < 3:
        return {"rho": None, "n_sampling_units": len(selected)}
    predictor = np.asarray(
        [float(row["metric_value"]) for row in selected], dtype=np.float64
    )
    outcome = np.asarray([float(row["error"]) for row in selected], dtype=np.float64)
    return {
        "rho": spearman_correlation(predictor, outcome),
        "n_sampling_units": len(selected),
    }


def _stratified_correlations(
    configurations: list[dict[str, Any]],
    metrics: list[str],
) -> dict[str, Any]:
    output: dict[str, Any] = {
        "sampling_unit": ["target_family", "path", "solver", "dim", "nfe"],
        "global": [],
        "per_target_family": [],
        "per_solver": [],
        "leave_one_family_out": [],
    }
    families = sorted({str(row["target_family"]) for row in configurations})
    solvers = sorted({str(row["solver"]) for row in configurations})
    for metric in metrics:
        metric_rows = [
            row for row in configurations if str(row["metric_name"]) == metric
        ]
        output["global"].append({"metric_name": metric, **_rho(metric_rows)})
        for family in families:
            rows = [row for row in metric_rows if str(row["target_family"]) == family]
            output["per_target_family"].append(
                {"metric_name": metric, "target_family": family, **_rho(rows)}
            )
        for solver in solvers:
            rows = [row for row in metric_rows if str(row["solver"]) == solver]
            output["per_solver"].append(
                {"metric_name": metric, "solver": solver, **_rho(rows)}
            )
        for family in families:
            rows = [row for row in metric_rows if str(row["target_family"]) != family]
            output["leave_one_family_out"].append(
                {"metric_name": metric, "excluded_family": family, **_rho(rows)}
            )
    return output


def _aligned_metric_arrays(
    configurations: list[dict[str, Any]],
    baseline_name: str,
    alternative_name: str,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    list[str],
]:
    by_key: dict[ConfigKey, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in configurations:
        by_key[_config_key(row)][str(row["metric_name"])] = row
    baseline = []
    alternative = []
    outcome = []
    strata = []
    for key in sorted(by_key):
        metrics = by_key[key]
        if baseline_name not in metrics or alternative_name not in metrics:
            continue
        baseline.append(float(metrics[baseline_name]["metric_value"]))
        alternative.append(float(metrics[alternative_name]["metric_value"]))
        outcome.append(float(metrics[baseline_name]["error"]))
        strata.append(key[0])
    return (
        np.asarray(baseline, dtype=np.float64),
        np.asarray(alternative, dtype=np.float64),
        np.asarray(outcome, dtype=np.float64),
        strata,
    )


def _bootstrap_table(
    configurations: list[dict[str, Any]],
    *,
    baseline: str,
    alternatives: list[str],
    n_bootstrap: int,
    seed: int,
) -> list[dict[str, Any]]:
    rows = []
    for index, alternative in enumerate(alternatives):
        base, alt, outcome, strata = _aligned_metric_arrays(
            configurations, baseline, alternative
        )
        result = paired_bootstrap_improvement(
            base,
            alt,
            outcome,
            strata,
            n_bootstrap=n_bootstrap,
            seed=seed + index,
        )
        rows.append(
            {
                "baseline_metric": baseline,
                "alternative_metric": alternative,
                "sampling_unit": [
                    "target_family",
                    "path",
                    "solver",
                    "dim",
                    "nfe",
                ],
                "stratification": "target_family",
                **result,
            }
        )
    return rows


def _residual_table(
    configurations: list[dict[str, Any]],
    *,
    baseline: str,
    alternatives: list[str],
) -> list[dict[str, Any]]:
    rows = []
    for alternative in alternatives:
        base, alt, outcome, _ = _aligned_metric_arrays(
            configurations, baseline, alternative
        )
        base_rank = np.asarray(rankdata(base), dtype=np.float64)
        alt_rank = np.asarray(rankdata(alt), dtype=np.float64)
        outcome_rank = np.asarray(rankdata(outcome), dtype=np.float64)
        design = np.column_stack((np.ones(base_rank.size, dtype=np.float64), base_rank))
        coefficients, _, _, _ = np.linalg.lstsq(design, outcome_rank, rcond=None)
        residual = outcome_rank - design @ coefficients
        rows.append(
            {
                "alternative_metric": alternative,
                "residual_spearman": spearman_correlation(alt_rank, residual),
                "n_sampling_units": int(base.size),
                "residual_definition": (
                    "outcome ranks minus least-squares fit on baseline ranks"
                ),
            }
        )
    return rows


def _sensitivity_table(
    observations: list[dict[str, Any]],
    *,
    metrics: list[str],
    metric_budgets: list[int],
    projection_budgets: list[int],
) -> list[dict[str, Any]]:
    output = []
    for metric_budget in metric_budgets:
        for projection_budget in projection_budgets:
            configurations = _aggregate_configurations(
                observations,
                metric_budget=metric_budget,
                projection_budget=projection_budget,
            )
            for metric in metrics:
                rows = [
                    row for row in configurations if str(row["metric_name"]) == metric
                ]
                output.append(
                    {
                        "metric_name": metric,
                        "metric_estimator_budget": metric_budget,
                        "projection_budget": projection_budget,
                        "stratum": "global",
                        "value": "all",
                        **_rho(rows),
                    }
                )
                for field in ("target_family", "solver", "dim", "nfe"):
                    values = sorted({row[field] for row in rows}, key=str)
                    for value in values:
                        subset = [row for row in rows if row[field] == value]
                        output.append(
                            {
                                "metric_name": metric,
                                "metric_estimator_budget": metric_budget,
                                "projection_budget": projection_budget,
                                "stratum": field,
                                "value": value,
                                **_rho(subset),
                            }
                        )
    return output


def _path_pairs(
    rows: list[dict[str, Any]],
    value_name: str,
) -> dict[tuple[Any, ...], tuple[str, float, str, float]]:
    grouped: dict[tuple[Any, ...], dict[str, float]] = defaultdict(dict)
    for row in rows:
        key = (
            str(row["target_family"]),
            str(row["solver"]),
            int(row["dim"]),
            int(row["nfe"]),
            int(row["seed"]),
            int(row["metric_estimator_budget"]),
            int(row["evaluator_budget"]),
        )
        grouped[key][str(row["path"])] = float(row[value_name])
    output = {}
    for key, values in grouped.items():
        if len(values) != 2:
            continue
        names = sorted(values)
        output[key] = (names[0], values[names[0]], names[1], values[names[1]])
    return output


def _inversion_table(
    observations: list[dict[str, Any]],
    *,
    baseline: str,
    calibration_ready_mixture_dimensions: set[int],
) -> dict[str, Any]:
    rows = [row for row in observations if str(row["metric_name"]) == baseline]
    error_pairs = _path_pairs(rows, "error")
    metric_pairs = _path_pairs(rows, "metric_value")
    checks = []
    block_directions: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for key in sorted(set(error_pairs) & set(metric_pairs), key=str):
        path_a, error_a, path_b, error_b = error_pairs[key]
        _, metric_a, _, metric_b = metric_pairs[key]
        error_sign = int(np.sign(error_a - error_b))
        metric_sign = int(np.sign(metric_a - metric_b))
        inversion = error_sign != 0 and metric_sign != 0 and error_sign != metric_sign
        row = {
            "target_family": key[0],
            "solver": key[1],
            "dim": key[2],
            "nfe": key[3],
            "seed": key[4],
            "metric_estimator_budget": key[5],
            "projection_budget": key[6],
            "path_a": path_a,
            "path_b": path_b,
            "error_sign_a_minus_b": error_sign,
            "metric_sign_a_minus_b": metric_sign,
            "inversion": inversion,
        }
        checks.append(row)
        block_directions[(key[0], key[1], key[2], key[3])].append(row)

    stable_blocks = []
    for block, block_rows in sorted(block_directions.items(), key=str):
        budget_groups: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
        for row in block_rows:
            budget_groups[
                (
                    int(row["metric_estimator_budget"]),
                    int(row["projection_budget"]),
                )
            ].append(row)
        budget_stability = []
        direction_pairs = []
        for budgets, budget_rows in sorted(budget_groups.items()):
            seeds = {int(row["seed"]) for row in budget_rows}
            required = 1 if seeds == {-1} else 8
            counter = Counter(
                (
                    int(row["metric_sign_a_minus_b"]),
                    int(row["error_sign_a_minus_b"]),
                )
                for row in budget_rows
                if bool(row["inversion"])
            )
            direction, count = counter.most_common(1)[0] if counter else ((0, 0), 0)
            stable = count >= required
            budget_stability.append(
                {
                    "metric_estimator_budget": budgets[0],
                    "projection_budget": budgets[1],
                    "stable": stable,
                    "count": count,
                    "required": required,
                    "direction": list(direction),
                }
            )
            if stable:
                direction_pairs.append(direction)
        all_stable = bool(budget_stability) and all(
            bool(row["stable"]) for row in budget_stability
        )
        same_direction = len(set(direction_pairs)) == 1 if direction_pairs else False
        if all_stable and same_direction:
            stable_blocks.append(
                {
                    "target_family": block[0],
                    "solver": block[1],
                    "dim": block[2],
                    "nfe": block[3],
                    "stable_across_seeds_and_estimators": True,
                    "direction": list(direction_pairs[0]),
                    "budget_checks": budget_stability,
                }
            )
    for row in stable_blocks:
        is_mixture = "gmm" in str(row["target_family"])
        row["calibration_ready"] = (
            not is_mixture or int(row["dim"]) in calibration_ready_mixture_dimensions
        )
    decision_blocks = [row for row in stable_blocks if bool(row["calibration_ready"])]
    families = sorted({str(row["target_family"]) for row in decision_blocks})
    return {
        "sampling_unit": ["target_family", "solver", "dim", "nfe"],
        "checks": checks,
        "stable_blocks": stable_blocks,
        "decision_blocks": decision_blocks,
        "reproducible_families": families,
        "condition_2_holds": len(families) >= 2,
    }


def _preferred_path(
    rows: list[dict[str, Any]],
) -> str | None:
    by_path: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_path[str(row["path"])].append(float(row["error"]))
    if len(by_path) != 2:
        return None
    medians = {name: median(values) for name, values in by_path.items()}
    names = sorted(medians)
    if medians[names[0]] == medians[names[1]]:
        return None
    return min(medians, key=lambda name: medians[name])


def _geometry_explanation(families: set[str]) -> str:
    has_mixture = any("gmm" in family for family in families)
    has_gaussian = any("gaussian" in family for family in families)
    if has_mixture and has_gaussian:
        return (
            "Gaussian fields are affine, while mixture fields have "
            "state-dependent Jacobians from changing responsibilities."
        )
    if has_mixture:
        return (
            "Mixture separation and weights change the responsibility gradients "
            "in the state-dependent field Jacobian."
        )
    return (
        "Gaussian covariance spectra change the affine field Jacobian and the "
        "solver truncation terms."
    )


def _interaction_table(
    observations: list[dict[str, Any]],
    *,
    projection_budget: int,
    calibration_ready_mixture_dimensions: set[int],
) -> dict[str, Any]:
    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in observations:
        if str(row["metric_name"]) != "averaged_squared_lipschitz_proxy":
            continue
        if int(row["metric_estimator_budget"]) != 128:
            continue
        if not _is_primary_error(row, projection_budget):
            continue
        if (
            "gmm" in str(row["target_family"])
            and int(row["dim"]) not in calibration_ready_mixture_dimensions
        ):
            continue
        unique_key = (
            str(row["target_family"]),
            str(row["path"]),
            str(row["solver"]),
            int(row["dim"]),
            int(row["nfe"]),
            int(row["seed"]),
        )
        unique[unique_key] = row
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in unique.values():
        group_key = (
            str(row["target_family"]),
            int(row["dim"]),
            int(row["nfe"]),
            int(row["seed"]),
            str(row["solver"]),
        )
        grouped[group_key].append(row)

    patterns: dict[tuple[str, int, int], list[dict[str, Any]]] = defaultdict(list)
    for group_key, rows in grouped.items():
        preferred = _preferred_path(rows)
        if preferred is not None:
            patterns[(group_key[0], group_key[1], group_key[2])].append(
                {
                    "seed": group_key[3],
                    "solver": group_key[4],
                    "preferred_path": preferred,
                }
            )

    candidates = []
    for block, pattern_rows in sorted(patterns.items(), key=str):
        by_seed: dict[int, dict[str, str]] = defaultdict(dict)
        for row in pattern_rows:
            by_seed[int(row["seed"])][str(row["solver"])] = str(row["preferred_path"])
        counter: Counter[tuple[tuple[str, str], ...]] = Counter()
        for values in by_seed.values():
            if len(values) == 3 and len(set(values.values())) > 1:
                counter[tuple(sorted(values.items()))] += 1
        if not counter:
            continue
        pattern, count = counter.most_common(1)[0]
        required = 1 if set(by_seed) == {-1} else 8
        stable = count >= required
        pattern_dict = dict(pattern)
        explained = (
            stable
            and pattern_dict.get("heun") == pattern_dict.get("rk4")
            and pattern_dict.get("euler") != pattern_dict.get("heun")
        )
        candidates.append(
            {
                "target_family": block[0],
                "dim": block[1],
                "nfe": block[2],
                "pattern": pattern_dict,
                "count": count,
                "required": required,
                "stable_across_seeds": stable,
                "plausible_mathematical_explanation": (
                    "Euler and the two higher-order methods have different "
                    "leading local truncation terms. Euler retains the first "
                    "material-derivative error term that the higher-order "
                    "methods cancel."
                    if explained
                    else None
                ),
                "usable_for_condition_3": explained,
            }
        )
    geometry_groups: dict[tuple[str, str, int, int], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for row in unique.values():
        geometry_key = (
            str(row["target_family"]),
            str(row["solver"]),
            int(row["dim"]),
            int(row["nfe"]),
        )
        geometry_groups[geometry_key].append(row)
    family_preferences: dict[tuple[str, int, int], list[dict[str, Any]]] = defaultdict(
        list
    )
    for geometry_key, geometry_rows in geometry_groups.items():
        geometry_by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in geometry_rows:
            geometry_by_seed[int(row["seed"])].append(row)
        geometry_preferences = [
            path_preference
            for seed_rows in geometry_by_seed.values()
            if (path_preference := _preferred_path(seed_rows)) is not None
        ]
        preference_counts: Counter[str] = Counter(geometry_preferences)
        family_preference, preference_count = (
            preference_counts.most_common(1)[0] if preference_counts else ("", 0)
        )
        geometry_required = 1 if set(geometry_by_seed) == {-1} else 8
        family_preferences[(geometry_key[1], geometry_key[2], geometry_key[3])].append(
            {
                "target_family": geometry_key[0],
                "preferred_path": family_preference,
                "count": preference_count,
                "required": geometry_required,
                "stable_across_seeds": preference_count >= geometry_required,
            }
        )

    geometry_candidates = []
    for geometry_block, preference_rows in sorted(family_preferences.items(), key=str):
        stable_preferences = [
            row for row in preference_rows if bool(row["stable_across_seeds"])
        ]
        stable_families = {str(row["target_family"]) for row in stable_preferences}
        geometry_paths = {str(row["preferred_path"]) for row in stable_preferences}
        usable_geometry = len(stable_preferences) >= 2 and len(geometry_paths) >= 2
        if len(geometry_paths) < 2:
            continue
        geometry_candidates.append(
            {
                "solver": geometry_block[0],
                "dim": geometry_block[1],
                "nfe": geometry_block[2],
                "family_preferences": stable_preferences,
                "stable_across_seeds": len(stable_preferences) >= 2,
                "plausible_mathematical_explanation": (
                    _geometry_explanation(stable_families) if usable_geometry else None
                ),
                "usable_for_condition_3": usable_geometry,
            }
        )

    usable = [row for row in candidates if bool(row["usable_for_condition_3"])]
    usable.extend(
        row for row in geometry_candidates if bool(row["usable_for_condition_3"])
    )
    return {
        "schedule_by_solver": candidates,
        "schedule_by_geometry": geometry_candidates,
        "condition_3_holds": bool(usable),
        "condition_3_evidence": usable,
    }


def _record(
    *,
    artifact_id: str,
    run_id: str,
    git: str,
    config_hash: str,
    code_status: str,
    env_hash: str,
    seeds: list[int],
    path: Path,
    timestamp: str,
    input_hashes: dict[str, str],
) -> ArtifactRecord:
    return ArtifactRecord(
        artifact_id=artifact_id,
        producing_run_id=run_id,
        git_commit=git,
        config_hash=config_hash,
        code_status=code_status,
        input_artifact_hashes=input_hashes,
        creation_timestamp=timestamp,
        software_environment_hash=env_hash,
        random_seeds=seeds,
        output_checksum="",
        path=str(path),
        kind="table",
    )


def run_gate_analysis(cfg: DictConfig) -> Path:
    """Run the frozen nested analysis on exact registered input artifacts."""
    start = datetime.now(UTC)
    root = _repo_root(cfg)
    analysis_path = _absolute(root, str(cfg.experiment.analysis_config))
    analysis_cfg = OmegaConf.load(analysis_path)
    if str(analysis_cfg.gate_version) != str(cfg.experiment.gate_version):
        raise ValueError("Analysis and experiment gate versions differ")
    gate_path = _absolute(root, str(analysis_cfg.inputs.gate_results.path))
    calibration_path = _absolute(root, str(analysis_cfg.inputs.calibration.path))
    gate_data = _load_json(gate_path)
    _load_json(calibration_path)
    estimator_audit_path: Path | None = None
    if "estimator_audit" in analysis_cfg.inputs:
        estimator_audit_path = _absolute(
            root, str(analysis_cfg.inputs.estimator_audit.path)
        )
        _load_json(estimator_audit_path)
    observations_value = gate_data.get("observations")
    if not isinstance(observations_value, list) or not observations_value:
        raise ValueError("Gate artifact has no observations")
    observations = []
    for row in observations_value:
        if not isinstance(row, dict):
            raise TypeError("Each gate observation must be an object")
        observations.append(row)

    baseline = str(analysis_cfg.primary_metric)
    alternatives = [str(value) for value in analysis_cfg.alternative_metrics]
    metrics = [baseline, *alternatives]
    metric_budget = int(analysis_cfg.primary_metric_estimator_budget)
    projection_budget = int(
        OmegaConf.select(analysis_cfg, "primary_projection_budget", default=64)
    )
    calibration_ready_mixture_dimensions = {
        int(value)
        for value in OmegaConf.select(
            analysis_cfg,
            "calibration_ready_mixture_dimensions",
            default=[2],
        )
    }
    decision_observations = [
        row
        for row in observations
        if _is_calibration_ready(row, calibration_ready_mixture_dimensions)
    ]
    configurations = _aggregate_configurations(
        decision_observations,
        metric_budget=metric_budget,
        projection_budget=projection_budget,
    )
    correlations = _stratified_correlations(configurations, metrics)
    correlations["analysis_scope"] = {
        "included_observations": len(decision_observations),
        "excluded_uncalibrated_observations": (
            len(observations) - len(decision_observations)
        ),
        "calibration_ready_mixture_dimensions": sorted(
            calibration_ready_mixture_dimensions
        ),
    }
    correlations["paired_bootstrap"] = _bootstrap_table(
        configurations,
        baseline=baseline,
        alternatives=alternatives,
        n_bootstrap=int(analysis_cfg.bootstrap_replicates),
        seed=int(analysis_cfg.bootstrap_seed),
    )
    correlations["residual_analysis"] = _residual_table(
        configurations,
        baseline=baseline,
        alternatives=alternatives,
    )
    sensitivity = {
        "sampling_unit": ["target_family", "path", "solver", "dim", "nfe"],
        "rows": _sensitivity_table(
            decision_observations,
            metrics=metrics,
            metric_budgets=[32, 128],
            projection_budgets=[32, 64, 128],
        ),
    }
    inversions = _inversion_table(
        decision_observations,
        baseline=baseline,
        calibration_ready_mixture_dimensions=calibration_ready_mixture_dimensions,
    )
    interactions = _interaction_table(
        decision_observations,
        projection_budget=projection_budget,
        calibration_ready_mixture_dimensions=calibration_ready_mixture_dimensions,
    )
    condition_1_rows = [
        row
        for row in correlations["paired_bootstrap"]
        if float(row["improvement"]) >= 0.15 and float(row["ci_lower"]) > 0.0
    ]
    conditions = {
        "condition_1": {
            "holds": bool(condition_1_rows),
            "evidence": condition_1_rows,
        },
        "condition_2": {
            "holds": bool(inversions["condition_2_holds"]),
            "evidence": inversions["decision_blocks"],
        },
        "condition_3": {
            "holds": bool(interactions["condition_3_holds"]),
            "evidence": interactions["condition_3_evidence"],
        },
        "condition_4": {
            "holds": False,
            "evidence": [],
            "reason": "No proposition was proposed in the Phase 3 gate.",
        },
    }
    decision = {
        "gate_version": str(cfg.experiment.gate_version),
        "sampling_unit": ["target_family", "path", "solver", "dim", "nfe"],
        "conditions": conditions,
        "continue": any(bool(value["holds"]) for value in conditions.values()),
        "recommendation": (
            "continue_to_phase4_review_only"
            if bool(inversions["condition_2_holds"])
            else "pivot_and_stop"
        ),
        "pivot_checks": {
            "random_seed_variation": {
                "status": "applies_to_rejected_candidates_only",
                "applies_to_gate_decision": False,
                "note": (
                    "Several mixture interactions fail the ten-seed rule. "
                    "The surviving condition 2 blocks pass it."
                ),
            },
            "wasserstein_estimator_instability": {
                "status": "applies_to_dimension_8_mixture_evidence",
                "applies_to_gate_decision": False,
                "note": (
                    "Dimension 8 fails the post-result calibration diagnostic and "
                    "is excluded from decision evidence. Dimension 2 mixture and "
                    "exact Gaussian evidence remain."
                ),
            },
            "endpoint_singularities": {
                "status": "does_not_apply",
                "applies_to_gate_decision": False,
                "note": "Only linear and regular trigonometric paths were used.",
            },
            "numerical_precision": {
                "status": "not_assessed_beyond_float64",
                "applies_to_gate_decision": None,
                "note": "The gate used float64. Higher precision was not run.",
            },
            "unequal_evaluation_budgets": {
                "status": "does_not_apply",
                "applies_to_gate_decision": False,
                "note": "Every observation records actual NFE equal to requested NFE.",
            },
            "implementation_error": {
                "status": "applied_to_superseded_analysis_outputs",
                "applies_to_gate_decision": False,
                "note": (
                    "Earlier analysis outputs had reporting defects. "
                    "This analysis uses the same immutable main artifact."
                ),
            },
            "previously_published_result": {
                "status": "not_fully_assessed",
                "applies_to_gate_decision": None,
                "note": (
                    "The source paper covers schedule effects for Euler and RK4, "
                    "but not this registered inversion table."
                ),
            },
            "disappears_with_higher_order_solver": {
                "status": "applies_to_condition_3_euler_effect",
                "applies_to_gate_decision": False,
                "note": (
                    "The low-rank Gaussian path preference changes from Euler "
                    "to Heun and RK4. Condition 2 remains."
                ),
            },
        },
    }

    run_id = str(cfg.experiment.run_id)
    output_dir = Path(str(cfg.artifact_policy.output_dir))
    if not output_dir.is_absolute():
        output_dir = (root / output_dir).resolve()
    run_dir = output_dir / run_id
    if (run_dir / "manifest.json").exists():
        raise FileExistsError(f"Refusing to overwrite completed analysis {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    unresolved_path = run_dir / "unresolved_config.yaml"
    resolved_path = run_dir / "resolved_config.yaml"
    resolved_analysis_path = run_dir / "resolved_analysis_config.yaml"
    unresolved_path.write_text(OmegaConf.to_yaml(cfg, resolve=False), encoding="utf-8")
    resolved_text = OmegaConf.to_yaml(cfg, resolve=True)
    resolved_path.write_text(resolved_text, encoding="utf-8")
    resolved_analysis_text = OmegaConf.to_yaml(analysis_cfg, resolve=True)
    resolved_analysis_path.write_text(resolved_analysis_text, encoding="utf-8")
    analysis_config_hash = sha256_text(resolved_analysis_text)
    config_hash = sha256_text(resolved_text + resolved_analysis_text)
    git = git_commit(root)
    status = git_code_status(root)
    env_hash = software_environment_hash()
    seeds = [int(value) for value in cfg.experiment.seeds]
    stamp = datetime.now(UTC).isoformat()
    input_hashes = {
        str(analysis_cfg.inputs.gate_results.artifact_id): sha256_file(gate_path),
        str(analysis_cfg.inputs.calibration.artifact_id): sha256_file(calibration_path),
    }
    if estimator_audit_path is not None:
        input_hashes[str(analysis_cfg.inputs.estimator_audit.artifact_id)] = (
            sha256_file(estimator_audit_path)
        )
    payloads: dict[str, Mapping[str, Any]] = {
        "correlation_table": correlations,
        "sensitivity_table": sensitivity,
        "inversion_table": inversions,
        "interaction_table": interactions,
        "decision_table": decision,
    }
    writer = FilesystemArtifactWriter()
    saved = []
    for output_name, payload in payloads.items():
        output_cfg = analysis_cfg.outputs[output_name]
        path = _absolute(root, str(output_cfg.path))
        if path.parent != run_dir:
            raise ValueError("Analysis outputs must be inside the run directory")
        record = _record(
            artifact_id=str(output_cfg.artifact_id),
            run_id=run_id,
            git=git,
            config_hash=config_hash,
            code_status=status,
            env_hash=env_hash,
            seeds=seeds,
            path=path,
            timestamp=stamp,
            input_hashes=input_hashes,
        )
        saved.append(writer.save_table(payload, path, record).to_dict())

    end = datetime.now(UTC)
    manifest = RunManifest(
        run_id=run_id,
        git_commit=git,
        config_hash=config_hash,
        code_status=status,
        software_environment_hash=env_hash,
        random_seeds=seeds,
        start_time=start.isoformat(),
        end_time=end.isoformat(),
        runtime_s=(end - start).total_seconds(),
        artifact_manifest=saved,
        resolved_config_path=str(resolved_path),
        unresolved_config_path=str(unresolved_path),
        command_line=" ".join(sys.argv),
        python_version=python_version(),
        package_lock_hash=package_lock_hash(root),
        cuda_version=cuda_version(),
        gpu_name=gpu_name(),
        release_ready=bool(cfg.artifact_policy.release_ready),
        extras={
            "mode": "gate_analysis",
            "phase": 3,
            "gate_version": str(cfg.experiment.gate_version),
            "analysis_config": str(analysis_path),
            "resolved_analysis_config_path": str(resolved_analysis_path),
            "analysis_config_hash": analysis_config_hash,
            "input_artifacts": input_hashes,
        },
    )
    manifest_path = run_dir / "manifest.json"
    writer.save_manifest(manifest, manifest_path)
    return manifest_path
