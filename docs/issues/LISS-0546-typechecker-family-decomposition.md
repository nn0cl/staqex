# LISS-0546: Typechecker family decomposition

## Metadata

- Local issue ID: LISS-0546
- GitHub issue: none
- Status: done
- Phase: done
- Type/priority: refactor / P1
- Initial/current planning size: XL / XL
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/typechecker-families`

## Summary

Retain `typecheck.TypeChecker`, `Ty`, and diagnostic behavior while extracting
declaration/body validation, operator algebra, dimensions, expression
inference, effects, and evolution policy into `typechecking/`.

## Planned extraction units

- `context.py`: one authoritative environment/diagnostic sink.
- `declarations.py`: duplicate, visibility, body, interface/implementation.
- `operators.py`: operator domains, indexed/binder and second-quantized checks.
- `dimensions.py`: units, arrays/tensors, promotion, conversions.
- `inference.py`: expression/call/pipe/binop/attribute inference dispatch.
- `evolution.py`: evolve and Suzuki contracts.

## Acceptance Notes

Diagnostic code, line, column, ordering, inferred types/units/effects, and
mutation of accepted AST annotations are exact pre/post matches. No subsystem
may emit directly outside the shared diagnostic sink.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0543
- Blocks: LISS-0550
- Related: type-first and scientific semantic specifications

## Adjudicator Decision Points

Approve `TypeCheckContext` ownership and unit sequence; do not combine this
branch with parser or behavior corrections.

## AI Planning Record — AIP-0546-001

- Status/date/size: proposed / 2026-09-11 / XL
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: six units; N/A token estimate
- Basis/confidence: 4,460-line class, several 200–580-line methods; medium
- Assumptions: AST and public `Ty` remain stable
- Revises/Superseded by: none

## Phase 0 acceptance / detailed design

- Adjudicator approval: `LISS-0546 Phase 0 acceptance 承認`, received
  2026-09-15.
- Canonical basis: [core module decomposition specification](../specs/staqex-core-module-decomposition.md)
  and the existing type-first/scientific language specifications.
- Review packet: [LISS-0546 Phase 0 design review](../collaboration/reviews/2026-09-15-liss-0546-phase0-design-review.md)
- Trace: [LISS-0546 design trace](../collaboration/traces/2026-09-15-liss-0546-typechecker-families-design.md)

### Current concentration

`compiler/staqex/typecheck.py` is approximately 4,668 lines. The highest-risk
concentrations are `check_unit()` (about 583 lines), `_infer_call()` (about 436
lines), `_infer_inner()` (about 217 lines), `_check_operator_expr()` (about
282 lines), and `_check_function_body()` (about 170 lines). The checker also
owns mutable environment, diagnostics, static scalar values, enum/class/struct
metadata, interface names, and system-register metadata.

### Extraction units and boundaries

| Unit | Owns | Does not own | Initial entrypoints |
|---|---|---|---|
| `context.py` | explicit environment, diagnostic sink, metadata lookup and scoped environment operations | grammar, AST schema, public `Ty` retirement | `TypeCheckContext` |
| `declarations.py` | duplicate/visibility checks, declarations, function/class/interface contracts | expression inference and operator algebra | declaration dispatch from `check_unit` |
| `operators.py` | operator domains, indexed/binder checks, second-quantized and algebra checks | dimensions, call effects, AST parsing | `_check_operator_expr`, `_check_algebra_call`, `_check_second_quantized_expr` |
| `dimensions.py` | dimension compatibility, unit/array/tensor promotion, local dimension surface | operator family policy and effects | `_check_assign`, `_check_payload_assign`, dimension helpers |
| `inference.py` | expression/call/pipe/binop/attribute inference | declaration registration, evolution policy | `_infer_inner`, `_infer_call`, `_infer_pipe` |
| `evolution.py` | evolve/Suzuki/effect contracts and static scalar policy | matrix/runtime execution and QASM | `_infer_evolve`, `_check_suzuki_policy`, `_check_evolve_until_contract` |

### State ownership and dependency direction

`TypeChecker` remains the single mutable compilation-state owner during the
incremental migration. Extracted units receive a narrow context protocol and
must not copy `env`, `diagnostics`, `static_scalars`, metadata maps, or scope
stacks. No extracted module may import back into the public `typecheck` facade.
`Ty`, `Dim`, AST classes, and diagnostic dictionaries remain existing public
contracts. No port, adapter, dependency, or provider boundary is added.

`check_unit()` will retain top-level sequencing and delegate one declaration or
statement family at a time. Scoped operations such as `forEach`, function body
frames, and implementation contracts must restore the previous environment in
all paths. Diagnostic emission remains centralized so code, span, and order are
unchanged.

### Boundary decisions

- Declaration registration precedes body checking exactly as today; moving a
  check must not change forward-reference or visibility behavior.
- Operator checks may request dimension facts through context, but dimensions
  do not decide operator-family policy.
- Inference may request effect information, but effects do not mutate the
  declaration registry.
- Evolution owns Suzuki/evolve contract diagnostics; runtime evolution stays
  outside this issue.
- No generic `utils.py` or catch-all checker service is allowed.

### Phase 1 acceptance matrix

- Declarations: duplicate/visibility, class/interface/implementation, function
  body and accepted annotation snapshots.
- Operators: domains, indexed/binder bounds, algebra, second quantization,
  and exact diagnostic ordering.
- Dimensions: units, arrays/tensors, payload assignment and promotion.
- Inference: calls, pipes, attributes, binary operations and inferred `Ty`.
- Evolution: Evolve/Suzuki/effects, static scalar resolution and rejection.
- Cross-unit: public symbols, one environment owner, scope restoration,
  diagnostic sink/order, import-cycle and no semantic change.

### Applied process lessons

- `compatibility-baseline`: derive and preserve actual public exports.
- `diagnostic-scope-versus-readiness`: retain diagnostic boundaries rather than
  treating checker success as downstream authorization.
- `red-contract-reuse`: reuse authoritative existing typecheck assertions.
- `evaluator-state-ownership`: apply the same single-owner rule to checker
  environments and scope state.

## Process Review

- Outcome: Phase 0 design complete; no tests or production implementation
  started.
- Lesson written: no new lesson; existing lessons applied.
- Template-feedback path: none

## Phase 1 Red result

- Adjudicator approval: `LISS-0546 Phase 1 Red 承認`, received 2026-09-15.
- Added four acceptance contracts for family entrypoints, facade body removal,
  context-only dependency direction, and explicit checker callbacks.
- Production implementation was not changed. The tests are expected to fail
  until the reviewed extraction is implemented.
- Active-Red ownership is recorded in `docs/testing/active-red-tests.toml`.
- Next gate: `LISS-0546 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0546 Phase 1 Red テストレビュー承認`, received
  2026-09-15.
- The four tests were accepted as the bounded TypeChecker extraction contract.
- Next gate: `LISS-0546 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0546 Phase 2 Green / Implementation 承認`,
  received 2026-09-15.
- Added the `typechecking` package, `TypeCheckContext`, and family entrypoints
  for declarations, operators, dimensions, inference, and evolution.
- Routed compatibility through named legacy delegates while preserving
  TypeChecker environment ownership, diagnostics, type inference, and public
  helper access.
- Verification: LISS-0546 **4 passed**; focused typecheck/runtime checks
  **17 passed**; `py_compile` and `git diff --check` passed.
- Next gate: `LISS-0546 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0546 Phase 3 Refactor 承認`, received
  2026-09-15.
- Re-read confirmed explicit family entrypoints, TypeChecker-owned environment
  and diagnostics, compatibility aliases, and no reverse facade imports.
- No broad body move was made in this bounded phase. The remaining checker
  methods cross scoped environment mutation and diagnostic helpers; they remain
  named delegates for separately characterized family migrations.
- Verification: LISS-0546 **4 passed**; focused typecheck/runtime checks
  **17 passed**; `py_compile`, lifecycle, coverage-ledger, and diff checks
  passed.
- Next gate: none; final review approved 2026-09-15.

## Phase 3 final review result

- Review packet: [LISS-0546 Phase 3 final review](../collaboration/reviews/2026-09-15-liss-0546-phase3-final-review.md)
- Adjudicator approval: `LISS-0546 Phase 3 最終レビュー 承認`, received
  2026-09-15.
- Disposition: **approved and complete**. Remaining body relocation is visible
  as separately reviewable family work.

## Verification

Diagnostic goldens including neighboring positive cases, inferred annotation
snapshots, public imports, full blocking suite, Spec Verification, cycles and
diff checks.

## Process Review

- Outcome: complete; phase evidence, review, and lifecycle records are aligned.
- Lesson written: no new lesson; existing typechecker/state-ownership lessons
  were applied.
- Template-feedback path: none
- Process review: no operating-contract deviation or operational problem found.
