# Gaussian Mixture Flow Matching Models

- paper_id: `gmflow_2025`
- authors: Hansheng Chen, Kai Zhang, Hao Tan, Zexiang Xu, Fujun Luan,
  Leonidas Guibas, Gordon Wetzstein, Sai Bi
- year: 2025
- source_url: https://arxiv.org/abs/2504.05304
- local_filename: gmflow_2025.pdf
- access_date: 2026-07-23
- sha256: see papers/manifest.json

## Relevance

Few-step discretization error for flow models and a learned Gaussian-mixture
parameterization of the **velocity residual distribution**. Relevant as
background for mixture targets and few-step NFE, not as a closed-form law for
exact GMM endpoint targets in this repository.

## Formulas or results needed

- mixture velocity parameterization (learned)
- discretization error discussion for mixtures / few-step sampling

## Notation differences

- GMFlow uses flow matching with `α_t := 1-t`, `σ_t := t` and residual velocity
  `u := (x_t - x_0) / σ_t` (eq. 2 in the PDF).
- Project SI convention uses `I_t = alpha(t) z + sigma(t) x_1` with
  `alpha(0)=1`, `sigma(1)=1`. Convert carefully; do not mix residual `σ_t`
  with SI `beta_t`.
- GMFlow predicts a GM over velocity `u` given `x_t` via a neural net. That is
  distinct from an exact GMM law for the target `x_1`.

## Assumptions to check

- learned model approximates the velocity residual distribution
- image / high-dimensional empirical setting for reported metrics
- Gaussian mixture components with shared isotropic variance `s^2 I` in their
  simplified parameterization

## Project satisfies assumptions?

Phase 2 exact GMM targets do **not** use GMFlow's learned GM velocity network.
Exact independent-coupling mixture marginal fields are an original derivation
documented in `docs/MATHEMATICAL_NOTES.md`, checked by AD and moment tests.

## Replication status

formulas-extracted-phase2-context-only

## Extracted equations

Source: local PDF pages 3-4 (sections 2-3).

Linear flow schedule (project-relevant convention in GMFlow):

`α_t := 1 - t`, `σ_t := t`

Residual velocity (eq. 2):

`u := (x_t - x_0) / σ_t`

Mean velocity is the conditional expectation of `u` under `p(x_0 | x_t)`.

GMFlow models `p(u | x_t)` as a Gaussian mixture and trains with a KL / hybrid
loss (eq. 6). Inference uses analytic GM-SDE / GM-ODE solvers derived from the
predicted mixture.

## Project use

- Cite for few-step discretization motivation and mixture velocity expressivity.
- Do not copy GMFlow solvers into Phase 2 exact analytical experiments.
- Do not claim that GMFlow proves formulas for exact GMM endpoint marginals.
