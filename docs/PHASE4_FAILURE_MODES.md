# Phase 4 failure modes

Status: Active audit record.

Scope: Exact Gaussian Phase 4 work only.

Artifact IDs used:

- `phase4_gaussian_reproduction_2026-07-24-v1:results`
- `phase4_gaussian_reproduction_2026-07-24-v1:validation`
- `phase4_precision_2026-07-24-v1:validation`
- `phase4_decomposition_2026-07-24-v1:validation`
- `phase4_diagnostics_2026-07-24-v1:validation`
- `phase4_robustness_2026-07-24-v1:validation`
- `phase4_final_validation_2026-07-24-v1:validation`

Registered reproduction and post-hoc explanation are separated below.

## Checked failures

The clean reproduction rules out failure to reproduce, unequal NFE
accounting, covariance asymmetry, loss of positive semidefiniteness, and
failure of continuous endpoint moments for Run 1. These are observations.
Their interpretation remains limited to the tested exact Gaussian grid.

Runs 2 through 5 checked floating-point sensitivity, higher-precision
agreement, local reconstruction, optional budgets, and parameter
perturbations. All focused checks passed.

## Remaining risks

- The strongest effect may be dominated by one low-variance eigenmode.
- A leading local coefficient may fail to rank paths because signed defects
  cancel after transport.
- Equal NFE gives different step counts across solvers. This is intended, but
  it prevents interpreting the result as an equal-step comparison.
- The minimal proposition is grid-aware and may be too artificial for a main
  scientific claim.
- The literature may already subsume solver-specific schedule dependence.
- A post-hoc proxy may fit the same rows that motivated it. Such a fit is not
  out-of-sample evidence.
- Optional NFE behavior may reverse under small target perturbations.

## Exclusions and invalidated outputs

Dimension 8 mixture evidence is excluded from decisions because its estimator
calibration failed. Dirty Phase 3 outputs are retained as historical
comparison inputs and are not release-ready. Smoke artifacts produced while
developing the Phase 4 audit runners are invalid for scientific claims and
must not appear in final tables.

No output has been deleted or overwritten.
