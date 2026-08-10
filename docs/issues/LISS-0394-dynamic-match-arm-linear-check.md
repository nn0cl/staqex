# LISS-0394: Linear-use checking inside dynamic-lane `match` arms

## Metadata

- Local issue ID: LISS-0394
- Status/phase: **complete** (2026-08-10) — Adjudicator Completion
  approval; PR [#503](https://github.com/nn0cl/staqex/pull/503)
- Type: Feature Path (Kernel — `hir.py` linear-use checker soundness
  fix; no language surface change, no evaluator change)
- Priority: P2
- Initial planning size: `M`
- Owner / agent: Claude Code
- Program: disclosed gap from LISS-0387 Decision 4's own code comment
  ("`MatchStmt`/bare `ExprStmt` bodies are not yet visited by this
  checker (pre-existing gap, not introduced here)") and LISS-0390's
  Refactor note ("this checker's Dynamic-lane exception depends on the
  premise that match arms are not yet traversed... will need
  re-verification when that changes")
- Parent: none (Kernel-internal soundness fix, not tied to a specific ADR)
- Depends on: LISS-0387/0390 (both **complete**) — this Issue extends
  their linear-use exception, does not revise it
- Related: `compiler/staqex/hir.py` (`_analyze_block`);
  `compiler/staqex/runtime/evaluator.py` (`_run_dynamic_arm_body` —
  investigated, not modified)
- Blocks: none
- Branch: `feature/liss-0394-dynamic-match-arm-linear-check`
- GitHub Issue / PR: [#503](https://github.com/nn0cl/staqex/pull/503)

## Intent

`hir.py`'s linear-use checker (`_analyze_block`) never visits `MatchStmt`
arm bodies at all today — confirmed by direct read (no `MatchStmt` case
exists in the per-statement dispatch). This means `reset`
(LISS-0390) or mid-circuit `measure` written **inside** a `match` arm is
completely invisible to the checker: `DYN_RESET_UNKNOWN_WIRE` cannot fire
for a nonsense `reset ghost` placed inside an arm, and no discard
accounting happens for anything an arm does. This Issue closes that gap
for the statement kinds the evaluator already executes inside arms.

## Design verification performed before this Plan (grounding, not to be re-derived during Red)

1. **Confirmed `_analyze_block`'s exact per-call behavior** (`hir.py:372-497`):
   one fresh `_LinearUseState()` per call, optionally seeded via
   `seed_linear` (`introduced`/`aliases` only, **never** `consumed`), and
   `_discard_diags(state)` runs unconditionally once at the end of *that*
   call, checking `introduced - consumed` for *that* state only.
2. **Rejected the "recurse via a fresh nested `_analyze_block` call, seeded
   from the outer scope" design** (the `ForEachStmt`/`DynamicQpuStmt`
   pattern) for match arms specifically. Traced concretely: if an arm
   were processed via a new `_analyze_block(arm.body, ...,
   seed_linear=state.introduced)` call, the arm's own fresh `consumed`
   set would start **empty**, so `_discard_diags` at the end of *that*
   call would incorrectly flag every wire already consumed **before** the
   `match` (e.g. `q`, consumed by the Controller-measure preceding it) as
   newly discarded **inside every arm** — a false
   `LINEAR_IMPLICIT_DISCARD` on LISS-0387's own already-shipped
   `_SOURCE_MEASURE_ONLY`-style fixture. `ForEachStmt`/`DynamicQpuStmt`
   avoid this because they are genuine separate lexical scopes with their
   own resource lifetime (confirmed: their existing recursive call passes
   **no** `seed_linear` at all, because a `dynamic qpu` block's wires are
   always block-local, never referencing an outer Static wire — see
   LISS-0387's own investigation). `match` arms are different: they are
   **mutually-exclusive continuations of the same enclosing scope**, not
   a nested scope with independent resource lifetime.
3. **Selected design instead:** process each arm's statements against the
   **same, shared** `_LinearUseState` object already being threaded
   through the enclosing `_analyze_block` call — no new state, no
   seeding, no separate discard check. This is correct by construction
   (same object => `q`'s already-recorded `consumed` status is trivially
   visible) and is the smallest model that avoids the false-positive
   traced in point 2.
4. **Confirmed the evaluator's actual execution surface inside arms**
   (`evaluator.py::_run_dynamic_arm_body`, `runtime/evaluator.py:1285-1298`):
   only three statement kinds are dispatched — bare `ExprStmt`+`Call`
   (untracked by the checker anywhere, confirmed no regression risk),
   `ResetStmt`, and generic `StateBind` (routed through `_bind_names`,
   **not** the dedicated `_collapse_dynamic_wire` path). This means a
   `Controller<T> = measure wire` written **inside** an arm today falls
   through to the generic `StateBind`/`_bind_names` path at runtime —
   already a pre-existing **evaluator**-level gap (nested/chained
   mid-circuit measurement inside an arm is not properly executed),
   separate from and predating this Issue. **This Issue does not fix
   that evaluator gap** — it is out of scope (see below) — but the
   `hir.py` design must not pretend it is handled either.
5. **Scope boundary chosen accordingly:** the new arm-body checker
   handles exactly `ResetStmt` (dedicated, mirrors LISS-0390's top-level
   logic verbatim) and nested `MatchStmt` (recurse, for completeness — no
   extra cost). A `StateBind` found inside an arm (including a
   Controller-measure-shaped one) is intentionally **not** specially
   handled — it falls through with no diagnostic and no state mutation,
   the same "invisible" status quo, but now **disclosed** in code comment
   rather than silently identical-looking to the fixed cases. This
   matches what the evaluator actually executes (nothing dedicated) and
   avoids inventing hir.py behavior for an evaluator path that doesn't
   exist yet.

## Explicitly out of scope

- Fixing `_run_dynamic_arm_body`'s generic `StateBind` fallthrough for a
  nested Controller-measure inside an arm (pre-existing evaluator gap,
  confirmed above, not introduced or fixed by this Issue).
- Any change to `evaluator.py` at all — this Issue is `hir.py`-only.
- Cross-arm variable visibility (a wire declared via `state x = |0>`
  **inside** one arm is not tracked as available to a sibling arm — since
  processing happens sequentially against a shared state, a later arm
  could in principle see an earlier arm's declaration in `state.introduced`
  even though physically only one arm ever executes; this is a disclosed,
  accepted imprecision, not a soundness *hazard* — the earlier arm's
  declaration was truly there, just not reachable from the exact runtime
  branch taken. **Not exercised by this Issue's own tests** and flagged
  here for future reference rather than fixed, per the Adjudicator's
  request for the smallest correct model.
- Any change to `DYN_RESET_UNKNOWN_WIRE`'s top-level (non-arm) behavior.

## Plan-locked decisions

1. **New function `_analyze_dynamic_lane_arm_stmts(stmts, state) ->
   list[dict]`** in `hir.py`: processes a list of statements (an arm's
   `body.stmts`) against the **shared, passed-in** `state` — no new
   `_LinearUseState`, no seeding, no independent discard check. Handles
   `ResetStmt` (identical logic to the existing top-level branch) and
   nested `MatchStmt` (recurse into its arms via this same function).
   All other statement kinds (bare `ExprStmt`/`Call`, generic `StateBind`)
   are explicitly skipped with a code comment citing this Plan's
   Design-verification point 5 (disclosed, not silently absent).
2. **Small DRY refactor, not duplication:** the `ResetStmt`-handling
   logic is extracted from the main `_analyze_block` loop into a shared
   helper `_check_reset_stmt(stmt, state) -> dict | None` (returns a
   diagnostic dict or `None`, mutates `state.consumed` in place) called
   from **both** the existing top-level branch (behavior-preserving code
   motion, verified by the existing, already-passing LISS-0390 tests)
   and the new `_analyze_dynamic_lane_arm_stmts`. Chosen over duplicating
   the ~10-line check in two places, given the full regression suite
   (1402 tests, including LISS-0390's dedicated cases) gives strong
   confidence a pure code-motion refactor is behavior-preserving.
3. **New `_analyze_block` branch:** `elif isinstance(stmt, MatchStmt):
   diags.extend(_analyze_dynamic_lane_match(stmt, state))` where
   `_analyze_dynamic_lane_match` loops over `stmt.arms` calling
   `_analyze_dynamic_lane_arm_stmts(arm.body.stmts, state)` for each.
4. **No change to `Controller<T> = measure wire` handling** at the
   top level (still its own dedicated branch, unchanged) — this Issue
   does not extend that dedicated handling into arms, per Design
   verification point 4/5.

## Acceptance reference

No dedicated spec file owns `hir.py`'s linear-use checker; recorded in
this Issue and `docs/architecture/open-work-register.md` instead of a new
spec file, matching LISS-0393's precedent for Host-internal machinery
with no single owning spec.

### Draft test scenarios (Plan review only, not yet normative)

1. `reset` of an unknown wire **inside a match arm** now fails closed
   with `DYN_RESET_UNKNOWN_WIRE` (previously silently unchecked).
2. `reset` of a wire **known from before the match** (introduced or
   Controller-measured at the top level of the same dynamic block) inside
   an arm does **not** false-positive — the shared-state design's core
   claim, verified directly against the exact failure mode traced in
   Design verification point 2.
3. Regression: LISS-0387's `_SOURCE_MEASURE_ONLY`-style fixture (measure,
   then an arm with no reset) still produces **no**
   `LINEAR_IMPLICIT_DISCARD` — proves the rejected seeded-recursion design
   would have broken this, and the shared-state design does not.
4. Nested `match` inside a `match` arm: an unknown-wire `reset` in the
   inner match's arm is still caught (recursion works).
5. Full regression sweep unaffected outside these new/targeted assertions.

## AI planning record (size M)

- Status: Green/Refactor complete; awaiting Completion approval.
- Confidence: high — every design choice above was traced against actual
  source (not assumed) before being written down, specifically to satisfy
  the Adjudicator's request to avoid mid-Red discovery of a misalignment;
  the one rejected alternative (seeded recursion) was rejected only after
  concretely tracing the false-positive it would cause, not on
  suspicion alone. Confirmed correct: zero mid-Red or mid-Green design
  surprises occurred.

## Exit criteria

- [x] Plan approval (2026-08-10).
- [x] Phase 1 Red (2026-08-10):
      `tests/test_liss_0394_dynamic_match_arm_linear_check_red.py` — 2 of
      5 tests failed for the stated reason (unknown-wire reset inside an
      arm, and inside a nested arm, both previously invisible); the other
      3 (known-wire-inside-arm no-false-positive, measure-only regression
      guard, top-level-reset regression guard) passed immediately,
      confirming those cases were never broken.
- [x] Phase 2 Green (2026-08-10): extracted `_check_reset_stmt` (pure
      code motion, behavior-preserving per full regression) + new
      `_analyze_dynamic_lane_match` / `_analyze_dynamic_lane_arm_stmts` +
      one new `MatchStmt` branch in `_analyze_block`. All 5 tests pass;
      no test edited to force it; no mid-Green design surprise.
- [x] Phase 3 Refactor: reviewed diff — matches the Plan's design exactly
      (`hir.py` +70/-16 net); no further changes needed.
- [x] Full regression sweep re-run: **1407 passed** (2026-08-10), up from
      1402 by exactly the 5 new tests. Confirmed LISS-0390's own
      dedicated top-level-reset tests still pass unchanged (proves the
      `_check_reset_stmt` extraction was behavior-preserving).
- [x] Completion approval (2026-08-10); PR [#503](https://github.com/nn0cl/staqex/pull/503).
