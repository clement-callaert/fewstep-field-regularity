"""Validate run manifests and artifact provenance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from fewstep_regularities.artifacts.manifest import (
    REQUIRED_ARTIFACT_FIELDS,
    REQUIRED_FIGURE_SIDECAR_FIELDS,
    REQUIRED_MANIFEST_FIELDS,
)
from fewstep_regularities.utils.hashing import sha256_file, sha256_manifest


class ValidationError(Exception):
    """Raised when provenance validation fails."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_fields(
    data: dict[str, Any],
    fields: tuple[str, ...],
    label: str,
    *,
    allow_empty_list_keys: frozenset[str] | None = None,
) -> list[str]:
    allowed_empty = allow_empty_list_keys or frozenset()
    missing: list[str] = []
    for key in fields:
        value = data.get(key)
        if value is None or value == "" or (value == [] and key not in allowed_empty):
            missing.append(f"{label}.{key}")
    return missing


COMPACT_RELEASE_TAG = "arxiv-v1"


def is_compact_manifest(manifest: dict[str, Any]) -> bool:
    """Return True for the preprint compact checksum manifest."""
    return isinstance(manifest.get("files"), dict) and "artifact_release_id" in manifest


def validate_compact_manifest(manifest: dict[str, Any], run_dir: Path) -> list[str]:
    """Validate compact preprint checksums. Does not check Hydra fields.

    The public verification path that also checks retired-commit placeholders
    is ``scripts/check_arxiv_release.py``. This function only checks the
    ``files`` checksum table in ``paper/arxiv/artifacts/manifest.json``.
    """
    errors: list[str] = []
    files = manifest.get("files", {})
    if not isinstance(files, dict) or not files:
        return ["compact manifest missing files"]
    for name, expected in files.items():
        path = run_dir / str(name)
        if name == "manifest.json":
            actual = sha256_manifest(manifest)
            if actual != expected:
                errors.append(
                    f"canonical self-hash mismatch for manifest.json: {actual}"
                )
            continue
        if not path.is_file():
            errors.append(f"missing compact artefact {name}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(f"checksum mismatch for {name}: {actual}")
    if manifest.get("planned_release_tag") != COMPACT_RELEASE_TAG:
        errors.append("manifest planned_release_tag is not arxiv-v1")
    return errors


def validate_manifest(manifest: dict[str, Any], run_dir: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(
        require_fields(
            manifest,
            REQUIRED_MANIFEST_FIELDS,
            "manifest",
            allow_empty_list_keys=frozenset({"artifact_manifest"}),
        )
    )

    if manifest.get("release_ready") and manifest.get("code_status") == "dirty":
        errors.append("dirty-code run marked release-ready")

    resolved = manifest.get("resolved_config_path")
    if resolved:
        resolved_path = Path(str(resolved))
        if not resolved_path.is_file():
            # Allow relative path inside run_dir.
            alt = run_dir / "resolved_config.yaml"
            if not alt.is_file():
                errors.append("missing resolved config")
    else:
        errors.append("missing resolved config path")

    seeds = manifest.get("random_seeds")
    if not isinstance(seeds, list) or not seeds:
        errors.append("missing seed records")

    for key in ("config_hash", "software_environment_hash", "package_lock_hash"):
        if not manifest.get(key):
            errors.append(f"missing hash: {key}")

    artifacts = manifest.get("artifact_manifest", [])
    if not isinstance(artifacts, list):
        errors.append("artifact_manifest must be a list")
        return errors

    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            errors.append(f"artifact[{index}] is not an object")
            continue
        errors.extend(
            require_fields(artifact, REQUIRED_ARTIFACT_FIELDS, f"artifact[{index}]")
        )
        path_value = artifact.get("path")
        checksum = artifact.get("output_checksum")
        if path_value and checksum:
            path = Path(str(path_value))
            if not path.is_absolute():
                path = run_dir / path
            if not path.is_file():
                errors.append(f"missing source artifact: {path}")
            else:
                actual = sha256_file(path)
                if actual != checksum:
                    errors.append(f"mismatched checksum: {path}")
        if artifact.get("kind") == "figure":
            if not path_value:
                errors.append(f"figure artifact[{index}] missing path")
                continue
            figure_path = Path(str(path_value))
            sidecar = figure_path.with_suffix(figure_path.suffix + ".json")
            if not sidecar.is_file():
                errors.append(f"figure without provenance sidecar: {figure_path}")
            else:
                side = load_json(sidecar)
                errors.extend(
                    require_fields(
                        side,
                        REQUIRED_FIGURE_SIDECAR_FIELDS,
                        f"figure_sidecar[{index}]",
                    )
                )
    return errors


def validate_path(target: Path) -> list[str]:
    if target.is_file() and target.name == "manifest.json":
        manifest_path = target
        run_dir = target.parent
    elif (target / "manifest.json").is_file():
        manifest_path = target / "manifest.json"
        run_dir = target
    else:
        return [f"No manifest.json found under {target}"]
    manifest = load_json(manifest_path)
    if is_compact_manifest(manifest):
        return validate_compact_manifest(manifest, run_dir)
    return validate_manifest(manifest, run_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Run directories or manifest.json paths to validate.",
    )
    args = parser.parse_args()

    all_errors: list[str] = []
    for path in args.paths:
        errors = validate_path(path)
        if errors:
            all_errors.append(f"{path}:")
            all_errors.extend(f"  - {err}" for err in errors)
        else:
            print(f"OK: {path}")

    if all_errors:
        print("Validation failed:", file=sys.stderr)
        for line in all_errors:
            print(line, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
