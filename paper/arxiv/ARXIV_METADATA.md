# arXiv metadata (not submitted)

Prepared 2026-08-13.
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

Few-step sampling in flow matching and stochastic interpolants requires choosing an interpolation schedule before endpoint error is observed. Averaged squared Lipschitzness of the drift, measured by the time-integrated squared 2-norm of its spatial Jacobian, is a plausible schedule-design criterion, but it is not a solver-specific discretization-error functional. Chen, Vanden-Eijnden, and Xu propose minimizing this quantity, denoted A_2; they do not claim or prove that A_2 universally ranks equal-NFE solver error. We study that narrower surrogate question. For independent N(0,1) and N(0,4), the exact regularity integrals are 5 pi/8 - 1 and pi^2/16, so regularity prefers trigonometric VP, whereas explicit Heun, a two-stage Runge-Kutta method, with a budget of eight function evaluations (NFE 8), prefers the linear path in Gaussian Wasserstein-2 distance. The inversion is certified by an exact rational Heun product and a nonnegative element of Q[pi, sqrt(2)]. A complementary construction shows that, for every step count N and every admissible endpoint log-scale, the unique integrated-regularity minimizer can have strictly larger N-step Euler endpoint error than a higher-regularity competitor aligned with that solver grid. A specified finite Gaussian enumeration of four candidate paths on 36 tested blocks contains both agreement and pairwise disagreement. These results limit a universal surrogate interpretation; they do not evaluate learned velocity fields or estimate a population failure frequency.

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

21 pages, 4 figures in the main text, 1 table in the main text. Code and compact artifacts: https://github.com/clement-callaert/fewstep-field-regularity

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
