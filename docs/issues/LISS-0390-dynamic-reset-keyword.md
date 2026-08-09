# LISS-0390: Implement the dynamic-lane `reset` keyword

## Metadata

- Local issue ID: LISS-0390
- Status/phase: **Green/Refactor complete** (2026-08-10) — awaiting
  Completion approval; PR not yet opened
- Type: Feature Path (Kernel — new contextual keyword; parser, AST,
  linear-use, capability law, evaluator dispatch)
- Priority: P1
- Initial planning size: `L`
- Owner / agent: Claude Code
- Program: [ADR 0199 Amendment](../architecture/adr/0199-dynamic-qubit-reuse-reset.md#amendment-accepted-2026-08-10-reset-keyword-option-b-revisited)
  (Accepted 2026-08-10, PR [#493](https://github.com/nn0cl/staqex/pull/493))
- Parent: ADR 0199 + its Amendment (both Accepted)
- Depends on: [LISS-0387](LISS-0387-dynamic-real-mid-circuit-measure.md) /
  [LISS-0388](LISS-0388-dynamic-reuse-capability-followup2.md) /
  [LISS-0389](LISS-0389-dynamic-outcome-confirmation.md) (all **complete**)
- Related: `compiler/staqex/parser.py` (`_stmt`, `_match_stmt` precedent);
  `compiler/staqex/ast_nodes.py` (`MatchStmt`); `compiler/staqex/hir.py`
  (Controller-measure linear-use exception, LISS-0387 Decision 4);
  `compiler/staqex/dynamic_capability.py`; `compiler/staqex/dynamic_qpu.py`;
  `compiler/staqex/runtime/evaluator.py` (`_run_dynamic_qpu_block`)
- Blocks: none
- Branch: `feature/liss-0390-dynamic-reset-keyword`
- GitHub Issue / PR: none yet

## Intent

Implement the `reset` keyword the ADR 0199 Amendment Accepted: a new
contextual keyword, lane-local to `dynamic qpu` (same precedent as
`match`). `reset wire` performs `Joint.trace_out(wire)` then re-prepares
`wire` as `|0⟩` — reusing the two already-shipped primitives LISS-0387
and ADR 0173 established. No new Joint math.

## Explicitly out of scope

- OpenQASM `reset` emission; live provider reset pulse schedules (ADR
  0199 Amendment's own Out of scope list).
- Any change to `measure` / `match` / the `Controller` model.
- Any change to Static Kernel `state x = |0>` semantics (deliberately
  kept distinct from Dynamic-lane `reset` — see the Amendment's Rejected
  alternative).
- `JobResult` / `dynamic_trace` DTO changes.

## Plan-locked decisions (Adjudicator 2026-08-10, ADR 0199 Amendment)

1. **Parser:** mirror `match`'s exact precedent
   ([parser.py:1722](../../compiler/staqex/parser.py),
   [parser.py:1832](../../compiler/staqex/parser.py) `_match_stmt`) —
   recognize `reset` as a contextual soft keyword via
   `self._check(TokenKind.IDENT) and self._peek().lexeme == "reset"` in
   `_stmt()`, not a new `TokenKind`. Grammar: `reset wire` (bare
   statement, single identifier target, no block, no binding).
2. **AST:** new `ResetStmt(target: str, span: Span)` in `ast_nodes.py`,
   mirroring `MatchStmt`'s shape (`scrutinee: str`).
3. **Lane validity:** `reset` outside `dynamic qpu` fails closed with a
   stable diagnostic. Plan-time investigation found `match` itself has no
   located explicit "outside dynamic qpu" rejection diagnostic in
   `typecheck.py`/`hir.py` — the exact mechanism (or lack of one) must be
   confirmed precisely during Red before deciding whether `reset` needs a
   new check or can rely on an existing one; do not assume equivalence to
   `match` without verifying against current source at Red time.
4. **`hir.py` linear-use law:** after `reset wire` inside the dynamic-lane
   nested scope, `wire` is treated as freshly introduced again (mirrors
   LISS-0387 Decision 4's Controller-measure exception, but goes further:
   fully fresh rather than "alive but measured"). `wire` must already be
   a known local root (introduced earlier in the same block) — resetting
   an unknown name fails closed.
5. **`dynamic_capability.py` inference:** `needs_reset` is inferred from
   source (presence of a `ResetStmt` in the block), replacing today's
   permanent `needs_reset=False` (LISS-0385 Decision 1, now superseded by
   the Amendment for the inference side only — LISS-0385's "never
   auto-inferred" boundary was itself conditioned on no reset spelling
   existing; one now does).
6. **`dynamic_qpu.py` capability law:** `needs_reset` is no longer
   unconditionally rejected on simulator-class profiles
   (`SIM0_EXACT`, `CH1_DIGITAL_RESEARCH`) — symmetric to LISS-0388's
   reuse treatment, same rationale (no physical constraint on a real
   local simulator).
7. **Evaluator dispatch:** `_run_dynamic_qpu_block` (LISS-0387) gains a
   `ResetStmt` branch: `joint = joint.trace_out(wire)` then
   `joint = self._bind_names(joint, [wire], KetLit(label="0", span=...),
   logs=[], inspect_out=None)`. No new Joint primitive.
8. **Host wiring:** `build_dynamic_exec_request`
   (`dynamic_fake_wire.py`) already calls `infer_dynamic_capability_demand`
   (LISS-0386) — once Decision 5 makes that function detect `needs_reset`,
   no further Host-layer change is needed (the existing auto-attach
   wiring already threads whatever the inference function returns).

## Acceptance reference

To be added to
[`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md) as a new
"Acceptance scenarios — reset keyword (ADR 0199 Amendment, LISS-0390)"
section.

### Draft Gherkin (Plan review only, not yet normative)

```gherkin
Feature: Dynamic-lane reset genuinely reinitializes a measured wire

  Scenario: reset outside dynamic qpu fails closed
    Given a Static-only program with a bare `reset q` statement
    When it is compiled
    Then diagnostics include a stable dynamic-lane-restriction code
    And Static Kernel behavior for ordinary programs is unaffected

  Scenario: reset inside dynamic qpu genuinely reinitializes the wire
    Given a dynamic qpu block with `state q = |0>`, `Controller<Bit> bit
      = measure q`, then `reset q`
    And a Host-supplied outcome consistent with the prepared state
    When the Evaluator runs the compiled unit
    Then q is traced out and re-prepared as |0> (verified at the
      Evaluator/Joint boundary, per LISS-0387 Decision 7's precedent)
    And no LINEAR_IMPLICIT_DISCARD / LINEAR_DUPLICATE_USE diagnostic is
      emitted for q

  Scenario: reset wire is usable again after reset
    Given the same program, with a second `Controller<Bit> bit2 = measure
      q` statement after `reset q`
    When the Evaluator runs the compiled unit
    Then the second measurement succeeds against the freshly reset |0>
      wire, exactly as if q were newly introduced

  Scenario: needs_reset is inferred and no longer rejected on simulator-class profiles
    Given a dynamic qpu block containing a reset statement
    When demand inference runs
    Then needs_reset is true
    And FakeDynamicExecutor / verify_dynamic_request accepts the request
      on SIM0_EXACT / CH1_DIGITAL_RESEARCH
```

## AI planning record (size L)

- Status: Plan drafted; awaiting Adjudicator Plan approval
- Authoring environment: Claude Code, 2026-08-10
- Size: `L` — spans parser, AST, `hir.py`, `dynamic_capability.py`,
  `dynamic_qpu.py`, and `evaluator.py`; new keyword surface (higher
  discovery risk than a pure Kernel-internal change).
- Route: AT-TDD after Plan approval.
- Confidence: medium — mechanism for each layer is grounded in an
  existing shipped precedent (`match` for parsing, LISS-0387's Controller
  exception for `hir.py`, LISS-0388 for capability law, `trace_out` +
  `KetLit` prep for evaluator), but the exact "reject reset outside
  dynamic qpu" mechanism is not yet confirmed (Decision 3) and may
  surface a small design question during Red.
- Revision links: implements the ADR 0199 Amendment (PR #493).

## Exit criteria

- [x] Plan approval (2026-08-10).
- [x] Phase 1 Red (2026-08-10):
      `tests/test_liss_0390_dynamic_reset_keyword_red.py` — 4 of 5 tests
      failed for the stated reasons after the parser/AST addition (the
      "outside dynamic qpu fails closed" scenario already passed
      unchanged, confirming Decision 3's resolution below). One test
      (`test_reset_wire_is_usable_again_after_reset`) was rewritten
      **during Red, before any Green code existed**: its first version
      passed even without implementation (reset being silently ignored
      is indistinguishable from working, when the only check was
      `status == "succeeded"`), so it was strengthened to assert
      `dynamic_trace.physical_outcome_confirmed` (LISS-0389) instead —
      the same kind of Red-phase verification-strategy correction made
      during LISS-0387.
- [x] Phase 2 Green (2026-08-10): parser (`_reset_stmt`, mirroring
      `_match_stmt`) + AST (`ResetStmt`) + `hir.py` (linear-use branch,
      unknown-wire diagnostic) + `dynamic_capability.py`
      (`_block_demands_reset`, `needs_reset` inference) +
      `dynamic_qpu.py` (capability law) + `evaluator.py`
      (`_reset_dynamic_wire`, dispatched from both
      `_run_dynamic_qpu_block` and `_run_dynamic_arm_body`). All 5 tests
      pass; no test edited to force it (the one rewrite above happened
      before Green).
- [x] Phase 3 Refactor: reviewed diff (ast_nodes.py +14, dynamic_capability.py
      +28/-5(net), dynamic_qpu.py +28/-22(net), hir.py +24, parser.py +13,
      evaluator.py +26) — minimal, no further changes needed. Implementation
      note: Decision 4's Plan wording ("wire is treated as freshly
      introduced again") was refined during Green to mirror LISS-0387
      Decision 4's simpler "mark consumed" treatment instead of a
      separate fresh-introduction bookkeeping path — functionally
      equivalent for every tested case (nothing in this checker
      re-inspects a consumed root for duplicate use), simpler to
      implement and reason about.
- [x] Full regression re-run surfaced two expected, previously-flagged
      consequences (not surprises): LISS-0388's own regression guards
      (`test_fake_gate_present_but_reset_demanded_still_fails_closed` in
      `test_liss_0383_...`, `test_ch1_profile_rejects_unsupported_reset_reuse_latency`
      in `test_dynamic_qpu_integrated_red.py`) asserted reset still
      rejected — exactly the capability-law change this Issue's own
      Decision 6 made. Amended in the same spirit as LISS-0388's own
      amendment of LISS-0383/0386, plus a new
      `test_ch1_profile_accepts_reset_alone` guard.
- [x] Spec (`staqex-dynamic-qpu-lane.md`) synced with the real Gherkin;
      status table updated.
- [x] Full regression sweep re-run: **1387 passed** (2026-08-10), up from
      1381 by 5 new LISS-0390 tests + 1 new CH1-accepts-reset-alone guard
      (the two LISS-0388 guard renames are 1:1 replacements). Static
      Kernel and pre-existing Dynamic-lane behavior outside this Issue's
      scope confirmed unaffected.
- [ ] Completion approval.
