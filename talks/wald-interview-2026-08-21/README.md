# Wald interview talk (21 August 2026)

Beamer deck for Clément Callaert's PhD interview with Christian Wald,
on the independent study

> When Averaged Field Regularity Fails to Rank Few-Step Generative Paths

## Contents

- `fewstep_wald_talk.tex` / `fewstep_wald_talk.pdf`: 12 main slides plus
  a technical appendix. Beamer theme Madrid, color theme beaver, 16:9
  geometry so the deck fills a typical Zoom or editor preview. Package
  `appendixnumberbeamer` keeps the main-slide counter at `n/12`.
- `CHANGELOG.md`: what moved from the previous 10-slide deck into the
  main narrative.
- `references.bib`
- `figures/`: data PDFs from frozen artifacts, plus TikZ in the tex file
- `make_talk_figures.py`: rebuilds the data figures
- `artifacts/`: pushable copies of the frozen 2026-07-24 run directories
- `artifacts/NUMBER_CONFIRMATION.md`: manuscript number check
- `speaker_notes.md`, `source_audit.md`, `qa_defense.md`

The original paper in `paper/gddl2026/` was not modified.

## Reproduce figures

From the repository root, with the project virtualenv:

```bash
.venv/bin/python talks/wald-interview-2026-08-21/make_talk_figures.py
```

The script reads checksum-pinned JSON from `talks/wald-interview-2026-08-21/artifacts/`
and refuses to plot on a digest mismatch.

## Compile the deck

`latexmk` may be absent. A clean pdflatex/bibtex loop:

```bash
cd talks/wald-interview-2026-08-21
rm -f fewstep_wald_talk.aux fewstep_wald_talk.bbl fewstep_wald_talk.blg \
      fewstep_wald_talk.log fewstep_wald_talk.nav fewstep_wald_talk.out \
      fewstep_wald_talk.snm fewstep_wald_talk.toc
pdflatex -interaction=nonstopmode fewstep_wald_talk.tex
bibtex fewstep_wald_talk
pdflatex -interaction=nonstopmode fewstep_wald_talk.tex
pdflatex -interaction=nonstopmode fewstep_wald_talk.tex
```

If `latexmk` is installed:

```bash
cd talks/wald-interview-2026-08-21
latexmk -pdf -interaction=nonstopmode fewstep_wald_talk.tex
```

## Pushing artifacts

`outputs/` is gitignored. The copies under `talks/wald-interview-2026-08-21/artifacts/`
are not. To track the repo-standard layout instead:

```bash
git add -f outputs/phase4_gaussian_reproduction_2026-07-24-v1 \
           outputs/phase4_precision_2026-07-24-v1 \
           outputs/phase4_decomposition_2026-07-24-v1 \
           outputs/workshop_external_validation_2026-07-24-v1
```

Do not change `.gitignore` unless that is an explicit later decision.
This talk directory was not committed by the talk build.

## Provenance

Frozen checksums match `docs/PHASE4_RESULTS.md`. See
`artifacts/NUMBER_CONFIRMATION.md` and `source_audit.md`.
HEAD at construction: `e48c939`. Requested freeze commit `b149f35`
is an ancestor; no checkout was performed.
