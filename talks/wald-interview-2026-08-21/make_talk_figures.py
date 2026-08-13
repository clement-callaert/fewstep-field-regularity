"""Build talk data figures from frozen checksum-pinned artifacts.

Writes only into talks/wald-interview-2026-08-21/figures/.
Does not modify paper/gddl2026/figures/.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

TALK_DIR = Path(__file__).resolve().parent
REPO_ROOT = TALK_DIR.parents[1]
FIGURE_DIR = TALK_DIR / "figures"
ARTIFACT_DIR = TALK_DIR / "artifacts"

PINNED_INPUTS = {
    "phase4_gaussian_reproduction_2026-07-24-v1:results": {
        "relpath": "phase4_gaussian_reproduction_2026-07-24-v1/results.json",
        "sha256": "b8930142cba5655ee553aae5ff400cd884c1137e77547d9a5fa94bd4e354973f",
    },
    "phase4_decomposition_2026-07-24-v1:table": {
        "relpath": "phase4_decomposition_2026-07-24-v1/table.json",
        "sha256": "690d068c3693f99f38ddb17b479ab0e63b5ad859835f2092c5420175d954f252",
    },
}

COLOR_LINEAR = "#0072B2"
COLOR_VP = "#D55E00"
SOLVER_COLORS = {"euler": "#0072B2", "heun": "#D55E00", "rk4": "#009E73"}
SOLVER_MARKERS = {"euler": "o", "heun": "s", "rk4": "^"}
GRAY = "#5f6368"

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.7,
        "pdf.fonttype": 42,
    }
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_pinned(artifact_id: str) -> Any:
    entry = PINNED_INPUTS[artifact_id]
    path = ARTIFACT_DIR / str(entry["relpath"])
    if not path.is_file():
        path = REPO_ROOT / "outputs" / str(entry["relpath"])
    if not path.is_file():
        raise FileNotFoundError(f"Missing artifact {artifact_id}: {path}")
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
        "figure_artifact_id": f"wald_talk_2026-08-13:{figure_path.stem}",
        "source_artifact_ids": artifact_ids,
        "source_table_hashes": {
            a: PINNED_INPUTS[a]["sha256"] for a in artifact_ids if a in PINNED_INPUTS
        },
        "plotting_script": "talks/wald-interview-2026-08-21/make_talk_figures.py",
        "plotting_config": plotting_config,
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        "figure_checksum_sha256": sha256_file(figure_path),
        "note": note,
    }
    sidecar_path = figure_path.with_suffix(figure_path.suffix + ".json")
    sidecar_path.write_text(
        json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def phase4_blocks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
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


def figure_strongest(blocks: list[dict[str, Any]]) -> Path:
    inversions = [b for b in blocks if b["is_inversion"]]
    strongest = max(inversions, key=lambda b: abs(b["w2_delta"]))
    lin, vp = strongest["linear"], strongest["vp"]
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.6))
    specs = (
        (
            axes[0],
            "baseline_metric",
            r"averaged regularity $\mathcal{R}[b]$",
            "lower is preferred by the criterion",
        ),
        (
            axes[1],
            "gaussian_w2",
            r"endpoint Gaussian $W_2$",
            "lower is preferred as the error",
        ),
    )
    for ax, key, title, xlabel in specs:
        vals = [lin[key], vp[key]]
        bars = ax.bar(
            [0, 1],
            vals,
            width=0.62,
            color=[COLOR_LINEAR, COLOR_VP],
            hatch=["", "//"],
            edgecolor=["none", "white"],
        )
        ax.bar_label(bars, [f"{v:.3f}" for v in vals], padding=3, fontsize=11)
        ax.set_xticks([0, 1], ["linear", "VP"])
        ax.set_title(title, loc="left")
        ax.set_xlabel(xlabel)
        ax.set_ylim(0, max(vals) * 1.28)
    axes[0].set_ylabel("value (dimensionless)")
    axes[1].set_ylabel(r"$W_2$ (state units)")
    fig.suptitle(
        "Strongest inversion: low-rank Gaussian, $d=8$, Euler, NFE 8",
        fontsize=12,
        y=1.02,
    )
    out = FIGURE_DIR / "fig_strongest_inversion.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    write_sidecar(
        out,
        artifact_ids=["phase4_gaussian_reproduction_2026-07-24-v1:results"],
        plotting_config={"kind": "strongest_inversion_bars"},
        note="Data figure from frozen Phase 4 results. Lower is preferred on both axes.",
    )
    return out


def figure_inversions14(blocks: list[dict[str, Any]]) -> Path:
    inversions = [b for b in blocks if b["is_inversion"]]
    if len(inversions) != 14:
        raise ValueError(f"Expected 14 inversions, got {len(inversions)}")
    inversions_sorted = sorted(inversions, key=lambda b: abs(b["w2_delta"]))
    solver_abbrev = {"euler": "Eu", "heun": "He", "rk4": "RK"}
    labels = [
        f"{'AN' if b['family'] == 'anisotropic_gaussian' else 'LR'}"
        f" d{b['dim']} {solver_abbrev[b['solver']]} n{b['nfe']}"
        for b in inversions_sorted
    ]
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    y = list(range(len(inversions_sorted)))
    ax.hlines(
        y,
        1e-6,
        [abs(b["w2_delta"]) for b in inversions_sorted],
        color="#c9c9c9",
        lw=1.0,
        zorder=1,
    )
    for yi, block in zip(y, inversions_sorted, strict=True):
        prefers_vp = block["w2_delta"] > 0
        ax.plot(
            abs(block["w2_delta"]),
            yi,
            marker="s" if prefers_vp else "o",
            ms=8,
            color=COLOR_VP if prefers_vp else COLOR_LINEAR,
            zorder=2,
        )
    ax.set_xscale("log")
    ax.set_xlim(5e-6, 1.0)
    ax.set_yticks(y, labels)
    ax.set_xlabel(r"$W_2$ margin of inversion (log scale; compresses, never exaggerates)")
    ax.set_title("All 14 inversion blocks in the tested grid (36 blocks total)")
    handles = [
        plt.Line2D(
            [],
            [],
            marker="o",
            ls="",
            ms=8,
            color=COLOR_LINEAR,
            label=r"$W_2$ prefers linear",
        ),
        plt.Line2D(
            [],
            [],
            marker="s",
            ls="",
            ms=8,
            color=COLOR_VP,
            label=r"$W_2$ prefers VP",
        ),
    ]
    ax.legend(handles=handles, frameon=False, loc="lower right")
    out = FIGURE_DIR / "fig_inversions14.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    write_sidecar(
        out,
        artifact_ids=["phase4_gaussian_reproduction_2026-07-24-v1:results"],
        plotting_config={"kind": "all_inversion_margins", "x_scale": "log"},
        note="Data figure. 14 of 36 blocks. Not a population frequency.",
    )
    return out


def figure_interaction(blocks: list[dict[str, Any]]) -> Path:
    lowrank = [b for b in blocks if b["family"] == "low_rank_gaussian"]
    solver_names = {"euler": "Euler", "heun": "Heun", "rk4": "RK4"}
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.7), sharey=True)
    for ax, dim in zip(axes, (2, 8), strict=True):
        for solver in ("euler", "heun", "rk4"):
            pts = sorted(
                (b for b in lowrank if b["dim"] == dim and b["solver"] == solver),
                key=lambda b: b["nfe"],
            )
            ax.plot(
                [b["nfe"] for b in pts],
                [b["w2_delta"] for b in pts],
                marker=SOLVER_MARKERS[solver],
                ms=7,
                lw=2.0,
                color=SOLVER_COLORS[solver],
                ls="-" if solver == "euler" else ("--" if solver == "heun" else ":"),
            )
            ax.annotate(
                solver_names[solver],
                xy=(pts[-1]["nfe"], pts[-1]["w2_delta"]),
                xytext=(6, 0),
                textcoords="offset points",
                color=SOLVER_COLORS[solver],
                fontsize=11,
                va="center",
            )
        ax.axhline(0.0, color="#333333", lw=1.0)
        ax.set_xscale("log", base=2)
        ax.set_yscale("symlog", linthresh=1e-4)
        ax.set_xlim(7, 48)
        ax.set_yticks([1e-1, 1e-3, 0.0, -1e-3, -1e-1])
        ax.set_xticks([8, 16, 32], ["8", "16", "32"])
        ax.set_xlabel("NFE (equal across solvers)")
        ax.set_title(f"low-rank target, $d={dim}$", loc="left")
    axes[0].set_ylabel(r"$W_2(\mathrm{linear})-W_2(\mathrm{VP})$")
    axes[0].text(
        8.2,
        0.35,
        "positive: VP has smaller $W_2$",
        fontsize=8,
        color=GRAY,
    )
    axes[0].text(
        8.2,
        -0.45,
        "negative: linear has smaller $W_2$",
        fontsize=8,
        color=GRAY,
    )
    fig.suptitle(
        "Signed equal-NFE $W_2$ margin in the low-rank family (symlog axis)",
        fontsize=12,
        y=1.02,
    )
    out = FIGURE_DIR / "fig_interaction.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    write_sidecar(
        out,
        artifact_ids=["phase4_gaussian_reproduction_2026-07-24-v1:results"],
        plotting_config={"kind": "lowrank_solver_path_interaction", "y_scale": "symlog"},
        note="Data figure. Positive prefers VP. Negative prefers linear.",
    )
    return out


def figure_eigenmode() -> Path:
    artifact_id = "phase4_decomposition_2026-07-24-v1:table"
    payload = load_pinned(artifact_id)
    selected: dict[str, dict[str, Any]] = {}
    for row in payload["rows"]:
        if (
            row["target_family"] == "low_rank_gaussian"
            and row["dim"] == 8
            and row["solver"] == "euler"
            and row["nfe"] == 8
        ):
            selected[str(row["path"])] = row
    lin, vp = selected["linear"], selected["variance_preserving"]
    fig, (ax_w2, ax_def) = plt.subplots(
        1, 2, figsize=(8.8, 3.6), gridspec_kw={"wspace": 0.35}
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
    ax_w2.set_ylabel(r"$W_2^2$ contribution (squared state units)")
    ax_w2.set_title("exact modal $W_2^2$ split", loc="left")
    ax_w2.legend(frameon=False)

    lin_dom = lin["modes"][int(lin["dominant_mode_index"])]
    vp_dom = vp["modes"][int(vp["dominant_mode_index"])]
    lin_tr = [float(x) for x in lin_dom["transported_local_contributions"]]
    vp_tr = [float(x) for x in vp_dom["transported_local_contributions"]]
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
    ax_def.set_ylabel("transported signed factor defect")
    ax_def.set_title(
        f"dominant mode {int(lin['dominant_mode_index'])} (exact identity)",
        loc="left",
    )
    fig.suptitle(
        "Backup data: strongest block modal split (decomposition table)",
        fontsize=12,
        y=1.02,
    )
    out = FIGURE_DIR / "fig_eigenmode.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    write_sidecar(
        out,
        artifact_ids=[artifact_id],
        plotting_config={"kind": "strongest_block_eigenmode"},
        note="Data figure from post-hoc decomposition. Uses W_2^2 modal split.",
    )
    return out


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    payload = load_pinned("phase4_gaussian_reproduction_2026-07-24-v1:results")
    blocks = phase4_blocks(payload["rows"])
    inversions = [b for b in blocks if b["is_inversion"]]
    if len(payload["rows"]) != 72 or len(blocks) != 36 or len(inversions) != 14:
        raise RuntimeError("Unexpected grid counts")
    paths = [
        figure_strongest(blocks),
        figure_inversions14(blocks),
        figure_interaction(blocks),
        figure_eigenmode(),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
