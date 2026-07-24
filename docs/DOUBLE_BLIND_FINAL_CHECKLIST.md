# Double-blind final checklist

Date: 2026-07-24. Scope: files intended for submission
(`paper/gddl2026/main.pdf`, sources, figures, sidecars,
`artifact_aliases.json`) plus repository-level exposure. Every item is
pass / fail / not applicable. **Any fail blocks submission.**

| # | item | status | note |
| --- | --- | --- | --- |
| 1 | "Clement" absent from submission files | pass | case-insensitive sweep |
| 2 | "Callaert" absent | pass | |
| 3 | "clement-callaert" absent | pass | |
| 4 | "MBDA" absent | pass | only false-positive substring of `\lambda` |
| 5 | "CentraleSupélec" absent | pass | |
| 6 | "Paris-Saclay" absent | pass | |
| 7 | Local usernames absent | pass | no `calla`, no `home/`, no `Users/` |
| 8 | Home-directory paths absent | pass | sidecars store repo-relative paths |
| 9 | Personal email addresses absent | pass | |
| 10 | GitHub repository URLs absent from submission files | pass | |
| 11 | Git commit hashes in submission files | **fail** | `artifact_aliases.json` and the three figure sidecars record `git_commit` (and sidecars a `git_status`) of the public repo; searchable. Strip these fields from the uploaded bundle, or keep the repository private during review (docs/DOUBLE_BLIND_AUDIT.md). |
| 12 | Acknowledgements absent | pass | submission mode also hides `\ack` |
| 13 | Employer names absent | pass | |
| 14 | PDF metadata authors/title/subject/keywords empty | pass | verified via pypdf |
| 15 | "Claude" absent from submission files | pass | |
| 16 | "Anthropic" absent from submission files | pass | |
| 17 | No NeurIPS 2025 footer / main-conference claim | pass | footer is official NeurIPS 2026 submission notice ("Submitted to 40th Conference… NeurIPS 2026"); no 39th/2025 string |
| 18 | Official NeurIPS 2026 template in use | pass | `[dblblindworkshop]` + `\workshoptitle{Geometric Distributional Deep Learning: Bridging Optimal Transport, Learning and Structured Data}`; sty from official CfP zip (SHA-256 `c3fc2894e83d2517ca18b66741d6c595986d97957dc08ec08bb2125a7ec4555a`). Note: official sty prints the workshop title in the footnote only under `[final]`; submission mode uses the conference-wide notice. Main-track `checklist.tex` not included. |
| 19 | Public repository does not expose the paper | **fail** | `paper/` with exact title and `docs/WORKSHOP_*` are pushed to the public repo. Make the repo private for the review window (recommended) or remove/relocate before submission (docs/REPOSITORY_PUBLICATION_PLAN.md). |
| 20 | Anonymized bundle not hosted on an owner-named account | pass (by policy) | upload only via the venue's supplementary mechanism |
| 21 | Legitimate citations preserved | pass | Chen/Vanden-Eijnden/Xu and all third-party citations retained; none removed by the sweep |
| 22 | Supplement exists for "accompanying supplement" claims | **fail** | the paper promises a proof/edge-case supplement and an alias-resolving supplement; assemble the anonymized bundle (P4-P1 audit, alias manifest with `code_commit` stripped, artifact tables) before submission |

## Blocking failures (must be resolved by the owner before submission)

1. Item 19 / 11: repository exposure and searchable commit hashes —
   decide privacy strategy per `docs/REPOSITORY_PUBLICATION_PLAN.md`.
2. Item 22: assemble the anonymized supplement bundle.
