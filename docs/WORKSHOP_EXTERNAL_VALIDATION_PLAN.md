# Workshop external validation plan

Status: **Frozen before execution on 2026-07-24.** No exploratory run,
partial computation, or preview of the family below was performed before
this freeze. Any change to this file after execution invalidates the
pre-registration.

Governing constraints: this validation may support only a limited
supporting claim under `docs/WORKSHOP_PAPER_CLAIMS.md`. It may not broaden
the primary claim beyond the tested systems, may not use mixtures, and may
not promote the post-hoc solver-specific proxy. Exactly one new family is
registered. No second family may be added after seeing the outcome.

## 1. Registered family

One new **non-centered anisotropic Gaussian family** ("shifted anisotropic
Gaussian"), not used in Phase 3 or Phase 4. Phases 3 and 4 used only
centered targets (anisotropic with anisotropy 4.0 and low-rank), and every
prior source was `N(0, I)`. This family has nonzero source and target
means and a new anisotropy value.

For dimension \(d\):

- Source: \(N(\mu_0, I_d)\) with \(\mu_{0,i} = 0.75\,(-1)^i\),
  \(i = 0,\dots,d-1\).
- Target: \(N(\mu_1, D)\) with \(\mu_{1,i} = 1.0 + 0.25\,i\) and
  \(D=\operatorname{diag}(\lambda_i)\), where the \(\lambda_i\) form a
  geometric sequence from \(6^{-1/2}\) to \(6^{1/2}\) (condition number
  6.0, the existing `anisotropic_gaussian` eigenvalue rule with anisotropy
  6.0).

Both endpoints are closed-form and deterministic. The geometry seed below
is recorded for manifest completeness; the family consumes no randomness.

Marginal path: \(X_t=\alpha(t)X_0+\sigma(t)X_1\) with independent
endpoints. Because the source covariance is \(I\) and \(D\) is diagonal,
\(Q(t)=\alpha^2 I+\sigma^2 D\) commutes with \(D\) and the system stays
modal. The exact marginal drift is affine,

\[
b(t,x)=A(t)x+c(t),\qquad
A(t)=C_tQ(t)^{-1},\qquad
c(t)=\dot m_t-A(t)m_t,
\]

with \(m_t=\alpha\mu_0+\sigma\mu_1\) and
\(\dot m_t=\alpha'\mu_0+\sigma'\mu_1\). Since \(\mu_0\) and \(\mu_1\) are
nonzero and non-proportional, \(c(t)\) is nonzero: the required
non-centered structure is present. The exact Gaussian W2 is available in
closed modal form,

\[
W_2^2=\lVert \hat m-\mu_1\rVert^2
+\sum_i\left(\lvert r_i\rvert-\sqrt{\lambda_i}\right)^2,
\]

for a diagonal numerical endpoint map with modal factors \(r_i\) and
numerical endpoint mean \(\hat m\), starting from source moments
\((\mu_0, I)\).

## 2. Frozen experimental grid

| item | frozen value |
| --- | --- |
| source mean | \(\mu_{0,i}=0.75\,(-1)^i\) |
| target mean | \(\mu_{1,i}=1.0+0.25\,i\) |
| target covariance | diagonal, geometric eigenvalues, anisotropy 6.0 |
| geometry seed | 314159 (recorded; no randomness consumed) |
| dimensions | 2 and 8 |
| paths | linear (\(\alpha=1-t,\ \sigma=t\)) and variance-preserving (\(\alpha=\cos(\pi t/2),\ \sigma=\sin(\pi t/2)\)) |
| solvers | Euler (1 eval/step), Heun (2), RK4 (4) |
| NFE budgets | 8, 16, 32 |
| precision | float64 throughout; no silent casts |
| device | CPU only |
| endpoint rows | 2 dims × 2 paths × 3 solvers × 3 NFE = 36 |
| comparison blocks | 2 dims × 3 solvers × 3 NFE = 18 two-path blocks |
| baseline metric | `averaged_squared_lipschitz_proxy`, `n_time` 24, trapezoidal, spectral norm (identical definition to Phase 4) |
| runtime | expected under 30 seconds; hard stop 10 minutes |

The baseline metric depends only on the Jacobian \(A(t)\) and is therefore
unchanged by the means. That is a property of the registered baseline
definition, recorded here before execution, not a post-hoc observation.

## 3. Frozen definitions

**Endpoint error.** The numerical endpoint map is recovered from zero and
basis probes (existing `recover_affine_solver_map`), source moments
\((\mu_0, I)\) are propagated through the affine map, and the exact
Gaussian W2 to the target is computed from the propagated moments,
including the mean term.

**Equal-NFE accounting.** A row is valid only if the recorded actual NFE
equals the requested NFE. Steps per solver: NFE divided by evaluations per
step. All three solvers divide 8, 16, and 32.

**Inversion.** Within one comparison block (dimension, solver, NFE), let
\(\Delta M\) be the linear-minus-VP baseline metric difference and
\(\Delta W\) the linear-minus-VP Gaussian W2 difference. The block is an
inversion iff \(\Delta M\cdot\Delta W<0\) and both
\(\lvert\Delta M\rvert>10^{-9}\) and \(\lvert\Delta W\rvert>10^{-9}\).
Note \(\Delta M\) is shared across solvers and NFE within a dimension.

**Numerical tolerance and high-precision audit.** For every block flagged
as an inversion (and only after the float64 run is complete), both W2
values are recomputed by non-centered modal propagation in mpmath at 80
decimal digits. The audit passes for that block iff (a) the maximum
absolute float64-versus-80-digit W2 difference over the two rows is at
most \(2\times10^{-9}\), and (b) the float64 W2 margin exceeds 100 times
that maximum difference, and (c) the 80-digit margin has the same sign.
Only audited inversions may be reported. The exact-endpoint consistency
check requires the continuous flow at \(t=1\) to reach the target with W2
at most \(10^{-9}\).

**Success interpretation.** If at least one audited inversion occurs, the
paper may add one clearly labeled supporting sentence: the ranking
non-implication also occurs in a pre-registered non-centered commuting
Gaussian family with affine drift \(A(t)x+c(t)\), \(c\neq0\), that was
fixed before execution. Scope stays "tested systems"; no broader
population claim is licensed.

**Null-result interpretation.** If no audited inversion occurs, that is
recorded and reported as a bounded null result: the pre-registered
non-centered family showed no inversion at the tested budgets. The frozen
Phase 4 primary claim is unaffected (it quantifies over the Phase 4
tested systems), but the paper must state the null outcome and may not
silently omit the family.

Either outcome is publishable within the frozen claims; neither outcome
authorizes a second family, changed parameters, or a rerun with different
budgets.

## 4. Frozen artifact IDs

Run ID: `workshop_external_validation_2026-07-24-v1`.

| artifact ID | content |
| --- | --- |
| `workshop_external_validation_2026-07-24-v1:results` | 36 endpoint rows with metric, W2, moments, affine map, diagnostics |
| `workshop_external_validation_2026-07-24-v1:inversions` | 18 comparison blocks with inversion flags and margins |
| `workshop_external_validation_2026-07-24-v1:precision` | 80-digit audit rows for every flagged inversion |
| `workshop_external_validation_2026-07-24-v1:validation` | validation summary (row count, equal NFE, PSD, endpoint check, audit) |

Outputs are written under
`outputs/workshop_external_validation_2026-07-24-v1/` with the standard
manifest. The run refuses a dirty worktree, refuses to overwrite a
completed manifest, and must be release-ready.

## 5. Execution protocol

1. Commit this plan and the implementation before execution.
2. Require a clean worktree at run time.
3. Run the full test suite, Ruff, MyPy, and pre-commit before execution.
4. Execute once via the CLI mode `workshop_external_validation`.
5. Validate the manifest with `scripts/validate_artifacts.py`.
6. Run the high-precision audit for every flagged inversion (part of the
   run itself; the precision artifact must exist even if empty).
7. Record all null and positive results in `docs/SESSION_LOG.md` and the
   workshop paper draft.
8. Hard stop: if the run exceeds 10 minutes it is killed, the partial
   output is discarded as invalid, and the failure is recorded. A crash
   does not authorize changing the frozen family.
