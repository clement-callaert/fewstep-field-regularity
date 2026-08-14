# Markdown consistency audit

Date: 2026-07-25. Scope: every project `.md` file except `.venv` and
`.ownership*` backups (45 files). Read-only for numbers; stale links may be
fixed in place. Canonical defaults used for proposed resolutions:

- Precision: `9.7050430488e-10` from `phase4_precision_2026-07-24-v1` and
  `docs/PHASE4_RESULTS.md`
- Ratio landing prose: "more than 11,500"; exact `11,528` only when derived
  from pinned margins `1.1188920612e-5 / 9.7050430488e-10`
- Inversion form: "14 of 36 blocks in the tested grid"
- P4-C3 / P4-P1 status: `docs/CLAIMS_LEDGER.md` wins; historical snapshots
  need labels
- `78%` gloss: non-canonical; exact margin `0.3543761036`

Ledger ceilings: P4-P1 supported; P4-C1 under-test; P4-C2 under-test;
P4-C3 inconclusive. Inversions must not be called frequent / common /
prevalent.

## CONTRADICTIONS

### Inversion count form (14 vs 14/36)

| location | wording |
| --- | --- |
| `docs/WORKSHOP_CORRECTION_REPORT.md:161` | `14/36 inversions` |
| `docs/PHASE4_RESULTS.md:33` | `All 14 clean Gaussian inversion blocks` |
| `docs/PHASE4_RESULTS.md:48` | `14 baseline ranking inversion blocks` |
| `docs/CLAIMS_LEDGER.md:16` | `Fourteen inversions reproduce` |
| `README_POST_REVIEW.md:20` | `Fourteen ranking inversions reproduced` |
| `docs/WORKSHOP_PAPER_CLAIMS.md:57` | `Fourteen averaged-regularity ranking inversions` |
| `docs/WORKSHOP_PAPER_OUTLINE.md:27`, `:73`, `:92` | `fourteen` without denominator |
| `docs/POSTMORTEM.md:110` | `Fourteen clean Gaussian inversions` |
| `docs/SESSION_LOG.md:415` | `Fourteen baseline inversion blocks` |
| `docs/UNRESOLVED_QUESTIONS.md:68` | `14 inversion blocks` |

Proposed resolution: use **14 of 36 blocks in the tested grid** wherever the
Phase 4 primary grid count is stated; keep bare "fourteen" only when the
surrounding sentence already names the 36-block grid.

### Margin-to-precision ratio (11,500 / 11,528 / 11,529)

Exact quotient from pinned values:
`1.1188920612e-5 / 9.7050430488e-10 = 11528.975…`.

| location | wording |
| --- | --- |
| `docs/PHASE4_RESULTS.md:36-37` | `more than 11,500 times` |
| `docs/PHASE4_RESULTS.md:76-77` | `still 11,528 times` |
| `docs/WORKSHOP_CORRECTION_REPORT.md:164` | `ratio 11,529 > 11,500` |
| `README_POST_REVIEW.md:67` | `more than 11,500 times` |
| `docs/WORKSHOP_PAPER_CLAIMS.md:70` | `more than 11,500` |
| `docs/UNRESOLVED_QUESTIONS.md:91` | `more than 11,500 times` |

Proposed resolution: landing / claims prose → **more than 11,500**; when an
integer derived from the pinned margins is required → **11,528** (not
11,529).

### Precision value vs near-duplicate reconstruction residual

| location | quantity as labeled | value |
| --- | --- | --- |
| `docs/PHASE4_RESULTS.md:36`, `:151`; `README_POST_REVIEW.md:68`; `docs/WORKSHOP_PAPER_CLAIMS.md:69`; `docs/SESSION_LOG.md:491`; `docs/WORKSHOP_CORRECTION_REPORT.md:164` | float64 vs 80-digit W2 (precision) | `9.7050430488e-10` |
| `docs/SESSION_LOG.md:535` (Run 3), `:586` (Run 4) | maximum reconstruction difference | `9.7050436884e-10` |

Proposed resolution: keep **`9.7050430488e-10`** as the only canonical
precision figure. Treat `9.7050436884e-10` as a separate reconstruction
residual; never substitute it for the precision audit maximum.

### Strongest-inversion regularity rounding

| location | linear regularity | VP regularity |
| --- | --- | --- |
| `docs/PHASE4_RESULTS.md:65-66`; `README_POST_REVIEW.md:62-63`; `docs/WORKSHOP_PAPER_CLAIMS.md:63-65`; `docs/WORKSHOP_CORRECTION_REPORT.md:162` | `2.9476523251` | `4.7295206355` |
| `docs/WORKSHOP_REVIEW_SIMULATION.md:179-180` (n=24 quadrature column) | `2.94765233` | `4.72952064` |

Proposed resolution: pinned strongest-inversion table uses full
`2.9476523251` / `4.7295206355`. The review-simulation table may keep
shorter digits only if labeled as a quadrature diagnostic, not as the
canonical strongest-inversion values.

### 78% gloss vs exact margin

| location | wording |
| --- | --- |
| `docs/WORKSHOP_CORRECTION_REPORT.md:163` | `0.3543761036 (77.63% → "78%")` |
| `docs/PHASE4_RESULTS.md:69`; `README_POST_REVIEW.md:66`; `docs/WORKSHOP_PAPER_CLAIMS.md:66`; `docs/SESSION_LOG.md:419` | margin `0.3543761036` only |

Proposed resolution: **non-canonical**. Prefer exact margin
`0.3543761036`; do not promote the 78% gloss in landing or claims prose.

### P4-C3 / P4-P1 status language vs ledger

Ledger (`docs/CLAIMS_LEDGER.md:18-19`): P4-C3 **inconclusive**; P4-P1
**supported**.

| location | stated status | conflict |
| --- | --- | --- |
| `docs/SESSION_LOG.md:454-455` (Run 1 claims block) | P4-C3 remains proposed; P4-P1 remains proposed | Current ledger: inconclusive / supported |
| `docs/PHASE4_PLAN.md:260-261` | initial status proposed / proposed | OK if read as plan-time initials; risks looking current |
| `docs/PHASE4_RESULTS.md:190-193` | P4-C3 inconclusive; P4-P1 verified | Aligns with ledger |
| `docs/UNRESOLVED_QUESTIONS.md:85-86`, `:96-97` | P4-C3 inconclusive; P4-P1 proof verified | Aligns with ledger |

Proposed resolution: **ledger wins**. Label `SESSION_LOG` Run 1 statuses as
historical (as-of Run 1). Keep `PHASE4_PLAN` table under an explicit
"initial status" heading (already present).

### Unicode em-dash (U+2014)

Present in process / authorship docs, absent from Phase 4 scientific
result docs:

| file | lines |
| --- | --- |
| `docs/DOUBLE_BLIND_AUDIT.md` | 12 |
| `docs/DOUBLE_BLIND_FINAL_CHECKLIST.md` | 35 |
| `docs/WORKSHOP_CORRECTION_REPORT.md` | 130, 143, 188, 222, 240 |
| `docs/REPOSITORY_PUBLICATION_PLAN.md` | 21, 43 |
| `docs/GIT_AUTHORSHIP_CLEANUP_PLAN.md` | 22, 23, 50 |
| `docs/GIT_AUTHORSHIP_AUDIT.md` | 34, 43, 50, 61 |

Proposed resolution: optional ASCII normalization (` - ` or commas) for
consistency; not a numerical conflict.

### Cross-checks with no numerical conflict

- Strongest-inversion W2 values `0.8108540111` / `0.4564779075`, margins
  `0.3543761036` / `1.1188920612e-5`: consistent across citing files.
- External validation `11 of 18` / `11/18`: consistent
  (`README_POST_REVIEW.md:166`, `docs/WORKSHOP_PAPER_CLAIMS.md:125-127`,
  `docs/SESSION_LOG.md:765`, `docs/POSTMORTEM.md:104`,
  `docs/UNRESOLVED_QUESTIONS.md:125`, `docs/WORKSHOP_CORRECTION_REPORT.md:165`).
- Phase 4 release-ready SHA-256 tables in `docs/PHASE4_RESULTS.md:178-183`
  and `README_POST_REVIEW.md:140-145` match `outputs/*/manifest.json`
  `output_checksum` fields. Workshop external-validation SHAs in
  `docs/SESSION_LOG.md:740-747` also match manifests.

## LEDGER VIOLATIONS

Ledger ceilings applied: P4-P1 supported; P4-C1 under-test; P4-C2
under-test; P4-C3 inconclusive. Inversions must not be called frequent,
common, or prevalent.

### P4-C1 asserted as settled while status is under-test

| location | sentence / excerpt | why over ceiling |
| --- | --- | --- |
| `README_POST_REVIEW.md:18-22` | "ordering … does not determine their fixed-NFE Gaussian Wasserstein error ordering. Fourteen ranking inversions reproduced…" as **Main finding** | States P4-C1 as established landing fact; ledger status is under-test |
| `docs/WORKSHOP_PAPER_CLAIMS.md:15-17` | Primary claim: "… does not determine their fixed-NFE Gaussian W2 ordering." | Paper freeze asserts the claim; ledger forbids stronger-than-under-test presentation |
| `docs/WORKSHOP_PAPER_CLAIMS.md:153-159` | Contribution: "We show … does not determine …" | Same overshoot for P4-C1 |
| `docs/AUDIT_REPORT.md:184-185` | "An averaged regularity ordering does not determine fixed-NFE error in the tested commuting Gaussian systems." | Interpretive verdict states the claim as concluded |
| `docs/POSTMORTEM.md:99-100` | "reject averaged regularity as a determinant of fixed-grid error in the tested setting." | Rejects the null as if P4-C1 were supported |
| `docs/PHASE4_LITERATURE_AUDIT.md:138-140` | "controlled commuting Gaussian decomposition showing why averaged Jacobian regularity does not determine fixed-grid W2 error." | Presents non-implication as shown, beyond under-test |

### P4-P1 wording stronger than supported / proof-verified vocabulary

| location | sentence / excerpt | why over ceiling |
| --- | --- | --- |
| `docs/WORKSHOP_REVIEW_SIMULATION.md:18` | "… and **proves** an elementary grid-aliasing proposition for forward Euler." | Project proof vocabulary forbids unmarked `proved`/`proves`; ledger status is supported with audit label "proof verified", not an unrestricted prove claim |

### Words frequent / common / prevalent (inversion strength)

None found in claim-strengthening use across audited markdown.

### Word predictive (claim-strengthening sense)

No sentence claims predictive superiority for the solver proxy. Occurrences
are negations, forbids, or outline warnings
(`docs/PHASE4_RESULTS.md:117`, `docs/SESSION_LOG.md:597-598`,
`README_POST_REVIEW.md:187`, `docs/WORKSHOP_PAPER_CLAIMS.md:114`,
`docs/WORKSHOP_PAPER_OUTLINE.md:75`, `docs/CLAIMS_LEDGER.md:18`).

### P4-C3 explanatory superiority

No markdown sentence claims out-of-sample or predictive superiority for
P4-C3. Same-grid agreement counts (29 of 36) appear with post-hoc /
inconclusive qualifiers where status is discussed.

## STALE OR ORPHAN REFERENCES

### Fixed in this audit

| location | was | fix |
| --- | --- | --- |
| `docs/REPOSITORY_PUBLICATION_PLAN.md:58` | paper aliases `A1–A5` | updated to `A1–A7` to match `paper/gddl2026/artifact_aliases.json` |

### Remaining orphans / missing targets (not auto-edited)

| location | reference | note |
| --- | --- | --- |
| `papers/notes/hairer2008solving_odes_i.md:7` | `local_filename: hairer2008solving_odes_i.pdf` | PDF absent under `papers/pdfs/`; note already marks `missing-source` / paywall |
| `papers/README.md:46` | hairer row `n/a unless author-legal PDF` | Consistent with missing PDF; not a false existence claim |
| Figure sidecars under `paper/gddl2026/figures/*.pdf.json` | `workshop_figures_2026-07-24-v1:fig*` | Artifact IDs not present in any `outputs/*/manifest.json` (sidecar-only; not cited in markdown prose) |
| `docs/REPOSITORY_PUBLICATION_PLAN.md:49` | `CITATION.cff` | Planned draft ("Draft `CITATION.cff`"); file does not exist yet |

### Markdown links

All relative markdown links of the form `[text](path)` in the audited
corpus resolve to existing paths. No further link rewrites were required.
