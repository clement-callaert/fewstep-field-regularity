# arXiv submission kit

Prepared 2026-08-14. This file is the form-field copy source for an owner
upload. It is not an upload. Do not invent an arXiv identifier.

The GDDL 2026 CFP states that the workshop is non-archival and that
submissions may be concurrently or subsequently submitted to other
venues. The NeurIPS 2026 Main Track Handbook states that a non-anonymous
arXiv preprint will not cause rejection, provided the public version does
not say “Under review at NeurIPS” and the paper is not aggressively
advertised during review. Concurrent arXiv + anonymous GDDL is therefore
allowed by the published policies. This file is not organizer permission
beyond those texts.

The compiled PDF is `paper/arxiv/main.pdf`. Source is packed by
`python scripts/pack_arxiv_source.py`.

## Title

Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching Schedules: A Certified Gaussian Counterexample

No LaTeX macros. No mathematical symbols. Character count: 110. Word count: 12.

## Abstract (plain text, arXiv form field)

Character count: update from the compiled abstract. Limit: 1920. One paragraph. Macros expanded; `$...$`
reduced to ASCII (`A_2`, `W_2`).

<!-- BEGIN ARXIV ABSTRACT -->
Few-step sampling in flow matching and stochastic interpolants requires choosing an interpolation schedule before endpoint error is observed. Averaged squared Lipschitzness of the drift, measured by the time-integrated squared 2-norm of its spatial Jacobian, is a plausible schedule-design criterion, but it is not a solver-specific discretization-error functional. Chen, Vanden-Eijnden, and Xu propose minimizing this quantity, denoted A_2; they do not claim or prove that A_2 universally ranks equal-NFE solver error. We study that narrower surrogate question. For independent N(0,1) and N(0,4), the exact regularity integrals are 5 pi/8 - 1 and pi^2/16, so regularity prefers trigonometric VP, whereas explicit Heun, a two-stage Runge-Kutta method, with a budget of eight function evaluations (NFE 8), prefers the linear path in Gaussian Wasserstein-2 distance. The inversion is certified by an exact rational Heun product and a nonnegative element of Q[pi, sqrt(2)]. A complementary construction shows that, for every step count N and every admissible endpoint log-scale, the unique integrated-regularity minimizer can have strictly larger N-step Euler endpoint error than a higher-regularity competitor aligned with that solver grid. A specified finite Gaussian enumeration of four candidate paths on 36 tested blocks contains both agreement and pairwise disagreement. These results limit a universal surrogate interpretation; they do not evaluate learned velocity fields or estimate a population failure frequency.
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
21 pages, 4 figures, 1 table in the main text. Code and compact artifacts: https://github.com/clement-callaert/fewstep-field-regularity
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
