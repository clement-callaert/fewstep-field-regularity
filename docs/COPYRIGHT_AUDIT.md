# Copyright audit of `papers/`

Date: 2026-07-25. Scope: the literature directory `papers/` only.
This is distinct from `paper/` (the owner's own manuscript under
`paper/gddl2026/`), which is not a third-party copyright redistribution
problem.

Read-only audit. No files were deleted. No history rewrite was performed.

## Classifications

- **OWNER-ORIGINAL**: notes, summaries, or indexes written by the owner. Safe.
- **THIRD-PARTY-PDF**: a published paper PDF or other copyrighted redistributed
  body. Not safe on a public repo, now or after republication.
- **METADATA-ONLY**: bibliographic index (title, authors, year, DOI, arXiv ID,
  URL) with no copyrighted body text. Safe.

## Summary

| class | count | in current tree | in git history |
| --- | ---: | ---: | ---: |
| OWNER-ORIGINAL | 12 | yes (tracked) | yes |
| METADATA-ONLY | 2 | yes (tracked) | yes |
| THIRD-PARTY-PDF | 9 | yes (untracked, on disk) | **no** |
| placeholder (empty) | 1 | yes (`papers/pdfs/.gitkeep`, untracked) | no |

**Critical finding:** nine third-party PDFs sit under `papers/pdfs/` in the
working tree (~145 MB). They are covered by the existing `papers/pdfs/`
gitignore rule and have **never** been committed. A full `git rev-list
--objects --all` scan finds **no** `papers/**/*.pdf` blob. History purge for
these paths is therefore a defensive no-op today, but the on-disk copies must
still be removed before any wider distribution, and ignore rules must stay
strict so they cannot be force-added later.

## File table

| path | classification | tree | history | introducing commit(s) | flag |
| --- | --- | --- | --- | --- | --- |
| `papers/README.md` | METADATA-ONLY | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` (2026-07-23, Add Phase 1 exact Gaussian validation stack.) | |
| `papers/manifest.json` | METADATA-ONLY | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/albergo2023stochastic_interpolants.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/bonneel2015sliced_wasserstein.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/gmflow_2025.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/hairer2008solving_odes_i.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/lipman2023flow_matching.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/lipschitz_guided_2025.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/liu2022rectified_flow.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/peyre2019computational_ot.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/tong2024conditional_flow_matching.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/yang2024consistency_flow_matching.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/propositions/README.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/notes/templates/paper_note.md` | OWNER-ORIGINAL | tracked | yes | `b836ae372330556d09d5e98ffdb9d1258f2bb9e3` | |
| `papers/pdfs/.gitkeep` | OWNER-ORIGINAL (empty placeholder) | untracked (ignored) | no | n/a | |
| `papers/pdfs/albergo2023stochastic_interpolants.pdf` | THIRD-PARTY-PDF | untracked on disk | **never** | n/a (never committed) | **FLAG** |
| `papers/pdfs/bonneel2015sliced_wasserstein.pdf` | THIRD-PARTY-PDF | untracked on disk | **never** | n/a | **FLAG** |
| `papers/pdfs/gmflow_2025.pdf` | THIRD-PARTY-PDF | untracked on disk | **never** | n/a | **FLAG** |
| `papers/pdfs/lipman2023flow_matching.pdf` | THIRD-PARTY-PDF | untracked on disk | **never** | n/a | **FLAG** |
| `papers/pdfs/lipschitz_guided_2025.pdf` | THIRD-PARTY-PDF | untracked on disk | **never** | n/a | **FLAG** |
| `papers/pdfs/liu2022rectified_flow.pdf` | THIRD-PARTY-PDF | untracked on disk | **never** | n/a | **FLAG** |
| `papers/pdfs/peyre2019computational_ot.pdf` | THIRD-PARTY-PDF | untracked on disk | **never** | n/a | **FLAG** |
| `papers/pdfs/tong2024conditional_flow_matching.pdf` | THIRD-PARTY-PDF | untracked on disk | **never** | n/a | **FLAG** |
| `papers/pdfs/yang2024consistency_flow_matching.pdf` | THIRD-PARTY-PDF | untracked on disk | **never** | n/a | **FLAG** |

No `hairer2008solving_odes_i.pdf` is present (catalog marks it as likely
missing / Springer). That absence is correct for copyright hygiene.

Later commits that touched `papers/` metadata or notes without adding PDFs
include `2817272` (Phase 2) and `1923793` (Phase 3). None introduced PDF
blobs.

## Target state (proposed; not executed)

1. Keep tracked: `papers/README.md` (METADATA-ONLY bibliographic index with
   citations and source URLs, not PDF bodies), `papers/manifest.json`
   (bibliographic fields and retrieval metadata only), and `papers/notes/**`
   (OWNER-ORIGINAL).
2. Remove every THIRD-PARTY-PDF from the working tree (`rm` of the nine files
   under `papers/pdfs/`). Optionally keep an empty `papers/pdfs/.gitkeep` for
   local retrieval via `scripts/retrieve_papers.py`.
3. History: no PDF purge is required for past commits today (none contain
   these blobs). Still run a defensive path filter if the owner wants a
   belt-and-suspenders history, after a mirror backup. See
   `scripts/prepare_papers_cleanup.sh` (print-only).
4. Keep ignore rules so `papers/**/*.pdf` cannot recur in commits.

## Owner recommendation (one line)

Purge the nine third-party PDFs from the working tree now, keep
METADATA-ONLY index and OWNER-ORIGINAL notes, and never commit
`papers/**/*.pdf`; history rewrite for these PDFs is unnecessary today
because they were never committed.
