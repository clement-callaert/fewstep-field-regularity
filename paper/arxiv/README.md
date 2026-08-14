# Public preprint sources

This directory is the public manuscript tree for the expanded article
*Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching
Schedules: A Certified Gaussian Counterexample*.

It is not a renamed short draft. The historical short draft lives under
`paper/archive/` and is not the public preprint.

## Build

From the repository root:

```bash
python scripts/verify_scalar_counterexample.py
python scripts/run_log_covariance_comparison.py
python scripts/run_in_family_comparison.py
python scripts/run_inversion_region.py
python scripts/run_lowrank_seed_fraction.py
python scripts/run_arxiv_stats.py
python scripts/make_arxiv_figures.py
python scripts/pack_arxiv_source.py
```

Compact JSON used by the PDF lives in `artifacts/`.
`make_arxiv_compact_artifacts.py` rebuilds those files from
`paper/arxiv/frozen_runs/` and from compact JSON already in `artifacts/`.
The gitignored `outputs/` tree is not required to rebuild the preprint.

Then from this directory:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

```bash
python scripts/check_arxiv_placeholder.py
python scripts/check_arxiv_release.py
python scripts/check_arxiv_structure.py
```

Default `pytest` must pass without a GitHub Release tag. Tag existence
is a later owner publication gate
(`python scripts/check_arxiv_release.py --require-tag`). Do not present
a release URL as live before that gate. Those checks are repository
maintenance; they are not stated in the public PDF.

## Files

| Path | Role |
| --- | --- |
| `main.tex` | Article body and appendices |
| `references.bib` | Bibliography |
| `generated/` | Macros and tables produced from artifacts |
| `figures/` | Vector figures plus JSON provenance sidecars |
| `artifacts/` | Compact machine-readable values used by the PDF |
| `main.pdf` | Compiled PDF (local deliverable) |
| `arxiv-source.zip` | Source bundle for an arXiv upload |
| `ARXIV_METADATA.md` | Title, abstract, categories, license options |
| `ARXIV_SUBMISSION_CHECKLIST.md` | Packaging checks |
| `CHANGELOG_FROM_CONFERENCE_VERSION.md` | Differences from the archived short draft |

No venue, review, or acceptance language belongs in `main.tex`.
License choice, git push, and arXiv upload remain owner decisions.
See `../../audit/RELEASE_GATE.md`.
