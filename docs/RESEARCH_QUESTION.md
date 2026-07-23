# Research question

Which notions of field regularity reliably predict fixed-budget discretization
error across probability paths, solvers, dimensions, and target geometries?

## Scope

This project builds a controlled, reproducible benchmark relating field
regularity metrics to fixed-NFE distributional error for continuous-time
generative models on exact Gaussian and Gaussian mixture test problems.

## Non-goals

- Do not assume that a counterexample exists.
- Do not optimize experiments to disprove any paper.
- Do not claim novelty before completing a literature comparison.
- Do not claim a theorem unless every mathematical step has been independently
  checked and the user approves a proved status.
- Do not claim an empirical result unless its full provenance is available.

## Registered hypotheses

These statements are hypotheses, not conclusions.

### H1

Lower averaged global Lipschitzness is associated with lower fixed-NFE
Wasserstein error.

### H2

Path-distribution-weighted local Jacobian metrics predict fixed-NFE error
better than global worst-case metrics.

### H3

Temporal stiffness and Jacobian variation explain errors not captured by
spatial Lipschitzness.

### H4

Metric rankings may change across solvers and target geometries.

## Primary outcome

Fixed-NFE Wasserstein error, with exact Gaussian W2 when available, and
calibrated empirical estimators otherwise.

## Process constraints

1. Register hypotheses and the decision gate before the gate benchmark.
2. Prefer exact analytical settings before empirical estimators.
3. Compare solvers at equal NFE, not equal step count.
4. Report nested and stratified correlations, not only pooled Spearman.
5. Mark surprising results unverified until the safety checklist passes.
