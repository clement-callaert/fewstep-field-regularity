# Workshop correction report

Date: 2026-07-24. Produced by the correction pass over the workshop paper,
repository presentation, documentation consistency, anonymization, artifact
references, and Git authorship configuration. **The working tree is left
uncommitted for the owner's review; no git write command was executed.**

## 1. Executive verdict

The paper is scientifically corrected within the frozen claims, fits four
main pages under the official NeurIPS 2026 `[dblblindworkshop]` style with
no NeurIPS 2025 footer, uses readable full-width figures with unobtrusive
artifact aliases, and every number was re-verified against its source
artifact. The Claude contributor entry comes solely from two pushed
`Co-Authored-By` trailers; removing it requires a small, message-only
history rewrite that is prepared but not executed. Two submission
blockers remain as owner decisions: repository exposure of the paper
during double blind, and assembling the anonymized supplement bundle.

## 2. Files modified (working tree, uncommitted)

Modified: `README.md`, `.pre-commit-config.yaml`, `docs/AUDIT_REPORT.md`,
`docs/POSTMORTEM.md`, `docs/UNRESOLVED_QUESTIONS.md`,
`docs/WORKSHOP_PAPER_OUTLINE.md`, `paper/gddl2026/main.tex`,
`paper/gddl2026/main.pdf`, three figure PDFs + three sidecars,
`scripts/make_workshop_figures.py`.

Added: `CONTRIBUTING.md`, `README_POST_REVIEW.md`,
`docs/GIT_AUTHORSHIP_AUDIT.md`, `docs/GIT_AUTHORSHIP_CLEANUP_PLAN.md`,
`docs/DOUBLE_BLIND_AUDIT.md`, `docs/DOUBLE_BLIND_FINAL_CHECKLIST.md`,
`docs/REPOSITORY_PUBLICATION_PLAN.md`,
`paper/gddl2026/artifact_aliases.json`,
`scripts/check_commit_attribution.py`,
`scripts/prepare_author_cleanup.sh`,
`tests/unit/test_commit_attribution.py`, this report.

## 3. Scientific wording corrections (Stage 6)

- 6.1 "every quantity is exact" removed; the abstract and Section 2 now
  say endpoint laws and Gaussian $W_2$ are closed-form, the regularity
  integrand is analytically known, and $\mathcal{R}$ is evaluated by
  trapezoidal quadrature; sampling/training/estimation noise absent.
- 6.2 "recovered exactly" → "reconstructed from $d{+}1$ deterministic
  probes"; the float64-versus-80-digit qualification is stated once.
- 6.3 VP citation fixed: "the trigonometric variance-preserving path",
  with Song et al. cited for VP diffusion background only.
- 6.4 Hairer conflation fixed: Lipschitz/stability constants enter
  classical bounds (Hairer); Chen et al. propose the averaged criterion.
- 6.5 Chronology accurate: inversions identified in the registered Phase 3
  benchmark, reproduced in the frozen clean-code Phase 4 grid; the
  non-centered family is the genuinely pre-registered one (11 of 18).
- 6.6 "independent adversarial review" removed from the paper; it now says
  the full proof and edge-case audit are in the supplement. The audit
  language in public-facing READMEs was changed to "documented internal
  adversarial proof audit".
- 6.7 "external validation" → "pre-registered non-centered replication";
  stated as Gaussian, diagonal, commuting, single-family, supporting
  only; $\mathcal{R}$ ignores $c(t)$ by its own definition.
- 6.8 Scope statements preserved: exponential/exact-linear integrators
  solve affine fields exactly; generic fixed-stage RK scope; learned
  fields non-affine but not evaluated; identity time parameterization;
  transfer-based optimization complementary; solver dependence known;
  no refutation of Lipschitz-guided design.
- The post-hoc solver-specific proxy sentence was removed from the paper
  entirely (the safest reading of "do not promote").

## 4. Template corrections (Stage 5, 11; updated 2026-07-24 style swap)

- Official `neurips_2026.sty` is in use with
  `\usepackage[dblblindworkshop]{neurips_2026}` and the GDDL
  `\workshoptitle{…}`. The temporary `neurips_2025` load and manual
  `\@noticestring` override are removed. See Section 17 for retrieval
  provenance.
- `hyperref` configured with `hidelinks` (no colored/boxed links) and
  empty `pdftitle/pdfauthor/pdfsubject/pdfkeywords`.
- Author block: official anonymous placeholder ("Anonymous Author(s)" /
  Affiliation / Address / email); no personal data.
- Main-track `checklist.tex` is not included (GDDL CFP does not require it).

## 5. Figure corrections (Stages 8–10)

- Figure 1 redesigned as a three-panel signed-defect schematic (fields +
  stage samples + averaged scalars; signed defects adding vs cancelling;
  reversed endpoint ranking). The caption labels it "Conceptual schematic,
  not experimental data" and states it illustrates the Section 3
  accounting, not the measured mechanism of any specific inversion.
- Figures are now generated at true column width (5.5 in) so fonts render
  at their natural 8–9 pt size instead of being scaled to ~6 pt.
- Figure 2: hatching distinguishes VP from linear (not color alone),
  marker shape + color encode the preferred path, abbreviated block
  labels (AN/LR, Eu/He/RK), log axis retained with the caption stating it
  compresses magnitudes.
- Figure 3: full column width, thicker lines, larger markers, direct
  solver labels at line ends (no tiny legend), explicit zero line, sign
  convention and symlog linear threshold ($10^{-4}$) explained in the
  caption, "NFE (equal across solvers)" axis label.

## 6. Anonymization corrections (Stages 5, 17)

See `docs/DOUBLE_BLIND_AUDIT.md` and
`docs/DOUBLE_BLIND_FINAL_CHECKLIST.md`. PDF body, metadata, sources, and
references are clean. Remaining fails are repository-level: the public
repo exposes the paper and workshop docs, and the alias manifest/sidecars
contain searchable commit hashes (strip from the uploaded bundle or make
the repo private during review).

## 7. Artifact-alias strategy (Stage 7)

`paper/gddl2026/artifact_aliases.json` maps A1–A7 to full artifact IDs,
SHA-256 checksums, config-hash prefixes, code commits, and release-ready
status. The paper cites only "artifact A1…A5"; full identifiers no longer
appear in captions. All alias rows were verified against the on-disk
manifests and file hashes.

## 8. README strategy (Stage 13)

`README.md` is now venue-silent (active research software, no title, no
venue, no paper numbers, generic reproduction commands).
`README_POST_REVIEW.md` holds the full future landing page (title, hero
result, mechanism, artifact IDs, workshop status, no acceptance claim).
`docs/REPOSITORY_PUBLICATION_PLAN.md` separates safe-before-review,
safe-after-submission, and safe-only-after-notification actions.

## 9. Contributor-audit result (Stage 2)

`docs/GIT_AUTHORSHIP_AUDIT.md`: all 21 commits are authored and committed
by the owner (initial commit committed by GitHub web-flow, normal). Claude
appears **only** as `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`
trailers in `f5e857ca4a74293b26327c612fddf2492bd77d08` and
`508101e759a2a035b194f9a4c56fab28fcac6f39` — classification 3 (AI as
co-author only), both reachable from `main` and pushed. No AI author,
committer, sign-off, bot, stale branch, or tag exists.

## 10. History-rewrite requirement (Stage 3)

Required only if the owner wants the contributor graph cleaned: a
message-only rewrite of the two commits above (trailer deletion), new
hashes for the top 7 commits, verified tree-identity, backup first, then
`git push --force-with-lease`. Prepared, not executed:
`scripts/prepare_author_cleanup.sh` (guarded, print-only) and
`docs/GIT_AUTHORSHIP_CLEANUP_PLAN.md`. Future commits are protected by
`scripts/check_commit_attribution.py` (tested; wired as a pre-commit
`commit-msg` hook — install with
`pre-commit install --hook-type commit-msg`) and the `CONTRIBUTING.md`
policy.

## 11. Tests run (Stage 16)

- `pytest`: all pass (including 9 new attribution-checker tests).
- `ruff check .`: pass. `ruff format --check .`: pass.
- `mypy src`: pass (strict).
- `pre-commit run --all-files`: all hooks pass.
- `git diff --check`: clean.
- LaTeX: `pdflatex`+`bibtex` clean; 0 Overfull boxes; no undefined
  citations; every page rendered to PNG and visually inspected.

## 12. Artifact validations (Stage 16)

`scripts/validate_artifacts.py` passes for all six Phase 4 runs and the
replication run. A dedicated cross-check verified every numerical claim in
the paper against its artifact: 72 rows; 14/36 inversions; strongest
values 2.9476523251 / 4.7295206355 / 0.8108540111 / 0.4564779075; margin
0.3543761036 (77.63% → "78%"); smallest margin 1.1188920612e-5; precision
9.7050430488e-10 (ratio 11,529 > 11,500); NFE 64/128 and perturbation
robustness present; replication 11/18, max deviation 2.068806e-11,
smallest inverted margin 1.423382e-6, metric margin 0.7513; dims/solvers/
NFE as stated. Figure sidecars carry all required fields, matching source
hashes, and matching figure checksums. No figure reads directories; inputs
are pinned by checksum. No rounding changes any comparison.

## 13. Paper page count

Four main pages; References begin at the top of page 5 (five PDF pages
total). Line numbers present (submission mode).

## 14. PDF metadata

`Author`, `Title`, `Subject`, `Keywords`: empty. `Creator`: "LaTeX with
hyperref". `Producer`: "pdfTeX-1.40.22". No identifying content.
`main.pdf` SHA-256 (post–2026 style swap):
`158ef36293c8db8ae994e0d137602c6406e0a98184d571e7170e78cec63adeea`.

## 15. Remaining blockers

Scientific: none within the frozen claims.

Administrative:
1. Repository exposure during double blind (checklist items 11/19) —
   owner decision per `docs/REPOSITORY_PUBLICATION_PLAN.md`.
2. Assemble the anonymized supplement bundle (P4-P1 proof audit, alias
   manifest with `code_commit` stripped, artifact tables).
3. Optional: execute the authorship history rewrite (owner-run only).
4. After committing, regenerate the figures once
   (`python scripts/make_workshop_figures.py` and rebuild the paper) so
   the sidecars record the clean commit instead of
   "dirty (regenerate after committing)".

## 17. Official NeurIPS 2026 style retrieval and swap (2026-07-24)

Branch A completed. Official source only (no third-party mirrors).

| field | value |
| --- | --- |
| CfP page | https://neurips.cc/Conferences/2026/CallForPapers (“Paper template”) |
| Download URL | https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip |
| Zip SHA-256 | `82473931e3ef710fcd3f4a8cd4119b9de32e56825f90f9e5a6d55f2d01b817d9` |
| `neurips_2026.sty` SHA-256 | `c3fc2894e83d2517ca18b66741d6c595986d97957dc08ec08bb2125a7ec4555a` |
| Retrieved (UTC) | 2026-07-24T18:17:44Z |
| Package options | `[dblblindworkshop]` |
| Workshop title | Geometric Distributional Deep Learning: Bridging Optimal Transport, Learning and Structured Data |
| `checklist.tex` | present in the official zip; **not** loaded in `main.tex` |

Other probed official paths (not used): `…/Styles/neurips_2026.sty` 404;
`…/Styles/` 404; `…/PaperInformation/StyleFiles` 404.

Validation: sty defines `dblblindworkshop` and `\workshoptitle`. Rebuild:
5 PDF pages; body ends page 4; References start page 5; 0 Overfull boxes;
empty Author/Title/Subject/Keywords metadata; link borders `[0,0,0]`
(hidelinks); no “39th” / “NeurIPS 2025” strings; figures legible on pages
2–4. Official submission-mode footer is the conference-wide notice
“Submitted to 40th Conference on Neural Information Processing Systems
(NeurIPS 2026). Do not distribute.” — the sty inserts `\@workshoptitle`
into the footnote only under `[final]` (camera-ready). `\workshoptitle`
is set correctly in source for that camera-ready path.

## 16. Exact commands for the owner (nothing below was executed)

Normal content commit:

```bash
git diff --check
git status
git diff
git add <reviewed files>
git commit -m "<reviewed message>"
git push origin main
```

Post-commit provenance refresh (then amend or follow-up commit as you
prefer — as a separate, reviewed action):

```bash
python scripts/make_workshop_figures.py
(cd paper/gddl2026 && pdflatex main && bibtex main && pdflatex main && pdflatex main)
```

Separate, clearly marked history rewrite (only if desired; see
`docs/GIT_AUTHORSHIP_CLEANUP_PLAN.md`; do **not** combine with the content
commit):

```bash
git clone --mirror https://github.com/clement-callaert/fewstep-field-regularity.git ../fewstep-field-regularity-backup.git
OLD_MAIN=$(git rev-parse main)
CLEMENT_NAME="Clément Callaert" CLEMENT_EMAIL="<your commit email>" bash scripts/prepare_author_cleanup.sh
# then run the filter-repo command it prints, verify per the plan, and only after
# explicit approval and collaborator clearance:
git push --force-with-lease origin main
```
