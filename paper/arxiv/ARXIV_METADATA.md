# arXiv metadata (not submitted)

Prepared 2026-08-13. No identifier is assigned. Do not invent an arXiv id.
Do not upload without an explicit owner decision.

## Title

When Averaged Field Regularity Fails to Rank Few-Step Generative Paths

## Author

- Name: Clément Callaert
- Affiliation: CentraleSupélec and Université Paris-Saclay
- Email: callaert.clement@gmail.com
- ORCID: none (by instruction)
- Postal address, laboratory, supervisor, funding: none (by instruction)

## Abstract (plain text, for the abstract field)

Choosing a probability path for few-step generative sampling is often guided by an averaged regularity scalar of the velocity field: a path with smaller averaged squared Jacobian norm is expected to discretize better at a fixed budget of function evaluations (NFE). This paper studies that ranking question in commuting Gaussian probability-flow ODEs, where endpoint laws and Gaussian 2-Wasserstein (W2) errors are available in closed form, the regularity integrand is analytically known, and sampling, training, and estimation noise are absent. On a registered grid of 72 equal-NFE configurations (36 two-path comparisons) the averaged-regularity ordering of linear versus variance-preserving paths does not determine the fixed-NFE W2 ordering: 14 of 36 blocks invert. The same phenomenon appears in a separately specified non-centered commuting family (11 of 18 blocks). All reported W2 values and inversion orderings survive an 80-digit reference calculation. An exact modal decomposition writes endpoint factor error as a transported sum of signed, solver-stage-dependent local defects, information that an unsigned time average of Jacobian norms cannot retain. An explicit scalar construction proves the corresponding non-implication for fixed-grid left-endpoint Euler, for every L>0 and every integer grid size N>=1. The construction is grid-aware and is not offered as the mechanism of the Gaussian inversions. The study is a controlled limitation: it does not refute regularity-guided schedule design, and no learned model is evaluated. The counts 14 of 36 and 11 of 18 are descriptive benchmark frequencies, not estimates of a population probability.

## Categories (proposed, not submitted)

- Primary: `cs.LG`
- Secondary: `math.NA`
- Optional further secondary: `stat.ML` if the current taxonomy still lists it as a cross-list for this kind of work.

Rationale: the scientific object is a ranking failure for a generative-path regularity scalar; the method is ODE analysis plus closed-form Gaussian W2.

## Keywords

flow matching, probability-flow ODE, few-step sampling, Wasserstein, Runge-Kutta, interpolant, field regularity

## Comments field (suggested)

11 pages, 4 figures. Source and reproduction scripts:
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
