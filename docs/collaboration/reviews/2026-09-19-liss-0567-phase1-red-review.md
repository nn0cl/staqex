# LISS-0567 Phase 1 Red test review

## Review packet

- Scope: Review the approved Phase 1 Red contracts for the evaluator
  classical/value and invocation-frame successor. No production extraction or
  Phase 2 work was reviewed or authorized.
- Canonical documents:
  - `docs/specs/staqex-core-module-decomposition.md`
  - `docs/work-plans/WP-0164-evaluator-classical-frame-successor.md`
  - `docs/issues/LISS-0567-evaluator-classical-frame-successor.md`
  - `docs/collaboration/verification-policy.md`
  - `docs/architecture/implementation-readiness.md`
  - `docs/testing/active-red-tests.toml`
  - `tests/test_liss_0567_classical_frame_red.py`
- Changed files: the bounded Red test, Active-Red registration, and the
  linked WP/Issue/trace/review records. No production source was changed.
- Findings:
  1. The eight contracts map to the accepted Phase 0 boundary: five
     structural successor contracts and three existing behavior
     characterizations.
  2. The structural contracts fail because `frames.py`/`classical.py`, the
     callback declarations, and compatibility installers do not yet exist.
  3. Function-frame, method-receiver, and struct-return characterization
     cases pass on the current evaluator.
  4. The test fixture was corrected before this review so the struct-return
     characterization reaches a terminal measurement without weakening its
     assertion.
- Dispositions:
  - Structural gaps: accepted as intentional Red failures; address in Phase 2
    Green within the approved paths.
  - Three characterization passes: closed with deterministic evidence.
  - Fixture correction: already closed; no behavior or assertion weakening.
  - Provider, parser, semantic-IR, QASM, and public-API work: out of scope.
- Remaining blockers: none for completing the Red review. Phase 2 Green /
  Implementation still requires explicit Adjudicator approval.
- Verification result:
  - `PYTHONPATH=. ./.venv/bin/pytest tests/test_liss_0567_classical_frame_red.py -q`
    -> **5 failed, 3 passed**; the five failures are the expected successor
    structural gaps.
  - `python3 scripts/check-test-lifecycle.py` -> `ACTIVE_RED_LIFECYCLE_OK`.
  - `python3 scripts/check-document-lifecycle.py` -> passed.
  - `python3 scripts/check-coverage-ledger-consistency.py` -> passed.
  - `git diff --check` -> passed.
- Tested SHA/environment, focused versus all-blocking evidence: tested
  baseline SHA `ce0323d5` (`refactor(runtime): complete evaluator successor
  audit`) with a dirty documentation/test tree; macOS host, Python 3.14,
  repository `.venv`. This is focused Phase 1 Red evidence, not full blocking
  Green evidence.
- New/resolved failures, root causes, affected/unassessed suites and
  exclusions: five new expected failures are caused by absent successor
  modules/callback wiring/compatibility installers. Three characterization
  cases are resolved as passing. No adjacent or all-blocking suite was run;
  those suites remain unassessed and are not represented as failures.
- Spec-to-change mapping and assertion/behavior changes: the test maps to the
  accepted Phase 0 contracts for module boundaries, callback completeness,
  single state ownership, and frame/value characterization. No reviewed
  assertion was weakened and no new language behavior was introduced.
- Consumer import compatibility and structural-budget dispositions: the Red
  test requires the new modules to avoid importing the public evaluator facade
  and to keep mutable state in `Evaluator`. The Phase 0 1,200-line successor
  module guardrail remains applicable; no successor module exists yet, so no
  post-extraction budget claim is made.
- Effective review route, measurement evidence and unavailable review/budget
  gaps: `same_context` per `docs/collaboration/runtime-routing.toml`; this is
  weaker than `separate_context`. The host re-read the artifacts and reran the
  deterministic focused checks. Separate-context review was not used.
- Next approval required: `WP-0164 / LISS-0567 Phase 2 Green / Implementation 承認`.

## Evidence links

- Canonical Register: `docs/collaboration/document-register.toml`
- Representative Trace: `docs/collaboration/traces/2026-09-19-evaluator-classical-frame-successor.md`
- Detailed Evidence: `tests/test_liss_0567_classical_frame_red.py`
