# Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow

- paper_id: `liu2022rectified_flow`
- authors: Xingchao Liu, Chengyue Gong, Qiang Liu
- year: 2022
- source_url: https://arxiv.org/abs/2209.03003
- local_filename: liu2022rectified_flow.pdf
- access_date: 2026-07-23
- sha256: see papers/manifest.json

## Relevance

Rectified flow and linear interpolation path.

## Formulas or results needed

- rectified flow ODE
- marginal preserving properties

## Notation differences

- Uses `X_t = t X_1 + (1-t) X_0` with independent coupling `π_0 × π_1` for the regression target.
- This is an independent-coupling straight path, not an OT coupling unless `(X_0, X_1)` is an OT plan.
- Project labels this path `linear` / independent coupling.

## Assumptions to check

- existence of velocity regression target
- no requirement of Gaussian endpoints for the learning objective
- Phase 1 exact fields use Gaussian endpoints for closed forms

## Project satisfies assumptions?

Linear path definition applies generally. Exact marginal velocity in Phase 1 requires Gaussian formulas from SI/Lipschitz notes.

## Replication status

formulas-extracted-phase1

## Extracted equations

Source: local PDF page 4, eq. (1).

Linear interpolation:

`X_t = t X_1 + (1-t) X_0`

Regression objective for drift `v`:

`min_v ∫_0^1 E[∥(X_1 - X_0) - v(X_t, t)∥^2] dt`

Conditional velocity along a fixed pair is `X_1 - X_0` (constant). Marginal velocity is `E[X_1 - X_0 | X_t]`.
