# PASS 7 final audit (updated 2026-08-14)

This is the current audit of `paper/arxiv/` and `paper/gddl2026/` after the
bounded pre-publication polish. Earlier `PASS5_*` files and
`FINAL_ARXIV_AUDIT.md` remain stale; see `STALE_AUDIT_NOTICE.md`.

## Outcome

**READY WITH DISCLOSURES.** Certificate, tests, compact hashes, figure
sidecars, both PDFs, fonts, structure, the release checker, and a clean
arXiv-source compile pass. Nothing was committed. The `arxiv-v1` tag does
not exist. Raw `phase4_robustness` Hydra tables are not distributed. No
learned-model experiments exist (scope, not a missing contribution). Dual
submission / preprint policy is `[CLOSED]` from the published CFP and
handbook.

## Source state

- Branch: `fix/pass6-polish`
- Base commit: `9f0bd9df39bb1e40987319cc26d0eda22d41035e`
- Working tree: dirty (this polish plus pre-existing untracked user files).
  Sidecars record `working_tree_dirty: true` and the lock hash of
  `requirements-lock.txt`.
- Git history: available. No commit, push, or tag was created.

## PDFs

| PDF | pages | excluding references | fonts | anonymity |
| --- | --- | --- | --- | --- |
| `paper/arxiv/main.pdf` | 21 | main text pp. 1–11; refs begin p. 11 and continue p. 12; appendix pp. 13–21 | embedded Type 1 / CID, no Type 3 | named |
| `paper/gddl2026/main.pdf` | 7 | six pages excluding the bibliography (main text occupies pp. 1–6; refs begin p. 6 and continue p. 7; Appendix A occupies the remainder of p. 7) | embedded Type 1 / CID, no Type 3 | `pdfauthor` empty; official Anonymous Author(s) / Affiliation / Address / email block |

Workshop long-track rule is 5–9 pages excluding references. The submission
has six non-reference content pages and is compliant. NeurIPS footer
retained. Hyperref `draft=true` only for pdfTeX 1.40.22.

TeX engine used for both rebuilds: pdfTeX 3.141592653-2.6-1.40.22
(TeX Live 2022/dev/Debian), latexmk 4.76.

## Validation run (this pass)

- `pytest -q -ra`: all passed except the expected skip of
  `test_release_tokens_resolved_after_notification` when
  `FEWSTEP_RELEASE_GATE` is unset. With `FEWSTEP_RELEASE_GATE=1`,
  `python scripts/check_release_gate.py` passed.
- `python scripts/check_arxiv_structure.py`: passed.
- `python scripts/check_arxiv_release.py`: passed; tag is a manual gate.
- `python scripts/validate_artifacts.py paper/arxiv/artifacts`: OK.
- `python scripts/check_pdf_fonts.py` on both PDFs: OK.
- `python scripts/pack_arxiv_source.py`: wrote `paper/arxiv/arxiv-source.zip`
  (26 files); clean compile 21 pages, embedded fonts, no Type 3, `main.bbl`
  included.
- Scalar certificate regenerated; ranking inverted; integer comparison
  `19211335367141247013930300 < 19214891013548725548089344`.
- Grid-aware robustness: 12 records, 5 inverted; phase / off-grid
  frequency / Heun break exact aliasing (reported, not hidden).
- Four-path enumeration: 36/36. VP vs Chen Example 3.3: 9/36 inversions,
  4 cells.

## Dual submission / preprint `[CLOSED]`

Official sources retrieved 2026-08-14:

1. GDDL 2026 CFP (https://gddl-neurips-2026.github.io/): non-archival;
   submissions may be concurrently or subsequently submitted to other
   venues; long papers 5–9 pages excluding references.
2. NeurIPS 2026 Main Track Handbook, Preprints
   (https://neurips.cc/Conferences/2026/MainTrackHandbook): a
   non-anonymous arXiv preprint will not cause rejection; the public
   version must not say “Under review at NeurIPS”; aggressive advertising
   of a paper under submission may be deemed a violation.

Public non-anonymous arXiv preprint: allowed. Anonymous GDDL submission:
allowed. Concurrent submission: allowed by the workshop CFP. Aggressive
promotion during review: should be avoided. This is not a signed organizer
letter beyond the published policy.

## Disclosures

1. No clean commit; provenance is base SHA + dirty flag + diff hash.
2. Compact `robustness_lowrank.json` is distributed; the raw Hydra
   robustness table is not.
3. Lockfile is `pip freeze --exclude-editable` from Python 3.11.15,
   including this machine’s NVIDIA wheels.
4. After the owner commits, provenance sidecars and `arxiv-source.zip`
   should be regenerated once so the tagged snapshot is not recorded as
   dirty.
5. Pre-existing untracked user files (`.claude/`, talk aux, archived
   `fig_eigenmode`) were left in place.
6. This TeX Live’s pdfTeX 1.40.22 requires workshop hyperref `draft=true`
   to avoid a `\pdfendlink` segfault. Do not patch `neurips_2026.sty`.
   A rebuild on a newer engine should keep hidelinks. The uploaded PDF
   must still pass `scripts/check_pdf_fonts.py`.
