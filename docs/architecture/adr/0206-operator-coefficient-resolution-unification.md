# ADR 0206: Operator coefficient/binder resolution unification (investigation)

## Status

**Accepted** (2026-08-12) — Adjudicator Architecture approval for the
unification direction, with explicit authorization in the same round to
resolve the three open design questions and implement (superseding the
ADR 0204/ADR 0205-style "Architecture approval, then separate Feature
Plan" precedent for this specific ADR, by the Adjudicator's own explicit
instruction: "統合で進める。この回でドキュメントも含めてすべて設計して
修正する" — proceed with unification, design and fix everything,
including documentation, in this round).

Implemented as [LISS-0407](../../issues/LISS-0407-operator-resolution-unification.md).
See "Design questions — resolved" and "Consequences" below for what was
actually built, which is a deliberately **bounded** slice of the full
unification sketched in the original Decision proposal — see "Scope
actually implemented" for the honest boundary between what shipped and
what remains future work.

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

## Decision

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

### Design questions — resolved

1. **Eager vs. lazy resolution timing → lazy, at the existing
   consumption points.** Mechanism 1's per-call scoping (load-bearing for
   LISS-0297's recursive/re-entrant factory calls) is preserved exactly:
   resolution still happens at `Operator` StateBind time and at
   `evolve`'s call site, not eagerly over the whole unit. The unified
   resolver (`Evaluator._resolve_operator_tree`, `runtime/evaluator.py`)
   is invoked from the same points mechanisms 1-3 already fired from —
   it replaces *what* they call, not *when* they're called.
2. **Error-reporting contract → resolution failure inside a node the
   resolver recognizes (a binder that needs an array, a struct field
   that doesn't exist) is always a `KernelError`; a node kind the
   resolver doesn't touch (already-literal Pauli algebra, unresolved
   `next`/`wrap` binder-internal calls) passes through unchanged.** The
   `except (IndexError, ValueError): return expr` silent swallow is
   removed from the binder-lowering step; genuine binder-lowering
   failures now surface as `KernelError(f"cannot lower Operator binder:
   {exc}")` instead of a much later, vaguer `cannot compile sparse Pauli
   for OpBinder`.
3. **Scope of `hamiltonian.py` (dense path) and `typecheck.py`
   (diagnostics) → explicitly out of scope, confirmed safe to leave
   untouched.** Both already consume fully-literal `OpExpr` trees
   correctly; the unified resolver's job is only to *produce* that
   literal form before either walker sees it. Verified by the full
   regression sweep and 100% spec-verification pass rate after
   implementation — neither file needed a change.

### Scope actually implemented

`Evaluator._resolve_operator_tree` (`runtime/evaluator.py`) is the new
single recursive entry point, invoked via `_lower_operator_value` from
the same three call sites mechanisms 1-3 used before. It handles, in one
pass:

- **`OpCall` anywhere in the tree** (not only as the entire
  right-hand side) — inlines a call to a known Operator-returning
  function via `_resolve_op_call`, which converts the `OpExpr` call
  arguments back into the generic `Expr` shape
  `_resolve_operator_factory_call` already understands and reuses that
  existing, tested arg-binding logic unchanged. Closes the LISS-0402
  "Operator-Call-inline" gap (`scale * f(weights)`).
- **`OpBinder`**, lowered against a merged array context
  (`Evaluator._operator_array_context`: top-level literal arrays +
  Host-resolved arrays, ADR 0119/LISS-0406) that now also includes any
  `Float[N]` array bound to the *current function call's own
  parameters* (`_resolve_operator_factory_call`'s new `local_arrays`).
  Closes the confirmed-broken parameter-array case.
- **`OpBin`/`OpPow`**, recursed structurally, preserving object identity
  when a subtree needs no change (avoids reconstructing unchanged trees).
- **`OpAttr`**, via the existing `materialize_op_attrs`
  (`op_attr_elaboration.py`), now also given an `operators` context so
  it recurses through an `OpVar` naming another bound Operator whose own
  tree still has an unresolved `OpAttr` leaf. Closes the struct-field-
  behind-an-intermediate-Operator-variable indirection case.

**Not implemented, deliberately** (matches "Scope of `hamiltonian.py`/
`typecheck.py`" above, and keeps this within what was directly
demonstrated as needed):

- `OpCall` support for binder-internal helpers other than Operator-
  returning user functions (e.g. anything beyond the already-working
  `next`/`wrap`, LISS-0373) — untouched, out of scope.
- Operator-typed function parameters in `_resolve_operator_factory_call`
  (a pre-existing, separate, narrower gap noticed but not one of the
  three confirmed cases this ADR targets) — left as documented future
  work, not attempted.
- Any change to `finite_binder.py`'s or `sparse_pauli.py`'s internals —
  reused exactly as they were; only the *context* passed into them
  changed.

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

- Folding `hamiltonian.py`'s dense-matrix walker or `typecheck.py`'s
  diagnostics walker into the unified resolver — confirmed unnecessary
  (Design questions, resolved, item 3).
- `OpCall` support for anything other than Operator-returning user
  functions, and Operator-typed factory parameters (Scope actually
  implemented, above) — real, narrower, separate gaps, not attempted.
- Redesigning `finite_binder.py`'s or `sparse_pauli.py`'s internals.

## Consequences

- A physicist can now combine per-candidate Host arrays, struct-typed
  named weights, function parameters, and nested Operator-returning
  function calls in an Operator expression in the natural combinations
  that previously required knowing which of three independent
  mechanisms happened to cover that specific shape.
- Three confirmed-broken combinations (Float[N] array threaded through a
  function parameter into a `sum` binder; a struct-field coefficient
  hidden behind an intermediate named Operator variable; a nested
  Operator-returning call inside a larger Operator expression, e.g.
  `scale * f(weights)` — the original LISS-0402 finding) now work,
  each locked in by a dedicated regression test
  (`tests/test_liss_0407_operator_resolution_unification_red.py`).
  A fourth test confirms a genuinely missing Host array still fails
  closed with a specific diagnostic, not the old generic
  `cannot compile sparse Pauli for OpBinder`.
- Full regression sweep: 1459 passed (up from 1455 before this Issue).
  Spec verification: 100.00% (161/161). S02's own example
  (`main_selection.sqx`, `run_selection.py`, `benchmark_report.py`)
  produces byte-identical output before and after this change,
  confirming no behavior change for already-working programs.
- The scope actually shipped is bounded, not the full sketch in the
  original Decision proposal — `hamiltonian.py`/`typecheck.py` unchanged,
  Operator-typed factory parameters and non-Operator `OpCall` targets
  unchanged. If a further concrete gap surfaces in either of those,
  it is new, separate scope, not something this ADR already covers.

## Acceptance boundary

Acceptance of this ADR authorized the unification described in Decision,
implemented as [LISS-0407](../../issues/LISS-0407-operator-resolution-unification.md)
in the same round. It does **not** authorize folding `hamiltonian.py`/
`typecheck.py` into the same resolver, or extending `OpCall`/factory-
parameter support beyond what "Scope actually implemented" describes —
either would be new scope requiring its own investigation.

## Implementation permission

| Item | Status |
|---|---|
| Architecture (unification direction) | **granted** 2026-08-12 |
| Design questions (timing, error contract, walker scope) | **resolved** 2026-08-12 (Design questions — resolved, above) |
| Technology selection | not applicable |
| Feature Plan (Issue-level Plan) | [LISS-0407](../../issues/LISS-0407-operator-resolution-unification.md), same-round Plan+Completion approval (Adjudicator's explicit "この回で…修正する" instruction) |
| Phase 1 Red / Kernel code | **complete** — `runtime/evaluator.py`, `runtime/op_attr_elaboration.py` |

## Decision history

| Date | Event |
|---|---|
| 2026-08-12 | Investigation requested (Adjudicator, S02 remaining-items review) |
| 2026-08-12 | Investigation complete; this document proposed |
| 2026-08-12 | Adjudicator asked "physically correct" framing; recommendation given (unification is philosophically correct per the language vision; engineering risk was a separate, sequencing question) |
| 2026-08-12 | Adjudicator Architecture approval + explicit same-round design-and-fix instruction → **Accepted**; implemented as LISS-0407 |
