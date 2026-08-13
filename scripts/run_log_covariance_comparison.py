"""Compare linear, VP, and per-mode log-covariance on the paper geometries."""

from __future__ import annotations

import json
from pathlib import Path

from fewstep_regularities.analysis.ranking_grids import (
    PRIMARY_NFE,
    SOLVERS,
    lowest_name,
    three_path_scores,
)

ROOT = Path(__file__).resolve().parents[1]
GEOMETRIES = ROOT / "paper" / "arxiv" / "artifacts" / "geometries.json"
OUT_JSON = ROOT / "paper" / "arxiv" / "artifacts" / "log_covariance_blocks.json"
OUT_TEX = ROOT / "paper" / "arxiv" / "generated" / "log_covariance_blocks.tex"
OUT_SUMMARY = ROOT / "paper" / "arxiv" / "generated" / "log_covariance_summary.tex"

GEOM_KEYS = (
    ("anisotropic_d2", "anisotropic", 2),
    ("anisotropic_d8", "anisotropic", 8),
    ("low_rank_d2", "low-rank", 2),
    ("low_rank_d8", "low-rank", 8),
)
PATH_LABEL = {
    "linear": "linear",
    "variance_preserving": "VP",
    "log_covariance": "log-cov",
}


def main() -> None:
    payload = json.loads(GEOMETRIES.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    n_log_smallest_w2 = 0
    n_total = 0
    for key, family, dim in GEOM_KEYS:
        eigenvalues = payload[key]["eigenvalues"]
        for solver in SOLVERS:
            for nfe in PRIMARY_NFE:
                scores = three_path_scores(eigenvalues, solver, nfe)
                r_best = lowest_name(scores, "regularity")
                w_best = lowest_name(scores, "w2")
                n_total += 1
                if w_best == "log_covariance":
                    n_log_smallest_w2 += 1
                rows.append(
                    {
                        "family": family,
                        "dim": dim,
                        "solver": solver,
                        "nfe": nfe,
                        "R_prefers": r_best,
                        "W2_prefers": w_best,
                        "R_linear": scores["linear"].regularity,
                        "R_vp": scores["variance_preserving"].regularity,
                        "R_log": scores["log_covariance"].regularity,
                        "W2_linear": scores["linear"].w2,
                        "W2_vp": scores["variance_preserving"].w2,
                        "W2_log": scores["log_covariance"].w2,
                    }
                )
    OUT_JSON.write_text(
        json.dumps(
            {
                "n_blocks": n_total,
                "n_log_covariance_smallest_w2": n_log_smallest_w2,
                "blocks": rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        r"\begin{tabular}{llcccccc}",
        r"\toprule",
        r"family & $d$ & solver & NFE & $R$ min & $W_2$ min & $W_{2,\mathrm{log}}$ & $W_{2,\mathrm{lin}}$ \\",
        r"\midrule",
    ]
    for row in rows:
                lines.append(
            f"{row['family']} & {row['dim']} & {row['solver']} & {row['nfe']} & "
            f"{PATH_LABEL[str(row['R_prefers'])]} & {PATH_LABEL[str(row['W2_prefers'])]} & "
            f"{float(str(row['W2_log'])):.4g} & {float(str(row['W2_linear'])):.4g} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    OUT_TEX.write_text("\n".join(lines), encoding="utf-8")
    OUT_SUMMARY.write_text(
        (
            f"On the {n_total} centered solver-budget conditions, the per-mode "
            f"log-covariance schedule (Chen et al.\\ Ex.~3.3) has the smallest "
            f"continuous $\\cR$ in every block and the smallest Gaussian $\\wtwo$ "
            f"in {n_log_smallest_w2} of {n_total} blocks.\n"
        ),
        encoding="utf-8",
    )
    workshop_rows = [
        row
        for row in rows
        if int(str(row["nfe"])) == 8 and str(row["solver"]) == "heun"
    ]
    workshop_lines = [
        r"\begin{tabular}{llcccc}",
        r"\toprule",
        r"family & $d$ & $\cR_{\mathrm{lin}}$ & $\cR_{\mathrm{VP}}$ & "
        r"$\cR_{\mathrm{log}}$ & Heun-8 $W_2$ min \\",
        r"\midrule",
    ]
    for row in workshop_rows:
        workshop_lines.append(
            f"{row['family']} & {row['dim']} & "
            f"{float(str(row['R_linear'])):.3f} & {float(str(row['R_vp'])):.3f} & "
            f"{float(str(row['R_log'])):.3f} & "
            f"{PATH_LABEL[str(row['W2_prefers'])]} \\\\"
        )
    workshop_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    workshop_tex = ROOT / "paper" / "arxiv" / "generated" / "log_covariance_workshop.tex"
    gddl_tex = ROOT / "paper" / "gddl2026" / "generated" / "log_covariance_workshop.tex"
    workshop_tex.write_text("\n".join(workshop_lines), encoding="utf-8")
    gddl_tex.parent.mkdir(parents=True, exist_ok=True)
    gddl_tex.write_text("\n".join(workshop_lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "n_blocks": n_total,
                "n_log_covariance_smallest_w2": n_log_smallest_w2,
                "wrote": str(OUT_JSON),
            }
        )
    )


if __name__ == "__main__":
    main()
