# Speaker notes

Target duration: 12 to 14 minutes, with about 1 to 3 minutes of safety in
a 15-minute slot. Appendix slides are not timed.

Pronunciation: NFE = "en-eff-ee" (field evaluations). VP = trigonometric
variance-preserving path. \(\mathcal{R}\) = "arr of b". Spectral norm, not
Frobenius. \(\mathrm{W}_2\) is Wasserstein-2, not \(\mathrm{W}_2^2\).

Do not say "regularity does not matter", "this disproves Chen et al.",
"VP is better than linear", or "the result transfers to CTMCs".

## Slide 1. Title (0:25)

Say who you are, affiliation, and that this is an independent study of
few-step sampling for the interview with Christian Wald.

Transition: "I will start from what Flow Matching actually learns."

If short: skip nothing here.

## Slide 2. Generative ODEs and Flow Matching (1:10)

Read the ODE. Stress that \(v_\theta\) takes time and state and returns a
velocity. Point at the continuity equation, then the FM loss: regress the
network onto a generating field \(u_t\). Close with: after training, one
still has to integrate the ODE numerically.

Source: Lipman et al., ICLR 2023, eq. (5).

Transition: "The population loss is intractable. Conditional Flow Matching
makes the target accessible."

If short: skip the domain of \(v_\theta\); keep the loss.

## Slide 3. CFM and interpolation (1:15)

Read the interpolant and \(\dot X_t\). Define \(b_t\) as the conditional
expectation, then say explicitly: \(b_t=u_t\), the generating field of
slide 2. Then CFM: train on per-sample conditional velocities.
Quote the gradient identity: \(\nabla\mathcal{L}_{\mathrm{CFM}}=\nabla\mathcal{L}_{\mathrm{FM}}\).
Do not let positivity of \(p_t\) stand alone. Add: "under the standard
integrability and differentiation assumptions". Close with the Gaussian
laboratory: the exact marginal field is \(b=Ax+c\).

Sources: Lipman Theorem 2; Albergo interpolant.

Transition: "Once the field is known, few-step sampling is a joint path
and solver problem."

If short: skip the pathwise derivative line.

## Slide 4. The few-step question (1:00)

Walk the chain left to right. Define NFE before Euler, Heun, RK4.
Read the two exact path formulas. Say: "With independent endpoint
sampling, the linear interpolant uses the product coupling, not an
optimal transport coupling." Then read the question slowly.

Sources: Lipman; Albergo; Liu; Chen, Vanden-Eijnden, and Xu; Sabour.

Transition: "To ask that ranking question cleanly, I use a closed-form
Gaussian laboratory."

If short: drop the Lipman-VP distinction; keep the product-coupling sentence.

## Slide 5. Exact Gaussian benchmark (1:10)

Read \(m_t\), \(Q(t)\), \(C_t\), then \(b=Ax+c\) with dimensions.
Use the wording "controlled Gaussian laboratory isolates discretization
error". Point at the coefficient plane. Then the five bullets. For the
metric, say "Gaussian \(W_2\) is available in closed form", not
"\(W_2\) is analytical".

Sources: Albergo; Lipman; Gelbrich.

Transition: "The candidate ranking statistic is an unsigned time average
of Jacobian magnitude."

If short: skip the centered \(A=\tfrac12 Q'Q^{-1}\) fact (it is in A2).

## Slide 6. Candidate regularity (1:00)

Read \(\mathcal{R}\). Stress spectral 2-norm. Bound versus ranking, in one
sentence. Then the three stage rows at NFE 8.

Source: Chen, Vanden-Eijnden, and Xu, arXiv:2509.01629v3, Def. 3.2.

Transition: "On a frozen commuting Gaussian grid, that distinction is
visible in the endpoint \(\mathrm{W}_2\) ranking."

If short: drop "what \(\mathcal{R}\) discards" and point at the stages.

## Slide 7. Frozen protocol (0:45)

Read the table once. Emphasize: each block holds target, solver, and NFE
fixed. Then: 14 ranking inversions among 36 prespecified paired
comparisons. Do not call this a frequency.

Source: `phase4_gaussian_reproduction_2026-07-24-v1:results`.

Transition: "The strongest inversion is visible in both quantities at once."

If short: skip condition-number wording; keep 72 / 36 / 14.

## Slide 8. Main result (1:15)

Point at the two bars: regularity prefers linear, \(\mathrm{W}_2\) prefers
VP. Quote the four numbers only if asked; the caption has them. Read the
result block slowly. Do not promote 14/36 into a population statement.

Source: same frozen results file. Strongest block: low-rank, \(d=8\),
Euler, NFE 8.

Transition: "The reason is exact once the modal error is written as a
signed transported sum."

If short: skip the 78\% clause.

## Slide 9. Mechanism (1:25)

This is the central identity. Read it. "Earlier numerical, later exact."
Point at same-sign accumulation versus alternating cancellation. Mark the
schematic as schematic.

Transition: "The same non-implication can be made fully explicit for
fixed-grid Euler."

If short: skip the schematic and keep the identity.

## Slide 10. Grid-aware Euler construction (1:15)

Define \(\epsilon_N\), \(a_0\), \(a_{1,N}\). Both exact endpoints equal
\(e^{L}\). The oscillatory field has strictly larger \(\mathcal{R}\).
Euler is exact on \(a_{1,N}\) because every node sits on a cosine maximum.
The constant field is not exact: \((1+L/N)^N<e^{L}\). Then the quantifier:
\(a_{1,N}\) is chosen after the grid \(N\).

Transition: "I will now separate what this study establishes from its
limitations."

If short: read the product identity and the quantifier only.

## Slide 11. Scope and limitations (1:00)

Left column, then right column. Next experiments in one breath.
Exponential integrators: exact on these affine fields, so the ranking
question is vacuous for them here.

Sources: Lu et al.; Zhang and Chen.

Transition: "Three conclusions, then the discrete-model question."

If short: skip the next-experiment list.

## Slide 12. Conclusion (1:00)

Read the three numbered conclusions slowly. Then the research-direction
box: path, rates, finite-step CTMC solver, fixed budget. Frame it as the
next question, not a proved transfer.

Stop. Do not add a fourth takeaway.

If short: skip nothing on this slide.

## Timed table

| slide | target | cumulative |
| --- | ---: | ---: |
| 1 Title | 0:25 | 0:25 |
| 2 Flow Matching | 1:10 | 1:35 |
| 3 CFM and interpolant | 1:15 | 2:50 |
| 4 Few-step question | 1:00 | 3:50 |
| 5 Gaussian benchmark | 1:10 | 5:00 |
| 6 Regularity criterion | 1:00 | 6:00 |
| 7 Frozen protocol | 0:45 | 6:45 |
| 8 Main result | 1:15 | 8:00 |
| 9 Mechanism | 1:25 | 9:25 |
| 10 Euler construction | 1:15 | 10:40 |
| 11 Scope | 1:00 | 11:40 |
| 12 Conclusion | 1:00 | 12:40 |

If running long after slide 8, skip slide 10 and keep 9, 11, and 12.
Proposition 1 can be answered in Q&A.

## Numerical claims and sources

- 72 configs, 36 blocks, 14 inversions, strongest four numbers:
  `phase4_gaussian_reproduction_2026-07-24-v1:results`
- 80-digit max discrepancy \(9.7050430488\times 10^{-10}\), smallest margin
  \(1.1188920612\times 10^{-5}\): `phase4_precision_2026-07-24-v1`
- 11 of 18, \(\mathcal{R}\) margin \(0.7513\):
  `workshop_external_validation_2026-07-24-v1`
- All of the above match `paper/gddl2026/main.tex`. See
  `artifacts/NUMBER_CONFIRMATION.md`.
