# Repository inventory (historical; 2026-08-13)

**Historical.** This inventory describes commit
`e48c9390e62b38f206342e6aeb7f160122ccc79c`. It is not the current tree.
Pull request #1 is merged; `talks/wald-interview-2026-08-21/` is on
public `main`. The current release audit is
`audit/PASS9_POST_MERGE_RELEASE.md`.

# Repository inventory

Audit date: 2026-08-13.
Audited commit: `e48c9390e62b38f206342e6aeb7f160122ccc79c` (branch `arxiv-audit-and-release`, created from `submission/gddl2026`).
Remote default: `origin/main` at `b149f35`.
Working tree at audit start: dirty (unstaged documentation and docstring edits plus untracked `talks/` and `.claude/`). Those user changes were preserved and not lump-committed.

Classification codes: S = source, G = generated output, E = evidence artifact, D = documentation, H = historical or process, A = needed for arXiv, X = not needed for arXiv.

## Top level

| Path | Purpose | Class | arXiv | Notes |
| --- | --- | --- | --- | --- |
| `README.md` | Public landing page | D | yes (rewrite) | Says manuscript material is under review. Must not remain as the public preprint pointer. |
| `README_POST_REVIEW.md` | Post-notification landing | D/H | no | Venue-adjacent. Keep as process history. |
| `CONTRIBUTING.md` | Owner-only commits | D | no | |
| `pyproject.toml` | Package metadata | S | yes | Declares MIT with no LICENSE file. Homepage URL `github.com/calla/...` does not match the remote `clement-callaert/...`. Python `>=3.11`. |
| `LICENSE` | Missing | | decision | Declared MIT in pyproject only. |
| `CITATION.cff` | Missing | | later | Add when an identifier exists. |
| `.github/workflows/ci.yml` | ruff, mypy, pytest on 3.11/3.12 | S | no | Does not validate Phase 4 artifacts. |
| `.gitignore` | Ignores `outputs/*`, `artifacts/*`, literature PDFs | S | yes | Scientific JSON evidence is local-only. |
| `.venv/` | Local environment | G | no | Python 3.11.15. |
| `talks/` | Untracked Wald interview materials | H | no | Leave untracked unless the owner asks. |
| `.claude/` | Untracked local settings | X | no | |

## Paper trees

| Path | Purpose | Class | arXiv | Notes |
| --- | --- | --- | --- | --- |
| `paper/gddl2026/main.tex` | Anonymous workshop draft | H | archive only | Do not edit. Anonymous authors, `dblblindworkshop`, refers to a missing supplement. |
| `paper/gddl2026/main.pdf` | Compiled workshop PDF | G/H | remove from public tip | Tracked on `origin/main`. Submission footer and "Do not distribute". |
| `paper/gddl2026/neurips_2026.sty` | Official 2026 style | H | no | |
| `paper/gddl2026/neurips_2025.sty` | Leftover style | H | no | Stale. |
| `paper/gddl2026/references.bib` | Workshop bibliography | H | seed for arXiv bib | |
| `paper/gddl2026/figures/` | Workshop figures and sidecars | G | regenerate under `paper/arxiv/figures/` | `fig_eigenmode.pdf` exists on disk but is not included in workshop `main.tex`. |
| `paper/gddl2026/artifact_aliases.json` | A1-A7 checksum map | E | cite in appendix | Checksums match local `outputs/`. |
| `papers/` | Literature notes and manifest | D | no | PDF bodies gitignored. |

## Code, configs, tests

| Path | Purpose | Class | arXiv | Notes |
| --- | --- | --- | --- | --- |
| `src/fewstep_regularities/` | Research package | S | yes | Affine Gaussian fields, solvers, W2, Phase 4 runners. |
| `src/.../analysis/propagation.py` | `d+1` probe affine maps | S | yes | Primary numerical endpoint map. |
| `src/.../analysis/local_error.py` | Modal factors and LTE coefficients | S | yes | Heun coefficient independently confirmed. |
| `src/.../solvers/common.py` | Equal-NFE `n_steps = NFE / stages` | S | yes | Exact divisibility required. |
| `src/.../metrics/affine_gaussian.py` | Trapezoidal spectral `R` | S | yes | `is_exact=False`; `n_time=24` in Phase 4 config. |
| `configs/experiment/phase4_*.yaml` | Frozen Phase 4 grid | S | yes | 72 configurations. |
| `configs/experiment/workshop_external_validation.yaml` | Non-centered family | S | yes | 36 rows, 18 blocks. |
| `tests/` |  unit, analytical, integration, regression | S | yes | Pytest passed on 2026-08-13. |
| `scripts/validate_artifacts.py` | Manifest checksum validator | S | yes | All seven scientific run dirs OK. |
| `scripts/make_workshop_figures.py` | Pinned-hash figure builder | S | adapt | Do not hand-edit PDFs. |

## Local evidence (`outputs/`, gitignored)

All of the following exist locally, validate, and match `artifact_aliases.json` where listed.

| Run directory | Role | Class |
| --- | --- | --- |
| `phase4_gaussian_reproduction_2026-07-24-v1` | 72 rows, 14 of 36 inversions | E |
| `phase4_precision_2026-07-24-v1` | 80-digit W2 audit | E |
| `phase4_decomposition_2026-07-24-v1` | Modal W2 and transported defects | E |
| `phase4_diagnostics_2026-07-24-v1` | Post-hoc proxies | E |
| `phase4_robustness_2026-07-24-v1` | Perturbations and NFE 64/128 | E |
| `phase4_final_validation_2026-07-24-v1` | Meta-validation | E |
| `workshop_external_validation_2026-07-24-v1` | 11 of 18 non-centered inversions | E |
| `phase3_*` | Gate and mixture diagnostics | E/H | Not a Phase 4 claim source except as the registered inversion discovery chain. |
| `artifacts/` | Empty placeholder | X |

Generated files that must not be hand-edited: JSON under `outputs/`, figure PDFs, `main.pdf`, sidecar `*.pdf.json`.

## Docs

Process and proof documents under `docs/` are documentation, not primary evidence. `[docs/CLAIMS_LEDGER.md](docs/CLAIMS_LEDGER.md)` is the claim-status ceiling. `[docs/P4_P1_PROOF_AUDIT.md](docs/P4_P1_PROOF_AUDIT.md)` is the full Euler construction. `[docs/MARKDOWN_CONSISTENCY_AUDIT.md](docs/MARKDOWN_CONSISTENCY_AUDIT.md)` lists prose contradictions to re-check against artifacts. `[docs/WORKSHOP_EXTERNAL_VALIDATION_PLAN.md](docs/WORKSHOP_EXTERNAL_VALIDATION_PLAN.md)` is the pre-execution freeze.

## Stale, conflicting, or submission-specific surfaces

- Anonymous workshop PDF on the public default branch.
- README review language.
- Missing supplement referenced by workshop `main.tex`.
- `docs/PHASE4_RESULTS.md` says the leading proxy agrees in 15 of 18 low-rank blocks; independent recount is 14 of 18 (overall 29 of 36 is correct).
- Workshop gloss "78% larger" is a rounding of 77.63 percent; do not reprint.
- Two nearby residuals: W2 80-digit max `9.7050430488e-10` versus eigenmode reconstruction `9.7050436884e-10`.
- No repository license file.
- Wrong GitHub URL in `pyproject.toml`.
