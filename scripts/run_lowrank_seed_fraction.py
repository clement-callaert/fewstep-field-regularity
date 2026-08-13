"""Fraction of low-rank geometries that invert under independent F draws."""

from __future__ import annotations

import json
import math
from pathlib import Path

import torch

from fewstep_regularities.analysis.ranking_grids import (
    PRIMARY_NFE,
    SOLVERS,
    linear_vp_inversion,
)
from fewstep_regularities.distributions.gaussian import low_rank_gaussian

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "paper" / "arxiv" / "artifacts" / "lowrank_seed_fraction.json"
OUT_TEX = ROOT / "paper" / "arxiv" / "generated" / "lowrank_seed_fraction.tex"
N_SEEDS = 50
BASE_SEED = 10000
DIMS = (2, 8)


def binomial_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Return a Wald interval clipped to [0, 1]."""
    if n <= 0:
        raise ValueError("n must be positive")
    p = successes / n
    half = z * math.sqrt(p * (1.0 - p) / n)
    return max(0.0, p - half), min(1.0, p + half)


def geometry_inverts(eigenvalues: list[float]) -> bool:
    for solver in SOLVERS:
        for nfe in PRIMARY_NFE:
            if linear_vp_inversion(eigenvalues, solver, nfe):
                return True
    return False


def main() -> None:
    records: list[dict[str, object]] = []
    for dim in DIMS:
        hits = 0
        for offset in range(N_SEEDS):
            seed = BASE_SEED + offset
            generator = torch.Generator().manual_seed(seed)
            gaussian = low_rank_gaussian(
                dim,
                rank=2,
                noise_variance=0.05,
                dtype=torch.float64,
                generator=generator,
            )
            eigenvalues = torch.linalg.eigvalsh(gaussian.covariance()).tolist()
            inverted = geometry_inverts(eigenvalues)
            hits += int(inverted)
            records.append(
                {"dim": dim, "seed": seed, "inversion_any_block": inverted}
            )
        lo, hi = binomial_interval(hits, N_SEEDS)
        print(f"d={dim} {hits}/{N_SEEDS} interval=({lo:.3f},{hi:.3f})")
        records.append(
            {
                "dim": dim,
                "n_seeds": N_SEEDS,
                "n_with_any_inversion": hits,
                "fraction": hits / N_SEEDS,
                "wald_low": lo,
                "wald_high": hi,
            }
        )
    summary = [row for row in records if "n_seeds" in row]
    OUT_JSON.write_text(
        json.dumps({"n_seeds": N_SEEDS, "summary": summary, "draws": records}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    lines = [
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r"$d$ & inversions / 50 & fraction & Wald 95\% \\",
        r"\midrule",
    ]
    for row in summary:
        lines.append(
            f"{row['dim']} & {row['n_with_any_inversion']}/50 & "
            f"{float(str(row['fraction'])):.2f} & "
            f"[{float(str(row['wald_low'])):.2f}, {float(str(row['wald_high'])):.2f}] \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    OUT_TEX.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT_JSON)


if __name__ == "__main__":
    main()
