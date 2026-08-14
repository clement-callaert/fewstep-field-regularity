# arXiv revision audit (2026-08-13)

This note records an independent re-audit of the working tree on branch
`arxiv-audit-and-release`. It is not a venue review and not a commit.

Statuses used below: `[VERIFIED]`, `[INFERENCE]`, `[OPEN]`, `[CONTRADICTED]`.

## Git and provenance

- Audited experiment-code commit: `e48c9390e62b38f206342e6aeb7f160122ccc79c`.
- Prior local manuscript commit: `ad18ff99b5298d89ed1c3fbcf332b8c3f192c536`.
- This revision is uncommitted by instruction.
- Provenance uses the planned immutable release tag `arxiv-v1` rather than a
  self-referential commit hash.
- Compact artifacts: `public_download: false`.
- Workshop/NeurIPS source is not the arXiv tree. Historical short draft:
  `paper/archive/gddl2026-conference/`.

## Scalar Gaussian counterexample (P4-P2)

Candidate (linear vs trigonometric VP, `lambda=4`, Heun NFE 8, four steps
`h=1/4`) was re-derived, not copied.

| Quantity | Result | Status |
| --- | --- | --- |
| `a_lin(t)=(5t-1)/(1-2t+5t^2)` | first-principles from `q'` | `[VERIFIED]` |
| `R_lin=5 pi/8 - 1` | trig sub; `arctan 2 + arctan(1/2)=pi/2`; rational boundary term `-1` | `[VERIFIED]` |
| `a_VP=(3 pi/2) sin(pi t)/(5-3 cos(pi t))` | from `q=(5-3 cos(pi t))/2` | `[VERIFIED]` |
| `R_VP=pi^2/16` | Weierstrass identity `int_0^pi sin^2 u/(5-3 cos u)^2 du = pi/36`, sympy | `[VERIFIED]` |
| Linear Heun steps `47/52, 6/5, 497/370, 97/74` | exact `fractions.Fraction` | `[VERIFIED]` |
| `r_lin=6797469/3559400` | product of those steps | `[VERIFIED]` |
| `W2_lin=321331/3559400 < 0.091` | integer comparison | `[VERIFIED]` |
| VP product in `(1.8696263416613175, 1.8696263416613176)` | `mpmath.iv` 40 dps | `[VERIFIED]` |
| `W2_lin < 0.091 < 0.130 < W2_VP` | interval endpoints | `[VERIFIED]` |
| All Heun factors positive | linear exact; VP interval `.a>0` | `[VERIFIED]` |
| Float64 vs 80-digit agreement to `1e-14` | package Heun vs mpmath | `[VERIFIED]` |

The candidate numerical values in the task prompt match these identities.
`W2=|r-2|=2-r` because both factors are in `(0,2)`.

Software: Python `fractions.Fraction`, `mpmath.iv` at 40 dps, independent
80-digit mpmath, package float64 Heun.

## Continuous `R` versus `Rhat_24`

- Benchmark code records `baseline_metric_is_exact: false` (24-node
  trapezoid of `||A||_2^2`).
- Headline arXiv claims use adaptive quadrature of `max_i a_i(t)^2`, and
  closed forms on the scalar pair.
- Path-ordering sign(`R_lin-R_VP`) agrees with `Rhat_24` on every headline
  geometry, including low-rank `d=2` (seed `271828`) and `d=8`.
- Inversion recount with continuous `R`: 14 of 36 and 11 of 18, same as
  `Rhat_24`.
- Strongest inversion (low-rank `d=8`, Euler, NFE 8): continuous
  `R=2.9441044083` vs `4.7305438136`; `W2` unchanged
  `0.8108540111` vs `0.4564779075`.
- Scipy `quad` error *estimates* can be pessimistic relative to the value
  error against closed forms. They are not interval certificates.
  `[VERIFIED]` for values; `[OPEN]` for a fully interval-certified multi-mode
  integral.

## Robustness 66

From `phase4_affine_audit.py` and frozen
`phase4_robustness_2026-07-24-v1:table`:

`2 dims x 3 solvers x (3 primary NFE x 3 perturbations + 2 extra NFE) = 66`.

Perturbation multiplies low-rank `noise_variance=0.05` by `(1+delta)`.
`F` is regenerated from the same seed. NFE 64 and 128 run only at
`delta=0`. Status: post-hoc. `[VERIFIED]`

## Non-centered family

Chronology: freeze `f5e857c` 15:28, Amendment A1 `508101e` 15:33 (endpoint
sanity check only), results `8b87c7f` 16:04, all 2026-07-24 +02.
Accurate phrase: pre-specified in the repository before execution, not
"preregistered". `R` ignores `c(t)`; mean still enters `W2^2`.
Among 11 inversions, dimension-8 Euler/Heun inversions are mean-driven;
two `d=2` inversions (Heun NFE 32, RK4 NFE 32) are covariance-driven.
`[VERIFIED]` from frozen results plus the mean/Bures split.

## Ledger

| ID | old | new | rationale |
| --- | --- | --- | --- |
| P4-P2 | (new) | `supported` | deterministic existence |
| P4-C1 | `under-test` | `under-test` | hierarchical descriptive count; not a second campaign |
| P4-C2 | `under-test` | `under-test` | solver-path split remains descriptive |
| P4-P1 | `supported` | `supported` | complementary grid-aware Euler construction |

## Literature (search 2026-08-13, primary sources)

Inspected official arXiv/CVPR pages, not secondary blogs, for technical
scope:

- Chen, Vanden-Eijnden, Xu, arXiv:2509.01629v3: averaged squared Lipschitzness
  as a schedule *criterion* (Def. 3.2), not a pairwise ranking theorem.
- Stéphanovitch, arXiv:2604.06065: Lipschitz bounds and Euler-type `W2`
  rates `sqrt(d)/N`.
- Gupta et al., arXiv:2605.11547: SharpEuler *grid* for a fixed learned field.
- Du, Zhang, Li, arXiv:2605.15419: least-action *path design*.
- Yuan et al., arXiv:2603.17671 / CVPR 2026 pp. 35882-35892: instance-aware
  discretizations.
- Tao and Choi, arXiv:2605.06680: Euler exact on McCann OT, not independent
  linear/VP coupling.
- Khan, arXiv:2604.04491: learned material-derivative regularizer.

Search absence of an identical commuting Gaussian ranking counterexample is
not a proof that none exists. `[INFERENCE]` for novelty scope only.

## Residual limitations

- Placeholder commit hash.
- Compact artifacts not a public download.
- Multi-mode `R` is adaptive quadrature, not interval-certified.
- P4-C1/C2 remain under-test.
- No learned-field experiment.
