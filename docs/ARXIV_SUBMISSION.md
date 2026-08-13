# arXiv submission kit

Prepared 2026-08-13. This file is the form-field copy source for an upload
**after GDDL notification**. It is not an upload. Do not invent an arXiv
identifier. Do not deposit before the workshop decision.

The compiled PDF is `paper/arxiv/main.pdf`. Source is packed by
`python scripts/pack_arxiv_source.py`.

## Title

Averaged Jacobian Regularity Does Not Order Few-Step Error in Flow Matching: A Certified Gaussian Counterexample

No LaTeX macros. No mathematical symbols. Character count: 108. Word count: 15.

## Abstract (plain text, arXiv form field)

Character count: 1372. Limit: 1920. One paragraph. Macros expanded; `$...$`
reduced to ASCII (`A_2`, `pi`, `lambda_max`, `alpha`, `sigma`).

<!-- BEGIN ARXIV ABSTRACT -->
Flow matching and stochastic interpolants specify a probability flow ODE whose few-step sampling error depends on the sampling schedule. Schedule design therefore needs an a priori criterion. Chen, Vanden-Eijnden, and Xu propose minimizing the averaged squared Jacobian norm A_2, a Lipschitz constant of the marginal field, as a selection criterion, without a proved bound on discretization error. This paper asks whether the order induced by A_2 between two paths is reliable at a fixed number of function evaluations (NFE). Already for centered Gaussian interpolants the implication fails: for independent N(0,1) and N(0,4), the exact regularity integrals of the linear and trigonometric variance-preserving paths are 5 pi/8 - 1 and pi^2/16, while Heun at NFE 8 reverses Gaussian Wasserstein-2 distance. Three regimes then separate. As a pairwise comparator of linear versus VP, the ranking inverts in 5 of 12 geometry-by-solver cells. As an in-family objective, trigonometric VP versus the scalar log-covariance schedule (Chen Example 3.3 with M = lambda_max) invert in 9 of 36 blocks (4 of 12 cells). The unconstrained per-mode minimizer attains both the smallest regularity and the smallest Wasserstein-2 distance in 36 of 36 blocks, but is not a shared (alpha, sigma) interpolant for d >= 2. The analysis is confined to commuting Gaussians; no learned field is used.
<!-- END ARXIV ABSTRACT -->

`tests/analytical/test_release_gate.py` checks that this block is at most
1920 characters and matches `paper/arxiv/ARXIV_METADATA.md`.

## Categories

Do not list more than these three. Extra categories are reclassified by
moderators and delay announcement.

- Primary: `cs.LG`
- Cross-list: `stat.ML`
- Cross-list: `math.NA`

`math.NA` is intentional: the object is Runge–Kutta endpoint error and a
Jacobian-norm criterion. That listing is read in full.

## MSC 2020

- `65L05` numerical methods for IVPs, ODEs
- `65L70` error bounds for numerical methods for ODEs
- `68T07` neural networks and deep learning
- `49Q22` optimal transportation

## ACM class

- `G.1.7` Numerical Analysis -- Ordinary Differential Equations
- `I.2.6` Learning

## Comments

This field appears in the daily listing and is indexed. It is the only
place the code URL is visible without opening the PDF.

```
23 pages, 4 figures, 2 tables in the main text. Code and compact artifacts: https://github.com/clement-callaert/fewstep-field-regularity
```

No venue, review, or acceptance language.

## License

**CC BY 4.0.** Not the default non-exclusive license. The arXiv license
chosen at upload is irrevocable for that version
(https://info.arxiv.org/help/license/). CC BY permits redistribution and
inclusion in corpora and aggregators.

## Submission window

Submit before 14:00 ET for the next day's announcement. Prefer a
Tuesday–Friday announcement. Monday listings absorb the weekend and are
the longest, so each paper is read less.

## Source preflight

arXiv compiles the source. It does not run BibTeX. Do not upload a PDF
alone.

```bash
python scripts/pack_arxiv_source.py
```

The script enforces, in code:

1. `main.bbl` is in `paper/arxiv/arxiv-source.zip`. Without it every
   citation becomes `[?]`.
2. The archived `main.tex` starts with `\pdfoutput=1` before
   `\documentclass`.
3. Every `\includegraphics` is a relative PDF path that stays inside the
   archive. No absolute paths, no `../`.
4. The archive contains no `.aux`, `.log`, `.out`, or `.synctex.gz`.
5. Extracting the zip into a fresh directory and running `latexmk -pdf`
   produces a PDF with the same page count as `paper/arxiv/main.pdf` and
   with no `??` in the extracted text.

`--skip-compile` packs the zip without step 5.

## After GDDL notification

Do not run this sequence now. Trigger it only after the workshop
decision.

1. Create the ORCID. Replace `TODO-ORCID` in `CITATION.cff`. Keep **one**
   spelling of the name everywhere: PDF, arXiv, GitHub, BibTeX. Graphy:
   `Clément Callaert`. Without ORCID, `Clément Callaert` and
   `Clement Callaert` become two authors in Google Scholar and OpenAlex.
2. `git checkout main && git merge --ff-only arxiv-audit-and-release && git push origin main`
3. Deposit on arXiv with the fields above. **v1 is the only discovery
   event**: it enters the daily listing and email alerts; v2 does not.
   Upload one complete version.
4. Once the identifier is assigned: replace `TODO-ARXIV-ID` in
   `README.md` and `CITATION.cff`, set `date-released` to the announcement
   date (`YYYY-MM-DD`), commit, and push.
5. `git tag -a arxiv-v1 -m "arXiv v1" && git push origin arxiv-v1`
6. Confirm `FEWSTEP_RELEASE_GATE=1 pytest tests/analytical/test_release_gate.py` passes.
7. Pin the repository on the GitHub profile again.

Until that sequence, do not merge into `main`, do not create tags, and do
not deposit. `main` currently carries the old workshop title; that
mismatch is useful while the signed preprint is unannounced.

## Owner actions outside git

Unpin the repository from the GitHub profile for the review window. Do
not switch the repository to private: it is already public and indexed,
and going private does not restore anonymity.
