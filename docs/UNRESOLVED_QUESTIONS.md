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
    Status (Phase 4): resolved for the focused grid. Run 1 reproduced all 72
    rows and 14 inversion blocks from clean commit `083dbf9`.

12. Which covariance eigendirections dominate the strongest Gaussian
    inversion.
    Status (Phase 4): resolved for the strongest inversion. The largest target
    covariance eigenvalue dominates. Broader uniform mode statements remain
    open.

13. Why Euler prefers variance-preserving in the low-rank Gaussian family
    while Heun and RK4 prefer linear under equal NFE.
    Status (Phase 4): partially resolved. Solver stage sampling and the
    derivative-dependent local coefficients differ, and exact transported
    local defects reconstruct endpoint factor error. A concise asymptotic sign
    proof for the whole low-rank parameter range remains open.

14. Whether a solver-specific leading local error quantity explains both
    Gaussian geometry families.
    Status (Phase 4): inconclusive. The leading proxy agrees in 29 of 36
    blocks but is post-hoc, in-sample, and misses three low-rank blocks.

15. Whether the smallest RK4 inversion margins dominate higher-precision
    numerical error.
    Status (Phase 4): resolved for the focused grid. The smallest margin is
    more than 11,500 times the maximum 80-digit reference difference.

16. Whether a minimal affine non-implication proposition can be stated without
    artificial assumptions.
    Status (workshop preparation, 2026-07-24): resolved for the grid-aware
    statement. P4-P1 passed the documented adversarial proof audit
    (docs/P4_P1_PROOF_AUDIT.md ends "proof verified"). The construction
    remains grid-aware by design; a grid-independent variant is question 18.

17. Whether the observed mechanism is already established in numerical ODE,
    diffusion schedule, or flow matching literature.
    Status (Phase 4): partially resolved. Solver-specific schedule dependence
    and exact-linear solver design are established in prior work. No exact
    match to the commuting Gaussian construction was located. Novelty remains
    under expert literature review.

18. Whether P4-P1 has a natural construction that is not tailored to the
    solver grid.
    Status (Phase 4): open.

19. Whether the solver-specific leading proxy generalizes out of sample.
    Status (workshop preparation, 2026-07-24): open. The pre-registered
    non-centered replication tested the primary ranking claim, not the
    proxy; the proxy remains post-hoc and in-sample.

20. Whether a uniform asymptotic argument explains the sign of the low-rank
    path preference for all sufficiently large NFE.
    Status (Phase 4): open. NFE 64 and 128 preserve the tested pattern, but
    finite checks do not establish an asymptotic theorem.

21. Whether the ranking non-implication persists outside the Phase 3/4
    design space.
    Status (workshop preparation, 2026-07-24): resolved for exactly one
    pre-registered non-centered commuting Gaussian family
    (`workshop_external_validation_2026-07-24-v1`): 11 of 18 comparison
    blocks invert and pass the 80-digit audit. Learned-model validation,
    non-commuting Gaussian validation, and any broader population claim
    remain open.
