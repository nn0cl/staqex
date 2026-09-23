# LISS-0568 Phase 1 Red test review

## Review packet

- Scope: Review the approved Phase 1 Red contracts for the evaluator
  classical/value and continuous body successor. No Phase 2 implementation was
  reviewed or authorized.
- Canonical documents:
  - `docs/specs/staqex-core-module-decomposition.md`
  - `docs/work-plans/WP-0165-evaluator-value-continuous-body-successor.md`
  - `docs/issues/LISS-0568-evaluator-value-continuous-body-successor.md`
  - `docs/collaboration/verification-policy.md`
  - `docs/architecture/implementation-readiness.md`
  - `docs/testing/active-red-tests.toml`
  - `tests/test_liss_0568_value_continuous_red.py`
- Changed files: the bounded Red test, Active-Red registration, and linked
  WP/Issue/trace records. No production implementation changed.
- Findings:
  1. The eight tests map to the accepted Phase 0 boundary: five structural
     successor/callback/wiring contracts and three behavior characterizations.
  2. The five structural contracts fail because `continuous.py`, the narrow
     value/continuous callbacks, and the family-specific compatibility
     installers do not yet exist.
  3. Classical value execution, continuous finiteization, and continuous
     provenance characterizations pass on the current evaluator.
  4. The initial classical fixture setup used a nonexistent `Evaluator.run()`
     API; it was corrected to the repository `run_source()` host entrypoint
     before the reviewed Red run without weakening an assertion.
- Dispositions:
  - Five structural failures: accepted as intentional Red gaps for Phase 2
    Green.
  - Three characterization passes: closed with deterministic evidence.
  - Fixture correction: already closed; no product defect inferred.
  - Parser, Semantic IR, QASM, provider, network, and public API retirement:
    out of scope.
- Remaining blockers: none for the Red test review. Phase 2 Green /
  Implementation requires explicit approval.
- Verification result:
  - `PYTHONPATH=. ./.venv/bin/pytest tests/test_liss_0568_value_continuous_red.py -q`
    -> **5 failed, 3 passed**.
  - `python3 scripts/check-test-lifecycle.py` -> `ACTIVE_RED_LIFECYCLE_OK
    entries=1`.
  - `python3 scripts/check-document-lifecycle.py` -> passed.
  - `python3 scripts/check-coverage-ledger-consistency.py` -> passed.
  - `git diff --check` -> passed.
- Tested SHA/environment, focused versus all-blocking evidence: baseline
  `2cb27b2e` with a dirty test/documentation tree; macOS host, Python 3.14,
  repository `.venv`. This is focused Phase 1 Red evidence, not full Green
  evidence.
- New/resolved failures, root causes, affected/unassessed suites and
  exclusions: five expected structural failures; three characterization cases
  pass. No adjacent or all-blocking suite was run, so those remain unassessed.
- Spec-to-change mapping and assertion/behavior changes: tests cover module
  entrypoints, no-facade/state ownership, context callbacks, compatibility
  wiring, and existing classical/continuous behavior. No reviewed assertion or
  language behavior changed.
- Consumer import compatibility and structural-budget dispositions: the Red
  contract requires successor modules to avoid the public facade and mutable
  state copies. The 1,200-line module guardrail remains applicable; no new
  implementation module exists yet, so no post-extraction budget claim is
  made.
- Effective review route, measurement evidence and unavailable review/budget
  gaps: `same_context` per runtime routing; weaker than `separate_context`.
  The reviewer re-read the artifacts and reran all deterministic Phase 1
  checks. Separate-context review was not used.
- Next approval required:
  `WP-0165 / LISS-0568 Phase 2 Green / Implementation 承認`.

## Evidence links

- Canonical Register: `docs/collaboration/document-register.toml`
- Representative Trace: `docs/collaboration/traces/2026-09-19-evaluator-value-continuous-body-successor.md`
- Detailed Evidence: `tests/test_liss_0568_value_continuous_red.py`
