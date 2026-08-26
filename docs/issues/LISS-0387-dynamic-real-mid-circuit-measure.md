# LISS-0387: Real dynamic-lane mid-circuit measurement and reuse

## Metadata

- Local issue ID: LISS-0387
- Status/phase: **complete** (2026-08-09) — Adjudicator Completion approval;
  PR [#486](https://github.com/nn0cl/staqex/pull/486)
- Type: Feature Path (Kernel — real evaluator execution of `dynamic qpu`
  blocks; root-cause fix, not bookkeeping)
- Priority: P1
- Initial planning size: `L`
- Owner / agent: Claude Code
- Program: [ADR 0200](../architecture/adr/0200-dynamic-lane-real-kernel-execution.md)
  Follow-up #1 (Decisions 1–2), folded together with the linear-use portion
  of Follow-up #3 (Decision 5) per Adjudicator direction 2026-08-09 — see
  "Scope note" below for why these two could not be cleanly separated.
- Parent: ADR 0200 (Accepted 2026-08-09)
- Depends on: ADR 0197 / LISS-0382 (mid-circuit IR, complete); ADR 0194
  (`HostInputPort` / `MappingHostInputAdapter`, shipped); existing
  `Joint.project_coord` / `Joint.trace_out` (shipped, unmodified)
- Related: LISS-0383/0385/0386 (bookkeeping layer this Issue does **not**
  remove or reject-behavior-change yet — see Explicitly out of scope)
- Blocks: ADR 0200 Follow-up #2 (amending LISS-0385/0386 simulator-profile
  reject-on-demand tests) — that Issue depends on this one shipping first
- Branch: `feature/liss-0387-dynamic-real-mid-circuit-measure`
- GitHub Issue / PR: [#486](https://github.com/nn0cl/staqex/pull/486)

## Intent

Replace the evaluator's unconditional `DynamicQpuStmt` skip
([evaluator.py:369-371](../../compiler/staqex/runtime/evaluator.py)) with
real execution: mid-circuit `Controller<T> c = measure wire` performs a
genuine Lüders projection + renormalize (reusing the already-shipped
`Joint.project_coord`, the same primitive `project(psi, k)` already uses in
the Static Kernel — no new Joint math), and the matching `match` arm's body
then executes for real against the collapsed joint using the existing
statement-dispatch loop. This is ADR 0200's root-cause fix, made concrete.

## Scope note: why Decision 5's linear-use portion is folded in here

Investigation during Plan (not assumed) found that `hir.py`'s linear-use
checker analyzes `DynamicQpuStmt.body` as a nested scope
([hir.py:439-449](../../compiler/staqex/hir.py)) but has no case recognizing
`StateBind` with a `MeasureExpr` right-hand side as consuming its target —
only a bare `Measure` **statement** counts
([hir.py:437](../../compiler/staqex/hir.py)). This is why
`LINEAR_IMPLICIT_DISCARD` fires today and why
`dynamic_fake_wire.py`'s `FAKE_BYPASS_HARD_CODES` has to hide it.

Naively marking `Controller<T> = measure wire` as "consumed" (Static-style
dead-after-measure) would fix that diagnostic but immediately break reuse:
a later `apply(X, wire)` in a `match` arm would then trip
`LINEAR_DUPLICATE_USE` ("reuses consumed root"), because Static linear
typing treats consumed as dead. ADR 0197 Decision 2 already settled that
dynamic-lane mid-circuit `measure` does **not** kill the wire — "a
post-measure Joint state that remains in-lane for further quantum ops."
Realizing Decisions 1–2 therefore requires the linear-use checker to gain a
**Dynamic-lane-specific state** for a mid-circuit-measured wire (alive, not
dead — distinct from both "introduced-unconsumed" and "consumed-dead"),
with disposal enforced at block end via the already-shipped `Joint.trace_out`
(no new Joint primitive). This is an implementation decision under ADR
0200's already-Accepted Decision 3 ("reuse is genuine continued evolution"),
not a new Architecture question — folding it into this Issue avoids leaving
Decision 1 half-working (fixing one linear diagnostic while immediately
enabling a different false one).

## Explicitly out of scope

- Amending LISS-0385/0386's `DynamicCapabilityDemand.needs_reuse`
  reject-on-demand tests/behavior for simulator profiles (ADR 0200 Decision
  3's named consequence) — separate Follow-up Issue, blocked on this one.
- RNG-sampled mid-circuit outcomes. This Issue supports **supplied-outcome**
  collapse only (via `HostInputPort`, ADR 0194), matching the existing
  LISS-0077 "supplied outcomes only" Fake honesty contract. Genuine
  RNG-sampled dynamic execution is a future Issue.
- `needs_reset` / reset execution (ADR 0199 Decision 3 unchanged; no new
  keyword).
- Any JobResult / `dynamic_trace` DTO shape change (ADR 0198 stays as
  accepted; this Issue does not add new observable fields).
- Live QPU provider; OpenQASM dynamic emission.
- Changing Host's existing `FakeDynamicExecutor` accept/reject bookkeeping
  path or `build_dynamic_exec_request` — this Issue only changes what the
  **evaluator** does once Host has already allowed the run through today's
  gate. The Host-level capability-reject flow for reuse-demanding programs
  is untouched here (still rejects, per LISS-0385/0386) — this Issue only
  makes the **currently-accepted** (non-reuse-demanding) programs execute
  for real. Reuse-demanding programs stay rejected at the Host layer until
  the Follow-up #2 Issue changes that policy.

## Plan-locked decisions (Adjudicator 2026-08-09)

1. **Real collapse:** mid-circuit `Controller<T> c = measure wire` inside
   `dynamic qpu` calls `joint.project_coord(wire, lambda v: v == outcome)`
   then renormalizes — identical operation to `project(psi, k)`
   ([evaluator.py:3996](../../compiler/staqex/runtime/evaluator.py) /
   [4011](../../compiler/staqex/runtime/evaluator.py)), not new Joint math.
2. **Outcome source:** the outcome comes from `HostInputPort`
   (`Evaluator.host_input`, ADR 0194's shipped channel) — Host routes
   `settings["dynamic_supplied_outcomes"]` into the same `host_input`
   mapping the S02 predicate feature already uses, keyed by controller
   name. No RNG sampling in this Issue (see Explicitly out of scope).
3. **Real arm execution:** after binding the `Controller` value and
   selecting the matching arm (same selection logic as today's
   `MatchPlan`), the arm's body statements execute via the **existing**
   statement-dispatch loop against the real post-measure joint — no
   separate "dynamic mini-evaluator."
4. **Linear-use exception:** `hir.py`'s linear-use checker recognizes
   `StateBind` with `MeasureExpr` RHS, **inside a `DynamicQpuStmt` nested
   scope only**, as producing a "dynamically measured, still alive" state
   for its target wire — distinct from Static "consumed-dead." Static
   `main` bodies outside `dynamic qpu` are unaffected (no change to
   `_check_measure`'s existing bare-`Measure`-statement handling).
5. **Block-end disposal:** any wire left in "dynamically measured, still
   alive" state when the nested block's own linear-use analysis ends is
   traced out automatically via the already-shipped `Joint.trace_out`
   (mirrors `_apply_measure_tracing_out`, ADR 0173 lineage) — no new
   discard diagnostic fires for this case; this replaces the need for
   `FAKE_BYPASS_HARD_CODES` to hide `LINEAR_IMPLICIT_DISCARD` for programs
   this Issue covers.
6. **Gating unchanged:** the evaluator does not add new Fake-profile
   gating logic — it is only ever reached with a `dynamic qpu` block
   present when Host's existing `_submit_allows_execution` has already
   allowed the run (unchanged from today).
7. **Verification boundary:** since `JobResult`/`dynamic_trace` gains no
   new field (Explicitly out of scope), Red/Green tests verify real
   execution at the `Evaluator`/`Joint` boundary directly (constructing a
   compiled unit, running `Evaluator.run_unit`, and inspecting the
   resulting joint/measure behavior), not solely through the public
   `submit_source` JobResult surface. `submit_source`-level tests still
   verify `physical_execution_claimed` stays `False` and existing
   Host-level behavior for out-of-scope (reuse-demanding) programs is
   unchanged.

## Acceptance reference

To be added to
[`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md) as a new
"Acceptance scenarios — real mid-circuit execution (LISS-0387)" section
once Plan is approved (drafted at Green, mirroring how LISS-0386 synced its
spec section after Green, per this session's established rhythm).

### Draft Gherkin (Plan review only, not yet normative)

```gherkin
Feature: Dynamic-lane mid-circuit measure genuinely collapses and continues

  Scenario: measure-only program produces a real collapse, not a label
    Given a dynamic qpu block with `state q = |0>` then
      `Controller<Bit> bit = measure q`
    And a Host-supplied outcome of "1" for controller `bit`
    When the Evaluator runs the compiled unit
    Then the resulting joint's marginal on `q` is definite at the supplied
      outcome (not a superposition), evidencing genuine project_coord
      collapse rather than a bookkeeping label
    And no LINEAR_IMPLICIT_DISCARD diagnostic is emitted for `q`

  Scenario: post-measure reuse inside a match arm actually evolves state
    Given the same program, with `match bit { 1 => { apply(X, q) } }`
    And a Host-supplied outcome of "1" for controller `bit`
    When the Evaluator runs the compiled unit
    Then `apply(X, q)` executes against the real post-measure joint (the
      arm's statements run, not just a label match)
    And no LINEAR_DUPLICATE_USE diagnostic is emitted for `q`
    And no LINEAR_IMPLICIT_DISCARD diagnostic is emitted for `q` (traced
      out automatically at block end)

  Scenario: Static Kernel programs outside dynamic qpu are unaffected
    Given a Static-only program with a bare `measure` statement
    When it is compiled and evaluated
    Then behavior is byte-for-byte identical to before this Issue
      (regression sweep, not a new assertion)

  Scenario: reuse-demanding programs still reject at the Host layer (unchanged)
    Given the LISS-0386 end-to-end regression fixture
      (post-measure reuse in match arms)
    And no Follow-up #2 policy change has landed
    When the Job is submitted through the Fake-gated Host path
    Then DynamicExecResult.status is still rejected with DYN_CAPABILITY_REUSE
      (Host-level bookkeeping untouched by this Issue)
```

## AI planning record (size L)

- Status: Plan drafted; awaiting Adjudicator Plan approval
- Authoring environment: Claude Code, 2026-08-09
- Size: `L` — evaluator dispatch change, `HostInputPort` wiring for
  dynamic outcomes, `hir.py` linear-use exception + block-end trace-out,
  new Evaluator/Joint-level tests.
- Route: AT-TDD after Plan approval.
- Confidence: medium-high — all underlying primitives (`project_coord`,
  `trace_out`, `RngPort`/`HostInputPort` pattern) are shipped and confirmed
  by direct code read; the linear-use exception is a genuinely new rule
  (not just wiring), so some Red-phase discovery risk remains there.
- Revision links: corrects this session's earlier "small hir.py fix"
  characterization — the linear-use change is Decision 3's realization
  mechanism, not a one-line patch.

## Exit criteria

- [x] Plan approval (2026-08-09).
- [x] Phase 1 Red (2026-08-09):
      `tests/test_liss_0387_dynamic_real_mid_circuit_measure_red.py` —
      both the collapse test and the HIR discard test failed for the
      stated reasons (block still skipped, `q` never entered the joint;
      `LINEAR_IMPLICIT_DISCARD` still present). Verification approach was
      revised once during Red: direct `q`-value inspection after
      `run_unit` doesn't work because block-end trace-out (Decision 5)
      removes `q` before the public result is inspectable — switched to a
      consistency-check strategy (supplying a physically-impossible
      outcome must vacuum the run) plus a direct Evaluator/Joint-boundary
      test for arm-body reuse, per Decision 7's verification-boundary
      allowance.
- [x] Phase 2 Green (2026-08-09): `evaluator.py` gained
      `_run_dynamic_qpu_block` / `_run_dynamic_arm_body` /
      `_resolve_dynamic_outcome` / `_collapse_dynamic_wire` (Decisions
      1–3, 6, reusing `Joint.project_coord` / `Joint.trace_out` unchanged);
      `hir.py` gained the Controller-measure linear-use exception
      (Decision 4); `host.py` routes `dynamic_supplied_outcomes` into
      `HostInputPort` under `dynamic:<controller>` keys (Decision 2). All
      4 new tests pass; full regression **1377 passed** (up from 1373 by
      exactly the 4 new tests) — confirmed LISS-0383/0385/0386 tests
      unaffected (Host-level bookkeeping path untouched, as scoped).
- [x] Phase 3 Refactor: reviewed diff (hir.py +21/-0, evaluator.py
      +126/-2, host.py +11/-2) — minimal, comments explain only
      non-obvious rationale; `_run_dynamic_arm_body` duplicates a small
      dispatch snippet from `_run_dynamic_qpu_block` (kept as two small
      blocks rather than a premature shared helper). No behavior change
      from Green.
- [x] Spec (`staqex-dynamic-qpu-lane.md`) synced with the real Gherkin,
      including the disclosed residual gap (Host bookkeeping vs. real
      physics not cross-validated — candidate for Follow-up #2).
- [x] Full regression sweep re-run: **1377 passed** (2026-08-09); Static
      Kernel behavior outside `dynamic qpu` confirmed unaffected (no
      Static-path test changed or newly failed).
- [x] Completion approval (2026-08-09); PR [#486](https://github.com/nn0cl/staqex/pull/486).

## Refactor note: residual gap disclosed, not fixed

Discovered during Green: Host's `FakeDynamicExecutor` bookkeeping
(LISS-0383/0385/0386) and the evaluator's real execution (this Issue) are
independent — a Host-accepted supplied outcome that is physically
inconsistent with the real prepared state now legitimately vacuums the run
at the Evaluator layer while Host's `dynamic_trace.controller_bindings`
still records the (physically-impossible) supplied label. `JobResult.status`
stays `"succeeded"` either way, since a vacuum terminal measurement is not a
Kernel error. This is disclosed in the spec and here rather than silently
left implicit; unifying the two layers is a candidate for the ADR 0200
Follow-up #2 Issue (which already plans to touch this boundary when
amending LISS-0385/0386's reject-on-demand policy for simulator profiles),
not resolved by this Issue.
