# Staqex Dynamic QPU lane specification

| Field | Value |
|---|---|
| Status | **Accepted rejection/capability boundary; timing + mid-circuit + JobResult Host channel + Fake-exec wire + reuse/reset demand inference + Host auto-attach + real mid-circuit execution + reuse capability repurposing + outcome confirmation + reset keyword all complete; live/provider execution still gated** |
| Decision | [ADR 0071](../architecture/decision-themes/dec-0006-host-qpu-and-external-ports.md); timing [ADR 0193](../architecture/adr/0193-dynamic-qpu-timing-region-intent.md); mid-circuit [ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md); JobResult [ADR 0198](../architecture/adr/0198-dynamic-jobresult-composition.md) (**Accepted**; Amendment **Accepted**); reuse/reset [ADR 0199](../architecture/adr/0199-dynamic-qubit-reuse-reset.md) (**Accepted**; Amendment **Accepted** — `reset` keyword); real execution [ADR 0200](../architecture/adr/0200-dynamic-lane-real-kernel-execution.md) (**Accepted**) |
| Issue | [LISS-0028](../issues/LISS-0028-dynamic-qpu-lane.md); [LISS-0381](../issues/LISS-0381-dynamic-qpu-timing-region-intent.md); [LISS-0382](../issues/LISS-0382-dynamic-mid-circuit-feed-forward.md); [LISS-0384](../issues/LISS-0384-dynamic-jobresult-trace.md); [LISS-0385](../issues/LISS-0385-dynamic-reuse-reset-demand.md); [LISS-0383](../issues/LISS-0383-dynamic-fake-executor-wire.md); [LISS-0386](../issues/LISS-0386-dynamic-host-auto-attach-demand.md); [LISS-0387](../issues/LISS-0387-dynamic-real-mid-circuit-measure.md); [LISS-0388](../issues/LISS-0388-dynamic-reuse-capability-followup2.md); [LISS-0389](../issues/LISS-0389-dynamic-outcome-confirmation.md); [LISS-0390](../issues/LISS-0390-dynamic-reset-keyword.md) |

This lane is intentionally separate from the Static Hilbert Kernel.

Required future contracts:

- explicit mid-circuit measurement semantics — **shipped (IR+diagnostics):**
  meaning Accepted in ADR 0197; Kernel complete (LISS-0382);
- classical feed-forward/control values — **shipped (IR+diagnostics):**
  `Controller<T>` + finite `match` + one-merge Accepted in ADR 0197;
  Kernel complete (LISS-0382);
- timing and qubit-reuse semantics — **partial:** timing *intent* shipped
  (ADR 0193 / LISS-0381); concrete per-backend timing meaning and qubit
  reuse remain open;
- target capability profile and explicit unsupported-feature errors
  (shipped for the rejection boundary);
- simulator/QPU equivalence at the observable JobResult boundary.

The dynamic lane remains non-executable until a Feature Issue explicitly
schedules otherwise (ADR 0197 Decision 7). Timing intent and mid-circuit
*meaning* alone do not authorize execution.

## Acceptance scenarios — timing intent (ADR 0193, LISS-0381)

Normative for Feature Path Phase 1–3 on LISS-0381. Assertions must match
these `Then` clauses exactly. Physicist-first: timing remains a named
intent on the lane region (`within <name>`), never backend `dt` literals
scattered between operations, and `dynamic qpu` stays a statement.

Composition stability (vision §2.2): expanding or combining well-formed
blackboard fragments must keep the timing intent attached and inspectable;
`within` must not steal ordinary identifiers outside the `dynamic qpu`
clause (contextual / soft keyword only in that position).

```gherkin
Feature: Dynamic QPU timing intent as a Region attribute

  Scenario: optional within clause is accepted on dynamic qpu
    Given source containing
      """
      dynamic qpu within coherent_window {
        apply H onto q0
      }
      """
    When the program is compiled
    Then parsing succeeds with DynamicQpuStmt.timing_intent == "coherent_window"
    And DynamicQpuStmt remains a statement (not an expression)
    And diagnostics include DYNAMIC_CAPABILITY_REQUIRED_ERROR
    And diagnostics include DYNAMIC_UNSUPPORTED_FEATURE_ERROR

  Scenario: dynamic qpu without within remains valid and unchanged
    Given source containing `dynamic qpu { … }` with no within clause
    When the program is compiled
    Then DynamicQpuStmt.timing_intent is None
    And no TimingRegion is present in Quantum Semantic IR
    And diagnostics include DYNAMIC_CAPABILITY_REQUIRED_ERROR
    And diagnostics include DYNAMIC_UNSUPPORTED_FEATURE_ERROR

  Scenario: TimingRegion carries the source-derived timing intent
    Given source containing `dynamic qpu within coherent_window { … }`
    When the program is compiled
    Then Quantum Semantic IR contains exactly one TimingRegion
    And that region's timing_intent equals "coherent_window"
    And the intent is not a hardcoded placeholder unrelated to the source

  Scenario: different timing names produce distinguishable TimingRegions
    Given one program with `within coherent_window`
    And another with `within idle_window`
    When both are compiled
    Then each TimingRegion.timing_intent equals its own source name
    And the two timing_intent values differ

  Scenario: malformed within clause fails closed
    Given source containing `dynamic qpu within` with no following identifier
      before `{`
    When the program is compiled
    Then diagnostics include DYNAMIC_TIMING_INTENT_MALFORMED
    And the clause is not silently accepted
    And the compiler does not crash

  Scenario: timing intent does not make the lane executable
    Given any well-formed `dynamic qpu` statement with or without within
    When the program is compiled
    Then DYNAMIC_CAPABILITY_REQUIRED_ERROR is still emitted
    And DYNAMIC_UNSUPPORTED_FEATURE_ERROR is still emitted
    And no Host/QPU execution path is taken for the dynamic block

  Scenario: evolve under/for inside within keeps timing intent (composition)
    Given source containing
      """
      dynamic qpu within coherent_window {
        state psi = |0>
        Operator H = X
        state psi = evolve psi under H for 1.0.s
        measure psi
      }
      """
    When the program is compiled
    Then DynamicQpuStmt.timing_intent == "coherent_window"
    And Quantum Semantic IR contains a TimingRegion with timing_intent
      "coherent_window"
    And diagnostics include DYNAMIC_CAPABILITY_REQUIRED_ERROR
    And diagnostics include DYNAMIC_UNSUPPORTED_FEATURE_ERROR
    And the enclosing within clause is not dropped because the body grew

  Scenario: multiple within blocks in one program yield multiple TimingRegions
    Given one main containing both
      `dynamic qpu within coherent_window { … }` and
      `dynamic qpu within idle_window { … }`
    When the program is compiled
    Then Quantum Semantic IR contains exactly two TimingRegions
    And their timing_intent values are {"coherent_window", "idle_window"}
    And both dynamic statements still emit the two dynamic rejection diagnostics

  Scenario: non-identifier timing intent fails closed
    Given source containing `dynamic qpu within 1 { … }`
      or `dynamic qpu within foo(bar) { … }`
    When the program is compiled
    Then diagnostics include DYNAMIC_TIMING_INTENT_MALFORMED
    And the clause is not silently accepted as a bare dynamic qpu block

  Scenario: within remains usable as an ordinary identifier outside the clause
    Given source that binds and measures a name `within` with no dynamic qpu
      timing clause
    When the program is compiled
    Then compilation does not emit DYNAMIC_TIMING_INTENT_MALFORMED
    And the program is not rejected solely because `within` is an identifier
    And (vision §2.2) introducing timing intent must not globally reserve
      `within` as a hard keyword

  Scenario: adjacent Static evolve and dynamic within do not corrupt each other
    Given one main with Static `evolve … under H for t` followed by
      `dynamic qpu within coherent_window { … }`
    When the program is compiled
    Then the dynamic statement's timing_intent == "coherent_window"
    And Quantum Semantic IR contains a TimingRegion with that intent
    And diagnostics include DYNAMIC_CAPABILITY_REQUIRED_ERROR
    And diagnostics include DYNAMIC_UNSUPPORTED_FEATURE_ERROR
    And the Static evolve form is not rewritten or dropped to accommodate
      the within clause
```

## Acceptance scenarios — mid-circuit measure / feed-forward (ADR 0197, LISS-0382)

Normative for Feature Path Phase 1–3 on LISS-0382. Plan-locked surface
sugar (Adjudicator Plan approval 2026-08-09):

- Mid-circuit collapse: Type-First
  `Controller<Bit> bit = measure q` **inside** `dynamic qpu { … }`
  (lane-local `measure` as expression RHS; not `observe`; not method-chain).
- Feed-forward: contextual soft keyword
  `match bit { <finite arms> }` immediately associated with that controller
  (exact arm body forms may use existing `apply(...)` statements).
- Default Plan: QSem witnesses + diagnostics only; today's
  `DYNAMIC_CAPABILITY_REQUIRED_ERROR` /
  `DYNAMIC_UNSUPPORTED_FEATURE_ERROR` remain. No Fake executor wire in
  this Issue unless Plan is amended.

Physicist-first / vision §2.2: expanding the body under `dynamic qpu` or
adding `within` must not drop mid-circuit markers; Static NLTS outside the
lane is unchanged.

```gherkin
Feature: Dynamic-lane mid-circuit measure and finite feed-forward

  Scenario: Controller bind from measure inside dynamic is mid-circuit
    Given source containing
      """
      dynamic qpu {
        state q = |0>
        Controller<Bit> bit = measure q
      }
      """
      plus a Static terminal measure after the block as required by main
    When the program is compiled
    Then parsing retains a mid-circuit measure bind (not EARLY_COLLAPSE_ERROR
      for that measure)
    And Quantum Semantic IR contains exactly one DynamicMeasurementRegion
    And diagnostics include DYNAMIC_CAPABILITY_REQUIRED_ERROR
    And diagnostics include DYNAMIC_UNSUPPORTED_FEATURE_ERROR

  Scenario: the same Controller = measure form outside dynamic fails as early collapse
    Given source where `Controller<Bit> bit = measure q` appears in Static
      main (no dynamic qpu)
    When the program is compiled
    Then diagnostics include EARLY_COLLAPSE_ERROR
    And no DynamicMeasurementRegion is present

  Scenario: observe remains retired
    Given source containing `observe x` in main
    When the program is compiled
    Then diagnostics include RETIRED_KEYWORD
    And no DynamicMeasurementRegion is introduced by observe

  Scenario: match after mid-circuit measure yields DynamicControlRegion
    Given source containing inside dynamic qpu
      """
      state q = |0>
      Controller<Bit> bit = measure q
      match bit {
        0 => { apply(X, q) }
        1 => { apply(Z, q) }
      }
      """
    When the program is compiled
    Then Quantum Semantic IR contains one DynamicMeasurementRegion
    And Quantum Semantic IR contains one DynamicControlRegion
    And the control region is paired to the measurement region
    And diagnostics include DYNAMIC_CAPABILITY_REQUIRED_ERROR
    And diagnostics include DYNAMIC_UNSUPPORTED_FEATURE_ERROR

  Scenario: mid-circuit plus within keeps both TimingRegion and DynamicMeasurementRegion
    Given source containing
      `dynamic qpu within coherent_window { … Controller<Bit> bit = measure q … }`
    When the program is compiled
    Then TimingRegion.timing_intent == "coherent_window"
    And exactly one DynamicMeasurementRegion is present
    And dynamic capability rejection diagnostics remain

  Scenario: Static terminal measure is unchanged
    Given a Static-only program with terminal `measure observed`
    When the program is compiled
    Then no DynamicMeasurementRegion is present
    And no DynamicControlRegion is present
    And the program is not rejected solely for DYNAMIC_UNSUPPORTED_FEATURE_ERROR
```

## Acceptance scenarios — Fake-exec wire (ADR 0197 Decision 7, LISS-0383)

Normative for Feature Path Phase 1–3 on LISS-0383. Plan-locked (2026-08-09).
**Amended 2026-08-09 under LISS-0386 (Adjudicator 案C):** the "accepts"
scenario's fixture no longer reuses the measured wire in its `match` arms —
see [LISS-0386](#acceptance-scenarios--host-auto-attach-inferred-capability-demand-liss-0386)
below for the repurposed reuse-demand regression.
**Amended again 2026-08-09 under LISS-0388 (ADR 0200 Decision 3):** reuse
demanded on a simulator-class profile (SIM0_EXACT / CH1_DIGITAL_RESEARCH)
now succeeds instead of failing closed, since a real local simulator
(LISS-0387) has no physical constraint against it. Reset is unaffected and
still fails closed on every profile.

- Fake gate: Host `settings["dynamic_fake_profile"]` ∈
  `{SIM0_EXACT, CH1_DIGITAL_RESEARCH}` (absent / unknown → fail closed;
  compile-only path without the gate keeps today's
  `DYNAMIC_CAPABILITY_REQUIRED_ERROR` /
  `DYNAMIC_UNSUPPORTED_FEATURE_ERROR`).
- Supplied outcomes: `settings["dynamic_supplied_outcomes"]` maps token id
  → classical tag (LISS-0077 honesty; not hardware sampling).
- Same Issue projects accepted Fake results into
  `JobResult.dynamic_trace` via `project_dynamic_trace` (LISS-0384 complete).
- `physical_execution_claimed` remains `False`.
- P0 profiles still reject `needs_reset` / `needs_reuse` / `needs_latency`.

```gherkin
Feature: Fake-gated dynamic execution under supplied outcomes

  Scenario: without Fake gate, compile still rejects dynamic lane
    Given a mid-circuit dynamic program as in LISS-0382
    And Host settings omit dynamic_fake_profile
    When the program is compiled (or submitted without the Fake gate)
    Then diagnostics include DYNAMIC_CAPABILITY_REQUIRED_ERROR
    And diagnostics include DYNAMIC_UNSUPPORTED_FEATURE_ERROR
    And no JobResult.dynamic_trace is produced from Fake execution

  Scenario: with Fake gate and supplied outcomes, Fake accepts without physical claim
    Given a mid-circuit dynamic program with match arms that do not reuse
      the measured wire (measure-only arms; LISS-0386 amendment)
    And settings.dynamic_fake_profile is SIM0_EXACT
    And settings.dynamic_supplied_outcomes supplies each mid-circuit token
    When the Job is submitted through the Fake-gated Host path
    Then DynamicExecResult.status is accepted (or equivalent Host success)
    And DynamicExecResult.physical_execution_claimed is False
    And JobResult.dynamic_trace is a DynamicTraceReport with
      physical_execution_claimed False
    And controller bindings appear only on dynamic_trace, not measurements

  Scenario: Fake gate present and reuse demanded now succeeds (LISS-0388 amendment)
    Given a Fake-gated request whose capability_demand.needs_reuse is true
      on a simulator-class profile (SIM0_EXACT or CH1_DIGITAL_RESEARCH)
    When FakeDynamicExecutor / verify_dynamic_request runs
    Then the result is accepted
    And physical_execution_claimed remains False

  Scenario: Fake gate present but reset demanded still fails closed (unchanged)
    Given a Fake-gated request whose capability_demand.needs_reset is true
      on a P0 feedback-only profile
    When FakeDynamicExecutor / verify_dynamic_request runs
    Then the result is rejected
    And diagnostics include DYN_CAPABILITY_RESET
    And physical_execution_claimed remains False
```

## Acceptance scenarios — real mid-circuit execution (ADR 0200, LISS-0387)

Normative for Feature Path Phase 1–3 on LISS-0387. Plan-locked (Adjudicator
root-cause direction, 2026-08-09): the evaluator's unconditional
`DynamicQpuStmt` skip is replaced with real execution. Mid-circuit
`Controller<T> = measure wire` performs a genuine Lüders projection +
renormalize (`Joint.project_coord`, the same primitive `project(psi, k)`
already uses) instead of a bookkeeping label; the matching `match` arm then
executes for real against the collapsed joint. Supplied-outcome only (no
RNG sampling in this Issue) — routed via the existing `HostInputPort` (ADR
0194). `needs_reset` / reset execution, RNG-sampled outcomes, and any
`JobResult`/`dynamic_trace` DTO change stay out of scope. The Host-level
`FakeDynamicExecutor` accept/reject bookkeeping path (LISS-0383/0385/0386)
is unchanged by this Issue — it still independently decides
`DynamicExecResult`/`dynamic_trace`; this Issue only makes the **evaluator**
genuinely execute the block once Host has allowed the run.

**Known residual gap (disclosed, not fixed by this Issue):** since the Host
bookkeeping layer and the evaluator's real execution are independent, a
program whose Host-supplied outcome is inconsistent with the real prepared
state (e.g. supplying `"1"` for a wire prepared as `|0>`) is still
Host-accepted (bookkeeping never checks amplitudes) while the real
evaluator legitimately vacuums the run (Born-rule zero-probability
outcome). `JobResult.status` stays `"succeeded"` either way (a vacuum
Static terminal measurement is not a Kernel error). Unifying Host
bookkeeping with real physics is a candidate for the ADR 0200 Follow-up #2
Issue, not resolved here.

```gherkin
Feature: Dynamic-lane mid-circuit measure genuinely collapses and continues

  Scenario: measure-only program, consistent outcome runs to completion
    Given a dynamic qpu block with `state q = |0>` then
      `Controller<Bit> bit = measure q`
    And a Host-supplied outcome of "0" for controller `bit` (consistent
      with the prepared |0>)
    When the Evaluator runs the compiled unit
    Then the Static terminal measure after the block still produces a
      real (non-vacuum) sample

  Scenario: measure-only program, inconsistent outcome vacuums the run
    Given the same program
    And a Host-supplied outcome of "1" for controller `bit` (zero
      probability against the prepared |0>)
    When the Evaluator runs the compiled unit
    Then the run vacuums (Static terminal measure is vacuum=True) --
      evidencing a real project_coord collapse, not an accepted label
    And no LINEAR_IMPLICIT_DISCARD diagnostic is emitted for `q`

  Scenario: post-measure reuse inside a match arm actually evolves state
    Given `match bit { 0 => { apply(X, q) } }` with a consistent outcome
    When the matching arm executes
    Then apply(X, q) runs against the real post-measure joint via the
      normal Call-statement dispatch (verified at the Evaluator/Joint
      boundary directly, since block-end trace-out removes q from the
      publicly observable JobResult)

  Scenario: Static Kernel programs outside dynamic qpu are unaffected
    Given a Static-only program with a bare `measure` statement
    When it is compiled and evaluated
    Then behavior is byte-for-byte identical to before this Issue
```

## Acceptance scenarios — physical outcome confirmation (ADR 0198 Amendment, LISS-0389)

Normative for Feature Path Phase 1–3 on LISS-0389. Plan-locked (Adjudicator,
ADR 0198 Amendment, 2026-08-09): `DynamicTraceReport` gains an additive
`physical_outcome_confirmed: bool` field (default `True`), reconciled from
the real evaluator's (LISS-0387) mid-circuit collapse outcome after
`Evaluator.run_unit` completes. `JobResult.status` is unaffected — a vacuum
dynamic run still reports `"succeeded"` (matching Static Kernel precedent
for a zero-probability measurement branch; not a defect).

```gherkin
Feature: dynamic_trace confirms whether the reported outcome was physically real

  Scenario: consistent supplied outcome is confirmed
    Given the LISS-0383 measure-only fixture with a Host-supplied outcome
      consistent with the prepared state
    When the Job is submitted through the Fake-gated Host path
    Then JobResult.dynamic_trace.physical_outcome_confirmed is True

  Scenario: inconsistent supplied outcome is not confirmed
    Given the same fixture with a Host-supplied outcome that is physically
      impossible against the prepared state (the run vacuums)
    When the Job is submitted through the Fake-gated Host path
    Then JobResult.status is still "succeeded" (unchanged; not a defect)
    And JobResult.dynamic_trace.physical_outcome_confirmed is False
    And dynamic_trace.controller_bindings still shows the supplied label
      (audit trail), now clearly marked as not confirmed
```

## Acceptance scenarios — reset keyword (ADR 0199 Amendment, LISS-0390)

Normative for Feature Path Phase 1–3 on LISS-0390. Plan-locked (Adjudicator,
ADR 0199 Amendment, 2026-08-10): a new contextual keyword `reset`, lane-local
to `dynamic qpu` (same precedent as `match`). `reset wire` performs
`Joint.trace_out(wire)` then re-prepares `wire` as `|0⟩` — reusing the two
already-shipped primitives LISS-0387 and ADR 0173 established, no new Joint
math. Deliberately distinct from the Static Kernel's same-name
`state x = |0>` idiom (LISS-0114 F verification) — the two mean different
physics and are not unified. `needs_reset` is now inferred from source and
no longer rejected on simulator-class profiles, symmetric to LISS-0388's
reuse treatment.

```gherkin
Feature: Dynamic-lane reset genuinely reinitializes a measured wire

  Scenario: reset outside dynamic qpu fails closed
    Given a Static-only program with a bare `reset q` statement
    When it is compiled and evaluated
    Then the run fails (mirrors `match`'s existing, unchanged fail-closed
      behavior outside the dynamic lane — no new dedicated diagnostic was
      needed)

  Scenario: reset inside dynamic qpu genuinely reinitializes the wire
    Given a dynamic qpu block that flips a wire away from |0> (e.g.
      apply(X, q)) then resets it
    When the Evaluator runs the block's statements
    Then the wire's joint coordinate is a definite 0 again (verified at
      the Evaluator/Joint boundary, since block-end trace-out removes it
      from the public JobResult, per LISS-0387 Decision 7's precedent)

  Scenario: reset wire is usable again after reset
    Given a dynamic qpu block that measures a wire, flips it, resets it,
      then measures it again with a Host-supplied outcome consistent with
      the reset |0> state
    When the Job is submitted through the Fake-gated Host path
    Then JobResult.dynamic_trace.physical_outcome_confirmed is True
      (LISS-0389) -- a False result would mean reset did not genuinely
      reinitialize the wire

  Scenario: needs_reset is inferred and accepted on simulator-class profiles
    Given a dynamic qpu block containing a reset statement
    When demand inference runs
    Then needs_reset is true
    And FakeDynamicExecutor / verify_dynamic_request accepts the request
      on SIM0_EXACT / CH1_DIGITAL_RESEARCH

  Scenario: resetting an unknown wire fails closed
    Given a dynamic qpu block with `reset ghost` where `ghost` was never
      introduced in the same block
    When it is compiled
    Then diagnostics include DYN_RESET_UNKNOWN_WIRE
```

## Acceptance scenarios — Host auto-attach inferred capability demand (LISS-0386)

Normative for Feature Path Phase 1–3 on LISS-0386. Plan-locked (Adjudicator
案C, 2026-08-09): `build_dynamic_exec_request`
(`compiler/staqex/dynamic_fake_wire.py`) auto-attaches
`infer_dynamic_capability_demand` (LISS-0385) instead of hardcoding
`needs_reuse=False`. `needs_reset` stays never-inferred per LISS-0385. This
closes the honesty gap LISS-0383 recorded as a soft-depend: a program that
demands an unsupported capability must fail closed through the Fake-gated
Host path itself, not only when a `DynamicExecRequest` is hand-built with
the demand already set.

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

  Scenario: post-measure reuse in match arms now fails closed end-to-end
    Given a mid-circuit dynamic program
      """
      Controller<Bit> bit = measure q
      match bit {
          0 => { apply(X, q) }
          1 => { apply(Z, q) }
      }
      """
      (the former LISS-0383 "accepts" fixture, before this amendment)
    And settings.dynamic_fake_profile is SIM0_EXACT
    And settings.dynamic_supplied_outcomes supplies each mid-circuit token
    When the Job is submitted through the Fake-gated Host path
    Then DynamicExecResult.status is rejected
    And diagnostics include DYN_CAPABILITY_REUSE
    And DynamicExecResult.physical_execution_claimed is False
    And no JobResult.dynamic_trace claims physical execution
```

## Acceptance scenarios — reuse/reset demand inference (ADR 0199, LISS-0385)

Normative for Feature Path Phase 1–3 on LISS-0385. Plan-locked (2026-08-09):

- **No new `reset` keyword** (Option B declined).
- **`needs_reset`:** never auto-inferred from source in this Issue.
- **`needs_reuse`:** inferred when, inside `dynamic qpu`, a wire that was
  mid-circuit measured (`Controller<…> = measure <wire>`) is later used as
  a quantum target in the same block (e.g. `apply(..., wire)`), including
  inside `match` arms. Mid-circuit measure alone, or `match` alone without
  further ops on that wire, does **not** set `needs_reuse`.
- **`within` timing** does not set reuse/reset demands.
- Diagnostics: **both** compile-time (when demand inferred against P0 /
  unsupported profile path) **and** Fake-verify (`DYN_CAPABILITY_*`) when
  a Fake request carries the demand. Host must not silent-emulate.

```gherkin
Feature: Dynamic reuse/reset demand inference without reset keyword

  Scenario: mid-circuit measure alone does not demand reuse
    Given dynamic qpu body with only Controller bind from measure
      and no later ops on that wire
    When demand inference runs
    Then needs_reuse is false
    And needs_reset is false

  Scenario: post-measure apply on the measured wire demands reuse
    Given dynamic qpu body
      """
      Controller<Bit> bit = measure q
      match bit {
        0 => { apply(X, q) }
        1 => { apply(Z, q) }
      }
      """
    When demand inference runs
    Then needs_reuse is true
    And needs_reset is false
    And on P0 Fake / unsupported profile the demand fails closed with
      DYN_CAPABILITY_REUSE (or compile-time equivalent)
    And no Host silent re-init occurs

  Scenario: within timing does not imply reuse
    Given dynamic qpu within coherent_window with mid-circuit measure only
    When demand inference runs
    Then needs_reuse is false
    And TimingRegion remains independent
```
