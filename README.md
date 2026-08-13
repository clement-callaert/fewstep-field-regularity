# Averaged Jacobian Regularity Does Not Order Few-Step Error in Flow Matching: A Certified Gaussian Counterexample

arXiv: [TODO-ARXIV-ID](https://arxiv.org/abs/TODO-ARXIV-ID)

**Abstract.** Flow matching and stochastic interpolants specify a probability flow ODE whose few-step sampling error depends on the sampling schedule. Schedule design therefore needs an a priori criterion. Chen, Vanden-Eijnden, and Xu propose minimizing the averaged squared Jacobian norm $A_2$, a Lipschitz constant of the marginal field, as a selection criterion, without a proved bound on discretization error. This paper asks whether the order induced by $A_2$ between two paths is reliable at a fixed number of function evaluations (NFE). Already for centered Gaussian interpolants the implication fails: for independent $N(0,1)$ and $N(0,4)$, the exact regularity integrals of the linear and trigonometric variance-preserving paths are $5\pi/8-1$ and $\pi^2/16$, while Heun at NFE 8 reverses Gaussian Wasserstein-2 distance. Three regimes then separate. As a pairwise comparator of linear versus VP, the ranking inverts in 5 of 12 geometry-by-solver cells. As an in-family objective, trigonometric VP versus the scalar log-covariance schedule (Chen Example 3.3 with $M=\lambda_{\max}$) invert in 9 of 36 blocks (4 of 12 cells). The unconstrained per-mode minimizer attains both the smallest regularity and the smallest Wasserstein-2 distance in 36 of 36 blocks, but is not a shared $(\alpha,\sigma)$ interpolant for $d\geq 2$. The analysis is confined to commuting Gaussians; no learned field is used.

```bibtex
@article{callaert2026averaged,
  title  = {Averaged Jacobian Regularity Does Not Order Few-Step Error in Flow Matching:
            A Certified Gaussian Counterexample},
  author = {Callaert, Cl\'ement},
  year   = {2026},
  eprint = {TODO-ARXIV-ID},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG}
}
```

GitHub also exposes this entry via [`CITATION.cff`](CITATION.cff). No identifier is assigned yet; do not invent one. Preprint sources: [`paper/arxiv/`](paper/arxiv/README.md).

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
