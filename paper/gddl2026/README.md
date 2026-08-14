# Anonymous NeurIPS 2026 GDDL workshop source

Title: *Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching
Schedules: A Certified Gaussian Counterexample*.

This directory is the **live** anonymous workshop manuscript, synchronized
from the public arXiv scientific content. Venue fit is indirect:
distribution learning, Wasserstein endpoint error, and the geometry of
Gaussian covariance interpolation, not a new geometric architecture.

The historical short draft remains at `paper/archive/gddl2026-conference/`
and is not edited in place. A former separate supplement is archived at
`paper/archive/gddl2026-supplement-2026-08-13/`.

## Constraints

- NeurIPS 2026 `dblblindworkshop` (not camera-ready / final).
- Official CFP (https://gddl-neurips-2026.github.io/, retrieved 2026-08-13):
  short papers 2--4 pages excluding references; long papers 5--9 pages
  excluding references. This version is a **long** paper: seven PDF pages
  total. Main text occupies pages 1--6 (the conclusion ends on page 6).
  References begin on page 6 and continue onto page 7. Appendix A occupies
  the remainder of page 7. Six pages excluding references, within the
  long-paper 5--9 page rule.
- No author name, email, GitHub username, or identifying artefact URL.
- No NeurIPS-review-status wording in the anonymous PDF or this README.
- One anonymous PDF: the rational VP Heun certificate is Appendix A after
  the bibliography, not a separate supplement.
- PDF metadata: title and keywords only; `pdfauthor` remains empty.

## Hyperref / pdfTeX 1.40.22

This TeX Live's pdfTeX 1.40.22 segfaults on `\pdfendlink` when a
citation hyperlink straddles a page break. `main.tex` therefore sets
`draft=true` **only** when `\pdftexrevision` is `22`. Newer engines keep
`hidelinks` with live destinations. Metadata is still written with
`\hypersetup` and `\pdfinfo`. This workaround is **not** used in
`paper/arxiv/main.tex`, which loads `\usepackage[hidelinks]{hyperref}`
and must keep working links.

## Build

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
python ../../scripts/check_pdf_fonts.py main.pdf
```
