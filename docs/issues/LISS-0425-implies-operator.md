# LISS-0425: `Implies` keyword operator for $\Rightarrow$

## Metadata

- Local issue ID: LISS-0425
- Status: complete
- Type: Feature Path (`compiler/staqex/parser.py`, `compiler/staqex/typecheck.py`,
  `compiler/staqex/runtime/evaluator.py`)
- Priority: P1
- Planning size: S (one new infix operator, two grammars)
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

$x_ix_j=1\Rightarrow C_{ij}=1$ needs a literal implication operator.
Rewriting $\Rightarrow$ as $\lnot A\lor B$ (as an earlier design sketch
did) is itself a translation the equation never wrote — the same class of
gap as everything else in this batch.

## Design decision

`->` and `=>` are both already taken — confirmed by reading `tokens.py`,
not assumed: `ARROW` (`->`) is used for function return types *and*
lambda expressions; `FAT_ARROW` (`=>`) is used for match arms (ADR 0197 /
LISS-0382). Reusing either would collide. `Implies` follows this
project's own established convention of a capitalized English name for a
blackboard symbol (`Sigma`, `Pi`, `In`) — a **contextual keyword**, like
`Sigma`/`Pi` themselves (an `IDENT` lexeme check, not a new reserved
`TokenKind`), so it stays available as an ordinary identifier everywhere
else.

## Real gap found and fixed during Green

`Implies` needed to work in **two separate grammars**, not one — found by
testing the actual target shape, not just the general case:

1. The general expression grammar (`_expression()` → ... → `_logical_or()`),
   for plain code like `Bool r = a Implies b`.
2. The Operator-DSL's own, *separate* expression grammar
   (`_op_expression()`), used by `Sigma`/`Pi` bodies (and the classical
   form LISS-0424 just added) — because the target use case,
   `(x[i]*x[j]==1) Implies (C[i][j]==1)`, appears **inside** a Sigma/
   ForAll/Min body, which never touches the general grammar at all.
   Before this fix, `Operator`-DSL bodies could not even reach `&&`/`||`
   (only the separate `where`-guard grammar, `_op_guard`, had those) — so
   `_op_expression()` was changed to route through a new `_op_implies()`
   wrapping `_op_guard()`, unifying body and guard expressiveness in one
   pass rather than maintaining two divergent chains. The `where` clause
   itself was updated to call `_op_implies()` too, for consistency (a
   guard gains `Implies` as well, though not required by the immediate
   use case).

## Scope

1. `parser.py`: new `_implies()` (general grammar, between `_pipe()` and
   `_logical_or()`) and `_op_implies()` (Operator-DSL grammar, now what
   `_op_expression()` and the `where`-clause parser both call), both
   producing `BinOp(op="Implies", ...)` / `OpBin(op="Implies", ...)`
   respectively — lowest precedence, matching implication's usual
   looser-than-conjunction binding.
2. `typecheck.py`: `"Implies"` added alongside `"&&"`/`"||"` in both the
   Classical and State Bool-Bool→Bool typing rules.
3. `evaluator.py`: `_apply_op` (general classical `BinOp` evaluation) and
   `_eval_op_expr_classical` (LISS-0424's classical Operator-DSL
   evaluator) both gained an `"Implies"` case (`not lhs or rhs`).

## Design verification performed

1. Confirmed via direct source read (not assumed) that `->`/`=>` are both
   already reserved for unrelated purposes before choosing `Implies`.
2. `test_implies_truth_table_in_general_expression_position`: all four
   truth-table rows.
3. `test_implies_works_inside_a_classical_sigma_body`: the actual target
   shape, `Sigma (i In 0..1) { (i==0) Implies (i<5) }` = 1+1 = 2
   (hand-verified: i=0 → True⇒True=True; i=1 → False⇒True=True vacuously).
4. `test_implies_lower_precedence_than_and_or`: `a && b Implies c` parses
   as `(a && b) Implies c`, not `a && (b Implies c)`.
5. `test_existing_arrow_and_fat_arrow_are_unaffected`: function return
   types (`-> Bool`) still work unchanged.
6. Full regression sweep: 1527 passed (up from 1523). Spec verification:
   100.00% (161/161).

## Exit criteria

- [x] `A Implies B` works in ordinary classical expressions and inside
  Operator-DSL binder bodies/guards alike.
- [x] `->`/`=>` are unaffected.
- [x] Correct precedence (lowest, below `&&`/`||`).
- [x] Full regression sweep passes (1527); spec verification 100.00%.
