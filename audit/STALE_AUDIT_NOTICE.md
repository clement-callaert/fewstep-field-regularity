# Stale audit notice

The files in this directory dated 2026-08-13 and named `PASS5_*`,
`FINAL_ARXIV_AUDIT.md`, `NEURIPS_SYNC_AUDIT.md`, `RELEASE_GATE.md`,
`REPOSITORY_INVENTORY.md`, and the `gates/` transcripts describe earlier
workshop builds (including an eight-page workshop PDF) and earlier
repository layouts. They are retained as history. In particular,
`REPOSITORY_INVENTORY.md` recorded `talks/` as untracked; that directory
is now on public `main`.

`audit/PASS7_FINAL_AUDIT.md` is historical: it describes the polish
that landed as commit `44bc8fe9faf78aebb328a18e0f6dd87252467e5e`, including
a then-dirty working tree that is no longer the branch tip.

`audit/PASS8_RELEASE.md` is historical: it describes the pre-merge
artifact-carrier state on `fix/pass6-polish`. Pull request #1 has since
been merged as `25186a5337ae8c85a9367051da24953b80b133a5`. GitHub Actions
run https://github.com/clement-callaert/fewstep-field-regularity/actions/runs/31822152552
on that merge succeeded for `cpu-checks` on Python 3.11 and 3.12.

They are **not** the current audit of the manuscripts in `paper/arxiv/`
and `paper/gddl2026/`. The current record is
`audit/PASS9_POST_MERGE_RELEASE.md`. Provenance sidecars record
`source_commit` as the scientific source snapshot that generated those
figures; they do not claim to contain the SHA of a later
artifact-carrier or documentation commit.
