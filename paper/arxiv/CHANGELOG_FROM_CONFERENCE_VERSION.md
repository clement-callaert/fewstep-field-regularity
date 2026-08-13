# Changes relative to the archived short draft

The short draft is stored at `paper/archive/gddl2026-conference/` as a
historical record. This file lists what the public article does
differently. It is not a submission note.

## Form

- Standard `article` class. No conference style file, no line numbers,
  no anonymous author block, no distribution footer.
- Author: Clément Callaert, CentraleSupélec and Université Paris-Saclay,
  `callaert.clement@gmail.com`.
- Full proofs, solver formulas, configuration details, and inversion
  tables are in appendices of this article. The short draft referred to a
  supplement that was not present in its directory.

## Claims and wording

- 14 of 36 and 11 of 18 are stated as descriptive counts on specified
  grids, not as population rates.
- The short-draft gloss that the strongest linear `W2` was "78% larger"
  is omitted. The article reports the pair
  `0.8108540111` versus `0.4564779075` and the margin `0.3543761036`.
- The 80-digit gap `9.7050430488e-10` is distinguished from the
  reconstruction residual `9.7050436884e-10`.
- The ratio of the smallest inversion margin to the 80-digit gap is the
  integer `11528` (floor of the exact quotient), not a rounded "more than
  11,500" slogan used as if it were a different number.
- `R` is identified as a 24-node trapezoidal quadrature of an exact
  integrand, recorded as non-exact in code.
- Ledger statuses are not upgraded: P4-C1 and P4-C2 remain `under-test`
  in `docs/CLAIMS_LEDGER.md`. The article uses reconstructed grid counts.

## Mathematics

- Affine field, commuting reduction, Gelbrich `W2`, telescoping identity,
  Euler and Heun leading coefficients, and the grid-aware Euler
  construction are written out with domains and quantifiers.
- The Euler construction is labeled grid-aware and is not offered as the
  mechanism of the Gaussian inversions.
- An 80-digit check that the oscillatory Euler product equals `e^L` is
  recorded in the appendix and in
  `tests/analytical/test_affine_flow_analysis.py`.

## Empirics

- Full inversion tables are generated from pinned JSON.
- Mixture exclusion is explained (dimension-8 mixture endpoint estimators
  failed post-result calibration; Phase 4 accepts Gaussian targets only).
- Non-centered family chronology includes Amendment A1 (endpoint sanity
  check only).
- Low-rank solver-path split is restricted to that family.

## Literature

- Search date 2026-08-13.
- Contemporaneous strain/vorticity and isokinetic-flow notes are cited
  with scope limits. No "to our knowledge" novelty slogan.

## What was not changed in substance

- The registered 72-configuration centered grid and the 18-block
  non-centered family.
- Frozen artifact checksums.
- The decision not to evaluate learned models, images, video, or
  world-model quantities.
