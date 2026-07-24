# Contributing

This is a single-owner research repository. Issues and questions are
welcome; the reproducibility and provenance rules in
`docs/REPRODUCIBILITY.md` apply to all changes.

## Commit authorship

- Commits are created, reviewed, and pushed by the repository owner.
- Automation and AI tools may edit the working tree, but they must not
  create commits, and they must not appear in commit metadata.
- AI identities (for example Claude or Anthropic accounts) must not
  appear as commit authors, committers, or co-authors.
- Commit messages must not contain automatically inserted
  `Co-authored-by` or `Signed-off-by` trailers for AI or automation
  identities. Human co-author trailers are acceptable when they reflect a
  real human contributor.
- `scripts/check_commit_attribution.py` enforces this policy. It runs as
  a `commit-msg` hook (install with
  `pre-commit install --hook-type commit-msg`) and can also audit a
  range: `python scripts/check_commit_attribution.py origin/main..HEAD`.
