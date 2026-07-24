"""Fail if prohibited AI identities appear in commit attribution.

Checks a commit range (default ``origin/main..HEAD``) or a commit-message
file (``--message-file``, for use as a ``commit-msg`` hook). It never
edits or rewrites anything; it only reports and sets the exit code.

Blocked identities are the specific AI/automation identities below.
Legitimate human co-authors are not blocked.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PROHIBITED_IDENTITY_PATTERNS: tuple[str, ...] = (
    r"\bclaude\b",
    r"\banthropic\b",
    r"noreply@anthropic\.com",
    r"\[bot\]",
)

TRAILER_RE = re.compile(
    r"^(co-authored-by|signed-off-by):\s*(?P<who>.+)$",
    re.IGNORECASE,
)


def _is_prohibited(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(p, lowered) for p in PROHIBITED_IDENTITY_PATTERNS)


def check_message(message: str, label: str) -> list[str]:
    """Return violations found in one commit message."""
    problems: list[str] = []
    for line in message.splitlines():
        match = TRAILER_RE.match(line.strip())
        if match and _is_prohibited(match.group("who")):
            problems.append(f"{label}: prohibited trailer: {line.strip()}")
    return problems


def check_identity(name: str, email: str, role: str, label: str) -> list[str]:
    """Return violations found in one author/committer identity."""
    if _is_prohibited(f"{name} <{email}>"):
        return [f"{label}: prohibited {role}: {name} <{email}>"]
    return []


def check_range(commit_range: str) -> list[str]:
    """Check every commit in a git range."""
    fmt = "%H%x1f%an%x1f%ae%x1f%cn%x1f%ce%x1f%B%x1e"
    out = subprocess.run(
        ["git", "log", f"--format={fmt}", commit_range],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    problems: list[str] = []
    for record in filter(None, (r.strip("\n") for r in out.split("\x1e"))):
        if not record.strip():
            continue
        sha, an, ae, cn, ce, body = record.split("\x1f", 5)
        label = sha[:12]
        problems += check_identity(an, ae, "author", label)
        problems += check_identity(cn, ce, "committer", label)
        problems += check_message(body, label)
    return problems


def main(argv: list[str] | None = None) -> int:
    """CLI entry point; returns process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "range",
        nargs="?",
        default="origin/main..HEAD",
        help="Commit range to check (default: origin/main..HEAD)",
    )
    parser.add_argument(
        "--message-file",
        type=Path,
        default=None,
        help="Check a commit-message file instead of a range",
    )
    args = parser.parse_args(argv)

    if args.message_file is not None:
        problems = check_message(
            args.message_file.read_text(encoding="utf-8"), str(args.message_file)
        )
    else:
        problems = check_range(args.range)

    if problems:
        print("Prohibited commit attribution found:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("commit attribution OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
