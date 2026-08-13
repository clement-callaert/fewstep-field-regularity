"""Sweep lambda x solver x NFE for linear-versus-VP ranking inversions."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from fewstep_regularities.analysis.ranking_grids import (
    HEUN_BUDGETS,
    PRIMARY_NFE,
    SOLVERS,
    linear_vp_inversion,
    path_regularity,
    path_w2,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "paper" / "arxiv" / "artifacts" / "inversion_region.json"
OUT_PDF_ARXIV = ROOT / "paper" / "arxiv" / "figures" / "fig_inversion_region.pdf"
OUT_PDF_GDDL = ROOT / "paper" / "gddl2026" / "figures" / "fig_inversion_region.pdf"

LAMBDAS = np.geomspace(0.05, 100.0, 41)
CONTROL_INVERT = (0.25, 0.5, 3.0, 4.0, 6.0)
CONTROL_NO_INVERT = (0.05, 0.1, 0.9, 1.5, 2.0, 9.0, 16.0, 36.0, 100.0)


def apply_paper_style() -> None:
    plt.rcParams.update(
        {
            "text.usetex": True,
            "text.latex.preamble": r"\usepackage{lmodern}",
            "font.family": "serif",
            "font.serif": ["Latin Modern Roman"],
            "mathtext.fontset": "cm",
            "pdf.fonttype": 42,
            "font.size": 9,
            "axes.titlesize": 9,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def main() -> None:
    apply_paper_style()
    grid: list[dict[str, object]] = []
    for solver in SOLVERS:
        for nfe in PRIMARY_NFE:
            for value in LAMBDAS:
                inverted = linear_vp_inversion([float(value)], solver, int(nfe))
                grid.append(
                    {
                        "lambda": float(value),
                        "solver": solver,
                        "nfe": int(nfe),
                        "inversion": inverted,
                    }
                )
    heun_budgets = {
        int(nfe): linear_vp_inversion([4.0], "heun", int(nfe)) for nfe in HEUN_BUDGETS
    }
    euler_budgets = {
        int(nfe): linear_vp_inversion([4.0], "euler", int(nfe)) for nfe in HEUN_BUDGETS
    }
    rk4_special = {
        8: linear_vp_inversion([4.0], "rk4", 8),
        12: linear_vp_inversion([4.0], "rk4", 12),
    }
    payload = {
        "grid": grid,
        "heun_lambda4_budgets": heun_budgets,
        "euler_lambda4_budgets": euler_budgets,
        "rk4_lambda4_nfe8": rk4_special[8],
        "rk4_lambda4_nfe12": rk4_special[12],
        "R_linear_lambda4": path_regularity("linear", [4.0]),
        "R_vp_lambda4": path_regularity("variance_preserving", [4.0]),
        "W2_heun8_linear": path_w2("linear", "heun", [4.0], 8),
        "W2_heun8_vp": path_w2("variance_preserving", "heun", [4.0], 8),
    }
    if OUT_JSON.is_file():
        previous = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        if "log_lebesgue" in previous:
            payload["log_lebesgue"] = previous["log_lebesgue"]
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    cmap = ListedColormap(["#f7f4ee", "#d55e00"])
    fig, axes = plt.subplots(
        1, 3, figsize=(5.45, 2.15), sharey=True, layout="constrained"
    )
    solver_titles = {"euler": "Euler", "heun": "Heun", "rk4": "RK4"}
    mesh = axes[0].pcolormesh(
        LAMBDAS,
        np.arange(len(PRIMARY_NFE)),
        np.zeros((len(PRIMARY_NFE), len(LAMBDAS))),
        cmap=cmap,
        vmin=0.0,
        vmax=1.0,
        shading="nearest",
    )
    mesh.remove()
    for ax, solver in zip(axes, SOLVERS, strict=True):
        mat = np.zeros((len(PRIMARY_NFE), len(LAMBDAS)))
        for nfe_index, nfe in enumerate(PRIMARY_NFE):
            for lam_index, value in enumerate(LAMBDAS):
                mat[nfe_index, lam_index] = float(
                    linear_vp_inversion([float(value)], solver, int(nfe))
                )
        mesh = ax.pcolormesh(
            LAMBDAS,
            np.arange(len(PRIMARY_NFE)),
            mat,
            cmap=cmap,
            vmin=0.0,
            vmax=1.0,
            shading="nearest",
        )
        ax.set_xscale("log")
        ax.set_xlim(0.05, 100.0)
        ax.set_yticks(np.arange(len(PRIMARY_NFE)), [str(n) for n in PRIMARY_NFE])
        ax.set_title(solver_titles[solver], loc="left")
        ax.set_xlabel(r"$\lambda$")
        ax.axvline(4.0, color="#222222", lw=0.7, ls="--")
    axes[0].set_ylabel("NFE")
    colorbar = fig.colorbar(
        mesh, ax=list(axes), fraction=0.03, pad=0.02, ticks=[0, 1]
    )
    colorbar.set_ticklabels(["agree", "invert"])
    OUT_PDF_ARXIV.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF_GDDL.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PDF_ARXIV, bbox_inches="tight")
    fig.savefig(OUT_PDF_GDDL, bbox_inches="tight")
    plt.close(fig)

    missing_invert = [
        value
        for value in CONTROL_INVERT
        if not linear_vp_inversion([value], "heun", 8)
    ]
    extra_invert = [
        value
        for value in CONTROL_NO_INVERT
        if linear_vp_inversion([value], "heun", 8)
    ]
    euler_hits = [
        value
        for value in CONTROL_INVERT + CONTROL_NO_INVERT
        if linear_vp_inversion([value], "euler", 8)
    ]
    if missing_invert or extra_invert:
        raise SystemExit(
            json.dumps(
                {
                    "missing_invert": missing_invert,
                    "extra_invert": extra_invert,
                    "euler_hits": euler_hits,
                }
            )
        )
    print(
        json.dumps(
            {
                "heun_lambda4_all_budgets": all(heun_budgets.values()),
                "euler_lambda4_any": any(euler_budgets.values()),
                "rk4_nfe8": rk4_special[8],
                "rk4_nfe12": rk4_special[12],
                "euler_control_hits": euler_hits,
                "wrote": str(OUT_JSON),
            }
        )
    )


if __name__ == "__main__":
    main()
