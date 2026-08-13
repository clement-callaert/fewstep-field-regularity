# Reproducibility audit

Audit date: 2026-08-13.
Audited commit: `e48c9390e62b38f206342e6aeb7f160122ccc79c`.
Python: 3.11.15 in `.venv`. Device: CPU. Default dtype: float64.

## Chain

Paper claim (14 of 36 inversions)
-> `src/fewstep_regularities/experiments/phase4_gaussian_reproduction.py`
-> `recover_affine_solver_map` (`d+1` probes: 0 and e_i)
-> `propagate_gaussian_moments` then `gaussian_w2`
-> `AveragedSquaredLipschitzProxy` with `n_time=24`
-> `configs/experiment/phase4_gaussian_reproduction.yaml`
-> command `fewstep-regularities experiment=phase4_gaussian_reproduction` (frozen run 2026-07-24)
-> `outputs/phase4_gaussian_reproduction_2026-07-24-v1/results.json`
-> workshop Table 1 / Fig. 2, and arXiv tables generated from the same file.

## Commands executed (2026-08-13)

| Command | Estimate | Observed | Result |
| --- | --- | --- | --- |
| `.venv/bin/pytest -q` | minutes | 9.6 s | pass (full suite) |
| `.venv/bin/pytest tests/analytical/test_affine_flow_analysis.py` after adding exact Euler identity | seconds | (run with paper tests) | identity assertion added |
| `python scripts/validate_artifacts.py outputs/phase4_*` and workshop external | seconds | all seven OK | pass |
| Independent Python grouping of `results.json` | seconds | 14 of 36 | pass |
| Independent grouping of workshop `results.json` | seconds | 11 of 18 | pass |
| sympy Heun expansion | seconds | coefficient match | pass |
| mpmath P4-P1 identity | seconds | product equals e^L | pass |
| Registered Phase 4 rerun | seconds, needs clean tree | not run | existing artifacts validate and reconstruct; overwrite is forbidden |

No registered rerun was required. Dirty-tree protection would have blocked a release-ready rerun without a stash. That is a process constraint, not a scientific defect.

## Installation and precision

`requires-python >=3.11`. Dependencies bounded but not fully pinned (torch>=2.2, numpy>=1.26,<2.5, mpmath>=1.3). CI runs 3.11 and 3.12. Analytical path is float64; `test_gaussian_w2_dtype.py` rejects silent casts. Seeds: geometry seed 271828 for low-rank factors; endpoint maps are deterministic given the field. Manifests record commit, config hash, environment hash, and SHA-256.

## Equal-NFE

Observed `(solver, nfe, n_steps)`: Euler (8,8), (16,16), (32,32); Heun (8,4), (16,8), (32,16); RK4 (8,2), (16,4), (32,8). All rows have `nfe==actual_nfe`.

## Affine probes

`recover_affine_solver_map` integrates the batch `(0, e_1,...,e_d)` once. CountingField increments once per `evaluate`, so NFE is per vectorized field call, which is the intended equal-NFE accounting.

## Regularity scalar

`R` is trapezoidal quadrature of the spectral 2-norm squared of `A(t)` on 24 nodes. `baseline_metric_is_exact` is false in all 72 rows. This matches Lipschitz-guided Def 3.2 for state-independent Jacobians, up to quadrature.

## Mixture exclusion

Mixture runners and GMM configs exist. Phase 4 reproduction refuses non-Gaussian targets. Dim-8 mixture sliced-W2 failed post-result calibration (`docs/GATE_RESULT.md`). No mixture row enters the 14 of 36 or 11 of 18 counts.

## Discrepancies

| Observed | Expected | Cause | Scientific bug? | Action |
| --- | --- | --- | --- | --- |
| Docs "15 of 18" low-rank proxy | 14 of 18 | documentation arithmetic | no | correct docs; paper uses 29 of 36 |
| Workshop "78% larger" | 77.63% | rounding gloss | no | omit |
| Euler test lacked `oscillatory_factor == e^L` | identity | incomplete regression | no | assertion added |
| Outputs gitignored | public checksums | policy | no | appendix tables plus alias manifest |
| pyproject homepage URL | `clement-callaert` | stale | no | propose fix |

No discrepancy changes an inversion or a theorem.
