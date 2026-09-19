# LISS-0567: Evaluator classical/value and frame successor

## Metadata

- Local issue ID: LISS-0567
- Status: done — Phase 3 final review accepted 2026-09-19
- Phase: done
- Type: Architecture Path bounded structural decomposition
- Planning size: XL
- Parent: WP-0164
- Depends on: WP-0163 / LISS-0566-A–D complete
- Blocks: none

## [DESIGN CHECK]

### Scope and expected behavior

Define a bounded successor for the remaining classical/value and invocation
frame responsibilities in `runtime/evaluator.py`. The result must reduce
facade responsibility while preserving language meaning, frame lifetime,
receiver semantics, diagnostics, fixed-seed local execution, and public
compatibility.

### Specifications and files inspected

- `docs/specs/staqex-core-module-decomposition.md`
- `docs/work-plans/WP-0163-evaluator-stateful-successor.md`
- `docs/work-plans/WP-0164-evaluator-classical-frame-successor.md`
- `docs/collaboration/verification-policy.md`
- `docs/architecture/implementation-readiness.md`
- `docs/collaboration/project-conventions.md`
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/calls.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/values.py`
- `tests/test_liss_0413_method_fn_local_operator_resolution_red.py`
- `tests/test_liss_0508_free_function_struct_argument_binding_red.py`

### Component boundaries, ports, and DTO candidates

- `Evaluator` remains the mutable state owner; no new port or adapter is
  required.
- `frames.py` receives explicit callbacks for receiver, local maps, frame
  units, nested binding, and trace-out cleanup.
- `classical.py` receives explicit environment/value/constructor callbacks and
  returns existing runtime DTOs (`ClassInstance`, `StructValue`, `PartialValue`)
  without creating new semantic authority.
- Existing `EvaluatorContext` is extended only with callbacks proven necessary
  by the Phase 0 call graph; no broad service-locator or copied environment is
  allowed.

### Applicable constraints

- no implementation before reviewed Phase 1 Red;
- no movement of `_run_legacy_ast_body`, `_bind`, or `_bind_names` as whole
  dispatchers;
- no assertion, fixture, diagnostic, QASM, or public-import weakening;
- new modules normally remain below 1,200 lines;
- private compatibility aliases remain until separately retired.

### Decisions, assumptions, and unresolved ambiguities

- Decision: split frame lifetime from classical expression/value policy rather
  than create one broad `classical.py` god module.
- Assumption: the current call-binding implementation remains the entrypoint;
  this issue extracts its callback targets, not a second call classifier.
- Ambiguity: exact helper placement between `frames.py` and `classical.py` is
  unresolved until the Phase 0 call graph and mutation audit are complete.
- Out of scope: scientific/continuous families and parser/typechecker work.

### Included and omitted AI context

- Included: evaluator methods listed in WP-0164, `calls.py`, context protocol,
  accepted decomposition spec, private-consumer tests, and relevant fixtures.
- Omitted: provider SDKs, credentials, unrelated scientific adapters, full
  repository exports, and historical WP-0162 records except for traceability.

### Task routing

- Architecture/design and dependency inventory: host agent with deterministic
  `rg`, AST, import, and test tools.
- Phase 1–3 implementation: host agent under typed Adjudicator approval and
  current runtime routing.
- Review: `same_context` unless routing is changed by an explicit decision.

### Input/output evidence contract

No external AI/model output or provider data is involved. Design output is
reviewable Markdown with measured method/line counts, consumer paths, allowed
files, ambiguity boundaries, and deterministic verification commands.

### Verification plan

Phase 0 must produce the mutation/state map, private consumer inventory, import
cycle audit, candidate module line budget, and exact Phase 1 Red acceptance
nodes. Later phases must run classical/frame characterization, adjacent
regression, full pytest, Spec Verification, compileall, lifecycle, coverage,
and diff checks.

## Requested decision

Requested approval type: **Architecture Path Phase 0 scope/design approval**.
This approval authorizes only the Phase 0 call-graph and boundary inventory;
it does not authorize Phase 1 tests, implementation, public API changes, or
facade retirement.

## Phase 0 evidence

The inventory confirms two cohesive extraction families:

- `frames.py`: `_bind_method`, `_bind_user_fun`,
  `_eval_classical_user_fun_value`, `_exec_assign`, frame-unit lifetime,
  receiver restoration, and dead-coordinate cleanup.
- `classical.py`: `_eval_classical_call`,
  `_eval_classical_method_call`, `_construct_instance`, `_construct_struct`,
  `_eval_value_with_unit`, `_legacy_evaluate_value`, and receiver/attribute
  value resolution.

`Evaluator` remains the only owner of runtime maps and receiver/frame state.
`_run_legacy_ast_body`, `_bind`, and `_bind_names` remain cross-family
dispatchers and are explicitly excluded from wholesale movement. Existing
extracted modules use callback/context boundaries and do not import the public
facade.

The allowed Phase 1 paths are limited to the two candidate modules,
`evaluator.py`, `context.py`, `compatibility.py`, the new bounded Red test, and
the linked issue/WP/trace/review documents. Parser, typechecker, Semantic IR,
QASM, provider, network, and historical WP-0162 files are excluded.

The proposed Red contract covers module ownership, no-facade imports, context
callback completeness, private alias preservation, receiver/frame restoration,
and existing classical/function/method/struct/partial/unit behavior.

## Phase 0 acceptance

Requested approval type: **Architecture Path Phase 0 acceptance**.

`WP-0164 / LISS-0567 Architecture Path Phase 0 acceptance 承認` is required
before adding the Phase 1 Red test file. Production implementation remains
unauthorized.

## Phase 0 acceptance

Accepted on 2026-09-19:
`WP-0164 / LISS-0567 Architecture Path Phase 0 acceptance 承認`.

The accepted scope is the two-module classical/frame boundary, the single
mutable `Evaluator` owner, the retained cross-family dispatchers, the exact
Phase 1 allowed paths, and the proposed structural/characterization contract.
No production source or test file was changed by this acceptance.

Next approval:
`WP-0164 / LISS-0567 Phase 1 Red 承認`.

## Phase 1 Red

Approved on 2026-09-19:
`WP-0164 / LISS-0567 Phase 1 Red 承認`.

Added `tests/test_liss_0567_classical_frame_red.py` with eight contracts: five
structural successor/callback/ownership gaps and three existing function,
method, and struct-return characterization cases. The issue-linked Active-Red
entry is registered in `docs/testing/active-red-tests.toml`.

Expected pre-Green result: **5 failed, 3 passed**. No production source or
reviewed assertion was changed. Phase 1 test review is required before Green.

Next approval:
`WP-0164 / LISS-0567 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

Accepted on 2026-09-19:
`WP-0164 / LISS-0567 Phase 1 Red テストレビュー承認`.

Review record:
`docs/collaboration/reviews/2026-09-19-liss-0567-phase1-red-review.md`.
The eight contracts are accepted as scoped: five intended structural failures
and three passing characterization cases. The exact focused result is
**5 failed, 3 passed**; lifecycle, document-lifecycle, coverage-ledger, and
diff checks passed. No production source or assertion was weakened.

## Phase 2 Green / Implementation

Approved and implemented on 2026-09-19:
`WP-0164 / LISS-0567 Phase 2 Green / Implementation 承認`.

Implemented the bounded successor wiring:

- `evaluation/frames.py` exposes method/function frame entrypoints and frame
  restoration through `EvaluatorContext` callbacks.
- `evaluation/classical.py` exposes classical value and class/struct
  construction entrypoints.
- `evaluation/compatibility.py` installs the frame/classical compatibility
  mappings; legacy bodies remain private `_legacy_*` callbacks.
- `Evaluator` remains the only mutable runtime-state owner.

Verification passed: the LISS-0567 and adjacent evaluator suites produced
**15 passed**, full pytest produced **2,163 passed**, and compileall,
lifecycle, document, coverage-ledger, and diff checks passed. The Active-Red
entry was retired. No new language behavior or external integration was added.

Next approval:
`WP-0164 / LISS-0567 Phase 3 Refactor 承認`.

## Phase 3 Refactor

Approved and completed on 2026-09-19:
`WP-0164 / LISS-0567 Phase 3 Refactor 承認`.

The refactor made the explicit frame/classical callback signatures and
compatibility grouping readable while preserving the Phase 2 implementation.
The successor modules still have no mutable evaluator-state copies or public
facade imports. No test assertion, fixture, language behavior, provider
integration, or public API was changed.

Verification after the refactor: focused and adjacent suites **15 passed**;
full pytest **2,163 passed**; compileall, test lifecycle, document lifecycle,
coverage-ledger consistency, and `git diff --check` passed.

Next approval:
`WP-0164 / LISS-0567 Phase 3 最終レビュー 承認`.

## Phase 3 final review

Accepted on 2026-09-19:
`WP-0164 / LISS-0567 Phase 3 最終レビュー 承認`.

Review packet:
`docs/collaboration/reviews/2026-09-19-liss-0567-phase3-final-review.md`.
The final review confirms the accepted boundaries, compatibility surface,
single mutable-state owner, and structural budget. Focused/adjacent tests
passed (**15**), full pytest passed (**2,163**), and compileall, lifecycle,
document, coverage-ledger, and diff checks passed.

Process review: no operating-contract deviation or operational problem found.

LISS-0567 is complete. Further evaluator body migration or private alias
retirement requires a new Issue/WP and approval.
