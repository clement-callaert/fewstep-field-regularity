# PASS 8 release audit

Current audit of `paper/arxiv/` and `paper/gddl2026/` after the bounded
release pass. `PASS7_FINAL_AUDIT.md` is historical (commit `44bc8fe`).
See `STALE_AUDIT_NOTICE.md`.

This file lives in the artifact-carrier commit. It does **not** contain
that commit’s own SHA. Generated PDFs, sidecars, compact artifacts, and
`arxiv-source.zip` were produced from source commit

`f6bdd65d4eddb2bfb5abf519c2f62241ea4fba64`

(`source_commit` / `base_commit` in provenance records). A subsequent
source patch `a815084` annotates compact-manifest hashing helpers for mypy; it does
not change generated scientific outputs. `working_tree_dirty: true` at
generation time because untracked local files (`.claude/`, talk aux,
archived `fig_eigenmode`) were present and were not deleted.

## Outcome

**READY WITH DISCLOSURES** pending owner decisions (Wald-talk directory;
identity confirmation; merge authorization) and GitHub Actions on the
pull request. No tag, GitHub Release, arXiv upload, GDDL submit, or merge
to `main` was performed here.

## Two-stage provenance

1. Source commits on `fix/pass6-polish` after `44bc8fe`:
   - `e51803d` editorial source (abstract, intro, appendix, Lipschitzness wording)
   - `f6bdd65` Ruff lint/format so CI can run
   - `a815084` mypy annotation patch on `src/fewstep_regularities/utils/hashing.py`
2. This artifact-carrier commit stores PDFs, tables, compact JSON, figure
   sidecars, the packed arXiv source, and this audit.
3. Sidecars record `source_commit = f6bdd65`. They do not claim to know
   the SHA of the commit that contains them.

## PDFs

| PDF | pages | excluding references | fonts | anonymity |
| --- | --- | --- | --- | --- |
| `paper/arxiv/main.pdf` | 21 | main text pp. 1–11; refs begin p. 11 and continue p. 12; appendix pp. 13–21 | embedded, no Type 3 | named Clément Callaert |
| `paper/gddl2026/main.pdf` | 7 | six pages excluding the bibliography (main text occupies pp. 1–6; refs begin p. 6 and continue p. 7; Appendix A occupies the rest of p. 7) | embedded, no Type 3 | `pdfauthor` empty |

Workshop long-track rule is 5–9 pages excluding references. Compliant.

Main-text floats (arXiv): 4 figures, 1 table.

Plain-text abstract: 1,520 characters, 213 whitespace-delimited words.

## Certificates (regenerated from `f6bdd65`)

- Ranking inverted: true
- Linear Heun product `6797469/3559400`; `W_2 = 321331/3559400`
- VP Heun product ≈ `1.8696263417`; certified `r_VP < 187/100`; `W_2 > 0.13`
- Grid-aware: 12 records, 5 inverted, 0 endpoint mismatches
- Four-path: 36/36
- VP vs Chen Ex. 3.3: 9 inversions, 4 cells

## SHA-256 of generated files in this commit

- `paper/arxiv/main.pdf`:
  `886e02b224a56d1a4a8471f169b4ba6e728da8804f67ca0a27e8ca2691689350`
- `paper/gddl2026/main.pdf`:
  `af780f36b28a4bfde34c99157740a1d36c9fd159a1a0c837ed93f65e87d8190a`
- `paper/arxiv/arxiv-source.zip`:
  `3521f95e5ac432b342d3fb6e62e65499bd65d50e852f9102594adb1bdf0c7f53`

Packed-source rebuild: 21 pages, embedded fonts, no Type 3, no `??`.
Bitwise PDF identity across TeX working directories is not required.

## Disclosures

1. Untracked local files made generation `working_tree_dirty: true`.
2. Compact `robustness_lowrank.json` is distributed; raw Hydra robustness
   tables are not.
3. Lockfile includes this machine’s NVIDIA wheels.
4. Workshop hyperref `draft=true` only on pdfTeX 1.40.22.
5. `talks/wald-interview-2026-08-21/` is in the branch history; merge to
   `main` is an owner decision.
6. Tag `arxiv-v1` does not exist (owner action).
7. Default `pytest` skips the optional release-gate test until
   `FEWSTEP_RELEASE_GATE=1`.
