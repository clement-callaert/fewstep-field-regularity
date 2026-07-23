"""Artifact writer interface and filesystem implementation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import torch
from torch import Tensor

from fewstep_regularities.artifacts.manifest import ArtifactRecord, RunManifest
from fewstep_regularities.utils.hashing import sha256_bytes, sha256_file


@runtime_checkable
class ArtifactWriter(Protocol):
    """Writes tables, tensors, figures, and manifests with provenance."""

    def save_table(
        self,
        table: Mapping[str, Any],
        path: Path,
        record: ArtifactRecord,
    ) -> ArtifactRecord:
        """Save a tabular artifact.

        Args:
            table: JSON-serializable mapping.
            path: Destination path.
            record: Provenance record (checksum filled by the writer).

        Returns:
            Updated ``ArtifactRecord`` with output checksum.

        Mathematical definition:
            Not applicable.
        """
        ...

    def save_tensor(
        self,
        tensor: Tensor,
        path: Path,
        record: ArtifactRecord,
    ) -> ArtifactRecord:
        """Save a tensor artifact.

        Args:
            tensor: Tensor of arbitrary shape.
            path: Destination path (``.pt``).
            record: Provenance record.

        Returns:
            Updated ``ArtifactRecord`` with output checksum.

        Device:
            Tensor is moved to CPU before serialization.
        """
        ...

    def save_figure(
        self,
        figure_path: Path,
        sidecar: Mapping[str, Any],
        record: ArtifactRecord,
    ) -> ArtifactRecord:
        """Register a figure and write its sidecar JSON.

        Args:
            figure_path: Path to an existing figure file.
            sidecar: Sidecar provenance mapping (exact input artifacts listed).
            record: Provenance record.

        Returns:
            Updated ``ArtifactRecord`` with output checksum.

        Notes:
            Figures must not read arbitrary files from a directory.
            The figure config must list exact input artifacts.
        """
        ...

    def save_manifest(self, manifest: RunManifest, path: Path) -> Path:
        """Save a run manifest.

        Args:
            manifest: Run provenance.
            path: Destination ``manifest.json``.

        Returns:
            Path written.
        """
        ...


class FilesystemArtifactWriter:
    """Filesystem-backed artifact writer."""

    def save_table(
        self,
        table: Mapping[str, Any],
        path: Path,
        record: ArtifactRecord,
    ) -> ArtifactRecord:
        # Save the run table.
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(table, indent=2, sort_keys=True).encode("utf-8")
        path.write_bytes(payload)
        checksum = sha256_bytes(payload)
        return _with_checksum(record, checksum, str(path), "table")

    def save_tensor(
        self,
        tensor: Tensor,
        path: Path,
        record: ArtifactRecord,
    ) -> ArtifactRecord:
        # Save tensor on CPU.
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(tensor.detach().cpu(), path)
        checksum = sha256_file(path)
        return _with_checksum(record, checksum, str(path), "tensor")

    def save_figure(
        self,
        figure_path: Path,
        sidecar: Mapping[str, Any],
        record: ArtifactRecord,
    ) -> ArtifactRecord:
        # Save figure sidecar next to the figure.
        figure_path = Path(figure_path)
        if not figure_path.is_file():
            msg = f"Figure file does not exist: {figure_path}"
            raise FileNotFoundError(msg)
        sidecar_path = figure_path.with_suffix(figure_path.suffix + ".json")
        sidecar_path.write_text(
            json.dumps(sidecar, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        checksum = sha256_file(figure_path)
        return _with_checksum(record, checksum, str(figure_path), "figure")

    def save_manifest(self, manifest: RunManifest, path: Path) -> Path:
        # Save the run manifest.
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(manifest.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return path


def _with_checksum(
    record: ArtifactRecord,
    checksum: str,
    path: str,
    kind: str,
) -> ArtifactRecord:
    data = asdict(record)
    data["output_checksum"] = checksum
    data["path"] = path
    data["kind"] = kind
    return ArtifactRecord(**data)
