# Frozen Phase-4 Hydra outputs

These directories are byte-identical copies of the frozen 2026-07-24
Hydra artifacts that previously lived only under
`talks/wald-interview-2026-08-21/artifacts/` and the gitignored
`outputs/` tree. They are included so arXiv figures that need the
eigenmode decomposition and non-centered split can be regenerated from
the public manuscript tree.

Checksums are pinned in `scripts/make_arxiv_figures.py` and in
`paper/arxiv/artifacts/manifest.json`. Do not edit the JSON in place.
Regenerate only by re-running the corresponding experiment configurations
and then updating the pins after a human audit.
