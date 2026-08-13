# Few-Step Flow-Matching Error Can Be Misranked by Averaged Jacobian Regularity: A Certified Gaussian Counterexample

arXiv: [TODO-ARXIV-ID](https://arxiv.org/abs/TODO-ARXIV-ID)

**Abstract.** Does averaged squared Jacobian regularity rank two interpolants in the same order as equal-NFE endpoint error? Chen, Vanden-Eijnden, and Xu propose minimizing $A_2$, the time-integrated squared spatial Jacobian norm of a flow-matching marginal ODE, as a criterion for schedule design, without a proved discretization-error bound. Classical one-step bounds use a Lipschitz constant of the field; $A_2$ is not that constant. Already for independent $N(0,1)$ and $N(0,4)$, the exact regularity integrals of the linear and trigonometric variance-preserving Gaussian interpolants are $5\pi/8-1$ and $\pi^2/16$, while Heun at NFE 8 reverses Gaussian Wasserstein-2 distance. The linear Heun product is the rational $6797469/3559400$; a nonnegative element of $\mathbb{Q}[\pi,\sqrt{2}]$ yields $r_{\mathrm{VP}}<187/100$. The object is a flow matching marginal interpolant ODE, not a score-based probability-flow ODE. The Gaussian drift and $W_2$ formula are closed form; the regularity integrand is exact, while multimode $R$ is evaluated deterministically by adaptive quadrature. Pairwise and four-path census comparisons on commuting Gaussian interpolants are reported below; a finite census does not imply that a global $A_2$-minimizer minimizes fixed-NFE error. The analysis uses stochastic interpolants, few-step sampling, Runge--Kutta, and interpolation schedules; no learned field is used.

```bibtex
@article{callaert2026fewstep,
  title  = {Few-Step Flow-Matching Error Can Be Misranked by Averaged Jacobian Regularity:
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
commuting flow-matching marginal ODEs.

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
pytest -q -ra
fewstep-regularities experiment=smoke
python scripts/validate_artifacts.py outputs/phase0_smoke
```

`validate_artifacts.py` checks Hydra run manifests under `outputs/`.
Compact preprint checksums are checked by
`python scripts/check_arxiv_release.py`.

Experiment configurations live under
[`configs/experiment`](configs/experiment). Research-process documents
live under [`docs/`](docs/).

Pinned Phase 4 artifacts used by the public manuscript are validated with
the compact-manifest checker. Commands that rebuild tables, figures, and
the certified scalar identities:

```bash
python scripts/verify_scalar_counterexample.py
python scripts/run_log_covariance_comparison.py
python scripts/run_in_family_comparison.py
python scripts/run_inversion_region.py
python scripts/run_lowrank_seed_fraction.py
python scripts/run_arxiv_stats.py
python scripts/make_arxiv_figures.py
python scripts/make_arxiv_tables.py
python scripts/check_arxiv_placeholder.py
python scripts/check_arxiv_release.py
python scripts/check_arxiv_structure.py
```

Compile from `paper/arxiv/` and `paper/gddl2026/`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Pack a clean arXiv source tree with `python scripts/pack_arxiv_source.py`.

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

## License

The code, tests, and scripts are MIT; see [LICENSE](LICENSE). The manuscript,
figures, and compact artifacts under `paper/` are CC BY 4.0, matching the
planned arXiv deposit.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Commits are created and pushed by
the repository owner only.
