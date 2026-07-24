# fewstep-field-regularity

> **Status of this file**: post-review landing page, to be swapped in as
> `README.md` by the repository owner only once the double-blind review
> policy permits. Until then the public `README.md` stays venue-silent.

Research status: Focused Phase 4 completed, including a pre-registered
non-centered replication. A workshop submission has been prepared. All
exact Gaussian inversions reproduced and passed the precision audit. No
universal metric, sampler, image, video, or world-model claim is made. No
acceptance is claimed.

A reproducible benchmark of field regularity metrics and few-step
discretization error in continuous-time generative models.

## 1. Main finding

In the tested commuting Gaussian generative flows, ordering probability paths
by averaged squared Jacobian regularity does not determine their fixed-NFE
Gaussian Wasserstein error ordering. Fourteen ranking inversions reproduced
from clean code across exact anisotropic and low-rank Gaussian targets, Euler,
Heun, and RK4.

This is a controlled limitation result. It does not show that regularity-based
schedule design fails universally, that one path is universally preferable,
or that the repository provides a new sampler or universal error predictor.

## 2. Mathematical mechanism

For the centered Gaussian path

\[
X_t=\alpha(t)X_0+\sigma(t)X_1,\qquad
X_0\sim N(0,I),\quad X_1\sim N(0,\Sigma_1),
\]

the covariance and marginal drift are

\[
Q(t)=\alpha(t)^2I+\sigma(t)^2\Sigma_1,\qquad
b(t,x)=A(t)x,\qquad A(t)=\tfrac12Q'(t)Q(t)^{-1}.
\]

The commuting system decomposes into scalar covariance eigenmodes. Each mode
has an exact one-step factor, while a numerical factor depends on solver stage
locations. The endpoint factor difference is exactly a sum of signed local
defects transported by earlier numerical and later exact transitions. An
unsigned time average of Jacobian magnitudes discards the stage sampling,
time derivatives, defect signs, cancellation, and endpoint transport that
enter this identity.

See
[docs/PHASE4_MATHEMATICAL_ANALYSIS.md](docs/PHASE4_MATHEMATICAL_ANALYSIS.md).

## 3. Strongest inversion

The strongest reproduced inversion is the low-rank Gaussian target in
dimension 8 with Euler at NFE 8:

| path | averaged regularity | Gaussian W2 |
| --- | ---: | ---: |
| linear | 2.9476523251 | 0.8108540111 |
| variance-preserving | 4.7295206355 | 0.4564779075 |

The regularity baseline prefers the linear path, while endpoint error prefers
the variance-preserving path. The W2 margin is `0.3543761036`. The smallest
surviving inversion margin is `1.1188920612e-5`, more than 11,500 times the
maximum float64 versus 80-digit W2 difference of `9.7050430488e-10`.

Source artifacts:
`phase4_gaussian_reproduction_2026-07-24-v1:results` and
`phase4_precision_2026-07-24-v1:table`.

## 4. P4-P1 proposition status

The minimal Euler non-implication proposition P4-P1 is **proof verified**
after a documented internal adversarial proof audit completed on
2026-07-24. For every
\(L>0\) and integer \(N\geq1\), an explicit smooth scalar construction gives
two fields with the same exact endpoint, a strictly larger averaged squared
Jacobian for one of them, an exact fixed-grid left-endpoint Euler solution
for the higher-regularity field, and strictly positive Euler error for the
constant field.

The construction is grid-aware: the oscillatory coefficient depends on
\(N\), so it establishes a logical non-implication for fixed-grid
left-endpoint Euler, not a mechanism for every Gaussian inversion and not a
uniform counterexample over all grids or solvers. See
[docs/P4_P1_PROOF_AUDIT.md](docs/P4_P1_PROOF_AUDIT.md).

## 5. Reproduction

Install the package:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pre-commit install
```

Default analytical precision is float64. Do not silently cast precision.

Run the smoke validations:

```bash
pytest
fewstep-regularities experiment=smoke
python scripts/validate_artifacts.py outputs/phase0_smoke
fewstep-regularities experiment=phase1_smoke
python scripts/validate_artifacts.py outputs/phase1_smoke
fewstep-regularities experiment=phase2_smoke
python scripts/validate_artifacts.py outputs/phase2_smoke
```

Validate the six release-ready Phase 4 runs:

```bash
for run in \
  phase4_gaussian_reproduction_2026-07-24-v1 \
  phase4_precision_2026-07-24-v1 \
  phase4_decomposition_2026-07-24-v1 \
  phase4_diagnostics_2026-07-24-v1 \
  phase4_robustness_2026-07-24-v1 \
  phase4_final_validation_2026-07-24-v1
do
  python scripts/validate_artifacts.py "outputs/${run}"
done
```

The resolved Phase 4 experiment configurations are under
[`configs/experiment`](configs/experiment). The runners refuse dirty
release-ready runs and refuse to overwrite completed manifests.

## 6. Release-ready Phase 4 artifacts

| artifact ID | SHA-256 |
| --- | --- |
| `phase4_gaussian_reproduction_2026-07-24-v1:results` | `b8930142cba5655ee553aae5ff400cd884c1137e77547d9a5fa94bd4e354973f` |
| `phase4_precision_2026-07-24-v1:table` | `5f8800a697c61c2eab2306281fe4fb1b01dee67bc3c678dd7ba4a626d9dc8e1b` |
| `phase4_decomposition_2026-07-24-v1:table` | `690d068c3693f99f38ddb17b479ab0e63b5ad859835f2092c5420175d954f252` |
| `phase4_diagnostics_2026-07-24-v1:table` | `5c5a1e4c1c47ef254b13559ef13c187d24c9f1e79a17454974d55f9348565ba1` |
| `phase4_robustness_2026-07-24-v1:table` | `3cace6e3d016f0c3e893a656fb76acfad11ce4569debc6ea418fe5aeec7d6306` |
| `phase4_final_validation_2026-07-24-v1:table` | `771ff7cbb02c4368b0601cc11d3e02fcdfaac5d964059e5846d62c25b7a0c4c9` |

Every manifest records the producing commit, configuration hash, code status,
command, environment, source hashes, output hashes, and release-ready status.
See [docs/PHASE4_RESULTS.md](docs/PHASE4_RESULTS.md) and
[docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

## 7. Workshop paper status

A four-page anonymized non-archival short paper, *When Averaged Field
Regularity Fails to Rank Few-Step Generative Paths*, was prepared as a
controlled limitation and reproducibility study for the Geometric
Distributional Deep Learning workshop at NeurIPS 2026 (submission
deadline August 29, 2026 AoE). The paper claims are frozen in
[docs/WORKSHOP_PAPER_CLAIMS.md](docs/WORKSHOP_PAPER_CLAIMS.md), the target
audit is [docs/WORKSHOP_TARGETS.md](docs/WORKSHOP_TARGETS.md), and the
outline is [docs/WORKSHOP_PAPER_OUTLINE.md](docs/WORKSHOP_PAPER_OUTLINE.md).
No workshop acceptance is claimed.

The contribution is an exact commuting Gaussian analysis, a reproducible
audit of fourteen regularity-ranking inversions with a pre-registered
non-centered replication (11 of 18 comparison blocks), and an audited
grid-aware scalar non-implication construction
([docs/P4_P1_PROOF_AUDIT.md](docs/P4_P1_PROOF_AUDIT.md)). No broad
Phase 5 experiment has started.

## 8. Claims and limitations

The research question is:

> Which notions of field regularity reliably predict fixed-budget
> discretization error across probability paths, solvers, dimensions, and
> target geometries?

Current claim status is governed by
[docs/CLAIMS_LEDGER.md](docs/CLAIMS_LEDGER.md). In particular:

- H2 is contradicted for the registered alternative metrics.
- H1 and H3 remain inconclusive.
- The Phase 4 result is limited to tested exact commuting Gaussian systems,
  linear and variance-preserving paths, Euler, Heun, and RK4.
- The solver-specific proxy is post-hoc and in-sample. It is not a claim of
  predictive superiority.
- The explicit scalar construction is grid-aware and passed the documented
  internal adversarial proof audit.
- No learned neural field, image benchmark, video benchmark, or mixture result
  supports the Phase 4 conclusion.
- Absence of an exact match in the literature audit does not establish
  novelty.

## 9. Excluded evidence

- The registered Phase 3 main run has dirty-code provenance. It is retained as
  a comparison input and is not release-ready.
- Dimension 8 mixture evidence failed the post-result estimator calibration
  diagnostic and is excluded from decisive claims.
- No mixture result supports the Phase 4 conclusions.
- Dirty smoke outputs, superseded Phase 3 analyses, and failed diagnostics are
  preserved for audit but excluded from release tables and figures.
- No completed run has been overwritten.

## 10. Citation status

The workshop manuscript and archival citation record are not yet available.
Do not cite the repository as evidence for a universal metric, a universal
schedule ordering, or a new sampler. Numerical results should be cited only
with their artifact IDs and the scope stated above.

Primary literature records and section-level overlap notes are in
[docs/PHASE4_LITERATURE_AUDIT.md](docs/PHASE4_LITERATURE_AUDIT.md). Papers are
retrieved only from legal public sources and indexed in
[`papers/README.md`](papers/README.md).

## 11. Repository structure

```text
configs/                     Hydra configuration groups
docs/                        Research process documents
papers/                      Paper index, PDFs, notes
scripts/                     Retrieval and validation utilities
src/fewstep_regularities/    Research package
tests/                       Unit, analytical, regression, integration tests
outputs/                     Run outputs with gitignored contents
artifacts/                   Optional curated artifacts
```
