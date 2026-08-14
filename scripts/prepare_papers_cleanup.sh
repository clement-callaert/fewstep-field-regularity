#!/usr/bin/env bash
# Guarded helper for removing third-party literature PDFs under papers/
# (plural). This is NOT about paper/ (singular), the owner's manuscript.
#
# THIS SCRIPT DOES NOT DELETE OR REWRITE ANYTHING. It verifies the audit
# preconditions, prints the affected paths, and prints the exact commands
# the repository owner must review and run himself. It refuses to run any
# destructive git or filesystem command.
#
# See docs/COPYRIGHT_AUDIT.md.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

# Per-invocation safe.directory only. Does not modify the user's git config.
git_safe() {
  git -c "safe.directory=${ROOT}" "$@"
}

THIRD_PARTY_PDFS=(
  papers/pdfs/albergo2023stochastic_interpolants.pdf
  papers/pdfs/bonneel2015sliced_wasserstein.pdf
  papers/pdfs/gmflow_2025.pdf
  papers/pdfs/lipman2023flow_matching.pdf
  papers/pdfs/lipschitz_guided_2025.pdf
  papers/pdfs/liu2022rectified_flow.pdf
  papers/pdfs/peyre2019computational_ot.pdf
  papers/pdfs/tong2024conditional_flow_matching.pdf
  papers/pdfs/yang2024consistency_flow_matching.pdf
)

# Refuse flags that would turn this script into an executor.
for arg in "${@:-}"; do
  case "${arg}" in
    --execute|--rm|--filter|--force|--yes)
      echo "Refusing destructive flag: ${arg}" >&2
      echo "This script only prints the owner-run plan." >&2
      exit 1
      ;;
  esac
done

echo "== Copyright cleanup plan for papers/ (literature), not paper/ =="
echo "Repository root: ${ROOT}"
echo

echo "== On-disk THIRD-PARTY-PDF inventory =="
MISSING=0
PRESENT=0
for f in "${THIRD_PARTY_PDFS[@]}"; do
  if [[ -f "${f}" ]]; then
    echo "present  ${f}"
    PRESENT=$((PRESENT + 1))
  else
    echo "absent   ${f}"
    MISSING=$((MISSING + 1))
  fi
done
echo "present=${PRESENT} absent=${MISSING}"
echo

echo "== Tracked PDF check under papers/ (should be empty) =="
TRACKED="$(git_safe ls-files 'papers/**/*.pdf' 'papers/pdfs/*.pdf' 2>/dev/null || true)"
if [[ -n "${TRACKED}" ]]; then
  echo "TRACKED third-party PDFs found (unexpected; include in git rm):"
  echo "${TRACKED}"
else
  echo "none tracked (matches docs/COPYRIGHT_AUDIT.md: never committed)"
fi
echo

echo "== History blob check for papers/**/*.pdf =="
HIST_BLOBS="$(git_safe rev-list --objects --all | awk '{print $2}' | grep -E '^papers/.*\.pdf$' || true)"
if [[ -n "${HIST_BLOBS}" ]]; then
  echo "WARNING: PDF paths exist in history objects:"
  echo "${HIST_BLOBS}"
else
  echo "none in history objects (history purge is defensive only)"
fi
echo

cat <<'INSTRUCTIONS'

================================================================
NOTHING HAS BEEN DELETED OR REWRITTEN. Review docs/COPYRIGHT_AUDIT.md,
then run each step yourself if you choose to proceed.
Do NOT run these commands against paper/ (the owner's manuscript).
================================================================

STEP 0 - CONFIRM SCOPE

  # Literature PDFs only:
  ls -la papers/pdfs/*.pdf

  # Must remain untouched:
  ls paper/gddl2026/main.tex

STEP 1 - BACKUP (mandatory before any history rewrite; recommended before
tree cleanup too). Either:

  git clone --mirror https://github.com/clement-callaert/fewstep-field-regularity.git \
      ../fewstep-field-regularity-backup.git

or, from this clone:

  git bundle create ../fewstep-field-regularity-before-papers-cleanup.bundle --all

STEP 2 - WORKING-TREE REMOVAL of untracked THIRD-PARTY-PDFs
(filesystem only; these paths are not in the index today):

  rm -f \
    papers/pdfs/albergo2023stochastic_interpolants.pdf \
    papers/pdfs/bonneel2015sliced_wasserstein.pdf \
    papers/pdfs/gmflow_2025.pdf \
    papers/pdfs/lipman2023flow_matching.pdf \
    papers/pdfs/lipschitz_guided_2025.pdf \
    papers/pdfs/liu2022rectified_flow.pdf \
    papers/pdfs/peyre2019computational_ot.pdf \
    papers/pdfs/tong2024conditional_flow_matching.pdf \
    papers/pdfs/yang2024consistency_flow_matching.pdf

  # Keep the directory for local retrieval:
  mkdir -p papers/pdfs
  touch papers/pdfs/.gitkeep

STEP 3 - INDEX REMOVAL if any PDF was ever force-added
(no-op when git ls-files papers/**/*.pdf is empty):

  git rm -f --cached --ignore-unmatch \
    papers/pdfs/albergo2023stochastic_interpolants.pdf \
    papers/pdfs/bonneel2015sliced_wasserstein.pdf \
    papers/pdfs/gmflow_2025.pdf \
    papers/pdfs/lipman2023flow_matching.pdf \
    papers/pdfs/lipschitz_guided_2025.pdf \
    papers/pdfs/liu2022rectified_flow.pdf \
    papers/pdfs/peyre2019computational_ot.pdf \
    papers/pdfs/tong2024conditional_flow_matching.pdf \
    papers/pdfs/yang2024consistency_flow_matching.pdf

  # Then the owner commits the tree-level cleanup and .gitignore update
  # himself (no AI authorship trailers):
  #   git add .gitignore docs/COPYRIGHT_AUDIT.md docs/ANONYMITY_EXPOSURE.md \
  #           scripts/prepare_papers_cleanup.sh
  #   git status
  #   git commit -m "Stop tracking third-party literature PDFs under papers/"

STEP 4 - HISTORY PURGE (owner only; destructive; only if blobs exist or
you want a defensive rewrite). Prefer git-filter-repo:

  OLD_MAIN=$(git rev-parse main)

  git filter-repo --force --refs main --preserve-commit-encoding \
    --path-glob 'papers/**/*.pdf' \
    --path-glob 'papers/pdfs/*.pdf' \
    --invert-paths

  # filter-repo removes the origin remote as a safety measure; re-add it:
  #   git remote add origin https://github.com/clement-callaert/fewstep-field-regularity.git
  #   git fetch origin

Fallback if git-filter-repo is unavailable (slower; still owner-run):

  git filter-branch --force --index-filter \
    'git rm -rf --cached --ignore-unmatch papers/pdfs/*.pdf papers/**/*.pdf' \
    --prune-empty --tag-name-filter cat -- --all

STEP 5 - VERIFY before any push:

  git rev-list --objects --all | awk '{print $2}' | grep -E '^papers/.*\.pdf$' || echo 'OK: no papers PDF blobs'
  git ls-files 'papers/**/*.pdf' || true
  test ! -f papers/pdfs/lipman2023flow_matching.pdf && echo 'OK: sample PDF absent from tree'
  test -f paper/gddl2026/main.tex && echo 'OK: owner manuscript paper/ untouched'

STEP 6 - PUSH only after explicit owner approval, and only if a history
rewrite actually changed tips:

  git push --force-with-lease origin main

Never use plain --force.

ANONYMITY NOTE (separate problem): making the repository private for the
review window covers paper/ and docs/WORKSHOP_* exposure without a rewrite.
See docs/ANONYMITY_EXPOSURE.md. Do not confuse that with this papers/ PDF purge.

INSTRUCTIONS
