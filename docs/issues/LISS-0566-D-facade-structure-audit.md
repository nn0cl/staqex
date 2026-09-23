# LISS-0566-D: Evaluator facade and structure audit

## Metadata

- Local issue ID: LISS-0566-D
- Status: done — Phase 3 final review accepted
- Phase: complete
- Type: Architecture Path bounded facade/structure audit
- Priority: high
- Planning size: M
- Parent: WP-0163 / WP-0162 successor
- Depends on: LISS-0566-A, LISS-0566-B, LISS-0566-C
- Related branch: to be selected after scope approval

## [DESIGN CHECK]

### Scope and expected behavior

Audit the remaining `runtime/evaluator.py` facade after Units A–C. Determine
which responsibilities must remain in the public compatibility facade, which
are orchestration, and which are still extraction candidates. Produce a
reviewable successor map and bounded Phase 1 Red contracts before any further
source movement.

The expected result is not a smaller file by line count alone. It is an
explicit public-facade contract, one mutable-state owner, discoverable private
consumer compatibility, and a responsibility map that prevents a second
god-method or generic utility layer from being created.

### Specifications and files inspected

- `docs/specs/staqex-core-module-decomposition.md`
- `docs/work-plans/WP-0163-evaluator-stateful-successor.md`
- `docs/issues/LISS-0566-C-operator-lowering-successor.md`
- `docs/collaboration/verification-policy.md`
- `docs/collaboration/project-conventions.md`
- `docs/architecture/implementation-readiness.md`
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`
- `compiler/staqex/runtime/evaluation/evolution.py`
- `compiler/staqex/runtime/evaluation/operators.py`

### Measured current surface

- `runtime/evaluator.py`: **4,491 lines**, **110 methods**.
- Largest remaining methods: `_legacy_bind_call` **491 lines**,
  `_run_legacy_ast_body` **414 lines**, `_bind_method` **171 lines**,
  `_bind_user_fun` **145 lines**, `_bind` **143 lines**, and
  `_legacy_evaluate_value` **134 lines**.
- Existing extracted modules remain below the 1,200-line guardrail:
  `evaluation/evolution.py` and `evaluation/operators.py`.

Static consumer inventory found **105 files** under `compiler/`, `tests/`,
`scripts/`, and `examples/` that reference `runtime.evaluator` or its direct
relative import forms. This is a search-based lower bound; dynamic imports and
runtime registration still require the consumer smoke manifest.

The current internal family wrappers `evaluation/calls.py` and
`evaluation/values.py` still delegate to `_legacy_bind_call` and
`_legacy_evaluate_value`. This confirms that the next audit target is not a
new public facade, but the implementation bodies behind existing context
callbacks.

### Component boundaries, ports, and DTO candidates

- `Evaluator` remains the sole mutable runtime-state owner during the audit.
- `evaluation/compatibility.py` remains a thin private-hook bridge; it is not a
  new policy or execution authority.
- Candidate responsibility families to classify, not yet approve for movement:
  legacy AST execution/body traversal, call binding and frame ownership,
  classical value evaluation, declaration/instance construction, finiteization,
  observation/measurement, and canonical runtime-plan dispatch.
- Candidate DTO/context boundaries must be derived from the actual call graph;
  no speculative `utils.py`, generic service locator, or copied environment
  maps are permitted.
- No new external port, provider adapter, network, credential, persistence, or
  QPU boundary is introduced by this audit.

### Applicable constraints

1. Preserve public imports, private consumer hooks, diagnostics, ordering,
   serialization, deterministic local execution, and QASM output.
2. Preserve Scientific Semantic IR as the compile-owned semantic authority.
3. Do not infer business or physics policy in compatibility code.
4. Inventory dynamic/private consumers before proposing any body movement.
5. Every proposed successor unit must have its own Issue, Red contracts,
   implementation approval, and final review.
6. A facade-size reduction is evidence only when ownership and consumer
   compatibility are independently demonstrated.

### Decisions, assumptions, and unresolved ambiguities

- Decision for intake: Unit D is an audit and decomposition-design boundary;
  no implementation or method extraction is authorized by this note.
- Assumption: `Evaluator` may remain a large orchestration facade temporarily
  while the call graph and public/private surface are measured.
- Open decision: whether `_legacy_bind_call` and `_run_legacy_ast_body` belong
  in one successor unit or must be split by frame, statement, and terminal
  execution responsibilities.
- Open decision: whether classical value evaluation is coupled tightly enough
  to call binding to share a context, or requires separate successor units.
- Open decision: which private aliases can be retired after consumer evidence
  and a typed migration decision; no retirement is assumed here.

### Proposed first bounded successor

The first candidate is a call-binding/frame slice behind
`evaluation/calls.py`, limited to dispatch classification and frame/receiver
boundary contracts. It must not absorb the entire 491-line
`_legacy_bind_call`, `_bind_method`, or `_bind_user_fun` bodies in one change.
The Phase 1 Red contract should cover function/method/object dispatch,
receiver restoration on success and error, local-map non-retention, diagnostic
ordering, private-hook compatibility, and unchanged fixed-seed local results.
The exact split and local Issue ID remain an acceptance decision after the
Phase 0 artifact review.

### Included and omitted AI context

Included: current evaluator AST/call graph, extracted Units A–C, compatibility
assignments, project structure/verification rules, public/private consumer
inventory, and deterministic baseline requirements.

Omitted: provider SDKs, live QPU credentials/network, Rust implementation,
unrelated parser/typechecker decomposition, new language semantics, and broad
historical ADR bodies not referenced by the current canonical specification.

### Task routing

- Path: Architecture Path for facade/state/compatibility boundary design.
- Design and inventory: host agent with deterministic AST/import tooling.
- Review: `same_context` under current routing; this is weaker than
  `separate_context` and requires typed Adjudicator approval.
- Implementation: not selected; future units must select host or a separately
  approved implementation route.

### Verification plan

Phase 0 design evidence must include:

- AST method/line inventory with responsibility classification;
- private/public import and dynamic consumer inventory;
- compatibility alias and re-export manifest;
- import-cycle and dependency-direction audit;
- structure-budget report for `Evaluator` and candidate successor modules;
- unchanged public/runtime/QASM/diagnostic baseline plan;
- proposed Phase 1 Red contracts for the first bounded successor unit.

No production implementation, test lifecycle entry, or facade retirement is
authorized until this design is accepted and the first successor's Phase 1
Red approval is explicit.

## Phase 0 design evidence

- AST inventory: **110 Evaluator methods**, with the six largest stateful
  bodies measured above.
- Static consumer inventory: **105** files in source/test/tool/example roots;
  dynamic loading remains an explicit follow-up check.
- Compatibility inventory: `evaluation/compatibility.py` installs evolution
  and operator hooks; `calls.py` and `values.py` remain thin delegation
  boundaries; observation, dynamic-lane, and orchestration families are also
  installed at the facade.
- Dependency direction: extracted evaluation modules reference the context
  protocol and domain/runtime DTOs; no extracted Unit A–C module imports the
  public `runtime.evaluator` facade.
- Structure finding: `_run_legacy_ast_body` is a cross-family dispatcher and
  must not be moved wholesale. `_legacy_bind_call` is the first candidate for
  bounded call/frame decomposition, but its fan-out requires a narrower Red
  contract before implementation.
- Deterministic checks: document lifecycle and `git diff --check` passed;
  no production tests were changed in this intake.

## Phase 0 acceptance

Accepted on 2026-09-19:
`WP-0163 / LISS-0566-D Phase 0 acceptance 承認`.

The audit boundary, measured surface, consumer inventory, single-state-owner
constraint, compatibility role, and proposed first call-binding/frame slice
are accepted as the Phase 1 Red input. This acceptance authorizes test/design
work only; it does not authorize production implementation, facade retirement,
or private-alias removal.

Next approval:
`WP-0163 / LISS-0566-D Phase 1 Red 承認`.

## Phase 1 Red

Approved on 2026-09-19:
`WP-0163 / LISS-0566-D Phase 1 Red 承認`.

Added `tests/test_liss_0566_unit_d_red.py` with eight bounded call-binding and
frame contracts. The suite intentionally expects structural failures for the
successor entrypoints, legacy body removal, and compatibility wiring while
keeping context, no-facade dependency, and existing local call behavior
visible. The issue-linked Active-Red entry is registered in
`docs/testing/active-red-tests.toml`.

Expected pre-Green result: **4 failed, 4 passed**. No production source or
reviewed assertion was changed. Phase 1 test review is required before Green.

Next approval:
`WP-0163 / LISS-0566-D Phase 1 Red テストレビュー承認`.

## Process lessons applied

- `evaluator-state-ownership`: retain one mutable state owner and derive
  contexts from the actual call graph.
- `private-consumer-inventory`: include underscore-prefixed and dynamic
  consumers before moving any remaining body.
- `decomposition-boundary`: name retained compatibility bridges explicitly;
  do not call the audit a completed migration.
- `quantitative-traceability`: label method/line counts and derive them from
  deterministic source inspection.

## Requested decision

Requested approval type: **Architecture Path scope/design approval** for the
Unit D audit only. This approval must not be interpreted as Phase 1 Red,
implementation, facade retirement, or commit/push/merge permission.

## Phase 1 Red test review

Review packet: [LISS-0566-D Phase 1 Red review](../collaboration/reviews/2026-09-19-liss-0566-d-phase1-red-review.md).

Approved on 2026-09-19:
`WP-0163 / LISS-0566-D Phase 1 Red テストレビュー承認`.

The eight contracts were accepted. The focused run reports **4 failed, 4
passed** with the expected four structural gaps; the four passing contracts
cover context/frame callbacks, no public-facade dependency, function-call
behavior, and method-call behavior. Active-Red ownership is explicit and
production implementation has not started.

Next approval:
`WP-0163 / LISS-0566-D Phase 2 Green / Implementation 承認`.

## Phase 2 Green

Approved on 2026-09-19:
`WP-0163 / LISS-0566-D Phase 2 Green / Implementation 承認`.

Moved the call-binding implementation behind the reviewed successor boundary
in `runtime/evaluation/calls.py`. The module now owns `bind_call` plus the
explicit `resolve_call_target`, `bind_function_call`, and `bind_method_call`
entrypoints. `Evaluator` remains the sole mutable state owner and exposes only
the required context callback for partial-value construction; the compatibility
bridge preserves the existing `_bind_call` identity for private consumers.
The cross-family `_run_legacy_ast_body` dispatcher was intentionally retained.

Verification: Unit D focused **8 passed**, adjacent call/evolution/operator
regressions **42 passed**, targeted extracted-call runtime regressions **19
passed**, and the full blocking pytest suite **2,155 passed**. The measured
source surface is now `runtime/evaluator.py` **4,003 lines** and
`runtime/evaluation/calls.py` **529 lines**. The LISS-0566-D Active-Red entry
was removed after Green.

No Semantic IR, QASM projection, parser/typechecker, provider SDK, network,
credential, or live-QPU behavior changed.

Next approval:
`WP-0163 / LISS-0566-D Phase 3 Refactor 承認`.

## Phase 3 Refactor

Approved on 2026-09-19:
`LISS-0566-D Phase 3 Refactor 承認`.

Separated call compatibility registration from evolution compatibility, made
the call service consume explicit environment/frame callbacks from
`EvaluatorContext`, and removed the obsolete `_legacy_bind_call` protocol
contract. The private `_bind_call` alias remains deliberately available for
existing consumers; its retirement is outside this phase. No test assertion,
runtime behavior, diagnostic ordering, or target artifact behavior changed.

The existing 105-file static consumer inventory remains the compatibility
baseline. The extracted call module remains below the 1,200-line structure
guardrail, and `Evaluator` remains the only mutable runtime-state owner.

Verification: focused Unit D/adjacent **42 passed**, targeted runtime
regressions **19 passed**, full blocking pytest **2,155 passed**, compileall,
Spec Verification **161/161**, lifecycle, document, coverage-ledger, and diff
checks passed.

Review packet: [LISS-0566-D Phase 3 review](../collaboration/reviews/2026-09-19-liss-0566-d-phase3-review.md).

Next approval:
`WP-0163 / LISS-0566-D Phase 3 最終レビュー 承認`.

## Phase 3 final review

Approved on 2026-09-19:
`LISS-0566-D Phase 3 最終レビュー 承認`.

The review found no blocker across compatibility wiring, context/state
ownership, private-consumer preservation, structure budget, or behavior
preservation. The issue is complete. The `_bind_call` private compatibility
alias remains intentionally documented; retirement is a separate future
consumer decision.

Process review: no operating-contract deviation or operational problem found.
