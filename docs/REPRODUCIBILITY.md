# Reproducibility policy

## Principles

- Every scientific artifact must be reconstructible from recorded inputs.
- Do not depend on the current working directory. Use `pathlib` and absolute
  or repo-rooted paths.
- Set `hydra.job.chdir` to false unless a documented exception is required.
- Default analytical precision is float64. Do not silently cast precision.

## Run requirements

Every run must save:

- resolved config
- unresolved config
- command line
- Git commit
- Git diff status (`clean` or `dirty`)
- Python version
- package lock hash
- CUDA version
- GPU name
- random seeds
- start time
- end time
- runtime
- artifact manifest (`manifest.json`)

## Artifact requirements

Every artifact must have:

- artifact ID
- producing run ID
- Git commit
- config hash
- code status
- input artifact hashes
- creation timestamp
- software environment hash
- random seeds
- output checksum

## Figure provenance

A figure must have a sidecar JSON file containing:

- source run IDs
- source table hashes
- plotting script
- plotting config
- Git commit
- generation timestamp

Figures must not read arbitrary files from a directory. The figure config must
list exact input artifacts.

## Validation

Run:

```bash
python scripts/validate_artifacts.py <run_dir_or_artifact_root>
```

The validator must reject:

- missing hashes
- dirty-code runs marked as release-ready
- missing resolved configs
- missing seed records
- missing source artifacts
- mismatched checksums
- figures without provenance

## Release-ready rule

A run may be marked `release_ready: true` only if:

- code status is `clean`
- all required provenance fields are present
- artifact checksums validate
- the claims ledger does not overstate the evidence
