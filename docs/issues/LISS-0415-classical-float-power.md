# LISS-0415: classical Float power (`^`)

## Metadata

- Local issue ID: LISS-0415
- Status: complete
- Type: Feature Path (`compiler/staqex/parser.py`, `compiler/staqex/ast_nodes.py`
  reused unchanged, `compiler/staqex/typecheck.py`,
  `compiler/staqex/runtime/evaluator.py`)
- Priority: P2
- Planning size: S
- Owner / agent: Claude Code
- Parent: WP-0098 (batch `case-sensitive-keywords-and-sigma-binder`)
- Branch: `batch/case-sensitive-keywords-and-sigma-binder` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

Writing a Sigma-sum coefficient like `1.0 / sqrt(2.0 ^ n)` literally, matching
how the equation reads aloud, needs `^` on classical `Float`/`Int`. Today `^`
(`TokenKind.CARET`) is Operator-DSL-only (`OpPow`, integer exponent only,
`parser.py:3054-3060`), meaning "repeated matrix multiplication" at runtime
(`hamiltonian.py:310-315`) — a completely different semantics than numeric
exponentiation, and not reachable from the general/classical expression
grammar at all (confirmed: no `_power()` level exists between `_unary` and
`_call` in the classical chain).

**Correction found during this Issue's own investigation**: the other half of
the originally-planned scope, `sqrt`, was already shipped by LISS-0356
(`compiler/staqex/stdlib/math_ops.py`'s `MATH_OPS` registry) and works
correctly when used inside a nested expression (`return sqrt(x)`,
confirmed by direct execution). It only fails when used as the *direct* RHS
of a top-level bind statement (`Float x = sqrt(4.0)`), because
`evaluator.py:4810-4814`'s `_bind_call` interprets any `math_ops`-named call
at bind-statement position as "map this op over an existing coordinate,"
requiring a `Var` argument — a separate, pre-existing, correct design for a
different use case (`state y = sqrt(x)` mapping over coordinate `x`), not a
bug. The target use case (`^`'s coefficient expression is a sub-expression
inside a larger `Sigma`-binder body, never a bare top-level bind) is
unaffected. No `sqrt` work was needed; scope reduced to `^` only.

## Scope

1. `parser.py`: new `_power()` precedence level between `_unary` and `_call`
   (right-associative, matching standard convention:
   `2.0 ^ 3.0 ^ 2.0` = `2.0 ^ (3.0 ^ 2.0)`), producing a plain `BinOp(op="^",
   ...)` — reusing the existing `BinOp` AST node rather than inventing a new
   one, since `^` needs no different node shape than `+`/`-`/`*`/`/`.
2. `typecheck.py::_infer_binop`: add an `expr.op == "^"` branch in both the
   Classical-operand path and the State-operand path, requiring both operands
   dimensionless (`TYPE_MISMATCH` diagnostic otherwise — dimensioned bases
   raised to a non-integer power are out of scope; this Issue only needs
   `2.0 ^ n` with a dimensionless base and exponent).
3. `runtime/evaluator.py::_apply_op`: add `op == "^"` computing `l ** r`.

## Explicitly out of scope

- `sqrt` (already shipped, LISS-0356 — see correction above).
- Dimensioned-base `^` (e.g. `Energy ^ 2`) — deferred; not needed for the
  Sigma-binder coefficient use case this batch targets.
- Any change to `OpPow`/Operator-DSL `^` semantics (unaffected, untouched).

## Design verification performed

1. Confirmed `sqrt` already works for the target use case (nested expression,
   not top-level bind) by direct execution before writing any new code.
2. Confirmed no existing classical `^` path exists anywhere in the grammar
   before adding one (`grep` for `CARET` across `parser.py` — exactly one
   match, inside `_op_power`, the Operator-DSL-only path).
3. `2.0 ^ 8` (Int exponent), `2.0 ^ n` (Int variable exponent), and
   `(1.0 / sqrt(2.0 ^ n))` (the actual target coefficient expression) all
   parse, typecheck, and evaluate to the correct numeric value.
4. Regression guard: existing Operator-DSL `^` (`OpPow`, e.g.
   `objective_hamiltonian`-style Hamiltonian construction) unaffected —
   confirmed full suite stays green.

## Exit criteria

- [x] `2.0 ^ n` (dimensionless Float base, Int exponent) parses, typechecks,
  and evaluates correctly.
- [x] Dimensioned base raised via `^` produces a clear `TYPE_MISMATCH`
  diagnostic, not a silent wrong answer.
- [x] Existing Operator-DSL `^`/`OpPow` completely unaffected.
- [x] Full regression sweep passes; spec verification 100.00%.
