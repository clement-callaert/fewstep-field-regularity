# Final arXiv scientific gate

Date: 2026-08-13.
Experiment-code commit used for frozen outputs: `e48c9390e62b38f206342e6aeb7f160122ccc79c`.
This report re-audits the extended manuscript. It does not reuse a previous “READY WITH DISCLOSURES” status.

Allowed scientific statuses: `SCIENTIFIC_READY` or `NOT_READY`.

## Scientific status

**SCIENTIFIC_READY**

The repaired manuscript has a correct completing-square identity, an analytical Euler proof, a rational/integer VP certificate that does not rely on `mpmath.iv` as the proof, a specified non-centered construction with signed $\Delta$ drivers, a readable signed-difference Figure 4, a non-centered $R$ vs $\widehat R_{24}$ row recomputed to $10^{-12}$, Chen et al. pairwise-ranking positioning that does not refute their theorem, and a clean extracted-source PDFLaTeX build. Remaining items are owner publication actions (tag, licences) or missing local tools (`qpdf`), not scientific blockers.

## Important claims

### C1. Completing-square identity and $R_{\mathrm{lin}}=5\pi/8-1$

- Label: `[VERIFIED]`
- Location: Appendix A, identities (eq:q-bracket) and (eq:q-plus); Proposition 1.
- Evidence: $q_{\mathrm{lin}}(t)=5[(t-1/5)^2+(2/5)^2]=5(t-1/5)^2+4/5$ expands to $1-2t+5t^2$. Substitution $u=t-1/5=(2/5)\tan\theta$ converts $\int a^2$ to $(5/2)\int\sin^2\theta\,d\theta$. Limits $\arctan(-1/2)\to\arctan 2$ and $\arctan 2+\arctan(1/2)=\pi/2$ give $5\pi/8-1$.
- Method: algebraic expansion in `completed_square_linear_variance`; `test_completed_square_expands_to_linear_variance`; hand re-derivation of the $\theta$ substitution.
- Tolerance: exact rational identity; closed form, no float tolerance.
- Residual risk: none for the identity. The false form $5(t-1/5)^2+(2/5)^2$ is absent from `paper/arxiv/main.tex`.

### C2. Exact VP Heun-grid drifts

- Label: `[VERIFIED]`
- Location: Appendix A, displayed grid; Proposition 1.
- Evidence: $a=(3\pi/2)\sin(\pi t)/(5-3\cos(\pi t))$ at $t=0,1/4,1/2,3/4,1$ equals $0$, $(9+15\sqrt{2})\pi/82$, $3\pi/10$, $(-9+15\sqrt{2})\pi/82$, $0$.
- Method: `vp_grid_drifts()` monomials in $\pi$ and $\sqrt{2}$; `test_vp_grid_drifts_exact_algebraic_values`. Sign of $a(3/4)$: $15^2\cdot 2-9^2=369>0$.
- Tolerance: exact.
- Residual risk: none.

### C3. Four-step VP Heun product in $\mathbb{Q}[\pi,\sqrt{2}]$

- Label: `[VERIFIED]`
- Location: Appendix A; artefact `paper/arxiv/artifacts/scalar_counterexample.json`.
- Evidence: twelve monomials, all nonnegative coefficients, so substituting upper bounds for $\pi$ and $\sqrt{2}$ is valid.
- Method: `vp_heun_product_poly`; `test_vp_heun_product_is_nonnegative_in_pi_sqrt2`.
- Tolerance: exact.
- Residual risk: the certificate uses the implemented Heun factor, not a generic two-stage RK.

### C4. Rational/integer certificate $r_{\mathrm{VP}}<187/100$ and $W_{2,\mathrm{VP}}>13/100$

- Label: `[VERIFIED]`
- Location: Proposition 1; Appendix A; generated `vp_certificate.tex`; workshop supplement.
- Evidence:
  - $\sqrt{2}<99/70$ because $99^2-2\cdot 70^2=1$.
  - $\pi<355/113$ from Machin $\pi=16\arctan(1/5)-4\arctan(1/239)$ with seven Taylor terms (odd, upper) for $\arctan(1/5)$ and four terms (even, lower) for $\arctan(1/239)$; integer comparison in `machin_pi_upper_bound_integer_certificate`.
  - $P(355/113,99/70)=192113353671412470139303/102753427879939708813312<187/100$, i.e. $19211335367141247013930300<19214891013548725548089344$.
  - Factors positive $\Rightarrow W_2=2-r$; $r<187/100\Rightarrow W_2>13/100$. Linear $W_2<0.091$ from the rational product $6797469/3559400$.
- Method: `test_rational_and_integer_vp_certificate`; `scripts/verify_scalar_counterexample.py`.
- Tolerance: exact integer comparison. `mpmath` 1.3.0 interval at 40 dps and an 80-digit product are independent cross-checks only.
- Residual risk: none for the stated inequality. The bound $187/100$ is strictly weaker than the interval $\approx 1.8696263416613175$.

### C5. Grid-aware Euler proposition

- Label: `[VERIFIED]`
- Location: Appendix D, Proposition 2.
- Evidence: $\int\cos(2\pi Nt)=0$ (endpoint match $e^L$); $\int\cos^2$ gives the $R$ gap $\varepsilon_N^2/2$; on $t_n=n/N$, $\cos(2\pi n)=1$ so oscillatory Euler factors equal $e^{L/N}$; constant-field factors equal $1+L/N$; $\log(1+z)<z$ yields $(1+L/N)^N<e^L$.
- Method: restored analytical proof in the manuscript; 80-digit check remains a test only.
- Tolerance: exact.
- Residual risk: the field $a_{1,N}$ is chosen after the grid. The paper states this is not the Gaussian Heun mechanism.

### C6. Covariance drift independent of $c(t)$

- Label: `[VERIFIED]`
- Location: Section 2, paragraph “Isotropic source”.
- Evidence: for $\Sigma_0=I$, $a_i=q_i'/(2q_i)$ with $q_i=\alpha^2+\lambda_i\sigma^2$. The restriction “when $c=0$” is not used.
- Method: first-principles $Q'=2C_t$ for isotropic source, whether or not means vanish.
- Tolerance: exact.
- Residual risk: commuting hypothesis still required.

### C7. Chen et al. positioning

- Label: `[VERIFIED]`
- Location: abstract; introduction paragraph; limitations; conclusion.
- Evidence: primary source arXiv:2509.01629v3, updated 2026-05-16T04:39:44Z, title *Lipschitz-Guided Design of Interpolation Schedules in Generative Models*, authors Yifan Chen, Eric Vanden-Eijnden, Jiawei Xu. Primary class `stat.ML` (cross-lists `cs.LG`, `math.NA`). The source proposes minimizing averaged squared Lipschitzness as a schedule-design criterion and does not claim that the scalar universally orders finite-step error of every pair of paths at fixed NFE.
- Method: arXiv Atom API + HTML v3; bibliography fields checked; manuscript wording checked for “refute”.
- Tolerance: n/a.
- Residual risk: a reader who stops at the first abstract sentence (“the implication fails”) could over-read; the next sentences and the introduction paragraph block that reading. Conclusion: “not a refutation of the Lipschitz-guided schedule criterion”.

### C8. Non-centered construction and signed drivers

- Label: `[VERIFIED]`
- Location: Section on the non-centered family; Appendix tables; Figure 4 caption.
- Evidence: $d\in\{2,8\}$, $i=0,\ldots,d-1$, $\mu_{0,i}=0.75(-1)^i$, $\mu_{1,i}=1+0.25 i$, geometric eigenvalues of $D$ from $6^{-1/2}$ to $6^{1/2}$ (condition number 6), Euler/Heun/RK4, $B\in\{8,16,32\}$, $S=B/s$, forward in $t$. Frozen $W_2$ from `outputs/workshop_external_validation_2026-07-24-v1/`; continuous $R$ recomputed. Drivers use $\Delta_{\mathrm{mean}}=M_{\mathrm{lin}}-M_{\mathrm{VP}}$, $\Delta_{\mathrm{cov}}=C_{\mathrm{lin}}-C_{\mathrm{VP}}$, not the largest raw term inside one path.
- Method: frozen JSON + `make_arxiv_compact_artifacts.py`; `test_compact_noncentered_signed_deltas_and_quadrature_row`.
- Tolerance: float64 frozen values; $R$ recomputed to $10^{-12}$.
- Residual risk: “pre-specified” (git chronology) is not an independent replication. Amendment A1 changed an endpoint sanity check, not the family.

### C9. Figure 4 readability

- Label: `[VERIFIED]`
- Location: Figure 4 (`fig_noncentered.pdf`), caption; Table of signed $\Delta$.
- Evidence: grouped symlog bars of $\Delta_{\mathrm{mean}}$ and $\Delta_{\mathrm{cov}}$; positive = linear larger than VP; stars mark inversions; exact numbers in the $\Delta$ table. On-bar numeric labels were omitted to avoid overlap at PDF size.
- Method: visual inspection of rendered PDF pages; caption wording.
- Tolerance: qualitative readability at the compiled page size.
- Residual risk: very small mixed blocks remain visually small on a symlog axis; the table carries the values.

### C10. Continuous $R$ versus $\widehat R_{24}$, including non-centered row

- Label: `[VERIFIED]`
- Location: Appendix quadrature table; strongest-row Table 1.
- Evidence: independent recomputation from `frozen_target_eigenvalues`:

  | path | continuous $R$ | $\widehat R_{24}$ |
  | --- | --- | --- |
  | linear | 1.093536901895 | 1.093850806380 |
  | VP | 0.342354218861 | 0.342535902815 |

  Strongest centered continuous $R$: $2.9441044083$ vs $4.7305438136$.
- Method: `test_noncentered_r_versus_rhat24_matches_published_targets`; generator fails outside abs $10^{-12}$.
- Tolerance: $10^{-12}$ absolute.
- Residual risk: $d=2$ and $d=8$ share spectral $R$ because $\cR=\int\max_i a_i(t)^2$.

### C11. Captions and precision wording

- Label: `[VERIFIED]`
- Location: Figure 2 caption; reproducibility paragraph.
- Evidence: “Modal contributions to squared Wasserstein error and transported signed defects.” “Default numerical precision for the benchmark runs is float64. The scalar calculation uses exact rational and algebraic expressions together with validated bounds; the precision audit uses 80-digit arithmetic.”
- Method: TeX grep; PDF text.
- Tolerance: n/a.
- Residual risk: none.

### C12. Provenance without a self-referential commit hash

- Label: `[VERIFIED]` for the manuscript; `[OPEN]` for tag existence (manual publication gate only)
- Location: reproducibility section; `generated/numbers.tex`; `scripts/check_arxiv_release.py`.
- Evidence: planned tag `arxiv-v1`; URL `https://github.com/clement-callaert/fewstep-field-regularity/releases/tag/arxiv-v1`. The retired placeholder token is absent (`scripts/check_arxiv_placeholder.py`). `--require-tag` is documented as the owner gate.
- Method: constructed-token grep; pytest hygiene tests.
- Tolerance: exact string absence.
- Residual risk: the URL 404s until the owner creates the tag and GitHub Release. Compact artefacts remain `public_download: false` until then.

### C13. 14/36 and 11/18 are descriptive

- Label: `[VERIFIED]`
- Location: abstract, introduction, benchmark, limitations.
- Evidence: $4$ geometries $\times$ $9$ solver-budget conditions; counts are hierarchical summaries, not iid population rates. Same sign as $\widehat R_{24}$.
- Method: compact JSON recount.
- Tolerance: exact integer counts.
- Residual risk: a casual reader may still treat 14/36 as a prevalence estimate; the paper says not to.

### C14. Clean source-package build

- Label: `[VERIFIED]` (modulo missing `qpdf`)
- Location: `paper/arxiv/arxiv-source.zip`.
- Evidence: extract to a fresh directory, `latexmk -pdf` with no repository-external files, 14 pages, 0 overfull, pdftotext identical to the repo PDF, Type 1 + embedded CID TrueType, no Type 3, no Anonymous / under review / placeholder / temporary email / local absolute path.
- Method: `scripts/pack_arxiv_source.py`; clean `/tmp` compile; `pdffonts`; `pdftotext`; page PNGs. `qpdf` is not installed.
- Tolerance: PDF byte hashes may differ by timestamp; text must match.
- Residual risk: `qpdf --check` was not run because the tool is absent. That is reported, not treated as passed.

### C15. Licence files

- Label: `[OPEN]` (owner action, not a scientific failure)
- Location: `pyproject.toml` `license = { text = "MIT" }`; no `LICENSE` file; `paper/arxiv/ARXIV_METADATA.md` lists arXiv licence options and selects none.
- Evidence: glob for `LICENSE*` is empty.
- Method: filesystem.
- Residual risk: a reader of `pyproject.toml` may infer MIT without a licence file.

## Findings

| Severity | Finding | Disposition |
| --- | --- | --- |
| Blocker | none remaining | |
| Major (repaired) | False completing-square identity | corrected to two equivalent true identities |
| Major (repaired) | VP certificate depended only on `mpmath.iv` | replaced by rational/integer certificate |
| Major (repaired) | Euler proposition stated without a sufficient proof | analytical proof restored |
| Major (repaired) | Drift formula restricted to $c=0$ | restriction removed |
| Major (repaired) | Figure 4 crushed small contributions | replaced by signed $\Delta$ symlog bars |
| Major (repaired) | Missing non-centered $R$ vs $\widehat R_{24}$ row | added and recomputed |
| Major (repaired) | Self-referential commit placeholder | replaced by planned tag `arxiv-v1` |
| Minor | `qpdf` not installed | reported; not treated as passed |
| Minor | Chen bib `primaryClass` was `cs.LG` | corrected to `stat.ML` from the Atom API |
| Manual | tag `arxiv-v1` does not exist yet | owner publication gate |
| Manual | arXiv licence not chosen | owner action |
| Manual | MIT in `pyproject.toml` without `LICENSE` | owner action |

## Commands and tests

See the handoff in the accompanying chat for literal pass/fail of ruff, mypy, pytest, scalar verification, artefact regeneration, LaTeX, zip extract, `pdffonts`, `pdftotext`, and `git diff --check`.
