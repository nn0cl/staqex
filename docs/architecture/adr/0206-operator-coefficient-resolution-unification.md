# ADR 0206: Operator coefficient/binder resolution unification (investigation)

## Status

**Proposed** — Architecture Path investigation only. This document does
**not** authorize implementation, technology selection, or Feature Path
Red of any kind. It requests Architecture approval for a *direction*;
even after acceptance, a full Work-Plan Investigation (multi-Issue batch,
matching the ADR 0204/ADR 0205 precedent) would still be required before
any Kernel code change.

Companions: [LISS-0402](../../issues/LISS-0402-s02-selection-example.md),
[LISS-0405](../../issues/LISS-0405-s02-unified-selection-evolve.md),
[LISS-0406](../../issues/LISS-0406-host-coefficient-tensor-evaluator-wiring.md)
(the S02 work that surfaced this — each hit a different corner of the gap
described below); [ADR 0119](../decision-themes/dec-0006-host-qpu-and-external-ports.md)
(Host coefficient tensors); [ADR 0194](../decision-themes/dec-0006-host-qpu-and-external-ports.md)
(`HostInputPort`); [`adjudicator-language-vision.md`](../adjudicator-language-vision.md)
§2.2 ("source must denote the same thing as the blackboard").

## Context

Building S02's objective Hamiltonian across three Issues required
combining Operator coefficients from several sources — a Type-First
scalar, a struct field, a Host-supplied per-position array, a function
parameter — and each combination that wasn't already a previously-shipped
narrow case failed with `cannot compile sparse Pauli for OpX`. Direct
investigation (this ADR) found the underlying cause: **there is no single
mechanism that resolves an Operator AST's non-literal coefficients before
`sparse_pauli.py::_eval`/`compile_sparse_pauli` consumes it.** There are
three, added incrementally by different Issues, none aware of the others:

1. **Function-call return-position inlining**
   (`evaluator.py::_resolve_operator_factory_call`, lines 3223-3317, and
   `_resolve_operator_method_call`, lines 3319-3441 — LISS-0136/0137/0139/0297).
   A macro-expansion-style pass: binds call-site args under the callee's
   *parameter* names, walks the function body's local `StateBind`s, then
   rewrites the return expression via two tree-walks in
   `runtime/op_attr_elaboration.py` — `materialize_op_scalar_vars`
   (`OpVar` → `OpLit` via a `scalars` dict) and `materialize_op_attrs`
   (`OpAttr` → `OpLit` via an `objects` dict, supporting nested
   `o.inner.c` chains, LISS-0306) — then a *separate* pass,
   `_lower_operator_value` (`evaluator.py:3199-3221`, LISS-0224), that
   only expands `OpBinder` nodes by delegating to `finite_binder.py` with
   **no array context** (`arrays={}`, hardcoded).
2. **Binder-array lowering** (`finite_binder.py`:
   `_collect_float_arrays`, `_host_placeholder_keys`,
   `merge_host_coefficient_arrays`, `lower_finite_binder_operators`).
   Resolves `Float[N]…` array-indexed coefficients (`w[i]`) inside
   `sum(...)`/`product(...)` binders — but only scans **top-level
   statements of `main()`** (`_collect_float_arrays`,
   `finite_binder.py:472-509`). Never sees function bodies or parameters.
3. **A third materialization fired from `evolve`'s own call site**
   (`evaluator.py::_bind_evolve_hamiltonian` → `_hamiltonian_evolve_one_step`,
   line 1934 — ADR 0114/LISS-0121). Calls `materialize_op_attrs` directly
   on whatever Operator AST is passed to `evolve(...)`, independent of
   mechanism 1. This is why a **bare top-level** `Operator H =
   weights.a * some_operator_var` (no function call at all) already
   works today — confirmed by direct execution, correcting an earlier,
   less precise version of this finding.

### What is confirmed broken, and exactly why

- **A `Float[N]` array threaded as a function *parameter*, indexed
  inside a `sum(...)` binder in that function's body** —
  `Operator H = f(arr)` where `f(w: Float[2]) -> Operator { return
  sum(i in Index<0..1>) { w[i] * Z[i] } }` — raises `cannot compile
  sparse Pauli for OpBinder`. Root cause, precisely: mechanism 1's
  `_lower_operator_value` (`evaluator.py:3219`) calls
  `finite_binder._lower_operator_expr(expr, unit)` with no `arrays=`
  argument, so the parameter `w` is never in the array map (mechanism 2
  only scans `main()`). The resulting `ValueError("indexed operator is
  not executable yet")` from `finite_binder.py:340` is then **silently
  discarded** by a blanket `except (IndexError, ValueError): return
  expr` at `evaluator.py:3220-3221` — a real, actionable diagnostic
  replaced by a much vaguer error three call frames and one module
  later. LISS-0224's own spec explicitly named this exact gap ("Requiring
  Host arrays inside method-returned binders") as Out of Scope when it
  shipped — known, not accidental.
- **Struct-field access hidden behind an intermediate named Operator
  variable** — `Operator G = weights.a * Z[0]; Operator H = G + other`,
  then `evolve psi under H` — is very likely to hit the same class of
  gap: mechanism 3's `materialize_op_attrs` is a shallow, single-tree
  rewrite that does not recurse through an `OpVar` reference into
  `self.operators[name]`'s own still-raw AST. (Flagged by investigation
  as *likely*, not yet independently reproduced with a fresh minimal
  repro — worth confirming before this becomes Feature Path scope.)

### Not accidental — a recurring pattern, not a one-off

`git log`/Issue-doc lineage: LISS-0052 (original binder lowering,
top-level only) → LISS-0136 (scalar-var materialization) → LISS-0137
(struct-field/method-return coefficients) → LISS-0139 (method-call
return position) → LISS-0224 (binders inside factory returns, Host
arrays explicitly deferred) → LISS-0297 (struct params bind under
parameter name) → LISS-0306 (nested field chains). Six Issues shipping
the next narrow case each time, none generalizing the underlying
question: *"given an Operator AST with some non-literal leaves, and a
context (scalars, objects, host input, function parameters) that could
resolve them, produce a fully-literal AST `sparse_pauli.py` can consume."*
Two further, independent duplications compound this: `hamiltonian.py`
(`op_n_qubits`/`op_space`, the dense-matrix path) and `typecheck.py`
(`_looks_like_operator_ast`/`_check_operator_expr`, diagnostics) each
re-implement their own partial understanding of the same `OpExpr` node
kinds, structurally parallel to but code-independent from both
`finite_binder.py` and `sparse_pauli.py`.

Per the language vision (§2.2, "source must denote the same thing as the
blackboard"): a physicist writing a per-candidate weighted Hamiltonian
naturally reaches for a struct of named weights, or a function that
builds the Hamiltonian from parameters — exactly the forms this
fragmentation currently rejects in combination, forcing "truncating or
reshaping chalk so the compiler is happier" (the vision's own words for
what the design explicitly should not do): flattening structs into bare
scalars, avoiding function wrapping, restructuring at `main()` level.

## Decision proposal (not yet accepted)

A single resolution entry point,

```
resolve_operator_expr(
    expr: OpExpr, *,
    scalars: dict[str, float],
    objects: dict[str, Any],
    operators: dict[str, OpExpr],
    array_context: Mapping[str, Any],  # unifies local literals + Host CoefficientTensors + function-parameter arrays
) -> OpExpr
```

closing over the union of what mechanisms 1-3 each see today, that:

- resolves `OpVar` (scalars, or recurse into `operators[name]`),
- resolves `OpAttr` (struct/nested-struct field access, `objects`),
- expands `OpBinder` (delegating to `finite_binder.py`'s existing
  expansion logic against `array_context`, which would need to include
  a function's local parameter-bound arrays, not only `main()`-level
  ones),
- inlines `OpCall` in Operator-return position (reusing
  `_resolve_operator_factory_call`'s existing arg-binding logic),

and is the **only** place any of these four substitutions happen,
replacing the three current call sites.

This document does not decide the following, each a real design
question the investigation surfaced and any implementation would need to
resolve first:

1. **Eager vs. lazy resolution timing.** Mechanism 2 runs once, eagerly,
   over the whole unit at `_run_unit_body` start. Mechanism 1 runs
   lazily, per-call, with a freshly-scoped local context — this scoping
   is load-bearing for recursive/re-entrant factory calls with
   differently-named arguments (LISS-0297's entire point). A unified
   pass must either become fully lazy (resolved on first use, memoized)
   or thread a call-context stack through the eager pass.
2. **Error-reporting contract.** The current silent
   `except (IndexError, ValueError): return expr` exists so a
   binder-lowering failure doesn't break factory calls whose return
   value doesn't actually contain a binder — but it also discards real,
   actionable errors (see "confirmed broken" above). Any unification
   needs an explicit contract for when resolution failure is a hard
   diagnostic versus a legitimate "this pass doesn't apply here" no-op.
3. **Scope of the dense-path (`hamiltonian.py`) and diagnostics-path
   (`typecheck.py`) walkers.** Whether they fold into the same unified
   pass, stay separately maintained but required to track it in a test,
   or are explicitly out of scope for this effort.

## Rejected / alternative considered

### Continue patching narrow cases one at a time (status quo)

The pattern this session found (six Issues, one narrow case each) could
simply continue — lower risk per change, no redesign, no regression
exposure to `hamiltonian.py`/`typecheck.py`. Concretely: fix the
parameter-array gap and the swallowed diagnostic (Context, "confirmed
broken", first bullet) as an isolated, contained bug fix — thread the
function's local array bindings into `evaluator.py:3219`'s call, and
stop discarding the `ValueError`. This alone closes the one gap that has
concretely blocked real work so far (S02), independent of whether full
unification is ever pursued, exactly as ADR 0205 treated the disclosed
`Z*Z` bug as independently fixable regardless of that ADR's own outcome.

Trade-off honestly stated: this keeps the fragmentation, and the next
new combination (a struct field indexed through an intermediate Operator
variable, or a Host array combined with a struct-typed weight, etc.)
will very likely need its own seventh patch.

## Non-goals

- Any implementation, in this document.
- Deciding eager/lazy timing, the error-reporting contract, or the
  dense/diagnostics-walker scope (open design questions above, for a
  later Feature Plan investigation if this ADR is accepted).
- Redesigning `finite_binder.py`'s or `sparse_pauli.py`'s public
  contracts beyond what unification requires.

## Consequences (if accepted and later implemented)

- A physicist could combine per-candidate Host arrays, struct-typed
  named weights, and function parameters in an Operator expression in
  any combination, without needing to know which of three independent
  mechanisms currently covers that specific shape.
- Real regression risk against the existing LISS-0121/0136/0137/0139/
  0224/0297/0306 test suite, and against `hamiltonian.py`'s dense path
  if that is folded in — sized at investigation time as multi-week,
  ~1,000+ lines across 6 files, not a contained refactor.
- If accepted, still requires a separate Work-Plan Investigation (spec/
  ADR-linked Local Issues, granularity rationale, execution order, draft
  batch record) before any Red, per CLAUDE.md's Work-Plan Investigation
  requirement for broad grants.

## Acceptance boundary

Acceptance of this ADR authorizes the unification *direction* described
in Decision proposal as a future architecture boundary. It does **not**
authorize:

- Any Kernel code change.
- A decision on eager/lazy timing, the error contract, or dense/
  diagnostics-walker scope — each remains open pending a Feature Plan
  investigation.
- The independently-fixable parameter-array gap and swallowed
  diagnostic (Rejected/alternative considered, above) as a separate
  Feature Path bug fix — that may proceed under normal bug-triage rules
  regardless of this ADR's status, exactly as the S02 `Z*Z` bug did
  under ADR 0205.

## Implementation permission

| Item | Status after Accept |
|---|---|
| Architecture (unification direction) | granted only if Accepted |
| Eager/lazy timing, error contract, walker scope | not decided — future Feature Plan |
| Technology selection | not applicable |
| Feature Plan (Issue-level Plan) | required separately, not requested by this document |
| Phase 1 Red / Kernel code | forbidden until a Feature Plan and Plan approval exist |

## Decision history

| Date | Event |
|---|---|
| 2026-08-12 | Investigation requested (Adjudicator, S02 remaining-items review) |
| 2026-08-12 | Investigation complete; this document proposed |
