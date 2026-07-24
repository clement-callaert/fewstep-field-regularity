"""Build the three workshop paper figures with provenance sidecars.

Inputs are explicit artifact files with pinned SHA-256 checksums. The
script refuses to run on a checksum mismatch and never scans directories.
Figure 1 is conceptual and consumes no artifact.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fewstep_regularities.utils.hashing import sha256_file

ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "paper" / "gddl2026" / "figures"
FIGURE_SUFFIX = ".pdf"

# Pinned inputs. No other file may be read.
PINNED_INPUTS = {
    "phase4_gaussian_reproduction_2026-07-24-v1:results": {
        "path": "outputs/phase4_gaussian_reproduction_2026-07-24-v1/results.json",
        "sha256": "b8930142cba5655ee553aae5ff400cd884c1137e77547d9a5fa94bd4e354973f",
    },
    "workshop_external_validation_2026-07-24-v1:results": {
        "path": "outputs/workshop_external_validation_2026-07-24-v1/results.json",
        "sha256": "4234bc2baefa8390414db9e037c7d028408cb04591e2b6302524ed8ad3bd205d",
    },
    "workshop_external_validation_2026-07-24-v1:inversions": {
        "path": "outputs/workshop_external_validation_2026-07-24-v1/inversions.json",
        "sha256": "cceebdfcba6f7cec4a7ff9e137d4a53f8c7e389acc0222a20805f16204a1b875",
    },
}

# Validated categorical palette (Okabe-Ito subset; CVD-checked).
COLOR_LINEAR = "#0072B2"
COLOR_VP = "#D55E00"
SOLVER_COLORS = {"euler": "#0072B2", "heun": "#D55E00", "rk4": "#009E73"}
SOLVER_MARKERS = {"euler": "o", "heun": "s", "rk4": "^"}
GRAY = "#5f6368"

plt.rcParams.update(
    {
        "font.size": 8,
        "axes.titlesize": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "pdf.fonttype": 42,
    }
)


def git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def load_pinned(artifact_id: str) -> Any:
    entry = PINNED_INPUTS[artifact_id]
    path = ROOT / str(entry["path"])
    actual = sha256_file(path)
    if actual != entry["sha256"]:
        raise ValueError(f"Checksum mismatch for {artifact_id}: {actual}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_sidecar(
    figure_path: Path,
    *,
    artifact_ids: list[str],
    plotting_config: dict[str, Any],
    note: str,
) -> None:
    sidecar = {
        "figure_artifact_id": f"workshop_figures_2026-07-24-v1:{figure_path.stem}",
        "source_run_ids": sorted({a.split(":")[0] for a in artifact_ids})
        or ["none_conceptual"],
        "source_artifact_ids": artifact_ids,
        "source_table_hashes": {a: PINNED_INPUTS[a]["sha256"] for a in artifact_ids},
        "plotting_script": "scripts/make_workshop_figures.py",
        "plotting_config": plotting_config,
        "git_commit": git_commit(),
        "generation_timestamp": datetime.now(UTC).isoformat(),
        "figure_checksum_sha256": sha256_file(figure_path),
        "note": note,
    }
    sidecar_path = figure_path.with_suffix(figure_path.suffix + ".json")
    sidecar_path.write_text(
        json.dumps(sidecar, indent=2, sort_keys=True), encoding="utf-8"
    )


def phase4_blocks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group Phase 4 rows into two-path comparison blocks."""
    by_key: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = {}
    for row in rows:
        key = (row["target_family"], row["dim"], row["solver"], row["nfe"])
        by_key.setdefault(key, {})[row["path"]] = row
    blocks = []
    for (family, dim, solver, nfe), paths in sorted(by_key.items()):
        lin, vp = paths["linear"], paths["variance_preserving"]
        d_metric = lin["baseline_metric"] - vp["baseline_metric"]
        d_w2 = lin["gaussian_w2"] - vp["gaussian_w2"]
        blocks.append(
            {
                "family": family,
                "dim": dim,
                "solver": solver,
                "nfe": nfe,
                "metric_delta": d_metric,
                "w2_delta": d_w2,
                "is_inversion": d_metric * d_w2 < 0,
                "linear": lin,
                "vp": vp,
            }
        )
    return blocks


def figure1_conceptual() -> Path:
    """Conceptual schematic: averaged regularity versus endpoint ranking."""
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(5.5, 1.9), gridspec_kw={"width_ratios": [1.4, 1.0]}
    )
    import numpy as np

    t = np.linspace(0.0, 1.0, 400)
    # Schematic Jacobian magnitude profiles (not data). Path B carries a
    # narrow spike centered between two solver nodes, so its larger time
    # average is invisible to the fixed grid.
    path_a = 1.0 + 0.25 * np.sin(2.4 * np.pi * t)
    path_b = 0.55 + 1.6 * np.exp(-((t - 0.875) ** 2) / 0.008)
    ax1.plot(t, path_a, color=COLOR_LINEAR, lw=1.4, label="path A")
    ax1.plot(t, path_b, color=COLOR_VP, lw=1.4, label="path B")
    for node in np.linspace(0, 1, 5):
        ax1.axvline(node, color=GRAY, lw=0.5, alpha=0.35, zorder=0)
    ax1.annotate(
        "solver nodes",
        xy=(0.5, 2.14),
        xytext=(0.24, 2.14),
        color=GRAY,
        fontsize=6.5,
        va="center",
        ha="right",
        arrowprops={"arrowstyle": "-", "color": GRAY, "lw": 0.5},
    )
    ax1.set_xlabel("time $t$")
    ax1.set_ylabel(r"$\Vert \partial_x b_t \Vert$ (schematic)")
    ax1.set_ylim(0, 2.3)
    ax1.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.86))
    ax1.set_title("averaged regularity: B > A", loc="left", fontsize=7.5)

    bars = ax2.bar(
        [0, 1],
        [0.71, 0.42],
        width=0.55,
        color=[COLOR_LINEAR, COLOR_VP],
        edgecolor="none",
    )
    ax2.bar_label(bars, ["A", "B"], padding=2, fontsize=7)
    ax2.set_xticks([0, 1], ["path A", "path B"])
    ax2.set_ylabel("endpoint error (schematic)")
    ax2.set_ylim(0, 0.95)
    ax2.set_title("fixed-NFE error: B < A", loc="left", fontsize=7.5)
    fig.tight_layout()
    out = FIGURE_DIR / ("fig1_conceptual" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def figure2_inversions() -> tuple[Path, list[str]]:
    """Strongest inversion plus all fourteen Phase 4 inversion blocks."""
    artifact_id = "phase4_gaussian_reproduction_2026-07-24-v1:results"
    payload = load_pinned(artifact_id)
    blocks = phase4_blocks(payload["rows"])
    inversions = [b for b in blocks if b["is_inversion"]]
    if len(inversions) != 14:
        raise ValueError(f"Expected 14 Phase 4 inversion blocks, got {len(inversions)}")

    strongest = max(inversions, key=lambda b: abs(b["w2_delta"]))
    fig = plt.figure(figsize=(6.9, 2.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[0.55, 0.55, 1.9], wspace=0.95)
    ax_m = fig.add_subplot(gs[0])
    ax_w = fig.add_subplot(gs[1])
    ax_all = fig.add_subplot(gs[2])

    lin, vp = strongest["linear"], strongest["vp"]
    for ax, key, title in (
        (ax_m, "baseline_metric", "avg. regularity"),
        (ax_w, "gaussian_w2", "Gaussian $W_2$"),
    ):
        vals = [lin[key], vp[key]]
        bars = ax.bar(
            [0, 1],
            vals,
            width=0.6,
            color=[COLOR_LINEAR, COLOR_VP],
            edgecolor="none",
        )
        ax.bar_label(bars, [f"{v:.2f}" for v in vals], padding=1.5, fontsize=6.5)
        ax.set_xticks([0, 1], ["lin", "vp"])
        ax.set_title(title, loc="left", fontsize=7.5)
        ax.set_ylim(0, max(vals) * 1.3)
    ax_m.set_ylabel("Avg-Lip$^2$")
    ax_w.set_ylabel("$W_2$")

    # All fourteen blocks: |W2 margin| of the inversion, log scale.
    inversions_sorted = sorted(inversions, key=lambda b: abs(b["w2_delta"]))
    labels = [
        f"{'aniso' if b['family'] == 'anisotropic_gaussian' else 'lowrank'}"
        f" d{b['dim']} {b['solver']} n{b['nfe']}"
        for b in inversions_sorted
    ]
    margins = [abs(b["w2_delta"]) for b in inversions_sorted]
    colors = [
        COLOR_VP if b["w2_delta"] > 0 else COLOR_LINEAR for b in inversions_sorted
    ]
    y = range(len(margins))
    ax_all.hlines(y, 1e-6, margins, color="#d0d0d0", lw=0.7, zorder=1)
    ax_all.scatter(margins, y, s=14, c=colors, zorder=2)
    ax_all.set_xscale("log")
    ax_all.set_xlim(5e-6, 1.0)
    ax_all.set_yticks(list(y), labels, fontsize=6)
    ax_all.set_xlabel(r"$|W_2|$ margin of inversion (log scale)")
    ax_all.set_title("all 14 inversion blocks", loc="left", fontsize=7.5)
    handles = [
        plt.Line2D(
            [], [], marker="o", ls="", color=COLOR_LINEAR, label="$W_2$ prefers linear"
        ),
        plt.Line2D([], [], marker="o", ls="", color=COLOR_VP, label="$W_2$ prefers vp"),
    ]
    ax_all.legend(handles=handles, frameon=False, loc="lower right", fontsize=6)
    fig.tight_layout()
    out = FIGURE_DIR / ("fig2_inversions" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out, [artifact_id]


def figure3_interaction() -> tuple[Path, list[str]]:
    """Low-rank solver-path interaction across solvers and NFE."""
    artifact_id = "phase4_gaussian_reproduction_2026-07-24-v1:results"
    payload = load_pinned(artifact_id)
    blocks = [
        b for b in phase4_blocks(payload["rows"]) if b["family"] == "low_rank_gaussian"
    ]
    fig, axes = plt.subplots(1, 2, figsize=(5.5, 1.9), sharey=True)
    for ax, dim in zip(axes, (2, 8), strict=True):
        for solver in ("euler", "heun", "rk4"):
            pts = sorted(
                (b for b in blocks if b["dim"] == dim and b["solver"] == solver),
                key=lambda b: b["nfe"],
            )
            ax.plot(
                [b["nfe"] for b in pts],
                [b["w2_delta"] for b in pts],
                marker=SOLVER_MARKERS[solver],
                ms=3.5,
                lw=1.2,
                color=SOLVER_COLORS[solver],
                label=solver if dim == 2 else None,
            )
        ax.axhline(0.0, color=GRAY, lw=0.6, alpha=0.6)
        ax.set_xscale("log", base=2)
        ax.set_yscale("symlog", linthresh=1e-4)
        ax.set_xticks([8, 16, 32], ["8", "16", "32"])
        ax.set_xlabel("NFE")
        ax.set_title(f"low-rank, $d={dim}$", loc="left", fontsize=7.5)
    axes[0].set_ylabel(r"$W_2$(lin) $-$ $W_2$(vp)")
    fig.text(
        0.99,
        0.99,
        "above 0: vp preferred · below 0: linear preferred",
        ha="right",
        va="top",
        color=GRAY,
        fontsize=6.5,
    )
    fig.legend(
        frameon=False,
        loc="lower center",
        ncol=3,
        fontsize=6.5,
        bbox_to_anchor=(0.5, -0.06),
    )
    fig.tight_layout(rect=(0.0, 0.06, 1.0, 0.97))
    out = FIGURE_DIR / ("fig3_interaction" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out, [artifact_id]


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig1 = figure1_conceptual()
    write_sidecar(
        fig1,
        artifact_ids=[],
        plotting_config={
            "kind": "conceptual_schematic",
            "consumes_artifacts": False,
        },
        note=(
            "Conceptual schematic only; curves and bars are illustrative and "
            "represent no measured quantity."
        ),
    )
    fig2, ids2 = figure2_inversions()
    write_sidecar(
        fig2,
        artifact_ids=ids2,
        plotting_config={
            "kind": "strongest_inversion_and_all_blocks",
            "block_definition": "two-path comparison per (family, dim, solver, nfe)",
            "x_scale": "log",
        },
        note="Log margin axis; no visual exaggeration of differences.",
    )
    fig3, ids3 = figure3_interaction()
    write_sidecar(
        fig3,
        artifact_ids=ids3,
        plotting_config={
            "kind": "lowrank_solver_path_interaction",
            "y_scale": "symlog linthresh 1e-4",
        },
        note="Signed margins; zero line marks path-preference boundary.",
    )
    for path in (fig1, fig2, fig3):
        print(path.relative_to(ROOT), sha256_file(path)[:16])


if __name__ == "__main__":
    main()
