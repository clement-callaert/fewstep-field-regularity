"""Environment and git metadata collection."""

from __future__ import annotations

import hashlib
import platform
import subprocess
import sys
from pathlib import Path


def python_version() -> str:
    """Return the Python version string."""
    return platform.python_version()


def git_commit(repo_root: Path | None = None) -> str:
    """Return the current git commit hash, or ``unknown``."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "unknown"
    return result.stdout.strip()


def git_code_status(repo_root: Path | None = None) -> str:
    """Return ``clean`` or ``dirty`` based on ``git status --porcelain``."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "unknown"
    return "dirty" if result.stdout.strip() else "clean"


def cuda_version() -> str:
    """Return CUDA version string if torch.cuda is available."""
    try:
        import torch
    except ImportError:
        return "unavailable"
    if not torch.cuda.is_available():
        return "null"
    return str(torch.version.cuda)


def gpu_name() -> str:
    """Return the first GPU name, or ``cpu``."""
    try:
        import torch
    except ImportError:
        return "cpu"
    if not torch.cuda.is_available():
        return "cpu"
    return str(torch.cuda.get_device_name(0))


def package_lock_hash(repo_root: Path) -> str:
    """Hash pyproject.toml as a lightweight lock proxy.

    Phase 0 does not require a lockfile. Prefer a lockfile hash later.
    """
    path = repo_root / "pyproject.toml"
    if not path.is_file():
        return "missing"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def software_environment_hash() -> str:
    """Hash a short description of the Python runtime."""
    payload = f"{sys.version}|{platform.platform()}".encode()
    return hashlib.sha256(payload).hexdigest()
