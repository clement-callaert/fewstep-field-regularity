"""Build compact machine-readable artifacts for the arXiv manuscript."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import mpmath as mp
import torch

from fewstep_regularities.analysis.continuous_regularity import regularity_report
from fewstep_regularities.analysis.ranking_grids import family_display_label
from fewstep_regularities.analysis.scalar_gaussian_counterexample import (
    EXACT_ENDPOINT_FACTOR,
    LINEAR_HEUN_FACTOR,
    certify,
    float64_crosscheck,
    high_precision_crosscheck,
    linear_heun_step_factors,
    linear_regularity,
    machin_pi_upper_bound,
    mpmath_version,
    sqrt2_upper_integer_certificate,
    vp_heun_product_records,
    vp_regularity,
)
from fewstep_regularities.distributions.gaussian import (
    anisotropic_gaussian,
    low_rank_gaussian,
)
from fewstep_regularities.experiments.workshop_external_validation import (
    frozen_source_mean,
    frozen_target_eigenvalues,
    frozen_target_mean,
)
from fewstep_regularities.utils.hashing import sha256_file, write_compact_manifest
from fewstep_regularities.utils.provenance import source_state

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "arxiv" / "artifacts"
GEN = ROOT / "paper" / "arxiv" / "generated"
FROZEN = ROOT / "paper" / "arxiv" / "frozen_runs"

PINNED = {
    "phase4_gaussian_reproduction_2026-07-24-v1:results": (
        FROZEN / "phase4_gaussian_reproduction_2026-07-24-v1/results.json",
        "b8930142cba5655ee553aae5ff400cd884c1137e77547d9a5fa94bd4e354973f",
    ),
    "phase4_precision_2026-07-24-v1:table": (
        FROZEN / "phase4_precision_2026-07-24-v1/table.json",
        "5f8800a697c61c2eab2306281fe4fb1b01dee67bc3c678dd7ba4a626d9dc8e1b",
    ),
    "workshop_external_validation_2026-07-24-v1:results": (
        FROZEN / "workshop_external_validation_2026-07-24-v1/results.json",
        "4234bc2baefa8390414db9e037c7d028408cb04591e2b6302524ed8ad3bd205d",
    ),
    "workshop_external_validation_2026-07-24-v1:inversions": (
        FROZEN / "workshop_external_validation_2026-07-24-v1/inversions.json",
        "cceebdfcba6f7cec4a7ff9e137d4a53f8c7e389acc0222a20805f16204a1b875",
    ),
}
ROBUSTNESS_PIN = (
    "phase4_robustness_2026-07-24-v1:table",
    "3cace6e3d016f0c3e893a656fb76acfad11ce4569debc6ea418fe5aeec7d6306",
)

RELEASE_TAG = "arxiv-v1"
RELEASE_URL = (
    "https://github.com/clement-callaert/fewstep-field-regularity/releases/tag/"
    + RELEASE_TAG
)
GEOMETRY_SEED = 271828
# Published 12-decimal targets for the non-centered spectral pair.
# Absolute tolerance 1e-12 is one unit in the last displayed digit.
NONCENTERED_R_TARGETS = {
    "linear_R": 1.093536901895,
    "linear_R24": 1.093850806380,
    "vp_R": 0.342354218861,
    "vp_R24": 0.342535902815,
}
NONCENTERED_R_TOL = 1.0e-12


def load_pinned(artifact_id: str) -> dict:
    path, expected = PINNED[artifact_id]
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(f"Checksum mismatch for {artifact_id}: {actual}")
    return json.loads(path.read_text(encoding="utf-8"))


def sci_tex(value: float, digits: int = 10) -> str:
    mantissa, exp = f"{value:.{digits}e}".split("e")
    return rf"{mantissa}\times 10^{{{int(exp)}}}"


def low_rank_geometry(dim: int) -> dict:
    generator = torch.Generator().manual_seed(GEOMETRY_SEED)
    gaussian = low_rank_gaussian(
        dim, rank=2, noise_variance=0.05, dtype=torch.float64, generator=generator
    )
    cov = gaussian.covariance()
    eigs = torch.linalg.eigvalsh(cov)
    return {
        "dim": dim,
        "rank": 2,
        "noise_variance": 0.05,
        "seed": GEOMETRY_SEED,
        "covariance": cov.tolist(),
        "eigenvalues": [float(v) for v in eigs.tolist()],
    }


def anisotropic_geometry(dim: int, anisotropy: float = 4.0) -> dict:
    cov = anisotropic_gaussian(
        dim, anisotropy=anisotropy, dtype=torch.float64
    ).covariance()
    eigs = torch.linalg.eigvalsh(cov)
    return {
        "dim": dim,
        "anisotropy": anisotropy,
        "eigenvalues": [float(v) for v in eigs.tolist()],
    }


def path_regularity(eigs: list[float]) -> dict:
    return {
        "linear": regularity_report("linear", eigs),
        "variance_preserving": regularity_report("variance_preserving", eigs),
    }


def write_json(path: Path, payload: dict) -> str:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return sha256_file(path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    GEN.mkdir(parents=True, exist_ok=True)

    certified = certify(dps=40)
    hp = high_precision_crosscheck(dps=80)
    f64 = float64_crosscheck()
    steps = [str(factor) for factor in linear_heun_step_factors()]
    bound = certified.vp_rational_upper
    int_left, int_right = certified.vp_integer_left, certified.vp_integer_right
    sqrt2_left, sqrt2_right = sqrt2_upper_integer_certificate()
    scalar = {
        "lambda": 4,
        "nfe": 8,
        "n_steps": 4,
        "evals_per_step": 2,
        "step_size": "1/4",
        "exact_endpoint_factor": EXACT_ENDPOINT_FACTOR,
        "R_linear": linear_regularity(),
        "R_linear_closed_form": "5*pi/8 - 1",
        "R_vp": vp_regularity(),
        "R_vp_closed_form": "pi^2/16",
        "heun_linear_steps": steps,
        "r_linear": str(LINEAR_HEUN_FACTOR),
        "W2_linear": str(certified.linear_w2),
        "W2_linear_float": float(certified.linear_w2),
        "r_vp_rational_upper": str(bound),
        "r_vp_rational_upper_float": float(bound),
        "r_vp_integer_certificate": {
            "left": int_left,
            "right": int_right,
            "comparison": "100 * numerator < 187 * denominator",
            "implies": "r_VP < 187/100",
        },
        "vp_heun_product_poly": vp_heun_product_records(),
        "sqrt2_upper": "99/70",
        "sqrt2_integer_certificate": {"left": sqrt2_left, "right": sqrt2_right},
        "pi_upper": "355/113",
        "machin_pi_upper": str(machin_pi_upper_bound()),
        "r_vp_interval_crosscheck": list(certified.vp_factor_interval),
        "W2_vp_interval_crosscheck": list(certified.vp_w2_interval),
        "certified_inequality": "W2_lin < 0.091 < 0.130 < W2_vp",
        "ranking_inverted": certified.ranking_inverted,
        "all_heun_factors_positive": certified.all_heun_factors_positive,
        "float64": f64,
        "mpmath_80digit": hp,
        "software": certified.software,
        "mpmath_version": certified.mpmath_version,
        "interval_dps": certified.interval_dps,
        "experiment_code_commit": "e48c9390e62b38f206342e6aeb7f160122ccc79c",
        "planned_release_tag": RELEASE_TAG,
        "planned_release_url": RELEASE_URL,
    }
    scalar_sha = write_json(OUT / "scalar_counterexample.json", scalar)

    geometries = {
        "scalar_lambda4": {
            "eigenvalues": [4.0],
            "regularity": path_regularity([4.0]),
        },
        "anisotropic_d2": {
            **anisotropic_geometry(2),
            "regularity": path_regularity(anisotropic_geometry(2)["eigenvalues"]),
        },
        "anisotropic_d8": {
            **anisotropic_geometry(8),
            "regularity": path_regularity(anisotropic_geometry(8)["eigenvalues"]),
        },
        "low_rank_d2": {
            **low_rank_geometry(2),
            "regularity": path_regularity(low_rank_geometry(2)["eigenvalues"]),
        },
        "low_rank_d8": {
            **low_rank_geometry(8),
            "regularity": path_regularity(low_rank_geometry(8)["eigenvalues"]),
        },
        "shifted_anisotropic_d2": {
            "eigenvalues": [
                float(v)
                for v in frozen_target_eigenvalues(
                    2, torch.float64, torch.device("cpu")
                )
            ],
            "source_mean": [
                float(v)
                for v in frozen_source_mean(2, torch.float64, torch.device("cpu"))
            ],
            "target_mean": [
                float(v)
                for v in frozen_target_mean(2, torch.float64, torch.device("cpu"))
            ],
        },
        "shifted_anisotropic_d8": {
            "eigenvalues": [
                float(v)
                for v in frozen_target_eigenvalues(
                    8, torch.float64, torch.device("cpu")
                )
            ],
        },
    }
    for key in ("shifted_anisotropic_d2", "shifted_anisotropic_d8"):
        geometries[key]["regularity"] = path_regularity(geometries[key]["eigenvalues"])
    nc_lin = geometries["shifted_anisotropic_d2"]["regularity"]["linear"]
    nc_vp = geometries["shifted_anisotropic_d2"]["regularity"]["variance_preserving"]
    nc_values = {
        "linear_R": float(nc_lin["R"]),
        "linear_R24": float(nc_lin["R24"]),
        "vp_R": float(nc_vp["R"]),
        "vp_R24": float(nc_vp["R24"]),
    }
    for name, expected in NONCENTERED_R_TARGETS.items():
        actual = nc_values[name]
        if abs(actual - expected) > NONCENTERED_R_TOL:
            raise RuntimeError(
                f"non-centered {name}={actual:.15f} disagrees with target "
                f"{expected} (tol {NONCENTERED_R_TOL})"
            )
    d8_lin = geometries["shifted_anisotropic_d8"]["regularity"]["linear"]
    d8_vp = geometries["shifted_anisotropic_d8"]["regularity"]["variance_preserving"]
    if abs(float(d8_lin["R"]) - nc_values["linear_R"]) > NONCENTERED_R_TOL:
        raise RuntimeError("non-centered d=2 and d=8 linear R differ")
    if abs(float(d8_vp["R"]) - nc_values["vp_R"]) > NONCENTERED_R_TOL:
        raise RuntimeError("non-centered d=2 and d=8 VP R differ")
    geom_sha = write_json(OUT / "geometries.json", geometries)

    results = load_pinned("phase4_gaussian_reproduction_2026-07-24-v1:results")
    precision = load_pinned("phase4_precision_2026-07-24-v1:table")
    by_key: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for row in results["rows"]:
        key = (row["target_family"], int(row["dim"]), row["solver"], int(row["nfe"]))
        by_key[key][row["path"]] = row
    geom_map = {
        ("anisotropic_gaussian", 2): geometries["anisotropic_d2"],
        ("anisotropic_gaussian", 8): geometries["anisotropic_d8"],
        ("low_rank_gaussian", 2): geometries["low_rank_d2"],
        ("low_rank_gaussian", 8): geometries["low_rank_d8"],
    }
    blocks = []
    for key, paths in sorted(by_key.items()):
        family, dim, solver, nfe = key
        lin, vp = paths["linear"], paths["variance_preserving"]
        reg = geom_map[(family, dim)]["regularity"]
        r_lin = float(reg["linear"]["R"])
        r_vp = float(reg["variance_preserving"]["R"])
        r24_lin = float(lin["baseline_metric"])
        r24_vp = float(vp["baseline_metric"])
        d_r = r_lin - r_vp
        d_r24 = r24_lin - r24_vp
        d_w2 = float(lin["gaussian_w2"]) - float(vp["gaussian_w2"])
        blocks.append(
            {
                "family": family,
                "dim": dim,
                "solver": solver,
                "nfe": nfe,
                "R_linear": r_lin,
                "R_vp": r_vp,
                "R24_linear": r24_lin,
                "R24_vp": r24_vp,
                "W2_linear": float(lin["gaussian_w2"]),
                "W2_vp": float(vp["gaussian_w2"]),
                "inversion_R": d_r * d_w2 < 0,
                "inversion_R24": d_r24 * d_w2 < 0,
                "same_R_sign_as_R24": (d_r > 0) == (d_r24 > 0),
                "W2_margin": abs(d_w2),
                "R_prefers": "linear" if d_r < 0 else "VP",
                "W2_prefers": "linear" if d_w2 < 0 else "VP",
            }
        )
    n_inv_r = sum(1 for b in blocks if b["inversion_R"])
    n_inv_r24 = sum(1 for b in blocks if b["inversion_R24"])
    if len(results["rows"]) != 72 or len(blocks) != 36:
        raise RuntimeError("unexpected Phase 4 counts")
    if not all(b["same_R_sign_as_R24"] for b in blocks):
        raise RuntimeError("continuous R changed a path ordering")
    if n_inv_r != 14 or n_inv_r24 != 14:
        raise RuntimeError(f"unexpected inversion counts R={n_inv_r} R24={n_inv_r24}")

    centered = {
        "n_endpoint_configs": 72,
        "n_blocks": 36,
        "n_geometries": 4,
        "n_solver_budget_conditions": 9,
        "hierarchy": "4 geometries x 3 solvers x 3 NFE",
        "n_inversions_continuous_R": n_inv_r,
        "n_inversions_R24": n_inv_r24,
        "blocks": blocks,
    }
    centered_sha = write_json(OUT / "centered_blocks.json", centered)

    workshop = load_pinned("workshop_external_validation_2026-07-24-v1:results")
    w_inv = load_pinned("workshop_external_validation_2026-07-24-v1:inversions")
    w_by: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for row in workshop["rows"]:
        key = (int(row["dim"]), row["solver"], int(row["nfe"]))
        w_by[key][row["path"]] = row
    noncentered = []
    for key, paths in sorted(w_by.items()):
        dim, solver, nfe = key
        lin, vp = paths["linear"], paths["variance_preserving"]
        geom = geometries[
            "shifted_anisotropic_d2" if dim == 2 else "shifted_anisotropic_d8"
        ]
        r_lin = float(geom["regularity"]["linear"]["R"])
        r_vp = float(geom["regularity"]["variance_preserving"]["R"])

        def split(row: dict) -> dict:
            w2 = float(row["gaussian_w2"])
            mean_err = float(row["mean_error"])
            mean_sq = mean_err**2
            cov_sq = w2**2 - mean_sq
            return {
                "W2": w2,
                "mean_term_sq": mean_sq,
                "bures_term_sq": cov_sq,
                "mean_fraction_of_W2sq": mean_sq / w2**2 if w2 else 0.0,
            }

        sl, sv = split(lin), split(vp)
        d_r = r_lin - r_vp
        delta_mean = sl["mean_term_sq"] - sv["mean_term_sq"]
        delta_cov = sl["bures_term_sq"] - sv["bures_term_sq"]
        delta_total = delta_mean + delta_cov
        d_w2 = sl["W2"] - sv["W2"]
        if delta_mean * delta_total > 0 and abs(delta_mean) > abs(delta_cov):
            driver = "mean"
        elif delta_cov * delta_total > 0 and abs(delta_cov) > abs(delta_mean):
            driver = "covariance"
        else:
            driver = "mixed"
        noncentered.append(
            {
                "dim": dim,
                "solver": solver,
                "nfe": nfe,
                "R_linear": r_lin,
                "R_vp": r_vp,
                "linear": sl,
                "vp": sv,
                "delta_mean": delta_mean,
                "delta_cov": delta_cov,
                "delta_total": delta_total,
                "inversion_R": d_r * d_w2 < 0,
                "W2_prefers": "linear" if d_w2 < 0 else "VP",
                "primary_W2sq_driver": driver,
            }
        )
    n_w_inv = sum(1 for b in noncentered if b["inversion_R"])
    if len(noncentered) != 18 or n_w_inv != 11:
        raise RuntimeError("unexpected non-centered counts")
    if sum(1 for r in w_inv["rows"] if r["is_inversion"]) != 11:
        raise RuntimeError("frozen inversion table disagrees")
    non_sha = write_json(
        OUT / "noncentered_blocks.json",
        {
            "n_blocks": 18,
            "n_inversions_continuous_R": n_w_inv,
            "description": "pre-specified non-centered stress test; R ignores c(t)",
            "W2_source": "frozen outputs/workshop_external_validation_2026-07-24-v1",
            "R_source": "recomputed continuous regularity from frozen eigenvalues",
            "construction": {
                "dims": [2, 8],
                "index": "i = 0, ..., d-1",
                "mu0_i": "0.75 * (-1)^i",
                "mu1_i": "1 + 0.25 * i",
                "eigenvalues": "geometric from 6^{-1/2} to 6^{1/2}",
                "condition_number": 6,
                "solvers": ["euler", "heun", "rk4"],
                "nfe": [8, 16, 32],
                "nfe_accounting": "S = B/s with s=1,2,4; forward in t",
            },
            "driver_definition": {
                "M": "||hat m - mu_1||_2^2",
                "C": "W2^2 - M",
                "Delta_mean": "M_lin - M_VP",
                "Delta_cov": "C_lin - C_VP",
                "Delta_total": "Delta_mean + Delta_cov",
                "mean_driven": "Delta_mean * Delta_total > 0 and |Delta_mean| > |Delta_cov|",
                "covariance_driven": "Delta_cov * Delta_total > 0 and |Delta_cov| > |Delta_mean|",
            },
            "blocks": noncentered,
        },
    )

    robust_hydra = (
        ROOT / "outputs/phase4_robustness_2026-07-24-v1/table.json"
    )
    if robust_hydra.is_file():
        actual = sha256_file(robust_hydra)
        if actual != ROBUSTNESS_PIN[1]:
            raise ValueError(
                f"Checksum mismatch for {ROBUSTNESS_PIN[0]}: {actual}"
            )
        robust = json.loads(robust_hydra.read_text(encoding="utf-8"))
        lr_prefs = [
            row
            for row in robust["preferences"]
            if row["target_family"] == "low_rank_gaussian"
        ]
    else:
        existing = json.loads((OUT / "robustness_lowrank.json").read_text(encoding="utf-8"))
        lr_prefs = existing["blocks"]
        print(
            "using committed robustness_lowrank.json; raw Hydra table "
            "phase4_robustness_2026-07-24-v1 is not in the public snapshot"
        )
    formula = 2 * 3 * (3 * 3 + 2)
    if len(lr_prefs) != 66 or len(lr_prefs) != formula:
        raise RuntimeError(f"low-rank robustness count {len(lr_prefs)} != 66")
    pattern_ok = all(
        (
            row["preferred_path"] == "variance_preserving"
            if row["solver"] == "euler"
            else row["preferred_path"] == "linear"
        )
        for row in lr_prefs
    )
    robust_sha = write_json(
        OUT / "robustness_lowrank.json",
        {
            "n_blocks": 66,
            "formula": "2 dims x 3 solvers x (3 primary NFE x 3 perturbations + 2 extra NFE at 0 perturbation)",
            "perturbation": "multiplies low-rank noise_variance 0.05 by (1+delta); F is regenerated from the same seed",
            "extra_nfe_64_128": "unperturbed target only",
            "status": "post-hoc",
            "solver_path_pattern_holds": pattern_ok,
            "blocks": lr_prefs,
        },
    )

    max_delta = max(r["absolute_reference_delta"] for r in precision["rows"])
    inversions = [b for b in blocks if b["inversion_R"]]
    strongest = max(inversions, key=lambda b: b["W2_margin"])
    smallest = min(inversions, key=lambda b: b["W2_margin"])
    ratio = smallest["W2_margin"] / max_delta

    pinned_inputs = {key: value[1] for key, value in PINNED.items()}
    pinned_inputs[ROBUSTNESS_PIN[0]] = ROBUSTNESS_PIN[1]
    manifest = {
        "artifact_release_id": "arxiv-compact-2026-08-13-local",
        "experiment_code_commit": "e48c9390e62b38f206342e6aeb7f160122ccc79c",
        "compact_manifest_source_state": source_state(),
        "canonical_self_hash_rule": (
            "SHA-256 of compact JSON with files.manifest.json blanked; "
            "sorted keys, separators (',', ':')"
        ),
        "planned_release_tag": RELEASE_TAG,
        "planned_release_url": RELEASE_URL,
        "public_download": False,
        "files": {
            "scalar_counterexample.json": scalar_sha,
            "geometries.json": geom_sha,
            "centered_blocks.json": centered_sha,
            "noncentered_blocks.json": non_sha,
            "robustness_lowrank.json": robust_sha,
        },
        "pinned_inputs": pinned_inputs,
    }
    for extra_name in (
        "log_covariance_blocks.json",
        "inversion_region.json",
        "lowrank_seed_fraction.json",
        "grid_aware_robustness.json",
        "in_family_blocks.json",
    ):
        extra_path = OUT / extra_name
        if extra_path.is_file():
            manifest["files"][extra_name] = sha256_file(extra_path)
    write_compact_manifest(OUT / "manifest.json", manifest)

    with mp.workdps(40):
        vp_lo = mp.mpf(certified.vp_factor_interval[0])
        vp_hi = mp.mpf(certified.vp_factor_interval[1])
        display_lo = "1.8696263416613175"
        display_hi = "1.8696263416613176"
        if not (mp.mpf(display_lo) < vp_lo <= vp_hi < mp.mpf(display_hi)):
            raise RuntimeError(
                "VP factor interval moved outside the displayed enclosure"
            )
        w_lo = mp.mpf(certified.vp_w2_interval[0])
        w_hi = mp.mpf(certified.vp_w2_interval[1])
        w_display_lo = "0.1303736583"
        w_display_hi = "0.1303736584"
        if not (mp.mpf(w_display_lo) < w_lo <= w_hi < mp.mpf(w_display_hi)):
            raise RuntimeError("VP W2 interval moved outside the displayed enclosure")

    macros = [
        r"\newcommand{\arxivReleaseTag}{" + RELEASE_TAG + "}",
        r"\newcommand{\arxivReleaseURL}{" + RELEASE_URL + "}",
        rf"\newcommand{{\mpmathVersion}}{{{mpmath_version()}}}",
        r"\newcommand{\nConfigs}{72}",
        r"\newcommand{\nBlocks}{36}",
        r"\newcommand{\nGeometries}{4}",
        r"\newcommand{\nSolverBudgets}{9}",
        rf"\newcommand{{\nInversions}}{{{n_inv_r}}}",
        r"\newcommand{\nWorkshopBlocks}{18}",
        rf"\newcommand{{\nWorkshopInversions}}{{{n_w_inv}}}",
        r"\newcommand{\nRobustLowRank}{66}",
        rf"\newcommand{{\scalarRlin}}{{{linear_regularity():.16f}}}",
        rf"\newcommand{{\scalarRvp}}{{{vp_regularity():.16f}}}",
        r"\newcommand{\scalarRlinClosed}{5\pi/8-1}",
        r"\newcommand{\scalarRvpClosed}{\pi^2/16}",
        r"\newcommand{\scalarRlinApprox}{0.9634954084936207}",
        r"\newcommand{\scalarRvpApprox}{0.6168502750680849}",
        r"\newcommand{\scalarRlinFrac}{6797469/3559400}",
        r"\newcommand{\scalarRlinFactor}{6797469/3559400}",
        rf"\newcommand{{\scalarWlin}}{{{float(certified.linear_w2):.16f}}}",
        rf"\newcommand{{\scalarWvpLower}}{{{w_display_lo}}}",
        rf"\newcommand{{\scalarWvpUpper}}{{{w_display_hi}}}",
        rf"\newcommand{{\scalarRvpLo}}{{{display_lo}}}",
        rf"\newcommand{{\scalarRvpHi}}{{{display_hi}}}",
        rf"\newcommand{{\vpHeunBoundNum}}{{{bound.numerator}}}",
        rf"\newcommand{{\vpHeunBoundDen}}{{{bound.denominator}}}",
        rf"\newcommand{{\vpHeunIntLeft}}{{{int_left}}}",
        rf"\newcommand{{\vpHeunIntRight}}{{{int_right}}}",
        rf"\newcommand{{\strongRlin}}{{{strongest['R_linear']:.10f}}}",
        rf"\newcommand{{\strongRvp}}{{{strongest['R_vp']:.10f}}}",
        rf"\newcommand{{\strongRlinHat}}{{{strongest['R24_linear']:.10f}}}",
        rf"\newcommand{{\strongRvpHat}}{{{strongest['R24_vp']:.10f}}}",
        rf"\newcommand{{\strongWlin}}{{{strongest['W2_linear']:.10f}}}",
        rf"\newcommand{{\strongWvp}}{{{strongest['W2_vp']:.10f}}}",
        rf"\newcommand{{\strongMargin}}{{{strongest['W2_margin']:.10f}}}",
        rf"\newcommand{{\smallMargin}}{{{sci_tex(smallest['W2_margin'])}}}",
        rf"\newcommand{{\maxPrecDelta}}{{{sci_tex(max_delta)}}}",
        rf"\newcommand{{\precRatio}}{{{int(ratio)}}}",
        rf"\newcommand{{\lrTwoLmin}}{{{geometries['low_rank_d2']['eigenvalues'][0]:.16f}}}",
        rf"\newcommand{{\lrTwoLmax}}{{{geometries['low_rank_d2']['eigenvalues'][1]:.16f}}}",
        r"\newcommand{\nInversionCells}{5}",
        r"\newcommand{\nGeometrySolverCells}{12}",
        r"\newcommand{\nAllNFEInvertCells}{4}",
        r"\newcommand{\nDistinctRComparisons}{3}",
        r"\newcommand{\nLogcovWins}{36}",
        r"\newcommand{\RlinAniso}{0.972296}",
        r"\newcommand{\RvpAniso}{0.192270}",
        "",
    ]
    (GEN / "numbers.tex").write_text("\n".join(macros), encoding="utf-8")

    inv_lines = [
        r"\begin{tabular}{llcccrr}",
        r"\toprule",
        r"family & $d$ & solver & NFE & $R$ prefers & $W_2$ prefers & $W_2$ margin \\",
        r"\midrule",
    ]
    for block in inversions:
        fam = family_display_label(str(block["family"]), int(block["dim"]))
        inv_lines.append(
            f"{fam} & {block['dim']} & {block['solver']} & {block['nfe']} & "
            f"{block['R_prefers']} & {block['W2_prefers']} & "
            f"${sci_tex(block['W2_margin'], 6)}$ \\\\"
        )
    inv_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (GEN / "inversions_centered.tex").write_text("\n".join(inv_lines), encoding="utf-8")

    nc_lines = [
        r"\begin{tabular}{cccccl}",
        r"\toprule",
        r"$d$ & solver & NFE & inversion & $W_2$ prefers & $W_2^2$ driver \\",
        r"\midrule",
    ]
    for block in noncentered:
        flag = "yes" if block["inversion_R"] else "no"
        nc_lines.append(
            f"{block['dim']} & {block['solver']} & {block['nfe']} & {flag} & "
            f"{block['W2_prefers']} & {block['primary_W2sq_driver']} \\\\"
        )
    nc_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (GEN / "inversions_noncentered.tex").write_text(
        "\n".join(nc_lines), encoding="utf-8"
    )

    delta_lines = [
        r"\begin{tabular}{ccccrrr}",
        r"\toprule",
        r"$d$ & solver & NFE & inv. & $\Delta_{\mathrm{mean}}$ "
        r"& $\Delta_{\mathrm{cov}}$ & $\Delta_{\mathrm{total}}$ \\",
        r"\midrule",
    ]
    for block in noncentered:
        flag = "yes" if block["inversion_R"] else "no"
        delta_lines.append(
            f"{block['dim']} & {block['solver']} & {block['nfe']} & {flag} & "
            f"${sci_tex(block['delta_mean'], 6)}$ & "
            f"${sci_tex(block['delta_cov'], 6)}$ & "
            f"${sci_tex(block['delta_total'], 6)}$ \\\\"
        )
    delta_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (GEN / "noncentered_deltas.tex").write_text(
        "\n".join(delta_lines), encoding="utf-8"
    )

    quad_lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"geometry & $\cR_{\mathrm{lin}}$ & $\Rhat^{\mathrm{lin}}$ "
        r"& $\cR_{\mathrm{VP}}$ & $\Rhat^{\mathrm{VP}}$ \\",
        r"\midrule",
    ]
    quad_names = [
        (r"scalar $\lambda=4$", "scalar_lambda4"),
        ("anisotropic $d=2,8$", "anisotropic_d2"),
        ("factor+noise $d=2$", "low_rank_d2"),
        ("rank-2 factor+noise $d=8$", "low_rank_d8"),
        ("non-centered anisotropic $d=2,8$", "shifted_anisotropic_d2"),
    ]
    for label, key in quad_names:
        lin = geometries[key]["regularity"]["linear"]
        vp = geometries[key]["regularity"]["variance_preserving"]
        quad_lines.append(
            f"{label} & {float(lin['R']):.6f} & {float(lin['R24']):.6f} & "
            f"{float(vp['R']):.6f} & {float(vp['R24']):.6f} \\\\"
        )
    quad_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (GEN / "quadrature_comparison.tex").write_text(
        "\n".join(quad_lines), encoding="utf-8"
    )

    rob_lines = [
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r"solver & $d=2$ blocks & $d=8$ blocks & preferred path \\",
        r"\midrule",
    ]
    for solver, preferred in (
        ("euler", "VP"),
        ("heun", "linear"),
        ("rk4", "linear"),
    ):
        n2 = sum(
            1 for row in lr_prefs if row["solver"] == solver and int(row["dim"]) == 2
        )
        n8 = sum(
            1 for row in lr_prefs if row["solver"] == solver and int(row["dim"]) == 8
        )
        rob_lines.append(f"{solver} & {n2} & {n8} & {preferred} \\\\")
    rob_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (GEN / "robustness_summary.tex").write_text("\n".join(rob_lines), encoding="utf-8")
    (GEN / "vp_certificate.tex").write_text(
        "\n".join(
            [
                r"The VP Heun product $P(\pi,\sqrt{2})\in\mathbb{Q}[\pi,\sqrt{2}]$ "
                r"has twelve monomials, all with nonnegative coefficients "
                r"(records in \path{paper/arxiv/artifacts/scalar_counterexample.json}). "
                r"Substituting $\pi<355/113$ and $\sqrt{2}<99/70$ therefore yields",
                r"\[",
                r"P\Bigl(\tfrac{355}{113},\tfrac{99}{70}\Bigr)"
                r"=\frac{\vpHeunBoundNum}{\vpHeunBoundDen}<1.87.",
                r"\]",
                r"Equivalently, the integer comparison",
                r"\[",
                r"\vpHeunIntLeft<\vpHeunIntRight",
                r"\]",
                r"holds. Hence $r_{\mathrm{VP}}<187/100$ and "
                r"$\wtwo^{\mathrm{VP}}=2-r_{\mathrm{VP}}>13/100$.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("wrote", OUT)
    print("inversions", n_inv_r, "noncentered", n_w_inv, "robust", len(lr_prefs))


if __name__ == "__main__":
    main()
