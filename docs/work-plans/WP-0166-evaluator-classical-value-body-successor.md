# WP-0166: Evaluator classical value body successor

| Field | Value |
|---|---|
| Status | done — Phase 3 final review accepted |
| Size | XL |
| Parent | WP-0165 / completed LISS-0568 successor |
| Scope approval | accepted 2026-09-19 — Architecture Path scope |
| Implementation permission | none |
| Canonical specification | [Core module decomposition](../specs/staqex-core-module-decomposition.md) |
| Candidate issues | LISS-0569 |

## [DESIGN CHECK]

### Scope and expected behavior

Move the remaining classical value-evaluation body from
`runtime/evaluator.py` into the existing `evaluation/classical.py` successor.
Preserve literals, attributes, constructors, calls, `when`, binders, units,
diagnostics, receiver semantics, fixed-seed local results, public imports, and
the single `Evaluator` mutable-state owner. This is structural extraction only;
it adds no syntax, semantics, or new classical behavior.

### Current evidence

- `evaluator.py`: **3,790 lines / 116 class methods** after extraction.
- `evaluation/classical.py`: **425 lines** and below the 1,200-line guardrail.
- Recursive value dispatch, unit conversion, attribute/receiver lookup, and
  unit-aware arithmetic now live in the classical successor module.
- `Evaluator` retains state/DTO ownership, cross-family callbacks, and
  compatibility aliases; no duplicate legacy value body remains in its class
  body.
- `evaluation/values.py`, `evaluation/evolution.py`, evaluator orchestration,
  and direct classical tests are the known consumers.

### Phase 0 inventory and accepted boundary

The accepted call graph is deliberately explicit:

| Caller or service | Current edge | Phase 2 destination |
|---|---|---|
| `evaluation/values.py` | `evaluate_value -> context._legacy_evaluate_value` | `classical.evaluate_value` owns the recursive dispatch |
| `_legacy_evaluate_value` | literals/variables/attributes/`when`/constructors/calls/OpBinder | same branches move into `evaluation/classical.py` |
| value dispatch | `_eval_value_with_unit`, `_eval_unit_convert` | classical facade callbacks with the same return/error contracts |
| classical calls | `_eval_classical_call` | remains an evaluator callback; no call-family migration here |
| classical binders | `_eval_classical_op_binder` | remains an evaluator callback; no binder-family migration here |
| `evaluation/evolution.py` | `context._eval_value_with_unit` | callback remains available through the context protocol |
| `evaluation/calls.py`, `operators.py` | `context._resolve_receiver_instance` | receiver lookup remains a classical callback |

The mutable-state and DTO inventory is closed as follows:

- Read-only environments are obtained through `_value_environment`,
  `_object_environment`, `_scalar_environment`, `_class_environment`,
  `_struct_environment`, and `_enum_environment`; the successor never stores
  copies of these mappings.
- Unit reads remain evaluator-owned through `scalar_units`, `_frame_units`,
  and `_call_local_units`, exposed only by the value/unit callback boundary.
- `objects`, `scalars`, `_this`, frame state, `classes`, `structs`, and `enums`
  remain owned by the one live `Evaluator` instance.
- `ClassInstance`, `StructValue`, `EnumValue`, and `PartialValue` remain
  evaluator-owned runtime DTOs. The extracted module may inspect and return
  them through callbacks but does not define replacements.
- Constructor and assignment mutations remain evaluator callbacks
  (`_construct_instance`, `_construct_struct`, `_store_runtime_object`); the
  classical module does not mutate evaluator maps directly.

The import/consumer audit found no public facade import in the successor
modules. `classical.py` may depend on `context.py`, AST/value types, dimension
helpers, and error/pure-operation helpers only. It must not import
`runtime.evaluator`, instantiate `Evaluator`, or access `self.*` state.

### Exact allowed paths for Phase 1–3

- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/classical.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`
- `compiler/staqex/runtime/evaluation/values.py`
- `compiler/staqex/runtime/evaluation/evolution.py`
- `tests/test_liss_0569_classical_value_red.py`
- `docs/testing/active-red-tests.toml`
- this WP, its linked Issue/Trace, and the LISS-0569 review packet

No other path is authorized without a new scope decision.

### Proposed component boundaries

| Component | Owns | Must not own |
|---|---|---|
| `evaluation/classical.py` | recursive value dispatch, unit-aware values, unit conversion, attribute/receiver reads, constructor routing | evaluator-owned maps, DTO definitions, Joint policy, continuous port logic, semantic authority |
| `evaluation/context.py` | narrow callbacks for environments, DTO predicates, nested evaluation, classical calls/binders, unit helpers, and receiver state | copied mutable runtime state |
| `evaluation/values.py` | stable value-service entrypoint and compatibility delegation | a second value implementation |
| `evaluator.py` | mutable state, DTO identity, cross-family dispatch, classical call/binder compatibility hooks | duplicate value body after migration |

### State and authority boundary

- `Evaluator` remains the sole owner of `objects`, `scalars`, units,
  classes/structs/enums, `_this`, frame state, injected ports, and `Joint`.
- `ClassInstance`, `StructValue`, `EnumValue`, and `PartialValue` remain
  evaluator-owned runtime DTOs unless Phase 0 proves a pure DTO move is
  necessary; such a move is out of scope by default.
- Scientific Semantic IR and continuous/provider boundaries remain outside
  this value evaluator.
- Extracted code must not import `runtime.evaluator`, construct `Evaluator`,
  or retain copied maps.

### Applicable constraints

- No implementation before reviewed Red contracts and Phase 2 approval.
- No parser, typechecker, Semantic IR, QASM, provider, network, credential,
  Rust, or public API retirement changes.
- Preserve diagnostic code/order, unit conversion, receiver restoration,
  constructor semantics, and classical OpBinder behavior.
- `classical.py` remains below the 1,200-line guardrail after body migration.
- Existing private aliases remain until a separate consumer decision.

### Decisions and unresolved ambiguities

- Decision: migrate the value body into the existing `classical.py`; do not
  create another generic value utility module.
- Decision: keep `_eval_classical_call` and `_eval_classical_op_binder` as
  explicit evaluator callbacks initially because they cross call/binder
  families and have their own consumer contracts.
- Decision: Phase 0 fixes the callback families as value environment, unit
  lookup, receiver lookup, constructor routing, nested evaluation, classical
  call, and classical OpBinder. Exact method names must remain narrow and
  protocol-declared; importing the facade is not an allowed shortcut.
- Ambiguity: `_apply_op`, `_pat_match`, and dimension helpers remain in the
  facade unless a mechanical pure-helper move is proven within the allowed
  paths.

### Included and omitted AI context

- Included: WP-0165/LISS-0568 final artifacts, decomposition spec,
  `evaluator.py` value/unit/attribute methods, `classical.py`, `values.py`,
  `context.py`, `compatibility.py`, `evolution.py`, and classical tests.
- Omitted: continuous implementation (already completed), parser/typechecker,
  Semantic IR, QASM/provider code, live QPU, and historical WP-0162 records.

### Task routing

- Phase 0: host agent using deterministic source/import/AST/search tools.
- Phase 1–3: host agent after typed approvals.
- Review: same-context under current runtime routing.

### Verification plan

- Phase 0: value call graph, mutation/DTO inventory, consumer/import manifest,
  callback boundary, exact allowed paths — completed in this acceptance.
- Phase 1 Red: classical entrypoints, no-facade/state-owner, callback/wiring,
  and literal/attribute/unit/constructor/binder characterization contracts.
- Phase 2 Green: body migration plus focused classical/unit/constructor suites,
  nearest evaluator regressions, and full pytest.
- Phase 3: import/compatibility cleanup, full pytest, compileall, Spec
  Verification, lifecycle, coverage-ledger, and diff checks.

## Phase 0 gate

Phase 0 is accepted for the bounded inventory and paths above. It does not
authorize production extraction or public API changes.

## Phase 1 Red

- Approval: `WP-0166 / LISS-0569 Phase 1 Red 承認` (2026-09-19).
- Added: `tests/test_liss_0569_classical_value_red.py`.
- Added the LISS-0569 active-Red manifest entry.
- Contract: five structural failures for the not-yet-migrated successor
  boundary and three passing characterization tests for literals,
  attributes/constructors/units, and classical binders.
- Production implementation permission: none; the active-Red entry remains
  until Phase 2 Green passes the contracts.
- Next approval:
  `WP-0166 / LISS-0569 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval: `WP-0166 / LISS-0569 Phase 1 Red テストレビュー承認`
  (2026-09-19).
- Review packet: `docs/collaboration/reviews/2026-09-19-liss-0569-phase1-red-review.md`.
- Result: **accepted**; five intended structural failures and three passing
  characterization cases were reproduced. No production implementation was
  added.
- Active-Red ownership remains with LISS-0569 until Phase 2 Green.
- Next approval:
  `WP-0166 / LISS-0569 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0166 / LISS-0569 Phase 2 Green / Implementation 承認`
  (2026-09-19).
- Moved recursive value dispatch, unit conversion, unit-aware arithmetic,
  attribute/receiver lookup, and constructor routing into
  `evaluation/classical.py`.
- Added narrow context callbacks for live unit lookup, enum construction, and
  cross-family classical call/binder delegation. `Evaluator` remains the
  mutable state and DTO owner.
- Retained private compatibility aliases through the compatibility installer;
  no second value implementation remains in the `Evaluator` class body.
- Active-Red ownership was retired after all eight approved contracts passed.
- Focused/adjacent: **38 passed**. Full pytest: **2,179 passed**.
- Phase 3 risk: readability cleanup is still required for dense mechanical
  helper formatting and compatibility-surface review.
- Next approval:
  `WP-0166 / LISS-0569 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0166 / LISS-0569 Phase 3 Refactor 承認` (2026-09-20).
- Refactored `evaluation/classical.py` into named helpers for dispatch,
  attributes, calls, units, and receiver handling without changing contracts.
- Review packet:
  `docs/collaboration/reviews/2026-09-20-liss-0569-phase3-review.md`.
- Verification: focused/adjacent **38 passed**, full pytest **2,179 passed**,
  compileall, lifecycle, coverage-ledger, and diff checks passed.
- Structural budget: `evaluator.py` **3,790 lines**;
  `classical.py` **425 lines**, below the 1,200-line guardrail.
- No active-Red entries remain. Final review is still required before marking
  the WP and Issue done.
- Next approval:
  `WP-0166 / LISS-0569 Phase 3 最終レビュー 承認`.

## Phase 3 final review

- Approval: `WP-0166 / LISS-0569 Phase 3 最終レビュー 承認`
  (2026-09-20).
- Review packet:
  `docs/collaboration/reviews/2026-09-20-liss-0569-phase3-review.md`.
- Result: accepted. No behavior, diagnostic, unit, receiver, import, or
  state-ownership regression was found within the approved scope.
- Verification: focused/adjacent **38 passed**, full pytest **2,179 passed**,
  compileall, lifecycle, coverage-ledger, and diff checks passed.
- Process review: no operating-contract deviation or operational problem
  found.
- Status: WP-0166 complete; LISS-0569 complete.
