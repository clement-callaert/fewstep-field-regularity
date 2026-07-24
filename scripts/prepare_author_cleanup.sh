#!/usr/bin/env bash
# Guarded helper for the one-time removal of the two Claude co-author
# trailers identified in docs/GIT_AUTHORSHIP_AUDIT.md.
#
# THIS SCRIPT DOES NOT REWRITE ANYTHING. It only verifies preconditions,
# prints the affected commits, and prints the exact commands the
# repository owner must review and run himself. It refuses to run any
# history-modifying command.
#
# Affected commits (message-only changes; trees must stay identical):
#   f5e857ca4a74293b26327c612fddf2492bd77d08
#   508101e759a2a035b194f9a4c56fab28fcac6f39

set -euo pipefail

AFFECTED_COMMITS=(
  f5e857ca4a74293b26327c612fddf2492bd77d08
  508101e759a2a035b194f9a4c56fab28fcac6f39
)
TRAILER_PATTERN='^Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>$'

: "${CLEMENT_NAME:?Set CLEMENT_NAME explicitly (no default is provided)}"
: "${CLEMENT_EMAIL:?Set CLEMENT_EMAIL explicitly (no default is provided)}"

case "${CLEMENT_NAME}" in
  *placeholder*|*PLACEHOLDER*|*TODO*|*example*|"Your Name"|"")
    echo "Refusing placeholder CLEMENT_NAME: ${CLEMENT_NAME}" >&2; exit 1;;
esac
case "${CLEMENT_EMAIL}" in
  *placeholder*|*PLACEHOLDER*|*TODO*|*example.com*|*@example*|"")
    echo "Refusing placeholder CLEMENT_EMAIL: ${CLEMENT_EMAIL}" >&2; exit 1;;
esac

echo "== Verifying the configured identity matches existing history =="
if ! git log --format='%an <%ae>' | sort -u | grep -Fq "${CLEMENT_NAME} <${CLEMENT_EMAIL}>"; then
  echo "WARNING: '${CLEMENT_NAME} <${CLEMENT_EMAIL}>' does not appear as an" >&2
  echo "existing author identity. Double-check before any rewrite." >&2
fi
echo "Note: this cleanup removes trailers only; it must NOT change any"
echo "author or committer identity. The identity variables exist purely to"
echo "confirm you are operating as the repository owner."

echo
echo "== Commits that would be affected (message-only) =="
for c in "${AFFECTED_COMMITS[@]}"; do
  echo "--- ${c}"
  git log -1 --format='%H%n%an <%ae>%n%cn <%ce>%n%B' "${c}"
done

echo "== Confirming the trailer is present exactly where expected =="
for c in "${AFFECTED_COMMITS[@]}"; do
  if git log -1 --format='%B' "${c}" | grep -Eq "${TRAILER_PATTERN}"; then
    echo "trailer present in ${c}"
  else
    echo "trailer NOT present in ${c} — audit is stale, STOP." >&2
    exit 1
  fi
done

OTHER=$(git log --all --grep='Co-authored-by' --regexp-ignore-case --format='%H' \
  | grep -vF -e "${AFFECTED_COMMITS[0]}" -e "${AFFECTED_COMMITS[1]}" || true)
if [ -n "${OTHER}" ]; then
  echo "Unexpected additional co-authored commits found — STOP and re-audit:" >&2
  echo "${OTHER}" >&2
  exit 1
fi

cat <<'INSTRUCTIONS'

================================================================
NOTHING HAS BEEN REWRITTEN. Review the plan below and run each
step yourself only after reading docs/GIT_AUTHORSHIP_CLEANUP_PLAN.md.
================================================================

STEP 1 — BACKUP (mandatory before any rewrite). Either:

  git clone --mirror https://github.com/clement-callaert/fewstep-field-regularity.git \
      ../fewstep-field-regularity-backup.git

or, from this clone:

  git bundle create ../fewstep-field-regularity-before-author-rewrite.bundle --all

STEP 2 — RECORD the old tip for later verification:

  OLD_MAIN=$(git rev-parse main)

STEP 3 — REWRITE (message-only, the two listed commits only).
Requires git-filter-repo. The callback deletes exactly the one trailer
line and touches no other commit, no identity, no date, no tree:

  git filter-repo --force --refs main --preserve-commit-encoding \
    --message-callback '
import re
target = b"Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
if target in message:
    lines = [l for l in message.splitlines() if l.strip() != target]
    while lines and lines[-1] == b"":
        lines.pop()
    message = b"\n".join(lines) + b"\n"
return message
'

  (filter-repo removes the origin remote as a safety measure; re-add it:
   git remote add origin https://github.com/clement-callaert/fewstep-field-regularity.git
   git fetch origin)

STEP 4 — VERIFY before any push:

  git fsck --full
  git log --all --format='%H%x09%an%x09%ae%x09%cn%x09%ce%x09%s'
  git log --all --grep='Co-authored-by' --regexp-ignore-case --format='%H%n%B%n'
  git log --all --grep='Claude' --regexp-ignore-case --format='%H%n%B%n'
  git shortlog -sne --all
  git diff --stat "${OLD_MAIN}"..main
  git diff --exit-code "${OLD_MAIN}"..main -- .

The last two commands MUST print no differences: only commit metadata
(the two messages) changed, never file contents.

STEP 5 — PUSH (owner only, after explicit approval, after confirming no
collaborator depends on the old history):

  git push --force-with-lease origin main

Never use plain --force.
INSTRUCTIONS
