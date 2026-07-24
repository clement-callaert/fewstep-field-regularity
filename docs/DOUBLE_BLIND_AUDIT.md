# Double-blind audit

Date: 2026-07-24. Scope: the workshop submission bundle
(`paper/gddl2026/main.pdf`, its sources, figures, sidecars, and the alias
manifest) and the interaction between the public repository and the
anonymized submission.

## Findings

| item | status | detail |
| --- | --- | --- |
| Title searchability | **FAIL (blocking)** | The exact paper title, the full LaTeX source, the figures, and the workshop directory are committed to the public repository and pushed to `origin/main`. A reviewer searching the title or any distinctive sentence finds the owner's GitHub account immediately. Resolution options (owner's choice): (a) make the repository private for the review period; (b) remove `paper/` from the public repo before submission (history would still contain it unless rewritten — combining this with the already-required authorship rewrite is possible); (c) accept the risk where the venue tolerates preprint-style exposure (GDDL allows concurrent work, but the title match defeats the *blind*). Recommended: (a). |
| Repository visibility | **FAIL (blocking)** | Same root cause as above; the public repo also names the exact artifact IDs quoted in the paper (`phase4_…`, `workshop_external_validation_…`), which are unique searchable strings. The alias table (A1–A7) removes them from the paper text; the repo must still be non-public or the artifacts renamed in any uploaded bundle. |
| Author metadata in PDF | pass | `Author`, `Title`, `Subject`, `Keywords` empty; `Creator`/`Producer` generic (pdfTeX/hyperref). |
| PDF body identity scan | pass | Case-insensitive scan of extracted text for Clement, Callaert, clement-callaert, MBDA, CentraleSupélec, Paris-Saclay, usernames, home paths, Claude, Anthropic: no hits. |
| Figure metadata | pass | Matplotlib-generated PDFs carry only generic matplotlib producer strings and creation dates; no author or path metadata. |
| Source comments | pass | `main.tex` comments record the official 2026 style source URL and sty SHA-256; no author names. |
| Artifact bundle paths | pass with action | `paper/gddl2026/artifact_aliases.json` maps aliases to artifact IDs, checksums, config hashes, and code commits. The `code_commit` values are hashes of the public repository and are searchable on GitHub; the file's own header warns that the uploaded copy must strip `code_commit` (or the repo must be private during review). |
| Git hashes identifying the repo | pass with action | Same as above; no commit hash appears in the paper body. |
| Personal usernames | pass | None in the submission bundle. |
| Absolute paths | pass | None in the PDF or sources; figure sidecars store repo-relative script paths only. |
| Acknowledgements | pass | None present (submission mode also suppresses `\ack`). |
| Funding / employer | pass | None present. |
| Self-citations | pass | No self-citation; all references are third-party primary sources. |
| 2025 footer / main-conference claim | pass | Footer is the official NeurIPS 2026 submission notice (“Submitted to 40th Conference… NeurIPS 2026”). No NeurIPS 2025 / 39th text. Workshop title is set via `\workshoptitle` and appears in the footnote under camera-ready `[final]` per the official sty. |
| Template authenticity | pass | Official `neurips_2026.sty` from the NeurIPS 2026 CfP “Paper template” zip on `media.neurips.cc`, loaded with `[dblblindworkshop]`. |

## Standing rules during review

- Do not publish the exact paper title or the PDF on the owner's public
  GitHub while review is double-blind.
- Do not host the anonymized bundle on an account named after the owner;
  use the venue's supplementary upload or an anonymous repository service.
- Recheck this audit after any README change and before OpenReview
  upload (repository privacy / hash stripping remain blocking).
