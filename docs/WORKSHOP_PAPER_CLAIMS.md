# Frozen workshop paper claims

Status: Frozen before external validation or paper drafting.

Freeze date: 2026-07-24.

Primary target:
[Geometric Distributional Deep Learning at NeurIPS 2026](https://gddl-neurips-2026.github.io/).

This document narrows the paper claims. It does not modify the registered
Phase 3 hypotheses and does not authorize a broad Phase 5.

## Primary claim

> In the tested commuting Gaussian generative flows, ordering probability
> paths by averaged squared Jacobian regularity does not determine their
> fixed-NFE Gaussian W2 ordering.

Allowed evidence:

- `phase4_gaussian_reproduction_2026-07-24-v1:results`
- `phase4_precision_2026-07-24-v1:table`
- `phase4_decomposition_2026-07-24-v1:table`
- `phase4_robustness_2026-07-24-v1:table`
- `phase4_final_validation_2026-07-24-v1:table`

Required scope words: tested, commuting Gaussian, fixed-NFE, Gaussian W2.

Forbidden extensions:

- all generative flows;
- all schedules, solvers, or regularity criteria;
- learned neural fields;
- mixture targets;
- universal failure of Lipschitz-guided schedules.

## Secondary claim

> In the tested commuting Gaussian systems, the discrepancy is explained
> exactly at the modal propagation level by solver-stage-dependent signed
> one-step defects and their transport to the endpoint.

Allowed evidence and derivations:

- `docs/PHASE4_MATHEMATICAL_ANALYSIS.md`;
- `docs/P4_P1_PROOF_AUDIT.md`;
- `phase4_decomposition_2026-07-24-v1:table`;
- `phase4_diagnostics_2026-07-24-v1:table`.

“Exactly” modifies the algebraic modal transition and transported-defect
identity. It does not describe numerical quadrature of the baseline metric,
floating-point matrix operations, or a universal causal explanation outside
the commuting affine setting.

## Supporting empirical claim

> Fourteen averaged-regularity ranking inversions reproduce from clean code
> in the exact Gaussian benchmark and survive the stated precision audit.

Allowed numerical details:

- strongest inversion: low-rank Gaussian, dimension 8, Euler, NFE 8;
- linear: regularity `2.9476523251`, Gaussian W2 `0.8108540111`;
- variance-preserving: regularity `4.7295206355`, Gaussian W2
  `0.4564779075`;
- strongest W2 margin: `0.3543761036`;
- smallest surviving margin: `1.1188920612e-5`;
- maximum float64 versus 80-digit W2 difference:
  `9.7050430488e-10`;
- smallest-margin to precision-difference ratio: more than 11,500.

Every occurrence must cite
`phase4_gaussian_reproduction_2026-07-24-v1:results` and, for precision
statements, `phase4_precision_2026-07-24-v1:table`.

## Optional proposition claim

> For every \(L>0\) and integer \(N\geq1\), an explicit smooth scalar
> construction demonstrates that a larger averaged squared Jacobian need not
> imply a larger endpoint error for fixed-grid left-endpoint Euler.

This claim may appear in the main paper only if
`docs/P4_P1_PROOF_AUDIT.md` ends with `proof verified`. The paper must state
that the construction is grid-aware, that the field depends on \(N\), and
that it is not claimed to cause every Gaussian inversion.

If the proof status weakens, omit the proposition and use:

> We provide a controlled empirical and mathematical study of why averaged
> field regularity can fail to rank few-step generative paths in exact
> Gaussian settings.

## Solver-path interaction

Allowed supporting statement:

> In the tested low-rank Gaussian grid, variance-preserving is preferred for
> Euler, while linear is preferred for Heun and RK4 at both dimensions and
> the primary NFE budgets; the pattern persists in the recorded robustness
> checks.

This is context, not the novelty claim. Solver-dependent schedule behavior is
already established broadly in prior work.

## Post-hoc solver-specific proxy

Allowed exploratory statement:

> A solver-specific leading proxy agrees with 29 of 36 observed path
> preferences, compared with 22 of 36 for the averaged-regularity baseline.

Mandatory qualifier: post-hoc and in-sample.

Forbidden statement: the proxy predicts better, generalizes better, or is a
new selection criterion. It is not a primary contribution and should not
receive a main-paper correlation figure.

## Supporting external-validation claim (added 2026-07-24 under the gate)

This section is added under the change gate below after the pre-registered
external validation completed. It adds a clearly labeled supporting result
and does not modify the primary claim or its population.

> In a pre-registered non-centered anisotropic Gaussian family with affine
> drift \(b(t,x)=A(t)x+c(t)\), \(c\neq0\), frozen before execution, 11 of
> 18 equal-NFE comparison blocks reproduce the averaged-regularity ranking
> inversion, and all 11 pass an 80-digit precision audit.

Allowed evidence:

- `workshop_external_validation_2026-07-24-v1:results`
- `workshop_external_validation_2026-07-24-v1:inversions`
- `workshop_external_validation_2026-07-24-v1:precision`
- `docs/WORKSHOP_EXTERNAL_VALIDATION_PLAN.md` (including Amendment A1)

Mandatory qualifiers: pre-registered, single family, supporting only. The
scope of the primary claim remains the tested systems.

## Exclusions

- No mixture result supports the workshop paper conclusions.
- Dimension 8 mixture evidence is excluded because estimator calibration
  failed.
- Dirty Phase 3 artifacts are comparison inputs only.
- Superseded analyses, dirty smoke runs, and failed diagnostics are excluded.
- No image, video, learned-network, or perceptual-quality claim is allowed.
- No novelty claim may be based on absence from the literature search.

## Contribution statement

Use:

> We show, in exact commuting Gaussian generative flows, that averaged
> Jacobian regularity does not determine fixed-budget Wasserstein error
> ordering between probability paths. The mismatch is explained by solver
> stage sampling and by signed local defects transported to the endpoint. A
> controlled benchmark reproduces fourteen ranking inversions across Euler,
> Heun, and RK4, and an explicit scalar construction establishes the
> underlying non-implication for fixed-grid Euler integration.

The final clause is conditional on a verified P4-P1 audit.

## Title freeze

Primary title:

> When Averaged Field Regularity Fails to Rank Few-Step Generative Paths

No title may claim universal failure, a new sampler, a universally better
metric, refutation of Lipschitz-guided schedules, or demonstrated image,
video, or world-model improvement.

## Gate for changing these claims

External validation may narrow a claim or add a clearly labeled supporting
result. It may not promote the post-hoc proxy, broaden the population beyond
the tested systems, or alter the registered Phase 3 hypotheses. Any claim
change must be recorded here before the paper text changes.
