"""Publication-time checks for the arXiv compact tree.

Default mode (used by pytest) verifies that the retired commit placeholder is
absent and that compact artefact checksums match the local manifest. Tag
existence is a manual owner gate: pass --require-tag only after creating
arxiv-v1. Missing tag is not a scientific failure of the manuscript.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

from fewstep_regularities.utils.hashing import sha256_file

ROOT = Path(__file__).resolve().parents[1]
RELEASE_TAG = "arxiv-v1"
ARTIFACTS = ROOT / "paper" / "arxiv" / "artifacts"
MANIFEST = ARTIFACTS / "manifest.json"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", f"safe.directory={ROOT}", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def check_checksums() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return ["missing paper/arxiv/artifacts/manifest.json"]
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = payload.get("files", {})
    for name, expected in files.items():
        if name == "manifest.json":
            continue
        path = ARTIFACTS / name
        if not path.is_file():
            errors.append(f"missing compact artefact {name}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(f"checksum mismatch for {name}: {actual}")
    if payload.get("planned_release_tag") != RELEASE_TAG:
        errors.append("manifest planned_release_tag is not arxiv-v1")
    return errors


def remaining_placeholders() -> list[str]:
    path = Path(__file__).with_name("check_arxiv_placeholder.py")
    spec = importlib.util.spec_from_file_location("check_arxiv_placeholder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check_arxiv_placeholder.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.remaining_placeholders()


def tag_exists() -> bool:
    result = _git("tag", "-l", RELEASE_TAG)
    return result.returncode == 0 and RELEASE_TAG in result.stdout.split()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-tag",
        action="store_true",
        help="Fail if the arxiv-v1 tag is absent (manual publication gate).",
    )
    args = parser.parse_args()

    errors = remaining_placeholders()
    errors.extend(check_checksums())
    tag_present = tag_exists()
    if args.require_tag and not tag_present:
        errors.append(
            f"release tag {RELEASE_TAG} does not exist; create it on the "
            "final scientific commit before submitting to arXiv"
        )
    if errors:
        raise SystemExit("release check failed:\n  " + "\n  ".join(errors))
    if tag_present:
        print(f"release checks passed; tag {RELEASE_TAG} exists")
    else:
        print(
            "scientific release checks passed; tag "
            f"{RELEASE_TAG} is the remaining manual publication gate"
        )


if __name__ == "__main__":
    main()
