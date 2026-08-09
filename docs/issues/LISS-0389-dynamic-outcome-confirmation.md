# LISS-0389: Thread real-execution outcome confirmation into dynamic_trace

## Metadata

- Local issue ID: LISS-0389
- Status/phase: **complete** (2026-08-09) — Adjudicator Completion approval;
  PR [#492](https://github.com/nn0cl/staqex/pull/492)
- Type: Feature Path (Kernel/Host — additive DTO field + internal signal
  threading; no new surface, no capability-law change)
- Priority: P2
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [ADR 0198 Amendment](../architecture/adr/0198-dynamic-jobresult-composition.md#amendment-accepted-2026-08-09-physical-outcome-confirmation)
  (Accepted 2026-08-09, PR [#490](https://github.com/nn0cl/staqex/pull/490))
- Parent: ADR 0198 (Accepted) + its Amendment (Accepted)
- Depends on: [LISS-0387](LISS-0387-dynamic-real-mid-circuit-measure.md)
  (**complete**) — real `_collapse_dynamic_wire`; LISS-0388 (**complete**)
- Related: `compiler/staqex/runtime/evaluator.py` (`EvalResult`,
  `_collapse_dynamic_wire`, `_run_dynamic_qpu_block`); `compiler/staqex/host.py`
  (`DynamicTraceReport`, `project_dynamic_trace`, `_submit_compiled`)
- Blocks: none
- Branch: `feature/liss-0389-dynamic-outcome-confirmation`
- GitHub Issue / PR: [#492](https://github.com/nn0cl/staqex/pull/492)

## Intent

Close the gap the ADR 0198 Amendment names: `dynamic_trace.controller_bindings`
currently reports a Host-supplied outcome as achieved fact even when the
real evaluator (LISS-0387) found it physically impossible and vacuumed the
run. Add `DynamicTraceReport.physical_outcome_confirmed: bool` (default
`True`), set to `False` only when the real local evaluator positively
determined a recorded controller binding was unreachable.

## Explicitly out of scope

- `JobResult.status` semantics — stays `"succeeded"` for a vacuum run
  (not a defect; matches Static Kernel precedent). This Issue does not
  touch `status`.
- Reset, capability-law changes, new profiles — untouched (ADR 0199/0200
  boundary unchanged).
- Any live-provider path (does not exist yet; the amendment's default
  `True`-when-unchecked already covers that case honestly).
- Multiple `dynamic qpu` blocks in one program — `build_dynamic_exec_request`
  only handles the first block today (pre-existing limitation, unrelated to
  this Issue); the new field tracks that same single-block scope.

## Plan-locked decisions (Adjudicator 2026-08-09, ADR 0198 Amendment)

1. **`EvalResult` gains `dynamic_outcomes_confirmed: bool = True`** (Kernel-
   internal, not Host-facing) — set to `False` on the evaluator instance
   when `_collapse_dynamic_wire` returns a vacuum/empty joint for any
   mid-circuit measurement in the run. Tracked as an instance attribute
   (`self._dynamic_outcomes_confirmed`, initialized `True` per
   `_run_unit_body` call) rather than changing `_run_dynamic_qpu_block`'s
   return signature, since `EvalResult` is only assembled once at the end
   of `_run_unit_body`.
2. **`DynamicTraceReport` gains `physical_outcome_confirmed: bool = True`**
   (additive, keyword field with default — `DynamicTraceReport` has one
   construction site, `project_dynamic_trace`, already keyword-based; no
   positional-compatibility risk).
3. **`host.py::_submit_compiled` reconciliation:** after
   `evaluated = evaluator.run_unit(...)` completes (and only when
   `dynamic_trace is not None`, i.e. a dynamic run actually happened),
   rebuild `dynamic_trace` via `dataclasses.replace(dynamic_trace,
   physical_outcome_confirmed=evaluated.dynamic_outcomes_confirmed)` before
   constructing the final `JobResult`.
4. **No change to `JobResult.status`, `measurements`, or any existing
   `dynamic_trace` field's meaning** — purely additive.

## Acceptance reference

To be added to
[`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md) as a new
"Acceptance scenarios — physical outcome confirmation (ADR 0198 Amendment,
LISS-0389)" section.

### Draft Gherkin (Plan review only, not yet normative)

```gherkin
Feature: dynamic_trace confirms whether the reported outcome was physically real

  Scenario: consistent supplied outcome is confirmed
    Given the LISS-0383 measure-only fixture with a Host-supplied outcome
      consistent with the prepared state
    When the Job is submitted through the Fake-gated Host path
    Then JobResult.dynamic_trace.physical_outcome_confirmed is True

  Scenario: inconsistent supplied outcome is not confirmed
    Given the LISS-0387 fixture with a Host-supplied outcome that is
      physically impossible against the prepared state (the run vacuums)
    When the Job is submitted through the Fake-gated Host path
    Then JobResult.status is still "succeeded" (unchanged; not a defect)
    And JobResult.dynamic_trace.physical_outcome_confirmed is False
    And dynamic_trace.controller_bindings still shows the supplied label
      (audit trail), now clearly marked as not confirmed

  Scenario: existing shipped tests are unaffected by the additive default
    Given any LISS-0383/0385/0386/0388 test that does not assert
      physical_outcome_confirmed
    When it runs against this Issue's Green implementation
    Then it continues to pass unchanged (regression sweep, not a new
      assertion)
```

## AI planning record (size S)

- Status: Plan drafted; awaiting Adjudicator Plan approval
- Authoring environment: Claude Code, 2026-08-09
- Size: `S` — one `EvalResult` field + one instance-attribute set in
  `_collapse_dynamic_wire`, one `DynamicTraceReport` field, one
  `dataclasses.replace` call in `host.py`, new tests.
- Route: AT-TDD after Plan approval.
- Confidence: high — mechanism fully scoped during ADR Amendment
  investigation; only one construction site for `DynamicTraceReport`
  confirmed by direct grep.
- Revision links: implements the ADR 0198 Amendment (PR #490).

## Exit criteria

- [x] Plan approval (2026-08-09).
- [x] Phase 1 Red (2026-08-09):
      `tests/test_liss_0389_dynamic_outcome_confirmation_red.py` — both
      tests failed for the stated reason
      (`AttributeError: 'DynamicTraceReport' object has no attribute
      'physical_outcome_confirmed'`).
- [x] Phase 2 Green (2026-08-09): `EvalResult.dynamic_outcomes_confirmed`
      + `_collapse_dynamic_wire` sets `self._dynamic_outcomes_confirmed =
      False` on vacuum; `DynamicTraceReport.physical_outcome_confirmed`
      added; `host.py` reconciles via `dataclasses.replace` after
      `evaluator.run_unit` completes. Both new tests pass; no test edited
      to force it.
- [x] Phase 3 Refactor: reviewed diff (evaluator.py +11/-0, host.py
      +14/-1) — minimal, no further changes needed.
- [x] Spec (`staqex-dynamic-qpu-lane.md`) synced with the real Gherkin;
      status table updated.
- [x] Full regression sweep re-run: **1381 passed** (2026-08-09), up from
      1379 by exactly the 2 new tests — confirmed additive-only (no
      existing `dynamic_trace` assertion broke).
- [x] Completion approval (2026-08-09); PR [#492](https://github.com/nn0cl/staqex/pull/492).
