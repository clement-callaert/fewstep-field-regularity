# fewstep-field-regularity

Research software and manuscript for a controlled study of averaged
field-regularity criteria versus few-step Gaussian Wasserstein error on
commuting probability-flow ODEs.

The public preprint sources are in
[`paper/arxiv/`](paper/arxiv/README.md). Claim scope and status are
governed by [`docs/CLAIMS_LEDGER.md`](docs/CLAIMS_LEDGER.md). No markdown
or landing text may state a stronger claim than that ledger. No universal
metric, sampler, image, video, or world-model claim is made.

The project provides exact Gaussian test cases, fixed-step Euler/Heun/RK4
solvers with equal-NFE accounting, closed-form Gaussian Wasserstein
evaluation, and a reproducibility-first artifact pipeline: every run
writes a manifest with code commit, configuration hash, environment hash,
seeds, and SHA-256 output checksums, and runners refuse dirty
release-ready runs or overwrites of completed manifests.

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

```bash
pytest
fewstep-regularities experiment=smoke
python scripts/validate_artifacts.py outputs/phase0_smoke
```

Experiment configurations live under
[`configs/experiment`](configs/experiment). Research-process documents
live under [`docs/`](docs). Completed run outputs validate with
`python scripts/validate_artifacts.py outputs/<run_id>`.

Pinned Phase 4 artifacts used by the public manuscript are validated the
same way. Figure and table generators:

```bash
python scripts/make_arxiv_tables.py
python scripts/make_arxiv_figures.py
```

## Repository structure

```text
audit/                       Adversarial audit of commit e48c939 (2026-08-13)
configs/                     Hydra configuration groups
docs/                        Research process documents
paper/arxiv/                 Public preprint sources
paper/archive/               Historical short draft (not the public preprint)
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
