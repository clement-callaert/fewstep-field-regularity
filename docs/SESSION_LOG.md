# Session log

Append one entry per work session. Do not delete prior entries.

## 2026-07-23 - Phase 0 scaffold

- Date: 2026-07-23
- Objective: Create repository scaffold and Phase 0 research infrastructure.
- Actions:
  - Created src-layout package `fewstep_regularities`.
  - Added Protocol interfaces for distributions, paths, fields, solvers,
    metrics, evaluators, and artifact writers.
  - Added Hydra configuration groups and dry-run CLI.
  - Wrote research process docs and decision gate.
  - Added paper retrieval script and index stubs.
  - Added artifact validation script and Phase 0 tests.
- Files changed: repository scaffold (see git status after review commit).
- Experiments launched: none (dry-run smoke only if executed during checks).
- Results observed: none scientific.
- Issues: none recorded at scaffold time.
- Decisions: Stop after Phase 0 and request code review before Phase 1.
- Next action: Code review of Phase 0, then Phase 1 exact Gaussian formulas.

## 2026-07-23 - Phase 1 exact Gaussians

- Date: 2026-07-23
- Objective: Implement exact Gaussian experiments and validate formulas.
- Actions:
  - Extracted source-cited formulas into paper notes (Lipman, Lipschitz-guided,
    Peyre, Albergo, Liu); recorded Hairer as missing.
  - Documented notation map and Gaussian affine / OT field derivations in
    docs/MATHEMATICAL_NOTES.md.
  - Implemented Gaussian distributions, SI-style paths, exact fields, equal-NFE
    Euler/Heun/RK4, exact Gaussian W2, and affine regularity metrics.
  - Added factories, gaussian_exact experiment mode, phase1_smoke and
    phase1_gaussian configs, and analytical/integration tests.
- Files changed: src/fewstep_regularities/{distributions,paths,fields,solvers,
  evaluation,metrics,experiments,cli}, tests/analytical/*, tests/integration/
  test_phase1_smoke.py, papers/notes/*, docs/MATHEMATICAL_NOTES.md,
  docs/UNRESOLVED_QUESTIONS.md, README.md, configs/experiment/phase1_*.yaml.
- Experiments launched: phase1_smoke (validation); phase1_gaussian available.
- Results observed: formula validation only; no scientific claims supported.
- Issues: Hairer PDF still missing; Lipschitz-guided uses effective scalar M
  for anisotropic targets.
- Decisions: Do not modify DECISION_GATE.md. Defer mixtures and gate to Phase 2+.
- Next action: Code review of Phase 1, then Phase 2 mixtures and estimator
  calibration.

## 2026-07-23 - Phase 1 audit and claim-safety fixes

- Date: 2026-07-23
- Objective: Audit Phase 1 completeness and fix claim-safety issues before push.
- Actions:
  - Fixed Lipschitz effective_M (max eigenvalue, not geometric mean).
  - Stopped silent dtype casts in Gaussian W2 evaluator.
  - Marked grid/trapezoid regularity metrics as non-exact.
  - Matched RNG generator device to compute device.
  - Hard-failed missing pushforward moment APIs.
  - Narrowed .gitignore so papers/notes and index are tracked; PDFs stay local.
- Files changed: factories, gaussian_w2, affine_gaussian, gaussian_exact,
  .gitignore, unit tests for factories and W2 dtype.
- Experiments launched: none new beyond re-running smoke via pytest.
- Results observed: 49 tests pass; ruff/mypy clean after fixes.
- Issues: none remaining critical for Phase 1 commit.
- Decisions: Do not push until user commits; provide push commands only.
- Next action: User commit and push, then Phase 2.

## 2026-07-23 - Phase 2 mixtures and estimator calibration

- Date: 2026-07-23
- Objective: Implement Gaussian mixtures and Wasserstein estimator calibration.
- Actions:
  - Fixed Bonneel PDF retrieval (wrong arXiv ID); extracted SW, Peyre entropic,
    and GMFlow context notes.
  - Documented GMM score and independent-coupling mixture marginal field in
    docs/MATHEMATICAL_NOTES.md.
  - Implemented GaussianMixture factories, MixtureAffineField, MC regularity
    metrics, projected/sliced/entropic/discrete OT evaluators.
  - Added phase2_smoke and phase2_calibration Hydra experiments and CLI modes.
- Files changed: distributions/gaussian_mixture.py, fields/mixture_affine.py,
  evaluation/projected_sliced.py, metrics/mixture_mc.py, experiments/*,
  configs/*, papers/notes/*, docs/*, README.md, tests/*.
- Experiments launched: phase2_smoke and phase2_calibration via pytest
  integration (when run).
- Results observed: formula and estimator validation only; no scientific
  claims supported.
- Issues: Bonneel was previously mis-downloaded; Hairer PDF still missing.
- Decisions: Do not modify DECISION_GATE.md. Do not run Phase 3 gate.
- Next action: Code review of Phase 2, then Phase 3 gate only if review passes.

## 2026-07-23 - Phase 2 audit fixes

- Date: 2026-07-23
- Objective: Resolve the blocking Phase 2 audit findings without running Phase 3.
- Actions:
  - Added convergence and marginal-feasibility checks to entropic OT and
    separated the regularized objective, transport component, and primary
    square-root diagnostic.
  - Corrected unequal-size empirical 1-D W2 integration and scoped discrete
    exactness to finite empirical measures.
  - Completed mixture dispatch for all registered regularity metrics.
  - Made Phase 2 tensor boundaries reject silent dtype and device conversions.
  - Made the bare Phase 2 smoke select GMM and sliced-Wasserstein defaults.
  - Expanded calibration to projected, sliced, entropic, and discrete
    diagnostics and registered summary artifacts.
- Scientific status: implementation fixes and numerical checks only. No claim
  status changed, no theorem status changed, and no Phase 3 gate was run.
- Decision: `DECISION_GATE.md` remains unchanged.

## 2026-07-23 - Phase 2 analytic mixture-field verification

- Date: 2026-07-23
- Objective: Replace a merely numerical mixture-field status with a direct
  analytic check while retaining the permitted `partially verified` label.
- Actions:
  - Derived the time-marginal GMM from conditional Gaussian laws.
  - Derived component and marginal velocities using Gaussian conditioning and
    the tower property.
  - Derived responsibility gradients and the full spatial Jacobian.
  - Verified the continuity equation by summing exact component equations.
  - Added deterministic pointwise continuity residual checks across all Phase
    2 GMM families, a full-covariance GMM, three schedules, and multiple times.
  - Added full-covariance AD Jacobian comparisons.
  - Documented that Lipschitz-guided clamped endpoint derivatives are numerical
    regularizations; Phase 2 smoke and calibration use the linear path.
- Scientific status: partially verified analytically and numerically. No
  theorem is marked proved and no Phase 3 gate was run.
- Decision: `DECISION_GATE.md` remains unchanged.

## 2026-07-23 - Phase 3 gate registration

- Timestamp: 2026-07-23T16:10:12Z
- Objective: Freeze the small Phase 3 decision-gate benchmark before outcomes.
- Prior checks:
  - Phase 1 and Phase 2 targeted tests passed: 115 tests.
  - `outputs/phase2_calibration` passed artifact validation.
  - The calibration marked sliced Wasserstein diagnostic readiness true.
- Registered grid:
  - Four families: anisotropic Gaussian, low-rank Gaussian, two-mode GMM,
    and imbalanced GMM.
  - Dimensions 2 and 8.
  - Linear and variance-preserving paths.
  - Euler, Heun, and RK4 at equal NFE 8, 16, and 32.
  - Ten seeds for stochastic mixture estimates.
  - Four metrics and mixture estimator budgets 32 and 128.
- Analysis:
  - The full frozen plan is `docs/PHASE3_ANALYSIS_PLAN.md`.
  - Exact artifact inputs and outputs are in
    `configs/analysis/phase3_gate.yaml`.
  - The configuration is the sampling unit. Seeds are nested estimates.
- Minimality: This grid supports held-out family correlations, path ranking
  inversions, schedule interactions, solver-order checks, dimension checks,
  NFE checks, and estimator-budget checks without running Phase 5.
- Outcome access: No Phase 3 smoke or main outcome was generated or inspected
  before this entry.
- Decision: Keep `docs/DECISION_GATE.md` unchanged.

## 2026-07-23 - Phase 3 analysis correction

- Timestamp: 2026-07-23T16:24:00Z
- Discovery point: After the main gate and first fixed analysis completed.
- Process errors:
  - Metric-budget sensitivity used only mixture families at budget 32 but all
    families at budget 128.
  - The registered schedule-by-geometry interaction table was not produced.
- Scope: The immutable main gate artifact, thresholds, primary metric budget,
  primary projection budget, nesting rule, and bootstrap rule are unchanged.
- Correction:
  - Reuse deterministic Gaussian metric rows in both metric-budget sensitivity
    strata so the target-family set is matched.
  - Produce the omitted geometry interaction table from the same immutable
    observations.
  - Save corrected analysis under new artifact IDs. Do not overwrite the first
    analysis.
- Invalidated outputs:
  - The first sensitivity table is invalid for cross-budget comparison.
  - The first interaction table is incomplete for geometry interactions.
- Unaffected outputs:
  - Primary correlations and paired bootstrap.
  - Ranking inversion checks.
  - The immutable gate results.
- Decision: Do not amend `docs/DECISION_GATE.md` because the error was found
  after main results were observed. Record it in the postmortem.

## 2026-07-23 - Phase 3 gate completion

- Timestamp: 2026-07-23T16:30:00Z
- Smoke: `phase3_gate_smoke_2026-07-23-v1` passed artifact validation.
- Main run: `phase3_gate_registered_2026-07-23-v1` completed with 17,568
  nested observation rows and exact equal-NFE accounting.
- Corrected analysis:
  `phase3_gate_analysis_corrected_2026-07-23-v1` passed artifact validation.
- Continue conditions:
  - Condition 1 does not hold.
  - Condition 2 holds in three target families.
  - Condition 3 holds under the registered interaction rule.
  - Condition 4 does not hold.
- Pivot checks:
  - Seed variation explains rejected mixture interactions, not the surviving
    condition 2 blocks.
  - Estimator sensitivity does not remove the stable two-mode inversions.
  - Pivot rule 8 applies to the Euler-specific condition 3 evidence.
  - The first analysis reporting error was corrected and retained.
- Claim status: No claim is marked supported. See docs/CLAIMS_LEDGER.md.
- Recommendation: Continue to Phase 4 review only. Stop before Phase 5 and
  request human review.

## 2026-07-23 - Full code and mathematics audit

- Objective: Audit the dirty worktree, formulas, statistics, provenance, and
  gate documentation before any commit.
- Confirmed and fixed:
  - Smoke resolved configs did not reflect the effective subset.
  - Superseded decision artifacts treated partial or unassessed pivot checks
    as false.
  - A geometry explanation did not match the family types in one block.
  - Analysis configs were hashed but not copied into analysis run directories.
  - The Lipschitz-guided anisotropic effective scalar was described too
    strongly relative to the source assumptions.
- Audited artifacts:
  - `phase3_gate_smoke_audited_2026-07-23-v1`
  - `phase3_gate_analysis_audited_2026-07-23-v1`
- Historical process issue: Pre-gate mixture calibration directly covered
  dimension 2, not dimension 8. The continue decision survives using exact
  Gaussian families and calibration-aligned dimension 2 mixture evidence.
- Source check: arXiv v3 of the Lipschitz-guided paper confirms Definition 3.2,
  the variance-log scalar schedule, the GMM field formula, and the restricted
  assumptions of Proposition 3.9.
- Decision: The gate recommendation remains Phase 4 review only. See
  docs/AUDIT_REPORT.md.

## 2026-07-23 - Final estimator-readiness audit

- Objective: Check mixture evaluator readiness at every gate dimension.
- Diagnostic:
  - `phase3_estimator_audit_2026-07-23` repeated calibration at dimensions 2
    and 8 with all ten gate seeds.
  - Dimension 2 remained the calibration-aligned mixture dimension.
  - Dimension 8 failed the sliced-versus-discrete diagnostic.
- Correction:
  - Excluded dimension 8 mixture blocks from condition 2 and condition 3
    decision evidence.
  - Kept the immutable registered gate results unchanged.
  - Wrote `phase3_gate_analysis_final_audit_2026-07-23-v2` under a new
    artifact ID.
- Result: Conditions 2 and 3 still hold. Condition 2 survives with two exact
  Gaussian families and dimension 2 two-mode mixture evidence.
- Decision: Continue to human Phase 4 review only. Do not start Phase 5.

## 2026-07-24 - Phase 4 planning and pre-run repair

- Status: Planning gate complete. Registered Run 1 not launched.
- Scope: Exact anisotropic and low-rank Gaussian families only, dimensions 2
  and 8, linear and variance-preserving paths, Euler, Heun, and RK4, and NFE
  8, 16, and 32.
- Comparison artifacts:
  - `phase3_gate_registered_2026-07-23-v1:gate_results`
  - `phase3_gate_analysis_final_audit_2026-07-23-v2:inversions`
  - `phase3_gate_analysis_final_audit_2026-07-23-v2:interactions`
- New planned run ID:
  `phase4_gaussian_reproduction_2026-07-24-v1`.
- Registered analysis:
  - The clean reproduction grid and comparison tolerance are fixed in
    `configs/experiment/phase4_gaussian_reproduction.yaml`.
  - The Phase 3 decision gate is unchanged.
- Post-hoc analysis:
  - No local error diagnostic was run.
  - No post-hoc quantity was added to the registered hypothesis list.
- Observation:
  - A temporary non-release integration test reproduced all 72 audited
    Gaussian rows within absolute tolerance `1e-12`.
  - This test is software validation. It is not a scientific artifact.
- Interpretation:
  - No mathematical explanation or proposition was accepted at this stage.
- Exact and estimated quantities:
  - Gaussian W2 is exact from analytically propagated numerical-map moments.
  - The averaged regularity baseline uses numerical time quadrature.
- Repairs:
  - Updated the valid artifact fixture checksum.
  - Added NumPy to the isolated pre-commit MyPy environment.
  - Added a dedicated Phase 4 runner with clean-code, input-hash,
    equal-NFE, covariance, comparison, and overwrite guards.
  - Moved affine numerical-map recovery and moment propagation into shared
    analysis functions used by both Phase 3 and Phase 4 runners.
- Checks:
  - Full suite: 132 tests passed in 5.29 seconds.
  - Ruff lint and format checks passed.
  - MyPy passed on 54 source files.
  - Pre-commit passed on all files.
- Exclusions:
  - No mixture result was generated or used.
  - Dimension 8 mixture evidence remains excluded from decisions.
  - No NFE 64 or 128 check was run.
  - No dimension 32 configuration was added.
- Invalidated outputs:
  - All superseded Phase 3 analyses remain preserved and retain their
    recorded invalidation status.
  - Dirty Phase 3 artifacts remain non-release-ready comparison inputs.
- Sources:
  - The planning source links remain recorded in
    `docs/PHASE4_PLAN.md`.
- Decision:
  - Commit and clean the reviewed worktree before Run 1.
  - Stop before Run 1 and do not start Phase 5.

## 2026-07-24 - CI dependency repair

- Status: Fixed locally. Awaiting a new GitHub Actions run.
- Scope: CI and development dependency resolution only. No scientific code,
  configuration grid, artifact, claim status, or decision rule changed.
- Failed workflow run: GitHub Actions run `30085501467`.
- Root cause:
  - Python 3.12 CI resolved NumPy 2.5.1 and MyPy 2.3.0.
  - MyPy targets Python 3.11 because the package supports Python 3.11.
  - The NumPy 2.5.1 stub used Python 3.12 type syntax, so MyPy stopped while
    parsing the dependency before checking project source.
- Repair:
  - Constrained project NumPy to `>=1.26,<2.5`.
  - Applied the same constraint to the isolated pre-commit MyPy environment.
- Validation:
  - NumPy 2.4.6 and MyPy 2.3.0 pass strict local checks.
  - Full suite: 132 tests passed.
  - Ruff lint and format checks passed.
  - Pre-commit passed on all files.
- Artifact IDs used: None. No experiment artifact was read or written.
- Registered and post-hoc analysis: Neither was run.
- Exact and estimated quantities: Not applicable.
- Exclusions: No Phase 4 run, mixture evidence, optional NFE, or new target.
- Invalidated outputs: None. The failed CI job is retained by GitHub.
- Interpretation: This was a dependency-resolution defect, not a scientific
  result.
- Sources: The exact installed versions and failure line are in GitHub Actions
  run `30085501467`.
- Unresolved question: The new GitHub Actions run must pass on Python 3.11 and
  Python 3.12 before Run 1.
