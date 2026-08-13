# Anonymous NeurIPS 2026 GDDL workshop source

This directory is the **live** anonymous workshop manuscript, synchronized
from the public arXiv scientific content.

The historical short draft remains at `paper/archive/gddl2026-conference/`
and is not edited in place.

## Constraints

- NeurIPS 2026 `dblblindworkshop` (not camera-ready / final).
- Official CFP (https://gddl-neurips-2026.github.io/, retrieved 2026-08-13):
  short papers 2--4 pages excluding references; long papers 5--9 pages
  excluding references. This version targets the **long** track at 5--6
  body pages.
- No author name, email, GitHub username, or identifying artefact URL.
- No "under review at NeurIPS" wording.
- Integer VP Heun certificate lives in `supplement.tex`.
- PDF metadata: title and keywords only; `pdfauthor` remains empty.

## Build

```bash
latexmk -pdf -interaction=nonstopmode main.tex
latexmk -pdf -interaction=nonstopmode supplement.tex
```
