# Git authorship audit

Date: 2026-07-24. Audited at HEAD `7ef5ee511f8750fd4409e9a69de5f019dead69cf`
(equal to `origin/main`; working tree clean at audit time; no divergence
before or after `git fetch origin`).

Scope: every commit reachable from any ref (`git log --all`), all branches,
all tags, plus trailer and message searches for `Co-authored-by`,
`Signed-off-by`, `Claude`, and `Anthropic` (case-insensitive).

Email policy: local parts are redacted in this file because it may become
public. Full addresses are visible locally via `git log --format='%ae %ce'`.

## Repository state at audit

- Branch: `main`, tracking `origin/main`
  (`https://github.com/clement-callaert/fewstep-field-regularity.git`).
- HEAD = `origin/main` = `7ef5ee51…`; ahead/behind 0/0. The public remote
  contains the completed Phase 4 and workshop work, including both
  offending commits below.
- Branches: only `main` (local) and `origin/main`. No tags. No commits
  unreachable from `main`.

## Commit table

All 21 commits were inspected. Only rows needing attention, plus the two
identity classes, are expanded; all other commits are authored and
committed solely by the owner with no trailers.

| commit | author | author email | committer | committer email | trailer | reachable from main | action needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `f5e857ca4a74293b26327c612fddf2492bd77d08` | Clément Callaert | `<redacted>@gmail.com` | Clément Callaert | `<redacted>@gmail.com` | `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` | yes (pushed) | remove trailer via message-only rewrite |
| `508101e759a2a035b194f9a4c56fab28fcac6f39` | Clément Callaert | `<redacted>@gmail.com` | Clément Callaert | `<redacted>@gmail.com` | `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` | yes (pushed) | remove trailer via message-only rewrite |
| `a48a2c66de78630331ba28e1b4669dc4df03a2a8` (initial commit) | Clément CALLAERT | `124050291+clement-callaert@users.noreply.github.com` | GitHub | `noreply@github.com` | none | yes | none — normal GitHub web-flow committer for a repository created in the web UI; not an AI identity |
| all 18 remaining commits | Clément Callaert | `<redacted>@gmail.com` | Clément Callaert | `<redacted>@gmail.com` | none | yes | none |

Searches with zero hits: AI author names, AI committer names, AI email
addresses as author/committer, `Signed-off-by` trailers (any), bot
authors, commits created through an AI account, stale branches, tags.

## Classification

**Class 3 — AI as co-author only.** Claude appears exclusively through the
`Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` trailer in the two
commit messages above. It is never the author or committer of any commit.
GitHub's contributors graph counts co-author trailers, which is exactly why
a Claude identity shows as a repository contributor.

Not applicable: class 1 (AI author), class 2 (AI committer), class 4
(stale branch/tag), class 5 (nothing found), class 6 (stale graph only —
the graph is accurate; it reflects the two real trailers).

## Why the trailers exist

The two commits were created on 2026-07-24 during an AI-assisted working
session. The tooling appended its default co-author trailer to the commit
messages before the owner instructed it to stop; later commits from the
same session (`8b87c7f` onward) have no trailer. The owner states that he
owns and directed the work and wants only his own commits represented; the
file trees of both commits are his reviewed work product, so removing the
trailers reattributes nothing — it deletes an unwanted automatic tooling
trailer. This paragraph documents that reasoning per audit policy.

## Correction plan (prepared, not executed)

Both offending commits are already on the public remote, so a local
message edit alone is insufficient: history must be rewritten for the last
seven commits (`f5e857c` is the oldest affected) and the branch updated
with a verified, backed-up `git push --force-with-lease`. The rewrite must
change only the two commit messages (trailer removal); author identities,
dates, and every file tree must remain byte-identical.

See `docs/GIT_AUTHORSHIP_CLEANUP_PLAN.md` for the full procedure and
`scripts/prepare_author_cleanup.sh` for the guarded, non-executing helper.
Only the repository owner runs any of it.

## Git identity check (Stage 1 requirement)

- `git config user.name` → `Clément Callaert` (global)
- `git config user.email` → `<redacted>@gmail.com` (global)
- `git config --local user.name` / `user.email` → unset

The effective identity matches the 20 owner-authored commits and the
GitHub account `clement-callaert` (confirmed by the `124050291+…noreply`
initial commit). No automatic change was made. If the owner wants the
identity pinned per-repository, he may run himself:

```bash
git config --local user.name "Clément Callaert"
git config --local user.email "<the exact email already used in existing commits>"
```
