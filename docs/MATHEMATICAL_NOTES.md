# Mathematical notes

This file indexes derivations used by the project.
Exact velocity fields are allowed only after a derivation here is checked
against a retrieved source or labeled as an original derivation.

## Path taxonomy

Keep these classes separate:

1. Independent coupling paths
2. Deterministic transport couplings
3. Gaussian optimal transport paths
4. Schedule reparameterizations

Do not call a path optimal transport unless the coupling and displacement
interpolation are mathematically valid.

## Notation conversion

Different papers use different conventions for `(alpha_t, sigma_t)`, score
parameterizations, and time direction. After paper retrieval, record:

- source equation numbers
- mapping between symbols
- endpoint conventions at `t = 0` and `t = 1`
- whether noise is multiplicative on `(x_1 - x_0)` or on a standard Gaussian

## Exact field checklist

For each exact field:

1. Write the derivation in this file or a linked note.
2. Cite the source or label it as original.
3. Add a symbolic or automatic differentiation check.
4. Add a continuity equation consistency test when practical.
5. Add a Monte Carlo moment evolution test.

## Derivation index

| field ID | path | source/target | status | note path |
| --- | --- | --- | --- | --- |
| (none yet) | | | pending | |

## Proof workflow

Proposition notes live in `papers/notes/propositions/`.
Allowed proof statuses: `sketch`, `partially verified`, `numerically checked`,
`source verified`, `needs expert review`.
Never use `proved` unless the user explicitly approves after manual review.
