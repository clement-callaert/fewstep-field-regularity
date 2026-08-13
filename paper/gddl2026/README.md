# Anonymous NeurIPS 2026 GDDL workshop source

This directory is the **live** anonymous workshop manuscript, synchronized
from the public arXiv scientific content after the arXiv gate passed.

The historical short draft remains at `paper/archive/gddl2026-conference/`
and is not edited in place.

## Constraints

- NeurIPS 2026 `dblblindworkshop` (not camera-ready / final).
- Short-paper limit: **4 pages excluding references**. The body must end
  on page 4; the References heading may start on page 5. No body text on
  page 5.
- No author name, email, GitHub username, or identifying artefact URL.
- No "under review at NeurIPS" wording.
- Integer VP Heun certificate lives in `supplement.tex`, not in the
  4-page body. Grid-aware Euler (arXiv Appendix D / former Prop. 2) is
  not in the workshop body.

## Build

```bash
latexmk -pdf -interaction=nonstopmode main.tex
latexmk -pdf -interaction=nonstopmode supplement.tex
```
