# Claim-to-evidence matrix

Audit date: 2026-08-13.
Audited commit: `e48c9390e62b38f206342e6aeb7f160122ccc79c`.
Independent reconstruction from local `outputs/` plus source, configs, and tests.
Ledger file: `docs/CLAIMS_LEDGER.md`. Ledger statuses were not silently upgraded.

Allowed statuses: verified; verified with narrower scope; empirically reproduced; supported but not independently reproduced; ambiguous; unsupported; contradicted; blocked by missing evidence.

Severity if false: S0 cosmetic; S1 docs/repro; S2 localized ambiguity; S3 material correction; S4 release blocker.

## Ledger reconciliation

| Ledger ID | Ledger status | Matrix status | Why the ledger was not changed |
| --- | --- | --- | --- |
| H1 | inconclusive | empirically reproduced (as inconclusive) | Phase 3 gate only. Opposite family signs. |
| H2 | contradicted | empirically reproduced (as contradicted) | No alternative met the registered Spearman threshold. |
| H3 | inconclusive | empirically reproduced (as inconclusive) | No registered support threshold. |
| H4 | under-test | verified with narrower scope | Gaussian inversions reproduce. Mixture dim-8 excluded. One gate run. |
| GATE | under-test | verified with narrower scope | Process record only. |
| P4-C1 | under-test | empirically reproduced | 14 of 36 reconstructed from frozen artifacts. Ledger forbids `supported` from one focused chain. This audit is a recount, not a second experimental campaign. |
| P4-C2 | under-test | empirically reproduced | Low-rank solver-path pattern reconstructed on the registered grid and on robustness rows. Not universal. |
| P4-C3 | inconclusive | empirically reproduced (as inconclusive) | Leading proxy 29 of 36, post-hoc, in-sample. Docs "15 of 18 low-rank" is wrong; recount is 14 of 18. |
| P4-P1 | supported | verified | Proof re-derived. 80-digit identity check added. Grid-aware Euler only. |

## Numerical claims

| Claim ID | Exact claim | Status | Assumptions | Paper location | Code symbol | Configuration | Artifact | Independent check | Severity if false | Required action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N01 | 72 equal-budget configurations | empirically reproduced | 2 families, 2 dims, 2 paths, 3 solvers, 3 NFE | workshop Sec. 4 | `phase4_gaussian_reproduction` | `configs/experiment/phase4_gaussian_reproduction.yaml` | `.../results.json` (72 rows) | row count 72; `nfe==actual_nfe` | S4 | none |
| N02 | 36 two-path comparison blocks | empirically reproduced | pairing by (family, dim, solver, NFE) | workshop Sec. 4 | `phase4_blocks` logic | same | same | 36 unique keys | S4 | none |
| N03 | Ranking inversion: strict disagreement of `R` and `W_2` orderings | verified with narrower scope | no ties in this grid | workshop Sec. 4 | `d_metric * d_w2 < 0` | same | same | 0 ties | S3 | keep this definition |
| N04 | 14 of 36 blocks invert | empirically reproduced | registered grid only; descriptive count | abstract, intro | grouping above | same | SHA-256 `b8930142...` | 14 reconstructed | S4 | do not treat as a population rate |
| N05 | All 72 float64 `W_2` agree with 80-digit reference to at most `9.7050430488e-10` | empirically reproduced | mpmath 80 digits; CPU float64 | workshop Sec. 4 | `high_precision_gaussian_w2` | `phase4_precision.yaml` | `.../table.json` | max delta `9.705043048770321e-10` | S3 | keep 10-digit rounding; do not mix with reconstruction residual |
| N06 | Reconstruction residual `9.7050436884e-10` | empirically reproduced | modal W2 rebuild | not in workshop abstract | decomposition audit | `phase4_decomposition.yaml` | final validation table | `9.705043688449603e-10` | S2 | keep distinct from N05 |
| N07 | Smallest inversion margin `1.1188920612e-5` | empirically reproduced | low-rank, d=2, RK4, NFE 32 | workshop Sec. 4 | grouping | reproduction results | same | `1.1188920611502225e-05` | S3 | none |
| N08 | That margin exceeds the 80-digit W2 gap more than 11,500-fold | empirically reproduced | uses global max delta, not the pair delta | workshop Sec. 4 | ratio of N07/N05 | both artifacts | both | `11528.55...` | S2 | say "more than 11,500" or print 11528; all 14 HP orderings match float64 |
| N09 | Strongest inversion: low-rank d=8 Euler NFE 8 | empirically reproduced | max absolute W2 margin among inversions | Table 1 | grouping | reproduction | same | key and values match | S4 | drop "78% larger" |
| N10 | linear `R=2.9476523251`, `W_2=0.8108540111` | empirically reproduced | trapezoidal `R`, exact-moment `W_2` | Table 1 | `AveragedSquaredLipschitzProxy`, `gaussian_w2` | n_time 24 | same | `2.947652325101451`, `0.8108540110923013` | S3 | print 10 digits as in workshop |
| N11 | VP `R=4.7295206355`, `W_2=0.4564779075` | empirically reproduced | same | Table 1 | same | same | same | `4.72952063545214`, `0.4564779075112565` | S3 | none |
| N12 | W2 margin `0.3543761036` | empirically reproduced | absolute difference | Table 1 / text | same | same | same | `0.35437610358104477` | S3 | none |
| N13 | Relative "78% larger" | contradicted as a canonical number | `0.81085/0.45648 - 1 = 0.7763` | workshop body | n/a | n/a | n/a | 77.63 percent | S2 | omit from arXiv |
| N14 | Low-rank: Euler prefers VP; Heun and RK4 prefer linear | empirically reproduced | both dims, NFE 8,16,32 | workshop Sec. 4 | grouping | reproduction | same | 18/18 low-rank primary blocks | S3 | do not extend to anisotropic or learned models |
| N15 | Pattern persists at NFE 64, 128 and +/-10% perturbations | empirically reproduced | robustness grid; post-hoc relative to Phase 3 | workshop Sec. 4 | robustness rows | `phase4_robustness.yaml` | robustness table | 66/66 low-rank blocks match the pattern | S2 | label robustness as such |
| N16 | Non-centered family: 11 of 18 inversions | empirically reproduced | frozen means and anisotropy 6 | workshop Sec. 4 | `workshop_external_validation` | plan + yaml | inversions.json | 11 of 18 reconstructed | S3 | descriptive count |
| N17 | Non-centered `R` prefers VP with margin `0.7513` | empirically reproduced | `R` ignores `c(t)` | workshop Sec. 4 | metric_delta | same | inversions.json | `0.751314903565047` | S2 | keep four decimals or exact |
| N18 | Non-centered 80-digit max deviation `2.07e-11`; smallest inverted margin `1.42e-6` | empirically reproduced | audited inversions only | workshop Sec. 4 | precision.json | same | validation + inversions | max `2.0688060551503958e-11`; min margin `1.4233816873306943e-06` | S3 | none |
| N19 | Pre-registered before execution | verified with narrower scope | git chronology plus freeze document | workshop Sec. 4 | n/a | `WORKSHOP_EXTERNAL_VALIDATION_PLAN.md` | commits `f5e857c` (15:28), `508101e` A1 (15:33), `8b87c7f` results (16:04) | family frozen before results; Amendment A1 changed the endpoint sanity check, not the family | S2 | report A1 explicitly |
| N20 | Mixtures excluded for calibration failure | verified with narrower scope | dim-8 mixture SW not calibrated; Phase 4 Gaussian only | workshop Sec. 4 | gate analysis | Phase 3 configs | `GATE_RESULT.md`, postmortem | dim-8 mixture excluded from decisions; dim-2 GMM is gate-only | S2 | state this in the paper |
| N21 | Leading proxy agrees in 29 of 36 vs 22 for baseline | empirically reproduced | post-hoc, in-sample; lower-proxy prefers same path as lower W2 | workshop (proxy sentence) / docs | `leading_local_error_proxy` | diagnostics table | diagnostics | 29/36 and 22/36; low-rank 14/18 not 15/18 | S1 | correct docs; paper may keep 29/36 as diagnostic |
| N22 | `R` is the exact integral of `||A||_2^2` | contradicted if read as exact | trapezoidal, n_time=24, `is_exact=False` | workshop Sec. 2 | `AveragedSquaredLipschitzProxy` | metric n_time 24 | results `baseline_metric_is_exact: false` | quadrature of an exact integrand | S3 | say quadrature in arXiv |
| N23 | Equal-NFE: Euler 1, Heun 2, RK4 4 evals/step | verified | exact divisibility | workshop Sec. 4 | `n_steps_from_nfe` | solver yamls | results n_steps | (8,8), (8,4), (8,2) for Euler/Heun/RK4 at NFE 8 | S4 | none |
| N24 | No learned / image / video / world-model result | verified | absence of such experiments | limitations | n/a | n/a | no such artifacts | confirmed | S3 | keep limitations tight |

## Mathematical claims

| Claim ID | Exact claim | Status | Assumptions | Paper location | Independent check | Severity | Required action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M01 | Interpolant `X_t=alpha X_0+sigma X_1` has mean `alpha mu_0+sigma mu_1` and covariance `alpha^2 Sigma_0+sigma^2 Sigma_1` | verified | independent endpoints | Sec. 2 | first-principles | S4 | none |
| M02 | Affine field `b=A x+c` with `A=C_t Q^{-1}`, `C_t=alpha' alpha Sigma_0+sigma' sigma Sigma_1` | verified | Gaussian conditionals, Q PD | Sec. 2 | derivation + `GaussianAffineField` | S4 | state PD and independence |
| M03 | Centered `Sigma_0=I` gives `A=(1/2) Q' Q^{-1}`, `c=0` | verified | `mu_0=mu_1=0` | Sec. 2 | `Q'=2 C_t` | S4 | none |
| M04 | Commuting eigenmode reduction | verified | `Sigma_0=I`, `Sigma_1` SPD, scalar schedules | Sec. 2 | simultaneous diagonalization | S4 | commuting hypothesis explicit |
| M05 | Exact factor `sqrt(q(t_{n+1})/q(t_n))` | verified | q>0 | Sec. 3 | `d/dt log q = 2a` | S4 | none |
| M06 | Euler/Heun/RK4 one-step factors | verified | classical RK; scalar `x'=a(t)x` | Sec. 3 | matches solver code | S4 | distinguish stages vs steps |
| M07 | Gaussian W2 / Gelbrich-Bures | verified | Gaussians, PSD square roots | Sec. 2 | Peyre (2.41)-(2.42); Gelbrich 1990 | S3 | cite both |
| M08 | Centered commuting `W_2^2=sum (|r_i|-sqrt(lambda_i))^2` | verified | mean 0, modal factors `r_i` | Sec. 2 | `|r_i|` from PSD sqrt | S4 | keep absolute values |
| M09 | Transported-defect telescoping identity | verified | nonzero numerical factors; no smallness | Sec. 3 | algebra + tests | S4 | indexing `j<n` numerical, `j>n` exact |
| M10 | Euler LTE leading coeff `(1/2)(a'+a^2)` | verified | C^2 coefficient | Sec. 3 | Taylor | S3 | smoothness |
| M11 | Heun LTE leading coeff `-a''/12 + a^3/6` | verified | C^3 coefficient; explicit trapezoidal Heun | Sec. 3 | sympy series of implemented factor | S3 | none (formula is correct) |
| M12 | P4-P1 for every L>0 and integer N>=1 | verified | left-endpoint Euler; field chosen after N | Prop. | 80-digit identity; proof | S4 | grid-aware only; not the Gaussian mechanism |
| M13 | `epsilon_N=N(e^{L/N}-1)-L>0` | verified | L>0, N>=1 | Prop. | `e^z>1+z` | S4 | exclude L=0 |
| M14 | Averaged regularity ranking does not determine fixed-NFE W2 ranking in the tested commuting Gaussians | empirically reproduced | registered grid | abstract | N04 | S3 | keep tested-system scope; ledger remains under-test |
