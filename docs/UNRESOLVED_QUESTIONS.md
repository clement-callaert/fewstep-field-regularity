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
   Status: open (Phase 2).

3. Validity domain of Gaussian OT displacement interpolation versus
   independent coupling for non-Gaussian mixtures.
   Status: open for mixtures. For Phase 1 Gaussians, Gaussian OT is valid
   via Peyré (2.40); independent coupling is a different path class.

4. Which Jacobian matrix norm and sampling measure match the baseline paper
   averaged squared Lipschitz proxy, after source verification.
   Status (Phase 1): Def 3.2 uses spectral 2-norm `∥∇b_t∥_2` and path measure
   of `I_t`. Implemented exactly for affine Gaussian fields.

5. Exact versus estimator status of each regularity metric under finite
   samples.
   Status (Phase 1): affine Gaussian metrics marked exact when Jacobians are
   state-independent. Monte Carlo estimators deferred to Phase 2.

6. Endpoint singularity handling for VP and OT schedules at `t in {0, 1}`.
   Status (Phase 1): trig VP and linear are regular on `[0,1]`. Lipman residual
   OT uses `σ_min > 0`. Lipschitz log-cov schedule requires `M ≠ 1` and
   positive schedule values.

7. Fair equal-NFE accounting for multistage solvers (Heun, RK4) versus Euler.
   Status (Phase 1): resolved. `n_steps = requested_nfe // evals_per_step`
   with exact divisibility required. See MATHEMATICAL_NOTES.md.

8. Conditions under which empirical W2 estimators are stable enough for
   Spearman comparisons at the planned sample sizes.
   Status: open (Phase 2 calibration).

9. Continuity-equation consistency tests that are practical for mixture
   fields.
   Status: open for mixtures. Gaussian affine fields use moment ODE checks
   in Phase 1.

10. Whether temporal stiffness metrics require exact `partial_t v` or only
    finite-difference estimators.
    Status (Phase 1): exact `partial_t v` used when the affine formula is
    differentiable; FD fallback documented with tolerance.
