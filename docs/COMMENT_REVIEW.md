# Comment and docstring review

Presentation-only audit of comments and docstrings under `src/`,
`scripts/`, and `tests/`. Scientific behavior, numeric literals in
code logic, and artifact bytes were not changed.

## Standard applied

- Plain declarative English; one idea per sentence.
- No em-dashes (Unicode or prose `---`), emojis, or decorative separators.
- Comments state what the code does and why; no self-praise.
- No commented-out dead code found.
- Numerical claims in comments cite an artifact ID or derivation doc, or are reworded.
- Substantive docstrings use Inputs, Outputs, Units, Precision/NFE in that order.

## Summary

- Python files in scope: 90
- Files with at least one rewrite: 38
- Total comments/docstrings rewritten: 125
- Comments deleted (old text removed): 10

## Files touched

| File | Comments/docstrings rewritten |
| --- | ---: |
| `scripts/make_workshop_figures.py` | 8 |
| `scripts/retrieve_papers.py` | 2 |
| `scripts/validate_artifacts.py` | 1 |
| `src/fewstep_regularities/analysis/correlation.py` | 1 |
| `src/fewstep_regularities/analysis/precision.py` | 1 |
| `src/fewstep_regularities/artifacts/writer.py` | 8 |
| `src/fewstep_regularities/distributions/base.py` | 6 |
| `src/fewstep_regularities/distributions/gaussian.py` | 8 |
| `src/fewstep_regularities/distributions/gaussian_mixture.py` | 1 |
| `src/fewstep_regularities/evaluation/base.py` | 4 |
| `src/fewstep_regularities/evaluation/gaussian_w2.py` | 4 |
| `src/fewstep_regularities/evaluation/projected_sliced.py` | 12 |
| `src/fewstep_regularities/experiments/estimator_calibration.py` | 2 |
| `src/fewstep_regularities/experiments/factories.py` | 1 |
| `src/fewstep_regularities/experiments/gate_benchmark.py` | 1 |
| `src/fewstep_regularities/experiments/gaussian_exact.py` | 4 |
| `src/fewstep_regularities/experiments/workshop_external_validation.py` | 7 |
| `src/fewstep_regularities/fields/base.py` | 3 |
| `src/fewstep_regularities/fields/gaussian_affine.py` | 2 |
| `src/fewstep_regularities/fields/gaussian_ot_field.py` | 2 |
| `src/fewstep_regularities/fields/mixture_affine.py` | 1 |
| `src/fewstep_regularities/metrics/base.py` | 4 |
| `src/fewstep_regularities/paths/base.py` | 7 |
| `src/fewstep_regularities/paths/gaussian_ot.py` | 3 |
| `src/fewstep_regularities/paths/lipschitz_guided.py` | 6 |
| `src/fewstep_regularities/paths/scalar_schedule.py` | 2 |
| `src/fewstep_regularities/solvers/base.py` | 4 |
| `src/fewstep_regularities/solvers/common.py` | 6 |
| `tests/analytical/test_external_validation_family.py` | 1 |
| `tests/analytical/test_fields.py` | 4 |
| `tests/analytical/test_gaussian_mixtures.py` | 1 |
| `tests/analytical/test_mixture_fields.py` | 2 |
| `tests/analytical/test_paths.py` | 1 |
| `tests/analytical/test_solvers.py` | 1 |
| `tests/analytical/test_w2_metrics.py` | 1 |
| `tests/analytical/test_wasserstein_estimators.py` | 1 |
| `tests/integration/test_phase1_smoke.py` | 1 |
| `tests/unit/test_commit_attribution.py` | 1 |

## Files reviewed with no rewrite

These files were inspected; comments/docstrings already met the standard
or needed no change under the minimal-edit rule (for example short property
one-liners and `__init__.py` module strings).

- `scripts/__init__.py`
- `scripts/check_commit_attribution.py`
- `src/fewstep_regularities/__init__.py`
- `src/fewstep_regularities/analysis/__init__.py`
- `src/fewstep_regularities/analysis/affine_flow.py`
- `src/fewstep_regularities/analysis/local_error.py`
- `src/fewstep_regularities/analysis/propagation.py`
- `src/fewstep_regularities/artifacts/__init__.py`
- `src/fewstep_regularities/artifacts/manifest.py`
- `src/fewstep_regularities/cli/__init__.py`
- `src/fewstep_regularities/cli/main.py`
- `src/fewstep_regularities/distributions/__init__.py`
- `src/fewstep_regularities/evaluation/__init__.py`
- `src/fewstep_regularities/experiments/__init__.py`
- `src/fewstep_regularities/experiments/gate_analysis.py`
- `src/fewstep_regularities/experiments/mixture_exact.py`
- `src/fewstep_regularities/experiments/phase4_affine_audit.py`
- `src/fewstep_regularities/experiments/phase4_gaussian_reproduction.py`
- `src/fewstep_regularities/fields/__init__.py`
- `src/fewstep_regularities/fields/conditional.py`
- `src/fewstep_regularities/metrics/__init__.py`
- `src/fewstep_regularities/metrics/affine_gaussian.py`
- `src/fewstep_regularities/metrics/mixture_mc.py`
- `src/fewstep_regularities/paths/__init__.py`
- `src/fewstep_regularities/paths/linear.py`
- `src/fewstep_regularities/paths/schedules.py`
- `src/fewstep_regularities/paths/variance_preserving.py`
- `src/fewstep_regularities/solvers/__init__.py`
- `src/fewstep_regularities/solvers/euler.py`
- `src/fewstep_regularities/solvers/heun.py`
- `src/fewstep_regularities/solvers/rk4.py`
- `src/fewstep_regularities/utils/__init__.py`
- `src/fewstep_regularities/utils/environment.py`
- `src/fewstep_regularities/utils/hashing.py`
- `src/fewstep_regularities/utils/precision.py`
- `src/fewstep_regularities/utils/shapes.py`
- `tests/analytical/test_affine_flow_analysis.py`
- `tests/analytical/test_affine_propagation.py`
- `tests/analytical/test_gaussian_distributions.py`
- `tests/conftest.py`
- `tests/integration/test_phase2_smoke.py`
- `tests/integration/test_phase3_gate_smoke.py`
- `tests/integration/test_phase4_gaussian_reproduction.py`
- `tests/integration/test_smoke_dry_run.py`
- `tests/regression/test_phase3_equal_nfe.py`
- `tests/regression/test_validate_artifacts.py`
- `tests/unit/test_artifacts.py`
- `tests/unit/test_factories.py`
- `tests/unit/test_gate_correlations.py`
- `tests/unit/test_gaussian_w2_dtype.py`
- `tests/unit/test_hydra_config.py`
- `tests/unit/test_interfaces.py`

## Deleted comments

Each row is the old comment text that no longer appears in the tree.

| File | Deleted comment | Reason |
| --- | --- | --- |
| `tests/analytical/test_gaussian_mixtures.py` | `# Var along axis 0: E[x^2] = 0.5*((-2)^2+2^2) + 0.25 = 4 + 0.25` | Asserted a numerical variance without an artifact or derivation cite; replaced with a non-numeric description. |
| `tests/analytical/test_w2_metrics.py` | `# W2 between N(0,1) and N(2,4) is sqrt(4 + (1-2)^2) = sqrt(5) for 1D:` | Asserted a numerical W2 identity in a comment; replaced with a cite to docs/MATHEMATICAL_NOTES.md. |
| `tests/analytical/test_w2_metrics.py` | `# Bures^2 = (sqrt(s1)-sqrt(s0))^2 for 1D.` | Companion numerical formula line removed after the parent comment was cited to the derivation doc. |
| `tests/analytical/test_mixture_fields.py` | `# Analytical mean velocity of marginal mean: d/dt (sigma(t) m_1) = sigma' m_1` | Formula comment replaced by a one-sentence decision about the zero-mean equal two-mode case. |
| `tests/analytical/test_mixture_fields.py` | `# for zero-mean source; target mean is 0 for equal two-mode, so mean stays 0.` | Merged into the replacement decision sentence; redundant second line removed. |
| `src/fewstep_regularities/evaluation/projected_sliced.py` | `# softmin over j: f_i = eps log a_i - eps logsumexp_j (log K_ij + g_j/eps)` | Inline formula asserted epsilon scaling; replaced with a plain-English softmin description. |
| `src/fewstep_regularities/paths/lipschitz_guided.py` | `# α' = -0.5 (β^2)' / α` | Numerical coefficient asserted without a derivation cite; replaced with a chain-rule sentence. |
| `src/fewstep_regularities/paths/lipschitz_guided.py` | `# β' = 0.5 (β^2)' / β` | Numerical coefficient asserted without a derivation cite; replaced with a chain-rule sentence. |
| `src/fewstep_regularities/paths/lipschitz_guided.py` | `# d/dt β^2 = M^t log(M) / (M - 1)` | Formula annotation rewritten as a full sentence without Unicode beta notation. |
| `scripts/make_workshop_figures.py` | `# All fourteen blocks: \|W2 margin\| of the inversion, log scale.` | Asserted a result count; replaced with wording that cites the inversion artifact instead. |

## Notes

- No commented-out dead code blocks were present; none were deleted for that reason.
- Protocol bases and key APIs were normalized to Inputs/Outputs/Units/Precision.
- Short accessors such as `dim`/`dtype` one-liners were left unchanged after review.
