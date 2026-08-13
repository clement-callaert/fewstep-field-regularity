# Public preprint sources

This directory is the public manuscript tree for the expanded article
*When Averaged Field Regularity Fails to Rank Few-Step Generative Paths*.

It is not a renamed short draft. The historical short draft lives under
`paper/archive/` and is not the public preprint.

## Build

From this directory:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

Numerical macros and inversion tables are generated from pinned local
artifacts, not typed by hand:

```bash
python scripts/make_arxiv_tables.py
python scripts/make_arxiv_figures.py
python scripts/pack_arxiv_source.py
```

Those scripts must be run from the repository root. They refuse to run if
a pinned SHA-256 does not match.

## Files

| Path | Role |
| --- | --- |
| `main.tex` | Article body and appendices |
| `references.bib` | Bibliography |
| `generated/` | Macros and tables produced from artifacts |
| `figures/` | Vector figures plus JSON provenance sidecars |
| `main.pdf` | Compiled PDF (local deliverable) |
| `arxiv-source.zip` | Source bundle for an arXiv upload |
| `ARXIV_METADATA.md` | Title, abstract, categories, license options |
| `ARXIV_SUBMISSION_CHECKLIST.md` | Packaging checks |
| `CHANGELOG_FROM_CONFERENCE_VERSION.md` | Differences from the archived short draft |

No venue, review, or acceptance language belongs in `main.tex`.
License choice, git push, and arXiv upload remain owner decisions.
See `../../audit/RELEASE_GATE.md`.
