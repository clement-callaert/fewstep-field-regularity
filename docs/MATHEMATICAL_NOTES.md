# Mathematical notes

This file indexes derivations used by the project.
Exact velocity fields are allowed only after a derivation here is checked
against a retrieved source or labeled as an original derivation.

## Path taxonomy

Keep these classes separate:

1. Independent coupling paths
2. Deterministic transport couplings
3. Gaussian optimal transport paths
4. Schedule reparameterizations

Do not call a path optimal transport unless the coupling and displacement
interpolation are mathematically valid.

## Notation conversion

Project protocol for scalar SI-style bridges:

- `alpha(t)` maps to SI / Lipschitz `α_t` (coefficient of source or noise)
- `sigma(t)` maps to SI / Lipschitz `β_t` (coefficient of target)

Endpoint conventions for one-sided bridges with `z ~ N(0, I)`, `x_1 ~ ρ_1`:

- `I_t = alpha(t) z + sigma(t) x_1`
- `alpha(0) = 1`, `alpha(1) = 0`, `sigma(0) = 0`, `sigma(1) = 1`

Two-sided independent linear bridge (Liu eq. 1, Albergo Fig. 2):

- `x_t = alpha(t) x_0 + sigma(t) x_1` with `alpha(t)=1-t`, `sigma(t)=t`

Lipman Flow Matching conversion:

- Lipman conditional path uses `μ_t(x_1)` and residual std `σ_t(x_1)`
- Lipman `σ_t` is **not** SI `β_t`
- Lipman OT conditional (eq. 20): `μ_t = t x_1`, residual `σ_t = 1-(1-σ_min)t`
- That residual std corresponds to a noise coefficient on `x_0`, not to SI `β_t`

Trigonometric variance-preserving schedule (project):

- `alpha(t) = cos(π t / 2)`, `sigma(t) = sin(π t / 2)`
- Satisfies `alpha(t)^2 + sigma(t)^2 = 1`
- Distinct from Lipman VP diffusion path (eq. 18)

Noise model: multiplicative coefficients on Gaussian endpoints; no extra latent
`γ(t) z` in Phase 1 deterministic ODE experiments (Albergo `γ=0`).

## Equal-NFE accounting

Resolved for Phase 1:

- Euler: 1 field evaluation per step
- Heun: 2 field evaluations per step
- RK4: 4 field evaluations per step
- `n_steps = requested_nfe // evals_per_step`
- Require `requested_nfe % evals_per_step == 0`; otherwise raise
- Bookkeeping (time grids, copies) does not count as NFE

## Endpoint handling

- Linear: well-defined on `[0, 1]`
- Trig VP: well-defined on `[0, 1]`
- Lipschitz-guided log-covariance schedule: require `M > 0`, `M ≠ 1`;
  clamp numerical noise near endpoints
- Gaussian OT displacement: well-defined for non-degenerate Gaussian pairs
- Lipman residual OT with `σ_min > 0`: avoids division by zero at `t=1`

## Exact field checklist

For each exact field:

1. Write the derivation in this file or a linked note.
2. Cite the source or label it as original.
3. Add a symbolic or automatic differentiation check.
4. Add a continuity equation consistency test when practical.
5. Add a Monte Carlo moment evolution test.

## Derivation: Gaussian affine marginal velocity

Field ID: `gaussian_affine_marginal`

Path class: independent scalar schedule or Gaussian OT schedule on Gaussian
endpoints.

Setup:

- `z ~ N(m_0, Σ_0)`, `x_1 ~ N(m_1, Σ_1)`, independent
- `I_t = alpha(t) z + sigma(t) x_1`
- Then `I_t ~ N(m_t, Σ_t)` with
  - `m_t = alpha(t) m_0 + sigma(t) m_1`
  - `Σ_t = alpha(t)^2 Σ_0 + sigma(t)^2 Σ_1`

Velocity of the interpolant before conditioning:

- `İ_t = alpha'(t) z + sigma'(t) x_1`

For jointly Gaussian `(I_t, İ_t)`,

- `b_t(x) = E[İ_t | I_t = x] = ṁ_t + C_t Σ_t^{-1} (x - m_t)`

where

- `ṁ_t = alpha' m_0 + sigma' m_1`
- `C_t = Cov(İ_t, I_t) = alpha' alpha Σ_0 + sigma' sigma Σ_1`

Jacobian (state-independent):

- `J_t = C_t Σ_t^{-1}`

Source: Lipschitz-guided Example 3.3 (isotropic) generalized to matrix
covariances; original derivation steps are the joint-Gaussian conditional mean.
Status: source verified (isotropic scalar case) + numerically checked (matrix).

Note path: `papers/notes/lipschitz_guided_2025.md`

## Derivation: Gaussian OT displacement field

Field ID: `gaussian_ot_displacement`

For Gaussians `ρ_0 = N(m_0, Σ_0)`, `ρ_1 = N(m_1, Σ_1)`, Peyré (2.40) gives
the OT map `T(x) = m_1 + A (x - m_0)` with

`A = Σ_0^{-1/2} (Σ_0^{1/2} Σ_1 Σ_0^{1/2})^{1/2} Σ_0^{-1/2}`.

McCann displacement:

`X_t = (1-t) X_0 + t T(X_0)`

Marginal law remains Gaussian. The constant-speed velocity along rays is
`T(X_0) - X_0`, and the marginal field in Eulerian coordinates is the
affine field matching the Gaussian moment ODEs for this coupling.

Status: source verified (map and W2) + numerically checked (pushforward moments).

Note path: `papers/notes/peyre2019computational_ot.md`

## Derivation: Lipman conditional Gaussian VF

Field ID: `lipman_conditional_gaussian`

Theorem 3 / eq. (15):

`u_t(x | x_1) = (σ'_t / σ_t) (x - μ_t) + μ'_t`

Used for conditional path tests, not as the Phase 1 marginal ODE field unless
explicitly configured.

Status: source verified.

Note path: `papers/notes/lipman2023flow_matching.md`

## Derivation index

| field ID | path | source/target | status | note path |
| --- | --- | --- | --- | --- |
| gaussian_affine_marginal | scalar SI schedules | Gaussian / Gaussian | source verified + numerically checked | papers/notes/lipschitz_guided_2025.md |
| gaussian_ot_displacement | gaussian OT | Gaussian / Gaussian | source verified + numerically checked | papers/notes/peyre2019computational_ot.md |
| lipman_conditional_gaussian | Lipman conditional | noise / point mass Gaussian | source verified | papers/notes/lipman2023flow_matching.md |
| mixture_affine_marginal | scalar SI schedules | Gaussian / GMM | original derivation + numerically checked | docs/MATHEMATICAL_NOTES.md |

## Gaussian W2

Peyré (2.41)-(2.42):

`W_2^2 = ∥m_0 - m_1∥^2 + tr(Σ_0 + Σ_1 - 2 (Σ_0^{1/2} Σ_1 Σ_0^{1/2})^{1/2})`

## Gaussian mixture density and score

For weights `π_k > 0` with `∑_k π_k = 1`, means `μ_k`, covariances `Σ_k ≻ 0`:

`p(x) = ∑_k π_k N(x; μ_k, Σ_k)`

`log p(x) = logsumexp_k (log π_k + log N(x; μ_k, Σ_k))`

Responsibilities:

`r_k(x) = softmax_k (log π_k + log N(x; μ_k, Σ_k))`

Score (stable form):

`∇ log p(x) = ∑_k r_k(x) (-Σ_k^{-1} (x - μ_k))`

Status: standard GMM identity; numerically checked via AD.

## Derivation: independent-coupling mixture marginal field

Field ID: `mixture_affine_marginal`

Path class: independent scalar schedule only (linear, trig VP, Lipschitz-guided).

Do not use Gaussian OT for non-Gaussian mixture targets.

Setup:

- `z ~ N(0, I)`, `x_1 ~ ∑_k π_k N(μ_k, Σ_k)`, independent
- `I_t = alpha(t) z + sigma(t) x_1`

Conditional on component `k` of `x_1`, the law of `I_t` is Gaussian with

- `μ_{k,t} = sigma(t) μ_k`
- `Σ_{k,t} = alpha(t)^2 I + sigma(t)^2 Σ_k`

so the marginal is the same mixture weights with these component parameters.

Conditional velocity given `(z, x_1)`:

`İ_t = alpha'(t) z + sigma'(t) x_1`

Given component `k` and `I_t = x`, the joint Gaussian conditional mean for the
component-restricted bridge yields the same affine formula as Phase 1 with
endpoints `N(0,I)` and `N(μ_k, Σ_k)`:

`b_{k,t}(x) = ṁ_{k,t} + C_{k,t} Σ_{k,t}^{-1} (x - μ_{k,t})`

where

- `ṁ_{k,t} = sigma'(t) μ_k`
- `C_{k,t} = alpha' alpha I + sigma' sigma Σ_k`

Marginal velocity (original derivation; SI conditional expectation):

`b_t(x) = ∑_k r_{k,t}(x) b_{k,t}(x)`

with responsibilities `r_{k,t}` of the time-`t` GMM.

Jacobian is state-dependent. Regularity metrics for this field use Monte Carlo
sampling from the time-`t` marginal GMM and are marked non-exact.

Status: original derivation + numerically checked (AD Jacobian, moment ODE).

Nearest sources: Albergo / Lipman conditional velocity identities; Phase 1
Gaussian affine field as the per-component building block.

## Empirical Wasserstein estimators (Phase 2)

- Exact empirical 1-D W2 for equal-size, equal-weight samples: sort projections
  and average squared differences of order statistics. For unequal sample
  sizes, integrate the two empirical quantile step functions over their combined
  CDF breakpoints.
- Sliced W2: Bonneel (30)-(31); Monte Carlo average over directions on `S^{d-1}`.
- Entropic OT: Peyré (4.2); report `ε`, `L_C^ε`, `<P,C>`, marginal residuals,
  iterations, and convergence. The primary diagnostic is `sqrt(<P,C>)`, not
  `L_C^ε` and not exact W2.
- Discrete OT: Kantorovich LP on small equal-weight clouds with cost
  `∥x_i - y_j∥^2`; exactness is scoped to the finite empirical measures.

## Proof workflow

Proposition notes live in `papers/notes/propositions/`.
Allowed proof statuses: `sketch`, `partially verified`, `numerically checked`,
`source verified`, `needs expert review`.
Never use `proved` unless the user explicitly approves after manual review.
