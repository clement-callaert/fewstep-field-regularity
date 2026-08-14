"""Honest source-state records for figures and compact artifacts.

Provenance records the git HEAD at generation time as ``source_commit``.
That SHA is the scientific source snapshot, not the later artifact-carrier
commit that stores generated PDFs and sidecars. A tracked file cannot
contain the SHA of the commit that adds the file. Records also include a
hash of the tracked working-tree diff and an explicit dirty flag.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fewstep_regularities.utils.environment import package_lock_hash
from fewstep_regularities.utils.hashing import sha256_bytes, sha256_file

ROOT = Path(__file__).resolve().parents[3]


def _git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    repo = cwd or ROOT
    return subprocess.run(
        ["git", "-c", f"safe.directory={repo}", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def source_state(repo_root: Path | None = None) -> dict[str, Any]:
    """Return a truthful source-state dictionary for provenance sidecars."""
    root = repo_root or ROOT
    head = _git("rev-parse", "HEAD", cwd=root)
    porcelain = _git("status", "--porcelain", cwd=root)
    diff = _git("diff", "HEAD", cwd=root)
    base = head.stdout.strip() if head.returncode == 0 else "unknown"
    status_text = porcelain.stdout if porcelain.returncode == 0 else ""
    diff_text = diff.stdout if diff.returncode == 0 else ""
    dirty = bool(status_text.strip())
    return {
        "source_commit": base,
        "base_commit": base,
        "working_tree_dirty": dirty,
        "working_tree_diff_sha256": sha256_bytes(diff_text.encode()),
        "working_tree_status_sha256": sha256_bytes(status_text.encode()),
        "environment_lock_hash": package_lock_hash(root),
        "recorded_at": datetime.now(UTC).isoformat(),
    }


def figure_sidecar_payload(
    figure_path: Path,
    *,
    artifact_ids: list[str],
    source_table_hashes: dict[str, str],
    plotting_script: str,
    plotting_config: dict[str, Any],
    note: str,
    generation_command: str,
    figure_artifact_id: str,
) -> dict[str, Any]:
    """Return a sidecar dict with honest source-state fields."""
    state = source_state()
    return {
        "figure_artifact_id": figure_artifact_id,
        "source_run_ids": sorted({a.split(":")[0] for a in artifact_ids})
        or ["none_conceptual"],
        "source_artifact_ids": artifact_ids,
        "source_table_hashes": source_table_hashes,
        "plotting_script": plotting_script,
        "plotting_config": plotting_config,
        "generation_command": generation_command,
        "source_commit": state["source_commit"],
        "git_commit": state["base_commit"],
        "base_commit": state["base_commit"],
        "working_tree_dirty": state["working_tree_dirty"],
        "working_tree_diff_sha256": state["working_tree_diff_sha256"],
        "working_tree_status_sha256": state["working_tree_status_sha256"],
        "environment_lock_hash": state["environment_lock_hash"],
        "generation_timestamp": state["recorded_at"],
        "figure_checksum_sha256": sha256_file(figure_path),
        "note": note,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    """Stable UTF-8 JSON used for hashing structured records."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_canonical_json(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
