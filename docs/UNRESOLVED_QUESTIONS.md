# Unresolved mathematical questions

These questions must be resolved from retrieved sources or explicit
derivations before corresponding implementations are treated as validated.

1. Exact notation conversion between stochastic interpolants, flow matching,
   and rectified flow for `(alpha_t, sigma_t)`.
   Status (Phase 1): resolved for implemented paths. See
   docs/MATHEMATICAL_NOTES.md notation conversion. Lipman residual `σ_t` is
   not SI `β_t`.

2. When a Lipschitz-guided schedule is well-defined for mixture targets,
   including assumptions and endpoint behavior.
   Status (Phase 2): partially resolved. Effective `M` uses the largest
   eigenvalue of the mixture covariance (same Phase 1 rule). Full paper
   assumptions for mixture targets remain open.

3. Validity domain of Gaussian OT displacement interpolation versus
   independent coupling for non-Gaussian mixtures.
   Status (Phase 2): resolved for implementation policy. Gaussian OT is
   refused for GMM targets in factories. Independent coupling mixture
   marginal fields are implemented and checked. For Phase 1 Gaussians,
   Gaussian OT remains valid via Peyré (2.40).

4. Which Jacobian matrix norm and sampling measure match the baseline paper
   averaged squared Lipschitz proxy, after source verification.
   Status (Phase 1): Def 3.2 uses spectral 2-norm `∥∇b_t∥_2` and path measure
   of `I_t`. Implemented exactly for affine Gaussian fields.

5. Exact versus estimator status of each regularity metric under finite
   samples.
   Status (Phase 2): mixture metrics use Monte Carlo sampling from the
   time-`t` marginal GMM and are marked non-exact. Affine Gaussian metrics
   remain as in Phase 1 (state-independent Jacobians; trapezoidal time grid).

6. Endpoint singularity handling for VP and OT schedules at `t in {0, 1}`.
   Status (Phase 1): trig VP and linear are regular on `[0,1]`. Lipman residual
   OT uses `σ_min > 0`. Lipschitz log-cov schedule requires `M ≠ 1` and
   positive schedule values.

7. Fair equal-NFE accounting for multistage solvers (Heun, RK4) versus Euler.
   Status (Phase 1): resolved. `n_steps = requested_nfe // evals_per_step`
   with exact divisibility required. See MATHEMATICAL_NOTES.md.

8. Conditions under which empirical W2 estimators are stable enough for
   Spearman comparisons at the planned sample sizes.
   Status (Phase 2): partially verified. The calibration experiment
   (`experiment=phase2_calibration`) covers projected, sliced, entropic, and
   exact empirical discrete W2 diagnostics across multiple seeds. Differences
   from continuous Gaussian W2 are diagnostic comparisons, not universal bias
   estimates. Criteria remain outside `DECISION_GATE.md`.

9. Continuity-equation consistency tests that are practical for mixture
   fields.
   Status (Phase 2): resolved for the implemented independent scalar
   schedules. The componentwise analytic continuity derivation is documented
   in MATHEMATICAL_NOTES.md. Deterministic pointwise AD residual checks,
   AD Jacobian checks, and a moment-evolution MC check are implemented.

10. Whether temporal stiffness metrics require exact `partial_t v` or only
    finite-difference estimators.
    Status (Phase 1): exact `partial_t v` used when the affine formula is
    differentiable; FD fallback documented with tolerance.

11. Whether every decisive exact Gaussian inversion reproduces from a clean
    Phase 4 commit.
    Status (Phase 4): under-test. A temporary software integration check
    matches the audited dirty-code rows, but registered Run 1 has not started.

12. Which covariance eigendirections dominate the strongest Gaussian
    inversion.
    Status (Phase 4): open. No affine decomposition run has started.

13. Why Euler prefers variance-preserving in the low-rank Gaussian family
    while Heun and RK4 prefer linear under equal NFE.
    Status (Phase 4): open. Solver order is an interpretation, not yet a
    source-verified derivation.

14. Whether a solver-specific leading local error quantity explains both
    Gaussian geometry families.
    Status (Phase 4): open. Any candidate evaluated on the motivating rows
    will remain labeled post-hoc.

15. Whether the smallest RK4 inversion margins dominate higher-precision
    numerical error.
    Status (Phase 4): open. The precision audit has not started.

16. Whether a minimal affine non-implication proposition can be stated without
    artificial assumptions.
    Status (Phase 4): proposed. No proposition is marked proved.

17. Whether the observed mechanism is already established in numerical ODE,
    diffusion schedule, or flow matching literature.
    Status (Phase 4): open. The Phase 4 primary-source audit has not started.
