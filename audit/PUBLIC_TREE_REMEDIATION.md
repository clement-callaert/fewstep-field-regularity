# Public-tree remediation (proposed, not pushed)

Audit date: 2026-08-13.
Branch: `arxiv-audit-and-release` from audited commit
`e48c9390e62b38f206342e6aeb7f160122ccc79c`.
Nothing in this document authorizes a git push, a GitHub visibility
change, or an arXiv upload.

## What this branch does to the public surface

1. Public preprint path is `paper/arxiv/`. Root `README.md` points there
   and contains no review language.
2. The short conference-style tree is moved to
   `paper/archive/gddl2026-conference/` with a README stating that it is
   historical, not the public preprint. `main.tex` in that archive is not
   edited.
3. The anonymous compiled PDF is removed from the **tip** of this branch.
   History retains it.
4. `README_POST_REVIEW.md` is replaced by a pointer. It is no longer a
   venue-adjacent landing page.
5. `pyproject.toml` homepage URLs are corrected from `github.com/calla/`
   to `github.com/clement-callaert/`. License text in pyproject is left
   as MIT pending an owner `LICENSE` file decision.
6. Ledger statuses are not changed. P4-C1 and P4-C2 remain `under-test`.
7. `talks/` and `.claude/` stay untracked.
8. No `CITATION.cff` until an arXiv identifier exists. Do not invent one.

## What remains dirty on purpose

The working tree still contains unstaged owner edits that were present
before this audit (documentation and docstring hygiene, figure rebuilds
under the archived short draft). Those files were mixed-reset off the
index at the start of the audit. They are **not** part of the audit
commit. Do not lump-commit them.

## License decision table (code)

pyproject currently declares `license = { text = "MIT" }` with no
`LICENSE` file. Choose one and add the file. This table does not choose.

| Option | What it allows | Main consequence for this repo |
| --- | --- | --- |
| MIT | Use, copy, modify, merge, publish, sublicense, sell, with copyright notice | Matches current pyproject text; simplest academic default |
| Apache-2.0 | MIT-like plus explicit patent grant and contribution terms | Stronger patent language; slightly more file boilerplate |
| GPL-3.0 | Copyleft: derivatives that are distributed must be GPL | Would restrict proprietary reuse of the solvers and metrics |

Recommendation for discussion only: MIT if the intent is to match
pyproject; Apache-2.0 if a patent grant is desired. GPL is a poor fit
for a small research library unless copyleft is an explicit goal.

## License decision table (arXiv manuscript)

See `paper/arxiv/ARXIV_METADATA.md`. The upload license is irrevocable
for that version. None is selected here.

Code license and manuscript license are independent decisions.

## GitHub visibility

Handbook-class policies for the overlapping conference season allow
non-anonymous preprints, and they forbid public text that says a paper is
under review at that conference. This branch removes that language from
the public README.

Whether the GitHub repository should be private until a notification
date is a separate owner decision (anonymity of a short draft versus a
named preprint). This branch does not change remotes or visibility.

## Citation

After an arXiv id exists, add `CITATION.cff` with that id, the title in
`paper/arxiv/`, and the author block already used there. Not before.

## Homepage URL

Corrected on this branch:

- was: `https://github.com/calla/fewstep-field-regularity`
- proposed: `https://github.com/clement-callaert/fewstep-field-regularity`

## Owner actions still required

1. arXiv license.
2. Code `LICENSE` file.
3. GitHub private vs public during any overlapping review.
4. Authorization to push this branch.
5. Authorization to submit to arXiv.
6. Whether `talks/` should remain local-only (recommended: yes).
7. Optional: retire leftover unstaged hygiene edits in a later owner
   commit, separate from this audit.
