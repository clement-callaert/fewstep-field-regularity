# Changes relative to the archived short draft

The short draft is stored at `paper/archive/gddl2026-conference/` as a
historical record. This file lists what the public article does
differently. It is not a submission note.

## Structure (2026-08-13 restructure)

- Title: *Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching
  Schedules: A Certified Gaussian Counterexample* (canonical; the retired
  wording began “Few-Step Flow-Matching Error Can Be Misranked...”).
- Body: Abstract, Introduction, Definitions, certified inversion, local
  error, grid-aware theorem, finite enumeration, Related work,
  Limitations, Conclusion. Reproducibility is an appendix.
- Experiments are split by question. VP versus Chen Example 3.3 scalar
  ($M=\lambda_{\max}$) is a post-hoc shared-schedule pairwise count: 9 of 36
  tested blocks, 4 of 12 cells. The 36 of 36 per-mode count is a
  four-candidate finite enumeration, not a global $W_2$ optimality theorem.
- The manuscript reports hierarchical descriptive counts. The $N=50$
  redraw of the low-rank factor is a descriptive 50/50 fraction on the
  sampled geometries, not a population interval and not a $p$-value on
  deterministic $R$ or $W_2$.

## Form

- Standard `article` class. No conference style file, no line numbers,
  no anonymous author block, no distribution footer.
- Author: Clément Callaert, CentraleSupélec and Université Paris-Saclay,
  `callaert.clement@gmail.com`.
- Full proofs, solver formulas, configuration details, and inversion
  tables are in appendices of this article. The short draft referred to a
  supplement that was not present in its directory.

## Claims and wording

- The leading logical result is a one-dimensional Gaussian Heun
  counterexample (exact `R` integrals, exact rational linear factor,
  rational VP certificate in `Q[pi, sqrt(2)]`).
- Headline linear-versus-VP inversions are 5 of 12 geometry×solver cells
  (4 of 12 at every NFE in {8,16,32}), from three distinct R comparisons.
  The 14 inverted solver-budget rows remain an appendix listing, not a
  headline. 11 of 18 non-centered blocks remain a hierarchical descriptive
  count, not a population rate.
- Headline regularity is the continuous integral `R`. The 24-node
  trapezoidal estimator is written `Rhat_24` and is an implementation check
  only. On the registered grid the path-ordering sign agrees; inversion
  counts are unchanged. The strongest-row pair is
  `R = 2.9441044083` vs `4.7305438136` (not the workshop `Rhat_24` pair
  `2.9476523251` vs `4.7295206355`).
- The short-draft gloss that the strongest linear `W2` was "78% larger"
  is omitted. The article reports `W2` `0.8108540111` versus `0.4564779075`
  and the margin `0.3543761036`.
- The 80-digit gap `9.7050430488e-10` is distinguished from the
  reconstruction residual `9.7050436884e-10`.
- The ratio of the smallest inversion margin to the 80-digit gap is the
  integer `11528`.
- Ledger: P4-P2 is `supported` (existence). P4-C1, P4-C2, and P4-C4 remain
  `under-test`. Robustness is labeled post-hoc. The non-centered family is
  a pre-specified stress test, not an independent replication.

## Mathematics

- Interpolant boundary conditions, isotropic-source commutation, and the
  telescoping identity without a non-vanishing hypothesis are written out.
- The Euler construction is labeled grid-aware and is not offered as the
  mechanism of the Gaussian inversions. Appendix C restores the analytical
  proof (endpoint matching, `cos^2` integral, grid evaluation, Euler
  factors `1+L/N`, and `(1+L/N)^N < exp(L)`). The 80-digit check remains a
  test, not the proof.

## Empirics

- Full inversion tables are generated from pinned JSON plus continuous `R`.
- Non-centered `W2^2` is split into mean and Bures terms.
- Mixture exclusion is explained (dimension-8 mixture endpoint estimators
  failed post-result calibration; Phase 4 accepts Gaussian targets only).
- Low-rank solver-path split is restricted to that family. The 66-block
  robustness count is `2 x 3 x (3 x 3 + 2)`.

## Literature

- Search date 2026-08-13.
- Lipschitz-guided design, Stéphanovitch, Gupta et al., Du et al., Yuan et
  al., Tao-Choi, Khan, Align Your Steps, EDM, DPM-Solver, DEIS are
  positioned by the object they control. Search absence is not a proof that
  no related example exists.

## What was not changed in substance

- The registered 72-configuration centered grid and the 18-block
  non-centered family.
- Frozen artifact checksums.
- The decision not to evaluate learned models, images, video, or
  world-model quantities.
