# Computational Optimal Transport

- paper_id: `peyre2019computational_ot`
- authors: Gabriel Peyre, Marco Cuturi
- year: 2019
- source_url: https://arxiv.org/abs/1803.00567
- local_filename: peyre2019computational_ot.pdf
- access_date: 2026-07-23
- sha256: see papers/manifest.json

## Relevance

Gaussian W2 closed form and Gaussian OT map / displacement interpolation.

## Formulas or results needed

- Gaussian W2 closed form
- entropic OT definition
- Sinkhorn iterations
- discrete Kantorovich LP for exact discrete OT

## Notation differences

- Peyré uses `α`, `β` for measures (not SI schedule coefficients).
- `m_α`, `Σ_α` are mean and covariance of the source Gaussian.
- Entropic cost is `L^ε_C`, not exact `L_C`. Project never labels entropic OT as exact W2.

## Assumptions to check

- positive definite covariances for the Bures formula as stated
- absolute continuity of Gaussians
- Brenier potential convexity for optimality of the affine map
- for entropic OT: discrete histograms on finite supports; `ε > 0`

## Project satisfies assumptions?

Yes when both laws are non-degenerate Gaussians. Singular covariances require
pseudoinverse handling and are flagged in code. Entropic OT is used only as
a regularized estimator with reported `epsilon`.

## Replication status

formulas-extracted-phase2

## Extracted equations

### Gaussian W2 / OT map (Phase 1)

Source: local PDF pages 37-38 (section 2.6).

Gaussian OT map (2.40):

`T(x) = m_β + A (x - m_α)`

with

`A = Σ_α^{-1/2} (Σ_α^{1/2} Σ_β Σ_α^{1/2})^{1/2} Σ_α^{-1/2} = A^T`

Wasserstein-2 between Gaussians (2.41)-(2.42):

`W_2^2(α, β) = ∥m_α - m_β∥^2 + B(Σ_α, Σ_β)^2`

`B(Σ_α, Σ_β)^2 = tr(Σ_α + Σ_β - 2 (Σ_α^{1/2} Σ_β Σ_α^{1/2})^{1/2})`

Displacement interpolation uses McCann interpolant `(1-t) Id + t T` between Gaussians.

### Entropic OT (Phase 2)

Source: local PDF chapter 4 (printed pages 57-62; section 4.1).

Discrete entropy (4.1):

`H(P) = - ∑_{i,j} P_{i,j} (log P_{i,j} - 1)`

Entropic OT problem (4.2):

`L^ε_C(a, b) = min_{P ∈ U(a,b)} ⟨P, C⟩ - ε H(P)`

As `ε → 0`, `L^ε_C → L_C` (Proposition 4.1). As `ε → ∞`, the coupling tends to
the independent product `a ⊗ b`. Therefore entropic OT is a biased estimator of
exact W2 for any fixed `ε > 0`.

Gibbs kernel: `K_{i,j} = exp(-C_{i,j}/ε)`.

Sinkhorn uses alternating KL projections / scaling iterations (section 4.2).
Log-domain / soft-min dual updates appear in (4.35)-(4.36).

### Discrete OT (Phase 2)

Kantorovich linear program over couplings in `U(a,b)` with cost `⟨P, C⟩`
(chapter 2 / 3). For equal-weight empirical samples with squared Euclidean cost,
`W_2^2 = ∑_{i,j} P^*_{i,j} ∥x_i - y_j∥^2` at an optimal coupling `P^*`,
where `P^*` has row and column masses `1/n` for two size-`n` clouds.

The Phase 2 entropic evaluator reports three distinct quantities: Peyré's
regularized objective `L_C^ε`, its transport component `<P,C>`, and
`sqrt(<P,C>)` as the primary diagnostic. It checks both marginal residuals
against a reported tolerance and refuses to return a non-converged plan.
