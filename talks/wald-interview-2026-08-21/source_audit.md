# Source audit for the Wald interview talk

Date: 2026-08-13.

This file records the mathematical checks, artifact provenance, and
number confirmation used in `fewstep_wald_talk.tex`. It does not claim
that inaccessible sources were read.

## Git freeze

- Requested analysis freeze: `b149f35541db4da6bf8d2e79f0bb267c72d91b77`
- HEAD at talk construction: `e48c9390e62b38f206342e6aeb7f160122ccc79c`
- The freeze commit is an ancestor of HEAD. No checkout was performed.
- The scientific tables used below are the frozen 2026-07-24 artifacts,
  whose SHA-256 values still match the pins in `docs/PHASE4_RESULTS.md`.

Granola, SciSpace, Zotero, Drive, Figma, and Canva were not available.
The attached file `main (7).pdf` was not found. The manuscript source of
truth is `paper/gddl2026/main.tex`.

## Artifact decision

Plan step 1 was to reuse frozen `outputs/` trees if checksums match.
They were present locally (gitignored) and every pinned digest matched.
Regeneration was therefore skipped. Pushable copies live in
`talks/wald-interview-2026-08-21/artifacts/`.

This is not a byte-identical claim about git commit metadata inside
manifests. It is a claim that the scientific JSON tables are the frozen
files.

See `artifacts/NUMBER_CONFIRMATION.md` for the number table. No
manuscript number was contradicted.

## Objects and dimensions

- Endpoints $X_0,X_1\in\mathbb{R}^d$.
- Mean $m_t\in\mathbb{R}^d$, covariance $Q(t)\in\mathbb{S}_{++}^d$.
- Field $b(t,\cdot):\mathbb{R}^d\to\mathbb{R}^d$.
- Jacobian $A(t)\in\mathbb{R}^{d\times d}$, offset $c(t)\in\mathbb{R}^d$.
- $\nabla_x b(t,x)=A(t)$.

Checked against `docs/MATHEMATICAL_NOTES.md`,
`src/fewstep_regularities/fields/gaussian_affine.py`, and
`paper/gddl2026/main.tex`.

## Interpolant and field

$X_t=\alpha(t)X_0+\sigma(t)X_1$ with independent Gaussian endpoints gives
$m_t=\alpha\mu_0+\sigma\mu_1$ and $Q=\alpha^2\Sigma_0+\sigma^2\Sigma_1$.
The marginal velocity is the interpolant conditional mean
$b=Ax+c$ with $A=C_t Q^{-1}$ and
$C_t=\dot\alpha\alpha\Sigma_0+\dot\sigma\sigma\Sigma_1$.
Centered with $\Sigma_0=I$: $A=\frac12 Q'Q^{-1}$, $c=0$.

This is the stochastic-interpolant marginal ODE. It is not identified
with every use of "probability-flow ODE" in score-based diffusion.

Linear $(1-t,t)$ is independent coupling, not a global OT coupling.
VP is $(\cos(\pi t/2),\sin(\pi t/2))$, distinct from Lipman VP diffusion
path eq. 18.

## Regularity baseline

$\mathcal{R}[b]=\int_0^1 \|A(t)\|_2^2\,dt$, spectral operator 2-norm,
not Frobenius. Affine Jacobians are state-independent, so the Chen et al.
expectation drops. Implementation:
`AveragedSquaredLipschitzProxy` in
`src/fewstep_regularities/metrics/affine_gaussian.py`, trapezoidal
quadrature, `n_time=24` in the Phase 4 config. Metadata marks
`is_exact=False` because of quadrature, not because the Jacobian is
sampled. A recorded n=2048 diagnostic does not change orderings.

What $\mathcal{R}$ retains: unsigned time average of spatial Jacobian
magnitude. What it discards: stage locations, time derivatives, local
defect signs, cancellation, downstream transport.

## Modes, NFE, and $\mathrm{W}_2$

Commuting case $\Sigma_0=I$, $\Sigma_1=U\mathrm{diag}(\lambda_i)U^\top$:
$q_i=\alpha^2+\sigma^2\lambda_i$, $a_i=q_i'/(2q_i)$.
Centered exact factor $e_{i,n}=\sqrt{q_i(t_{n+1})/q_i(t_n)}$.
This square-root formula is not applied to the non-centered family.

Equal NFE, not equal steps: Euler $B$, Heun $B/2$, RK4 $B/4$, with exact
divisibility (`src/fewstep_regularities/solvers/common.py`).

Reported error is Gaussian $\mathrm{W}_2$ (square root). Code primary in
`gaussian_w2.py` is $\mathrm{W}_2$. Centered commuting identity uses
$\mathrm{W}_2^2=\sum_i(|r_i|-\sqrt{\lambda_i})^2$. The absolute value is
required. Talk slides distinguish the two.

## Transported defects and local expansions

The telescoping identity is exact, earlier-numerical / later-exact, with
no smallness assumption. Sign convention is exact minus method:
Euler $\frac12(a'+a^2)h^2+O(h^3)$;
Heun $(-\frac1{12}a''+\frac16 a^3)h^3+O(h^4)$.
Checked in `docs/P4_P1_PROOF_AUDIT.md` and
`src/fewstep_regularities/analysis/local_error.py`.
No memorized RK4 leading formula is asserted.

## Proposition 1

Grid-aware: $a_{1,N}$ depends on $N$. Four claims hold for every $L>0$
and integer $N\ge 1$. Proof verified in `docs/P4_P1_PROOF_AUDIT.md`.
The unit test
`test_euler_nonimplication_construction` checks one $(L,N)$ pair and a
weaker inequality. The talk follows the audited proof, not the test.

This is a logical non-implication, not the mechanism of every Gaussian
inversion, and not a new numerical-analysis phenomenon.

## What was not found to be inconsistent

No mathematical inconsistency requiring a corrected statement on the
slides was found. Two scope remarks are already in the talk:

1. $\mathcal{R}$ is a trapezoidal integral of a closed-form integrand,
   not a symbolic antiderivative.
2. Exponential / exact-linear integrators solve the affine laboratory
   exactly, so the ranking question is vacuous for those methods.

## Chen et al. version

Repository notes (`papers/notes/lipschitz_guided_2025.md`) record
arXiv:2509.01629 version 3, 16 May 2026. The talk bibliography uses that
version note. Page-level claims in the talk are limited to Def. 3.2
(averaged squared spectral Jacobian) and the existence of a transfer
formula, as extracted in those notes.

## 12-slide revision (same day)

Main-deck FM/CFM formulas were extracted from Lipman et al., arXiv
2210.02747 (ICLR 2023), via the HTML of the locked arXiv record:

- CNF ODE: Lipman eqs. (1)--(2), written as \(v_\theta(t,X_t)\).
- Continuity: Lipman eq. (26), with generating field \(u_t\).
- \(\mathcal{L}_{\mathrm{FM}}\): Lipman eq. (5).
- \(\mathcal{L}_{\mathrm{CFM}}\): Lipman eq. (9).
- Gradient identity: Lipman Theorem 2, under \(p_t(x)>0\).

The interpolant \(X_t=\alpha X_0+\sigma X_1\) and \(b_t(x)=\mathbb{E}[\dot X_t\mid X_t=x]\)
remain the manuscript / Albergo objects, not Lipman's one-sided residual
\(\sigma_t\). Gaussian field, \(\mathcal{R}\), telescope, Euler construction,
and all displayed numbers are unchanged from the confirmation table.
The title slide no longer states manuscript or venue status. The main
counter is `n/12` via `appendixnumberbeamer`.
