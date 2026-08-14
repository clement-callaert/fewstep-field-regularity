"""In-family census: trigonometric VP versus shared Chen Ex. 3.3 (M=λ_max)."""

from __future__ import annotations

import json
from pathlib import Path

from fewstep_regularities.analysis.ranking_grids import (
    GEOM_KEYS,
    PRIMARY_NFE,
    SOLVERS,
    family_display_label,
    four_path_scores,
    path_regularity,
    path_w2,
    ranking_inversion,
)

ROOT = Path(__file__).resolve().parents[1]
GEOMETRIES = ROOT / "paper" / "arxiv" / "artifacts" / "geometries.json"
OUT_JSON = ROOT / "paper" / "arxiv" / "artifacts" / "in_family_blocks.json"
OUT_TEX = ROOT / "paper" / "arxiv" / "generated" / "in_family_blocks.tex"

EXPECTED = {
    ("anisotropic", 2, "euler", 16),
    ("anisotropic", 2, "euler", 32),
    ("anisotropic", 8, "euler", 8),
    ("anisotropic", 8, "euler", 16),
    ("anisotropic", 8, "euler", 32),
    ("low-rank", 2, "euler", 8),
    ("low-rank", 2, "heun", 8),
    ("low-rank", 2, "heun", 16),
    ("low-rank", 2, "heun", 32),
}


def main() -> None:
    payload = json.loads(GEOMETRIES.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    inverted: list[tuple[str, int, str, int]] = []
    cells: dict[tuple[str, int, str], list[bool]] = {}
    for key, family, dim in GEOM_KEYS:
        eigenvalues = payload[key]["eigenvalues"]
        r_vp = path_regularity("variance_preserving", eigenvalues)
        r_sc = path_regularity("log_covariance_scalar", eigenvalues)
        for solver in SOLVERS:
            flags: list[bool] = []
            for nfe in PRIMARY_NFE:
                w_vp = path_w2("variance_preserving", solver, eigenvalues, nfe)
                w_sc = path_w2("log_covariance_scalar", solver, eigenvalues, nfe)
                inverted_flag = ranking_inversion(r_vp, r_sc, w_vp, w_sc)
                flags.append(inverted_flag)
                scores = four_path_scores(eigenvalues, solver, nfe)
                row = {
                    "family": family,
                    "dim": dim,
                    "solver": solver,
                    "nfe": nfe,
                    "R_vp": r_vp,
                    "R_scalar": r_sc,
                    "W2_vp": w_vp,
                    "W2_scalar": w_sc,
                    "R_prefers": "VP" if r_vp < r_sc else "scalar",
                    "W2_prefers": "VP" if w_vp < w_sc else "scalar",
                    "inversion": inverted_flag,
                    "W2_margin": abs(w_vp - w_sc),
                    "R_linear": scores["linear"].regularity,
                    "R_log": scores["log_covariance"].regularity,
                    "W2_linear": scores["linear"].w2,
                    "W2_log": scores["log_covariance"].w2,
                }
                rows.append(row)
                if inverted_flag:
                    inverted.append((family, dim, solver, nfe))
            cells[(family, dim, solver)] = flags
    n_cells = sum(any(flags) for flags in cells.values())
    found = {(fam, dim, solver, nfe) for fam, dim, solver, nfe in inverted}
    if found != EXPECTED:
        raise SystemExit(f"unexpected shared-schedule pairwise inversions: {sorted(found)}")
    if len(rows) != 36 or len(inverted) != 9 or n_cells != 4:
        raise SystemExit("unexpected shared-schedule pairwise census counts")
    OUT_JSON.write_text(
        json.dumps(
            {
                "n_blocks": 36,
                "n_inversions": 9,
                "n_cells": 4,
                "comparison": "variance_preserving vs log_covariance_scalar M=lambda_max",
                "status": "post-hoc",
                "blocks": rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        r"\begin{tabular}{llcccc}",
        r"\toprule",
        r"family & $d$ & solver & NFE & $R$ prefers & $W_2$ prefers \\",
        r"\midrule",
    ]
    for row in rows:
        if not row["inversion"]:
            continue
        lines.append(
            f"{family_display_label(str(row['family']), int(str(row['dim'])))} & "
            f"{row['dim']} & {row['solver']} & {row['nfe']} & "
            f"{row['R_prefers']} & {row['W2_prefers']} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    OUT_TEX.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"n_inversions": 9, "n_cells": 4, "wrote": str(OUT_JSON)}))


if __name__ == "__main__":
    main()
