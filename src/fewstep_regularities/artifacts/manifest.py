"""Artifact provenance schemas."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any

REQUIRED_MANIFEST_FIELDS: tuple[str, ...] = (
    "run_id",
    "git_commit",
    "config_hash",
    "code_status",
    "software_environment_hash",
    "random_seeds",
    "start_time",
    "end_time",
    "runtime_s",
    "artifact_manifest",
    "resolved_config_path",
    "unresolved_config_path",
    "command_line",
    "python_version",
    "package_lock_hash",
    "cuda_version",
    "gpu_name",
    "release_ready",
)


REQUIRED_ARTIFACT_FIELDS: tuple[str, ...] = (
    "artifact_id",
    "producing_run_id",
    "git_commit",
    "config_hash",
    "code_status",
    "input_artifact_hashes",
    "creation_timestamp",
    "software_environment_hash",
    "random_seeds",
    "output_checksum",
)


REQUIRED_FIGURE_SIDECAR_FIELDS: tuple[str, ...] = (
    "source_run_ids",
    "source_table_hashes",
    "plotting_script",
    "plotting_config",
    "git_commit",
    "generation_timestamp",
)


def required_manifest_fields() -> tuple[str, ...]:
    """Return required top-level run manifest fields."""
    return REQUIRED_MANIFEST_FIELDS


@dataclass(frozen=True)
class ArtifactRecord:
    """Provenance record for one saved artifact.

    Attributes:
        artifact_id: Stable artifact identifier.
        producing_run_id: Run that created the artifact.
        git_commit: Git commit hash at creation time.
        config_hash: Hash of the resolved config.
        code_status: ``clean`` or ``dirty``.
        input_artifact_hashes: Hashes of upstream artifacts.
        creation_timestamp: ISO-8601 creation time.
        software_environment_hash: Hash of the software environment.
        random_seeds: Seeds used to produce the artifact.
        output_checksum: SHA256 of the artifact bytes.
        path: Relative path of the artifact file.
        kind: Artifact kind (``table``, ``tensor``, ``figure``, ``manifest``).
    """

    artifact_id: str
    producing_run_id: str
    git_commit: str
    config_hash: str
    code_status: str
    input_artifact_hashes: Mapping[str, str]
    creation_timestamp: str
    software_environment_hash: str
    random_seeds: Sequence[int]
    output_checksum: str
    path: str
    kind: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return asdict(self)


@dataclass
class RunManifest:
    """Run-level provenance manifest.

    Attributes:
        run_id: Unique run identifier.
        git_commit: Git commit hash.
        config_hash: Hash of the resolved config.
        code_status: ``clean`` or ``dirty``.
        software_environment_hash: Environment hash.
        random_seeds: Registered seeds for the run.
        start_time: ISO-8601 start time.
        end_time: ISO-8601 end time.
        runtime_s: Runtime in seconds.
        artifact_manifest: Nested artifact records.
        resolved_config_path: Path to resolved config YAML/JSON.
        unresolved_config_path: Path to unresolved config.
        command_line: Exact command line.
        python_version: Python version string.
        package_lock_hash: Hash of dependency lock or installed set.
        cuda_version: CUDA version or ``null`` string.
        gpu_name: GPU name or ``cpu``.
        release_ready: Whether the run is marked release-ready.
        extras: Additional metadata.
    """

    run_id: str
    git_commit: str
    config_hash: str
    code_status: str
    software_environment_hash: str
    random_seeds: Sequence[int]
    start_time: str
    end_time: str
    runtime_s: float
    artifact_manifest: Sequence[Mapping[str, Any]]
    resolved_config_path: str
    unresolved_config_path: str
    command_line: str
    python_version: str
    package_lock_hash: str
    cuda_version: str
    gpu_name: str
    release_ready: bool = False
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return asdict(self)

    def missing_fields(self) -> list[str]:
        """Return required fields that are missing or empty."""
        data = self.to_dict()
        missing: list[str] = []
        for key in REQUIRED_MANIFEST_FIELDS:
            value = data.get(key)
            if value is None or value == "" or (key == "random_seeds" and value == []):
                missing.append(key)
        return missing
