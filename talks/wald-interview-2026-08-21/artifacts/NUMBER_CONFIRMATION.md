# Manuscript number confirmation

Date: 2026-08-13.

Source: frozen run directories copied from `outputs/` into this folder.
All listed SHA-256 digests match the pins in
`docs/PHASE4_RESULTS.md` and `scripts/make_workshop_figures.py`.
No experiment was re-run: the original 2026-07-24 artifacts were present
and checksum-valid. Regeneration was therefore skipped, as specified in
the talk plan.

Git HEAD at confirmation: `e48c9390e62b38f206342e6aeb7f160122ccc79c`.
Requested analysis freeze: `b149f35541db4da6bf8d2e79f0bb267c72d91b77`
(an ancestor of HEAD). Scientific tables below are the frozen 2026-07-24
files, not a new execution.

Reported error throughout is Gaussian \(W_2\), not \(W_2^2\).

## Artifact checksums

| artifact | SHA-256 |
| --- | --- |
| `phase4_gaussian_reproduction_2026-07-24-v1:results` | `b8930142cba5655ee553aae5ff400cd884c1137e77547d9a5fa94bd4e354973f` |
| `phase4_precision_2026-07-24-v1:table` | `5f8800a697c61c2eab2306281fe4fb1b01dee67bc3c678dd7ba4a626d9dc8e1b` |
| `phase4_decomposition_2026-07-24-v1:table` | `690d068c3693f99f38ddb17b479ab0e63b5ad859835f2092c5420175d954f252` |
| `workshop_external_validation_2026-07-24-v1:results` | `4234bc2baefa8390414db9e037c7d028408cb04591e2b6302524ed8ad3bd205d` |
| `workshop_external_validation_2026-07-24-v1:inversions` | `cceebdfcba6f7cec4a7ff9e137d4a53f8c7e389acc0222a20805f16204a1b875` |

## Comparison to `paper/gddl2026/main.tex` and `docs/WORKSHOP_PAPER_CLAIMS.md`

| claim | manuscript | artifact | status |
| --- | ---: | ---: | --- |
| endpoint configurations | 72 | 72 | match |
| two-path comparison blocks | 36 | 36 | match |
| ranking inversions | 14 of 36 | 14 of 36 | match |
| strongest family, dim, solver, NFE | low-rank, 8, Euler, 8 | same | match |
| linear \(\mathcal{R}\) | 2.9476523251 | 2.9476523251 | match |
| linear \(W_2\) | 0.8108540111 | 0.8108540111 | match |
| VP \(\mathcal{R}\) | 4.7295206355 | 4.7295206355 | match |
| VP \(W_2\) | 0.4564779075 | 0.4564779075 | match |
| strongest \(W_2\) margin | 0.3543761036 | 0.3543761036 | match |
| smallest inversion margin | \(1.1188920612\times 10^{-5}\) | \(1.1188920612\times 10^{-5}\) | match |
| max float64 vs 80-digit \(W_2\) | \(9.71\times 10^{-10}\) (paper), \(9.7050430488\times 10^{-10}\) (claims) | \(9.705043048770321\times 10^{-10}\) | match (paper rounds) |
| smallest-margin / precision ratio | more than 11,500 | 11,528 | match |
| non-centered inversions | 11 of 18 | 11 of 18 | match |
| non-centered \(\mathcal{R}\) margin (linear minus VP) | 0.7513 | 0.751314903565047 | match (paper rounds) |
| non-centered smallest inverted \(W_2\) margin | \(1.42\times 10^{-6}\) | \(1.4233816873306943\times 10^{-6}\) | match (paper rounds) |
| non-centered max float64 vs 80-digit | \(2.07\times 10^{-11}\) | \(2.0688060551503958\times 10^{-11}\) | match (paper rounds) |
| linear squared-\(W_2\) dominant-mode contribution | 0.4939430141 (results doc) | 0.49394301412306846 | match |
| VP squared-\(W_2\) dominant-mode contribution | 0.1837966072 (results doc) | 0.18379660723494287 | match |
| mean error in strongest block | 0 | 0.0 | match |

Low-rank solver-path pattern in the primary grid: VP is preferred under Euler
and linear under Heun and RK4 at both \(d\in\{2,8\}\) and NFE in \(\{8,16,32\}\).
This matches the manuscript statement.

No mixture row is used. No manuscript number in the table above was contradicted.
