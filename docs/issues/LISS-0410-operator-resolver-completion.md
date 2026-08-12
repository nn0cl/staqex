# LISS-0410: complete the ADR 0206/LISS-0407 unified Operator resolver

## Metadata

- Local issue ID: LISS-0410
- Status: complete
- Type: Feature Path (bug fix; `compiler/staqex/runtime/evaluator.py`
  only — closes a gap in ADR 0206's own already-Accepted, already-shipped
  implementation, not a new architecture decision, per CLAUDE.md's Bug
  Triage)
- Priority: P0 (correctness — `apply`/`capply` silently rejected valid
  programs `evolve` already accepted)
- Planning size: `M`
- Owner / agent: Claude Code
- Parent: independent-context source code review (this session,
  Adjudicator-requested); Part 1 of the resulting fix plan
  (`unitarity_check.py`/QASM backend static-analysis completion is
  LISS-0411, a separate Issue)
- Branch: `feature/liss-0410-operator-resolver-completion`
- GitHub Issue / PR: (opened at Completion)

## Intent

A code review found `apply`/`capply` (`Evaluator._resolve_unitary_matrix`)
read raw `self.operators[name]` AST directly, with no resolution step —
so a struct-field coefficient that already worked for `evolve`
(`Operator U = weights.a * X; apply(U, psi)`) still raised `cannot
compile operator node OpAttr`. Investigating why revealed LISS-0407's
own "unified resolver" claim was incomplete: `_resolve_operator_tree`
never actually learned to handle `OpAttr` — that stayed a separate,
bolted-on call (`materialize_op_attrs`) reachable only from `evolve`'s
own call site and the factory-call path. This Issue folds `OpAttr`
resolution into `_resolve_operator_tree` itself, so every `Operator`
StateBind is guaranteed fully resolved once bound — fixing `apply`/
`capply` with **no code change in `_resolve_unitary_matrix` at all**,
since it already just reads the (now pre-resolved) `self.operators[name]`.

## Scope

1. `Evaluator._resolve_operator_tree`: add an `OpAttr` case (reusing
   `op_attr_elaboration.py`'s existing `_op_attr_float`/
   `OpAttrElaborationError`, not reimplementing struct-field lookup),
   checked first in the recursive dispatch.
2. Thread an `objects: Mapping[str, Any] | None` parameter through
   `_resolve_operator_tree` → `_lower_operator_value` →
   `_resolve_operator_expr`, defaulting to `self.objects` (module scope)
   when not given.
3. `_resolve_operator_factory_call`'s own internal loop (resolving a
   factory function's *local* `Operator` binds) now passes
   `objects=attr_objects` — the call's own param-name-rekeyed object
   scope — instead of implicitly falling back to module-level
   `self.objects`.
4. `_resolve_unitary_matrix` (`apply`/`capply`): **no change**.

## Explicitly out of scope

- `unitarity_check.py` and the QASM/Trotter backend — separate,
  compile-time-only static-analysis code paths with no live `Evaluator`
  state; their own fix is LISS-0411.
- Deeper nested-call argument scoping (a factory function calling
  *another* struct-parameterized factory using one of its own local
  parameter names as the argument) — not exercised by any current
  example or test; `_resolve_operator_factory_call`'s own arg-binding
  loop still resolves `Var` arguments against module-level
  `self.objects`/`self.scalars` only. Left as a known, narrower,
  undemonstrated limitation rather than expanded ahead of need.
- Adding inline-anonymous-Operator-expression support to `evolve ...
  under <expr> for t` — see Design verification point 1; this was never
  a working form at all (parser-level, unrelated to this Issue).

## Design verification performed

1. **A wrong assumption in the plan, corrected during this Issue's own
   Red phase**: the plan assumed `evolve q under (scale * weights.a *
   Z) for dur` (an inline, never-bound Operator expression) already
   reached `_resolve_operator_tree`-compatible AST and just needed
   richer resolution. Direct testing showed this form was **never**
   supported at all — even the struct-field-free `evolve q under (scale
   * Z) for dur` fails today with `hamiltonian must be Operator name or
   Pauli literal`, because the parser produces generic `BinOp`/`Var`
   nodes for this position, not the Operator-DSL `Op*` AST the resolver
   operates on. Only a *bare* Pauli literal (`under Z`) or a bound
   Operator *name* work inline. This is a separate, pre-existing
   parser-level gap, unrelated to ADR 0206/LISS-0407 — corrected out of
   scope rather than silently expanding it. Locked in as a regression
   guard (`test_inline_compound_evolve_expression_was_never_supported`)
   so this doesn't get accidentally "fixed" without a deliberate
   decision later.
2. **A real regression found and fixed during Green**: folding `OpAttr`
   into `_resolve_operator_tree` using a hardcoded `self.objects` broke
   4 existing tests (`test_applied_catalog_health_red.py`,
   `test_liss_0338_a11_structural_monitoring_magnetometer_red.py`,
   `test_noether_forge_slice_b_integrated_red.py`,
   `test_noether_forge_slice_c_d_integrated_red.py`) — all failing with
   `unbound struct for Operator coefficient \`c.defect\``. Root cause:
   A11's `build_sensor_hamiltonian(c: SensorCouplings) -> Operator`
   builds a local `Operator H = c.defect * X[1] + ...` bind *inside* the
   factory function, where `c` is a **parameter** name (LISS-0297
   param-name rekeying) — not necessarily present in module-level
   `self.objects` at all. `_resolve_operator_factory_call`'s own loop
   called `self._resolve_operator_expr(stmt.expr)` with no way to pass
   its already-built `attr_objects` (the correct, param-rekeyed scope)
   through to my new OpAttr-resolving code, which defaulted to the
   wrong, module-level `self.objects`. Fixed by threading an explicit
   `objects` parameter through the whole call chain instead of
   hardcoding `self.objects` anywhere in the new resolution path.
3. **A wrong test expectation, corrected during Green**: initially
   expected `apply` to newly *reject* a genuinely non-unitary struct-field
   Operator with a `KernelError`. Direct testing showed the *runtime*
   `apply` path has never validated unitarity at all — even a bare-literal
   `Operator Bad = 2.0 * X; apply(Bad, psi)` already ran without error
   before this Issue, producing an unnormalized result
   (`marginal={1: 4.0}`). Only the *static* `check` command
   (`unitarity_check.py`, LISS-0411's scope) is supposed to catch this.
   Corrected the test to assert the literal and struct-field forms now
   behave *identically* (same pre-existing unnormalized-result shape),
   not that either newly raises an error — this Issue's job is making
   `apply`/`capply` able to resolve these Operator forms at all, not
   adding a new runtime safety check that never existed.
4. Full regression sweep: 1464 passed (up from 1459 — 5 new tests, 0
   regressions once the A11-class fix above landed). Spec verification:
   100.00% (161/161).

## Exit criteria

- [x] `apply`/`capply` resolve struct-field Operator coefficients
  (previously `cannot compile operator node OpAttr`).
- [x] Operator-variable indirection through the `self.operators[name]`
  shortcut works once the referenced Operator is itself fully resolved
  at its own bind time (no separate fix needed for the shortcut itself
  — confirmed by direct testing, smaller than the original plan assumed).
- [x] The three LISS-0407 target cases remain fixed.
- [x] A11/Noether-Forge factory-function struct-field resolution
  regression found during Green is fixed (objects context threading).
- [x] Full regression sweep passes (1464 passed); spec verification
  100.00% (161/161).
