# Phase 3 analysis plan

Frozen at: 2026-07-23T16:10:12Z

Gate version: 2026-07-23-v1

Status: Frozen before the Phase 3 smoke and main gate runs.

## Grid

The target families are anisotropic Gaussian, low-rank Gaussian, two-mode
GMM, and imbalanced GMM. Dimensions are 2 and 8. Paths are linear and
variance-preserving. Solvers are Euler, Heun, and RK4. NFE budgets are 8, 16,
and 32. These budgets are divisible by the field evaluation count of every
solver.

The ten registered seeds are 0 through 9. They apply to mixture endpoint
samples, sliced Wasserstein projections, and mixture metric estimates.
Gaussian endpoint error is computed from analytical moments after applying the
numerical solver map. It does not require seed replication.

The primary mixture estimator uses 256 endpoint samples and 64 sliced
projections. Estimator sensitivity uses 32, 64, and 128 projections on the
same endpoint samples. Phase 2 calibration artifact
`phase2_calibration:calibration_table` is the readiness reference. Sliced
Wasserstein is an empirical diagnostic. It is not exact W2. Gaussian targets
use exact Gaussian W2 on analytical moments.

## Metrics

The primary baseline is `averaged_squared_lipschitz_proxy`.

The alternatives are:

- `path_weighted_expected_jacobian_norm`
- `expected_squared_jacobian_norm`
- `jacobian_temporal_variation`

Mixture metrics use 24 time points. The primary estimator budget is 128 state
samples per time. Budget sensitivity uses 32 and 128 samples. Gaussian
Jacobians are state independent and use the same 24-point time grid.

## Sampling and nesting

The configuration sampling unit is
`(target_family, path, solver, dim, nfe)`. Seed rows are repeated estimates
nested inside that unit. Metric rows retain the full identifier
`(target_family, path, solver, dim, nfe, seed, metric_name)`.

The primary configuration summary is the median over seeds. Bootstrap
resampling draws configuration units within target family. It never resamples
seed rows as independent configurations.

## Registered correlations

Spearman correlation uses configuration medians. The analysis reports:

- global Spearman
- per-target-family Spearman
- per-solver Spearman
- leave-one-family-out Spearman
- the mean of held-out family Spearman values

Metric improvement is the alternative signed Spearman minus the baseline
signed Spearman. The registered held-out improvement is the difference between
the mean per-family Spearman values. A paired stratified bootstrap resamples
the same configuration units for both metrics and reports a percentile
95 percent confidence interval from 2,000 replicates.

Condition 1 holds only when the improvement is at least 0.15 and the interval
lower bound is above zero.

## Ranking inversions

Within each `(target_family, solver, dim, nfe)` block, the two paths define one
pair. An inversion occurs when the baseline metric difference and error
difference have opposite nonzero signs. A family is reproducible only when
one direction appears in at least 8 of 10 mixture seeds, or when an analytical
Gaussian comparison has that direction, and the direction remains under all
available estimator checks. Condition 2 requires at least two reproducible
families.

## Interactions

A schedule-by-solver interaction occurs when the lower-error path changes
between solvers inside a matched `(target_family, dim, nfe)` block. A
schedule-by-geometry interaction occurs when the lower-error path changes
between target families inside a matched `(solver, dim, nfe)` block. A
stochastic interaction is stable only when its direction appears in at least
8 of 10 seeds.

Condition 3 also requires a short mathematical explanation based on solver
order, local truncation terms, or target geometry. An unexplained interaction
does not satisfy the condition.

## Other analyses

H3 residual analysis reports Spearman correlation between each temporal metric
and residual error ranks after a linear fit on baseline metric ranks. It is
diagnostic and does not replace the gate criteria.

Sensitivity tables repeat configuration summaries by dimension, NFE, solver,
target family, mixture metric estimator budget, and sliced projection budget.
Mixture estimator stability also compares per-seed sliced Wasserstein rankings
and the registered Phase 2 sliced versus discrete calibration diagnostic.

Condition 4 is false unless a separate proposition note meets the registered
workflow. No proposition is assumed in this plan.

## Minimality

Four families allow family-held-out and two-family inversion checks. Two paths
are the smallest schedule comparison. Three solver orders permit the
higher-order pivot check. Two dimensions permit dimension sensitivity. Three
equal-NFE budgets permit budget trends. The design omits dimension 32, NFE 4
and 64, Gaussian OT, Lipschitz-guided endpoint regularization, eight-mode GMM,
and the full Cartesian Phase 5 grid.

The subgrid can test all four continue conditions. It does not claim power for
every target geometry or dimension.

## Immutable inputs

The analysis reads only the exact artifacts listed in
`configs/analysis/phase3_gate.yaml`. No result directory scan is allowed.
No continue or pivot threshold may change after the main run.
