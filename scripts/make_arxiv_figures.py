"""Build arXiv figures with provenance sidecars.

Inputs are explicit artifact files with pinned SHA-256 checksums. The
script refuses to run on a checksum mismatch and never scans directories.
Figure 1 is conceptual and consumes no artifact. Figures 2, eigenmode, and 3
read pinned Phase 4 tables only.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt

from fewstep_regularities.utils.hashing import sha256_file
from fewstep_regularities.utils.provenance import figure_sidecar_payload, write_json

ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "paper" / "arxiv" / "figures"
FIGURE_SUFFIX = ".pdf"

# Pinned frozen Hydra tables. These live in paper/arxiv/frozen_runs/ so
# figures regenerate without the gitignored outputs/ tree. Checksums must
# match the compact-artifact manifest.
PINNED_INPUTS = {
    "phase4_gaussian_reproduction_2026-07-24-v1:results": {
        "path": "paper/arxiv/frozen_runs/phase4_gaussian_reproduction_2026-07-24-v1/results.json",
        "sha256": "b8930142cba5655ee553aae5ff400cd884c1137e77547d9a5fa94bd4e354973f",
    },
    "phase4_decomposition_2026-07-24-v1:table": {
        "path": "paper/arxiv/frozen_runs/phase4_decomposition_2026-07-24-v1/table.json",
        "sha256": "690d068c3693f99f38ddb17b479ab0e63b5ad859835f2092c5420175d954f252",
    },
    "workshop_external_validation_2026-07-24-v1:results": {
        "path": "paper/arxiv/frozen_runs/workshop_external_validation_2026-07-24-v1/results.json",
        "sha256": "4234bc2baefa8390414db9e037c7d028408cb04591e2b6302524ed8ad3bd205d",
    },
    "workshop_external_validation_2026-07-24-v1:inversions": {
        "path": "paper/arxiv/frozen_runs/workshop_external_validation_2026-07-24-v1/inversions.json",
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
COLOR_SCALAR = "#E69F00"
COLOR_MINIMIZER = "#009E73"
SOLVER_COLORS = {"euler": "#0072B2", "heun": "#D55E00", "rk4": "#009E73"}
SOLVER_MARKERS = {"euler": "o", "heun": "s", "rk4": "^"}
GRAY = "#5f6368"
FIGWIDTH = 5.45


def apply_paper_style() -> None:
    plt.rcParams.update(
        {
            "text.usetex": False,
            "mathtext.fontset": "cm",
            "font.family": "serif",
            "font.serif": ["DejaVu Serif"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
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


apply_paper_style()


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
        return _git("rev-parse", "HEAD").stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "snapshot-without-git"


def git_status_flag() -> str:
    if (ROOT / "REVISION").is_file() and not (ROOT / ".git").exists():
        return "git-archive-snapshot"
    try:
        out = _git("status", "--porcelain").stdout.strip()
        return "clean" if not out else "dirty (regenerate after committing)"
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "git-unavailable"


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
    sidecar = figure_sidecar_payload(
        figure_path,
        artifact_ids=artifact_ids,
        source_table_hashes={a: PINNED_INPUTS[a]["sha256"] for a in artifact_ids},
        plotting_script="scripts/make_arxiv_figures.py",
        plotting_config=plotting_config,
        note=note,
        generation_command="python scripts/make_arxiv_figures.py",
        figure_artifact_id=f"arxiv_figures_2026-08-13-v1:{figure_path.stem}",
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


def figure1_regimes() -> Path:
    """Three-comparison bar overview: pairwise, shared-schedule, four-path census.

    Inputs: paper/arxiv/artifacts/geometries.json via exact-moment modal RK.
    Outputs: path to the written figure PDF.
    Units: continuous R dimensionless; Gaussian W2 in the ambient metric.
    Precision: float64 exact-moment factors; headline blocks Euler NFE 8.
    """
    import numpy as np

    from fewstep_regularities.analysis.ranking_grids import four_path_scores

    payload = json.loads(
        (ROOT / "paper/arxiv/artifacts/geometries.json").read_text(encoding="utf-8")
    )
    low8 = four_path_scores(payload["low_rank_d8"]["eigenvalues"], "euler", 8)
    aniso8 = four_path_scores(payload["anisotropic_d8"]["eigenvalues"], "euler", 8)

    def _bars(
        ax: Any, names: list[str], colors: list[str], values: list[float]
    ) -> None:
        x = np.arange(len(names))
        bars = ax.bar(x, values, color=colors, width=0.62)
        tick_size = 6.5 if len(names) > 2 else 7
        ax.set_xticks(x, names, fontsize=tick_size)
        ax.bar_label(bars, [f"{v:.3g}" for v in values], padding=1.2, fontsize=7)
        ax.set_ylim(0.0, max(values) * 1.32)

    fig, axes = plt.subplots(3, 2, figsize=(FIGWIDTH, 4.2), layout="constrained")
    fig.set_constrained_layout_pads(w_pad=0.02, h_pad=0.04, hspace=0.08, wspace=0.06)

    def _panel_label(ax: Any, text: str) -> None:
        ax.set_title(text, loc="left", fontsize=7)

    _bars(
        axes[0, 0],
        ["lin", "VP"],
        [COLOR_LINEAR, COLOR_VP],
        [low8["linear"].regularity, low8["variance_preserving"].regularity],
    )
    _bars(
        axes[0, 1],
        ["lin", "VP"],
        [COLOR_LINEAR, COLOR_VP],
        [low8["linear"].w2, low8["variance_preserving"].w2],
    )
    axes[0, 0].set_ylabel(r"$\mathcal{R}$")
    axes[0, 1].set_ylabel(r"$W_2$")
    _panel_label(axes[0, 0], r"(a) lin vs VP")

    _bars(
        axes[1, 0],
        ["VP", "Ex. 3.3"],
        [COLOR_VP, COLOR_SCALAR],
        [
            aniso8["variance_preserving"].regularity,
            aniso8["log_covariance_scalar"].regularity,
        ],
    )
    _bars(
        axes[1, 1],
        ["VP", "Ex. 3.3"],
        [COLOR_VP, COLOR_SCALAR],
        [aniso8["variance_preserving"].w2, aniso8["log_covariance_scalar"].w2],
    )
    axes[1, 0].set_ylabel(r"$\mathcal{R}$")
    axes[1, 1].set_ylabel(r"$W_2$")
    _panel_label(axes[1, 0], r"(b) VP vs Chen")

    _bars(
        axes[2, 0],
        ["lin", "VP", "Ex. 3.3", "pm"],
        [COLOR_LINEAR, COLOR_VP, COLOR_SCALAR, COLOR_MINIMIZER],
        [
            low8["linear"].regularity,
            low8["variance_preserving"].regularity,
            low8["log_covariance_scalar"].regularity,
            low8["log_covariance"].regularity,
        ],
    )
    _bars(
        axes[2, 1],
        ["lin", "VP", "Ex. 3.3", "pm"],
        [COLOR_LINEAR, COLOR_VP, COLOR_SCALAR, COLOR_MINIMIZER],
        [
            low8["linear"].w2,
            low8["variance_preserving"].w2,
            low8["log_covariance_scalar"].w2,
            low8["log_covariance"].w2,
        ],
    )
    axes[2, 0].set_ylabel(r"$\mathcal{R}$")
    axes[2, 1].set_ylabel(r"$W_2$")
    _panel_label(axes[2, 0], r"(c) four paths")

    r_lin = low8["linear"].regularity
    r_vp = low8["variance_preserving"].regularity
    r_sc = low8["log_covariance_scalar"].regularity
    r_pm = low8["log_covariance"].regularity
    if abs(r_lin - 2.9441044082631174) > 1e-9:
        raise ValueError(f"fig1(c) linear R is {r_lin}, expected low-rank d=8")
    if abs(r_vp - 4.730543813636288) > 1e-9:
        raise ValueError(f"fig1(c) VP R is {r_vp}, expected low-rank d=8")
    if abs(r_sc - 11.418837310605857) > 1e-9:
        raise ValueError(f"fig1(c) Chen R is {r_sc}, expected low-rank d=8")
    if abs(r_pm - 2.243602963703273) > 1e-9:
        raise ValueError(f"fig1(c) per-mode R is {r_pm}, expected low-rank d=8")
    if (
        aniso8["linear"].regularity > 1.5
        or abs(aniso8["linear"].regularity - r_lin) < 0.5
    ):
        raise ValueError("panel (b) must use anisotropic d=8, not low-rank")

    out = FIGURE_DIR / ("fig1_regimes" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    workshop = (
        ROOT / "paper" / "gddl2026" / "figures" / ("fig1_regimes" + FIGURE_SUFFIX)
    )
    workshop.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(workshop, bbox_inches="tight")
    plt.close(fig)
    return out


def figure_four_paths() -> Path:
    """Four-path R and Euler-8 W2 on the four centered geometries.

    Inputs: paper/arxiv/artifacts/geometries.json and exact-moment modal RK.
    Outputs: path to fig_four_paths.pdf.
    Units: continuous R dimensionless; Gaussian W2 in the ambient metric.
    Precision: float64 exact-moment factors; R by adaptive quadrature except
    the per-mode log-covariance closed form.
    """
    import numpy as np

    from fewstep_regularities.analysis.ranking_grids import (
        FOUR_PATHS,
        GEOM_KEYS,
        four_path_scores,
    )

    payload = json.loads(
        (ROOT / "paper/arxiv/artifacts/geometries.json").read_text(encoding="utf-8")
    )
    labels = {
        "linear": "linear",
        "variance_preserving": "VP",
        "log_covariance_scalar": "Ex. 3.3",
        "log_covariance": r"per-mode",
    }
    colors = {
        "linear": COLOR_LINEAR,
        "variance_preserving": COLOR_VP,
        "log_covariance_scalar": COLOR_SCALAR,
        "log_covariance": COLOR_MINIMIZER,
    }
    tick_labels = [r"$d{=}2$", r"$d{=}8$", r"$d{=}2$", r"$d{=}8$"]
    r_vals = {path: [] for path in FOUR_PATHS}
    w_vals = {path: [] for path in FOUR_PATHS}
    for key, _family, _dim in GEOM_KEYS:
        eigenvalues = payload[key]["eigenvalues"]
        scores = four_path_scores(eigenvalues, "euler", 8)
        for path in FOUR_PATHS:
            r_vals[path].append(scores[path].regularity)
            w_vals[path].append(scores[path].w2)

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.05), layout="constrained")
    x = np.arange(len(tick_labels), dtype=float)
    width = 0.18
    offsets = (-1.5, -0.5, 0.5, 1.5)
    for ax, store, ylabel, title in (
        (
            axes[0],
            r_vals,
            r"$R=\int_0^1\Vert A(t)\Vert_2^2\,dt$",
            "regularity (lower preferred)",
        ),
        (
            axes[1],
            w_vals,
            r"Euler $W_2$ at NFE $8$",
            "endpoint error (lower preferred)",
        ),
    ):
        for offset, path in zip(offsets, FOUR_PATHS, strict=True):
            ax.bar(
                x + offset * width,
                store[path],
                width,
                color=colors[path],
                label=labels[path],
            )
        ax.set_xticks(x, [r"$d{=}2$", r"$d{=}8$", r"$d{=}2$", r"$d{=}8$"], fontsize=8)
        ax.annotate(
            "aniso.",
            xy=(0.5, 0.0),
            xycoords=("data", "axes fraction"),
            xytext=(0, -16),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=8,
        )
        ax.annotate(
            "factor+noise",
            xy=(2.5, 0.0),
            xycoords=("data", "axes fraction"),
            xytext=(0, -16),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=8,
        )
        ax.set_ylabel(ylabel)
        ax.set_title(title, loc="left", fontsize=8.5)
        ax.set_yscale("log")
        ax.tick_params(axis="x", pad=2)
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        legend_labels,
        loc="upper center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 1.08),
        fontsize=8,
    )
    out = FIGURE_DIR / ("fig_four_paths" + FIGURE_SUFFIX)
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
    fig = plt.figure(figsize=(FIGWIDTH, 2.4))
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
        1, 2, figsize=(FIGWIDTH, 2.2), gridspec_kw={"wspace": 0.35}
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
    fig, axes = plt.subplots(1, 2, figsize=(FIGWIDTH, 2.2), sharey=True)
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
        title = (
            rf"rank-2 factor+noise target, $d={dim}$"
            if dim == 8
            else rf"factor+noise target, $d={dim}$"
        )
        ax.set_title(title, loc="left")
    axes[0].set_ylabel(r"$W_2(\mathrm{linear})-W_2(\mathrm{VP})$")
    fig.tight_layout()
    out = FIGURE_DIR / ("fig3_interaction" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out, [artifact_id]


def figure_scalar_counterexample() -> Path:
    """Certified 1-D counterexample: drifts plus exact R and Heun-8 W2 bars."""
    import numpy as np

    from fewstep_regularities.analysis.affine_flow import scalar_drift
    from fewstep_regularities.analysis.scalar_gaussian_counterexample import (
        certify,
        linear_regularity,
        vp_regularity,
    )

    eigenvalue = 4.0
    t = np.linspace(0.0, 1.0, 401)
    a_lin = np.array([scalar_drift("linear", eigenvalue, ti) for ti in t])
    a_vp = np.array([scalar_drift("variance_preserving", eigenvalue, ti) for ti in t])
    nodes = np.array([0.0, 0.25, 0.5, 0.75])
    a_lin_nodes = np.array([scalar_drift("linear", eigenvalue, ti) for ti in nodes])
    a_vp_nodes = np.array(
        [scalar_drift("variance_preserving", eigenvalue, ti) for ti in nodes]
    )
    certified = certify()
    r_lin = float(linear_regularity())
    r_vp = float(vp_regularity())
    w_lin = float(certified.linear_w2)
    w_vp = float(certified.vp_w2_interval[0])

    fig = plt.figure(figsize=(FIGWIDTH, 4.45), layout="constrained")
    grid = fig.add_gridspec(2, 2, height_ratios=(1.45, 1.0))
    ax = fig.add_subplot(grid[0, :])
    ax_r = fig.add_subplot(grid[1, 0])
    ax_w = fig.add_subplot(grid[1, 1])

    ax.axhline(0.0, color="0.45", lw=0.8)
    ax.fill_between(
        t,
        a_lin,
        0.0,
        where=(a_lin < 0.0),
        color=COLOR_LINEAR,
        alpha=0.18,
        interpolate=True,
    )
    ax.plot(t, a_lin, color=COLOR_LINEAR, lw=1.8, label=r"$a_{\mathrm{lin}}$")
    ax.plot(t, a_vp, color=COLOR_VP, lw=1.8, label=r"$a_{\mathrm{VP}}$")
    ax.plot(nodes, a_lin_nodes, "o", color=COLOR_LINEAR, ms=5.5, zorder=3)
    ax.plot(nodes, a_vp_nodes, "s", color=COLOR_VP, ms=5.0, zorder=3)
    ax.annotate(
        r"$a_{\mathrm{lin}}(0)=-1$",
        xy=(0.0, -1.0),
        xytext=(0.14, -1.32),
        fontsize=8,
        color=COLOR_LINEAR,
        arrowprops={"arrowstyle": "-", "color": COLOR_LINEAR, "lw": 0.6},
    )
    ax.annotate(
        r"$a_{\mathrm{lin}}(1)=+1$",
        xy=(1.0, 1.0),
        xytext=(0.72, 1.28),
        fontsize=8,
        color=COLOR_LINEAR,
        arrowprops={"arrowstyle": "-", "color": COLOR_LINEAR, "lw": 0.6},
    )
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(-1.55, 1.55)
    ax.set_xlabel(r"$t$")
    ax.set_ylabel(r"$a(t)$")
    ax.legend(frameon=False, loc="lower right")
    ax.set_title(r"(a) signed drifts", loc="left", fontsize=8)
    ax.annotate(
        r"shaded: $a_{\mathrm{lin}}<0$",
        xy=(0.18, -0.45),
        xytext=(0.42, -1.38),
        fontsize=7,
        color=COLOR_LINEAR,
        arrowprops={"arrowstyle": "->", "color": COLOR_LINEAR, "lw": 0.7},
    )

    def _bars(axis, values, ylabel, panel, prefer_index, prefer_text):
        colors = [COLOR_LINEAR, COLOR_VP]
        bars = axis.bar([0, 1], values, color=colors, width=0.55)
        axis.set_xticks([0, 1], ["lin", "VP"])
        axis.set_ylabel(ylabel)
        axis.set_title(panel, loc="left", fontsize=8)
        ymax = max(values)
        shorter = values[prefer_index]
        y_ann = ymax * 1.18
        axis.set_xlim(-0.85, 1.85)
        axis.set_ylim(0.0, ymax * 1.48)
        for bar, val in zip(bars, values, strict=True):
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:.3f}",
                ha="center",
                va="bottom",
                fontsize=7,
                zorder=6,
                clip_on=False,
            )
        # Side annotation: leader lands on the named bar and misses the value label.
        side = -1.0 if prefer_index == 0 else 1.0
        text_x = prefer_index + side * 0.70
        if prefer_index == 0:
            # Inward of the y-axis and below the 0.15 tick; still above the lin label.
            y_ann = ymax * 1.02
            text_x = 0.28
        axis.annotate(
            prefer_text,
            xy=(prefer_index + side * 0.18, shorter * 0.48),
            xytext=(text_x, y_ann),
            fontsize=7,
            color="black",
            ha="center",
            va="bottom",
            zorder=4,
            bbox={
                "facecolor": "white",
                "alpha": 0.85,
                "edgecolor": "none",
                "pad": 1.5,
            },
            arrowprops={
                "arrowstyle": "->",
                "color": "black",
                "lw": 0.7,
                "connectionstyle": (
                    "arc3,rad=0.25" if prefer_index == 0 else "arc3,rad=-0.25"
                ),
            },
        )

    _bars(
        ax_r,
        [r_lin, r_vp],
        r"$\mathcal{R}$",
        r"(b) exact $\mathcal{R}$",
        1,
        r"$\mathcal{R}$ prefers VP",
    )
    _bars(
        ax_w,
        [w_lin, w_vp],
        r"$W_2$",
        r"(c) Heun $W_2$",
        0,
        r"$W_2$ prefers lin",
    )
    out = FIGURE_DIR / ("fig_scalar" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    workshop = ROOT / "paper" / "gddl2026" / "figures" / ("fig_scalar" + FIGURE_SUFFIX)
    workshop.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(workshop, bbox_inches="tight")
    plt.close(fig)
    return out


def figure_noncentered_decomposition() -> tuple[Path, list[str]]:
    """Signed mean and covariance path differences on the non-centered family."""
    artifact_id = "workshop_external_validation_2026-07-24-v1:results"
    payload = load_pinned(artifact_id)
    compact = json.loads(
        (ROOT / "paper/arxiv/artifacts/noncentered_blocks.json").read_text(
            encoding="utf-8"
        )
    )
    blocks = compact["blocks"]
    if len(blocks) != 18:
        raise ValueError(f"expected 18 non-centered blocks, got {len(blocks)}")
    for row in blocks:
        for key in ("delta_mean", "delta_cov", "delta_total"):
            if key not in row:
                raise KeyError(f"missing {key} in non-centered compact artifact")

    solver_abbrev = {"euler": "Eu", "heun": "He", "rk4": "RK"}
    fig, axes = plt.subplots(
        2, 1, figsize=(FIGWIDTH, 4.8), sharex=True, gridspec_kw={"hspace": 0.28}
    )
    width = 0.38
    for ax, dim in zip(axes, (2, 8), strict=True):
        rows = [row for row in blocks if int(row["dim"]) == dim]
        y = list(range(len(rows)))
        labels = [
            f"{solver_abbrev[row['solver']]} {row['nfe']}"
            + (r"$^\ast$" if row["inversion_R"] else "")
            for row in rows
        ]
        mean_vals = [row["delta_mean"] for row in rows]
        cov_vals = [row["delta_cov"] for row in rows]
        ax.barh(
            [yi - width / 2 for yi in y],
            mean_vals,
            width,
            color=COLOR_LINEAR,
            label=r"$\Delta_{\mathrm{mean}}$",
        )
        ax.barh(
            [yi + width / 2 for yi in y],
            cov_vals,
            width,
            color=COLOR_VP,
            hatch="//",
            edgecolor="white",
            label=r"$\Delta_{\mathrm{cov}}$",
        )
        ax.axvline(0.0, color="#333333", lw=1.0)
        ax.set_xscale("symlog", linthresh=1e-6)
        ax.set_yticks(y, labels, fontsize=8)
        ax.set_title(f"$d={dim}$", loc="left")
        ax.legend(frameon=False, loc="lower right", fontsize=8)
        ax.grid(axis="x", alpha=0.25, linewidth=0.4)
    axes[1].set_xlabel(
        r"signed path difference (symlog; $+$ means linear larger than VP)"
    )
    out = FIGURE_DIR / ("fig_noncentered" + FIGURE_SUFFIX)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    del payload
    return out, [artifact_id]


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    fig1 = figure1_regimes()
    write_sidecar(
        fig1,
        artifact_ids=[],
        plotting_config={
            "kind": "three_regime_R_W2_bars",
            "pairwise_block": "low_rank_d8 euler NFE 8",
            "in_family_block": "anisotropic_d8 euler NFE 8",
            "unconstrained_block": "low_rank_d8 euler NFE 8",
            "counts": {
                "pairwise_cells": "5/12",
                "in_family_blocks": "9/36",
                "minimizer": "36/36",
            },
        },
        note=(
            "Headline R and W2 bars for the three regimes. Counts are a finite "
            "enumeration of the four specified candidate paths, not estimators. "
            "Source geometries.json."
        ),
    )
    written.append(fig1)
    fig_s = figure_scalar_counterexample()
    write_sidecar(
        fig_s,
        artifact_ids=[],
        plotting_config={"kind": "scalar_drift_lin_vp_heun_nodes"},
        note="Exact closed-form drifts a_lin and a_VP on [0,1]; Heun nodes at NFE 8.",
    )
    written.append(fig_s)
    fig4 = figure_four_paths()
    write_sidecar(
        fig4,
        artifact_ids=[],
        plotting_config={"kind": "four_path_R_and_euler8_W2"},
        note=(
            "Linear, trigonometric VP, shared Chen Ex. 3.3 (M=lambda_max), "
            "and per-mode log-covariance. R is continuous; W2 is Euler at NFE 8."
        ),
    )
    written.append(fig4)
    frozen_root = (
        ROOT
        / "paper"
        / "arxiv"
        / "frozen_runs"
        / "phase4_gaussian_reproduction_2026-07-24-v1"
    )
    if frozen_root.is_dir():
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
        written.append(fig_e)
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
                "Signed factor-plus-noise W2 margins versus equal-NFE Euler, Heun, and RK4."
            ),
        )
        written.append(fig3)
        fig_n, ids_n = figure_noncentered_decomposition()
        write_sidecar(
            fig_n,
            artifact_ids=ids_n,
            plotting_config={"kind": "noncentered_mean_bures_split"},
            note="Signed Delta_mean and Delta_cov on all 18 blocks; * marks inversions.",
        )
        written.append(fig_n)
    else:
        print(
            "skipping Hydra-backed figures (fig2_inversions, fig_eigenmode, "
            "fig3_interaction, fig_noncentered): missing "
            "paper/arxiv/frozen_runs/phase4_gaussian_reproduction_2026-07-24-v1"
        )
    for path in written:
        print(path.relative_to(ROOT), sha256_file(path)[:16])


if __name__ == "__main__":
    main()
