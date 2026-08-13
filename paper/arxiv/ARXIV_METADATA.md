# arXiv metadata (not submitted)

Prepared 2026-08-13. No identifier is assigned. Do not invent an arXiv id.
Do not upload without an explicit owner decision.

## Title

Averaged Jacobian Regularity Does Not Order Few-Step Error in Flow Matching: A Certified Gaussian Counterexample

Hard constraints: no LaTeX macros, no mathematical symbols, under 120 characters,
contains "flow matching". Character count: 108. Word count: 15.

## Author

- Name: Clément Callaert
- Affiliation: CentraleSupélec and Université Paris-Saclay
- Email: callaert.clement@gmail.com
- ORCID: owner action required before upload (Semantic Scholar / OpenAlex / Google Scholar merge on ORCID)
- Graphy: always "Clément Callaert" in the PDF, arXiv, GitHub, LinkedIn, and BibTeX
- Postal address, laboratory, supervisor, funding: none (by instruction)

## Abstract (plain text, for the abstract field)

Flow matching and stochastic interpolants specify a probability flow ODE whose few-step sampling error depends on the sampling schedule. Schedule design therefore needs an a priori criterion. Chen, Vanden-Eijnden, and Xu propose minimizing the averaged squared Jacobian norm A_2, a Lipschitz constant of the marginal field, as a selection criterion, without a proved bound on discretization error. This paper asks whether the order induced by A_2 between two paths is reliable at a fixed number of function evaluations (NFE). Already for centered Gaussian interpolants the implication fails. For independent N(0,1) and N(0,4) endpoints, the exact regularity integrals of the linear and trigonometric variance-preserving paths are 5 pi/8 - 1 and pi^2/16. Explicit Heun method, a two-stage Runge-Kutta scheme, with NFE 8 reverses the ranking of Gaussian Wasserstein-2 distance: the linear factor is the rational 6797469/3559400, and a rational enclosure of the VP product in Q[pi, sqrt(2)] yields r_VP < 187/100. Three regimes then separate. As a pairwise comparator of linear versus VP, the ranking inverts in 5 of 12 geometry-by-solver cells (4 of 12 at every tested NFE), from 3 distinct regularity comparisons. As an in-family objective, trigonometric VP versus the scalar log-covariance schedule (Chen Example 3.3 with M = lambda_max) invert in 9 of 36 blocks and 4 of 12 cells. The unconstrained per-mode minimizer attains both the smallest regularity and the smallest Wasserstein-2 distance in 36 of 36 blocks, but is not a shared (alpha, sigma) interpolant for d >= 2. The analysis is confined to commuting Gaussians; no learned field is used.

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

flow matching, stochastic interpolants, diffusion models, probability flow ODE, few-step sampling, sampling schedule, Lipschitz regularity, Wasserstein distance, Runge-Kutta, numerical analysis

## Comments field (suggested)

19 pages, 7 figures, 13 tables. Code and compact artifacts: https://github.com/clement-callaert/fewstep-field-regularity

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
