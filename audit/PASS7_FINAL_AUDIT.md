# PASS 7 final audit (2026-08-13)

This is the current audit of `paper/arxiv/` and `paper/gddl2026/` after
the scientific-repositioning pass. Earlier `PASS5_*` files and
`FINAL_ARXIV_AUDIT.md` are stale; see `STALE_AUDIT_NOTICE.md`.

## Outcome

**READY WITH DISCLOSURES.** Certificate, tests, compact hashes, figure
sidecars, both PDFs, fonts, structure, and the release checker pass.
Nothing was committed. The `arxiv-v1` tag does not exist. Raw
`phase4_robustness` Hydra tables are not distributed. No learned-model
experiments exist. GDDL venue fit is distributional rather than
architectural. Dual-submission/preprint policy remains `[OPEN]`.

## Source state

- Branch: `fix/pass6-polish`
- Base commit: `aaef59caa6e3d4bca79b4538bb3f3d6d1706a8e4`
- Working tree: dirty (tracked edits plus new files). Sidecars record
  `working_tree_dirty: true` and the lock hash of `requirements-lock.txt`.
- Git history: available. No commit, push, or tag was created.

## PDFs

| PDF | pages | body excluding refs | fonts | anonymity |
| --- | --- | --- | --- | --- |
| `paper/arxiv/main.pdf` | 21 | 10 (refs start p.11) | embedded Type 1 / CID, no Type 3 | named |
| `paper/gddl2026/main.pdf` | 7 | 5 (refs p.6, appendix p.7) | embedded Type 1 / CID, no Type 3 | `pdfauthor` empty; Anonymous Author(s) |

Workshop long-track rule is 5–9 pages excluding references. Body is 5.
NeurIPS footer retained. Hyperref `draft=true` only for pdfTeX 1.40.22.

## Validation run (this pass)

- `pytest -q -ra`: all passed except the expected skip of
  `test_release_tokens_resolved_after_notification` (`FEWSTEP_RELEASE_GATE` unset).
- `python scripts/check_arxiv_structure.py`: passed.
- `python scripts/check_arxiv_release.py`: passed; tag is a manual gate.
- `python scripts/validate_artifacts.py paper/arxiv/artifacts`: OK.
- `python scripts/check_pdf_fonts.py` on both PDFs: OK.
- `python scripts/pack_arxiv_source.py --skip-compile`: wrote
  `paper/arxiv/arxiv-source.zip` (26 files).
- Scalar certificate regenerated; ranking inverted; integer comparison
  `19211335367141247013930300 < 19214891013548725548089344`.
- Grid-aware robustness: 12 records, 5 inverted; phase / off-grid
  frequency / Heun break exact aliasing (reported, not hidden).

## Disclosures

1. No clean commit; provenance is base SHA + dirty flag + diff hash.
2. Compact `robustness_lowrank.json` is distributed; the raw Hydra
   robustness table is not.
3. Lockfile is `pip freeze --exclude-editable` from Python 3.11.15,
   including this machine’s NVIDIA wheels.
4. GDDL 2026 dual-submission/preprint rule is still `[OPEN]`.
5. Pre-existing untracked user files (`.claude/`, talk aux, archived
   `fig_eigenmode`) were left in place.
