# Code and mathematics audit

Date: 2026-07-23

Scope: Full dirty worktree, Phase 1 to Phase 3 mathematical code, statistical
analysis, artifact provenance, tests, and scientific documentation.

## Verdict

No unresolved blocking code defect remains after the corrections listed below.
The Phase 3 continue decision is unchanged. It is supported by condition 2
using exact Gaussian evidence even if mixture dimension 8 is excluded.

The repository still has scientific and provenance limitations. They are
listed below and prevent calling the work release-ready.

## Corrections made during the audit

1. The Phase 3 smoke runner wrote its resolved config before applying the
   smoke subset. The runner now writes the effective executed grid. A new smoke
   run validates the correction.
2. The first two analysis decision artifacts reported several pivot checks as
   false even when they were partial or unassessed. The audited analysis uses
   explicit statuses and does not turn missing evidence into a negative result.
3. One geometry-interaction explanation mentioned mixture fields even when a
   block contained only Gaussian families. Explanations now depend on the
   family types in each block.
4. The analysis config was included in the config hash but was not copied into
   the run directory. Audited analysis runs now save
   `resolved_analysis_config.yaml` and its hash.
5. Metric-budget sensitivity originally compared different family sets. The
   audited table uses the same family set at both metric budgets.
6. The registered geometry interaction table was originally omitted. It is
   present in the audited analysis.
7. The Lipschitz-guided source note incorrectly described the anisotropic
   effective scalar. The code uses a documented heuristic. It is not claimed
   to be the source-optimal rule outside Proposition 3.9 assumptions.
8. The pre-gate estimator calibration covered mixture dimension 2 only. A
   post-result audit found that dimension 8 failed the calibration diagnostic.
   The final analysis excludes dimension 8 mixture blocks from decision
   evidence.

## Code audit

- Tensor boundaries reject silent dtype and device conversions.
- Gate experiments require float64.
- Gaussian endpoint moments are propagated through the affine numerical solver
  map without particle estimation.
- Mixture targets refuse `gaussian_ot`.
- Euler, Heun, and RK4 record actual NFE equal to requested NFE.
- Main and analysis runners refuse to overwrite completed run manifests.
- Configuration and artifact paths are resolved from the repository root.
- Seed reuse across solvers and paths provides paired stochastic comparisons.
- Bootstrap resampling uses configuration units within target family. Seed rows
  remain nested.

## Mathematical audit

- The Gaussian affine field follows joint Gaussian conditioning.
- The Gaussian OT field and Gaussian W2 use the Bures formulas.
- The mixture marginal field follows componentwise Gaussian conditioning and
  posterior responsibilities.
- The mixture Jacobian outer-product orientation matches componentwise
  differentiation.
- The continuity equation follows by summing component continuity equations.
- Sliced Wasserstein is labeled empirical and is never called exact W2.
- Entropic transport is labeled regularized and is never called exact W2.
- The Euler local error explanation uses the material derivative
  `partial_t b + J b`. It is an explanation, not a theorem.
- No proposition is marked proved.

Primary source checks used:

- [Lipschitz-guided schedules, arXiv v3](https://arxiv.org/abs/2509.01629)
- [Stochastic Interpolants](https://arxiv.org/abs/2303.08797)
- [Computational Optimal Transport](https://arxiv.org/abs/1803.00567)
- [Sliced and Radon Wasserstein Barycenters](https://hal.science/hal-00881872)

## Statistical audit

The primary sampling unit is
`(target_family, path, solver, dim, nfe)`. The primary analysis contains 108
configuration units. Mixture seed estimates are summarized inside each unit.

Condition 1 remains false. Condition 2 remains true. Condition 3 remains true
under its registered interaction rule, with pivot rule 8 applying to its
Euler-specific part. Condition 4 remains false.

The low-rank Gaussian family at dimension 2 uses rank 2, so it is not
low-dimensional relative to the ambient space. The dimension 8 member is
genuinely low rank. The condition 2 decision does not depend on calling the
dimension 2 member low rank.

## Provenance audit

Validated artifacts:

- `phase2_calibration`
- `phase3_estimator_audit_2026-07-23`
- `phase3_gate_smoke_audited_2026-07-23-v1`
- `phase3_gate_registered_2026-07-23-v1`
- `phase3_gate_analysis_final_audit_2026-07-23-v2`

The registered main run was produced from dirty code and is not release-ready.
The exact main input checksum remains unchanged across every analysis pass.

The first analysis sensitivity table and interaction table are invalidated.
The second corrected analysis is superseded by the audited analysis because
its pivot statuses and one explanation were incomplete. The next audited
analysis is superseded by the final audit because it still admitted
uncalibrated dimension 8 mixture evidence.

## Remaining limitations

- The Phase 2 pre-gate calibration directly covered dimension 2 only. The
  post-result audit rejected dimension 8 mixture evidence for decision use.
- The registered run used float64. Higher precision was not tested.
- Mixture outcomes use sliced Wasserstein with finite samples and projections.
- The main artifact has dirty-code provenance.
- The full literature-overlap question is not closed.
- The Lipschitz-guided anisotropic effective scalar is a heuristic.

These limitations are disclosed in the gate result and claims ledger. They do
not change the recommendation to continue only to human Phase 4 review.
