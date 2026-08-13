# arXiv source checklist

Audit date: 2026-08-13. This checklist records local packaging. It is not
authorization to submit.

## Source rules

- [x] Submit LaTeX source, not a TeX-generated PDF as the only upload.
- [x] Filenames are portable (no spaces).
- [x] No absolute paths in `main.tex`.
- [x] PDFLaTeX figures (vector PDF).
- [x] `main.bbl` included in `arxiv-source.zip` (natbib).
- [x] Generated macros live in `generated/` and are included by relative path.

## Compile

- [x] `latexmk -pdf` from `paper/arxiv/` succeeds.
- [x] Second compile from `paper/arxiv/` with latexmk succeeds (14 pages).
- [ ] Re-extract `arxiv-source.zip` and compile in a clean directory immediately before upload.
- [x] No undefined citations or references in the final log.
- [x] Overfull boxes checked: none in the final `main.log`.

## Content greps (PDF text and TeX)

- [x] No em dash character (Unicode or TeX `---`).
- [x] No `Anonymous`.
- [x] No `Do not distribute`.
- [x] No `under review`.
- [x] No venue name in `main.tex` (bibliography may list conference
  proceedings titles such as ICLR or ICML as publication data).

## Fonts and PDF

- [x] `pdffonts main.pdf`: embedded Type 1 / Type 42, no Type 3.
- [x] `pdftotext` readable title, author, abstract.
- [ ] `qpdf --check`: tool not installed in this environment.
- [ ] `chktex`: tool not installed in this environment.

## Numbers

- [x] Macros from `scripts/make_arxiv_compact_artifacts.py` (continuous `R`).
- [x] `make_arxiv_tables.py` is an alias and must not restore `Rhat_24`.
- [x] `\precRatio` is `11528`.
- [x] 5 of 12 geometry×solver cells (4 of 12 at all three NFE); 14 inverted rows remain in the appendix listing.
- [x] Strongest-row `R` is `2.9441044083` vs `4.7305438136`, not the workshop `Rhat_24` pair.
- [x] Scalar Heun counterexample: `R_lin = 5 pi/8 - 1`, `r_lin = 6797469/3559400`.
- [x] Reconstruction residual distinct from 80-digit W2 gap.

## Provenance

- [x] Planned immutable release tag is `arxiv-v1`, created only after
      GDDL notification. Not presented as a live GitHub Release URL.
- [x] No retired commit-placeholder token remains in the arXiv tree.
- [ ] Owner must create `arxiv-v1` on the final scientific commit and
      publish the GitHub Release or Zenodo deposit before arXiv upload.
      Tag existence is a manual publication gate, not a scientific failure.

## Owner actions still required

- Create tag `arxiv-v1` on the final scientific commit.
- Publish the GitHub Release or Zenodo deposit from that tagged tree.
- Choose arXiv license (`ARXIV_METADATA.md`); none is selected here.
- Choose a code license file: `pyproject.toml` currently says MIT, but no
  `LICENSE` file exists. Do not treat that metadata line as a chosen license.
- Authorize push and/or arXiv upload.
- Obtain endorsement if the account needs it.
- Optional: GitHub visibility during any overlapping anonymous review.
