# Release gate

Audit date: 2026-08-13.
Audited commit: `e48c9390e62b38f206342e6aeb7f160122ccc79c`.
Decision: **CONDITIONAL PASS**.

No S4 issue was found. Central mathematics and central empirical counts reconstruct from code, configuration, and frozen artifacts. An arXiv manuscript may be prepared. Submission, license choice, and git push remain owner decisions.

## Severity list

| ID | Severity | Issue | Disposition |
| --- | --- | --- | --- |
| G1 | S1 | No LICENSE file; pyproject declares MIT | Present options; do not choose |
| G2 | S1 | pyproject homepage URL is `github.com/calla/...` | Propose correction |
| G3 | S1 | Public `main` tracks an anonymous workshop PDF | Archive; do not present as preprint |
| G4 | S1 | Outputs gitignored | Put generated tables in the paper |
| G5 | S1 | Leftover `neurips_2025.sty` | Archive with workshop tree |
| G6 | S1 | Docs say proxy 15 of 18 low-rank; recount 14 of 18 | Correct in audit; arXiv uses 29 of 36 |
| G7 | S1 | Euler regression test omitted exact identity | Assertion added |
| G8 | S2 | Ledger P4-C1 remains under-test while counts reproduce | Keep ledger; paper uses descriptive counts |
| G9 | S2 | Workshop "78% larger" | Omit |
| G10 | S2 | Two nearby 9.705e-10 residuals | Distinguish W2 vs reconstruction |
| G11 | S2 | Workshop refers to a missing supplement | Full proofs in arXiv appendices |
| G12 | S2 | `R` is quadrature, not an exact integral | State n_time=24 trapezoid |
| G13 | S2 | Amendment A1 between freeze and results | Report in chronology |
| G14 | S2 | Contemporaneous Tao-Choi 2026 and Iso-FM 2026 | Cite with scope |
| G15 | S0 | Ratio "more than 11,500" vs 11528 | Either is honest |

No S3 formula error in Euler/Heun LTE or P4-P1. No S4.

## Gate checklist

| Criterion | Status |
| --- | --- |
| No unresolved S4 | pass |
| Central math verified | pass (P4-P1, telescoping, affine field, W2) |
| Central empirical claims traceable | pass (14/36, 11/18, strongest row, 80-digit) |
| Figures/tables from controlled sources | pass (`paper/arxiv/generated/`, `paper/arxiv/figures/`) |
| Ledger vs manuscript | pass if arXiv does not upgrade P4-C1 to a population law |
| Citations support statements | pass after adding contemporaneous NA papers |
| Limitations match scope | pass if no learned-model claims |
| Paper self-contained | required of the arXiv draft |
| Source package compiles | pass (`paper/arxiv/main.pdf`, zip compile) |

## If this had failed

Shortest path would have been: (S4 math) stop and correct P4-P1; (S4 empirics) stop and freeze a new artifact. Neither occurred.
