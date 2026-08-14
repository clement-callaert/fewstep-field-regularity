# Literature and novelty audit

Search date: 2026-08-13.
Databases and interfaces: arXiv HTML/abs, DOI records, existing repository notes under `papers/notes/`, NeurIPS 2026 Main Track Handbook, GDDL workshop CFP, arXiv submit help.
Queries (representative): Lipschitz-guided interpolation schedules Chen Vanden-Eijnden Xu 2509.01629; flow matching Lipschitz Jacobian few-step ranking; Align Your Steps; DPM-Solver; EDM; Gelbrich Wasserstein Gaussians; "few-step flow matching path regularity Jacobian"; strain vorticity flow matching 2026.
Limitation: absence of an identical title is not a novelty proof. Web search is incomplete for paywalled books (Hairer was checked against existing notes and standard statements).

## Closest identified results

| Work | Role | What it does | What it does not do |
| --- | --- | --- | --- |
| Chen, Vanden-Eijnden, Xu, arXiv:2509.01629 v3 (2026-05-16) | criterion under test | Def 3.2 avg-Lip2 `int E[||nabla b_t(I_t)||_2^2] dt`; Gaussian affine Example 3.3; transfer formula Prop 3.1 | Does not claim that avg-Lip2 ordering determines equal-NFE Gaussian W2 ranking for linear vs VP |
| Sabour, Fidler, Kreis, ICML 2024, arXiv:2404.14507 | solver-specific schedules | Align Your Steps optimizes the sampling schedule per solver, model, and dataset | Not a closed-form commuting Gaussian ranking study |
| Karras et al., NeurIPS 2022 (EDM) | schedule vs discretization | Separates preconditioning, ODE, and solver | No avg-Lip2 ranking claim |
| Lu et al., DPM-Solver / DPM-Solver++, Zhang-Chen DEIS | exact linear parts | High-order solvers exploiting the linear component of diffusion ODEs | Affine interpolant ranking under Euler/Heun/RK4 |
| Lipman et al., ICLR 2023; Albergo, Boffi, Vanden-Eijnden, JMLR 26(209) 2025; Liu, Gong, Liu, ICLR 2023; Tong et al. CFM | path machinery | Gaussian and interpolant fields | Not the inversion table |
| Gelbrich, Math. Nachr. 147 (1990) | W2 formula | L2 Wasserstein between Gaussians | |
| Hairer / Butcher / Hairer-Lubich-Wanner | RK and backward error | Local error machinery | No generative-path ranking |
| Tao and Choi, arXiv:2605.06680 (2026-04-22) | contemporaneous NA companion | Strain vs vorticity in FM integration error; Euler exact on McCann OT displacement | Independent-coupling linear/VP ranking by avg-Lip2; not a counterexample to Def 3.2 |
| Khan, Iso-FM, arXiv:2604.04491 (2026) | contemporaneous | Material-derivative regularizer for learned FM | Learned images; not this benchmark |

## Citation accuracy

| Manuscript use | Source check |
| --- | --- |
| Lipschitz-guided Def 3.2 as the tested scalar | Confirmed in arXiv HTML v3, Eq. (3.4), spectral 2-norm |
| Example 3.3 Gaussian affine field | Confirmed; centered 1D form matches `A=C Q^{-1}` |
| Albergo interpolant `X_t=alpha X_0+sigma X_1` | JMLR 2025 record used in current bib; arXiv:2303.08797 is the preprint |
| Lipman FM Gaussian paths | ICLR 2023 / arXiv:2210.02747 |
| Liu rectified flow | bib `liu2023rectified` ICLR 2023, arXiv:2209.03003 (correct year 2023 for ICLR) |
| Gelbrich 1990 | formula source; code comments also cite Peyre (2.41)-(2.42), which is the same Gaussian identity |
| AYS / EDM / DPM-Solver as solver-schedule interaction | accurate as context, not as the present theorem |

## Novelty wording

Do not write "to our knowledge" without repeating this search log in the paper. Preferred contribution sentence:

This work records a controlled non-implication: on a registered commuting Gaussian grid, ordering two scalar interpolants by trapezoidal averaged squared Jacobian does not determine their equal-NFE Gaussian W2 ordering, and an explicit grid-aware Euler construction shows the same logical gap for a scalar linear ODE. Closest prior work proposes avg-Lip2 as a design criterion (Chen et al., 2025) and documents solver-dependent schedules (Sabour et al., 2024; Karras et al., 2022). Contemporaneous strain/OT analysis (Tao and Choi, 2026) concerns McCann displacement interpolation, which is not the independent-coupling linear and VP paths used here.

Search absence does not prove that no earlier counterexample exists.

## BibTeX issues to fix in the arXiv bib

- Keep Albergo as JMLR 2025 with arXiv:2303.08797 in the note.
- Add Tao and Choi arXiv:2605.06680 as contemporaneous.
- Add Iso-FM arXiv:2604.04491 only if cited; if cited, keep the claim scope (learned FM, not this grid).
- DPM-Solver++ remains an arXiv preprint in the workshop bib; check for a later venue before asserting a conference.
- Do not cite NeurIPS as a venue of the present paper.
