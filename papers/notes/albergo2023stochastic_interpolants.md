# Stochastic Interpolants: A Unifying Framework for Flows and Diffusions

- paper_id: `albergo2023stochastic_interpolants`
- authors: Michael S. Albergo, Nicholas M. Boffi, Eric Vanden-Eijnden
- year: 2023
- source_url: https://arxiv.org/abs/2303.08797
- local_filename: albergo2023stochastic_interpolants.pdf
- access_date: 2026-07-23
- sha256: see papers/manifest.json

## Relevance

Probability paths, interpolants, velocity fields.

## Formulas or results needed

- interpolant definition
- conditional and marginal velocity formulas

## Notation differences

- Definition 1: `x_t = I(t, x_0, x_1) + γ(t) z` with boundary `I(0)=x_0`, `I(1)=x_1`, `γ(0)=γ(1)=0`.
- Linear example (Fig. 2): `x_t = (1-t) x_0 + t x_1` (independent coupling when `(x_0,x_1)~ρ_0×ρ_1`).
- Lipschitz-guided companion uses scalar `I_t = α_t z + β_t x_1` (one-sided).
- Project protocol: `alpha ↔ α`, `sigma ↔ β` for one-sided SI; two-sided linear uses `alpha(t)=1-t`, `sigma(t)=t` with endpoints `(x_0, x_1)`.

## Assumptions to check

- Assumption 5: positive C2 densities with finite Fisher information; moment bounds on `∂_t I`
- Phase 1 Gaussians satisfy smoothness and moment bounds
- latent `γ` not required for Phase 1 deterministic ODE experiments

## Project satisfies assumptions?

Yes for Gaussian endpoints with finite moments. We use deterministic interpolants (`γ=0`) for Phase 1 ODE experiments.

## Replication status

formulas-extracted-phase1

## Extracted equations

Source: local PDF pages 9-12.

Definition 1 (2.1):

`x_t = I(t, x_0, x_1) + γ(t) z`

Linear interpolant without latent variable (Fig. 2):

`x_t = (1-t) x_0 + t x_1`

Velocity is the conditional expectation of `∂_t I` given `x_t` (transport equation / probability flow). Phase 1 uses the closed-form Gaussian affine field derived in the Lipschitz-guided note Example 3.3 generalized.
