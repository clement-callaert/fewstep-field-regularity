# Unresolved mathematical questions

These questions must be resolved from retrieved sources or explicit
derivations before corresponding implementations are treated as validated.

1. Exact notation conversion between stochastic interpolants, flow matching,
   and rectified flow for `(alpha_t, sigma_t)`.
2. When a Lipschitz-guided schedule is well-defined for mixture targets,
   including assumptions and endpoint behavior.
3. Validity domain of Gaussian OT displacement interpolation versus
   independent coupling for non-Gaussian mixtures.
4. Which Jacobian matrix norm and sampling measure match the baseline paper
   averaged squared Lipschitz proxy, after source verification.
5. Exact versus estimator status of each regularity metric under finite
   samples.
6. Endpoint singularity handling for VP and OT schedules at `t in {0, 1}`.
7. Fair equal-NFE accounting for multistage solvers (Heun, RK4) versus Euler.
8. Conditions under which empirical W2 estimators are stable enough for
   Spearman comparisons at the planned sample sizes.
9. Continuity-equation consistency tests that are practical for mixture
   fields.
10. Whether temporal stiffness metrics require exact `partial_t v` or only
    finite-difference estimators.
