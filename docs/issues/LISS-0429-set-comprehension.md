# LISS-0429: `Set F = { x In D : cond1, cond2, ... }` comprehension

## Metadata

- Local issue ID: LISS-0429
- Status: complete
- Type: Feature Path (`compiler/staqex/ast_nodes.py`, `compiler/staqex/parser.py`,
  `compiler/staqex/typecheck.py`, `compiler/staqex/runtime/evaluator.py`)
- Priority: P1
- Planning size: M (new AST node, new lexical disambiguation, new evaluation)
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

$F=\{x\in\{0,1\}^n\mid\text{cond}_1,\ \text{cond}_2,\ \text{cond}_3\}$ is a
first-class set-builder value the equation references directly ($x\in F$
in $P_F=\sum_{x\in F}\lvert x\rangle\langle x\rvert$) — Staqex had no way
to construct or name such a value at all before this Issue.

## Scope

1. `ast_nodes.py`: new `SetComprehension(variable, domain, conditions:
   list[OpExpr], span)`.
2. `parser.py`: `_primary()`'s existing `{` handling (already
   disambiguating bare-block/anticommutator/`{0,1}^n`) gained a third
   case — a 2-token lookahead (`{` IDENT `In`) unambiguously identifies a
   comprehension, since neither an anticommutator operand nor a
   set-power label list can be immediately followed by `In`. New
   `_set_comprehension()`: reuses `_binder_domain()` for `D` and
   `_op_implies()` for each comma-separated condition — the
   Operator-DSL expression grammar, needed because conditions require
   `x[i]`-style indexing (`OpIndexed`), which the general expression
   grammar does not support (confirmed during LISS-0424).
3. `typecheck.py`: `SetComprehension` → `Ty("Classical", "Set", DIMLESS)`.
4. `evaluator.py`: `_eval_set_comprehension` enumerates the domain
   (`{0,1}^n` via `itertools.product`, matching `_bind_ket_sum_binder`'s
   own enumeration) and keeps elements where **every** condition holds
   (comma = AND, the same convention LISS-0428 established for `where`
   guards). Reuses `_eval_op_expr_classical` for conditions. `_bind`
   gained a `SetComprehension` case (`Set F = {...}` is a pure classical
   computation — the comprehension's own bound variable never touches
   per-World `assign` data, so no `Joint` access is actually needed
   beyond the uniform `bind_const` wrapper).

## Real gap found and fixed during Green

Conditions like `Sigma (i In 0..n-1) { x[i] } == 3` are themselves
`OpBin(op="==", lhs=OpBinder(...), rhs=OpLit(3))` — a nested `Sigma`/
`ForAll`/`Min` **inside** a larger classical expression. `_eval_op_expr_
classical` (LISS-0424) had no case for `OpBinder` as a sub-expression —
only `_bind`/`_eval_value` (the two *top-level* entry points) dispatched
to it. Found while integration-testing the actual target `F` (all three
S02 conditions together), not from an isolated unit test. Fixed by adding
an `OpBinder` case to `_eval_op_expr_classical` itself, delegating back to
`_eval_classical_op_binder` — closing the recursion so nested binders
work at *any* depth, not just as the two previously-wired top-level
shapes.

## Explicitly out of scope

- A bare-range `D` (e.g. `{ i In 0..n-1 : ... }`) — the confirmed target
  design only ever uses `{0,1}^n`; `_eval_set_comprehension` raises a
  clear error for any other domain shape rather than silently
  mis-handling it.

## Design verification performed

1. `test_single_condition_filters_the_set_power_domain` /
   `test_comma_separated_conditions_mean_and`: basic cases.
2. `test_target_shape_all_three_s02_f_conditions_together`: the full
   confirmed `F` — Sigma count + ForAll pairwise-Implies + Min diversity,
   all three comma-joined — run directly against `n=3`'s 8 patterns and
   compared to the hand-enumerated result `{(1,0,1), (1,1,0)}` (excluding
   `(0,1,1)` for violating the pairwise condition), not just "doesn't
   crash." This is the first point in the batch where all of LISS-
   0424/0425/0427/0428/0429 were exercised together as one integrated
   expression, matching the actual shape `main_selection.sqx` will use.
3. `test_empty_result_when_no_element_satisfies_all_conditions`: a
   contradictory condition pair correctly yields `()`.
4. Full regression sweep: 1544 passed (up from 1540). Spec verification:
   100.00% (161/161).

## Exit criteria

- [x] `Set F = { x In {0,1}^n : cond1, cond2, ... }` evaluates to the
  tuple of matching elements, comma meaning AND.
- [x] Conditions may themselves contain nested `Sigma`/`Pi`/`ForAll`/
  `Min` (the recursion gap found and fixed during Green).
- [x] The full confirmed S02 `F` (all three conditions together) verified
  against hand-enumerated ground truth.
- [x] Full regression sweep passes (1544); spec verification 100.00%.
