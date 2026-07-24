"""Tests for the commit-attribution checker."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "check_commit_attribution.py"
)
spec = importlib.util.spec_from_file_location("check_commit_attribution", MODULE_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
sys.modules["check_commit_attribution"] = checker
spec.loader.exec_module(checker)


def test_blocks_claude_coauthor_trailer() -> None:
    message = "Fix bug\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>\n"
    assert checker.check_message(message, "x")


def test_blocks_anthropic_signoff() -> None:
    message = "Fix bug\n\nSigned-off-by: Anthropic Bot <bot@anthropic.com>\n"
    assert checker.check_message(message, "x")


def test_blocks_bot_coauthor() -> None:
    message = "Fix\n\nCo-authored-by: dependabot[bot] <x@users.noreply.github.com>\n"
    assert checker.check_message(message, "x")


def test_allows_human_coauthor() -> None:
    message = "Fix bug\n\nCo-authored-by: Ada Lovelace <ada@example.org>\n"
    assert not checker.check_message(message, "x")


def test_allows_plain_message_mentioning_nothing() -> None:
    assert not checker.check_message("Record Phase 4 robustness audit\n", "x")


def test_allows_scientific_mention_outside_trailer() -> None:
    # A body sentence is not a trailer; only trailers and identities block.
    message = "Discuss the Claude Shannon entropy bound in the notes\n"
    assert not checker.check_message(message, "x")


def test_blocks_ai_author_identity() -> None:
    assert checker.check_identity(
        "Claude Fable 5", "noreply@anthropic.com", "author", "x"
    )


def test_blocks_ai_committer_identity() -> None:
    assert checker.check_identity("Anthropic CI", "ci@anthropic.com", "committer", "x")


def test_allows_owner_identity() -> None:
    assert not checker.check_identity(
        "Clément Callaert", "someone@example.org", "author", "x"
    )
