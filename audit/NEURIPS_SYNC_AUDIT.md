# NeurIPS 2026 GDDL sync audit

Date: 2026-08-13.
Phase B is activated only because Phase A issued `SCIENTIFIC_READY` in `audit/FINAL_ARXIV_AUDIT.md`.

## Live source versus archive

| Path | Role |
| --- | --- |
| `paper/gddl2026/` | **Live** anonymous workshop source. Edited in this repair. |
| `paper/archive/gddl2026-conference/` | Historical short draft. Not edited in place. |

## GDDL constraints

| Constraint | Status |
| --- | --- |
| NeurIPS 2026 `dblblindworkshop` (not `final`) | `[VERIFIED]` in `paper/gddl2026/main.tex` |
| Long paper 5–9 pages excluding references | `[VERIFIED]` 5 body pages + 1 references page (6 pages total) |
| Double-blind: no Clément Callaert name, email, GitHub username, or public repo URL | `[VERIFIED]` by `pdftotext` on `main.pdf` and `supplement.pdf` and by `test_gddl_workshop_source_is_anonymous` |
| No “under review” | `[VERIFIED]` |
| Official style footer | Expected: “Submitted to 40th Conference on Neural Information Processing Systems (NeurIPS 2026). Do not distribute.” This is the NeurIPS 2026 submission footer from `neurips_2026.sty`, not camera-ready mode. |
| Type 3 font | `[OPEN]` as a workshop-template fact, not a scientific leak: `pdffonts` reports one Type 3 face from the `lineno` package in non-final NeurIPS mode. Camera-ready (`final`) would remove it; that mode was not used. |
| Anonymous author block | Official style replaces `\author` with “Anonymous Author(s) / Affiliation / Address / email”. Appropriate for double-blind, not a deanonymizing sentence. |

## Scientific subset synchronized (not stronger than arXiv)

| Item | Workshop location | arXiv counterpart |
| --- | --- | --- |
| Certified scalar Gaussian Heun counterexample as the lead | Sec. 3, Prop. 1, Fig. scalar | Prop. 1 |
| Corrected completing-square identities | Prop. 1 proof sketch | App. A |
| Exact VP grid and rational enclosure $r_{\mathrm{VP}}<187/100$ | Prop. 1; integer comparison in anonymous supplement | App. A |
| Continuous $\cR$ as headline; $\widehat R_{24}$ as check | Sec. 2 and Table 1 | Sec. 2 and Table 1 |
| Strongest-row continuous $R$ $2.9441044083$ vs $4.7305438136$ | Table 1 | Table 1 |
| $4$ geometries $\times$ $9$ solver-budget conditions | Sec. 4 | benchmark section |
| 14/36 and 11/18 descriptive, not iid | abstract and Sec. 4 | abstract |
| Non-centered construction, $\Delta$ definitions, mean/cov drivers | Sec. 4 | non-centered section |
| Covariance drift independent of $c(t)$ | Sec. 2 | Sec. 2 |
| Chen et al. pairwise-ranking caveat | intro and limitations | intro and limitations |
| Restored Euler analytical proof | Sec. 5 | App. D |
| Same limitations | last section | limitations |
| Bulky integer certificate | `supplement.tex` (anonymous) | App. A / generated macros |

Workshop claims that were **not** added: no learned-field result, no population rate, no refutation of Chen et al., no stronger numerical bound than $187/100$.

## Diff summary

### arXiv-only

- Full 14-page manuscript with appendices, exhaustive inversion tables, signed-$\Delta$ table, quadrature table, robustness appendix, public author/email, GitHub release URL based on tag `arxiv-v1`, compact artefacts, Figure 4 (non-centered signed $\Delta$).
- `paper/arxiv/` generated macros and `arxiv-source.zip`.
- Public reproducibility scripts and checksums.

### NeurIPS-synchronized scientific changes

- New live tree `paper/gddl2026/` (copy of the archive plus arXiv `fig_scalar.pdf` and scientific repairs).
- Scalar Heun as the leading existence result with the corrected identities and rational certificate.
- Continuous $R$ in Table 1; $\widehat R_{24}$ labeled as a check.
- Hierarchical 4×9 wording; descriptive 14/36 and 11/18.
- Specified non-centered family and $\Delta$ drivers (no crushed Figure 4 in the workshop body; that figure remains arXiv-only).
- Chen caveat; restored Euler proof; expanded related work to match arXiv limitations.
- Anonymous supplement with the integer comparison only.

### Generated artefacts

- arXiv compact JSON/TeX under `paper/arxiv/generated/` and `paper/arxiv/artifacts/`.
- Workshop PDFs `paper/gddl2026/main.pdf` and `supplement.pdf` (compiled locally).
- LaTeX intermediates are gitignored in `paper/gddl2026/.gitignore`.

### Manual actions remaining (owner)

- Create tag `arxiv-v1` on the final scientific commit.
- Publish GitHub Release or Zenodo from that tag.
- Choose arXiv licence (`paper/arxiv/ARXIV_METADATA.md`).
- Resolve MIT in `pyproject.toml` versus missing `LICENSE`.
- Push, arXiv upload, endorsement if needed.
- Workshop submission of the anonymous PDFs; do not include the public GitHub URL.

## Anonymization grep (compiled PDFs)

Forbidden strings with count 0 in `main.pdf` and `supplement.pdf`:

- `Clément`
- `Callaert`
- `callaert.clement`
- `clement-callaert`
- `github.com/clement`
- `under review`

`Anonymous` appears only in the official author block / supplement title.

## Page count

- Workshop body: 5 pages excluding references (minimum of the 5–9 long-paper window).
- References: page 6.
- Supplement: 1 page.

Two underfull vboxes in the workshop log; zero overfull boxes; no undefined references.
