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
