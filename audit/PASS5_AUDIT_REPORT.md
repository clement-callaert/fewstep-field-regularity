# Pass-5 correction audit

**Copy:** `/tmp/fewstep-pass5-20260813`  
**Source archive:** `/tmp/fewstep-corrected-20260813.zip`  
**sha256:** `9a4c13bd64e8c67124ec1691003e3fa61c3b7e49b317b8349c7357191bfc6200`  
**Not done:** commit, push, tag, arXiv upload, OpenReview submit.

Gate logs: `audit/gates/`. Unified source diffs: `audit/diffs/pass5_*.diff`.

---

## 1. Starting PDFs (this build)

Confirmed **current** title:
*Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching Schedules: A Certified Gaussian Counterexample*.

| PDF | sha256 | pages |
| --- | --- | --- |
| `paper/arxiv/main.pdf` (start) | `887c1f0336ecb4a4718717aa7a1da274205d42b8a7e60745da0977d3c243cb38` | 22, A4 |
| `paper/gddl2026/main.pdf` (start) | `ee31e939ec4dbb2a669b5b120223017d8ba222f77034d9f949d640b105fa26ba` | 7, letter |

These match the prompt. Stale PDFs with the older title were ignored.

Confirmed defects on that build:

- ArXiv last words: “The 80-digit Gelbrich audit occupies the” then EOF. `pdftotext` shows `Phase224`.
- Workshop: folio `7` through “Machin’s formula”. Final sentence present; collision real.
- Original bbox: arXiv p.22 body `yMax=844.3 > height=841.9`; workshop p.7 `formula` overlaps folio `7`.

---

## 2. Modified files

Full unified diffs: `audit/diffs/pass5_*.diff`. Compact JSON artifacts did **not** change.

### Source / docs / tests

| File | What changed |
| --- | --- |
| `paper/arxiv/main.tex` | Deleted `\enlargethispage{12\baselineskip}`; grouped Tables 9–12 `[H]` → `[ht]`. Appendix `\newgeometry{margin=1.15in}` left in place. |
| `paper/gddl2026/main.tex` | Deleted `\enlargethispage{8\baselineskip}`. Stock NeurIPS footer and `\workshoptitle` untouched. Official `neurips_2026.sty` `\enlargethispage{2\baselineskip}` untouched. |
| `paper/arxiv/ARXIV_METADATA.md` | Comments **23 pages** |
| `docs/ARXIV_SUBMISSION.md` | Comments **23 pages** |
| `scripts/make_arxiv_figures.py` | Fig 1 (`fig_scalar`) annotations: black text, white bbox, above the shorter bar, arrow to the outer bar face; panel (c) points at `lin`; `xlim`/`ylim` headroom; no series-coloured labels |
| `scripts/make_workshop_figures.py` | Stopped writing unreferenced `fig1_conceptual.pdf`; Hydra skip unchanged |
| `scripts/pack_arxiv_source.py` | Last-page needle; folio/overflow bbox gate (HTML y-down, sequential pages); refuse `fig1_conceptual.pdf`; pack only `\includegraphics` PDFs |
| `tests/analytical/test_pdf_completeness.py` | **New.** 7 tests: last-page needles, folio/overflow, fonts on both PDFs, dead conceptual fig, pack membership, no `\enlargethispage` in live `main.tex` |

### Regenerated / deleted binaries

| File | Note |
| --- | --- |
| `paper/arxiv/figures/fig_scalar.pdf` (+ `.json`) | Regenerated. sha256 `2a10b7461b432543e460476aea4b99207ec060484cbc74b64ba5da5c6123dd7a` |
| `paper/gddl2026/figures/fig_scalar.pdf` | Same bytes as the arXiv figure |
| `paper/arxiv/figures/fig1_regimes.pdf`, `fig_four_paths.pdf` | Regenerated, **bit-identical** to the archive |
| `paper/arxiv/figures/fig1_conceptual.pdf` (+ `.json`) | **Deleted** (unreferenced) |
| `paper/gddl2026/figures/fig1_conceptual.pdf` (+ `.json`) | **Deleted** (unreferenced) |
| `paper/arxiv/main.pdf`, `paper/gddl2026/main.pdf` | Rebuilt after the figure fix |
| `paper/arxiv/arxiv-source.zip` | Repacked; clean compile 23 pages |

### Unchanged (required)

All 10 files in `paper/arxiv/artifacts/*.json` are **bit-identical** to the archive. All 15 `paper/arxiv/generated/*.tex` files are **bit-identical**.

---

## 3. Defect table

| Defect | Evidence of the defect | Correction | Evidence of the correction |
| --- | --- | --- | --- |
| **1 CRITICAL** Preprint ends mid-sentence | Archive last words: “The 80-digit Gelbrich audit occupies the”. Source continues with footnote, GitHub URL, three closing sentences. Cause: `\enlargethispage{12\baselineskip}` at former line 1220. `latexmk` reported 0 Overfull. | Delete that line. Accept **23 pages**. Comments fields updated. | Last page text includes `https://github.com/clement-callaert/fewstep-field-regularity`, footnote `outputs/phase4_precision_2026-07-24-v1/`, and “Tag existence is a manual publication gate, not a scientific failure of this manuscript.” 23 pages. |
| **2 CRITICAL** Folio printed through body text | ArXiv p.22: `Phase224`. Workshop p.7: `for`+`7`+`ula`. | Same deletions. Workshop becomes **8 pages** (GDDL long track 5–9 excluding references). | ArXiv p.22 folio clear of “Phase 4”. Workshop p.7 folio clear of “Machin’s formula” (that sentence now sits on p.8). Bbox gate: original PDFs **FAIL**, corrected PDFs **PASS**. |
| **3 MAJOR** Fig 1 annotations overprint bars / clip | Panel (b): orange “R prefers VP” on the blue bar. Panel (c): blue “W2 prefers lin” on the orange bar, clipped at the frame. | Black text, white bbox, placed **above** the shorter bar; arrow to the outer face; panel (c) points at `lin`; `xlim (-0.85, 1.85)`, `ylim` ×1.48. | Raster of `fig_scalar.pdf` and preprint p.2 / workshop p.3: labels above the shorter bars; values `0.963` / `0.617` / `0.090` / `0.130` free; no clip. |
| **4 MINOR** No gate detects truncation | Page count, fonts, and `??` all green on the truncated 22-page PDF. | Last-page needle `fewstep-field-regularity` (arxiv) / `cross-check, not the proof` (workshop). Overflow: `yMax > page height`. Folio overlap in the footer band. Tests + packer. | `pack_arxiv_source.py`: `clean compile passed: 23 pages, embedded fonts, no Type 3`. Original 22-page PDF fails the new gate. |
| **5a MINOR** Dead `fig1_conceptual.pdf` | Present in both `figures/` trees; referenced by neither `main.tex`. | Deleted both PDFs and JSON sidecars; workshop `main()` no longer writes it; packer errors if it reappears. | Files absent. Pack membership equals `\includegraphics` names. |
| **5b MINOR** Font gate not on workshop | `check_pdf_fonts.py` only ran from the arXiv packer. | Tests call it on **both** PDFs. Workshop README already documents the command. | `fonts ok (embedded, no Type 3)` both PDFs. |

The first version of the folio gate was a no-op on this poppler (`<page>` tags have no `number=`). It is now sequential + HTML y-down + footer band, and it **fails the archive PDFs** for the named collisions.

---

## 4. Gate log (from the copy, archive-only)

Python: `/home/calla/AI_projects/fewstep-field-regularity/.venv/bin/python`  
`PYTHONPATH=/tmp/fewstep-pass5-20260813/src`  
Torch-free: `/tmp/fewstep-notorch`  
`SOURCE_DATE_EPOCH=1786579200` `FORCE_SOURCE_DATE=1`

| Gate | Result | Skip / note |
| --- | --- | --- |
| `pytest -q -ra` | **225 passed, 1 skipped**, EXIT 0 | Skip: `tests/analytical/test_release_gate.py:46` — `FEWSTEP_RELEASE_GATE` after GDDL notification. Justified. Baseline was 218+1; **+7** completeness tests. |
| `verify_scalar_counterexample.py` | EXIT 0; `ranking_inverted: true`; `R_lin=0.9634954084936207`; `R_VP=0.6168502750680849`; `321331/3559400`; integer certificate identical | venv **with** torch |
| same, torch **absent** | EXIT 0; `torch` never in `sys.modules` | `/tmp/fewstep-notorch` |
| `run_log_covariance_comparison.py` | `36/36` | |
| `run_in_family_comparison.py` | `9` inversions, `4` cells | |
| `run_inversion_region.py` | Heun λ=4 all budgets; Euler λ=4 absent; RK4 NFE 8/12 absent | matplotlib `SOURCE_DATE_EPOCH` timestamp warnings only |
| `run_lowrank_seed_fraction.py` | `50/50` both `d`; interval `(0.929, 1.000)` | |
| `run_arxiv_stats.py` | paired concordance `0.2222…` (`2/9`); Clopper–Pearson `[0.928878…, 1.0]`; Heun-8 log-Lebesgue `3.337` | |
| `make_arxiv_figures.py` | EXIT 0 | Hydra skip: `fig2_inversions, fig_eigenmode, fig3_interaction, fig_noncentered` — `outputs/` not in the public snapshot. Justified. |
| `make_workshop_figures.py` | EXIT 0 | Hydra skip: `fig2_inversions, fig3_interaction`. Justified. No conceptual fig. |
| `make_arxiv_tables.py` | EXIT 0; inversions 14, noncentered 11, robust 66 | Generated `.tex` bit-identical to archive |
| `validate_artifacts.py paper/arxiv/artifacts` | `OK: paper/arxiv/artifacts` | |
| `pack_arxiv_source.py` | `wrote … arxiv-source.zip files 25`; clean compile **23 pages**, embedded, no Type 3, last-page needle, folio/overflow | |
| `check_pdf_fonts.py` | both PDFs OK | |
| `check_arxiv_placeholder` | `no commit placeholder remains` | |
| `check_arxiv_release` | passed; tag `arxiv-v1` remains a **manual** publication gate | |
| `check_arxiv_structure` | passed | |
| `latexmk` arXiv | 23 pp, **0 Overfull**, no `??` | A4 |
| `latexmk` GDDL | 8 pp, **0 Overfull**, no `??` | letter; Author empty; stock NeurIPS workshop footer |

---

## 5. Final PDFs

| PDF | sha256 | pages |
| --- | --- | --- |
| `paper/arxiv/main.pdf` | `6837db257813e69f6c1f9f8f21163b5186fb1310969922feadbf21eb58b39927` | **23**, A4 |
| `paper/gddl2026/main.pdf` | `c618140ddfa5b4784a372704d6eb59e71b1d2ebb47973a8ee540a52efa60b934` | **8**, letter |

Comments field in **both** `paper/arxiv/ARXIV_METADATA.md` line 52 and `docs/ARXIV_SUBMISSION.md` line 58:

```
23 pages, 4 figures, 2 tables in the main text. Code and compact artifacts: https://github.com/clement-callaert/fewstep-field-regularity
```

---

## 6. Last non-empty extracted lines (documents complete)

`pdftotext` last token is the folio. Last **content** line, then the closing block.

**ArXiv, last page (23), last content line:**

```
Path outputs/phase4_precision_2026-07-24-v1/, not part of the public snapshot.
```

Closing block of that page (verbatim from `pdftotext`):

```
frozen Hydra tree when that tree is present.1 Source:
https://github.com/clement-callaert/fewstep-field-regularity. The placeholder check
must pass with no retired commit token remaining. The release check verifies compact checksums.
Tag existence is a manual publication gate, not a scientific failure of this manuscript.

1

Path outputs/phase4_precision_2026-07-24-v1/, not part of the public snapshot.

23
```

**Workshop, last page (8), last content line:**

```
cross-check, not the proof.
```

Closing block:

```
Hence rVP < 187/100 and W2VP > 13/100. The bound 2 < 99/70 is 992 − 2 · 702 = 1. The
bound π < 355/113 follows from Machin’s formula with Leibniz remainders (seven Taylor terms
for arctan(1/5), four for arctan(1/239)). An independent mpmath 1.3.0 interval enclosure is a
cross-check, not the proof.

8
```

(Line numbers 212–215 in the left margin are the NeurIPS `lineno` draft overlay, not truncation.)

---

## 7. Section 1 values unchanged

Artifact JSON diff vs the starting zip: **10/10 IDENTICAL**. Generated TeX: **15/15 IDENTICAL**.

Certificate and census numbers from the re-run gates match §1.1–1.4: `R_lin`, `R_VP`, Heun product, `W2_lin=321331/3559400=0.0902767320335`, integer comparison, `36/36`, `9/4`, concordance `2/9=0.2222…`, geometry `1/3, 5/9, -1/3, 1/3` with `n=9`, solver `1/2, -1/3, 1/2` with `n=12`, Clopper–Pearson `[0.92888, 1]`, Heun λ=4 inverts at the listed NFEs, RK4 absent at 8 and 12.

Hand arithmetic:

- `99² − 2·70² = 1`
- `192113353671412470139303 × 100 < 187 × 102753427879939708813312`
- `(n_agree − n_invert)/n = −1/3` is possible for `n=12` (4 vs 8) and for `n=9` (3 vs 6); **not** for `n=4`

---

## 8. Page-by-page visual inspection

Rasters: `/tmp/pass5-pages/arxiv/p-01.png` … `p-23.png` and `/tmp/pass5-pages/gddl/p-1.png` … `p-8.png`, 100 dpi. Figures also rastered at 150 dpi under `/tmp/pass5-fig/`.

Normal page-break mid-sentences are **not** truncation.

### Preprint (`paper/arxiv/main.pdf`, 23 pages)

| Page | Looked at | Result |
| --- | --- | --- |
| 1 | Title, abstract, intro | Current title. Author/email present (non-anonymous preprint). Folio 1 clear. |
| 2 | Figure 1 | Panel titles above axes. Annotations above shorter bars, black, white bbox. Arrow on (c) at `lin`. Values 0.963 / 0.617 / 0.090 / 0.130. No clip. |
| 3 | Figure 2 | `Ex. 3.3` **no backslash**. W2 `0.0226` vs `0.0262`. Four-path row 2.94 / 4.73 / 11.4 / 2.24. |
| 4 | Classes S/Q/R | Clean. |
| 5 | Solvers, Gelbrich, A2 | Clean. |
| 6 | Prop. 1, Chen Ex. 3.3 wording | Clean. No stray backslash. |
| 7 | Prop. 2 fractions | `5π/8−1`, `π²/16`, `6797469/3559400`, `321331/3559400`. Folio 7 clear. |
| 8 | Three regimes, setup | Clean. |
| 9 | Table 1, §4.3 | `n = 12` / `n = 9`; Heun `−1/3`. `Ex. 3.3` in the table. |
| 10 | Figure 3 | Legend `Ex. 3.3`. 36 of 36 wording. |
| 11 | Figure 4 heat maps | λ=4 dashed line. Clopper–Pearson `[0.929, 1.000]`. |
| 12 | Table 2, related work | `50/50`, `[0.929, 1.000]`. |
| 13 | Conclusion, limitations, refs start | Clean. |
| 14 | References | Clean. Folio well below last entry. |
| 15 | Appendix A | Heun factors 47/52, 6/5, 497/370, 97/74. Polynomial present. Page-break mid-sentence is a normal break. |
| 16 | Machin / App. B / App. C | `π<355/113`, Pell `99²−2·70²=1`. Integer comparison. Grid-aware Euler. Folio 16 clear of Machin. |
| 17 | Class S embedding, Table 3 | 14 inverted rows. |
| 18 | Tables 4, Figures 5–6 | Strongest-block numbers 2.9441044083 vs 4.7305438136. |
| 19 | Tables 5–6 | 36 of 36; 9 of 36 / 4 of 12. |
| 20 | Figure 7, App. F | `n=12` / `n=9` in the following page; this page clean. |
| 21 | Tables 7–8, concordance prose | `n=12` `+1/2`, `−1/3`; `n=9` `1/3, 5/9, −1/3, 1/3`. |
| 22 | Tables 9–12, start of H | Table 12 caption: geometry `n=9`, solver `n=12`. Folio **22 not** through “Phase 4”. Last word on this page is a normal break (“Compact”). |
| 23 | Rest of Appendix H | Complete: footnote, GitHub URL, placeholder/release/tag sentences. Sparse (~one paragraph). Folio 23 clear. **Accepted.** |

### Workshop (`paper/gddl2026/main.pdf`, 8 pages)

| Page | Looked at | Result |
| --- | --- | --- |
| 1 | Title, anonymous authors, abstract, intro | Stock NeurIPS footer “Submitted to 40th Conference… Do not distribute.” **Not a defect.** No folio on p.1 (template). Line numbers: `lineno`. |
| 2 | Classes, Prop. 1 | `Ex. 3.3` clean. Fractions match. Folio 2 clear. |
| 3 | Figure 1 | Same annotation fix as the preprint. Folio 3 clear. |
| 4 | Figure 2, Table 1 | `Ex. 3.3` no backslash. W2 `0.0226` vs `0.0262`. R values 0.972 / 0.192 / 0.173 / 0.120 and low-rank 2.944 / 4.731 / 11.419 / 2.244. |
| 5 | Table 2, Figure 3, Class S Euler | Strongest-block numbers. Heat maps. Folio 5 clear. |
| 6 | Related work, limitations, conclusion, refs start | `9 of 36`, `36 of 36`. Folio 6 clear. |
| 7 | Refs continue, Appendix A start | Polynomial, integer comparison. Folio **7 not** on “Machin’s formula”. |
| 8 | Appendix remainder | Machin’s formula intact. Ends “cross-check, not the proof.” Sparse. Folio 8 clear. **Accepted.** |

### Regenerated figures (standalone rasters)

`fig_scalar`, `fig1_regimes`, `fig_four_paths`, `fig_inversion_region`: no overprint, no clip, no `Ex.\ `.

### Matplotlib label sweep

AST walk of string constants in `scripts/*.py` and `src/**/*.py`. After stripping `$...$`, remaining `\command` hits are **LaTeX table generators** (`\toprule`, `\begin{tabular}`) and **regexes**, not matplotlib labels. `make_arxiv_figures.py` / `make_workshop_figures.py`: no `Ex.\ 3.3`; remaining TeX is inside `$...$`.

---

## 9. Remaining open items

Owner actions, not fixed here:

- `CITATION.cff` still has `orcid: TODO-ORCID`.
- PDF / `CITATION.cff` still carry a personal Gmail; institutional address preferable.
- NeurIPS checklist: `[OWNER DECISION]` until GDDL organizers confirm in writing.
- Timing of the arXiv deposit vs the double-blind window.
- Tag `arxiv-v1` / GitHub Release / Zenodo: still a **manual publication gate**.
- `pyproject.toml` says MIT; no `LICENSE` file.

Non-blocking leftovers:

- `paper/arxiv/figures/fig2_inversions.pdf` is still on disk, **not** referenced by `main.tex`, **not** packed. Hydra leftover. Packer already omits unreferenced figures.
- `figure1_conceptual()` still exists unused in `make_workshop_figures.py`; `main()` does not call it.
- Last pages are sparse (arxiv p.23, workshop p.8). That is the legitimate alternative to `\enlargethispage`. Do not cram again.
- Workshop p.1 has no folio (NeurIPS first-page style).

---

## 10. Verdicts

| Axis | Verdict |
| --- | --- |
| **SCIENTIFIC_TRUTH** | **PASS**. Section 1 values, classes, quantifiers, and certificate untouched. Artifacts bit-identical. |
| **PUBLIC_REPRODUCIBILITY** | **PASS**. 225 passed, 1 justified skip. Torch-free cert. Compact artifacts validate. Hydra skips documented. |
| **ARXIV_READY** | **PASS** as a *typeset preprint ready for an owner upload decision*. 23 pages, complete last page, 0 Overfull, no `??`, fonts embedded, no Type 3, Comments field matches. **Not uploaded.** Blocked only by owner items (ORCID, email, deposit timing, release tag). |
| **GDDL_READY** | **PASS** as a *typeset anonymous workshop PDF ready for an owner OpenReview decision*. 8 pages, long track 5–9 excluding references, appendix complete, folio clean. **Not submitted.** Blocked only by owner items (checklist confirmation, preprint-timing policy). |

A green `pytest`, a clean `latexmk`, and a matching page count were treated as necessary, not sufficient. Completeness was checked by extracted last-page text, bbox overflow, and looking at every rendered page.
