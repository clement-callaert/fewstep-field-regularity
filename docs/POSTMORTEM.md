# Postmortem

Status: Phase 4 update complete. A final project postmortem remains due in
Phase 7.

Scope: Phase 1 through the focused exact Gaussian Phase 4 audit.

Artifact IDs used:

- `phase3_gate_analysis_final_audit_2026-07-23-v2:decision`
- `phase4_gaussian_reproduction_2026-07-24-v1:results`
- `phase4_precision_2026-07-24-v1:validation`
- `phase4_decomposition_2026-07-24-v1:table`
- `phase4_diagnostics_2026-07-24-v1:table`
- `phase4_robustness_2026-07-24-v1:table`
- `phase4_final_validation_2026-07-24-v1:validation`

Registered and post-hoc analyses are identified in the Phase 4 results. Exact
Gaussian moment quantities are separated from numerical quadrature estimates.
Invalidated outputs remain recorded.

## 1. Initial hypothesis

H1 to H4 were evaluated in the small registered Phase 3 gate. They remain
hypotheses. See docs/GATE_RESULT.md and docs/CLAIMS_LEDGER.md.

## 2. Registered decision gate

See docs/DECISION_GATE.md version 2026-07-23-v1. It was not changed.

## 3. What was implemented

Phase 3 added a frozen small grid, exact Gaussian numerical-moment evaluation,
calibrated mixture evaluation, nested correlations, paired bootstrap,
sensitivity checks, ranking inversions, interactions, and full provenance.

## 4. What worked

The smoke and main manifests validate. Equal NFE holds for every solver.
Exact Gaussian cases and mixture estimator sensitivity can be analyzed in one
nested schema. Reproducible ranking inversions survived in three families.

## 5. What failed

No alternative metric passed condition 1. Several mixture interaction
candidates failed the ten-seed stability rule. The temporal metric did not add
positive residual association in the registered analysis.

## 6. Bugs discovered

The first analysis compared different family sets across metric budgets and
omitted the schedule-by-geometry table. Both errors were corrected from the
same immutable gate artifact under new artifact IDs.

## 7. Invalidated results

The first sensitivity table is invalid for cross-budget comparison. The first
interaction table is incomplete. The next corrected decision used overly
strong pivot statuses and one overbroad explanation. These artifacts remain
on disk and are excluded from docs/GATE_RESULT.md. A later audited pass still
admitted dimension 8 mixture evidence even though pre-gate calibration covered
dimension 2 only. The final audited pass excludes those blocks.

## 8. Evidence that survived

Primary nested correlations, paired bootstrap, ranking inversion checks,
equal-NFE validation, and the immutable main results survived the corrections.
The final audited analysis passes artifact validation. Condition 2 survives
using two exact Gaussian families and calibrated dimension 2 mixture evidence.

## 9. Decisions changed

The gate recommends Phase 4 review because condition 2 holds. Condition 3 also
holds under its registered rule, but its Euler-specific evidence triggers
pivot rule 8 and is not the sole basis for continuing.

## 10. Time allocation

Each Phase 4 run finished in under 10 seconds of manifest runtime. Run 4 was
the longest at 8.109213 seconds. Derivation, implementation, source review,
tests, and audit documentation took substantially longer than computation.

## 11. Reproducibility failures

The main run records dirty code and is not release-ready. The analysis needed
corrective passes. Dimension 8 mixture evaluation failed a post-result
calibration diagnostic and is excluded from decision evidence. These facts
require human review before Phase 4.

## 12. Scientific conclusion

The small gate passed condition 2. This is not a paper conclusion. H1 and H3
are inconclusive, H2 is contradicted for the registered alternatives, and H4
remains under-test.

## 13. Next project recommendation

Pivot. Do not start the Phase 5 Cartesian benchmark. The exact Gaussian
mechanism is understood well enough to reject averaged regularity as a
determinant of fixed-grid error in the tested setting. Broad solver dependence
is already represented in prior schedule literature, while the new minimal
construction is elementary and needs expert review.

## 14. Phase 4 observation and interpretation

Observation: Fourteen clean Gaussian inversions reproduce. Precision,
decomposition, robustness, and final validation pass. The low-rank solver
preference persists through NFE 128 and small target perturbations.

Interpretation: Signed and transported solver defects explain why a scalar
average of Jacobian size loses information. The same-grid leading proxy is
suggestive but not validated out of sample.

## 15. Phase 4 exclusions and unresolved work

Mixtures, dimension 32, and new target families were excluded. Dimension 8
mixture evidence remains invalid for decisions. Dirty smoke artifacts and
superseded Phase 3 analyses remain excluded. Open work is listed in
[unresolved questions](UNRESOLVED_QUESTIONS.md), and the derivation is in
[the mathematical analysis](PHASE4_MATHEMATICAL_ANALYSIS.md).
