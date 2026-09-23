# LISS-0570: Evaluator successor decomposition

## Metadata

- Local issue ID: LISS-0570
- Status: done — Unit A1 execution-shell successor complete
- Phase: complete
- Type: Architecture Path structural decomposition
- Planning size: XL
- Parent: WP-0167
- Depends on: WP-0166 / LISS-0569 complete
- Blocks: none

## [DESIGN CHECK]

### Scope and expected behavior

Reduce the remaining `runtime/evaluator.py` size by extracting cohesive
runtime families into new or explicitly bounded evaluation modules. Preserve
behavior, diagnostics, mutation order, DTO identity, private compatibility,
and the single live `Evaluator` state owner.

### Initial decomposition plan

1. Unit A — execution fallback and statement routing.
2. Unit B — frames, constructors, and assignments, split by responsibility
   rather than enlarging one existing dependency module.
3. Unit C — pure pipe/polynomial mechanics.
4. Unit D — state construction and state algebra.

The units are not authorized as one implementation batch. Each receives its
own design intake, Red contract, implementation approval, refactor review,
and final review.

### Boundaries and exclusions

- `Evaluator` owns all mutable maps, DTO definitions, `Joint` lifecycle,
  injected ports, and compatibility aliases.
- Successor modules use `EvaluatorContext` callbacks and do not import or
  instantiate `runtime.evaluator`.
- `typecheck.py` and `parser.py` are excluded. They are large but independent
  compiler phases; their decomposition will not directly reduce evaluator
  size and must be planned separately.
- No parser, typechecker, Semantic IR, QASM, provider, network, Rust, syntax,
  or public API retirement work is included.

### Phase 0 evidence to produce

- AST method-family inventory with current line/method counts.
- Call graph for `_run_legacy_ast_body`, `_bind`, frame/constructor/
  assignment, pipe, and state families.
- State/DTO read-write inventory and callback ownership map.
- Static private-consumer/import manifest plus limitations.
- Exact allowed paths and Unit A acceptance contract.

### Requested decision

Requested approval type: **Architecture Path scope approval**.

Requested target:
`WP-0167 / LISS-0570 Architecture Path scope approval`

### Phase 0 acceptance record

Approved target:
`WP-0167 / LISS-0570 Architecture Path scope approval` (2026-09-20).

The evaluator-only scope is accepted. Unit A1 is narrowed to the execution
shell: `_run_legacy_ast_body`, `_run_unit_body` compatibility wiring, main
statement routing, run-state initialization, and `EvalResult` assembly.
`_bind` and `_bind_names` remain explicit consumer boundaries for a later A2
slice because dynamic-lane, observation, continuous, and direct tests call
them privately.

Accepted Unit A1 paths are `evaluator.py`, new
`runtime/evaluation/execution.py`, `context.py`, `compatibility.py`, the new
Red test, active-Red ledger, and linked lifecycle/review records. No
typechecker, parser, language, provider, QPU, Semantic IR, or unrelated
runtime changes are included.

The single mutable `Evaluator` state owner, runtime DTO identity, `Joint`
lifecycle, injected ports, and canonical execution authority remain unchanged.

This acceptance does not authorize implementation. Next gate:

`WP-0167 / LISS-0570 Unit A1 Phase 1 Red 承認`.

## Unit A1 Phase 1 Red

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 1 Red 承認` (2026-09-20).
- Test: `tests/test_liss_0570_execution_red.py`.
- Active-Red ownership: registered in `docs/testing/active-red-tests.toml`.
- Contract: five intended structural failures and three passing
  characterization tests. The structural nodes cover successor existence,
  facade body retirement, compatibility wiring, context callbacks, and the
  no-public-facade dependency boundary.
- No production implementation was started.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 1 Red テストレビュー承認`.

## Unit A1 Phase 1 Red test review

- Approval reviewed: `WP-0167 / LISS-0570 Unit A1 Phase 1 Red テストレビュー承認`
  (2026-09-20).
- Review packet: `docs/collaboration/reviews/2026-09-20-liss-0570-a1-phase1-red-review.md`.
- Result: bounded suite reproduced **5 failed, 3 passed**. Structural gaps
  remain intentionally Red; characterization behavior remains passing.
- Required lifecycle, document, coverage-ledger, and diff checks passed.
- No implementation permission is inferred from this review. Active-Red
  ownership remains `phase-1-red` under LISS-0570.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 2 Green / Implementation 承認`.

## Unit A1 Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 2 Green / Implementation 承認`
  (2026-09-21).
- Implemented the approved execution-shell extraction in
  `runtime/evaluation/execution.py`; removed both execution method bodies from
  `runtime/evaluator.py`; retained private compatibility names through the
  compatibility installer.
- The successor has no public-facade dependency and remains below the 1,200
  line guardrail. Mutable evaluator state and runtime DTO identity remain
  evaluator-owned.
- Verification: Red contract **8 passed**; focused/adjacent **40 passed**;
  full blocking suite **2,187 passed** in 310.23s. Compileall, lifecycle,
  document, coverage-ledger, and diff checks passed.
- The active-Red entry was retired after all eight approved nodes passed.
- Phase 3 refactor and same-context review are still required; this does not
  mark LISS-0570 complete.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 3 Refactor 承認`.

## Unit A1 Phase 3 Refactor

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 3 Refactor 承認`
  (2026-09-21).
- Named the execution-context preparation and terminal-result assembly
  responsibilities in `runtime/evaluation/execution.py` without changing
  behavior or the accepted A1 boundary.
- Review packet: `docs/collaboration/reviews/2026-09-21-liss-0570-a1-phase3-review.md`.
- Verification: focused/adjacent **23 passed**; all-blocking **2,187 passed**;
  compileall, lifecycle, document, coverage-ledger, and diff checks passed.
- No blocker found. Final review is required; LISS-0570 is not complete.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 3 最終レビュー 承認`.

## Unit A1 Phase 3 final review

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 3 最終レビュー 承認`
  (2026-09-21).
- Final review packet: `docs/collaboration/reviews/2026-09-21-liss-0570-a1-final-review.md`.
- Result: accepted. Unit A1 execution-shell decomposition is complete;
  compatibility aliases, state ownership, diagnostics, ordering, and
  structural boundaries remain valid.
- Verification: focused/adjacent **23 passed**; latest all-blocking
  verification **2,187 passed**; compileall, lifecycle, document,
  coverage-ledger, and diff checks passed.
- Process review: no operating-contract deviation or operational problem
  found.
- LISS-0570 is done. A2 and Units B–D require new phase approvals.
