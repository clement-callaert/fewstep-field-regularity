# fewstep-field-regularity

Research status: Work in progress. No scientific claim has been validated.

A reproducible benchmark of field regularity metrics and few-step discretization
error in continuous-time generative models.

## 1. Research question

Which notions of field regularity reliably predict fixed-budget discretization
error across probability paths, solvers, dimensions, and target geometries?

## 2. Scientific status

Phase 2 Gaussian mixture distributions, exact independent-coupling mixture
fields, and Wasserstein estimator calibration are under validation. Phase 1
exact Gaussian stack remains in place. No main benchmark or decision gate has
been run. No claim in the claims ledger is marked supported.

## 3. Registered hypotheses

Treat all four statements as hypotheses, not conclusions.

- **H1:** Lower averaged global Lipschitzness is associated with lower fixed-NFE
  Wasserstein error.
- **H2:** Path-distribution-weighted local Jacobian metrics predict fixed-NFE
  error better than global worst-case metrics.
- **H3:** Temporal stiffness and Jacobian variation explain errors not captured
  by spatial Lipschitzness.
- **H4:** Metric rankings may change across solvers and target geometries.

See [docs/CLAIMS_LEDGER.md](docs/CLAIMS_LEDGER.md).

## 4. Decision gate

Continue toward a full paper only if a registered condition in
[docs/DECISION_GATE.md](docs/DECISION_GATE.md) holds. The gate must not be
modified after observing main results. Pivot rules are listed in the same file.

## 5. Installation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pre-commit install
```

Default analytical precision is float64. Do not silently cast precision.

## 6. Smoke test

```bash
pytest
fewstep-regularities experiment=smoke
python scripts/validate_artifacts.py outputs/phase0_smoke
fewstep-regularities experiment=phase1_smoke
python scripts/validate_artifacts.py outputs/phase1_smoke
fewstep-regularities experiment=phase2_smoke
python scripts/validate_artifacts.py outputs/phase2_smoke
```

Phase 0 smoke is a dry-run. Phase 1 smoke runs an exact Gaussian fixed-NFE
validation on a tiny grid. Phase 2 smoke runs a mixture fixed-NFE check with
sliced Wasserstein.

## 7. Reproduction commands

Phase 0:

```bash
python scripts/retrieve_papers.py
fewstep-regularities experiment=smoke
python scripts/validate_artifacts.py outputs/phase0_smoke
```

Phase 1 validation (not the gate):

```bash
fewstep-regularities experiment=phase1_gaussian
python scripts/validate_artifacts.py outputs/phase1_gaussian
```

Phase 2 mixture smoke and estimator calibration (not the gate):

```bash
fewstep-regularities experiment=phase2_smoke
python scripts/validate_artifacts.py outputs/phase2_smoke
fewstep-regularities experiment=phase2_calibration
python scripts/validate_artifacts.py outputs/phase2_calibration
```

Gate and full benchmarks remain blocked until Phases 1-2 pass review. Do not
launch them from this README yet.

## 8. Repository structure

```
configs/                     Hydra configuration groups
docs/                        Research process documents
papers/                      Paper index, PDFs, notes
scripts/                     Retrieval and validation utilities
src/fewstep_regularities/    Research package (src layout)
tests/                       Unit, analytical, regression, integration
outputs/                     Run outputs (gitignored contents)
artifacts/                   Optional curated artifacts
```

## 9. Artifact provenance

Every run writes a `manifest.json` with config hashes, seeds, git status, and
environment metadata. Figures require sidecar JSON listing exact input
artifacts. See [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

## 10. Paper retrieval

Papers are retrieved only from legal public sources (arXiv, OpenReview, author
pages, official proceedings). Index: [papers/README.md](papers/README.md).

## 11. Known limitations

- Phase 2 covers GMM targets under independent coupling only. Gaussian OT is
  refused for mixture targets.
- Empirical W2 estimators have a multi-seed calibration experiment, but are not
  continuous exact W2 for mixtures.
- Hairer ODE PDF is missing; solver orders are checked numerically only.
- Lipschitz-guided schedules use a scalar effective ``M`` (max eigenvalue of
  target covariance, including mixtures).
- No novelty claim is made before literature comparison.
- No theorem is marked proved without independent manual review.

## 12. Citation

This repository is incomplete research software. Do not cite empirical results
until the claims ledger marks them supported with multi-run evidence.
