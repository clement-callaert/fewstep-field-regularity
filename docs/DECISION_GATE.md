# Decision gate

Status: Registered before any gate benchmark.

Version: 2026-07-23-v1

Immutability rule: Never modify this gate after observing the main results.
Any later amendment must be appended below with a timestamp and justification.

## Continue toward a full paper only if at least one condition holds

1. An alternative metric improves held-out Spearman correlation by at least
   0.15 relative to the primary baseline, and a paired bootstrap confidence
   interval for the improvement excludes zero.
2. At least two target families show a reproducible ranking inversion between
   the baseline metric and fixed-NFE Wasserstein error.
3. A stable schedule-by-solver or schedule-by-geometry interaction appears
   across seeds and has a plausible mathematical explanation.
4. A simple proposition or bound explains a reproducible phenomenon not
   already covered by the reviewed literature.

## Pivot if observed results are explained by

1. Random seed variation.
2. Wasserstein estimator instability.
3. Endpoint singularities.
4. Numerical precision.
5. Unequal evaluation budgets.
6. An implementation error.
7. A previously published result.
8. A phenomenon that disappears with a higher-order solver.

## Operational notes

- The gate benchmark is Phase 3. It must not run until Phases 0 to 2 are
  reviewed and analytical validations pass.
- Passing the gate does not authorize stronger paper claims than the claims
  ledger supports.
- Failing the gate is a valid scientific outcome and must be recorded in
  `docs/POSTMORTEM.md`.

## Amendments

None.
