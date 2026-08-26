# LISS-0424: classical numeric `Sigma`/`Pi`

## Metadata

- Local issue ID: LISS-0424
- Status: complete
- Type: Feature Path (`compiler/staqex/runtime/evaluator.py`)
- Priority: P1
- Planning size: M (new evaluation path, reuses existing Operator-DSL grammar)
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

$\sum_i x_i=3$ in the blackboard equation is a literal classical numeric
sum — no Operator, no State, just an Int. Today `Sigma`/`Pi` only produce
an Operator (`OpBinder`, folded via `finite_binder.py`'s Pauli/matrix
lowering) or a State (`KetSumBinder`, LISS-0420). Neither path accepts a
pure classical body — `Sigma (i In 0..n-1) { x[i] }` had no way to become
an `Int`/`Float` value.

## Design decision (confirmed before Red)

Reuse the *existing* Operator-DSL body grammar (`_op_expression()`,
already used for `activity_w[i] * Z[i]`-style classical-coefficient-times-
Operator terms) rather than inventing new general-expression array-index
syntax — `OpIndexed`/`OpBin`/`OpVar`/`OpLit` already parse `x[i]`
correctly inside a `Sigma`/`Pi` body; the missing piece was purely an
*evaluation* path, not a *parsing* one.

**Dispatch signal**: `Operator H = Sigma (...) {...}` statements are
already handled by a separate code path (`stmt.ty.name == "Operator"`
checks in the statement-execution loop) that never calls `_bind` at all
(confirmed by reading `evaluator.py`, not assumed). This means any
`OpBinder` that *does* reach `_bind` (or `_eval_value`, for `Sigma(...)`
used as a sub-expression, e.g. `Sigma(...) == 3`) is, by construction,
never an Operator-typed one — so no additional "does the body contain a
Pauli atom" check is needed at the dispatch point.

## Real bug found and fixed during Green

Initially only added the `OpBinder` case to `_bind` (covering `Int total
= Sigma(...) {...}`). Testing the actual target shape —
`Sigma (i In 0..n-1) { x[i] } == 2` used *inside* a larger boolean
expression — crashed with `KernelError: cannot evaluate OpBinder as
value`, because `_bind`'s `BinOp` handling for non-`*` operators falls
through to `_eval_value(expr, a)`, a *separate* function from `_bind`
that had no `OpBinder` case at all. Found by actually running the target
use case end-to-end, not just the simpler top-level-bind case. Fixed by
adding the same dispatch to `_eval_value`.

## Scope

1. `_eval_classical_op_binder(expr, assign)`: walks a bare-range
   `IndexDomain` (through any `RevDomain` wrapper), evaluates the guard
   (if present) and body per index via `_eval_op_expr_classical`, folds
   with `+` (Sigma) or `*` (Pi). Multi-binding `Sigma (i In D1, j In D2)
   where ... {...}` is handled by recursing into `expr.body` when it is
   itself an `OpBinder` — matching the *exact* nesting shape
   `parser.py::_op_binder` already produces for multi-binding (confirmed
   by re-reading that function, not assumed), so no separate multi-
   binding code path was needed.
2. `_eval_op_expr_classical(expr, assign)`: evaluates `OpLit`/`OpVar`/
   `OpIndexed`/`OpPow`/`OpBin` (arithmetic `+`/`-`/`*`, comparisons
   `<`/`<=`/`>`/`>=`/`==`/`!=`, and `&&`/`||` for guard expressions) as
   plain Python values. Any other `OpExpr` node (a genuine Pauli/Fock
   atom) raises a clear `KernelError` naming the mismatch, rather than
   silently misbehaving.
3. `_bind` and `_eval_value` both gained an `OpBinder` case delegating to
   `_eval_classical_op_binder`, covering both the top-level-bind and
   sub-expression call shapes.

## Explicitly out of scope

- Comma-separated multi-condition guards (`where i < j, x[i]*x[j]==1`) —
  `_op_guard()`'s grammar is untouched by this Issue; still `&&`/`||`
  only. That is LISS-TBD-S7's own scope (`Set` comprehension's comma
  convention).
- General expression-position array indexing outside the Operator-DSL —
  confirmed (via `test_liss_0369...`) that array indexing is currently
  Operator-DSL-only; this Issue reuses that existing grammar rather than
  building a new one.

## Design verification performed

1. Confirmed `Operator H = Sigma(...)` statements never reach `_bind` at
   all (separate `stmt.ty.name == "Operator"` dispatch), so the new
   `OpBinder` cases in `_bind`/`_eval_value` cannot be reached for a
   genuine Operator-typed binder — verified by re-running the full
   existing Operator-DSL test suite (unchanged, all green).
2. `test_bare_classical_sigma_sums_the_index`: `Sigma (i In 0..2) { i }`
   = 0+1+2 = 3.
3. `test_classical_pi_multiplies`: `Pi (i In 1..3) { i }` = 1×2×3 = 6.
4. `test_classical_sigma_indexes_a_tuple_valued_state_coordinate`: the
   exact target shape for S02's `F` predicate
   (`Sigma (i In 0..n-1) { x[i] } == 2` over `prepare_selection(3)`) —
   cross-checked against the hand-computed $\binom{3}{2}=3$ of 8 patterns
   probability (3/8), not just "doesn't crash."
5. `test_multi_binding_classical_sigma_with_guard_recurses_correctly`:
   `Sigma (i In D1, j In D2) where i<j { x[i]*x[j] }` cross-checked
   against hand-enumerated per-pattern pair-counts (0/1/3 for the 8
   possible 3-bit patterns) — not just "doesn't crash."
6. `test_classical_sigma_rejects_pauli_atom_in_body`: a genuine Pauli
   atom reaching the classical path (which should never happen given
   decision above, but verified as a safety net) raises a clear error.
7. Full regression sweep: 1523 passed (up from 1518). Spec verification:
   100.00% (161/161).

## Exit criteria

- [x] `Sigma (i In 0..n-1) { <classical expr> }` and `Pi (...)` evaluate
  as literal classical Int/Float folds, both as a top-level bind and as a
  sub-expression inside a larger boolean/arithmetic expression.
- [x] Multi-binding with a guard folds correctly, matching the parser's
  own nested-`OpBinder` shape.
- [x] A genuine Pauli/Operator atom reaching this path fails with a clear
  diagnostic rather than silently misbehaving.
- [x] Full regression sweep passes (1523); spec verification 100.00%.
