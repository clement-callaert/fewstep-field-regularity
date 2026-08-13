# Averaged Jacobian Regularity Does Not Order Few-Step Error in Flow Matching: A Certified Gaussian Counterexample

Clément Callaert (CentraleSupélec and Université Paris-Saclay)

Preprint sources: [`paper/arxiv/`](paper/arxiv/README.md). No arXiv identifier is assigned yet. Do not invent one.

**Abstract.** Flow matching and stochastic interpolants specify a probability flow ODE whose few-step sampling error depends on the sampling schedule. Schedule design therefore needs an a priori criterion. Chen, Vanden-Eijnden, and Xu propose minimizing the averaged squared Jacobian norm $A_2$, a Lipschitz constant of the marginal field, as a selection criterion, without a proved bound on discretization error. This paper asks whether the order induced by $A_2$ between two paths is reliable at a fixed number of function evaluations (NFE). Already for centered Gaussian interpolants the implication fails. A certified one-dimensional Heun counterexample, a three-regime census, and an inversion map over target variance are given. The analysis is confined to commuting Gaussians; no learned field is used.

```bibtex
@misc{callaert2026averaged,
  title={Averaged Jacobian Regularity Does Not Order Few-Step Error in Flow Matching: A Certified {G}aussian Counterexample},
  author={Callaert, Cl{\'e}ment},
  year={2026},
  note={Preprint. Source: https://github.com/clement-callaert/fewstep-field-regularity},
}
```

GitHub also exposes this entry via [`CITATION.cff`](CITATION.cff).

---

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
python scripts/run_in_family_comparison.py
python scripts/run_arxiv_stats.py
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
