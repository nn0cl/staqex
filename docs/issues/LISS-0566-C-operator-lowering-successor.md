# LISS-0566-C: Operator resolution/lowering successor

## Metadata

- Local issue ID: LISS-0566-C
- Status: done — Phase 3 final review accepted
- Phase: phase-3-final-review
- Type: Feature Path bounded structural decomposition
- Priority: high
- Planning size: L
- Parent: WP-0163 / WP-0162 successor
- Depends on: LISS-0566-A, LISS-0566-B
- Blocks: LISS-0566-D successor facade/structure audit
- Related branch: `codex/liss-0566-evaluator-stateful-successor`

## Summary

Move the remaining stateful Operator resolution/lowering implementation out of
`compiler/staqex/runtime/evaluator.py` into
`compiler/staqex/runtime/evaluation/operators.py`, while preserving the
physicist-facing Operator meaning, runtime behavior, diagnostics, QASM output,
and the existing private compatibility surface.

This is a structural extraction. It is not permission to repair an unrelated
operator semantic defect, add syntax, change Semantic IR authority, or add a
provider/QPU integration.

## Design intake and measured scope

Approved on 2026-09-19:
`WP-0163 / LISS-0566-C acceptance/design intake 承認`.

The current `runtime/evaluator.py` is **4,957 lines**. Unit C contains **11
methods / 507 physical lines**:

| Responsibility | Methods | Lines |
|---|---|---:|
| name/RHS classification | `_operator_legacy_operator_name`, `_operator_legacy_looks_like_operator_rhs` | 22 |
| resolution/array context | `_operator_legacy_resolve_operator`, `_operator_legacy_array_context` | 52 |
| nested calls/tree/set lookup | `_operator_legacy_resolve_op_call`, `_operator_legacy_resolve_operator_tree`, `_operator_legacy_lookup_set_comprehension_value` | 135 |
| value lowering | `_operator_legacy_lower_operator_value` | 18 |
| function factory | `_operator_legacy_resolve_operator_factory_call` | 135 |
| class method | `_operator_legacy_resolve_operator_method_call` | 123 |
| second-quantized bind | `_operator_legacy_bind_second_quantized` | 22 |

Existing pure helpers `expr_arg_to_source_expr` and
`build_projector_sum_operator` remain in `evaluation/operators.py` and must
not be duplicated or moved into a generic AST utility module.

## Boundary decisions

1. `Evaluator` remains the sole mutable state owner.
2. Operator services receive a typed context or narrow callbacks for live
   operator/grid-Hamiltonian, scalar/object/class/struct/enum,
   second-quantized, and finite-array environments; the service does not copy
   or retain those maps.
3. Factory-call parameter-rekeyed locals and method-call receiver state remain
   call-local. Receiver `_this` restoration is exception-safe.
4. Recursive Operator-tree resolution remains one canonical runtime pass and
   preserves ordering, unchanged-subtree identity, `OpAttr`, nested calls,
   finite binders, projector sums, and supported second-quantized mapping.
5. `evaluation/compatibility.py` retains established private hooks until Unit
   D; the bridge contains no policy or duplicate implementation.
6. Scientific Semantic IR, QASM projection, diagnostic contracts, provider
   boundaries, and deployment behavior are unchanged.

## Included / excluded

Included: Unit C methods, explicit context callbacks, compatibility wiring,
focused structural/characterization tests, and documentation evidence.

Excluded: Unit D facade audit; parser/typechecker/IR changes; new language
semantics; provider SDK/network/credentials/live QPU; Rust migration; and
unrelated pre-existing semantic failures.

## Acceptance contract

Phase 1 Red must cover ownership and no-facade dependency, narrow context
contracts, private-consumer compatibility, factory/method local binding and
receiver restoration, finite-binder materialization, recursive tree behavior,
second-quantized mapping, positive neighboring forms, unsupported-form
rejection, fixed-seed local results, QASM identity, and diagnostic atomicity.

Phase 2 Green may move only the minimum implementation needed for the reviewed
Red contracts. Phase 3 may rename/clarify extracted responsibilities without
changing assertions or behavior. Unit C is complete only after final review,
status synchronization, and process review.

## Phase 1 Red

Approved on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 1 Red 承認`.

Added `tests/test_liss_0566_unit_c_red.py` with eleven contracts. The focused
run reports **4 failed, 7 passed**: structural ownership,
callback, and exact compatibility contracts fail because the Unit C
implementation is still on `Evaluator`; the no-facade dependency and seven
runtime characterization contracts, including explicit projector-tree and
second-quantized nodes, remain green. No production source or reviewed
assertion was changed.

The active-Red ownership is recorded in
`docs/testing/active-red-tests.toml`. Phase 1 exit requires a separate typed
test-review approval before Phase 2 Green can be requested.

## Phase 1 Red test review

Review packet: [LISS-0566-C Phase 1 Red test review](../collaboration/reviews/2026-09-19-liss-0566-c-phase1-red-test-review.md).

Approved on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 1 Red テストレビュー承認`.

The review accepted the four intentional structural Red failures and seven
passing characterization contracts. Two explicit characterization nodes for
set-projector tree lowering and Jordan-Wigner second-quantized binding were
added during review. The active-Red entry remains until Phase 2 Green.

## Process lessons applied

- Private consumers are inventoried before extraction; exact compatibility
  assignments are tested rather than inferred from name presence.
- `Evaluator` remains the sole mutable state owner; extracted code receives
  explicit callbacks and does not reconstruct state.
- Compatibility bridges are named as retained migration surfaces, not claimed
  as complete implementation migration.
- Negative unsupported-form assertions are paired with positive neighboring
  representations to avoid overmatching valid operators.

## Next approval

`WP-0163 / LISS-0566-C Phase 2 Green / Implementation 承認`

## Phase 2 Green

Implementation approval received on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 2 Green / Implementation 承認`.

Moved the eleven Unit C implementation methods into
`runtime/evaluation/operators.py`. The extracted functions receive live
Evaluator state through declared context callbacks; they do not import or
construct `Evaluator`, retain copied mutable maps, or add provider/QPU
dependencies. `evaluation/compatibility.py` keeps the established private
hooks and `_resolve_operator_expr` alias as a thin migration bridge.

Measured result: `runtime/evaluator.py` is **4,491 lines** and
`runtime/evaluation/operators.py` is **617 lines**. The 11-method, 507-line
Unit C surface is no longer implemented on the facade. The active-Red entry for
LISS-0566-C was removed after Green.

Verification: Unit C focused **11 passed**, adjacent regressions **29 passed**,
combined structural suite **17 passed**, affected S02/benchmark/legacy suite
**20 passed**, and full blocking pytest **2,147 passed**. `git diff --check`
passed after whitespace cleanup.

No Semantic IR, parser/typechecker, QASM projection, diagnostics,
provider/QPU boundary, credential, network, or live-QPU behavior changed.
Phase 3 remains for responsibility naming, formatting, and final review only;
it must preserve the Phase 2 assertions and compatibility bridge.

Next approval:
`WP-0163 / LISS-0566-C Phase 3 Refactor 承認`.

## Phase 3 Refactor

Refactor approval received on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 3 Refactor 承認`.

Improved `evaluation/operators.py` without changing its acceptance assertions
or runtime meaning: normalized extracted-function indentation and signatures,
removed a duplicate local AST import, added the missing `LitFloat` import for
source-expression conversion, centralized numeric receiver-field extraction,
clarified class lookup and host-array merging, and formatted long lowering and
mapping calls. The compatibility bridge and all extracted entrypoints remain
unchanged in ownership.

Verification after refactor: Unit C and adjacent suites **46 passed**, full
blocking pytest **2,147 passed**, compileall passed, and `git diff --check`
passed. Spec Verification remains **161/161**; document lifecycle, Active-Red
lifecycle, and coverage-ledger checks pass. The module sizes remain
`evaluator.py` **4,491 lines** and `operators.py` **617 lines**.

No parser/typechecker, Semantic IR, QASM projection, provider boundary,
network, credential, or live-QPU behavior changed.

Next approval:
`WP-0163 / LISS-0566-C Phase 3 最終レビュー 承認`.

## Phase 3 final review

Review packet: [LISS-0566-C Phase 3 final review](../collaboration/reviews/2026-09-19-liss-0566-c-phase3-final-review.md).

Approved on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 3 最終レビュー 承認`.

The bounded Unit C scope is complete. The review found no blocker: extracted
ownership, single-state ownership, compatibility wiring, structure budget, and
behavior-preservation evidence all passed. Process review found no
operating-contract deviation or operational problem. Unit D facade/structure
audit remains separate successor scope and requires its own acceptance/design
intake.

Process review: no operating-contract deviation or operational problem found.
