# Evaluator Classical Call Evaluation Specification

| Field | Value |
|---|---|
| Status | Phase 3 final review approved 2026-09-24 — commit verification pending |
| Scope | LISS-0577 / WP-0170 |
| Source authority | [Core module decomposition](staqex-core-module-decomposition.md) |

## Purpose

Define and implement a behavior-preserving successor boundary for evaluating
pure classical function and method calls in runtime value contexts. This
successor extracts the remaining active method bodies identified after
LISS-0576 without changing value semantics.

## Candidate responsibility

The candidate source family is `Evaluator._eval_classical_call`,
`_eval_classical_method_call`, `_eval_classical_user_fun`, and
`_eval_classical_user_fun_value` (259 source lines on the LISS-0576 base).
The accepted destination is the focused
`runtime/evaluation/classical_calls.py` successor; Phase 0 accepted its
cohesion and callback boundaries.

Preserve free-function and method result eligibility, nested call frames,
object/scalar argument lookup and shadowing, unit propagation, intermediate
assignment behavior, method receiver binding, struct-valued returns, and exact
diagnostics/error and restoration behavior. Call evaluation must remain a
classical value operation; it must not create a `Joint` or alter state-lane
semantics.

## Ownership and dependencies

`Evaluator` remains the sole owner of mutable runtime maps, runtime DTO
identity, receiver state, frame-unit state, and call-local-unit state. The
successor may observe or mutate that live state only through a narrow explicit
context contract; it must not copy maps, import or instantiate
`runtime.evaluator`, or move state ownership. Do not enlarge `classical.py`,
`calls.py`, or the shared `EvaluatorContext` protocol without Phase 0 evidence
and an explicit boundary rationale.

Required integration consumers found by initial search:

- `evaluation/classical.py` dispatches value-context `Call` nodes through
  `_evaluate_classical_call`.
- `evaluation/execution.py` invokes `_eval_classical_user_fun_value` when
  binding eligible classical-returning function results.
- `Evaluator._bind` retains existing runtime compatibility entrypoints.

### Phase 0 consumer and behavior inventory

| Consumer/contract | Current path | Existing evidence to preserve |
|---|---|---|
| Classical `Call` in value expressions | `evaluation/classical.py::_evaluate_call` -> `Evaluator._evaluate_classical_call` -> `_eval_classical_call` | `test_liss_0273_classical_call_in_expr_red.py` covers free-function and method values in expressions and rejects state-forming calls |
| Classical-returning free function binding | `evaluation/execution.py` -> `_eval_classical_user_fun_value` | `test_liss_0292_typefirst_freefn_args_red.py`, `test_liss_0294_nested_freefn_args_red.py`, `test_liss_0353_struct_returning_free_function_execution_path_red.py` |
| Classical function arguments and nested scopes | `Evaluator` maps and call-local frames | LISS-0292/0294 cover Type-First objects, nested calls, field projection, and caller-local shadowing |
| Scalar math calls | `_eval_classical_call` dispatches `stdlib.math_ops` | `test_liss_0356_math_ops_classical_scalar_support_red.py` |
| Class method receiver and nested attribute resolution | `_eval_classical_method_call` -> receiver/class/function environments | `test_liss_0358_nested_attr_receiver_dispatch_red.py`, `test_namespace_and_class_methods.py`, and LISS-0273 |
| Unit-bearing field/function values and downstream use | `_eval_value_with_unit`, frame/call unit maps | `test_liss0254_type_first_field_units_red.py`, `test_classical_float_operator_evolve_binding_red.py` |
| Struct returns and nested returned values | `_eval_classical_user_fun_value` | `test_liss_0353_struct_returning_free_function_execution_path_red.py` |
| Adjacent stateful call/frame path | `evaluation/calls.py`, `evaluation/frames.py` | `test_liss_0566_unit_d_red.py`, `test_liss_0567_classical_frame_red.py`; these are adjacent regression, not substitutes for classical-value coverage |

Static search found no direct test imports or name references to the four
private methods. In-repository runtime consumers are the three paths above;
dynamic/reflection-based consumers cannot be ruled out by search. Preserve the
existing private evaluator names as compatibility entrypoints and test their
installed callable identity.

The exact source-state dependencies are live function, class, struct, object,
scalar, and scalar-unit environments; current receiver; frame-unit and
call-local-unit frames; nested value evaluation; receiver resolution; and
assignment execution. The method bodies restore receiver/frame/call-unit state
in `finally` paths. No new runtime DTO is needed. Failure-path restoration
needs an explicit characterization because the existing tests do not directly
assert it for the classical-value call path.

### Phase 0 callback and file-boundary decision

Architecture approval: `LISS-0577 Architecture approval 承認` (2026-09-24).
Phase 0 acceptance: `LISS-0577 Phase 0 acceptance 承認` (2026-09-24).
The accepted boundary is the four-method classical-call family, separate from
state-producing call binding and classical operator expression/projection.
`Evaluator` remains the single state and DTO owner.

Phase 0 recommendation: implement the successor functions in
`evaluation/classical_calls.py` with a small module-local `ClassicalCallContext`
Protocol that lists only live environment references and required callbacks.
Keep `evaluation/context.py`, `classical.py`, and `execution.py` unchanged.
Preserve existing Evaluator method names by installing the successor functions
through `evaluation/compatibility.py`. Add only narrowly scoped Evaluator
accessors `_call_local_units_environment()` and
`_set_call_local_units_environment(value)` for optional call-unit-frame
save/restore; do not expose `_call_local_units` as a copied map. If consumer
characterization shows that this contract cannot be honored without broader
file changes, stop and request a revised scope before implementation.

Proposed characterization additions are limited to the accepted gap: receiver,
frame-unit, and call-local-unit restoration after nested classical call success
and failure, plus compatibility-hook identity. Existing behavior suites above
remain unchanged and blocking.

### Phase 1 acceptance scenarios

1. **Given** a classical function or method call in a value context, **when**
   the evaluator processes it, **then** existing scalar, unit, nested-call,
   receiver, assignment, and struct-return behavior remains observable through
   the existing evaluator entrypoints.
2. **Given** the classical-call bodies are extracted, **when** modules are
   inspected, **then** `classical_calls.py` owns the four bodies, has no
   evaluator-facade dependency or second mutable-state owner, and the existing
   evaluator hooks resolve to the successor functions.
3. **Given** an outer receiver, frame-unit map, and call-local-unit map, **when**
   a nested classical function succeeds or its value evaluation raises,
   **then** all three prior values are restored, preserving map identity.

### Exact phase paths

- Phase 1 Red: `tests/test_liss_0577_classical_calls_red.py`,
  `docs/testing/active-red-tests.toml`, this Issue, WP-0170, this specification,
  the LISS-0577 trace, and the required review record.
- Phase 2 Green: `compiler/staqex/runtime/evaluator.py`,
  `compiler/staqex/runtime/evaluation/classical_calls.py` (new),
  `compiler/staqex/runtime/evaluation/compatibility.py`, the Phase 1 test and
  lifecycle entry, and LISS-0577/WP-0170/spec/trace evidence. Existing
  `evaluation/classical.py`, `execution.py`, `context.py`, calls/frames modules,
  and unrelated tests are not editable without a new decision.
- Phase 3: the same production and tests paths; documentation/review evidence
  remains limited to LISS-0577, WP-0170, this specification, trace, and review
  record.

Phase 0, Phase 1 test acceptance, Phase 2 Green/Implementation approval, Phase
2 Green acceptance, and Phase 3 Refactor approval were recorded 2026-09-24.
The four bodies are extracted; Phase 3 consolidated repeated class-method
resolution and return-expression selection without changing test assertions
or behavior. Focused, consumer, adjacent, and all-blocking tests pass, and the
active-Red exclusion was removed. The project's existing `.venv` was reused;
no environment was created or modified. Final Adjudicator review, including
acceptance of the bounded 324-line structure disposition, was approved
2026-09-24. Commit-specific blocking verification remains pending.

## In scope

- The four candidate classical call evaluation bodies and their narrow
  context/compatibility wiring.
- Characterization of nested free-function calls, object and scalar arguments,
  shadowing, units, method receivers, assignments, struct returns, and failure
  restoration.
- Actual consumers, private imports, import smoke, and adjacent regression.

## Out of scope

- Classical operator binders, operator-expression evaluation and projection.
- Runtime-plan eligibility/execution, `when`, tensor/foreach dispatch, and
  continuous-field behavior.
- Parser/typechecker, language syntax or semantics, QPU/QASM/provider behavior,
  public API retirement, and unrelated cleanup.

## Acceptance boundary

The boundary and Phase 1 Red contract are accepted, and Phase 2 implementation
approval was explicit. Tests preserve behavior rather than merely prove source
ownership. Phase 2 verification separately reports focused, consumer,
adjacent, and all-blocking results; the current evidence is against a dirty
worktree at the recorded base SHA and must be rerun against the final commit.
