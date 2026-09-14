# LISS-0543 Phase 2 Green acceptance review

## Review Target

- Artifact: active-Red lifecycle authority and deterministic refactor baseline
- Current phase: Phase 2 Green
- Requested approval: accept Green and authorize Phase 3 Refactor
- Approval type: phase
- Approved scope: LISS-0543 test lifecycle authority, baseline capture, and CI
  integration only
- Implementation allowed: yes, only for the already approved Phase 2 scope
- Post-review required: yes; Phase 3 final review remains a separate gate
- Execution batch ID: not applicable

## Canonical Evidence Re-read

- `docs/specs/staqex-core-module-decomposition.md`
- `docs/issues/LISS-0543-regression-authority-for-refactor.md`
- `.github/workflows/ci.yml`
- `scripts/check-test-lifecycle.py`
- `scripts/capture-refactor-baseline.py`
- `docs/testing/active-red-tests.toml`
- `docs/testing/refactor-baseline.json`
- both LISS-0543 contract test files and their fixtures

## What Changed

- Replaced the global `*_red.py` CI exclusion with 19 exact pytest node
  deselections backed by open-Issue, current-Phase, owner, review-date, and
  review-condition metadata.
- Added validation that fails closed for missing, duplicate, expired, unknown,
  completed, or phase-drifted entries and for reintroduction of the global
  filename glob.
- Added deterministic atomic capture of six current Python public namespaces
  and fixed representative runtime, QASM, and diagnostic evidence.
- CI now checks lifecycle metadata, regenerates and byte-compares the baseline,
  and runs all tests except the validated exact active-Red nodes.
- The repository-sanity job pins Python 3.12 because these scripts use
  standard-library `tomllib`.

## Findings and Dispositions

- Apply: the first implementation treated only module-owned definitions and
  uppercase constants as public. For modules without `__all__`, that was
  narrower than Python's actual public wildcard-import surface. Baseline
  capture now records every non-underscore name; focused tests were rerun.
- Apply: a direct script run initially could not import `compiler` because the
  repository root was absent from `sys.path`. The explicitly selected root is
  inserted before imports, and direct generation now succeeds.
- Already closed with evidence: no compiler, runtime, language, diagnostic,
  QASM, SDK, credential, network, or live-QPU implementation changed.
- Already closed with evidence: all previously passing tests are blocking;
  only the 19 named active-Red nodes are deselected.
- Out of scope: repairing or reclassifying the semantics of those 19 active
  Red nodes. The accepted architecture explicitly excludes those behavior
  fixes from structural-refactor work.

## Failure Scenarios Reviewed

- A completed or unknown issue retains a test exclusion.
- Manifest phase differs from the issue's current phase.
- A test disappears, is duplicated, or passes its review deadline.
- CI silently restores a suffix-wide Red exclusion.
- Baseline generation receives a missing input and leaves a partial artifact.
- Baseline evidence contains a timestamp, current working directory, or
  machine-specific repository path.
- Future extraction removes an accidentally imported but publicly reachable
  non-underscore module name.

## Verification

- Focused LISS-0543 tests: 12 passed.
- Full blocking pytest: 2,043 passed, 19 exact nodes deselected.
- Spec Verification: 161/161 passed.
- Lifecycle validation: 19 valid entries as of 2026-09-11.
- Baseline: three behavior cases, six public modules, deterministic byte
  regeneration, and no absolute repository path.
- Script `compileall` and `git diff --check`: passed.
- Document lifecycle and coverage-ledger checks are rerun after this packet is
  added and recorded in the work trace.

## Isolation and Blocker

- Configured review isolation is `same_context`, which is weaker than
  `separate_context`.
- LISS-0543 is size L and the implementing and reviewing model would be the
  same. Repository review policy therefore forbids claiming an independent
  same-context approval. This packet presents deterministic evidence for the
  human Adjudicator; it is not an agent self-approval.

## Applied Process Lessons

- Phase acceptance boundary: the complete suite and the focused contract suite
  were both run, rather than relying only on the new checker tests.
- Status drift: Issue, work-plan, trace, and active-Red phase metadata are
  synchronized before requesting the next gate.
- Boundary completeness: the public baseline follows Python's actual export
  behavior rather than a hand-selected symbol subset.

## Next Approval Required

`LISS-0543 Phase 3 Refactor 承認`

