# LISS-0386: Host auto-attach of inferred reuse/reset capability demand

## Metadata

- Local issue ID: LISS-0386
- Status/phase: **complete** (2026-08-09) — Adjudicator Completion approval;
  PR [#484](https://github.com/nn0cl/staqex/pull/484)
- Type: Feature Path (Kernel/Host — wire LISS-0385 inference into the Fake
  request builder; no new surface, no profile enablement)
- Priority: P1
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [ADR 0199](../architecture/adr/0199-dynamic-qubit-reuse-reset.md)
  Follow-up work item (Decision Gate option 1, post-PR #483)
- Parent: ADR 0199 (Accepted; Option B declined)
- Depends on: [LISS-0383](LISS-0383-dynamic-fake-executor-wire.md)
  (**complete**); [LISS-0385](LISS-0385-dynamic-reuse-reset-demand.md)
  (**complete**) — `infer_dynamic_capability_demand`
  (`compiler/staqex/dynamic_capability.py`)
- Related: [ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md);
  `compiler/staqex/dynamic_fake_wire.py`; `compiler/staqex/host.py`
- Blocks: none
- Branch: `feature/liss-0386-host-auto-attach-plan`
- GitHub Issue / PR: [#484](https://github.com/nn0cl/staqex/pull/484)

## Intent

`compiler/staqex/dynamic_fake_wire.py::build_dynamic_exec_request` currently
hardcodes `DynamicCapabilityDemand(needs_reset=False, needs_reuse=False,
needs_latency=False)` regardless of source (line ~144). LISS-0385 already
implements `infer_dynamic_capability_demand(unit)` but nothing on the Host
Fake-exec path calls it — LISS-0383 recorded this explicitly as a soft-depend
gap. This Issue wires the two together so a program that demands reuse is
honestly rejected through the Fake-gated Host path, not silently accepted.

## Trigger finding (confirmed in code before Plan, not hypothetical)

The LISS-0383 "accepts without physical claim" success fixture
(`_SOURCE_MATCH` in
`tests/test_liss_0383_dynamic_fake_executor_wire_red.py`) is:

```
Controller<Bit> bit = measure q
match bit {
    0 => { apply(X, q) }
    1 => { apply(Z, q) }
}
```

This is exactly the shape `infer_dynamic_capability_demand` flags as
`needs_reuse=True` (post-measure quantum use of the measured wire inside a
`match` arm). Auto-attaching inference therefore flips
`test_with_fake_gate_and_supplied_outcomes_accepts_without_physical_claim`
from accepted to rejected. This is Adjudicator-resolved (2026-08-09, 案C):
the prior "accept" was silently hiding an unsupported-capability demand
behind the hardcoded `False`; auto-attach closes that honesty gap rather than
creating a regression.

## Explicitly out of scope

- `needs_reset` auto-inference (LISS-0385 boundary: never inferred).
- Enabling any Fake profile to actually perform reuse/reset (separate
  profile-enable Issue; ADR 0199 Follow-up #2).
- OpenQASM dynamic emission; live provider; `reset` keyword (ADR 0199 Option
  B, declined).
- Changing `DYN_CAPABILITY_REUSE` / `DYN_CAPABILITY_RESET` diagnostic codes
  or `physical_execution_claimed` semantics.

## Plan-locked decisions (Adjudicator 2026-08-09, 案C)

1. **Auto-attach:** `build_dynamic_exec_request` calls
   `infer_dynamic_capability_demand(unit)` and uses its result as
   `capability_demand` instead of the hardcoded all-`False` value.
   `needs_reset` remains `False` from that function (LISS-0385 contract);
   this Issue does not add reset inference.
2. **LISS-0383 success scenario amendment:** the "with Fake gate and supplied
   outcomes, Fake accepts without physical claim" scenario's fixture is
   revised to a **measure-only match that does not reuse the measured wire**
   (e.g. arms bind/observe a classical outcome or apply to a fresh wire,
   never the measured one). This keeps that scenario's intent (Fake accepts
   a supported program under supplied outcomes) true after auto-attach.
3. **Repurposed regression:** the current reuse-demanding `_SOURCE_MATCH`
   fixture is kept as a **new** scenario proving the same program now fails
   closed end-to-end through the Host Fake-gated path (`DYN_CAPABILITY_REUSE`,
   `physical_execution_claimed=False`), rather than deleted.
4. **No Host silent re-init; no new keyword; no profile change.**

## Acceptance reference

To be added to
[`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md) as a new
"Acceptance scenarios — Host auto-attach inferred capability demand
(LISS-0386)" section, alongside an amendment to the existing LISS-0383
section's success-scenario `Given`. Drafted below for Plan review; not yet
normative until Plan approval.

### Draft Gherkin (Plan review only)

```gherkin
Feature: Host auto-attaches inferred reuse demand into the Fake-exec request

  Scenario: measure-only match without wire reuse still accepts (regression guard)
    Given a mid-circuit dynamic program
      """
      Controller<Bit> bit = measure q
      match bit {
          0 => { }
          1 => { }
      }
      """
    And settings.dynamic_fake_profile is SIM0_EXACT
    And settings.dynamic_supplied_outcomes supplies each mid-circuit token
    When the Job is submitted through the Fake-gated Host path
    Then DynamicExecResult.status is accepted
    And DynamicExecResult.physical_execution_claimed is False
    And JobResult.dynamic_trace is a DynamicTraceReport with
      physical_execution_claimed False

  Scenario: post-measure reuse in match arms now fails closed end-to-end (was silently accepted before LISS-0386)
    Given the same mid-circuit dynamic program as the former LISS-0383
      success fixture
      """
      Controller<Bit> bit = measure q
      match bit {
          0 => { apply(X, q) }
          1 => { apply(Z, q) }
      }
      """
    And settings.dynamic_fake_profile is SIM0_EXACT
    And settings.dynamic_supplied_outcomes supplies each mid-circuit token
    When the Job is submitted through the Fake-gated Host path
    Then DynamicExecResult.status is rejected
    And diagnostics include DYN_CAPABILITY_REUSE
    And DynamicExecResult.physical_execution_claimed is False
    And no JobResult.dynamic_trace claims physical execution
```

## AI planning record (size S)

- Status: Green/Refactor complete; awaiting Completion approval
- Authoring environment: Claude Code, 2026-08-09
- Size: `S` — one call-site wiring change in `dynamic_fake_wire.py`, one
  fixture/Gherkin amendment on LISS-0383's spec section, one repurposed test
  + one new regression test.
- Route: AT-TDD, Plan approved 2026-08-09 (Adjudicator "続けて").
- Confidence: high — inference function and gap are both already shipped and
  confirmed by direct code read; verified empirically before Plan
  (`infer_dynamic_capability_demand` on the reuse fixture returns
  `needs_reuse=True`, on the measure-only fixture returns `False`).
- Revision links: supersedes the "Host inferred-reuse auto-attach" open item
  noted in LISS-0383 metadata and `open-work-register.md`.

## Exit criteria

- [x] Plan approval (2026-08-09, Adjudicator "続けて" after 案C resolution).
- [x] Phase 1 Red (2026-08-09): `tests/test_liss_0383_dynamic_fake_executor_wire_red.py`
      — **1 failed / 3 passed**. New
      `test_host_auto_attach_reuse_demand_fails_closed_end_to_end` failed
      (`'succeeded' == 'failed'`, hardcoded `needs_reuse=False` still in
      place); amended accept-scenario test and the two pre-existing tests
      passed unchanged.
- [x] Phase 2 Green (2026-08-09): `build_dynamic_exec_request`
      (`compiler/staqex/dynamic_fake_wire.py`) replaces the hardcoded
      `DynamicCapabilityDemand(...)` literal with
      `infer_dynamic_capability_demand(unit)`; no other behavior change.
      All 7 tests across the two Fake/demand-inference files pass.
- [x] Phase 3 Refactor: none needed — Green diff is minimal (one import swap,
      one field value swap); no design smell introduced.
- [x] Spec (`staqex-dynamic-qpu-lane.md`) and LISS-0383 addendum synced
      (2026-08-09): new "Host auto-attach inferred capability demand
      (LISS-0386)" section added; LISS-0383's accept-scenario `Given`
      amended in place.
- [x] Full regression sweep re-run: **1373 passed** (2026-08-09), up from the
      1372-passed baseline at PR #483 by exactly the one new test.
- [x] Completion approval (2026-08-09); PR [#484](https://github.com/nn0cl/staqex/pull/484).
