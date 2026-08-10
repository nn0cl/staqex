# LISS-0395: Unify dynamic-lane statement execution (arm-only wire leak; chained mid-circuit measurement)

## Metadata

- Local issue ID: LISS-0395
- Status/phase: **complete** (2026-08-10) — Adjudicator Completion approval;
  PR (recorded below once opened)
- Type: Feature Path (Kernel — `evaluator.py` runtime fix/extension +
  matching `hir.py` linear-use checker extension; extends ADR 0200's
  already-decided mechanism, no new Architecture decision)
- Priority: P1 (Fix A is a confirmed silent state-leak bug in shipped
  LISS-0390 code, not merely a missing feature)
- Initial planning size: `M`
- Owner / agent: Claude Code
- Program: disclosed gap surfaced while investigating "what's next" after
  LISS-0394; confirmed by direct execution against the real evaluator (not
  assumption) before this Plan was written
- Parent: ADR 0200 (Decision 4's own disclosed gap: "`MatchStmt`/bare
  `ExprStmt` bodies are not yet visited") — this Issue closes the
  **evaluator**-side half of that gap; LISS-0394 already closed the
  `hir.py`-side half for `ResetStmt`/nested `MatchStmt`
- Depends on: LISS-0387/0389/0390/0394 (all **complete**)
- Related: `compiler/staqex/runtime/evaluator.py`
  (`_run_dynamic_qpu_block`, `_run_dynamic_arm_body`);
  `compiler/staqex/hir.py` (`_analyze_block`,
  `_analyze_dynamic_lane_arm_stmts`)
- Blocks: none
- Branch: `feature/liss-0395-dynamic-lane-arm-body-unification`
- GitHub Issue / PR: (opened at Completion)

## Intent

Two confirmed defects in the arm-body execution surface, both traced to the
same root cause: `_run_dynamic_arm_body` is a **second, hand-maintained
statement dispatcher** that only partially mirrors
`_run_dynamic_qpu_block`'s top-level loop, and has drifted out of sync with
it.

1. **Wire leak (confirmed bug, silent).** A wire that is only ever touched
   *inside* a `match` arm (introduced at the top level, but never
   top-level-measured or top-level-`reset`) is never added to
   `_run_dynamic_qpu_block`'s local `dynamically_measured` bookkeeping list,
   so the block-end `trace_out` loop (LISS-0387 Decision 5) never runs on
   it. It leaks into the surrounding Joint after the `dynamic qpu` block
   ends, violating the documented invariant that dynamically-touched wires
   are block-local.
2. **Chained mid-circuit measurement unsupported (confirmed gap, loud).**
   `Controller<T> = measure wire` written *inside* a `match` arm parses and
   passes `hir.py` silently (LISS-0394 explicitly left this case
   unhandled), but at evaluation time falls through
   `_run_dynamic_arm_body`'s generic `StateBind` branch into `_bind_names`
   → `_bind`, which has no `MeasureExpr` case and raises
   `KernelError("cannot bind expr MeasureExpr")`. A nested nested `match`
   dispatching on that second measurement is equally unreachable today.

## Design verification performed before this Plan (grounding, not to be re-derived during Red)

1. **Confirmed the leak concretely by direct execution**, not by reading
   code alone:
   ```
   dynamic qpu {
       state q = |0>
       state r = |0>
       Controller<Bit> bit = measure q
       match bit {
           0 => { reset r }
           1 => { }
       }
   }
   ```
   Running `Evaluator._run_dynamic_qpu_block` directly and inspecting the
   returned `Joint.worlds` shows `r` still present in `world.assign` after
   the block returns (`{'r': 0}`) — `dynamically_measured` only ever
   contained `["q"]` (from the top-level Controller-measure), so the
   block-end `trace_out` loop never touches `r`.
2. **Confirmed the `MeasureExpr` gap concretely by direct execution**:
   `grep -n "MeasureExpr" evaluator.py` shows exactly one `isinstance`
   check in the whole file (`_run_dynamic_qpu_block`'s top-level branch);
   neither `_bind_names` nor `_bind` has a `MeasureExpr` case, and `_bind`'s
   final fallback is `raise KernelError(f"cannot bind expr
   {type(expr).__name__}")` — confirmed this is the actual exception raised
   for a `Controller<T> = measure wire` written inside an arm.
3. **Traced why both defects share one root cause**: `_run_dynamic_arm_body`
   (`evaluator.py:1285-1298`) independently re-implements a subset of what
   `_run_dynamic_qpu_block`'s top-level loop (`evaluator.py:1219-1262`)
   already does — it omits the Controller-measure branch entirely, and it
   has no access to the outer `dynamically_measured` list or
   `controller_values` dict (both are local variables of
   `_run_dynamic_qpu_block`, never passed in). Two independently maintained
   copies of the same dispatch logic is exactly the "patchwork" shape
   flagged earlier this session — the correct fix is **unification**, not a
   third patch bolted onto the arm-only copy.
4. **Designed the unification**: collapse `_run_dynamic_qpu_block`'s
   top-level loop and `_run_dynamic_arm_body` into a single recursive
   function (kept under the existing `_run_dynamic_arm_body` name so the
   top level becomes "the outermost arm body" — no new function, no new
   concept). It takes `controller_values: dict[str, str]` and
   `dynamically_measured: list[str]` as **mutable, threaded-by-reference**
   parameters (mirroring how `_run_dynamic_qpu_block` already threads
   `logs`/`inspect_out` today), defaulting to fresh empty containers when
   omitted. `_run_dynamic_qpu_block` shrinks to: build the two empty
   containers, delegate the entire block body to
   `_run_dynamic_arm_body(joint, stmt.body.stmts, controller_values,
   dynamically_measured, logs=logs, inspect_out=inspect_out)`, then run the
   unchanged block-end `trace_out` loop over whatever
   `dynamically_measured` ended up containing — correct at any nesting
   depth for free, because every recursive call mutates the same two
   containers.
5. **Verified the default-argument design keeps the existing direct-call
   test backward compatible.** `tests/test_liss_0390_dynamic_reset_keyword_red.py::test_reset_inside_dynamic_qpu_genuinely_reinitializes`
   calls `evaluator._run_dynamic_arm_body(joint, dynamic_stmt.body.stmts)`
   directly (2 positional args, no `controller_values` /
   `dynamically_measured`). Confirmed the new signature's defaults
   (`controller_values: dict[str, str] | None = None`,
   `dynamically_measured: list[str] | None = None`, materialized to fresh
   empty containers inside the function when `None`) make that call site
   behave identically to today — **no existing test needs editing**.
6. **Confirmed `hir.py`'s matching half.** `_analyze_block`'s existing
   top-level Controller-measure branch
   (`isinstance(stmt, StateBind) and stmt.ty.name == "Controller" and
   isinstance(stmt.expr, MeasureExpr) and isinstance(stmt.expr.expr, Var)`
   → `state.consumed.add(wire_root)`) has no counterpart in
   `_analyze_dynamic_lane_arm_stmts` (LISS-0394 explicitly left it
   unhandled, citing exactly this evaluator gap as the reason). Once the
   evaluator supports it, the checker must too, or a real
   Controller-measure inside an arm would be executed without ever
   entering `state.consumed` — reopening the same false
   `LINEAR_IMPLICIT_DISCARD` risk LISS-0394 was written to close for
   `ResetStmt`. Extracting the existing top-level check into a small shared
   helper (mirroring the `_check_reset_stmt` extraction precedent from
   LISS-0394) avoids duplicating the ~6-line condition in two places.
7. **Confirmed `dynamic_capability.py` needs no change.**
   `_block_demands_reset`/`_block_demands_reuse` already recurse into
   `MatchStmt` arms (`for arm in statement.arms: ... arm.body`) — this is
   static AST-shape demand inference, independent of both defects above; no
   change required.

## Explicitly out of scope

- **Log/inspect threading side-effect.** The unification incidentally makes
  arm-body `inspect`/log statements receive the real `logs`/`inspect_out`
  instead of the old arm-body copy's hardcoded `logs=[], inspect_out=None`
  (a discarded-output gap in the pre-LISS-0395 code, now closed as a direct
  consequence of deleting the duplicate dispatcher — not independently
  designed or tested beyond what the unification naturally produces).
- **RNG-sampled outcomes** for a chained second measurement — still
  supplied-outcome only (ADR 0200 Decision 4 scope, unchanged).
- **A new `LINEAR_DUPLICATE_USE`-style check** for re-measuring the same
  wire twice without an intervening `reset` — top-level Controller-measure
  has never checked this (`state.consumed.add` is unconditional there
  today); the arm extension mirrors that exact existing behavior rather
  than inventing stricter checking not asked for.
- **Cross-arm variable visibility** — already disclosed and left as-is by
  LISS-0394; unaffected by this Issue.
- Any `JobResult`/`DynamicTraceReport` DTO change (LISS-0389's
  `physical_outcome_confirmed` field is reused unchanged for verification,
  not extended).

## Plan-locked decisions

1. Extend `_run_dynamic_arm_body`'s signature to
   `(self, joint, stmts, controller_values=None, dynamically_measured=None,
   *, logs=None, inspect_out=None)`, materializing fresh empty containers
   when the mutable defaults are `None`. Body becomes the union of the old
   top-level loop's four branches (Controller-measure, `MatchStmt`,
   `ResetStmt`, generic `StateBind`) plus the existing bare
   `ExprStmt`+`Call` branch, with `MatchStmt` dispatch recursing into this
   same function (passing the same `controller_values` /
   `dynamically_measured` references through).
2. Shrink `_run_dynamic_qpu_block` to: allocate the two containers,
   delegate to `_run_dynamic_arm_body`, keep the unchanged block-end
   `trace_out` loop. Delete the now-duplicate inline loop.
3. In `hir.py`, extract `_is_controller_measure_stmt(stmt) -> bool` and
   `_consume_controller_measure_wire(stmt, state) -> None` from
   `_analyze_block`'s existing inline check (pure code motion, same pattern
   LISS-0394 used for `_check_reset_stmt`). Call both from `_analyze_block`
   (replacing the inline check) **and** from
   `_analyze_dynamic_lane_arm_stmts` (new branch), updating that function's
   docstring to no longer claim Controller-measure is unhandled.
4. No AST, parser, ADR, or DTO change. No new diagnostic code.

## Draft test scenarios (Plan review only, not yet normative)

1. **Leak fix, direct evaluator check**: the exact reproduction in Design
   verification point 1 — after `_run_dynamic_qpu_block` returns, `r` is
   **not** present in any world's `assign` (mirrors
   `test_reset_inside_dynamic_qpu_genuinely_reinitializes`'s direct-Joint
   style).
2. **Chained measurement runs for real**: `Controller<Bit> bit2 = measure
   q2` inside an arm, no longer raises `KernelError`; a nested `match bit2
   {...}` inside the same arm dispatches to the arm matching the
   Host-supplied outcome for `bit2`.
3. **Chained measurement physical-consistency check** (mirrors LISS-0389's
   verification rigor): a Host-supplied outcome for the *second* measure
   that is physically impossible given the real post-first-collapse state
   vacuums the run — `dynamic_trace.physical_outcome_confirmed is False` —
   proving the second collapse is a real `project_coord` projection, not a
   bookkeeping label.
4. **`hir.py` regression guard**: source with a Controller-measure inside
   an arm and nothing after produces **no** `LINEAR_IMPLICIT_DISCARD` for
   the measured wire (mirrors LISS-0394 Scenario 3's shape).
5. **Backward-compat regression**: existing LISS-0387/0389/0390 tests
   (including the direct 2-arg `_run_dynamic_arm_body` call site) pass
   unchanged with no edits.
6. Full regression sweep unaffected outside these new/targeted assertions.

## AI planning record (size M)

- Status: Green/Refactor complete; Completion approval granted (2026-08-10).
- Confidence: high — both defects were confirmed by direct execution
  (printed evaluator output), not by reading code and assuming; the
  unification design was checked against the one existing direct-call test
  site before being locked, specifically to avoid an editing-a-test
  surprise mid-Green.

## Exit criteria

- [x] Plan approval (2026-08-10).
- [x] Phase 1 Red (2026-08-10):
      `tests/test_liss_0395_dynamic_arm_body_unification_red.py` — 4 of 5
      tests failed for the stated reason (arm-only wire `r` still present
      after block end; chained measure raised `RUNTIME_ERROR: cannot bind
      expr MeasureExpr`, confirmed via direct `job.result()` inspection,
      for both the consistent- and inconsistent-outcome variants; `hir.py`
      emitted `LINEAR_IMPLICIT_DISCARD` for the arm-measured wire). The
      backward-compat regression guard (existing 2-arg
      `_run_dynamic_arm_body` call shape) passed immediately, confirming
      that case was never broken.
- [x] Phase 2 Green (2026-08-10): unified `_run_dynamic_qpu_block`'s
      top-level loop into `_run_dynamic_arm_body` (now threading
      `controller_values`/`dynamically_measured` by reference, with
      backward-compatible `None`-defaulted parameters); extracted
      `_is_controller_measure_stmt`/`_consume_controller_measure_wire` in
      `hir.py` and called both from `_analyze_block` (code motion) and
      `_analyze_dynamic_lane_arm_stmts` (new). All 5 new tests pass; no
      test edited to force it; no mid-Green design surprise.
- [x] Phase 3 Refactor: reviewed diff — matches the Plan's design exactly
      (`evaluator.py` net +46/-64 lines net incl. moved code,
      `hir.py` +25/-24 lines net incl. moved code); no further changes
      needed.
- [x] Full regression sweep re-run: **1412 passed** (2026-08-10), up from
      1407 by exactly the 5 new tests.
- [x] Completion approval (2026-08-10).
