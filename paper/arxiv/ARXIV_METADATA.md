# arXiv metadata (not submitted)

Prepared 2026-08-13. No identifier is assigned. Do not invent an arXiv id.
Do not upload without an explicit owner decision.

## Title

Averaged Jacobian Regularity Does Not Order Few-Step Error of Gaussian Interpolant ODEs

## Author

- Name: Clément Callaert
- Affiliation: CentraleSupélec and Université Paris-Saclay
- Email: callaert.clement@gmail.com
- ORCID: none (by instruction)
- Postal address, laboratory, supervisor, funding: none (by instruction)

## Abstract (plain text, for the abstract field)

Few-step sampling of a continuous-time generative model requires a probability path, a numerical solver, and a budget of field evaluations (NFE). Chen, Vanden-Eijnden, and Xu propose minimizing averaged squared Jacobian regularity A2 as a path-selection criterion. This paper asks whether the order that this scalar induces between two interpolants is reliable at fixed NFE. The implication fails already for centered Gaussian interpolants. The main logical result is a one-dimensional, seed-free counterexample: for independent N(0,1) and N(0,4) endpoints, the exact regularity integrals of the linear and trigonometric variance-preserving paths are 5 pi/8 - 1 and pi^2/16, while explicit Heun with NFE 8 reverses the Gaussian W2 ranking. The linear Heun factor is the rational 6797469/3559400; a rational enclosure in Q[pi, sqrt(2)] certifies W2_lin < 0.091 < 0.130 < W2_VP. On four centered geometries the per-mode log-covariance schedule (Chen et al. Example 3.3), which minimizes R, attains the smallest W2 in all 36 solver-budget blocks. Linear versus VP invert in 5 of 12 geometry-by-solver cells (4 of 12 at every NFE in {8,16,32}), from three distinct R comparisons. Thus R is reliable as an objective on this family and not reliable as a linear-versus-VP comparator away from that optimum.

## Categories (proposed, not submitted)

- Primary: `cs.LG`
- Secondary: `math.NA`
- Optional further secondary: `stat.ML` if the current taxonomy still lists it as a cross-list for this kind of work.

Rationale: the scientific object is a ranking failure for a generative-path regularity scalar; the method is ODE analysis plus closed-form Gaussian W2.

## Keywords

flow matching, interpolant ODE, few-step sampling, Wasserstein, Runge-Kutta, field regularity

## Comments field (suggested)

14 pages, figures. Source and reproduction scripts:
https://github.com/clement-callaert/fewstep-field-regularity

Do not put venue, review, or acceptance language in the comments field.

## Journal reference / DOI

None.

## Repository

https://github.com/clement-callaert/fewstep-field-regularity

Public preprint path after this branch is merged by the owner: `paper/arxiv/`.

## License options (owner must choose; none is selected here)

The arXiv license chosen at upload is irrevocable for that version
(https://info.arxiv.org/help/license/ and the submittal agreement,
checked 2026-08-13).

| Option | What it allows | Main consequence |
| --- | --- | --- |
| CC BY 4.0 | Share and adapt, including commercial use, with attribution | Most journal-friendly among the open CC options; others may republish adapted versions |
| CC BY-SA 4.0 | Same, but adaptations must use the same license | Copyleft on derivatives; some publishers dislike ShareAlike |
| CC BY-NC-SA 4.0 | Non-commercial share-alike | Blocks commercial reuse; can conflict with some publisher policies |
| CC BY-NC-ND 4.0 | Non-commercial, no derivatives | Strong reuse limit; translations and overlays need separate permission |
| CC0 1.0 | Public domain dedication | Copyright is waived to the extent allowed; strongest reuse, least control |
| arXiv.org perpetual non-exclusive license 1.0 | arXiv may distribute; no general reuse grant to third parties | Default-like restricted reuse; others must ask the author |

If a journal or funder requires a license not in the list, arXiv currently
says: select the arXiv non-exclusive license and print the desired license
on the first page, provided it does not restrict arXiv's own license.

This file does not choose.

## Endorsement

`cs.LG` (and `math.NA`) may require endorsement for a submitter without a
prior accepted arXiv paper in a related category. Endorsement is an owner
action. This repository does not request endorsement on the author's
behalf.

## What this file is not

Not an upload. Not a claim of institutional endorsement. Not a license
grant.
