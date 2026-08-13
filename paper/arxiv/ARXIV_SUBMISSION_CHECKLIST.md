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
- [x] Second compile from a clean extraction of `arxiv-source.zip` succeeds.
- [x] No undefined citations or references in the final log.
- [x] Overfull boxes checked (hashes wrapped; remaining overfulls recorded below if any).

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

- [x] Macros from `scripts/make_arxiv_tables.py`.
- [x] `\precRatio` is `11528`.
- [x] 14/36 and 11/18 from artifact recount.
- [x] Reconstruction residual distinct from 80-digit W2 gap.

## Owner actions still required

- Choose arXiv license (`ARXIV_METADATA.md`).
- Choose code `LICENSE`.
- Authorize push and/or arXiv upload.
- Obtain endorsement if the account needs it.
- Optional: GitHub visibility during any overlapping anonymous review.
