# LISS-0407: Operator coefficient/binder resolution unification

## Metadata

- Local issue ID: LISS-0407
- Status: complete
- Type: Feature Path (Kernel: `compiler/staqex/runtime/evaluator.py`,
  `compiler/staqex/runtime/op_attr_elaboration.py`)
- Priority: P1
- Planning size: `M`
- Owner / agent: Claude Code
- Parent: [ADR 0206](../architecture/adr/0206-operator-coefficient-resolution-unification.md)
  (Accepted 2026-08-12)
- Branch: `feature/liss-0407-operator-resolution-unification`
- GitHub Issue / PR: (opened at Completion)

## Approval

Same-round Plan + Completion approval, per the Adjudicator's explicit
instruction accompanying ADR 0206's Architecture approval: "統合で進め
る。この回でドキュメントも含めてすべて設計して修正する" (proceed with
unification; design and fix everything, including documentation, in this
round).

## Intent

Implement ADR 0206's unification direction as a bounded, safely-scoped
slice: one recursive resolver, `Evaluator._resolve_operator_tree`,
invoked from the same points the three previous ad-hoc mechanisms fired
from, closing the three confirmed-broken combinations found while
writing S02 (LISS-0402/0405/0406) plus the swallowed-diagnostic bug —
without folding in `hamiltonian.py`/`typecheck.py` or extending
`OpCall`/factory-parameter support beyond what's directly demonstrated
as needed (see ADR 0206's own "Scope actually implemented" / Non-goals).

## Scope

1. `Evaluator._operator_array_context` — merged Float[N]… coefficient
   arrays (top-level literal + Host-resolved, ADR 0119/LISS-0406)
   visible at `main` level.
2. `Evaluator._resolve_op_call` / `_op_expr_arg_to_source_expr` — inline
   a call to a known Operator-returning function found anywhere in an
   Operator expression tree (not only as the entire right-hand side),
   by converting `OpExpr` call arguments back into the generic `Expr`
   shape `_resolve_operator_factory_call` already handles and reusing
   that logic unchanged.
3. `Evaluator._resolve_operator_tree` — the single recursive entry point:
   `OpCall` (inline via #2), `OpBin`/`OpPow` (structural recursion,
   identity-preserving when unchanged), `OpBinder` (lower against the
   merged array context, now a `KernelError` on genuine failure instead
   of a silent pass-through).
4. `Evaluator._lower_operator_value` rewritten to route through #3.
5. `Evaluator._resolve_operator_factory_call`: thread `Float[N]…`
   array-typed parameters into a new `local_arrays` context (closes the
   parameter-array gap), and pass `operators=self.operators` into
   `materialize_op_attrs` (closes the intermediate-Operator-variable
   indirection gap).
6. `op_attr_elaboration.py::materialize_op_attrs`: new optional
   `operators` parameter — recurses through an `OpVar` naming another
   bound Operator whose own tree still has an unresolved `OpAttr` leaf,
   with a `_seen` cycle guard.
7. `_hamiltonian_evolve_one_step`'s existing `materialize_op_attrs` call
   site (the `evolve`-time mechanism) updated to pass
   `operators=self.operators`.

## Explicitly out of scope

- `hamiltonian.py` (dense-matrix path) and `typecheck.py` (diagnostics)
  — confirmed unnecessary to change (ADR 0206, Design questions
  resolved, item 3).
- `OpCall` support for anything beyond Operator-returning user functions
  (binder-internal `next`/`wrap` helpers, LISS-0373, untouched).
- Operator-typed parameters in `_resolve_operator_factory_call` — a
  pre-existing, separate, narrower gap noticed but not one of the three
  confirmed cases this Issue targets.
- Rewriting `main_selection.sqx` or any other shipped example — not
  needed; S02's own output is confirmed byte-identical before/after.

## Design verification performed

1. **Confirmed all three target cases fail today, for the expected
   reasons**, before writing any implementation: `cannot compile sparse
   Pauli for OpBinder` (parameter array), `cannot compile sparse Pauli
   for OpAttr` (operator-variable indirection), `cannot compile sparse
   Pauli for OpCall` (nested Operator-returning call) — via direct
   execution, not assumed.
2. **Full regression sweep after implementation: 1459 passed** (up from
   1455 before this Issue — 4 new tests in
   `tests/test_liss_0407_operator_resolution_unification_red.py`, zero
   regressions).
3. **Spec verification: 100.00% (161/161)**
   (`tests/spec_verification/run_all.py`) — confirms `hamiltonian.py`'s
   dense path and every other spec-covered surface remain correct
   without any change to those files.
4. **S02's own example is byte-identical before and after**: `python3 -m
   compiler.staqex check main_selection.sqx`, `run_selection.py`, and
   `benchmark_report.py` (feasibility_rate, infeasible_shots,
   top_k_overlap, terminal_selection, all quality metrics) produce
   exactly the same output as before this Issue — direct confirmation
   that unification did not silently change behavior for an
   already-working real program.

## Exit criteria

- [x] Red tests demonstrate all three target gaps against a real
  `Evaluator` run (`tests/test_liss_0407_operator_resolution_unification_red.py`).
- [x] Green: all three gaps closed; swallowed diagnostic replaced with a
  specific `KernelError`; existing 1455-test suite fully green plus 4
  new tests (1459 total).
- [x] Spec verification 100.00% (161/161).
- [x] S02's own example confirmed unaffected (byte-identical output).
- [x] ADR 0206 updated to Accepted with the three design questions
  resolved and "Scope actually implemented" documented honestly against
  the original, larger sketch.
