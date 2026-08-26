# PR #574 conflict resolution trace

## Scope

- Pull request: #574, `codex/adr-quantum-mental-model` → `main`.
- Trigger: GitHub reported the PR as conflicting with the current `main`.
- Resolution commit: `8caed9d9` (`merge: resolve PR 574 conflicts with main`).

## Resolution policy

- Current `main` canonical contract and architecture documents were retained
  where the PR branch had older copies or broad historical deletions.
- The parser and evaluator were resolved against the current `main` versions,
  retaining the existing scientific-name resolution, tensor-call handling,
  norm expression handling, and state-first evaluation boundaries.
- PR-specific scientific-alias and quantum-mental-model content was retained
  only where it was already represented by the current canonical files.
- No new provider, datastore, deployment technology, or language semantics
  were selected during conflict resolution.

## Verification evidence

- No unresolved Git conflict markers remain.
- `git diff --check` passed.
- Python syntax compilation passed for the resolved parser, evaluator,
  scientific vocabulary, and alias test files.
- `python3 tests/spec_verification/run_all.py` passed: 161/161 (100%).
- GitHub CI run `32963641471` passed Kernel root suites and Spec verification;
  Repository sanity failed only because this trace was not yet present.

## Follow-up

This trace is added to satisfy the repository's contract-file change
traceability gate. The PR must rerun Repository sanity after this commit; no
merge is requested by this trace alone.
