"""Grid-aware Euler robustness census: phase, frequency, node, and solver."""

from __future__ import annotations

import json
import math
from pathlib import Path

from fewstep_regularities.analysis.grid_aware import (
    records_as_dicts,
    robustness_census,
    theorem_holds,
)
from fewstep_regularities.utils.hashing import sha256_file
from fewstep_regularities.utils.provenance import source_state, write_json

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "paper" / "arxiv" / "artifacts" / "grid_aware_robustness.json"
OUT_TEX = ROOT / "paper" / "arxiv" / "generated" / "grid_aware_robustness.tex"

L = math.log(2.0)


def _fmt(value: float) -> str:
    if value == 0.0:
        return "0"
    if abs(value) < 1e-12:
        return r"$<10^{-12}$"
    if abs(value) >= 0.01:
        return f"{value:.3f}"
    return f"{value:.2e}"


def _phase_tex(phase: float) -> str:
    if abs(phase) < 1e-15:
        return "0"
    if abs(phase - 0.5 * math.pi) < 1e-12:
        return r"$\pi/2$"
    if abs(phase - math.pi) < 1e-12:
        return r"$\pi$"
    if abs(phase - 0.25 * math.pi) < 1e-12:
        return r"$\pi/4$"
    return f"{phase:.3f}"


def main() -> None:
    if not all(theorem_holds(L, n) for n in (1, 2, 4, 8, 16)):
        raise SystemExit("aligned grid-aware theorem failed on the check grid")
    records = robustness_census(L)
    payload = {
        "L": L,
        "lambda": math.exp(2.0 * L),
        "note": (
            "Perturbations of the aligned left-Euler construction. "
            "ranking_inverted is True only when exact endpoints still match "
            "and the constant minimizer has strictly larger solver error. "
            "This census is a transparency check, not a population frequency."
        ),
        "source_state": source_state(),
        "records": records_as_dicts(records),
    }
    write_json(OUT_JSON, payload)
    lines = [
        r"\begin{tabular}{rllllrrcc}",
        r"\toprule",
        r"$N$ & solver & $\phi$ & $f$ & $\theta$ & err $a_0$ & err $a_{1,N}$ "
        r"& ends & invert \\",
        r"\midrule",
    ]
    for row in records:
        ends = "yes" if row.endpoints_match else "no"
        invert = "yes" if row.ranking_inverted else "no"
        lines.append(
            f"{row.n_steps} & {row.solver} & {_phase_tex(row.phase)} & "
            f"{row.frequency:g} & {row.theta:g} & {_fmt(row.error0)} & "
            f"{_fmt(row.error1)} & {ends} & {invert} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    OUT_TEX.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "n_records": len(records),
                "n_inverted": sum(row.ranking_inverted for row in records),
                "n_endpoint_mismatch": sum(not row.endpoints_match for row in records),
                "json": str(OUT_JSON.relative_to(ROOT)),
                "sha256": sha256_file(OUT_JSON),
            }
        )
    )


if __name__ == "__main__":
    main()
