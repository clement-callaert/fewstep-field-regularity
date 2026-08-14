# Empirical audit

Audit date: 2026-08-13.
Source artifacts: frozen JSON under `outputs/`, checksums in `paper/gddl2026/artifact_aliases.json`.

## Design

Source `N(0,I)`. Targets: anisotropic (condition number 4) and low-rank (`FF^T+0.05 I`, rank 2, geometry seed 271828). Dimensions 2 and 8. Paths: linear `(1-t,t)` and trigonometric VP. Solvers: Euler, Heun, RK4. NFE in {8,16,32} with equal-NFE accounting. 72 rows, 36 blocks.

Inversion definition used here: in a two-path block, the strict `R` ordering disagrees with the strict `W_2` ordering. There were no ties.

These 14 of 36 and 11 of 18 figures are descriptive benchmark counts. They are not estimates of a population probability.

## Centered grid

Independent grouping of `phase4_gaussian_reproduction_2026-07-24-v1:results` yields 14 inversions:

| family | dim | solver | NFE | R prefers | W2 prefers | W2 margin |
| --- | --- | --- | --- | --- | --- | --- |
| anisotropic | 2 | heun | 8 | VP | linear | 1.9053104102e-3 |
| anisotropic | 2 | heun | 16 | VP | linear | 1.9398061047e-3 |
| anisotropic | 2 | heun | 32 | VP | linear | 6.6344393985e-4 |
| anisotropic | 8 | heun | 16 | VP | linear | 1.7589416768e-3 |
| anisotropic | 8 | heun | 32 | VP | linear | 7.6281733407e-4 |
| low-rank | 2 | heun | 8 | VP | linear | 1.8362512506e-2 |
| low-rank | 2 | heun | 16 | VP | linear | 6.0399251342e-3 |
| low-rank | 2 | heun | 32 | VP | linear | 1.6980345740e-3 |
| low-rank | 2 | rk4 | 8 | VP | linear | 1.5167218273e-3 |
| low-rank | 2 | rk4 | 16 | VP | linear | 1.2899810362e-4 |
| low-rank | 2 | rk4 | 32 | VP | linear | 1.1188920612e-5 |
| low-rank | 8 | euler | 8 | linear | VP | 3.5437610358e-1 |
| low-rank | 8 | euler | 16 | linear | VP | 2.0469460968e-1 |
| low-rank | 8 | euler | 32 | linear | VP | 1.0965760680e-1 |

Strongest block: low-rank, d=8, Euler, NFE 8. Values match the workshop table to the printed 10 digits. Relative W2 gap is 77.63 percent, not a canonical 78 percent.

Every inversion keeps the same W2 ordering under the 80-digit reference. The smallest margin is 11528 times the global max float64-vs-80-digit W2 gap `9.7050430488e-10`. Using the pair-specific gap the ratio is larger.

## Solver-path interaction

On all 18 low-rank primary blocks, Euler prefers VP and Heun/RK4 prefer linear at equal NFE. This is a grid observation, not a universal schedule rule. Anisotropic blocks do not follow that Euler/Heun/RK4 split (anisotropic inversions are Heun-only in the primary grid).

Robustness (`phase4_robustness_2026-07-24-v1`, post-hoc): 66 low-rank blocks covering +/-10 percent target perturbations and NFE 64 and 128 at zero perturbation. The same Euler-VP / Heun-RK4-linear pattern holds on all 66. Analysis status in the artifact is `post-hoc`.

## Non-centered replication

Plan file dated 2026-07-24, commit `f5e857c` at 15:28. Amendment A1 (endpoint moment gap) `508101e` at 15:33. Results `8b87c7f` at 16:04. The family (means, anisotropy 6, grid) was specified before results. A1 changed a sanity check, not the family. Calling this "pre-registered" is fair for the family and grid; it is not a clinical-trial protocol.

Independent recount: 11 of 18 inversions. `R` prefers VP with margin 0.7513149036 on every block (`R` ignores `c(t)`). W2 prefers linear on the 11 inverted blocks. All 11 pass the 80-digit audit (max difference `2.0688e-11`; smallest inverted margin `1.4234e-6`). Drift offset is nonzero by construction and by validation flags.

The family remains Gaussian, diagonal, and commuting.

## Proxies

On the same 36 blocks, baseline `R` agrees with W2 preference in 22 blocks. The solver-specific leading local-error proxy agrees in 29 blocks (14 of 18 low-rank). This comparison is post-hoc and in-sample. Exact transported defects reconstruct endpoint factor error by identity.

## Chronology of the 14 inversions

Inversions were first listed in the registered Phase 3 gate, then the 72-row Gaussian grid was frozen and rerun from clean code as Phase 4 Run 1. Diagnostics, decomposition, and robustness are post-hoc relative to that gate. The non-centered family is a later supporting replication, not a second discovery pass on the same design.

## Terms

| Term | What the repository actually establishes |
| --- | --- |
| registered | Phase 3/4 configs and artifact IDs frozen in git |
| pre-registered | non-centered family written down before its result commit |
| replication | one additional commuting Gaussian family |
| audit | checksummed 80-digit and validation JSON, plus this recount |
| robustness | post-hoc perturbations and extra NFE |
| independent | this 2026-08-13 recount; not a second lab |
