# Review Summary: LISS-0580 Phase 1 Red

## Review packet

- Scope: Phase 1 Red test-contract review only; no implementation.
- Canonical documents re-read: accepted specification, LISS-0580, WP-0173,
  ADR 0227, verification policy, and runtime-routing policy.
- Changed files reviewed: `tests/test_liss_0580_legacy_when_binding_red.py`
  and `docs/testing/active-red-tests.toml`.
- Findings:
  - **Initial finding — resolved:**
    `test_canonical_control_mixture_fallback_reaches_legacy_when_binding`
    initially observed the host path, `_run_legacy_ast_body`, and `_bind_when`
    without establishing the canonical plan family/fallback choice. The test
    now wraps `execute_control_mixture_plan`, asserts its family is
    `control_mixture`, records that its deferred eligibility checks are all
    false, and records that this executor invocation calls the legacy body
    once. It still asserts `_bind_when` is reached through `run_source`.
- Disposition: resolved in the test-only correction; no remaining test
  contract blocker found on same-context re-review.
- Remaining blockers: Adjudicator acceptance of the Phase 1 Red review;
  separate Phase 2 implementation approval remains mandatory.
- Verification: focused suite **3 failed, 1 passed** as expected; adjacent
  consumer run **3 expected structural failures, 12 passed**; lifecycle,
  `py_compile`, and `git diff --check` passed. No collection errors. The
  failures are the three intended structural gaps.
- Tested SHA/environment: base SHA
  `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`, dirty tree; macOS 27.0.0 arm64,
  Python 3.14.6, repository `.venv`. Commands were the focused pytest file
  and its combined run with LISS-0495, LISS-0225, ket-arm, and LISS-0375
  suites. All-blocking suites were not run; they are not required for this
  test-only review and remain a later-phase requirement.
- Failure comparison: no new product failure identified. The corrected
  characterization passes against current behavior. Broader blocking suites
  remain unassessed for this Phase 1 review.
- Spec mapping: structural checks map to Scenario D. The passing runtime
  characterization maps to Scenario B and asserts the `control_mixture`
  executor's ineligible fallback and live `_bind_when` callback. No
  assertions were weakened or excluded.
- Consumer compatibility/structure: Phase 1 changes only tests and lifecycle
  metadata; no runtime consumer or source structure changed. Private consumer
  compatibility remains for Phase 2/3.
- Effective review route: `same_context`, configured in
  `docs/collaboration/runtime-routing.toml`, weaker than separate-context
  review. No model switch was available in-session. Diff measurement is
  incomplete because the worktree is dirty and the Phase 1 test is untracked;
  no large-change override is enabled.
- Next approval: Phase 2 Green/Implementation, separately from the accepted
  Phase 1 test review.

## Evidence links

- Canonical Register: `docs/specs/evaluator-legacy-when-binding.md`
- Representative Trace: `docs/collaboration/traces/2026-09-27-liss-0580-legacy-when-design.md`
- Detailed Evidence: `docs/issues/LISS-0580-legacy-when-binding-extraction.md`

## Review isolation

Same-context review; this is weaker than separate-context review and is not
Adjudicator approval.

## Re-review

- Date: 2026-09-27.
- The test now asserts the exact canonical family, false deferred eligibility
  within that executor, and its own legacy-body invocation before confirming
  the `_bind_when` callback through Host.
- Re-ran focused (**3 expected failures, 1 pass**), adjacent consumer run
  (**3 expected failures, 12 passes**), lifecycle, test compilation, and
  `git diff --check`; all non-pytest checks passed.
- Disposition: no remaining test-contract blocker found. This same-context
  reviewer disposition is not human approval; implementation is not
  authorized.

## Adjudicator Review Target

- Artifact: corrected Phase 1 Red tests and this Review Summary.
- Current phase: Phase 1 Red test review.
- Requested approval: accept the Phase 1 Red test contract.
- Approval type: phase.
- Approved scope: tests/fixtures and active-Red lifecycle registration only.
- Implementation allowed: no.
- Post-review required: yes; separate Phase 2 Green/Implementation approval.
- Decision: accepted by Adjudicator on 2026-09-27 via
  `LISS-0580 Phase 1 Red テストレビュー承認`.

## Next Adjudicator Review Target

- Artifact: accepted specification and reviewed Phase 1 Red evidence.
- Current phase: Phase 2 Green verified.
- Decision: Phase 2 Green/Implementation was approved and executed on
  2026-09-27; evidence is recorded in the accepted specification and trace.

## Next Adjudicator Review Target

- Artifact: Phase 2 implementation and verification evidence in the accepted
  specification, Issue, and WP.
- Current phase: Phase 3 Refactor executed and reviewed.
- Requested approval: final review of the Phase 3 result.
- Approval type: phase.
- Approved scope: inspect the moved implementation for readability and
  responsibility boundaries; make only behavior-preserving refactor changes;
  rerun tests and document reviewer risks.
- Implementation allowed: no further implementation in this review step.
- Post-review required: yes; commit and tested-final-commit evidence.
- Decision: Adjudicator approved `LISS-0580 Phase 3 最終レビュー 承認` on
  2026-09-27. Commit and tested-final-commit evidence remain outstanding.

## Phase 3 Refactor Review Packet

- Scope: readability, responsibility boundaries, and consumer compatibility
  for the extracted legacy `when` binder; no semantic change.
- Canonical documents re-read: accepted LISS-0580 specification, ADR 0227,
  LISS-0580, WP-0173, runtime-routing/verification/source-quality policies,
  and current Phase 1 review evidence.
- Changed Phase 3 source: one explanatory comment in
  `legacy_control_binding.py`; no test assertions or behavior changed.
- Findings: the module's helpers already have clear responsibilities. A
  further extraction would increase navigation without reducing complexity.
  The arm-selection precedence was a reviewer question; the comment now
  answers it in place.
- Dispositions: no blockers; no additional code changes recommended within
  the approved scope.
- Verification: focused/adjacent **15 passed**; full blocking suite
  **2,275 passed in 314.44s**; lifecycle and coverage-ledger checks passed;
  `git diff --check` passed.
- Evidence: base SHA `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`, dirty tree;
  macOS 27.0.0 arm64, Python 3.14.6, pytest 9.1.1. A final commit does not
  yet exist, so final-SHA evidence is outstanding. Ruff unavailable.
- Consumers: dispatcher, context protocol callback, compatibility installer,
  live identity check, and accepted characterization suites; no extra private
  imports/monkeypatch consumers found.
- Structure: successor 141 lines, compatibility module 289 lines, evaluator
  1,305 lines. No numeric structure budget; large-change override is absent
  (disabled). Workspace inventory is 13 changed files (4 modified, 9
  untracked; manually counted 1,379 additions and 102 deletions).
  `review-change.py` cannot model the current dirty/untracked snapshot as a
  Git-ref comparison; the configured conditional review override is disabled.
- Isolation: `same_context`, weaker than separate-context; same-context review
  is not Adjudicator approval.
- Next action: commit when authorized, then rerun all blocking suites on the
  final commit before closure.
