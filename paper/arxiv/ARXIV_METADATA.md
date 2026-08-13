# arXiv metadata (not submitted)

Prepared 2026-08-13. No identifier is assigned. Do not invent an arXiv id.
Do not upload without an explicit owner decision.

## Title

Few-Step Flow-Matching Error Can Be Misranked by Averaged Jacobian Regularity: A Certified Gaussian Counterexample

Hard constraints: no LaTeX macros, no mathematical symbols, under 120 characters,
contains "flow matching" (as "Flow-Matching"). Character count: 114. Word count: 14.

## Author

- Name: Clément Callaert
- Affiliation: CentraleSupélec and Université Paris-Saclay
- Email: callaert.clement@gmail.com
- ORCID: owner action required before upload (Semantic Scholar / OpenAlex / Google Scholar merge on ORCID)
- Graphy: always "Clément Callaert" in the PDF, arXiv, GitHub, LinkedIn, and BibTeX
- Postal address, laboratory, supervisor, funding: none (by instruction)

## Abstract (plain text, for the abstract field)

Does averaged squared Jacobian regularity rank two interpolants in the same order as equal-NFE endpoint error? Chen, Vanden-Eijnden, and Xu propose minimizing A_2, the time-integrated squared spatial Jacobian norm of a flow-matching marginal ODE, as a criterion for schedule design, without a proved discretization-error bound. Classical one-step bounds use a Lipschitz constant of the field; A_2 is not that constant. Already for independent N(0,1) and N(0,4), the exact regularity integrals of the linear and trigonometric variance-preserving Gaussian interpolants are 5 pi/8 - 1 and pi^2/16, while Heun at NFE 8 reverses Gaussian Wasserstein-2 distance. The linear Heun product is the rational 6797469/3559400; a nonnegative element of Q[pi, sqrt(2)] yields r_VP < 187/100. The object is a flow matching marginal interpolant ODE, not a score-based probability-flow ODE. The Gaussian drift and W_2 formula are closed form; the regularity integrand is exact, while multimode R is evaluated deterministically by adaptive quadrature. Pairwise and four-path census comparisons on commuting Gaussian interpolants are reported below; a finite census does not imply that a global A_2-minimizer minimizes fixed-NFE error. The analysis uses stochastic interpolants, few-step sampling, Runge-Kutta, and interpolation schedules; no learned field is used.

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

25 pages, 4 figures, 2 tables in the main text. Code and compact artifacts: https://github.com/clement-callaert/fewstep-field-regularity

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

## Dual submission `[OPEN]`

The official GDDL 2026 CFP (https://gddl-neurips-2026.github.io/, retrieved 2026-08-13) states that the workshop is non-archival and that "Workshop submissions can be subsequently or concurrently submitted to other venues." That is not, by itself, a signed permission to post a de-anonymized arXiv preprint during double-blind review. Keep this item open until the organizers or OpenReview state an explicit preprint rule. This file is not permission to deposit.
