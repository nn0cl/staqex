# Evaluator Classical Operator-expression Evaluation Specification

| Field | Value |
|---|---|
| Status | Phase 0 through Phase 3 accepted; final commit verification pending |
| Scope | WP-0171 / LISS-0578 |
| Source authority | [Core module decomposition](staqex-core-module-decomposition.md) |

## Purpose

Specify a behavior-preserving decomposition boundary for the classical
evaluation of Operator-DSL expression ASTs and binders. The accepted design
separates pure classical expression interpretation from general Operator
resolution and from the `Joint`-transforming general-operator projection.

## Candidate responsibility

The candidate source family is `Evaluator._eval_op_expr_classical` and
`Evaluator._eval_classical_op_binder`, two mutually recursive methods in
`runtime/evaluator.py` (142 physical source lines combined on the
LISS-0577 branch: 72 and 70 lines respectively). The accepted destination is a focused
`runtime/evaluation/classical_operator_eval.py` module. The successor owns the
expression and binder algorithms; it does not own runtime maps or `Evaluator`
state.

`Evaluator._eval_set_comprehension` remains the consumer/dispatch operation.
It enumerates its accepted set-power domain and delegates each condition to the
classical expression evaluator. It is not absorbed into the new module merely
because it shares that callback.

Preserve the current behavior for:

- `OpLit`, `OpVar`, `OpIndexed`, `OpPow`, `OpBin`, and nested `OpBinder` ASTs.
- scalar assignment lookup, Evaluator scalar lookup, and operator-array lookup.
- `IndexDomain` and nested `RevDomain`, inclusive integer bounds, reversed
  ranges, guards, nested binders, and the `Sigma`, `Pi`, `ForAll`, and `Min`
  fold identities and behavior.
- `ForAll` short-circuiting and the current logical/arithmetic/comparison
  operators.
- index range errors, unbound names, unsupported operators, and clear rejection
  of Operator/Pauli terms in classical contexts, including message text and
  failure location.
- set-comprehension condition evaluation and all existing caller-visible
  results.

## Ownership and dependencies

`Evaluator` remains the sole owner of mutable runtime maps, scalar bindings,
operator-array bindings, environment identity, and runtime DTOs. The new module
receives an explicit assignment mapping and a narrow context for live scalar
and operator-array lookup. It must not import or instantiate `runtime.evaluator`
or make a copied state store.

Phase 0 consumer inventory identified:

- `Evaluator._bind` routes classical `OpBinder` expressions through
  `_eval_classical_op_binder`.
- `runtime/evaluation/classical.py::evaluate_value` dispatches `OpBinder`
  through `context._evaluate_classical_op_binder`; the existing LISS-0424
  Sigma characterization exercises this classical-value route.
- `_eval_classical_op_binder` recursively evaluates domain bounds and guards,
  and calls itself for nested binders; its body otherwise delegates to
  `_eval_op_expr_classical`.
- `_eval_op_expr_classical` recursively handles indexed, power, binary, and
  nested binder expressions.
- `evaluation/binding.py` dispatches `SetComprehension` to
  `_eval_set_comprehension`; conditions call `_eval_op_expr_classical`.
- `evaluation/operators.py::lookup_set_comprehension_value` resolves a Set
  definition through the Evaluator `_evaluate_set_comprehension` hook.
  LISS-0430 exercises this lookup while resolving an Operator built from that
  set; its five tests are included in the named consumer characterization.
- `evaluation/compatibility.py` installs operator-resolution hooks dynamically.
  The classical expression hooks are currently concrete Evaluator methods, so
  any new installer wiring and the active hook identity must be explicitly
  tested rather than inferred from module imports.
- Existing focused behavioral evidence includes
  `test_liss_0427_forall_binder_red.py`,
  `test_liss_0429_set_comprehension_red.py`,
  `test_liss_0430_sigma_over_set_projector_red.py`, and
  `test_liss_0431_project_no_implicit_renorm_red.py`; Phase 1 must inventory
  adjacent and direct private consumers before finalizing exact nodes.

Do not grow the existing 619-line `evaluation/operators.py` with a second
unrelated interpretation family. Do not broaden the shared
`EvaluatorContext` protocol without consumer evidence; prefer a module-local
protocol that names only scalar lookup and operator-array lookup if those
callbacks are confirmed as required.

## Separate projection boundary

`Evaluator._project_onto_operator` is explicitly excluded from LISS-0578. It
does more than evaluate an Operator expression: it reads the live operator
environment, compiles a Hamiltonian matrix, checks diagonal-projector
eligibility, reads coordinate values, creates new `World` values, and returns a
new `Joint`. It is called from `evaluation/calls.py` through the
`EvaluatorContext._project_onto_operator` callback.

This is a distinct state/value transformation boundary and should receive a
separate successor scope and issue if pursued. This specification does not
create that issue or authorize its investigation or implementation.

## Phase 0 boundary decision

Approval: `WP-0171 / LISS-0578 Phase 0 acceptance 承認` (2026-09-24).

Accepted design:

1. Extract only classical Operator-expression and classical binder evaluation
   into `runtime/evaluation/classical_operator_eval.py`.
2. Keep set-comprehension domain enumeration at its current Evaluator/binding
   boundary; it is a consumer of the successor, not part of its algorithm.
3. Keep Evaluator as the unique mutable-state owner and pass explicit live
   lookup callbacks/context; no evaluator-facade import from the successor.
4. Keep general operator projection outside LISS-0578 and require a separate
   scope decision for it.
5. Phase 1 must distinguish structural migration failures from positive
   behavior characterizations and test active hook identity plus real
   consumers.

No tests, implementation, compatibility rewrite, or active-Red entry is
authorized by Phase 0 acceptance alone. Separate Phase 1 Red approval was
received on 2026-09-24; it authorizes only the issue-owned test file and its
active-Red manifest entry. Production changes remain unauthorized.

## Phase 1 Red contract

1. **Given** a classical Operator expression or binder using supported AST
   forms, **when** evaluated through existing language entrypoints, **then**
   the established values, fold semantics, short-circuit behavior, and exact
   diagnostics remain unchanged.
2. **Given** the evaluator bodies are extracted, **when** modules and runtime
   hooks are inspected, **then** the successor owns the algorithms, Evaluator
   owns mutable state, and compatibility hooks resolve to the successor with
   no duplicate active authority.
3. **Given** classical value dispatch, binding dispatch, and Operator
   resolution consume these expressions, **when** their real runtime paths
   execute, **then** all consumers continue to receive the same values and
   errors.

The issue-owned structural suite is
`tests/test_liss_0578_classical_operator_eval_red.py`. It checks five distinct
contracts: successor ownership and non-owning boundary, duplicate-body
retirement from Evaluator, exact AST-matched installer assignments, invocation
of that installer during Evaluator setup, and runtime hook identity with the
successor functions. Before Green, the ownership, duplicate-body, exact
assignment, and live-identity contracts fail; installer invocation is already
present and passes. Existing passing characterizations remain in
`test_liss_0424_classical_numeric_sigma_red.py`,
`test_liss_0427_forall_binder_red.py`,
`test_liss_0428_min_binder_red.py`, and
`test_liss_0429_set_comprehension_red.py`; together with
`test_liss_0430_sigma_over_set_projector_red.py` these provide 22 passing
characterization checks across classical value dispatch, binder/set behavior,
and Operator-resolution lookup. Run structural Red separately so intended
migration failures are not conflated with behavior regressions. The first
test-review pass was not accepted because the compatibility contract only
searched for source substrings and omitted two consumers. The bounded
correction and corrected Phase 1 Red were approved on 2026-09-24. The correction
review evidence is linked from the LISS-0578 issue. Phase 2 implementation was
approved and applied. After separate verification-baseline snapshot scope
approval on 2026-09-24, `docs/testing/refactor-baseline.json` was synchronized
with the already-public `MutableMapping` export and fresh-capture comparison
passes. This snapshot-only update does not claim GitHub-hosted CI or final
commit verification; Phase 3 still requires separate approval.

## Exact phase paths

- Phase 1 Red (approved 2026-09-24): issue-owned focused tests,
  active-Red manifest entry, this Issue/WP/spec/trace, and review evidence
  only. No production code.
- Phase 2 Green (approved 2026-09-24):
  `runtime/evaluator.py`, new `runtime/evaluation/classical_operator_eval.py`,
  `runtime/evaluation/compatibility.py`, accepted tests, and this issue's
  lifecycle/spec/trace documentation. Any additional path requires a revised
  scope decision. The algorithms and hook wiring are implemented; full test
  and spec suites pass. The refactor-baseline snapshot has been synchronized
  under its separately approved scope and fresh-capture comparison passes.
- Phase 3 Refactor (approved 2026-09-24): the extracted implementation,
  successor ownership, compatibility direction, and consumers were reviewed;
  no further refactor was warranted. Focused and all-root suites passed on the
  dirty tree. Adjudicator accepted the Phase 3 final review on 2026-09-24;
  all-blocking verification after the final commit SHA remains required.
  Duplicate-body removal was completed in Phase 2 Green.

## Exclusions

- `_project_onto_operator` and Hamiltonian-to-`Joint` projection.
- Generic Operator lowering/resolution, operator arrays' storage owner, and
  set-comprehension domain enumeration.
- Parser/typechecker changes, language syntax/semantics changes, provider/QPU
  behavior, Semantic IR authority, and unrelated evaluator decomposition.
