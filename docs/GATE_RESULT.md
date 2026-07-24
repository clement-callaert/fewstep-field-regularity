# Phase 3 gate result

Gate version: 2026-07-23-v1

Main run ID: `phase3_gate_registered_2026-07-23-v1`

Audited analysis run ID:
`phase3_gate_analysis_final_audit_2026-07-23-v2`

Decision: Continue to Phase 4 review only. Do not start Phase 5.

## Sampling and estimators

The sampling unit for every correlation is
`(target_family, path, solver, dim, nfe)`. The primary analysis has 108
configuration units. Ten seed estimates are nested inside each stochastic
mixture configuration. They are summarized by their median. They are not
treated as independent configuration samples.

Gaussian targets use exact Gaussian W2 on analytical moments propagated by
the numerical solver map. Mixture targets use sliced Wasserstein with 256
samples and 64 projections. This is an empirical diagnostic, not exact W2.
Projection sensitivity uses 32, 64, and 128 projections. The readiness
reference is `phase2_calibration:calibration_table`.
The post-result dimension audit is
`phase3_estimator_audit_2026-07-23:calibration_table`.

The primary metric estimator budget is 128 states at each of 24 times.
Mixture metric sensitivity also uses budget 32. All calculations use float64
on CPU.

## Continue conditions

### Condition 1

Does not hold.

Every alternative has a held-out mean per-family Spearman improvement over
`averaged_squared_lipschitz_proxy` of approximately zero. Every paired 95
percent bootstrap interval includes zero. Bootstrap resampling uses paired
configuration units within target family.

### Condition 2

Holds.

Calibration-ready stable baseline ranking inversions occur in three target
families:
anisotropic Gaussian, low-rank Gaussian, and two-mode GMM. The two-mode GMM
dimension 2 inversions survive the ten-seed rule and every combination of
metric budgets 32 and 128 with projection budgets 32, 64, and 128. The
Gaussian checks use analytical moments and have no stochastic seed replicate.

The pre-gate calibration directly covered mixture dimension 2, not dimension
8. The decisive condition does not depend on dimension 8 mixture evidence.
The two exact Gaussian families already satisfy the two-family threshold.
Dimension 2 two-mode blocks provide additional calibration-aligned evidence.
This condition is not a paper claim.

### Condition 3

Holds under the registered interaction rule, with a pivot warning.

For the low-rank Gaussian family, the preferred path is
variance-preserving for Euler and linear for Heun and RK4. This repeats at
both dimensions and all three NFE budgets. The field is affine, so there is no
seed or Wasserstein estimator uncertainty in this comparison.

A plausible explanation is solver order. Euler retains the first local error
term involving the material derivative of the field. Heun and RK4 cancel
lower-order terms. This explanation also means the Euler-specific part is
covered by pivot rule 8. Condition 3 is therefore not used as the only reason
to continue.

The corrected geometry-interaction table is diagnostic. It is not needed for
the gate decision.

### Condition 4

Does not hold.

No proposition or bound was proposed in Phase 3.

## Pivot explanations

1. Random seed variation: Does not explain the surviving condition 2
   evidence. It does explain several rejected mixture interaction candidates.
2. Wasserstein estimator instability: Applies to dimension 8 mixture evidence,
   which is excluded from the decision. It does not explain the stable
   dimension 2 two-mode blocks. Projection-budget sensitivity preserves them.
3. Endpoint singularities: Does not apply. Only linear and regular
   trigonometric variance-preserving paths were used.
4. Numerical precision: No precision failure was identified. The gate used
   float64. Higher-than-float64 checks were not run and remain a risk.
5. Unequal evaluation budgets: Does not apply. Requested and actual NFE agree
   for every observation.
6. Implementation error: Applies to superseded analysis reporting passes only.
   Cross-budget sensitivity was not initially family matched, the geometry
   table was omitted, and later pivot statuses were too strong. The audited
   analysis uses the same immutable main artifact.
7. Previously published result: Not assessed in Phase 3. A literature audit is
   Phase 4 work.
8. Disappears with a higher-order solver: Applies to the Euler-specific
   schedule preference used in condition 3. It does not explain condition 2,
   which includes Heun and RK4 inversions.

## Claim interpretation

The global baseline Spearman correlation is positive, but the per-family
correlations have different signs. H1 is inconclusive under the required
stratified reading.

No alternative reaches the condition 1 threshold. H2 is contradicted for the
registered alternatives in this small gate.

The registered temporal metric has a small positive residual rank association
after fitting baseline ranks. The gate registered no support threshold for
this diagnostic, and condition 1 fails. H3 is inconclusive.

Solver and geometry rankings change, but this is one registered gate run. H4
remains under-test and is not marked supported.

## Artifacts

- `phase2_calibration:calibration_table`
- `phase3_estimator_audit_2026-07-23:calibration_table`
- `phase3_gate_registered_2026-07-23-v1:gate_results`
- `phase3_gate_analysis_final_audit_2026-07-23-v2:correlations`
- `phase3_gate_analysis_final_audit_2026-07-23-v2:sensitivity`
- `phase3_gate_analysis_final_audit_2026-07-23-v2:inversions`
- `phase3_gate_analysis_final_audit_2026-07-23-v2:interactions`
- `phase3_gate_analysis_final_audit_2026-07-23-v2:decision`

The first analysis sensitivity and interaction artifacts are retained but are
invalidated for decision use.

## Unresolved risks

- The main run has dirty-code provenance because Phase 2 audit and Phase 3
  changes were uncommitted.
- Mixture error is sliced Wasserstein, not exact W2.
- Only two paths, two dimensions, and three NFE budgets were tested.
- Pre-gate mixture calibration directly covered dimension 2 only.
- Post-result calibration rejected dimension 8 mixture evidence for decision
  use.
- The dimension 2 low-rank Gaussian uses rank equal to ambient dimension.
- Gaussian comparisons have no seed uncertainty because they are analytical.
- Higher-than-float64 precision was not available in the gate workflow.
- Literature overlap has not been audited.
- The geometry interaction explanation needs human mathematical review.

## Recommendation

Continue to Phase 4 review of the surviving condition 2 inversions. Do not run
the Phase 5 Cartesian benchmark until a human reviews the artifacts,
dirty-code provenance, analysis correction, and pivot rule 8. No claim is
marked supported.
