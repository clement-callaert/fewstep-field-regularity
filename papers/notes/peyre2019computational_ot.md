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
- entropic OT definition (Phase 2)

## Notation differences

- Peyré uses `α`, `β` for measures (not SI schedule coefficients).
- `m_α`, `Σ_α` are mean and covariance of the source Gaussian.

## Assumptions to check

- positive definite covariances for the Bures formula as stated
- absolute continuity of Gaussians
- Brenier potential convexity for optimality of the affine map

## Project satisfies assumptions?

Yes when both laws are non-degenerate Gaussians. Singular covariances require pseudoinverse handling and are flagged in code.

## Replication status

formulas-extracted-phase1

## Extracted equations

Source: local PDF pages 37-38 (section 2.6).

Gaussian OT map (2.40):

`T(x) = m_β + A (x - m_α)`

with

`A = Σ_α^{-1/2} (Σ_α^{1/2} Σ_β Σ_α^{1/2})^{1/2} Σ_α^{-1/2} = A^T`

Wasserstein-2 between Gaussians (2.41)-(2.42):

`W_2^2(α, β) = ∥m_α - m_β∥^2 + B(Σ_α, Σ_β)^2`

`B(Σ_α, Σ_β)^2 = tr(Σ_α + Σ_β - 2 (Σ_α^{1/2} Σ_β Σ_α^{1/2})^{1/2})`

Displacement interpolation uses McCann interpolant `(1-t) Id + t T` between Gaussians.
