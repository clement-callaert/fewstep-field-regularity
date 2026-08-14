"""Hashing helpers for artifact provenance."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    """Return the SHA256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the SHA256 hex digest of a file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    """Return the SHA256 hex digest of a UTF-8 string."""
    return sha256_bytes(text.encode("utf-8"))


MANIFEST_SELF_KEY = "manifest.json"
MANIFEST_SELF_PLACEHOLDER = ""


def canonical_manifest_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of a compact-artifact manifest with the self-hash blanked.

    A file cannot contain its own ordinary cryptographic hash. The canonical
    hashing rule therefore copies the JSON object, always sets
    ``files['manifest.json']`` to an empty string (inserting the key if
    needed), and serializes with sorted keys and compact separators. The
    recorded self-hash is SHA-256 of that canonical encoding.
    """
    import copy

    data = copy.deepcopy(payload)
    files = data.setdefault("files", {})
    if not isinstance(files, dict):
        raise TypeError("manifest payload 'files' must be a dict")
    files[MANIFEST_SELF_KEY] = MANIFEST_SELF_PLACEHOLDER
    return data


def sha256_manifest(payload: dict[str, Any]) -> str:
    """Return the canonical self-hash of a compact-artifact manifest."""
    import json

    canonical = canonical_manifest_payload(payload)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return sha256_bytes(encoded)


def write_compact_manifest(path: Path, payload: dict[str, Any]) -> str:
    """Write a compact manifest and fill the canonical self-hash.

    The self-hash is SHA-256 of the JSON object after blanking
    ``files['manifest.json']``. After writing, the recorded value is checked
    against a fresh canonical hash of the on-disk file.
    """
    import json

    data = canonical_manifest_payload(payload)
    digest = sha256_manifest(data)
    files = data.setdefault("files", {})
    files[MANIFEST_SELF_KEY] = digest
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    if sha256_manifest(on_disk) != digest:
        raise RuntimeError(f"canonical manifest self-hash failed for {path}")
    if on_disk.get("files", {}).get(MANIFEST_SELF_KEY) != digest:
        raise RuntimeError(f"manifest self-hash not recorded for {path}")
    return digest
