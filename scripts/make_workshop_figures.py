"""Build workshop paper figures with provenance sidecars.

Inputs are explicit artifact files with pinned SHA-256 checksums. The
script refuses to run on a checksum mismatch and never scans directories.
The live workshop PDF uses fig_scalar, fig1_regimes, and
fig_inversion_region. Hydra-backed figures are skipped when outputs/
is absent.
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
from fewstep_regularities.utils.provenance import figure_sidecar_payload, write_json

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
        "text.usetex": False,
        "mathtext.fontset": "cm",
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
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
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def _revision_commit() -> str | None:
    path = ROOT / "REVISION"
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lower().startswith("commit:"):
            return line.split(":", 1)[1].strip()
    return None


def git_commit() -> str:
    pinned = _revision_commit()
    if pinned:
        return pinned
    try:
        return subprocess.run(
            ["git", "-c", f"safe.directory={ROOT}", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "snapshot-without-git"


def git_status_flag() -> str:
    if (ROOT / "REVISION").is_file() and not (ROOT / ".git").exists():
        return "git-archive-snapshot"
    try:
        out = subprocess.run(
            ["git", "-c", f"safe.directory={ROOT}", "status", "--porcelain"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return "clean" if not out else "dirty (regenerate after committing)"
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "git-unavailable"


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
    sidecar = figure_sidecar_payload(
        figure_path,
        artifact_ids=artifact_ids,
        source_table_hashes={a: PINNED_INPUTS[a]["sha256"] for a in artifact_ids},
        plotting_script="scripts/make_workshop_figures.py",
        plotting_config=plotting_config,
        note=note,
        generation_command="python scripts/make_workshop_figures.py",
        figure_artifact_id=f"workshop_figures_2026-08-13-v1:{figure_path.stem}",
    )
    write_json(figure_path.with_suffix(figure_path.suffix + ".json"), sidecar)


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
    """Conceptual signed-defect schematic (not data).

    Communicates: two time-dependent fields; an averaged scalar loses
    temporal structure; solvers sample stage locations; signed local
    defects cancel or amplify; transported endpoint error can reverse
    the scalar ranking. It does not depict any measured mechanism.
    """
    import numpy as np

    fig, (ax1, ax2, ax3) = plt.subplots(
        1,
        3,
        figsize=(5.5, 1.4),
        gridspec_kw={"width_ratios": [1.3, 1.05, 0.7], "wspace": 0.55},
    )

    t = np.linspace(0.0, 1.0, 400)
    field_a = 1.05 + 0.25 * np.sin(2.2 * np.pi * t)
    field_b = 1.25 + 0.55 * np.sin(4.4 * np.pi * t + 0.6)
    ax1.plot(t, field_a, color=COLOR_LINEAR, lw=1.6)
    ax1.plot(t, field_b, color=COLOR_VP, lw=1.6, ls="--")
    ax1.text(0.36, 0.72, "path A", color=COLOR_LINEAR, fontsize=8.5)
    ax1.text(0.03, 1.9, "path B", color=COLOR_VP, fontsize=8.5)
    stages = np.linspace(0, 1, 5)[:-1]
    ax1.plot(stages, np.interp(stages, t, field_a), "o", ms=4, color=COLOR_LINEAR)
    ax1.plot(stages, np.interp(stages, t, field_b), "s", ms=4, color=COLOR_VP)
    ax1.axhline(float(np.mean(field_a)), color=COLOR_LINEAR, lw=0.9, alpha=0.5)
    ax1.axhline(float(np.mean(field_b)), color=COLOR_VP, lw=0.9, alpha=0.5)
    ax1.set_xlabel("time $t$")
    ax1.set_ylabel(r"$\Vert \partial_x b_t \Vert$ (schematic)")
    ax1.set_xlim(0, 1.0)
    ax1.set_ylim(0.45, 2.05)
    ax1.set_title("(a) fields and averages", loc="left")

    steps = np.arange(1, 5)
    defects_a = np.array([0.30, 0.34, 0.38, 0.42])
    defects_b = np.array([0.55, -0.45, 0.50, -0.40])
    width = 0.38
    ax2.bar(steps - width / 2, defects_a, width, color=COLOR_LINEAR, label="path A")
    ax2.bar(
        steps + width / 2,
        defects_b,
        width,
        color=COLOR_VP,
        hatch="//",
        edgecolor="white",
        label="path B",
    )
    ax2.axhline(0.0, color=GRAY, lw=0.9)
    ax2.set_xticks(steps, [str(n) for n in steps])
    ax2.set_xlabel("solver step")
    ax2.set_ylabel("local defect")
    ax2.set_title("(b) signed defects", loc="left")

    totals = [float(np.abs(defects_a.sum())), float(np.abs(defects_b.sum()))]
    bars = ax3.bar(
        [0, 1],
        totals,
        width=0.55,
        color=[COLOR_LINEAR, COLOR_VP],
        hatch=["", "//"],
        edgecolor=["none", "white"],
    )
    ax3.bar_label(bars, ["A", "B"], padding=2, fontsize=8)
    ax3.set_xticks([0, 1], ["path A", "path B"])
    ax3.set_ylim(0, 1.75)
    ax3.set_ylabel("endpoint\nerror")
    ax3.set_title("(c) ranking reversed", loc="left")
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
    fig = plt.figure(figsize=(5.5, 1.78))
    gs = fig.add_gridspec(1, 3, width_ratios=[0.5, 0.5, 1.7], wspace=1.25)
    ax_m = fig.add_subplot(gs[0])
    ax_w = fig.add_subplot(gs[1])
    ax_all = fig.add_subplot(gs[2])

    lin, vp = strongest["linear"], strongest["vp"]
    for ax, key, title in (
        (ax_m, "baseline_metric", "avg. regularity $\\mathcal{R}$"),
        (ax_w, "gaussian_w2", "Gaussian $W_2$"),
    ):
        vals = [lin[key], vp[key]]
        bars = ax.bar(
            [0, 1],
            vals,
            width=0.62,
            color=[COLOR_LINEAR, COLOR_VP],
            hatch=["", "//"],
            edgecolor=["none", "white"],
        )
        ax.bar_label(bars, [f"{v:.2f}" for v in vals], padding=1.5, fontsize=8)
        ax.set_xticks([0, 1], ["lin", "VP"])
        ax.set_title(title, loc="left", fontsize=8.5)
        ax.set_ylim(0, max(vals) * 1.32)
    ax_m.set_ylabel("$\\mathcal{R}[b]$")
    ax_w.set_ylabel("$W_2$")

    # All fourteen blocks: |W2 margin| of the inversion, log scale.
    inversions_sorted = sorted(inversions, key=lambda b: abs(b["w2_delta"]))
    solver_abbrev = {"euler": "Eu", "heun": "He", "rk4": "RK"}
    labels = [
        f"{'AN' if b['family'] == 'anisotropic_gaussian' else 'LR'}"
        f" d{b['dim']} {solver_abbrev[b['solver']]} n{b['nfe']}"
        for b in inversions_sorted
    ]
    y = list(range(len(inversions_sorted)))
    ax_all.hlines(
        y,
        1e-6,
        [abs(b["w2_delta"]) for b in inversions_sorted],
        color="#c9c9c9",
        lw=0.8,
        zorder=1,
    )
    for yi, block in zip(y, inversions_sorted, strict=True):
        prefers_vp = block["w2_delta"] > 0
        ax_all.plot(
            abs(block["w2_delta"]),
            yi,
            marker="s" if prefers_vp else "o",
            ms=5,
            color=COLOR_VP if prefers_vp else COLOR_LINEAR,
            zorder=2,
        )
    ax_all.set_xscale("log")
    ax_all.set_xlim(5e-6, 1.0)
    ax_all.set_yticks(y, labels, fontsize=7)
    ax_all.set_xlabel(r"$W_2$ margin of inversion (log scale)")
    ax_all.set_title("all 14 inversion blocks", loc="left", fontsize=8.5)
    handles = [
        plt.Line2D(
            [],
            [],
            marker="o",
            ls="",
            ms=5,
            color=COLOR_LINEAR,
            label="$W_2$ prefers linear",
        ),
        plt.Line2D(
            [],
            [],
            marker="s",
            ls="",
            ms=5,
            color=COLOR_VP,
            label="$W_2$ prefers VP",
        ),
    ]
    ax_all.legend(handles=handles, frameon=False, loc="lower right", fontsize=7.5)
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
    solver_names = {"euler": "Euler", "heun": "Heun", "rk4": "RK4"}
    fig, axes = plt.subplots(1, 2, figsize=(5.5, 1.42), sharey=True)
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
                ms=5,
                lw=1.8,
                color=SOLVER_COLORS[solver],
            )
            # Direct label at the right end of each line; no legend.
            ax.annotate(
                solver_names[solver],
                xy=(pts[-1]["nfe"], pts[-1]["w2_delta"]),
                xytext=(6, 0),
                textcoords="offset points",
                color=SOLVER_COLORS[solver],
                fontsize=9,
                va="center",
            )
        ax.axhline(0.0, color="#333333", lw=1.0)
        ax.set_xscale("log", base=2)
        ax.set_yscale("symlog", linthresh=1e-4)
        ax.set_xlim(7, 46)
        ax.set_yticks([1e-1, 1e-3, 0.0, -1e-3, -1e-1])
        ax.set_xticks([8, 16, 32], ["8", "16", "32"])
        ax.set_xlabel("NFE (equal across solvers)")
        ax.set_title(f"low-rank target, $d={dim}$", loc="left")
    axes[0].set_ylabel(r"$W_2(\mathrm{linear})-W_2(\mathrm{VP})$")
    fig.tight_layout()
    out = FIGURE_DIR / ("fig3_interaction" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out, [artifact_id]


def main() -> None:
    """Copy the three live workshop figures from the arXiv tree with sidecars.

    Hydra-backed fig2/fig3 are not written into the live workshop directory
    because the anonymous PDF does not include them.
    """
    import shutil

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    arxiv_fig = ROOT / "paper" / "arxiv" / "figures"
    written: list[Path] = []
    for name in ("fig_scalar.pdf", "fig1_regimes.pdf", "fig_inversion_region.pdf"):
        src = arxiv_fig / name
        dst = FIGURE_DIR / name
        if not src.is_file():
            raise FileNotFoundError(f"missing arXiv figure {src}")
        shutil.copy2(src, dst)
        write_sidecar(
            dst,
            artifact_ids=[],
            plotting_config={"kind": "copied_from_arxiv", "source": name},
            note=f"Copied from paper/arxiv/figures/{name} for the anonymous PDF.",
        )
        written.append(dst)
    for path in written:
        print(path.relative_to(ROOT), sha256_file(path)[:16])


if __name__ == "__main__":
    main()
