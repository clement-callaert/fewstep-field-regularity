# Postmortem

Fill this document in Phase 7 regardless of outcome.
Never delete invalidated findings. Mark them clearly and link to the bug or
methodological issue.

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

To be filled in Phase 7.

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

Review the Phase 3 artifacts and correction. If approved, continue to Phase 4
only. Do not start the Phase 5 Cartesian benchmark yet.
