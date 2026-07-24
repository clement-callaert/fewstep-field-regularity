# Repository publication plan

Date: 2026-07-24. Owner-only actions; nothing here is automatic. The plan
separates what is safe at each stage of the double-blind lifecycle. It
never authorizes an accepted-paper claim.

## Safe before review (now)

- Keep `README.md` in its venue-silent form: active research software,
  continuous-time generative models, regularity and fixed-budget
  discretization, exact Gaussian and calibrated mixture test cases,
  reproducibility-first design, generic reproduction commands, no exact
  workshop title, no venue, no paper PDF, no identifying artifact bundle.
- **Decide the paper-exposure blocker** (see `docs/DOUBLE_BLIND_AUDIT.md`):
  the public repo currently contains `paper/` with the exact title and
  the identifying workshop documents under `docs/WORKSHOP_*`. Options:
  1. Make the repository private for the review window (recommended;
     simplest, reversible, also resolves artifact-ID searchability).
  2. Remove `paper/` and the `WORKSHOP_*` docs from the public tree
     before submission; note they remain in git history unless the
     (already planned) history rewrite also drops them — weigh carefully.
  3. Accept exposure where the venue's policy tolerates concurrent
     public preprints; this weakens blindness and is not recommended.
- LICENSE audit: confirm the intended license file exists and matches the
  owner's intent before any wider publicity.
- Do not add repository description/topics that echo the paper title.

## Safe after submission (before notification)

- Keep everything above unchanged; the submission deadline does not end
  the blind.
- Internal-only: tag (locally, unpushed if the repo is public) the exact
  submitted state for later reference.
- Recheck the workshop CFP one week before the deadline (template
  version, appendix policy, dual-submission policy) per
  `docs/WORKSHOP_TARGETS.md`.

## Safe only after notification

- Swap `README_POST_REVIEW.md` content into `README.md` (owner decision;
  it contains the paper title, hero result, strongest inversion,
  mechanism, figures, full reproduction commands, artifact IDs, and
  workshop status — still no acceptance claim unless and until true, and
  then only with the wording the venue permits).
- Restore repository visibility to public if it was made private.
- Add repository description and suggested topics (e.g.,
  `generative-models`, `numerical-analysis`, `optimal-transport`,
  `reproducibility`).
- Draft `CITATION.cff` naming the owner and the workshop paper with its
  final status; do not cite it as archival (the workshop is
  non-archival).
- Release checklist: create a versioned release/tag of the submitted and
  camera-ready states; attach the audit bundle (artifact tables,
  manifests, alias map) as release assets; verify all checksums after
  upload.
- Badges (CI, license) may be added at any point; result badges never.
- Artifact release structure: `outputs/<run_id>/` trees with manifests,
  plus `paper/gddl2026/artifact_aliases.json` mapping the paper's A1–A5
  aliases; the released copy may restore `code_commit` fields once
  anonymity no longer applies.
