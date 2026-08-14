# Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching Schedules: A Certified Gaussian Counterexample

No arXiv identifier has been assigned. Do not invent one.

**Abstract.** Few-step sampling in flow matching and stochastic interpolants requires an interpolation schedule, equivalently a sampling schedule, to be chosen before any endpoint error is observed. Averaged squared Jacobian regularity is a plausible schedule-design criterion, but it is not a solver-specific discretization-error functional. Chen, Vanden-Eijnden, and Xu propose minimizing A_2, the time-integrated squared spatial Jacobian Lipschitzness of a flow-matching marginal ODE. They do not claim or prove that A_2 universally ranks equal-NFE solver error. We study that narrower surrogate question. For independent N(0,1) and N(0,4), the exact integrals are 5 pi/8 - 1 and pi^2/16, so regularity prefers trigonometric VP, while explicit Heun, a two-stage Runge-Kutta method, at eight number of function evaluations (NFE 8) prefers the linear path in Gaussian Wasserstein-2 distance. The inversion is certified by an exact rational Heun product and a nonnegative element of Q[pi, sqrt(2)]. A complementary construction shows that, for every step count N and every admissible endpoint log-scale, the unique integrated-regularity minimizer can have strictly larger N-step Euler endpoint error than a higher-regularity competitor aligned to that solver grid. A specified finite Gaussian enumeration of four candidate paths on 36 tested blocks contains both agreement and pairwise disagreement. The results establish a limitation of a universal surrogate interpretation. They do not evaluate learned velocity fields and do not estimate a population frequency of failure.

```bibtex
@article{callaert2026fewstep,
  title  = {Averaged Jacobian Regularity Can Misrank Few-Step Flow-Matching
            Schedules: A Certified Gaussian Counterexample},
  author = {Callaert, Cl\'ement},
  year   = {2026},
  note   = {Preprint; arXiv identifier not yet assigned}
}
```

GitHub also exposes this entry via [`CITATION.cff`](CITATION.cff). Preprint sources: [`paper/arxiv/`](paper/arxiv/README.md).

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
evaluation, and a reproducibility pipeline: compact artifacts under
`paper/arxiv/artifacts/` with SHA-256 checksums, frozen Phase-4 tables
under `paper/arxiv/frozen_runs/`, and figure provenance sidecars that
record the base commit and a working-tree dirty flag.

Pinned Python dependencies are in [`requirements-lock.txt`](requirements-lock.txt).

## Reproduction

Install:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install -e ".[dev]"
pre-commit install
```

Default analytical precision is float64. Do not silently cast precision.

```bash
pytest -q -ra
fewstep-regularities experiment=smoke
python scripts/validate_artifacts.py paper/arxiv/artifacts
```

`validate_artifacts.py` checks compact preprint checksums, including the
canonical manifest self-hash. Compact preprint checksums are also checked by
`python scripts/check_arxiv_release.py`.

Experiment configurations live under
[`configs/experiment`](configs/experiment). Research-process documents
live under [`docs/`](docs/).

Commands that rebuild tables, figures, and the certified scalar identities:

```bash
python scripts/verify_scalar_counterexample.py
python scripts/run_log_covariance_comparison.py
python scripts/run_in_family_comparison.py
python scripts/run_inversion_region.py
python scripts/run_lowrank_seed_fraction.py
python scripts/run_grid_aware_robustness.py
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

The distributed snapshot includes compact derived artifacts and frozen
Phase-4 tables needed by the manuscript figures. It does not include a
live Hydra `outputs/` tree. The raw `phase4_robustness` Hydra table is
not distributed; the derived `robustness_lowrank.json` is.

## Repository structure

```text
audit/                       Historical audits; see PASS7 for the current record
configs/                     Hydra configuration groups
docs/                        Research process documents
paper/arxiv/                 Public preprint sources
paper/arxiv/frozen_runs/     Frozen Phase-4 tables used by figures
paper/archive/               Historical drafts (not the public preprint)
papers/                      Literature index and notes
scripts/                     Retrieval, validation, and figure utilities
src/fewstep_regularities/    Research package
tests/                       Unit, analytical, regression, integration tests
outputs/                     Run outputs with gitignored contents
```

## License

The code, tests, and scripts are MIT; see [LICENSE](LICENSE). The manuscript,
figures, and compact artifacts under `paper/` are CC BY 4.0, matching the
planned arXiv deposit.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Commits are created and pushed by
the repository owner only.
