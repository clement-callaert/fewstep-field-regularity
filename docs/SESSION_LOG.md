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

## 2026-07-24 - CI test portability repair

- Status: Fixed locally. Awaiting a new GitHub Actions run.
- Scope: Test portability and explicit input configuration only. No
  scientific grid, numerical formula, artifact claim, or decision rule
  changed.
- Failed workflow: `Fix NumPy typing compatibility in CI #5`, commit
  `10209b0`.
- Root causes:
  - The Phase 3 smoke test relied on an ignored local Phase 2 calibration
    artifact.
  - The Phase 4 integration test relied on ignored local Phase 3 artifacts.
  - The valid artifact fixture stored an absolute workstation path.
- Repairs:
  - Added an optional explicit Phase 2 calibration input to the Phase 3
    runner without changing the registered Phase 3 config.
  - The Phase 3 integration tests list that input in their resolved Hydra
    configs.
  - Made both integration tests create their required inputs under the pytest
    temporary directory.
  - Made the fixture artifact path relative to its run directory.
  - Made artifact validation resolve relative artifact paths from the run
    directory.
- Validation:
  - The three failing CI tests pass locally.
  - Full suite: 132 tests passed in 5.37 seconds.
  - MyPy and every pre-commit hook passed.
- Artifact IDs used: None. Test artifacts are temporary and non-release.
- Registered and post-hoc analysis: Neither was run.
- Exact and estimated quantities: Not applicable.
- Exclusions: No registered Phase 4 run, optional NFE, mixtures, or new target.
- Invalidated outputs: None.
- Interpretation: These were checkout-portability defects in tests.
- Sources: The GitHub Actions failure log supplied by the repository owner.
- Unresolved question: Both CI matrix jobs must pass before Run 1.

## 2026-07-24 - Phase 4 Run 1 clean Gaussian reproduction

- Status: Completed and validated. Stopped before Run 2.
- Scope:
  - anisotropic Gaussian and low-rank Gaussian
  - dimensions 2 and 8
  - linear and variance-preserving paths
  - Euler, Heun, and RK4
  - NFE 8, 16, and 32
  - float64 on CPU
- Run ID: `phase4_gaussian_reproduction_2026-07-24-v1`.
- Code commit: `083dbf96b5bf189650d7d3d519b99887f18aa15e`.
- Config hash:
  `82ec484f42fb8cd45000e4c3c8b399d46a64763226bf84ed2235080a1dae7e2b`.
- Artifact IDs:
  - `phase4_gaussian_reproduction_2026-07-24-v1:results`
  - `phase4_gaussian_reproduction_2026-07-24-v1:phase3_comparison`
  - `phase4_gaussian_reproduction_2026-07-24-v1:validation`
- Input artifact IDs:
  - `phase3_gate_registered_2026-07-23-v1:gate_results`
  - `phase3_gate_analysis_final_audit_2026-07-23-v2:inversions`
  - `phase3_gate_analysis_final_audit_2026-07-23-v2:interactions`
- Clean-code gate:
  - The worktree was clean and synchronized with `origin/main`.
  - Full suite: 132 tests passed.
  - Ruff lint and format checks passed.
  - MyPy passed on 54 source files.
  - Pre-commit passed on all files.
- Runtime:
  - Manifest runtime: 0.350331 seconds.
  - Full command wall time: 2.03 seconds.
  - Hard stop: 45 minutes.
- Registered analysis:
  - Run 1 used the frozen 72-configuration grid.
  - The absolute Phase 3 comparison tolerance was `1e-12`.
- Post-hoc analysis:
  - No solver-specific diagnostic or new regularity metric was evaluated.
  - A summary of inversion margins was computed only to validate and report
    the reproduced rows.
- Observations:
  - All 72 Phase 4 error values equal their Phase 3 comparison values.
  - All 72 baseline metric values equal their Phase 3 comparison values.
  - Fourteen baseline inversion blocks reproduce.
  - The strongest reproduced inversion by absolute Gaussian W2 margin is
    low-rank Gaussian, dimension 8, Euler, NFE 8.
  - Its linear and variance-preserving errors are 0.8108540111 and
    0.4564779075, giving margin 0.3543761036.
  - In the low-rank Gaussian family, variance-preserving is preferred for
    Euler and linear is preferred for Heun and RK4 at both dimensions and all
    three NFE budgets.
- Numerical validation:
  - Equal NFE passed for every row.
  - Covariance symmetry and positive semidefiniteness passed for every row.
  - Minimum numerical covariance eigenvalue: 0.0273188110.
  - Maximum numerical covariance eigenvalue: 10.8536434383.
  - Maximum numerical affine-map condition number: 16.6018078049.
  - Maximum continuous endpoint Gaussian W2 check: 6.3220272766e-08.
- Exact and estimated quantities:
  - Endpoint Gaussian W2 uses analytical moments propagated through the
    numerical affine map and is exact for those represented Gaussian laws.
  - The baseline metric uses numerical time quadrature and is not symbolic
    exact.
- Interpretation:
  - Run 1 establishes clean reproduction only.
  - It does not establish numerical precision separation, a solver-specific
    mechanism, a proposition, or novelty.
- Exclusions:
  - No mixture result was generated or used.
  - Dimension 8 mixture evidence remains excluded from decisions.
  - NFE 64 and 128 were not run.
  - Dimension 32 was not added.
- Invalidated outputs:
  - Superseded Phase 3 analyses remain preserved and invalidated as recorded.
  - Dirty Phase 3 artifacts remain comparison inputs only.
- Sources:
  - Mathematical and literature sources remain listed in
    `docs/PHASE4_PLAN.md`.
  - No new literature conclusion was made.
- Claims:
  - P4-C1 remains under-test.
  - P4-C2 remains under-test.
  - P4-C3 remains proposed.
  - P4-P1 remains proposed.
- Unresolved questions:
  - Whether inversion margins dominate higher-precision numerical error.
  - Which affine eigendirections generate the strongest inversion.
  - Why solver order changes the low-rank path preference.
  - Whether the mechanism is already established in prior literature.
- Decision:
  - Run 2 is justified because the clean Gaussian inversions reproduce.
  - Stop before Run 2 for artifact and scientific review.

## 2026-07-24: Phase 4 Run 2 precision audit

Status: Complete and release-ready.

Scope: The 72 exact Gaussian Run 1 configurations at 80 decimal digits.

Artifact IDs used:

- `phase4_gaussian_reproduction_2026-07-24-v1:results`
- `phase4_precision_2026-07-24-v1:table`
- `phase4_precision_2026-07-24-v1:validation`

- Code commit: `2a28fd41193fb2c2500d13af4b2c364601c1d12b`.
- Config hash:
  `d58d1bb54cd0a24c741cacc87aff1a03c95fc8cc672e7d1006f8ed9a27dc192b`.
- Runtime:
  - Manifest runtime: 0.177238 seconds.
  - Command wall time: 1.95 seconds.
  - Hard stop: 45 minutes.
- Registered analysis:
  - This run is the pre-specified high-accuracy check of Run 1.
- Post-hoc analysis:
  - None.
- Observation:
  - All 72 comparisons passed.
  - The maximum absolute float64 versus 80-digit W2 difference is
    `9.7050430488e-10`.
  - The acceptance tolerance is `2e-9`.
- Interpretation:
  - Float64 reference error is much smaller than the strongest inversion
    margin. The complete minimum-margin comparison is deferred to the final
    precision table.
- Exact and estimated quantities:
  - The reference uses scalar commuting eigenmode propagation in mpmath.
  - It is a high-precision numerical reference, not a symbolic exact value.
- Exclusions:
  - No mixture, dimension 32, or optional NFE was used.
- Invalidated outputs:
  - Earlier dirty smoke runs remain excluded.
- Decision:
  - Run 3 is justified because the precision audit passed.
  - Stop before Run 3 for artifact review.

## 2026-07-24: Phase 4 Run 3 affine error decomposition

Status: Complete and release-ready.

Scope: Mean, covariance, eigenmode, local defect, and endpoint transport
decomposition for the 72 Run 1 Gaussian configurations.

Artifact IDs used:

- `phase4_gaussian_reproduction_2026-07-24-v1:results`
- `phase4_decomposition_2026-07-24-v1:table`
- `phase4_decomposition_2026-07-24-v1:validation`

- Code commit: `e3ad51a16fba8289e91c86b247e75e5761fdc51b`.
- Config hash:
  `a8e6f7355b2fc36d2abdd5105e92d0ab958cb068cf8ff2ff408bb062048362aa`.
- Runtime:
  - Manifest runtime: 0.043046 seconds.
  - Command wall time: 1.72 seconds.
  - Hard stop: 60 minutes.
- Registered analysis:
  - None. The decomposition is a pre-specified Phase 4 workstream but is
    post-hoc relative to the Phase 3 hypotheses.
- Post-hoc analysis:
  - Eigenvalue-wise W2 contributions and transported local defects.
- Observations:
  - All 72 W2 reconstructions passed.
  - Maximum reconstruction difference: `9.7050436884e-10`.
  - The mean error is zero in every centered configuration.
  - In the strongest inversion, the dominant target covariance eigenvalue is
    `10.6756382265`.
  - Its squared W2 contribution is `0.4939430141` for linear Euler and
    `0.1837966072` for variance-preserving Euler at dimension 8 and NFE 8.
- Interpretation:
  - The strongest inversion is driven mainly by the largest-variance target
    eigendirection, not by a mean error.
  - Exact transported local defects provide a mechanism for the endpoint
    factor difference. Their value as a general predictor is not established.
- Exact and estimated quantities:
  - Propagated moments and commuting W2 contributions are analytical for each
    represented numerical affine map.
  - Floating-point evaluation causes the reported reconstruction residual.
- Exclusions:
  - No mixture, dimension 32, or optional NFE was used.
- Invalidated outputs:
  - Earlier dirty smoke decompositions remain excluded.
- Decision:
  - Run 4 is justified because the decomposition is stable and identifies a
    dominant eigenmode.
  - Stop before Run 4 for artifact review.

## 2026-07-24: Phase 4 Run 4 solver diagnostics

Status: Complete and release-ready.

Scope: Pre-declared post-hoc diagnostics for the 72 Run 1 Gaussian
configurations.

Artifact IDs used:

- `phase4_gaussian_reproduction_2026-07-24-v1:results`
- `phase4_diagnostics_2026-07-24-v1:table`
- `phase4_diagnostics_2026-07-24-v1:validation`

- Code commit: `f3ad0f96024175228fd622e83c28c4d681fd70a7`.
- Config hash:
  `c135d79214f25c444175657f7769677c41cd66fe9ba8718f6b19f294bca56716`.
- Runtime:
  - Manifest runtime: 8.109213 seconds.
  - Command wall time: 9.72 seconds.
  - Hard stop: 60 minutes.
- Registered analysis:
  - None.
- Post-hoc analysis:
  - Integrated material derivative norms, temporal Jacobian variation,
    solver-specific leading local coefficients, and exact local log defects.
- Observations:
  - All 72 eigenmode endpoint reconstructions passed.
  - Maximum reconstruction difference: `9.7050436884e-10`.
  - Across 36 two-path blocks, the baseline, integrated material derivative,
    and expected material derivative each agree with the observed preferred
    path in 22 blocks.
  - The solver-specific leading local proxy agrees in 29 blocks.
  - The unsigned exact local log defect agrees in 22 blocks.
  - In low-rank Gaussian, the leading proxy agrees in all six Euler blocks,
    five of six Heun blocks, and four of six RK4 blocks.
- Interpretation:
  - Solver stages and derivatives explain more of the observed ordering on
    this same diagnostic grid than the averaged baseline.
  - This is not out-of-sample evidence and does not establish predictive
    superiority.
  - Unsigned local defects can fail because sign cancellation and endpoint
    transport matter. The exact transported decomposition remains the
    stronger mathematical explanation.
- Exact and estimated quantities:
  - The endpoint reconstruction uses exact scalar affine step formulas up to
    float64 evaluation.
  - Time integrals use 257-point numerical quadrature and are estimated.
- Exclusions:
  - No mixture, dimension 32, optional NFE, or new family was used.
- Invalidated outputs:
  - Earlier dirty smoke diagnostics remain excluded.
- Decision:
  - P4-C3 cannot be marked supported from this same-grid post-hoc comparison.
  - Run 5 is justified to test optional budgets and perturbations.
  - Stop before Run 5 for artifact review.

## 2026-07-24: Phase 4 Run 5 robustness

Status: Complete and release-ready.

Scope: The two Gaussian families, two dimensions, two paths, three solvers,
three primary NFE budgets, ±10 percent target perturbations, and unperturbed
NFE 64 and 128 checks.

Artifact IDs used:

- `phase4_gaussian_reproduction_2026-07-24-v1:results`
- `phase4_robustness_2026-07-24-v1:table`
- `phase4_robustness_2026-07-24-v1:validation`

- Code commit: `08c14852676196d0a697b2f65be6bd5ba44d06f5`.
- Config hash:
  `1b10d16804d30623a70fd068dde496766506d0edd92d405a7a695904887610b9`.
- Runtime:
  - Manifest runtime: 0.055365 seconds.
  - Command wall time: 1.78 seconds.
  - Hard stop: 90 minutes.
- Registered analysis:
  - None. The robustness checks were pre-declared for Phase 4 but are outside
    the Phase 3 gate.
- Post-hoc analysis:
  - Small target-parameter perturbations and optional NFE budgets.
- Observations:
  - All 264 endpoint errors are finite.
  - All 132 two-path preference blocks were evaluated.
  - The low-rank pattern has zero failures: variance-preserving is preferred
    for Euler, while linear is preferred for Heun and RK4.
  - The pattern persists at both dimensions for perturbations -10 percent,
    zero, and +10 percent at NFE 8, 16, and 32.
  - The unperturbed pattern also persists at NFE 64 and 128.
- Interpretation:
  - The low-rank solver-dependent preference is stable in the tested local
    parameter neighborhood and optional budgets.
  - This remains focused robustness evidence, not a universal statement.
- Exact and estimated quantities:
  - Endpoint errors use scalar affine propagation and commuting Gaussian W2.
  - No sampling estimator is used.
- Exclusions:
  - No mixture, dimension 32, new family, or full Cartesian grid was used.
- Invalidated outputs:
  - Earlier dirty smoke robustness output remains excluded.
- Decision:
  - Run 6 is justified because all focused robustness checks passed.
  - Stop before Run 6 for artifact review.

## 2026-07-24: Phase 4 Run 6 final focused validation

Status: Complete and release-ready.

Scope: Validation aggregation for the explicitly listed Run 1 through Run 5
artifacts. No new scientific grid was run.

Artifact IDs used:

- `phase4_final_validation_2026-07-24-v1:table`
- `phase4_final_validation_2026-07-24-v1:validation`

- Code commit: `cc0c56ab24cd159efe5005074de9fd0c98120e5a`.
- Config hash:
  `a091cee17347767bcd9133de6c3139b7e9ea1f6fd48e1b1c63232f2c300e80eb`.
- Runtime:
  - Manifest runtime: 0.011677 seconds.
  - Command wall time: 1.74 seconds.
  - Hard stop: 120 minutes.
- Registered analysis:
  - None. Run 6 aggregates validations.
- Post-hoc analysis:
  - Final focused audit summary only.
- Observation:
  - All five input validations and the Run 6 manifest pass.
- Interpretation:
  - Passing validation does not itself establish a scientific claim.
- Exact and estimated quantities:
  - Run 6 computes no new scientific quantity.
- Exclusions:
  - No mixtures, dimension 32, new family, or Cartesian benchmark.
- Invalidated outputs:
  - Dirty smoke and superseded Phase 3 artifacts remain recorded and excluded.
- Decision:
  - Phase 4 execution is complete.
  - Recommend pivot. Do not start Phase 5 or draft a full paper.

## 2026-07-24: Repository-state resolution before workshop construction

Status: Complete.

Scope: Git-state audit only. No scientific file was changed in this step.

- Branch: `main`, tracking `origin/main`.
- HEAD hash: `3c47b6799d6bbd5ba9b53617a69835b80491f596`
  ("Complete focused Phase 4 audit").
- Local `origin/main` hash before fetch:
  `3c47b6799d6bbd5ba9b53617a69835b80491f596`.
- Divergence before fetch: `git log --left-right --count origin/main...HEAD`
  reported `0 0`.
- `git fetch origin` succeeded; network access is available.
- `origin/main` hash after fetch:
  `3c47b6799d6bbd5ba9b53617a69835b80491f596`.
- Divergence after fetch: `0 0`. Local and remote are identical.
- Working tree at audit time: uncommitted modifications to `README.md`,
  `docs/CLAIMS_LEDGER.md`, `docs/PHASE4_MATHEMATICAL_ANALYSIS.md`, and
  `docs/PHASE4_RESULTS.md`; untracked `docs/P4_P1_PROOF_AUDIT.md`,
  `docs/WORKSHOP_PAPER_CLAIMS.md`, `docs/WORKSHOP_PAPER_OUTLINE.md`, and
  `docs/WORKSHOP_TARGETS.md`. These are the workshop-preparation documents
  from the previous session and will be committed with the workshop work.
- No force-push and no history rewrite was performed or is needed.

Decision: Proceed to the workshop submission construction phase against
HEAD `3c47b67`.
