# Lipschitz-Guided Design of Interpolation Schedules in Generative Models

- paper_id: `lipschitz_guided_2025`
- authors: Yifan Chen, Eric Vanden-Eijnden, Jia Wei Xu
- year: 2025
- source_url: https://arxiv.org/abs/2509.01629
- local_filename: lipschitz_guided_2025.pdf
- access_date: 2026-07-23
- source_version: arXiv v3, 2026-05-16
- sha256: see papers/manifest.json

## Relevance

Baseline Lipschitz-guided schedule and averaged squared Lipschitzness proxy.

## Formulas or results needed

- Lipschitz-guided schedule definition
- averaged squared Lipschitzness proxy
- transfer formula between schedules

## Notation differences

- Uses SI-style `I_t = α_t z + β_t x_1` with reference linear schedule `α^†_t = 1-t`, `β^†_t = t`.
- Project protocol: `alpha ↔ α`, `sigma ↔ β`.
- `∥∇b_t∥_2` in Def 3.2 is the spectral (operator) 2-norm of the Jacobian.

## Assumptions to check

- smoothness of drift
- scalar schedules (matrix schedules deferred)
- for closed form (3.6): isotropic Gaussian variance ratio `M > 0`, `M ≠ 1`
- absolute continuity of Gaussians

## Project satisfies assumptions?

Phase 1 uses scalar schedules. Proposition 3.9 assumes that all target
covariance eigenvalues are at most one and selects the smallest eigenvalue.
The implemented anisotropic and low-rank families do not always meet this
assumption. The factory uses the largest covariance eigenvalue, or a condition
ratio when that value is numerically one, as an explicitly documented
heuristic. It is not claimed to implement the source-optimal anisotropic
schedule. Exact avg-Lip² evaluation still applies to each resulting affine
Gaussian field.

## Replication status

formulas-extracted-phase1

## Extracted equations

Source: local PDF pages 7-10.

Proposition 3.1 transfer formula (3.1), reference linear schedule `α^†=1-t`, `β^†=t`, with `t^† = 1 / (1 + α_t/β_t)`:

`b_t(x) = (α'_t / α_t) x + (β'_t - α'_t β_t / α_t) * ((1 - t^†) b^†_{t^†}(t^† x / β_t) + t^† x / β_t)`

Definition 3.2 avg-Lip² (3.4):

`A_2 = ∫_0^1 E[∥∇ b_t(I_t)∥_2^2] dt`

Example 3.3 1D Gaussian with `x_1 ~ N(0, M)`, `z ~ N(0,1)`:

`b_t(x) = (α α' + β β' M) / (α^2 + β^2 M) * x`

Optimized schedule under `α^2 + β^2 = 1` (eq. 3.6):

`α_t = sqrt((M - M t) / (M - 1))`, `β_t = sqrt((M t - 1) / (M - 1))`

Equation (3.6) in arXiv v3 is the same variance-log schedule used by the
implementation. The PDF text extraction can lose the superscript in `M^t`.
It follows from
`log Cov(I_t) = (1-t) log Cov(I_0) + t log Cov(I_1)` with
`α^2 + β^2 = 1`, so `α_t^2 + β_t^2 M = M^t` and

`β_t^2 = (M^t - 1) / (M - 1)`, `α_t^2 = 1 - β_t^2` when `M ≠ 1`.

Do not call a sampled Jacobian norm a global Lipschitz constant.
