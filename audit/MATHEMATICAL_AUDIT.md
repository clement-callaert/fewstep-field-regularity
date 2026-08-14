# Mathematical audit

Audit date: 2026-08-13.
Method: first-principles derivation, then comparison with `docs/PHASE4_MATHEMATICAL_ANALYSIS.md`, `docs/P4_P1_PROOF_AUDIT.md`, and the implementation. Symbolic algebra (sympy) and 80-digit mpmath were used as secondary checks, not as proofs.

Convention: a prime denotes a derivative in time. State space is `R^d`. Time interval is `[0,1]`.

## 1. Interpolant

Input: independent random vectors `X_0 ~ N(mu_0, Sigma_0)`, `X_1 ~ N(mu_1, Sigma_1)` in `R^d`, and scalar C^1 schedules `alpha, sigma: [0,1] -> R` with `alpha(0)=sigma(1)=1` and `alpha(1)=sigma(0)=0` in the implemented linear and trigonometric VP paths.

Definition: `X_t = alpha(t) X_0 + sigma(t) X_1`.

Mean: `m_t = alpha mu_0 + sigma mu_1`.

Covariance: because of independence,
`Q(t) := Cov(X_t) = alpha^2 Sigma_0 + sigma^2 Sigma_1`.

Domain: t in [0,1]. Codomain: Gaussian laws on `R^d`. Require `Q(t)` symmetric positive definite for every t used by the solver, including endpoints. For `Sigma_0=I` and `lambda_min(Sigma_1)>0`, both implemented paths have `q_i(t)=alpha^2+lambda_i sigma^2 > 0` on [0,1].

Conclusion: valid.

## 2. Affine marginal velocity

Assume the interpolant is differentiable in t pathwise. Then `dot X_t = alpha' X_0 + sigma' X_1`.

For jointly Gaussian `(dot X_t, X_t)`,
`E[dot X_t | X_t=x] = m'_t + Cov(dot X_t, X_t) Q(t)^{-1} (x - m_t)`.

`Cov(dot X_t, X_t) = alpha' alpha Sigma_0 + sigma' sigma Sigma_1 =: C_t`.

Hence `b(t,x)= A(t) x + c(t)` with
`A(t)= C_t Q(t)^{-1}`, `c(t)= m'_t - A(t) m_t`.

This uses invertibility of `Q(t)` and Gaussian conditionals. It is the standard formula in Lipschitz-guided Example 3.3, extended to non-centered non-isotropic endpoints. Implementation: `GaussianAffineField`.

Centered specialization `mu_0=mu_1=0`, `Sigma_0=I`: `m_t=0`, `m'_t=0`, `Q= alpha^2 I + sigma^2 Sigma_1`, `Q'= 2 alpha alpha' I + 2 sigma sigma' Sigma_1 = 2 C_t`, so `A=(1/2) Q' Q^{-1}` and `c=0`.

Conclusion: valid under Q PD and independent Gaussian endpoints.

## 3. Simultaneous diagonalization

If `Sigma_0=I` and `Sigma_1=U diag(lambda) U^T` with `U` orthogonal, then `Q(t)`, `Q'(t)`, and `A(t)` are all polynomials in `Sigma_1`, hence they commute and share the eigenbasis U.

In eigen-coordinates, mode i obeys `x_i' = a_i(t) x_i + c_i(t)` with
`q_i= alpha^2 + lambda_i sigma^2`, `a_i= q_i'/(2 q_i)` when `Sigma_0=I`.
If also `mu_0=mu_1=0`, then `c_i=0`.

The non-centered frozen family keeps `Sigma_0=I` and diagonal `Sigma_1`, so it remains modal, with nonzero `c_i`.

This commuting hypothesis is essential. It is not claimed for general noncommuting covariance flows.

Conclusion: valid under the commuting hypothesis. Not valid without it.

## 4. Exact scalar transition

For `x'=a(t)x` with `a=q'/(2q)` and `q>0`,
`d/dt log q = q'/q = 2a`, so `int_{t_n}^{t_{n+1}} a = (1/2) log(q(t_{n+1})/q(t_n))`.
Thus the exact transition factor is `exp(int a)= sqrt(q(t_{n+1})/q(t_n))`.

For centered modes with `q(0)=1` and `q(1)=lambda_i`, the exact endpoint factor is `sqrt(lambda_i)`.

Conclusion: valid.

## 5. Numerical one-step factors

Implemented on `x'=a(t)x`, x scalar:

- Euler: `r=1+h a(t_n)`. One field evaluation.
- Heun: predictor `1+h a(t_n)`; `r=1+(h/2)(a(t_n)+a(t_{n+1})(1+h a(t_n)))`. Two evaluations.
- Classical RK4: four stage samples at `t_n`, `t_n+h/2` (twice), `t_{n+1}`. Four evaluations.

These match `EulerSolver`, `HeunSolver`, `RK4Solver` and `scalar_step_factor`.

Equal-NFE: `n_steps = requested_nfe // evals_per_step` with remainder zero. Endpoint time is t=1 on an inclusive uniform grid. NFE counts `evaluate` calls, not Jacobian calls.

Conclusion: valid for these three fixed-step methods. Not a statement about adaptive or exponential integrators.

## 6. Gaussian W2

For Gaussians, Gelbrich (1990) and Peyre-Cuturi (2.41)-(2.42) give
`W_2^2 = ||m_a-m_b||^2 + tr(C_a+C_b-2 (C_a^{1/2} C_b C_a^{1/2})^{1/2})`.

Implementation uses the Bures form with PSD square roots (`matrix_sqrt_psd`) and clamps the square root of W_2^2 at 0.

Centered commuting specialization: numerical endpoint covariance is diagonal with entries `r_i^2` in the eigenbasis (from `C = R C_0 R^T` with `C_0=I`). Target eigenvalues `lambda_i`. Mean error 0. Then
`W_2^2 = sum_i (|r_i|-sqrt(lambda_i))^2`,
because the PSD square root of `r_i^2` is `|r_i|`.

Conclusion: valid. The absolute value is required.

## 7. Telescoping identity

Let `r_0,...,r_{S-1}` and `e_0,...,e_{S-1}` be nonzero scalars. Then
`prod r - prod e = sum_{n=0}^{S-1} (r_n-e_n) (prod_{j<n} r_j) (prod_{j>n} e_j)`.

Proof: the n-th summand replaces the n-th exact factor by the numerical one, after numerical prefixes and before exact suffixes. Adjacent terms cancel (telescoping). No smoothness or smallness.

Code: `propagate_scalar_mode` uses this indexing. Tests check the identity to `2e-15` on representative modes.

If a numerical factor is negative, log-defect bookkeeping uses `log|r|` and is a different identity. The factor identity uses signed `r_n-e_n`.

Conclusion: valid.

## 8. Local truncation expansions

Exact factor on `[t,t+h]`, x(t)=1:
`1 + h a + (h^2/2)(a'+a^2) + (h^3/6)(a''+3 a a'+a^3) + O(h^4)`,
using `x''=(a'+a^2)x` and `x'''=(a''+3aa'+a^3)x`, assuming a is C^3.

Euler factor `1+h a`. Exact minus Euler: `(h^2/2)(a'+a^2)+O(h^3)`.

Heun: substitute `a(t+h)=a+h a'+(h^2/2)a''+(h^3/6)a'''+O(h^4)` into
`r=1+(h/2)(a + a(t+h)(1+h a))`.
Sympy expansion of this implemented factor yields
`exact - Heun = h^3 (-a''/12 + a^3/6) + O(h^4)`.
The claimed coefficient is therefore correct for explicit trapezoidal Heun. The `aa'` terms cancel. Assumptions: a is C^3; the method is the implemented two-stage Heun, not a different RK2.

RK4: no closed leading coefficient is asserted. Code estimates `(exact-numerical)/h^5` numerically.

Conclusion: Euler and Heun coefficients valid. RK4 closed form not claimed.

## 9. Proposition P4-P1

Statement. For every real L>0 and every integer N>=1, let h=1/N and let forward Euler use left endpoints t_n=n/N on [0,1]. Define
`epsilon_N = N(e^{L/N}-1)-L`,
`a_0(t)=L`,
`a_{1,N}(t)=L+epsilon_N cos(2 pi N t)`,
and `f_k(t,x)=a_k(t) x`. For x(0)=1:

(i) both exact endpoints equal e^L;
(ii) int_0^1 a_{1,N}^2 = L^2 + epsilon_N^2/2 > int a_0^2;
(iii) Euler is exact for a_{1,N};
(iv) Euler has strictly positive endpoint error for a_0.

Hence larger averaged squared Jacobian does not imply larger fixed-grid Euler endpoint error.

Proof (checked).

(i) int_0^1 cos(2 pi N t) dt = sin(2 pi N)/(2 pi N)=0 for integer N>=1. Both integrals of a equal L. Solutions of x'=a x, x(0)=1, are exp(int a).

(ii) Orthogonality of 1 and cos(2 pi N t) on [0,1], and int cos^2 = 1/2. Positivity of epsilon_N: z=L/N>0 and e^z>1+z imply N(e^{L/N}-1)>L.

(iii) cos(2 pi N t_n)=cos(2 pi n)=1, so each Euler factor is `1+h(L+epsilon_N)=e^{L/N}`. Product e^L. All factors positive.

(iv) log(1+z)<z for z=L/N>0, so (1+L/N)^N < e^L.

Edge cases. N=1 holds. L=0 is excluded (ordering not strict). As N to infinity, epsilon_N ~ L^2/(2N) -> 0: the oscillatory field depends on N.

Quantifiers. The field a_{1,N} is chosen after the grid. Shifted nodes, right Euler, Heun, and RK4 sample other phases and are not covered. This is a logical non-implication for left-endpoint Euler, not a mechanism for the Gaussian inversions, and not a new numerical-analysis phenomenon.

80-digit check: for representative (L,N) including (1,8), (1,1), (pi,17), the oscillatory Euler product equals e^L to working precision. The repository test now asserts that identity, not only a relative-error inequality.

Conclusion: valid.

## 10. What the proposition does not prove

It does not identify the Gaussian inversions. It does not apply to Heun or RK4. It does not survive grid refinement with a fixed oscillatory field. It does not bound W_2. Exponential integrators that integrate `x'=a(t)x` exactly make both Euler errors in (iii)-(iv) irrelevant.

## External theorems

- Gaussian conditionals: standard. Assumptions (joint Gaussianity) hold for the interpolant.
- Gelbrich / Bures W2: applies to Gaussian pairs; covariances are SPD in the tested grid (min propagated eigenvalue 0.027...).
- Hairer local-to-global order: used only as background, not as a ranking theorem.
- Lipschitz-guided Def 3.2: `A_2=int E[||nabla b_t(I_t)||_2^2] dt`. For state-independent A(t), this is int ||A(t)||_2^2 dt. Implementation is trapezoidal, n_time=24.

No S4 mathematical failure.
