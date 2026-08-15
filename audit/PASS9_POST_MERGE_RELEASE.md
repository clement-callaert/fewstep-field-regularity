# PASS 9 post-merge release audit

**Current** release audit of `paper/arxiv/` and `paper/gddl2026/` after
the post-merge related-work and documentation pass on branch
`fix/postmerge-release-finalization`. Audit date: **2026-08-14**.

`audit/PASS7_FINAL_AUDIT.md` and `audit/PASS8_RELEASE.md` are historical
pre-merge snapshots. They were accurate for the states they described.
They are not descriptions of current `main`. See
`audit/STALE_AUDIT_NOTICE.md`.

This file lives in the documentation commit that follows the artifact
commit. It does **not** claim that a tracked PDF contains the SHA of the
commit that first introduces that PDF.

## Outcome

**READY WITH DISCLOSURES.** Local scientific, font, packed-source, and
workshop-constraint checks passed. GitHub Actions on this branch is a
remaining automated gate and is not a substitute for the owner actions
listed below. No `arxiv-v1` tag, GitHub Release, arXiv upload, GDDL
upload, or merge to `main` was performed here.

## Git state at this audit

| Item | Value |
| --- | --- |
| Starting `origin/main` | `25186a5337ae8c85a9367051da24953b80b133a5` |
| Merge recorded there | Pull request #1 (`fix/pass6-polish`) |
| Main Actions run | https://github.com/clement-callaert/fewstep-field-regularity/actions/runs/31822152552 |
| Main Actions result | Success; `cpu-checks` matrix Python 3.11 and Python 3.12 both passed (Node.js 20 deprecation warnings only) |
| Branch | `fix/postmerge-release-finalization` |
| Related-work source | `17a37df54037a881a3997dcf3e864220e901d3a9` |
| Grammar-fix source snapshot used for PDF generation | `3932b48b3a0f61a464230329a9363917e77f8c47` (clean working tree) |
| Artifact-carrier commit | `4a9d5ceea4ceb30e357271c49bf0d23f06ee081f` |
| Tags | no `arxiv-v1`; no GitHub Release |
| arXiv identifier | none |

`origin/main` was fetched at the start of this pass and again before the
artifact commit. It remained `25186a5337ae8c85a9367051da24953b80b133a5`.

## Two-stage provenance

1. Source commits on this branch, from merged `main`:
   - `17a37df` related-work citations in both manuscripts
   - `3932b48` subject-verb agreement on the single-author Iso-FM cite
2. PDFs, `.bbl` files, and `paper/arxiv/arxiv-source.zip` were built from
   clean temporary directories at `3932b48`, then stored in `4a9d5ce`.
3. Figure sidecars, compact JSON, and numerical certificates were **not**
   regenerated. They still record `source_commit = f6bdd65` and
   `working_tree_dirty: true` from the PASS 8 generation. That is
   historical figure provenance, not a new dirty-tree PDF build.
4. This audit file is a later documentation commit. Sidecars and PDFs do
   not contain this file's commit SHA.

TeX used for both rebuilds: pdfTeX 3.141592653-2.6-1.40.22 (TeX Live
2022/dev/Debian), latexmk 4.76. This is the same engine family as PASS 8.
The workshop monospace font in the distributed GDDL PDF is `SFTT1000`
Type 1 (cm-super), embedded, not Type 3.

## PDFs after regeneration

| PDF | pages | excluding references | main-text floats | fonts | metadata |
| --- | --- | --- | --- | --- | --- |
| `paper/arxiv/main.pdf` | 21 | main text through the related-work close on p. 11; refs pp. 11–12; appendix pp. 13–21 | 4 figures, 1 table | embedded Type 1 / CID TrueType; zero Type 3 | named Clément Callaert; affiliation CentraleSupélec and Université Paris-Saclay |
| `paper/gddl2026/main.pdf` | 7 | six pages excluding the bibliography (conclusion ends on p. 6; refs begin p. 6 and continue p. 7; Appendix A occupies the rest of p. 7) | 3 figures, 2 tables | embedded Type 1 / CID TrueType; zero Type 3 | `pdfauthor` empty; body `Anonymous Author(s)` / Affiliation / Address / email |

Workshop long-track rule, confirmed 2026-08-14 from
https://gddl-neurips-2026.github.io/: NeurIPS 2026 template; long papers
5–9 pages excluding references; all submissions anonymized; double-blind
via OpenReview. Compliant. Official style file remains
`neurips_2026.sty` with `[dblblindworkshop]`.

Packed arXiv source: 26 files; clean-directory rebuild 21 pages,
embedded fonts, no Type 3, no `??`. Bitwise PDF identity across TeX
working directories is not required.

## SHA-256 of regenerated files

- `paper/arxiv/main.pdf`:
  `1e003f414684eddc8b284e101f4fb0ac0852c863593d7f51139ea9694966743d`
- `paper/gddl2026/main.pdf`:
  `5aa7d1254da230432e9c09cfc2f7664ba139014add401b1674fac00765bb53a0`
- `paper/arxiv/arxiv-source.zip`:
  `34f88bc3001f6e6ea4fe8d6eb30169e9d9d6c33a56e0bb0335ba2455b80377fb`

These differ from the PASS 8 hashes solely because bibliography and
related-work source changed. Compact JSON, frozen runs, and figure PDFs
were not modified (`git diff origin/main -- paper/arxiv/artifacts
paper/arxiv/figures paper/arxiv/generated` is empty).

## Certificates (not regenerated; independently rechecked)

`python scripts/verify_scalar_counterexample.py` still reports:

- `ranking_inverted`: true
- Linear Heun product `6797469/3559400`; `W_2 = 321331/3559400`
- Integer comparison `19211335367141247013930300 < 19214891013548725548089344`

No theorem statement, numerical table, figure, or compact artifact
changed.

## Scientific diff (claims)

No main claim was strengthened. Title and canonical abstract are
unchanged. Chen et al.'s `A_2` is still not described as a universal
fixed-NFE ranking theorem. The 36-block evaluation remains an explicit
enumeration. The grid-aware result remains an impossibility result in
the stated classes. No learned-field, FID, or production-sampler claim
was added. Optimal transport is not claimed as novel here; Tao and Choi
(arXiv:2605.06680) remain the cited source for vanishing material
derivative and Lagrangian Euler exactness on McCann displacement
interpolation, which is not the independent-coupling linear/VP path.

New citations, bibliographic metadata from the official arXiv Atom
records (retrieved 2026-08-14), all still preprints:

| Cite key | Official title | Authors | arXiv | Where |
| --- | --- | --- | --- | --- |
| `gupta2026sharpen` | Sharpen Your Flow: Sharpness-Aware Sampling for Flow Matching | Aditi Gupta, Soon Hoe Lim, Annan Yu, N. Benjamin Erichson | 2605.11547 | arXiv and GDDL related work |
| `khan2026isofm` | Isokinetic Flow Matching for Pathwise Straightening of Generative Flows | Tauhid Khan | 2604.04491 | arXiv related work |
| `malnick2026otdesign` | Optimal Transport Flow Matching by Design | Shimon Malnick, Matan Rusanovsky, Ohad Fried, Shai Avidan | 2606.04092 | arXiv related work |

The user-facing alias “A Lagrangian Perspective on Flow Matching” for
arXiv:2605.06680 does **not** match the official record. That identifier
is Tao and Choi, already cited. It was not retitled in the bibliography.

Positioning added to related work, adapted to existing prose: complementary
solver-aware methods use temporal information rather than an integrated
spatial-Jacobian energy; SharpEuler calibrates Euler grids from trajectory
acceleration; isokinetic flow matching regularizes material acceleration
during training; other work modifies coupling or prior design toward
straighter OT-like flows; this paper is neither a sampler nor a training
regularizer.

## Metadata consistency

Checked against each other: `paper/arxiv/main.tex`,
`paper/arxiv/ARXIV_METADATA.md`, `docs/ARXIV_SUBMISSION.md`, `README.md`,
`CITATION.cff`.

| Field | Status |
| --- | --- |
| Canonical title | identical; 110 characters; required phrases preserved |
| Abstract | synchronized; 1520 characters in the arXiv form field |
| Categories | primary `cs.LG`; cross-lists `stat.ML`, `math.NA` |
| Comments | still `21 pages, 4 figures, 1 table in the main text` plus the code URL |
| Code URL | `https://github.com/clement-callaert/fewstep-field-regularity` |
| arXiv id | none |
| Named arXiv PDF | Clément Callaert; CentraleSupélec and Université Paris-Saclay; `callaert.clement@gmail.com` |
| ORCID | `0009-0001-6863-8778` in CITATION.cff / ARXIV_METADATA.md / ARXIV_SUBMISSION.md; not inserted into the GDDL PDF |
| Anonymous GDDL PDF | no author name, email, ORCID, GitHub URL, or affiliation |

Owner identity was **not** silently changed. Upload still requires owner
confirmation of that identity.

## Workshop constraints (official CFP, 2026-08-14)

https://gddl-neurips-2026.github.io/

- NeurIPS 2026 template: yes (`neurips_2026.sty`, `dblblindworkshop`)
- Long paper 5–9 pages excluding references: yes (6)
- Anonymous / double-blind: yes in the distributed GDDL PDF
- No acknowledgements, ORCID, repository link, or author block in that PDF
- Non-archival; concurrent or subsequent submission allowed
- Deadline 2026-08-29 AoE remains an owner calendar fact, not a git gate

## Local validation (2026-08-14, Python 3.11.15 venv)

| Command | Exit | Result |
| --- | --- | --- |
| `ruff check src tests scripts` | 0 | All checks passed |
| `ruff format --check src tests scripts` | 0 | 123 files already formatted |
| `mypy --config-file pyproject.toml` | 0 | 66 source files, no issues |
| `python -W error::SyntaxWarning -m compileall -q src scripts tests` | 0 | OK |
| `pytest -q -ra` | 0 | All tests passed; 1 skip (`test_release_tokens_resolved_after_notification` without `FEWSTEP_RELEASE_GATE`) |
| `FEWSTEP_RELEASE_GATE=1 pytest tests/analytical/test_release_gate.py` | 0 | 3 passed |
| `python scripts/verify_scalar_counterexample.py` | 0 | ranking inverted; integer certificate unchanged |
| `python scripts/check_arxiv_placeholder.py` | 0 | no commit placeholder remains |
| `python scripts/check_arxiv_structure.py` | 0 | structure checks passed |
| `python scripts/check_arxiv_release.py` | 0 | scientific checks passed; `arxiv-v1` is the remaining manual gate |
| `FEWSTEP_RELEASE_GATE=1 python scripts/check_release_gate.py` | 0 | release gate passed |
| `python scripts/validate_artifacts.py paper/arxiv/artifacts` | 0 | OK |
| `python scripts/check_pdf_fonts.py` | 0 | both distributed PDFs embedded, no Type 3 |
| `python scripts/pack_arxiv_source.py` | 0 | 26 files; clean compile 21 pages, fonts OK |
| Clean-temp `latexmk` arXiv | 0 | no undefined refs/cites; no overfull hbox/vbox |
| Clean-temp `latexmk` GDDL | 0 | no undefined refs/cites; no overfull hbox/vbox |

## Disclosures

1. `talks/wald-interview-2026-08-21/` is already on public `main`. The
   owner was asked to choose (A) keep it intentionally or (B) remove it
   from the current tip in a dedicated commit. No answer during this
   pass. It was left unchanged. Removing it from the tip would **not**
   purge it from existing Git history. The repository is public; this
   audit does not claim it is private.
2. Author identity confirmation remains an owner action before arXiv
   upload.
3. Merge of this branch, `arxiv-v1` tag, GitHub Release, arXiv deposit,
   and GDDL OpenReview upload remain owner actions.
4. Figure sidecars still flag `working_tree_dirty: true` from PASS 8.
   New PDFs were generated from a clean source snapshot.
5. Compact `robustness_lowrank.json` is distributed; raw
   `phase4_robustness` Hydra tables are not.
6. `requirements-lock.txt` includes this machine’s NVIDIA wheels.
7. Workshop hyperref `draft=true` only when `\pdftexrevision` is 22.
8. The public repository contains the exact paper title. GDDL review is
   double-blind. The published CFP allows concurrent or subsequent
   submission; the NeurIPS 2026 Main Track Handbook states that a
   non-anonymous preprint will not cause rejection if it is not
   advertised aggressively and does not say “Under review at NeurIPS”.
   Title searchability is a process disclosure, not a mathematical
   failure.
9. GitHub Actions on *this* pull request is recorded in the PR, not in
   the SHA of the PDFs.

## Remaining owner decisions

| Decision | Status |
| --- | --- |
| Talk directory keep vs delete-from-tip | Unresolved; left in tree |
| Confirm name / affiliation / email / ORCID | Recorded, not changed |
| Merge this PR to `main` | Not done |
| Create `arxiv-v1` / GitHub Release | Not done |
| arXiv upload | Not done |
| GDDL submission | Not done |

## Files changed on this branch relative to `25186a5`

Manuscript/source: `paper/arxiv/main.tex`, `paper/arxiv/references.bib`,
`paper/gddl2026/main.tex`.

Artifacts: `paper/arxiv/main.pdf`, `paper/arxiv/main.bbl`,
`paper/arxiv/arxiv-source.zip`, `paper/gddl2026/main.pdf`,
`paper/gddl2026/main.bbl`.

Documentation: `audit/PASS9_POST_MERGE_RELEASE.md`,
`audit/STALE_AUDIT_NOTICE.md`, `audit/PASS7_FINAL_AUDIT.md`,
`audit/PASS8_RELEASE.md`, `audit/REPOSITORY_INVENTORY.md`, `README.md`,
`docs/ARXIV_SUBMISSION.md`.
