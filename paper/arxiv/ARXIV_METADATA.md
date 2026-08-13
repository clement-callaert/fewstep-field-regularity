# arXiv metadata (not submitted)

Prepared 2026-08-13. No identifier is assigned. Do not invent an arXiv id.
Do not upload without an explicit owner decision.

## Title

Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching Schedules: A Certified Gaussian Counterexample

Hard constraints: no LaTeX macros, no mathematical symbols, under 120 characters,
contains "flow matching" (as "Flow-Matching"). Character count: 110. Word count: 12.

## Author

- Name: Clément Callaert
- Affiliation: CentraleSupélec and Université Paris-Saclay
- Email: callaert.clement@gmail.com
- ORCID: https://orcid.org/0009-0001-6863-8778
- Graphy: always "Clément Callaert" in the PDF, arXiv, GitHub, LinkedIn, and BibTeX
- Postal address, laboratory, supervisor, funding: none (by instruction)

## Abstract (plain text, for the abstract field)

Few-step sampling in flow matching and stochastic interpolants requires an interpolation schedule to be chosen before any endpoint error is observed. A natural question for schedule design is whether a scalar regularity functional ranks two schedules in the same order as equal-NFE discretization error. Chen, Vanden-Eijnden, and Xu propose minimizing A_2, the time-integrated squared spatial Jacobian norm of a flow-matching marginal ODE. They prove no bound relating A_2 to discretization error, Wasserstein-2 distance, or sampling error. Classical one-step bounds use a Lipschitz constant of the field; A_2 is not that constant. Already for independent N(0,1) and N(0,4), exact regularity integrals prefer the trigonometric variance-preserving interpolant while the Heun method at NFE 8 prefers the linear path in Gaussian Wasserstein-2 distance. The inversion is certified by an exact rational Heun product and a nonnegative polynomial in pi and sqrt(2), not by floating-point comparison. Fixed-stage Runge-Kutta methods use signed stage evaluations that the unsigned time average discards. All comparisons use exact Gaussian marginal fields. Multimode results are finite deterministic censuses, not a global optimality proof, and no learned vector field is used.

## Categories (proposed, not submitted)

- Primary: `cs.LG`
- Cross-list: `stat.ML`
- Cross-list: `math.NA`

Do not cross-list beyond these three. `math.NA` is intentional: the object is Runge-Kutta endpoint error and a Jacobian-norm criterion.

## MSC 2020 (arXiv form fields)

- `65L05` numerical methods for IVPs, ODEs
- `65L70` error bounds for numerical methods for ODEs
- `68T07` neural networks and deep learning
- `49Q22` optimal transportation

## ACM class (arXiv form fields)

- `G.1.7` Numerical Analysis -- Ordinary Differential Equations
- `I.2.6` Learning

## Keywords

flow matching, stochastic interpolants, few-step sampling, Runge-Kutta, Gaussian interpolants, Wasserstein-2, interpolation schedules

## Comments field (suggested)

23 pages, 4 figures, 2 tables in the main text. Code and compact artifacts: https://github.com/clement-callaert/fewstep-field-regularity

Update the page/figure/table counts from the compiled PDF immediately before upload. Do not put venue, review, or acceptance language in the comments field.

## License (prepared choice)

**CC BY 4.0.** The arXiv license chosen at upload is irrevocable for that version
(https://info.arxiv.org/help/license/). CC BY permits redistribution and
inclusion in corpora and aggregators.

## Journal reference / DOI

None.

## Repository

https://github.com/clement-callaert/fewstep-field-regularity

Public preprint path: `paper/arxiv/`.

## Timing (owner action)

Submit before 14:00 ET for the next day's announcement. Prefer a Tuesday--Friday
announcement; Monday listings include the weekend and are the longest.

## Endorsement

`cs.LG` (and `math.NA`) may require endorsement for a submitter without a
prior accepted arXiv paper in a related category. Endorsement is an owner
action. This repository does not request endorsement on the author's
behalf.

## What this file is not

Not an upload. Not a claim of institutional endorsement. Not an assigned arXiv id.

## Dual submission `[CLOSED]`

Official sources retrieved 2026-08-13:

1. GDDL 2026 CFP (https://gddl-neurips-2026.github.io/): non-archival;
   concurrent or subsequent submission to other venues is allowed;
   double-blind via OpenReview; follow the NeurIPS 2026 template and
   instructions.
2. NeurIPS 2026 Main Track Handbook, Preprints: a non-anonymous preprint
   will not result in rejection; do not write "Under review at NeurIPS";
   aggressive advertising of a paper under submission may be deemed a
   violation.
3. GDDL OpenReview invitation `NeurIPS.cc/2026/Workshop/GDDL/-/Submission`:
   no preprint field and no supplement-PDF field.

A non-anonymous preprint is allowed. It must not be promoted aggressively
during review. This file is not permission to deposit.
