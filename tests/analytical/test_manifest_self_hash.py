"""Canonical compact-manifest self-hash."""

from __future__ import annotations

from fewstep_regularities.utils.hashing import (
    MANIFEST_SELF_KEY,
    sha256_manifest,
    write_compact_manifest,
)


def test_canonical_manifest_self_hash_roundtrip(tmp_path) -> None:
    payload = {
        "artifact_release_id": "test",
        "planned_release_tag": "arxiv-v1",
        "files": {"other.json": "abc"},
    }
    path = tmp_path / "manifest.json"
    digest = write_compact_manifest(path, payload)
    on_disk = __import__("json").loads(path.read_text(encoding="utf-8"))
    assert on_disk["files"][MANIFEST_SELF_KEY] == digest
    assert sha256_manifest(on_disk) == digest
    # Changing a file hash must change the canonical digest.
    on_disk["files"]["other.json"] = "def"
    assert sha256_manifest(on_disk) != digest


def test_provenance_root_is_repository() -> None:
    from fewstep_regularities.utils.provenance import ROOT, source_state

    assert (ROOT / "pyproject.toml").is_file()
    state = source_state()
    assert state["base_commit"] != "unknown"
    assert state["environment_lock_hash"] != "missing"
    assert isinstance(state["working_tree_dirty"], bool)
