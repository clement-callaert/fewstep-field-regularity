"""Artifact hashing and writer tests."""

from __future__ import annotations

from pathlib import Path

import torch

from fewstep_regularities.artifacts.manifest import ArtifactRecord
from fewstep_regularities.artifacts.writer import FilesystemArtifactWriter
from fewstep_regularities.utils.hashing import sha256_bytes, sha256_file


def _record(path: str = "tmp") -> ArtifactRecord:
    return ArtifactRecord(
        artifact_id="a1",
        producing_run_id="r1",
        git_commit="c",
        config_hash="h",
        code_status="clean",
        input_artifact_hashes={},
        creation_timestamp="t",
        software_environment_hash="e",
        random_seeds=[0],
        output_checksum="",
        path=path,
        kind="table",
    )


def test_sha256_bytes_stable() -> None:
    assert sha256_bytes(b"abc") == sha256_bytes(b"abc")
    assert sha256_bytes(b"abc") != sha256_bytes(b"abd")


def test_save_table_writes_checksum(tmp_path: Path) -> None:
    writer = FilesystemArtifactWriter()
    path = tmp_path / "table.json"
    updated = writer.save_table({"x": 1}, path, _record())
    assert path.is_file()
    assert updated.output_checksum == sha256_file(path)
    assert updated.kind == "table"


def test_save_tensor_cpu(tmp_path: Path) -> None:
    writer = FilesystemArtifactWriter()
    path = tmp_path / "tensor.pt"
    tensor = torch.arange(4, dtype=torch.float64)
    updated = writer.save_tensor(tensor, path, _record())
    loaded = torch.load(path, weights_only=True)
    assert torch.equal(loaded, tensor)
    assert updated.output_checksum
