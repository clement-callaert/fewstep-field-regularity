"""Build arXiv figures with provenance sidecars.

Inputs are explicit artifact files with pinned SHA-256 checksums. The
script refuses to run on a checksum mismatch and never scans directories.
Figure 1 is conceptual and consumes no artifact. Figures 2, eigenmode, and 3
read pinned Phase 4 tables only.
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
FIGURE_DIR = ROOT / "paper" / "arxiv" / "figures"
FIGURE_SUFFIX = ".pdf"

# Pinned artifact inputs. No other file may be read.
PINNED_INPUTS = {
    "phase4_gaussian_reproduction_2026-07-24-v1:results": {
        "path": "outputs/phase4_gaussian_reproduction_2026-07-24-v1/results.json",
        "sha256": "b8930142cba5655ee553aae5ff400cd884c1137e77547d9a5fa94bd4e354973f",
    },
    "phase4_decomposition_2026-07-24-v1:table": {
        "path": "outputs/phase4_decomposition_2026-07-24-v1/table.json",
        "sha256": "690d068c3693f99f38ddb17b479ab0e63b5ad859835f2092c5420175d954f252",
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

# Strongest inversion block selection for the eigenmode figure.
# Source: phase4_gaussian_reproduction_2026-07-24-v1:results.
STRONGEST_BLOCK = {
    "target_family": "low_rank_gaussian",
    "dim": 8,
    "solver": "euler",
    "nfe": 8,
}

# Categorical palette from an Okabe-Ito subset; checked for CVD safety.
COLOR_LINEAR = "#0072B2"
COLOR_VP = "#D55E00"
SOLVER_COLORS = {"euler": "#0072B2", "heun": "#D55E00", "rk4": "#009E73"}
SOLVER_MARKERS = {"euler": "o", "heun": "s", "rk4": "^"}
GRAY = "#5f6368"

plt.rcParams.update(
    {
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
    }
)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run git with a per-invocation safe.directory for this repo root.

    Does not modify the user's git config. Needed when the process user
    differs from the directory owner (for example root in WSL).
    """
    return subprocess.run(
        ["git", "-c", f"safe.directory={ROOT}", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )


def git_commit() -> str:
    return _git("rev-parse", "HEAD").stdout.strip()


def git_status_flag() -> str:
    out = _git("status", "--porcelain").stdout.strip()
    return "clean" if not out else "dirty (regenerate after committing)"


def load_pinned(artifact_id: str) -> Any:
    """Load one pinned JSON artifact after SHA-256 verification.

    Inputs: artifact_id key in PINNED_INPUTS.
    Outputs: parsed JSON object.
    Units: none; byte checksum only.
    Precision: checksum must match the pinned hex digest exactly.
    """
    if artifact_id not in PINNED_INPUTS:
        raise KeyError(f"Missing pinned input entry: {artifact_id}")
    entry = PINNED_INPUTS[artifact_id]
    for field in ("path", "sha256"):
        if field not in entry:
            raise KeyError(f"Missing pinned field {field!r} for {artifact_id}")
    path = ROOT / str(entry["path"])
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing pinned artifact file for {artifact_id}: {path}"
        )
    actual = sha256_file(path)
    if actual != entry["sha256"]:
        raise ValueError(f"Checksum mismatch for {artifact_id}: {actual}")
    return json.loads(path.read_text(encoding="utf-8"))


def require_row_fields(
    row: dict[str, Any], fields: tuple[str, ...], *, context: str
) -> None:
    """Raise KeyError naming the first missing field on a decomposition row."""
    for field in fields:
        if field not in row:
            raise KeyError(f"Missing field {field!r} in {context}")


def write_sidecar(
    figure_path: Path,
    *,
    artifact_ids: list[str],
    plotting_config: dict[str, Any],
    note: str,
) -> None:
    sidecar = {
        "figure_artifact_id": f"arxiv_figures_2026-08-13-v1:{figure_path.stem}",
        "source_run_ids": sorted({a.split(":")[0] for a in artifact_ids})
        or ["none_conceptual"],
        "source_artifact_ids": artifact_ids,
        "source_table_hashes": {a: PINNED_INPUTS[a]["sha256"] for a in artifact_ids},
        "plotting_script": "scripts/make_arxiv_figures.py",
        "plotting_config": plotting_config,
        "git_commit": git_commit(),
        "git_status": git_status_flag(),
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
    """Write the conceptual signed-defect schematic.

    Inputs: none; no artifact bytes are read.
    Outputs: path to the written figure PDF.
    Units: schematic axes only; not measured data.
    Precision: illustrative curves; not tied to an NFE budget or artifact ID.
    """
    import numpy as np

    fig, (ax1, ax2, ax3) = plt.subplots(
        1,
        3,
        figsize=(6.8, 2.1),
        gridspec_kw={"width_ratios": [1.3, 1.05, 0.7], "wspace": 0.45},
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
    # Spacing uses gridspec wspace; tight_layout conflicts with that on mpl 3.11+.
    out = FIGURE_DIR / ("fig1_conceptual" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def figure2_inversions() -> tuple[Path, list[str]]:
    """Strongest inversion plus all 14 of 36 Phase 4 inversion blocks.

    Inputs: pinned phase4_gaussian_reproduction_2026-07-24-v1:results.
    Outputs: path to fig2_inversions.pdf and source artifact IDs.
    Units: averaged regularity dimensionless; Gaussian W2 in the ambient metric.
    Precision: float64 rows from the pinned artifact; equal-NFE blocks only.
    """
    artifact_id = "phase4_gaussian_reproduction_2026-07-24-v1:results"
    payload = load_pinned(artifact_id)
    if "rows" not in payload:
        raise KeyError(
            "Missing field 'rows' in phase4_gaussian_reproduction_2026-07-24-v1:results"
        )
    blocks = phase4_blocks(payload["rows"])
    inversions = [b for b in blocks if b["is_inversion"]]
    if len(inversions) != 14:
        raise ValueError(f"Expected 14 Phase 4 inversion blocks, got {len(inversions)}")

    strongest = max(inversions, key=lambda b: abs(b["w2_delta"]))
    fig = plt.figure(figsize=(6.8, 2.4))
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

    # Absolute W2 margin of each inversion block from the pinned Phase 4
    # reproduction results, log scale.
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
    # Spacing uses gridspec wspace; tight_layout conflicts with that on mpl 3.11+.
    out = FIGURE_DIR / ("fig2_inversions" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out, [artifact_id]


def figure_eigenmode() -> tuple[Path, list[str]]:
    """Signed-defect and eigenmode decomposition for the strongest comparison.

    Inputs: pinned phase4_decomposition_2026-07-24-v1:table.
    Outputs: path to fig_eigenmode.pdf and source artifact IDs.
    Units: W2-squared modal contributions; transported local contributions
    dimensionless on the log-factor scale of the decomposition.
    Precision: float64 exact modal identity from the pinned table; any
    aggregate proxy remains post-hoc and is not plotted as predictive.
    """
    artifact_id = "phase4_decomposition_2026-07-24-v1:table"
    payload = load_pinned(artifact_id)
    if "rows" not in payload:
        raise KeyError(f"Missing field 'rows' in {artifact_id}")
    required = (
        "target_family",
        "dim",
        "solver",
        "nfe",
        "path",
        "modes",
        "dominant_mode_index",
    )
    selected: dict[str, dict[str, Any]] = {}
    for row in payload["rows"]:
        require_row_fields(row, required, context=artifact_id)
        if (
            row["target_family"] == STRONGEST_BLOCK["target_family"]
            and row["dim"] == STRONGEST_BLOCK["dim"]
            and row["solver"] == STRONGEST_BLOCK["solver"]
            and row["nfe"] == STRONGEST_BLOCK["nfe"]
        ):
            selected[str(row["path"])] = row
    for path_name in ("linear", "variance_preserving"):
        if path_name not in selected:
            raise KeyError(
                f"Missing strongest-block row path={path_name!r} in {artifact_id} "
                f"for {STRONGEST_BLOCK}"
            )

    lin, vp = selected["linear"], selected["variance_preserving"]
    for label, row in (("linear", lin), ("variance_preserving", vp)):
        require_row_fields(
            row, ("modes", "dominant_mode_index"), context=f"{artifact_id}:{label}"
        )
        if not row["modes"]:
            raise KeyError(f"Missing field 'modes' entries in {artifact_id}:{label}")
        dom = int(row["dominant_mode_index"])
        if dom < 0 or dom >= len(row["modes"]):
            raise KeyError(
                f"Missing field modes[{dom}] for dominant_mode_index in {artifact_id}:{label}"
            )
        mode = row["modes"][dom]
        require_row_fields(
            mode,
            (
                "mode_index",
                "w2_squared_contribution",
                "transported_local_contributions",
                "signed_local_log_defect_sum",
            ),
            context=f"{artifact_id}:{label}:modes[{dom}]",
        )
        for i, m in enumerate(row["modes"]):
            require_row_fields(
                m,
                ("mode_index", "w2_squared_contribution"),
                context=f"{artifact_id}:{label}:modes[{i}]",
            )

    fig, (ax_w2, ax_def) = plt.subplots(
        1, 2, figsize=(6.8, 2.2), gridspec_kw={"wspace": 0.35}
    )
    mode_idx = [int(m["mode_index"]) for m in lin["modes"]]
    width = 0.38
    ax_w2.bar(
        [i - width / 2 for i in mode_idx],
        [float(m["w2_squared_contribution"]) for m in lin["modes"]],
        width,
        color=COLOR_LINEAR,
        label="linear",
    )
    ax_w2.bar(
        [i + width / 2 for i in mode_idx],
        [float(m["w2_squared_contribution"]) for m in vp["modes"]],
        width,
        color=COLOR_VP,
        hatch="//",
        edgecolor="white",
        label="VP",
    )
    ax_w2.set_xlabel("covariance eigenmode")
    ax_w2.set_ylabel(r"$W_2^2$ contribution")
    ax_w2.set_title("exact modal $W_2^2$ split", loc="left", fontsize=8.5)
    ax_w2.legend(frameon=False, fontsize=7.5)

    lin_dom = lin["modes"][int(lin["dominant_mode_index"])]
    vp_dom = vp["modes"][int(vp["dominant_mode_index"])]
    lin_tr = [float(x) for x in lin_dom["transported_local_contributions"]]
    vp_tr = [float(x) for x in vp_dom["transported_local_contributions"]]
    if len(lin_tr) != len(vp_tr):
        raise ValueError(
            "transported_local_contributions length mismatch between linear and VP "
            "dominant modes"
        )
    steps = list(range(1, len(lin_tr) + 1))
    ax_def.bar(
        [s - width / 2 for s in steps],
        lin_tr,
        width,
        color=COLOR_LINEAR,
        label="linear",
    )
    ax_def.bar(
        [s + width / 2 for s in steps],
        vp_tr,
        width,
        color=COLOR_VP,
        hatch="//",
        edgecolor="white",
        label="VP",
    )
    ax_def.axhline(0.0, color=GRAY, lw=0.9)
    ax_def.set_xticks(steps, [str(s) for s in steps])
    ax_def.set_xlabel("solver step")
    ax_def.set_ylabel("transported signed defect")
    ax_def.set_title(
        f"dominant mode {int(lin['dominant_mode_index'])} (exact identity)",
        loc="left",
        fontsize=8.5,
    )
    out = FIGURE_DIR / ("fig_eigenmode" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out, [artifact_id]


def figure3_interaction() -> tuple[Path, list[str]]:
    """Low-rank solver-path interaction across solvers and NFE.

    Inputs: pinned phase4_gaussian_reproduction_2026-07-24-v1:results.
    Outputs: path to fig3_interaction.pdf and source artifact IDs.
    Units: signed Gaussian W2 margin versus equal-NFE budget.
    Precision: float64 rows; Euler, Heun, and RK4 at equal NFE.
    """
    artifact_id = "phase4_gaussian_reproduction_2026-07-24-v1:results"
    payload = load_pinned(artifact_id)
    if "rows" not in payload:
        raise KeyError(
            "Missing field 'rows' in phase4_gaussian_reproduction_2026-07-24-v1:results"
        )
    blocks = [
        b for b in phase4_blocks(payload["rows"]) if b["family"] == "low_rank_gaussian"
    ]
    solver_names = {"euler": "Euler", "heun": "Heun", "rk4": "RK4"}
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.2), sharey=True)
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
            # Place a direct label at the right end of each line; omit a legend.
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
        note=(
            "Source: phase4_gaussian_reproduction_2026-07-24-v1:results. "
            "Log margin axis for 14 of 36 inversion blocks in the tested grid."
        ),
    )
    fig_e, ids_e = figure_eigenmode()
    write_sidecar(
        fig_e,
        artifact_ids=ids_e,
        plotting_config={
            "kind": "eigenmode_signed_defect_strongest_block",
            "block": STRONGEST_BLOCK,
        },
        note=(
            "Source: phase4_decomposition_2026-07-24-v1:table. "
            "The modal decomposition is exact; any aggregate solver proxy is "
            "post-hoc and in-sample and is not shown as predictive."
        ),
    )
    fig3, ids3 = figure3_interaction()
    write_sidecar(
        fig3,
        artifact_ids=ids3,
        plotting_config={
            "kind": "lowrank_solver_path_interaction",
            "y_scale": "symlog linthresh 1e-4",
        },
        note=(
            "Source: phase4_gaussian_reproduction_2026-07-24-v1:results. "
            "Signed low-rank W2 margins versus equal-NFE Euler, Heun, and RK4."
        ),
    )
    for path in (fig1, fig2, fig_e, fig3):
        print(path.relative_to(ROOT), sha256_file(path)[:16])


if __name__ == "__main__":
    main()
