# LISS-0388: Repurpose reuse reject-on-demand for simulator-class profiles

## Metadata

- Local issue ID: LISS-0388
- Status/phase: **complete** (2026-08-09) — Adjudicator Completion approval;
  PR [#488](https://github.com/nn0cl/staqex/pull/488)
- Type: Feature Path (Kernel/Fake — capability law repurposing; no new
  surface, no profile addition)
- Priority: P1
- Initial planning size: `M`
- Owner / agent: Claude Code
- Program: [ADR 0200](../architecture/adr/0200-dynamic-lane-real-kernel-execution.md)
  Follow-up #2 (Decision 3's named consequence)
- Parent: ADR 0200 (Accepted); depends on
  [LISS-0387](LISS-0387-dynamic-real-mid-circuit-measure.md) (**complete**,
  PR [#486](https://github.com/nn0cl/staqex/pull/486)) shipping real
  mid-circuit execution first
- Depends on: LISS-0385/0386 (both **complete**) — this Issue amends their
  reject-on-demand tests, not their inference logic
- Related: `compiler/staqex/dynamic_qpu.py`
  (`_FEEDBACK_ONLY_PROFILES` / `_capability_diagnostics`);
  `compiler/staqex/dynamic_capability.py` (`reuse_demand_diagnostics`)
- Blocks: none
- Branch: `feature/liss-0388-dynamic-reuse-capability-followup2`
- GitHub Issue / PR: [#488](https://github.com/nn0cl/staqex/pull/488)

## Intent

ADR 0200 Decision 3 named this consequence explicitly at Accept time: once
a profile genuinely simulates state (LISS-0387 shipped), rejecting
`needs_reuse` on that same profile has no physical justification anymore.
`SIM0_EXACT` and `CH1_DIGITAL_RESEARCH` are both simulator-class Fake
profiles (no live hardware, no physical qubit-recycling constraint) — the
Fake executor should stop rejecting reuse-demanding programs on them.
`needs_reset` is unaffected (ADR 0199 Decision 3 / ADR 0200 Decision 4
boundary: reset execution is still unimplemented and stays out of scope).

## Explicitly out of scope

- Reset (`needs_reset`) — still rejects on every profile, unchanged.
- Any new profile, live QPU, or hardware-constrained profile tier (the
  "non-simulator" case the reject-on-demand law is repurposed *toward*
  does not exist in code yet — nothing to wire it to today).
- The separate Host-bookkeeping-vs-real-physics gap LISS-0387 disclosed
  (a Host-accepted but physically-inconsistent supplied outcome still
  vacuums the run while `JobResult.status` stays `"succeeded"`) — that is
  a distinct concern (outcome *consistency*, not reuse *capability*) and
  is **not** resolved by this Issue. Left as a named future gap.
- `needs_latency` — untouched (ADR 0193 Follow-up #2, still deferred).
- Renaming `_FEEDBACK_ONLY_PROFILES` — the name is now slightly imprecise
  (these profiles support reuse after this Issue) but renaming is a
  larger, unrelated blast-radius change; a clarifying comment is added
  instead (Decision 3 below).

## Plan-locked decisions (Adjudicator direction 2026-08-09, "続けて")

1. **`dynamic_qpu.py::_capability_diagnostics`:** `demand.needs_reuse` no
   longer appends `DYN_CAPABILITY_REUSE` when `request.profile_id` is in
   `_FEEDBACK_ONLY_PROFILES` (i.e., for every profile that exists in code
   today). `demand.needs_reset` keeps rejecting unconditionally.
   `DYN_PROFILE_UNKNOWN` (unknown profile) is unaffected.
2. **Compile-time advisory wording:**
   `dynamic_capability.py::reuse_demand_diagnostics`'s `DYN_CAPABILITY_REUSE`
   message is reworded from "unsupported on P0 feedback-only profiles" (no
   longer universally true) to a neutral notice that reuse is demanded,
   without asserting rejection. The diagnostic is not a `HARD_CODES` entry
   today and stays advisory (does not block compilation or execution
   either before or after this change).
3. **Naming clarified, not changed:** a comment is added at
   `_FEEDBACK_ONLY_PROFILES`'s definition noting that "feedback-only" no
   longer means "no reuse" as of ADR 0200 / this Issue — it still means
   "no reset, no live hardware, no latency guarantees."
4. **Amend named-consequence tests:**
   `test_fake_gate_present_but_reuse_demanded_still_fails_closed` (LISS-0383)
   and `test_host_auto_attach_reuse_demand_fails_closed_end_to_end`
   (LISS-0386) flip from rejected to accepted for `SIM0_EXACT`.
   `test_post_measure_apply_on_measured_wire_demands_reuse` (LISS-0385)
   keeps its inference assertions (`needs_reuse is True`) and drops the
   rejection-coupled assertion, since that Issue's own job (inference) is
   unaffected — only the *consequence* of the demand changed.
5. **New regression guard:** `needs_reset=True` on `SIM0_EXACT` still
   rejects with `DYN_CAPABILITY_RESET` — added explicitly so this Issue
   cannot be mistaken for "capability law removed" rather than "reuse
   specifically repurposed."
6. **End-to-end closure:** a `submit_source`-level test confirms the
   previously-rejected reuse fixture now succeeds **and** that the real
   evaluator (LISS-0387) actually applied the arm's gate — tying the
   capability-law change to the real execution it is now honestly
   describing, not just flipping a bookkeeping flag in isolation.

## Acceptance reference

To be added to
[`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md), amending
the existing "Fake gate present but reset/reuse demanded still fails closed"
scenario (LISS-0383 section) to split reset (still fails closed) from reuse
(now succeeds on simulator-class profiles), plus a new scenario in this
Issue's own section.

### Draft Gherkin (Plan review only, not yet normative)

```gherkin
Feature: Reuse capability law is repurposed for simulator-class profiles

  Scenario: reuse-demanding program now succeeds on a simulator-class profile
    Given a Fake-gated request whose capability_demand.needs_reuse is true
    And profile_id is SIM0_EXACT (or CH1_DIGITAL_RESEARCH)
    When FakeDynamicExecutor / verify_dynamic_request runs
    Then the result is accepted
    And physical_execution_claimed remains False

  Scenario: reset demand still fails closed (unchanged)
    Given a Fake-gated request whose capability_demand.needs_reset is true
    And profile_id is SIM0_EXACT
    When FakeDynamicExecutor / verify_dynamic_request runs
    Then the result is rejected
    And diagnostics include DYN_CAPABILITY_RESET

  Scenario: end-to-end, the real evaluator applies the arm's gate
    Given the LISS-0387 match-arm-reuse fixture
    And settings.dynamic_fake_profile is SIM0_EXACT
    And settings.dynamic_supplied_outcomes supplies a consistent outcome
    When the Job is submitted through the Fake-gated Host path
    Then DynamicExecResult.status is accepted
    And the real post-measure joint reflects the arm's apply(X, q)
      (verified at the Evaluator/Joint boundary, per LISS-0387 Decision 7)
```

## AI planning record (size M)

- Status: Plan drafted; awaiting Adjudicator Plan approval
- Authoring environment: Claude Code, 2026-08-09
- Size: `M` — one capability-check condition change, one diagnostic message
  reword, three amended tests, two new tests (reset regression guard +
  end-to-end closure).
- Route: AT-TDD after Plan approval.
- Confidence: high — this is the Adjudicator-anticipated, explicitly named
  consequence of ADR 0200 Decision 3; no new design decision expected.
- Revision links: closes the "amend LISS-0385/0386 simulator-profile tests"
  item named in ADR 0200's Follow-up work and in LISS-0387's Refactor note.

## Exit criteria

- [x] Plan approval (2026-08-09).
- [x] Phase 1 Red (2026-08-09): amended tests in
      `test_liss_0383_dynamic_fake_executor_wire_red.py` failed for the
      stated reason (**2 failed / 6 passed**) — the two flipped tests
      failed against unmodified `dynamic_qpu.py` (`'rejected' ==
      'accepted'`, `'failed' == 'succeeded'`); the new reset-regression
      test and all unrelated tests passed unchanged, confirming
      LISS-0385's inference test needed no amendment (it checks the
      compile-time advisory diagnostic, not the runtime accept/reject
      path this Issue changes).
- [x] Phase 2 Green (2026-08-09): `dynamic_qpu.py::_capability_diagnostics`
      no longer rejects `needs_reuse` (reset unaffected);
      `dynamic_capability.py`'s advisory message reworded. All 12 targeted
      tests pass.
- [x] Phase 3 Refactor: reviewed diff (dynamic_qpu.py +7/-6,
      dynamic_capability.py +3/-1) — minimal, no further changes needed.
- [x] Full regression re-run surfaced one additional pre-existing call
      site not caught during Plan investigation:
      `tests/test_dynamic_qpu_integrated_red.py::test_ch1_profile_rejects_unsupported_reset_reuse_latency`
      (LISS-0077-era, predates this lineage) asserted reuse+reset+latency
      rejected together for `CH1_DIGITAL_RESEARCH`. Amended in the same
      spirit as Decision 4 (same already-approved policy, wider blast
      radius than catalogued at Plan time) — split into
      `test_ch1_profile_rejects_unsupported_reset_latency` (reuse
      excluded) and a new `test_ch1_profile_accepts_reuse_alone`. Reported
      here rather than treated as a silent scope change.
- [x] Spec (`staqex-dynamic-qpu-lane.md`) synced: LISS-0383 section's
      fail-closed scenario split into an "accepts" (reuse) and unchanged
      "fails closed" (reset) scenario; status table updated.
- [x] Full regression sweep re-run: **1379 passed** (2026-08-09), up from
      1377 by the 2 net-new tests (reset-regression guard +
      CH1-reuse-accept guard; the flipped/renamed tests are 1:1
      replacements).
- [x] Completion approval (2026-08-09); PR [#488](https://github.com/nn0cl/staqex/pull/488).
