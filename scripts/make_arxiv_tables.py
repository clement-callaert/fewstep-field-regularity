"""Generate arXiv numerical macros and inversion tables from pinned artifacts."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from fewstep_regularities.utils.hashing import sha256_file

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "arxiv" / "generated"

PINNED = {
    "phase4_gaussian_reproduction_2026-07-24-v1:results": (
        ROOT / "outputs/phase4_gaussian_reproduction_2026-07-24-v1/results.json",
        "b8930142cba5655ee553aae5ff400cd884c1137e77547d9a5fa94bd4e354973f",
    ),
    "phase4_precision_2026-07-24-v1:table": (
        ROOT / "outputs/phase4_precision_2026-07-24-v1/table.json",
        "5f8800a697c61c2eab2306281fe4fb1b01dee67bc3c678dd7ba4a626d9dc8e1b",
    ),
    "workshop_external_validation_2026-07-24-v1:inversions": (
        ROOT / "outputs/workshop_external_validation_2026-07-24-v1/inversions.json",
        "cceebdfcba6f7cec4a7ff9e137d4a53f8c7e389acc0222a20805f16204a1b875",
    ),
    "phase4_decomposition_2026-07-24-v1:validation": (
        ROOT / "outputs/phase4_decomposition_2026-07-24-v1/validation.json",
        "bf2efcc86b8456c2563780557bcc4137105db849240db09a04c4993c38ebcdc6",
    ),
}

PRIMARY_RESULTS_SHA = PINNED["phase4_gaussian_reproduction_2026-07-24-v1:results"][1]
AUDIT_COMMIT = "e48c9390e62b38f206342e6aeb7f160122ccc79c"


def load_pinned(artifact_id: str) -> dict:
    path, expected = PINNED[artifact_id]
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(f"Checksum mismatch for {artifact_id}: {actual}")
    return json.loads(path.read_text(encoding="utf-8"))


def blocks_from_rows(rows: list[dict]) -> list[dict]:
    by_key: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        key = (row["target_family"], int(row["dim"]), row["solver"], int(row["nfe"]))
        by_key[key][row["path"]] = row
    out = []
    for key, paths in sorted(by_key.items()):
        lin, vp = paths["linear"], paths["variance_preserving"]
        d_metric = lin["baseline_metric"] - vp["baseline_metric"]
        d_w2 = lin["gaussian_w2"] - vp["gaussian_w2"]
        out.append(
            {
                "family": key[0],
                "dim": key[1],
                "solver": key[2],
                "nfe": key[3],
                "lin": lin,
                "vp": vp,
                "d_metric": d_metric,
                "d_w2": d_w2,
                "is_inversion": d_metric * d_w2 < 0,
                "margin": abs(d_w2),
            }
        )
    return out


def sci_tex(value: float, digits: int = 10) -> str:
    mantissa, exp = f"{value:.{digits}e}".split("e")
    return rf"{mantissa}\times 10^{{{int(exp)}}}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = load_pinned("phase4_gaussian_reproduction_2026-07-24-v1:results")
    precision = load_pinned("phase4_precision_2026-07-24-v1:table")
    workshop = load_pinned("workshop_external_validation_2026-07-24-v1:inversions")
    decomposition_val = load_pinned("phase4_decomposition_2026-07-24-v1:validation")
    recon_delta = float(decomposition_val["maximum_reconstruction_delta"])
    rows = results["rows"]
    blocks = blocks_from_rows(rows)
    inversions = [b for b in blocks if b["is_inversion"]]
    if len(rows) != 72 or len(blocks) != 36 or len(inversions) != 14:
        raise RuntimeError("Unexpected Phase 4 counts")

    strongest = max(inversions, key=lambda b: b["margin"])
    smallest = min(inversions, key=lambda b: b["margin"])
    max_delta = max(r["absolute_reference_delta"] for r in precision["rows"])
    ratio = smallest["margin"] / max_delta
    w_inv = [r for r in workshop["rows"] if r["is_inversion"]]
    if len(workshop["rows"]) != 18 or len(w_inv) != 11:
        raise RuntimeError("Unexpected workshop inversion counts")
    w_margin = min(abs(r["w2_delta_linear_minus_vp"]) for r in w_inv)
    w_prec = max(r["audit_max_absolute_difference"] for r in w_inv)
    w_rmargin = abs(w_inv[0]["metric_delta_linear_minus_vp"])

    macros = OUT / "numbers.tex"
    macros.write_text(
        "\n".join(
            [
                rf"\newcommand{{\nConfigs}}{{{len(rows)}}}",
                rf"\newcommand{{\nBlocks}}{{{len(blocks)}}}",
                rf"\newcommand{{\nInversions}}{{{len(inversions)}}}",
                rf"\newcommand{{\nWorkshopBlocks}}{{18}}",
                rf"\newcommand{{\nWorkshopInversions}}{{11}}",
                rf"\newcommand{{\strongRlin}}{{{strongest['lin']['baseline_metric']:.10f}}}",
                rf"\newcommand{{\strongRvp}}{{{strongest['vp']['baseline_metric']:.10f}}}",
                rf"\newcommand{{\strongWlin}}{{{strongest['lin']['gaussian_w2']:.10f}}}",
                rf"\newcommand{{\strongWvp}}{{{strongest['vp']['gaussian_w2']:.10f}}}",
                rf"\newcommand{{\strongMargin}}{{{strongest['margin']:.10f}}}",
                rf"\newcommand{{\smallMargin}}{{{sci_tex(smallest['margin'])}}}",
                rf"\newcommand{{\maxPrecDelta}}{{{sci_tex(max_delta)}}}",
                rf"\newcommand{{\precRatio}}{{{int(ratio)}}}",
                rf"\newcommand{{\workshopRmargin}}{{{w_rmargin:.4f}}}",
                rf"\newcommand{{\workshopSmallMargin}}{{{sci_tex(w_margin, 2)}}}",
                rf"\newcommand{{\workshopPrecDelta}}{{{sci_tex(w_prec, 2)}}}",
                rf"\newcommand{{\reconResidual}}{{{sci_tex(recon_delta)}}}",
                rf"\newcommand{{\primarySha}}{{{PRIMARY_RESULTS_SHA}}}",
                rf"\newcommand{{\auditCommit}}{{{AUDIT_COMMIT}}}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    lines = [
        r"\begin{tabular}{llcccrr}",
        r"\toprule",
        r"family & $d$ & solver & NFE & $R$ prefers & $W_2$ prefers & $W_2$ margin \\",
        r"\midrule",
    ]
    for b in inversions:
        r_pref = "linear" if b["d_metric"] < 0 else "VP"
        w_pref = "linear" if b["d_w2"] < 0 else "VP"
        fam = "anisotropic" if b["family"] == "anisotropic_gaussian" else "low-rank"
        lines.append(
            f"{fam} & {b['dim']} & {b['solver']} & {b['nfe']} & {r_pref} & {w_pref} & "
            f"${sci_tex(b['margin'], 6)}$ \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (OUT / "inversions_centered.tex").write_text("\n".join(lines), encoding="utf-8")

    wlines = [
        r"\begin{tabular}{ccccrr}",
        r"\toprule",
        r"$d$ & solver & NFE & inversion & $R_{\mathrm{lin}}-R_{\mathrm{VP}}$ & $W_2^{\mathrm{lin}}-W_2^{\mathrm{VP}}$ \\",
        r"\midrule",
    ]
    for r in workshop["rows"]:
        flag = "yes" if r["is_inversion"] else "no"
        wlines.append(
            f"{r['dim']} & {r['solver']} & {r['nfe']} & {flag} & "
            f"{r['metric_delta_linear_minus_vp']:.4f} & "
            f"${sci_tex(r['w2_delta_linear_minus_vp'], 6)}$ \\\\"
        )
    wlines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (OUT / "inversions_noncentered.tex").write_text("\n".join(wlines), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
