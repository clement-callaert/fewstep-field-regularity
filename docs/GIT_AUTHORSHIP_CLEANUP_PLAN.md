# Git authorship cleanup plan

Status: prepared 2026-07-24; **not executed**. Only the repository owner
runs any command in this plan.

## Why an AI identity appears

`docs/GIT_AUTHORSHIP_AUDIT.md` found exactly one mechanism: the commits
`f5e857ca4a74293b26327c612fddf2492bd77d08` and
`508101e759a2a035b194f9a4c56fab28fcac6f39` carry the trailer
`Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`, appended
automatically by session tooling before the owner disabled it. GitHub
counts co-author trailers in the contributors graph, so Claude appears as
a contributor. No commit anywhere has an AI author or committer; there are
no AI sign-offs, stale branches, or tags.

## Is rewriting necessary?

Yes, if the owner wants the contributor graph to show only himself: both
commits are reachable from `main` and already pushed to the public
remote, so the trailers can only be removed by rewriting those two commit
messages and force-updating `main`. This is a *message-only* rewrite —
class "co-author trailer only" — so the prepared procedure removes just
the trailer line. It must not touch author/committer identities (already
correct), author dates, file contents, trees, scientific artifacts, or
any of the 19 other commits.

If the owner instead judges a public-history rewrite not worth it, the
alternative is to leave history as-is and accept the contributor-graph
entry; the safeguards in Stage 4 prevent recurrence. That is a legitimate
choice; this plan exists for the stated preference to remove it.

## Affected commits

| commit | change |
| --- | --- |
| `f5e857ca4a74293b26327c612fddf2492bd77d08` | delete one trailer line from the message |
| `508101e759a2a035b194f9a4c56fab28fcac6f39` | delete one trailer line from the message |
| the 5 descendant commits (`8b87c7f`, `2cf1b8c`, `5471e12`, `2d9d71a`, `7ef5ee5`) | unchanged content and metadata, but new hashes because their parent chain changes |
| all 14 commits at or below `3c47b67` | completely untouched, identical hashes |

## Consequences of the new history

- The last 7 commit hashes change; everything from `3c47b67` down is
  stable. Any bookmark, CI reference, or document quoting the old top-7
  hashes becomes stale. Known internal references: figure provenance
  sidecars record `git_commit` values (`8b87c7f`, `2cf1b8c`) and
  `docs/WORKSHOP_REVIEW_SIMULATION.md` quotes `2d9d71a`;
  `docs/SESSION_LOG.md` quotes `508101e`. These are historical records of
  the states that produced the artifacts — after a rewrite they refer to
  the pre-rewrite hashes, which remain resolvable from the backup. Either
  leave them (documented here) or regenerate figures once at the new
  HEAD; do not hand-edit checksummed artifacts.
- Existing clones (including any collaborator's) will diverge; they must
  re-clone or `git fetch && git reset --hard origin/main`. Warn anyone
  with a clone **before** pushing. If any collaborator has unpushed work,
  do not proceed until it is preserved.
- GitHub contributor statistics are cached; expect hours to a few days
  before the graph refreshes after the force-push. If the Claude entry
  lingers well beyond that, contact GitHub support with the rewrite
  timestamps.

## Procedure (owner only)

1. **Backup** (mandatory):
   `git clone --mirror https://github.com/clement-callaert/fewstep-field-regularity.git ../fewstep-field-regularity-backup.git`
   or `git bundle create ../fewstep-field-regularity-before-author-rewrite.bundle --all`.
2. **Dry-run review**: run `scripts/prepare_author_cleanup.sh` with
   `CLEMENT_NAME` and `CLEMENT_EMAIL` set. It only prints; it verifies the
   two trailers are still exactly where the audit says and that no other
   co-authored commit exists.
3. **Rewrite**: the `git filter-repo --message-callback` command printed
   by the script (also inlined in the script body). It deletes exactly the
   one trailer line in the two commits and nothing else. An equivalent
   alternative for a 7-commit-deep edit is an interactive
   `git rebase -i 3c47b67` rewording the two messages by hand; filter-repo
   is preferred because it is scriptable and reviewable.
4. **Verify** (all must pass before pushing):
   - `git fsck --full`
   - `git log --all --format='%H%x09%an%x09%ae%x09%cn%x09%ce%x09%s'`
   - `git log --all --grep='Co-authored-by' --regexp-ignore-case --format='%H%n%B%n'` → empty
   - `git log --all --grep='Claude' --regexp-ignore-case --format='%H%n%B%n'` → empty
   - `git shortlog -sne --all` → owner identities only
   - `git diff --stat "$OLD_MAIN"..main` → empty
   - `git diff --exit-code "$OLD_MAIN"..main -- .` → exit 0
   The last comparison proves the rewrite changed commit metadata only,
   never repository contents.
5. **Push** (only after the backup exists, verification passed, the owner
   explicitly approves, and no collaborator depends on the old history):
   `git push --force-with-lease origin main`. Never plain `--force`.

## Recurrence prevention

`scripts/check_commit_attribution.py` (with tests) fails any commit range
containing AI author/committer identities or AI co-author/sign-off
trailers, and `CONTRIBUTING.md` states the authorship policy. The checker
is deterministic and read-only; it never edits commits.
