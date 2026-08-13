# Anonymity exposure audit

Date: 2026-07-25. Double-blind review window.

**Making the repository private for the review window covers ALL of these
exposures at once and is reversible. Removing files from the tree without a
history rewrite does NOT cover the history-level exposure.**

This audit concerns anonymity (title, venue, searchable artifact identity),
not copyright. Copyright of redistributed literature PDFs is covered in
`docs/COPYRIGHT_AUDIT.md` under `papers/` (plural). The owner's manuscript
lives under `paper/` (singular) and is an anonymity issue, not a third-party
copyright issue.

Read-only audit. No visibility change. No history rewrite. No commits.

## Earliest history milestones

| exposure | earliest commit | date | subject |
| --- | --- | --- | --- |
| Full Phase 4 artifact IDs in docs/results | `3c47b6799d6bbd5ba9b53617a69835b80491f596` | 2026-07-24 13:54 | Complete focused Phase 4 audit |
| Paper title string in workshop claims | `f5e857ca4a74293b26327c612fddf2492bd77d08` | 2026-07-24 15:28 | Freeze workshop claims and pre-registered external validation |
| Venue / GDDL / Geometric Distributional naming in docs | `f5e857ca4a74293b26327c612fddf2492bd77d08` | 2026-07-24 15:28 | (same; `docs/WORKSHOP_*` freeze) |
| Manuscript tree `paper/gddl2026/` with title in `main.tex` | `2d9d71ac97cecb5e9c57825b11ab0931925576ab` | 2026-07-24 17:53 | Add four-page anonymized GDDL 2026 workshop paper draft |
| Official NeurIPS 2026 dblblindworkshop style swap | `b149f35541db4da6bf8d2e79f0bb267c72d91b77` | 2026-07-24 20:51 | Apply workshop correction pass and switch to official NeurIPS 2026 dblblindworkshop style |

Artifact IDs appear earlier still in Phase 4 record commits
(`2a28fd41`, `e3ad51a1`, `f3ad0f96`, `08c14852`, `cc0c56ab`, …) once those
runs were committed into docs and related files.

## Exposure inventory

Remedy codes:

- **PRIVATE**: covered by making the repo private for the review window
  (tree and history become non-public at once).
- **REWRITE**: if the repo stays public, tree deletion alone is insufficient;
  a history rewrite (or never having pushed) is required to remove the
  searchable content from GitHub.

Every row below is covered by **PRIVATE**. The REWRITE column states whether
a public-repo strategy would also need history work.

| path / surface | what it reveals | tree now | also in history | remedy if public |
| --- | --- | --- | --- | --- |
| `paper/gddl2026/main.tex` | Exact title; `\workshoptitle{Geometric Distributional Deep Learning...}`; NeurIPS 2026 workshop mode | yes | yes (from `2d9d71ac`) | REWRITE |
| `paper/gddl2026/main.pdf` | Compiled manuscript with title and venue styling | yes | yes | REWRITE |
| `paper/gddl2026/README.md` | "GDDL @ NeurIPS 2026"; workshop name | yes | yes | REWRITE |
| `paper/gddl2026/neurips_2026.sty` / `neurips_2025.sty` | Official NeurIPS workshop template presence | yes | yes | REWRITE |
| `paper/gddl2026/references.bib` | Bibliography tied to the submission | yes | yes | REWRITE |
| `paper/gddl2026/figures/fig*.pdf` | Result figures (searchable visual identity) | yes | yes | REWRITE |
| `paper/gddl2026/figures/fig*.pdf.json` | `git_commit`, artifact IDs, SHA-256 source hashes | yes | yes | REWRITE |
| `paper/gddl2026/artifact_aliases.json` | Full artifact IDs, checksums, searchable `code_commit` hashes | yes | yes | REWRITE |
| `docs/WORKSHOP_TARGETS.md` | Venue URLs, GDDL name, proposed title | yes | yes (from `f5e857ca`) | REWRITE |
| `docs/WORKSHOP_PAPER_CLAIMS.md` | Title; GDDL @ NeurIPS 2026 link | yes | yes | REWRITE |
| `docs/WORKSHOP_PAPER_OUTLINE.md` | Title; NeurIPS 2026 GDDL target | yes | yes | REWRITE |
| `docs/WORKSHOP_CORRECTION_REPORT.md` | Venue, style, paper paths, artifact aliases | yes | yes | REWRITE |
| `docs/WORKSHOP_REVIEW_SIMULATION.md` | Draft path; GDDL CFP references | yes | yes | REWRITE |
| `docs/WORKSHOP_EXTERNAL_VALIDATION_PLAN.md` | Workshop-linked validation plan | yes | yes | REWRITE |
| `docs/DOUBLE_BLIND_AUDIT.md` | Names the exposure and GDDL policy notes | yes | yes | REWRITE |
| `docs/DOUBLE_BLIND_FINAL_CHECKLIST.md` | NeurIPS 2026 / GDDL checklist text | yes | yes | REWRITE |
| `docs/REPOSITORY_PUBLICATION_PLAN.md` | Names `paper/gddl2026/`, workshop lifecycle, alias map | yes | yes | REWRITE (path `gddl2026` alone is identifying) |
| `README_POST_REVIEW.md` | Exact paper title; figure embeds; artifact IDs | yes | yes (title content) | REWRITE |
| `README.md` (public) | Venue-silent by design; omits title/venue/hero | yes | yes | none for anonymity |
| `docs/PHASE4_RESULTS.md` and related Phase 4 docs | Full artifact IDs and SHA-256 tables (searchable) | yes | yes (from Phase 4 commits) | REWRITE if IDs must stay secret while public |
| `scripts/make_workshop_figures.py` | Path `paper/gddl2026/figures`; pinned artifact IDs | yes | yes | REWRITE for path/IDs if public |

## What private covers vs tree-only deletion

| action | tree exposure | history exposure on GitHub | reversible |
| --- | --- | --- | --- |
| Make repository private | covered | covered | yes (restore public later) |
| Delete `paper/` and `docs/WORKSHOP_*` from tip only | reduced | **still searchable** in old commits | tip change only |
| History rewrite removing those paths | reduced | reduced (after force-push) | destructive; needs backup |

## Owner recommendation (one line)

Make the repository private for the review window; that single reversible
action covers every anonymity exposure listed above without rewriting
history.
