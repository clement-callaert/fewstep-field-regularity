# arXiv submission kit

Prepared 2026-08-13. This file is the form-field copy source for an upload
**after GDDL notification**. It is not an upload. Do not invent an arXiv
identifier. Do not deposit before the workshop decision.

The compiled PDF is `paper/arxiv/main.pdf`. Source is packed by
`python scripts/pack_arxiv_source.py`.

## Title

Few-Step Flow-Matching Error Can Be Misranked by Averaged Jacobian Regularity: A Certified Gaussian Counterexample

No LaTeX macros. No mathematical symbols. Character count: 114. Word count: 14.

## Abstract (plain text, arXiv form field)

Character count: 1341. Limit: 1920. One paragraph. Macros expanded; `$...$`
reduced to ASCII (`A_2`, `pi`, `W_2`). Word count: 190.

<!-- BEGIN ARXIV ABSTRACT -->
Does averaged squared Jacobian regularity rank two interpolants in the same order as equal-NFE endpoint error? Chen, Vanden-Eijnden, and Xu propose minimizing A_2, the time-integrated squared spatial Jacobian norm of a flow-matching marginal ODE, as a criterion for schedule design, without a proved discretization-error bound. Classical one-step bounds use a Lipschitz constant of the field; A_2 is not that constant. Already for independent N(0,1) and N(0,4), the exact regularity integrals of the linear and trigonometric variance-preserving Gaussian interpolants are 5 pi/8 - 1 and pi^2/16, while Heun at NFE 8 reverses Gaussian Wasserstein-2 distance. The linear Heun product is the rational 6797469/3559400; a nonnegative element of Q[pi, sqrt(2)] yields r_VP < 187/100. The object is a flow matching marginal interpolant ODE, not a score-based probability-flow ODE. The Gaussian drift and W_2 formula are closed form; the regularity integrand is exact, while multimode R is evaluated deterministically by adaptive quadrature. Pairwise and four-path census comparisons on commuting Gaussian interpolants are reported below; a finite census does not imply that a global A_2-minimizer minimizes fixed-NFE error. The analysis uses stochastic interpolants, few-step sampling, Runge-Kutta, and interpolation schedules; no learned field is used.
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
25 pages, 4 figures, 2 tables in the main text. Code and compact artifacts: https://github.com/clement-callaert/fewstep-field-regularity
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

## Dual submission `[OPEN]`

The official GDDL 2026 CFP (https://gddl-neurips-2026.github.io/, retrieved 2026-08-13) states that the workshop is non-archival and that "Workshop submissions can be subsequently or concurrently submitted to other venues." That is not a signed permission to post a de-anonymized arXiv preprint during double-blind review. Do not deposit the preprint or submit the workshop as part of packing this kit. Keep dual-submission status open until an explicit preprint rule is confirmed.
