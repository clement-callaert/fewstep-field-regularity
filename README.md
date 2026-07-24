# fewstep-field-regularity

Active research software studying field-regularity criteria and
fixed-budget discretization error in continuous-time generative models
(probability-flow ODE sampling with a small number of function
evaluations).

The project provides exact Gaussian and calibrated mixture test cases,
fixed-step Euler/Heun/RK4 solvers with equal-NFE accounting, closed-form
Gaussian Wasserstein evaluation, and a reproducibility-first artifact
pipeline: every run writes a manifest with code commit, configuration
hash, environment hash, seeds, and SHA-256 output checksums, and runners
refuse dirty release-ready runs or overwrites of completed manifests.

Manuscript material derived from this repository is under review; no
accepted publication is claimed, and this page intentionally omits
submission details for the duration of the review period. Claim status is
governed by [docs/CLAIMS_LEDGER.md](docs/CLAIMS_LEDGER.md); no universal
metric, sampler, image, video, or world-model claim is made.

## Reproduction

Install:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pre-commit install
```

Default analytical precision is float64. Do not silently cast precision.

Run the checks and smoke validations:

```bash
pytest
fewstep-regularities experiment=smoke
python scripts/validate_artifacts.py outputs/phase0_smoke
```

Experiment configurations live under
[`configs/experiment`](configs/experiment); research-process documents
live under [`docs/`](docs). Completed run outputs validate with
`python scripts/validate_artifacts.py outputs/<run_id>`.

## Repository structure

```text
configs/                     Hydra configuration groups
docs/                        Research process documents
papers/                      Literature index and notes
scripts/                     Retrieval, validation, and figure utilities
src/fewstep_regularities/    Research package
tests/                       Unit, analytical, regression, integration tests
outputs/                     Run outputs with gitignored contents
artifacts/                   Optional curated artifacts
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Commits are created and pushed by
the repository owner only.
