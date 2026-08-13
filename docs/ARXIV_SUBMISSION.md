# arXiv submission kit

Prepared 2026-08-13. This file is the form-field copy source for an upload
**after GDDL notification**. It is not an upload. Do not invent an arXiv
identifier. Do not deposit before the workshop decision.

The compiled PDF is `paper/arxiv/main.pdf`. Source is packed by
`python scripts/pack_arxiv_source.py`.

## Title

Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching Schedules: A Certified Gaussian Counterexample

No LaTeX macros. No mathematical symbols. Character count: 110. Word count: 12.

## Abstract (plain text, arXiv form field)

Character count: 1267. Limit: 1920. One paragraph. Macros expanded; `$...$`
reduced to ASCII (`A_2`, `W_2`). Word count: 180.

<!-- BEGIN ARXIV ABSTRACT -->
Few-step sampling in flow matching and stochastic interpolants requires an interpolation schedule to be chosen before any endpoint error is observed. A natural question for schedule design is whether a scalar regularity functional ranks two schedules in the same order as equal-NFE discretization error. Chen, Vanden-Eijnden, and Xu propose minimizing A_2, the time-integrated squared spatial Jacobian norm of a flow-matching marginal ODE. They prove no bound relating A_2 to discretization error, Wasserstein-2 distance, or sampling error. Classical one-step bounds use a Lipschitz constant of the field; A_2 is not that constant. Already for independent N(0,1) and N(0,4), exact regularity integrals prefer the trigonometric variance-preserving interpolant while the Heun method at NFE 8 prefers the linear path in Gaussian Wasserstein-2 distance. The inversion is certified by an exact rational Heun product and a nonnegative polynomial in pi and sqrt(2), not by floating-point comparison. Fixed-stage Runge-Kutta methods use signed stage evaluations that the unsigned time average discards. All comparisons use exact Gaussian marginal fields. Multimode results are finite deterministic censuses, not a global optimality proof, and no learned vector field is used.
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
   produces a PDF with the same page count as `paper/arxiv/main.pdf`,
   embedded fonts, no Type 3 fonts, and no `??` in the extracted text.
   Bitwise PDF hashes are not required to match across TeX versions.

`--skip-compile` packs the zip without step 5.

## After GDDL notification

Do not run this sequence now. Trigger it only after the workshop
decision.

1. ORCID is set in `CITATION.cff`:
   `https://orcid.org/0009-0001-6863-8778`. Keep **one** spelling of the
   name everywhere: PDF, arXiv, GitHub, BibTeX. Graphy: `Clément Callaert`.
   At arXiv upload, paste the same ORCID into the author form.
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

## Dual submission `[CLOSED]`

Official sources retrieved 2026-08-13:

1. GDDL 2026 CFP (https://gddl-neurips-2026.github.io/): non-archival;
   "Workshop submissions can be subsequently or concurrently submitted to
   other venues"; double-blind via OpenReview; submissions "must follow the
   NeurIPS 2026 template and instructions."
2. NeurIPS 2026 Main Track Handbook
   (https://neurips.cc/Conferences/2026/MainTrackHandbook), Preprints:
   "The existence of non-anonymous preprints (on arXiv or other online
   repositories, personal websites, social media) will not result in
   rejection." Public versions must not say "Under review at NeurIPS".
   "While having a nonanonymized preprint alone is not a violation of the
   double-blind reviewing policy, aggressive advertising of papers under
   submission may be deemed a violation."
3. GDDL OpenReview invitation `NeurIPS.cc/2026/Workshop/GDDL/-/Submission`
   (api2.openreview.net): form fields are title, authors, keywords, TLDR
   (optional), abstract, pdf, reciprocal_reviewer, email_sharing,
   data_release. There is no preprint-policy field and no supplement-PDF
   field.

A non-anonymous preprint is allowed under the NeurIPS instructions that
GDDL requires authors to follow. It must not be promoted aggressively
during review. This file is not permission to deposit.
