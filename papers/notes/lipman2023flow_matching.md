# Flow Matching for Generative Modeling

- paper_id: `lipman2023flow_matching`
- authors: Yaron Lipman, Ricky T. Q. Chen, Heli Ben-Hamu, Maximilian Nickel, Matt Le
- year: 2023
- source_url: https://arxiv.org/abs/2210.02747
- local_filename: lipman2023flow_matching.pdf
- access_date: 2026-07-23
- sha256: see papers/manifest.json

## Relevance

Conditional Gaussian probability paths and closed-form conditional vector fields.

## Formulas or results needed

- OT and VP conditional flows
- conditional velocity

## Notation differences

- Lipman uses one-sided conditional paths `p_t(x | x_1) = N(x | μ_t(x_1), σ_t(x_1)^2 I)` with noise at `t=0` and data at `t=1`.
- Lipman `σ_t` is a residual standard deviation, not the SI data coefficient `β_t`.
- Project SI map: protocol `alpha(t) ↔ α_t` (noise/source coeff), `sigma(t) ↔ β_t` (data coeff). See docs/MATHEMATICAL_NOTES.md.
- Lipman Example II is conditional OT between endpoint Gaussians, not global OT between arbitrary measures.

## Assumptions to check

- smoothness: yes for Gaussian paths with differentiable schedules
- bounded support: no (Gaussians have full support)
- absolute continuity: yes for non-degenerate Gaussians
- non-degenerate covariance: requires `σ_t > 0` away from endpoints; `σ_min` small at `t=1`

## Project satisfies assumptions?

Yes for Phase 1 exact Gaussian experiments with `float64` and non-degenerate covariances. Endpoint `σ_min` handling is documented in code.

## Replication status

formulas-extracted-phase1

## Extracted equations

Source: local PDF pages 4-6.

Conditional Gaussian path (eq. 10):

`p_t(x | x_1) = N(x | μ_t(x_1), σ_t(x_1)^2 I)`

with `μ_0=0`, `σ_0=1`, `μ_1=x_1`, `σ_1=σ_min`.

Flow map (eq. 11):

`ψ_t(x) = σ_t(x_1) x + μ_t(x_1)`

Theorem 3 / eq. (15):

`u_t(x | x_1) = (σ'_t / σ_t) (x - μ_t) + μ'_t`

VP diffusion path (eq. 18)-(19): mean `α_{1-t} x_1`, std `sqrt(1 - α_{1-t}^2)`. This is **not** the project's trigonometric VP schedule.

OT conditional path (eq. 20)-(21):

`μ_t = t x_1`, `σ_t = 1 - (1 - σ_min) t`

`u_t(x | x_1) = (x_1 - (1 - σ_min) x) / (1 - (1 - σ_min) t)`

McCann displacement interpretation on p.6 for the conditional Gaussian pair.
