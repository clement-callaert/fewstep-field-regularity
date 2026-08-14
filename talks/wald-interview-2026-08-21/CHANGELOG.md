# Change log: 12-slide Wald revision

Date: 2026-08-13.

Rewrite of `fewstep_wald_talk.tex` from a 10-slide Madrid + beaver deck
into a 12-slide scientific narrative. Geometry remains 4:3. The paper in
`paper/gddl2026/` was not modified. Frozen numbers are unchanged.

## Promoted into the main narrative

- Flow Matching and Conditional Flow Matching (new main slides 2--3).
  These foundations were not in the previous appendix; they are taken
  from Lipman et al., ICLR 2023, eqs. (5) and (9) and Theorem 2, plus
  the Albergo interpolant used by the manuscript.
- Affine Gaussian field with dimensions (former backup affine slide):
  now main slide 5.
- Grid-aware Euler construction: formerly a conceptual picture plus four
  bullets; now main slide 10 with the Proposition 1 formulas
  (\(\epsilon_N\), integrals, exact Euler product).

## Replaced

- Title-slide manuscript / venue-acceptance disclaimer: removed.
- Internal ledger language (`P4-C1`, `under-test`): removed.
- Former scope slide titled around what is "not established": replaced by
  slide 11, `Scope and limitations`.
- Former final slide (`The transferable object is the question, not the
  theorem`): replaced by slide 12, `Conclusion`.

## Moved to the technical appendix

Former `Backup:` slides are now A1 through A13, excluded from the `n/12`
counter by `appendixnumberbeamer`:

- equal-NFE accounting
- remaining affine derivation notes
- Gelbrich \(\mathrm{W}_2\) and \(|r_i|\)
- Euler / Heun local defects
- precision audit
- all 14 inversion margins
- non-centered replication
- solver-path interaction
- strongest-block modal split
- Chen et al. Def. 3.2 versus this ranking experiment
- exponential integrators
- expanded CTMC analogy
- full references
