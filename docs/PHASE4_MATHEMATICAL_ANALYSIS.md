# Phase 4 mathematical analysis

Status: Core derivations checked. P4-P1 was independently reviewed and
verified on 2026-07-24; see
[the proof audit](P4_P1_PROOF_AUDIT.md).

Scope: Centered anisotropic and low-rank Gaussian targets in dimensions 2 and
8, linear and variance-preserving paths, and fixed-step Euler, Heun, and RK4.
No mixture result is used.

Artifact IDs used:

- `phase4_gaussian_reproduction_2026-07-24-v1:results`
- `phase4_gaussian_reproduction_2026-07-24-v1:validation`
- `phase4_precision_2026-07-24-v1:validation`
- `phase4_decomposition_2026-07-24-v1:table`
- `phase4_diagnostics_2026-07-24-v1:table`

Run 1 is registered reproduction evidence. The local error quantities and
decompositions are post-hoc. Phase 3 dirty outputs are comparison inputs only.

## Assumptions and notation

Let \(X_0\sim N(0,I_d)\) and \(X_1\sim N(0,\Sigma_1)\) be independent, where
\(I_d\) is the \(d\) dimensional identity and \(\Sigma_1\) is symmetric
positive definite. Let

\[
X_t=\alpha(t)X_0+\sigma(t)X_1,\qquad 0\leq t\leq1,
\]

where \(\alpha,\sigma\) are three times continuously differentiable and
\(Q(t)=\alpha(t)^2I_d+\sigma(t)^2\Sigma_1\) is positive definite. A prime
denotes a time derivative. All displayed formulas use exact real arithmetic.
The implementation evaluates them in float64 unless stated otherwise.

The linear path has \(\alpha(t)=1-t\) and \(\sigma(t)=t\). The
variance-preserving path has
\(\alpha(t)=\cos(\pi t/2)\) and \(\sigma(t)=\sin(\pi t/2)\).

## Gaussian affine field

Status: Original derivation, symbolically checked, numerically checked.

The conditional velocity is

\[
b(t,x)=E[\dot X_t\mid X_t=x]=A(t)x,
\]

with

\[
A(t)=\frac12Q'(t)Q(t)^{-1},\qquad c(t)=0.
\]

This follows from the standard Gaussian conditional expectation identity
\(E[\dot X_t\mid X_t=x]=\operatorname{Cov}(\dot X_t,X_t)Q(t)^{-1}x\)
and
\(\operatorname{Cov}(\dot X_t,X_t)=\alpha'\alpha I_d+
\sigma'\sigma\Sigma_1=Q'/2\).

The matrices \(Q(t)\), \(Q'(t)\), \(A(t)\), and \(\Sigma_1\) commute because
each is a scalar function of \(\Sigma_1\). If \(\lambda_i\) is a target
covariance eigenvalue, define

\[
q_i(t)=\alpha(t)^2+\lambda_i\sigma(t)^2,\qquad
a_i(t)=\frac{q_i'(t)}{2q_i(t)}.
\]

For the linear and variance-preserving paths, respectively,

\[
a_i^{\mathrm{lin}}(t)=
\frac{(1+\lambda_i)t-1}{(1-t)^2+\lambda_i t^2},
\]

\[
a_i^{\mathrm{vp}}(t)=
\frac{\pi(\lambda_i-1)\sin(\pi t)}
{4\{\cos^2(\pi t/2)+\lambda_i\sin^2(\pi t/2)\}}.
\]

These are exact quantities, not sampled Jacobian estimates.

## Exact flow and moment dynamics

Status: Standard identities plus original specialization, numerically checked.

Let \(\Phi(t,s)\) solve
\(\partial_t\Phi(t,s)=A(t)\Phi(t,s)\) with \(\Phi(s,s)=I_d\).
Commutativity gives

\[
\Phi(t,s)=Q(t)^{1/2}Q(s)^{-1/2}.
\]

Thus \(\Phi(1,0)=\Sigma_1^{1/2}\). For a general affine field
\(b(t,x)=A(t)x+c(t)\),

\[
m'(t)=A(t)m(t)+c(t),\qquad
C'(t)=A(t)C(t)+C(t)A(t)^\mathsf{T},
\]

where \(m(t)\) and \(C(t)\) are the mean and covariance. In the tested
centered cases, \(m(t)=0\) and \(C(t)=Q(t)\).

## Discrete affine maps

Status: Original algebra from the solver definitions, symbolically checked.

Let \(t_n=nh\), \(h=1/S\), \(A_n=A(t_n)\), and \(c_n=c(t_n)\).
Each solver step is \(x_{n+1}=R_nx_n+d_n\). The moment update is

\[
m_{n+1}=R_nm_n+d_n,\qquad
C_{n+1}=R_nC_nR_n^\mathsf{T}.
\]

Euler uses

\[
R_n=I_d+hA_n,\qquad d_n=hc_n.
\]

Heun uses

\[
R_n=I_d+\frac h2
\{A_n+A_{n+1}+hA_{n+1}A_n\},
\]

\[
d_n=\frac h2\{c_n+c_{n+1}+hA_{n+1}c_n\}.
\]

For RK4, define affine stages recursively:

\[
k_1(x)=A_nx+c_n,
\]
\[
k_2(x)=A(t_n+h/2)\{x+hk_1(x)/2\}+c(t_n+h/2),
\]
\[
k_3(x)=A(t_n+h/2)\{x+hk_2(x)/2\}+c(t_n+h/2),
\]
\[
k_4(x)=A_{n+1}\{x+hk_3(x)\}+c_{n+1}.
\]

Then \(x_{n+1}=x+h(k_1+2k_2+2k_3+k_4)/6\). Applying this expression to the
identity map and zero vector constructs \(R_n\) and \(d_n\) without an
expanded formula. Euler, Heun, and RK4 use one, two, and four field
evaluations per step.

## Gaussian Wasserstein endpoint error

Status: Source verified identity and original commuting specialization.

For Gaussian means \(m_0,m_1\) and covariances \(C_0,C_1\),

\[
W_2^2=\lVert m_0-m_1\rVert_2^2+
\operatorname{tr}\{C_0+C_1-
2(C_1^{1/2}C_0C_1^{1/2})^{1/2}\}.
\]

This is the Gaussian formula treated by
[Gelbrich, 1990](https://doi.org/10.1002/mana.19901470121). In the tested
commuting centered setting, if \(r_i\) is the numerical endpoint factor,

\[
W_2^2=\sum_i(|r_i|-\sqrt{\lambda_i})^2.
\]

The endpoint W2 in this analysis is exact from the propagated numerical
moments up to floating-point matrix operations. It is not an empirical
estimator.

## Material derivative and local error

Status: Original derivation from Taylor expansion, symbolically checked.

For \(b(t,x)=A(t)x+c(t)\), its derivative along a solution is

\[
\partial_tb+Jb=(A'+A^2)x+c'+Ac,
\]

because \(J=A\). For a scalar eigenmode \(x'=a(t)x\),

\[
x''=(a'+a^2)x,\qquad
x'''=(a''+3aa'+a^3)x.
\]

The exact one-step factor expanded at \(t_n\) is

\[
1+ha+\frac{h^2}{2}(a'+a^2)
+\frac{h^3}{6}(a''+3aa'+a^3)+O(h^4).
\]

Therefore the exact-minus-method leading local coefficient for Euler is

\[
\frac12(a'+a^2).
\]

Direct expansion of explicit trapezoidal Heun gives

\[
-\frac1{12}a''+\frac16a^3.
\]

The \(aa'\) terms cancel. RK4 is evaluated from its exact scalar stage
polynomial and compared with the exact factor
\(\sqrt{q(t_{n+1})/q(t_n)}\). No memorized non-autonomous RK4 defect formula
is asserted.

The final factor difference has the exact telescoping decomposition

\[
\prod_{j=0}^{S-1}r_j-\prod_{j=0}^{S-1}e_j
=\sum_{i=0}^{S-1}(r_i-e_i)
\left(\prod_{j<i}r_j\right)\left(\prod_{j>i}e_j\right),
\]

where \(r_i\) and \(e_i\) are the numerical and exact one-step factors.
This identity explains how local defects are transported to the endpoint.
It also shows why an integral of \(\lVert A(t)\rVert^2\) alone does not
determine fixed-grid error: derivatives, solver stages, signs, cancellation,
and transport weights all enter.

## Minimal proposition P4-P1

Status: Proof verified after independent adversarial review. Explicit
construction, symbolically checked and numerically checked. See
[the proof audit](P4_P1_PROOF_AUDIT.md) for the quantified statement, edge
cases, objections, and scope.

Fix \(L>0\) and integer \(N\geq1\). Let \(h=1/N\), \(t_n=n/N\), and consider
the scalar ODE \(x'=a(t)x\), \(x(0)=1\). Define

\[
a_0(t)=L,
\]

\[
\epsilon_N=N\{\exp(L/N)-1\}-L,\qquad
a_1(t)=L+\epsilon_N\cos(2\pi Nt).
\]

Both fields are smooth and induce the same exact endpoint
\(x(1)=\exp(L)\), since both time integrals equal \(L\). Their averaged
squared Jacobians satisfy

\[
\int_0^1a_1(t)^2dt=L^2+\epsilon_N^2/2>L^2
=\int_0^1a_0(t)^2dt.
\]

At every left Euler node, \(a_1(t_n)=L+\epsilon_N\), so its numerical
endpoint is

\[
\{1+(L+\epsilon_N)/N\}^N=\exp(L).
\]

Its Euler endpoint error is zero. Constant \(a_0\) gives
\((1+L/N)^N<\exp(L)\), hence positive endpoint error. Thus, under these
explicit assumptions, larger averaged squared Jacobian does not imply larger
fixed-step Euler endpoint error.

The construction is grid-aware and therefore artificial relative to the
Gaussian paths. It establishes non-implication, not novelty and not an
explanation of every observed inversion. The singular case \(L=0\) is
excluded because the strict ordering vanishes. Positivity of \(\epsilon_N\)
follows from \(\exp(z)>1+z\) for \(z>0\). All Euler factors are positive.
The numerical test covers representative \(L\) and \(N\), but exhaustive
counterexample search is not a formal proof review.

## Numerical checks and unresolved questions

Automatic differentiation and centered finite differences agree for the
material derivative formulas. Constant, diagonal, and commuting systems are
covered by CPU tests. Run 2 provided an 80 digit scalar reference. Runs 3 and
4 checked the W2 reconstruction and transported defects.

Unresolved questions include whether a concise RK4 leading expression adds
insight beyond the exact stage defect, whether the dominant eigenmodes admit a
uniform asymptotic sign argument, and whether P4-P1 has a less grid-aware
construction. See [unresolved questions](UNRESOLVED_QUESTIONS.md).
