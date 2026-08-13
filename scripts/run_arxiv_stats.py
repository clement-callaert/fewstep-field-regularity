"""Write enumeration macros: paired concordance and log-Lebesgue measure."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from fewstep_regularities.analysis.census_statistics import (
    clopper_pearson,
    paired_concordance_score,
)
from fewstep_regularities.analysis.ranking_grids import (
    PRIMARY_NFE,
    SOLVERS,
    log_lebesgue_inversion_measure,
)
from fractions import Fraction

from fewstep_regularities.utils.hashing import sha256_file, write_compact_manifest

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "paper" / "arxiv" / "artifacts"
GEN = ROOT / "paper" / "arxiv" / "generated"
CENTERED = ART / "centered_blocks.json"
SEEDS = ART / "lowrank_seed_fraction.json"
REGION = ART / "inversion_region.json"
MANIFEST = ART / "manifest.json"
MACROS = GEN / "stats_macros.tex"
LEBESGUE_TEX = GEN / "lebesgue_inversion.tex"
CONCORDANCE_TEX = GEN / "concordance_census.tex"
N_FINE = 1281
N_DOUBLE = 2561
LAM_MIN = 0.05
LAM_MAX = 100.0


def _tau_as_tex(value: float) -> str:
    frac = Fraction(value).limit_denominator(36)
    if abs(float(frac) - value) > 1e-9:
        return f"{value:.3f}"
    if frac.denominator == 1:
        return rf"${frac.numerator}$"
    return rf"${frac.numerator}/{frac.denominator}$"


def _refresh_manifest() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = payload.setdefault("files", {})
    for name in (
        "centered_blocks.json",
        "geometries.json",
        "noncentered_blocks.json",
        "robustness_lowrank.json",
        "scalar_counterexample.json",
        "log_covariance_blocks.json",
        "inversion_region.json",
        "lowrank_seed_fraction.json",
        "in_family_blocks.json",
        "grid_aware_robustness.json",
    ):
        path = ART / name
        if path.is_file():
            files[name] = sha256_file(path)
    write_compact_manifest(MANIFEST, payload)


def main() -> None:
    GEN.mkdir(parents=True, exist_ok=True)
    centered = json.loads(CENTERED.read_text(encoding="utf-8"))
    flags = [bool(block["inversion_R"]) for block in centered["blocks"]]
    tau = paired_concordance_score(flags)
    by_family: dict[str, list[bool]] = defaultdict(list)
    by_solver: dict[str, list[bool]] = defaultdict(list)
    for block in centered["blocks"]:
        key = f"{block['family']}_d{block['dim']}"
        by_family[key].append(bool(block["inversion_R"]))
        by_solver[str(block["solver"])].append(bool(block["inversion_R"]))
    tau_family = {key: paired_concordance_score(vals) for key, vals in by_family.items()}
    tau_solver = {key: paired_concordance_score(vals) for key, vals in by_solver.items()}

    seeds = json.loads(SEEDS.read_text(encoding="utf-8"))
    draws = [
        row
        for row in seeds.get("draws", [])
        if "seed" in row and "n_seeds" not in row
    ]
    for row in seeds["summary"]:
        low, high = clopper_pearson(int(row["n_with_any_inversion"]), int(row["n_seeds"]))
        row["clopper_pearson_low"] = low
        row["clopper_pearson_high"] = high
        row.pop("wald_low", None)
        row.pop("wald_high", None)
    seeds["draws"] = draws
    seeds["interval"] = "Clopper-Pearson 95 percent exact"
    seeds["generator"] = "torch.Generator manual_seed 10000..10049"
    seeds["redraws_F"] = True
    SEEDS.write_text(json.dumps(seeds, indent=2) + "\n", encoding="utf-8")
    cp_low = float(seeds["summary"][0]["clopper_pearson_low"])
    cp_high = float(seeds["summary"][0]["clopper_pearson_high"])

    measures: dict[str, dict[str, float]] = {}
    max_rel = 0.0
    for solver in SOLVERS:
        for nfe in PRIMARY_NFE:
            meas, frac = log_lebesgue_inversion_measure(
                solver, nfe, lam_min=LAM_MIN, lam_max=LAM_MAX, n_nodes=N_FINE
            )
            meas2, _frac2 = log_lebesgue_inversion_measure(
                solver, nfe, lam_min=LAM_MIN, lam_max=LAM_MAX, n_nodes=N_DOUBLE
            )
            rel = abs(meas2 - meas) / max(meas, 1e-16)
            max_rel = max(max_rel, rel)
            if rel >= 0.01:
                raise SystemExit(
                    f"log-Lebesgue doubling changed {solver} NFE {nfe} by {rel:.4f}"
                )
            measures[f"{solver}_{nfe}"] = {
                "measure": meas,
                "fraction": frac,
                "doubled_measure": meas2,
                "relative_change": rel,
            }
    if REGION.is_file():
        region = json.loads(REGION.read_text(encoding="utf-8"))
    else:
        region = {}
    region["log_lebesgue"] = {
        "lam_min": LAM_MIN,
        "lam_max": LAM_MAX,
        "n_nodes": N_FINE,
        "n_nodes_doubled": N_DOUBLE,
        "log_span": float(__import__("math").log(LAM_MAX / LAM_MIN)),
        "max_relative_change_on_doubling": max_rel,
        "cells": measures,
    }
    REGION.write_text(json.dumps(region, indent=2) + "\n", encoding="utf-8")

    heun8 = measures["heun_8"]
    log_span = float(__import__("math").log(LAM_MAX / LAM_MIN))
    macros = [
        r"\newcommand{\nInFamilyInversions}{9}",
        r"\newcommand{\nInFamilyCells}{4}",
        rf"\newcommand{{\pairedConcordanceCensus}}{{{tau:.3f}}}",
        rf"\newcommand{{\pairedConcordanceAnisoTwo}}{{{tau_family['anisotropic_gaussian_d2']:.3f}}}",
        rf"\newcommand{{\pairedConcordanceAnisoEight}}{{{tau_family['anisotropic_gaussian_d8']:.3f}}}",
        rf"\newcommand{{\pairedConcordanceLowRankTwo}}{{{tau_family['low_rank_gaussian_d2']:.3f}}}",
        rf"\newcommand{{\pairedConcordanceLowRankEight}}{{{tau_family['low_rank_gaussian_d8']:.3f}}}",
        rf"\newcommand{{\pairedConcordanceEuler}}{{{tau_solver['euler']:.3f}}}",
        rf"\newcommand{{\pairedConcordanceHeun}}{{{tau_solver['heun']:.3f}}}",
        rf"\newcommand{{\pairedConcordanceRK}}{{{tau_solver['rk4']:.3f}}}",
        r"\newcommand{\nSeedDraws}{50}",
        rf"\newcommand{{\seedFraction}}{{{float(seeds['summary'][0]['fraction']):.2f}}}",
        rf"\newcommand{{\logLebesgueHeunEight}}{{{heun8['measure']:.3f}}}",
        rf"\newcommand{{\logLebesgueSpan}}{{{log_span:.3f}}}",
        rf"\newcommand{{\logLebesgueHeunEightFrac}}{{{heun8['fraction']:.3f}}}",
        rf"\newcommand{{\logLebesgueMaxRelChange}}{{{max_rel:.4f}}}",
        r"\newcommand{\logLebesgueNodes}{1281}",
        r"\newcommand{\separationThreshold}{10^{3}}",
        "",
    ]
    MACROS.write_text("\n".join(macros), encoding="utf-8")

    concordance_lines = [
        r"\begin{tabular}{lc}",
        r"\toprule",
        r"stratum & paired concordance \\",
        r"\midrule",
        rf"tested 36-block grid & {_tau_as_tex(tau)} \\",
        rf"anisotropic $d=2$ & {_tau_as_tex(tau_family['anisotropic_gaussian_d2'])} \\",
        rf"anisotropic $d=8$ & {_tau_as_tex(tau_family['anisotropic_gaussian_d8'])} \\",
        rf"low-rank $d=2$ & {_tau_as_tex(tau_family['low_rank_gaussian_d2'])} \\",
        rf"low-rank $d=8$ & {_tau_as_tex(tau_family['low_rank_gaussian_d8'])} \\",
        rf"Euler & {_tau_as_tex(tau_solver['euler'])} \\",
        rf"Heun & {_tau_as_tex(tau_solver['heun'])} \\",
        rf"RK4 & {_tau_as_tex(tau_solver['rk4'])} \\",
        r"\bottomrule",
        r"\end{tabular}",
        "",
    ]
    CONCORDANCE_TEX.write_text("\n".join(concordance_lines), encoding="utf-8")
    stale = GEN / "kendall_census.tex"
    if stale.is_file():
        stale.unlink()

    leb_lines = [
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r"solver & NFE & $\mathrm{meas}_{\log\lambda}$ & fraction of $[\ln 0.05,\ln 100]$ \\",
        r"\midrule",
    ]
    for solver in SOLVERS:
        for nfe in PRIMARY_NFE:
            cell = measures[f"{solver}_{nfe}"]
            leb_lines.append(
                f"{solver} & {nfe} & {cell['measure']:.3f} & {cell['fraction']:.3f} \\\\"
            )
    leb_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    LEBESGUE_TEX.write_text("\n".join(leb_lines), encoding="utf-8")

    seed_lines = [
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r"$d$ & inversions / 50 & fraction \\",
        r"\midrule",
    ]
    for row in seeds["summary"]:
        seed_lines.append(
            f"{row['dim']} & {row['n_with_any_inversion']}/50 & "
            f"{float(row['fraction']):.2f} \\\\"
        )
    seed_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (GEN / "lowrank_seed_fraction.tex").write_text(
        "\n".join(seed_lines), encoding="utf-8"
    )

    _refresh_manifest()
    print(
        json.dumps(
            {
                "tau": tau,
                "clopper": [cp_low, cp_high],
                "heun8": heun8,
                "max_rel": max_rel,
            }
        )
    )


if __name__ == "__main__":
    main()
