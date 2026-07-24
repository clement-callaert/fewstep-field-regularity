# Phase 4 results

Status: Complete for the focused Phase 4 scope. Scientific claims remain
limited and under review.

Scope: Exact anisotropic and low-rank Gaussian targets, dimensions 2 and 8,
linear and variance-preserving paths, Euler, Heun, RK4, and NFE 8, 16, and
32. NFE 64 and 128 and ±10 percent perturbations are robustness diagnostics.
Phase 5 was not started.

Artifact IDs used:

- `phase4_gaussian_reproduction_2026-07-24-v1:results`
- `phase4_precision_2026-07-24-v1:table`
- `phase4_decomposition_2026-07-24-v1:table`
- `phase4_diagnostics_2026-07-24-v1:table`
- `phase4_robustness_2026-07-24-v1:table`
- `phase4_final_validation_2026-07-24-v1:table`

The clean reproduction and precision audit are pre-specified Phase 4 checks.
The decomposition, local diagnostics, perturbations, and optional budgets are
post-hoc relative to the Phase 3 gate. No post-hoc quantity is promoted to the
registered hypothesis list.

## Executive summary

Phase 4 meets success criteria 1 and 3 in a limited sense. The exact Gaussian
flow separates into commuting scalar eigenmodes. Fixed-grid error depends on
solver stage values, time derivatives, signed local defects, and their
transport to the endpoint. An average of squared Jacobian norms discards this
information and therefore cannot determine the endpoint ordering.

All 14 clean Gaussian inversion blocks reproduce. The low-rank preference
pattern persists under the allowed parameter perturbations and at NFE 64 and
128. Float64 agrees with an 80-digit reference to at most
`9.7050430488e-10`. Even the smallest inversion margin is more than 11,500
times that reference difference.

The broad scientific novelty is weak. Primary literature already establishes
solver-specific schedule optimization and solver-dependent few-step behavior.
The narrow commuting Gaussian decomposition remains useful as a controlled
limitation of averaged regularity, but the minimal proposition is elementary
and grid-aware.

## Clean reproduction

Run 1 reproduced all 72 Gaussian rows from the surviving Phase 3 artifact
within the registered absolute tolerance `1e-12`. It reproduced 14 baseline
ranking inversion blocks. Equal NFE, covariance symmetry, covariance positive
semidefiniteness, and endpoint moment checks passed.

Observation: The low-rank family prefers variance-preserving for Euler and
linear for Heun and RK4 at both dimensions and every primary NFE budget.

Interpretation: This is a solver-path interaction in the tested grid. It is
not evidence that one path is optimal outside the grid.

## Strongest surviving inversion

The strongest absolute W2 inversion is low-rank Gaussian, dimension 8, Euler,
NFE 8:

| path | baseline metric | Gaussian W2 |
| --- | ---: | ---: |
| linear | 2.9476523251 | 0.8108540111 |
| variance-preserving | 4.7295206355 | 0.4564779075 |

The baseline prefers linear, while endpoint error prefers
variance-preserving. The W2 margin is `0.3543761036`.

The largest target covariance eigenvalue, `10.6756382265`, dominates this
configuration. Its squared W2 contribution is `0.4939430141` for linear and
`0.1837966072` for variance-preserving. The mean error is zero.

The smallest reproduced inversion is low-rank Gaussian, dimension 2, RK4,
NFE 32. Its margin is `1.1188920612e-5`, still 11,528 times the maximum
80-digit reference difference.

## Mathematical explanation

For covariance
\(Q(t)=\alpha(t)^2I+\sigma(t)^2\Sigma_1\), the centered Gaussian drift is

\[
A(t)=\frac12Q'(t)Q(t)^{-1}.
\]

All matrices commute with \(\Sigma_1\), so each eigenmode obeys
\(x_i'=a_i(t)x_i\), with exact transition
\(\sqrt{q_i(t_{n+1})/q_i(t_n)}\). The numerical solver instead multiplies
stage-dependent factors. The final factor error is the exact sum of signed
one-step defects multiplied by earlier numerical and later exact transition
factors.

This decomposition explains the non-implication. The baseline integral
contains amplitudes of \(A(t)\), but not the solver stage sampling, derivatives
of \(A(t)\), signs, cancellation, or endpoint transport. See
[the mathematical analysis](PHASE4_MATHEMATICAL_ANALYSIS.md).

## Solver-specific explanation

For affine \(b(t,x)=A(t)x+c(t)\), the Euler material derivative is

\[
(A'(t)+A(t)^2)x+c'(t)+A(t)c(t).
\]

For a scalar mode, the exact-minus-Euler leading local coefficient is
\((a'+a^2)/2\). The exact-minus-Heun coefficient is
\(-a''/12+a^3/6\). RK4 uses different stage samples and cancels all lower
order terms.

On the same 36 path-comparison blocks, the baseline and material-derivative
integrals each agree with the observed preference in 22 blocks. The
solver-specific leading proxy agrees in 29 blocks, including 15 of 18
low-rank blocks. This comparison is post-hoc and in-sample. It suggests the
right mechanism but does not establish predictive superiority. Exact
transported local defects, rather than an unsigned aggregate, fully account
for the endpoint factor error by algebraic identity.

## Minimal proposition

P4-P1 has an explicit smooth scalar construction. Two fields have the same
exact endpoint. The field with strictly larger averaged squared Jacobian has
zero fixed-grid Euler endpoint error, while the constant field has positive
error. The statement is numerically and symbolically checked and remains
`needs expert review`.

The construction is tailored to the Euler grid. It demonstrates
non-implication but should not be presented as the mechanism behind every
Gaussian inversion or as a major theorem.

## Literature overlap

Classical Runge-Kutta and backward-error literature already supplies the
general local and modified-equation machinery. DPM-Solver, DPM-Solver++, and
DEIS treat exact linear terms and solver-specific expansions. Align Your
Steps explicitly optimizes schedules for particular solvers, models, and
data. Lipschitz-guided schedule work proposes the averaged squared
Lipschitzness baseline and analyzes Gaussian targets.

No audited source was found with the exact P4-P1 construction or the exact
commuting Gaussian inversion table. This does not establish novelty. The
overlap substantially weakens a broad solver-dependence contribution. See
[the literature audit](PHASE4_LITERATURE_AUDIT.md).

## Precision audit

All 72 float64 W2 values were compared with 80-digit mpmath propagation.
Maximum absolute difference: `9.7050430488e-10`. The threshold was `2e-9`.
The strongest margin is `0.3543761036`; the smallest inversion margin is
`1.1188920612e-5`.

Across Run 1, the minimum propagated covariance eigenvalue is `0.0273188110`,
the maximum is `10.8536434383`, and the maximum numerical affine-map condition
number is `16.6018078049`. Covariance symmetry, positive semidefiniteness,
matrix square-root use, endpoint moments, W2 reconstruction, and equal NFE
passed.

## Runtime

| run | run ID | manifest runtime | command wall time | hard stop |
| --- | --- | ---: | ---: | ---: |
| 1 | `phase4_gaussian_reproduction_2026-07-24-v1` | 0.350331 s | 2.03 s | 45 min |
| 2 | `phase4_precision_2026-07-24-v1` | 0.177238 s | 1.95 s | 45 min |
| 3 | `phase4_decomposition_2026-07-24-v1` | 0.043046 s | 1.72 s | 60 min |
| 4 | `phase4_diagnostics_2026-07-24-v1` | 8.109213 s | 9.72 s | 60 min |
| 5 | `phase4_robustness_2026-07-24-v1` | 0.055365 s | 1.78 s | 90 min |
| 6 | `phase4_final_validation_2026-07-24-v1` | 0.011677 s | 1.74 s | 120 min |

Every run remained far below its hard stop. No Cartesian benchmark was run.

## Artifact checksums

| artifact ID | SHA-256 |
| --- | --- |
| `phase4_gaussian_reproduction_2026-07-24-v1:results` | `b8930142cba5655ee553aae5ff400cd884c1137e77547d9a5fa94bd4e354973f` |
| `phase4_precision_2026-07-24-v1:table` | `5f8800a697c61c2eab2306281fe4fb1b01dee67bc3c678dd7ba4a626d9dc8e1b` |
| `phase4_decomposition_2026-07-24-v1:table` | `690d068c3693f99f38ddb17b479ab0e63b5ad859835f2092c5420175d954f252` |
| `phase4_diagnostics_2026-07-24-v1:table` | `5c5a1e4c1c47ef254b13559ef13c187d24c9f1e79a17454974d55f9348565ba1` |
| `phase4_robustness_2026-07-24-v1:table` | `3cace6e3d016f0c3e893a656fb76acfad11ce4569debc6ea418fe5aeec7d6306` |
| `phase4_final_validation_2026-07-24-v1:table` | `771ff7cbb02c4368b0601cc11d3e02fcdfaac5d964059e5846d62c25b7a0c4c9` |

Each manifest records the remaining validation checksums, config hash, code
commit, command, environment, package lock hash, and source hashes.

## Claims and recommendation

P4-C1 and P4-C2 remain under-test because the policy forbids support from this
single focused evidence chain. P4-C3 is inconclusive because its apparent
improvement is post-hoc and in-sample. P4-P1 remains proposed and needs expert
review. H1 and H3 remain inconclusive, H2 remains contradicted, and H4 remains
under-test.

Recommendation: pivot. Do not start Phase 5 and do not draft a full paper.
The mathematical mechanism is real in the tested affine Gaussian settings,
but broad novelty is weakened by prior solver-specific schedule literature,
and the strongest solver proxy lacks out-of-sample validation. A short
methodological note may become defensible after expert proof review and a
pre-specified external validation family, but adding such a family is outside
Phase 4.

## Exclusions and invalidated outputs

No mixture result supports this conclusion. Dimension 8 mixture evidence
remains invalid for decisions. Dirty Phase 3 artifacts are historical
comparison inputs only. All dirty smoke outputs, superseded Phase 3 analyses,
and failed diagnostics remain recorded and excluded. No completed run was
overwritten.
