# LISS-0426: `||State||` norm notation + `State / Float` division

## Metadata

- Local issue ID: LISS-0426
- Status: complete
- Type: Feature Path (`compiler/staqex/ast_nodes.py`, `compiler/staqex/parser.py`,
  `compiler/staqex/typecheck.py`, `compiler/staqex/runtime/evaluator.py`)
- Priority: P1
- Planning size: M (new lexical disambiguation, new AST node, new bind path)
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

$\lvert\psi_{sel}\rangle=P_F\lvert\psi_0\rangle/\lVert P_F\lvert\psi_0\rangle\rVert$
is a literal fraction with an explicit norm in the denominator — not a
named function `normalize(...)`, which was this design's own first
attempt and was rejected for the same reason `is_feasible`/`count_selected`
etc. were: it names an operation the equation spells with symbols, not a
word.

## Real parsing ambiguity found and fixed during Green

`||` is lexed as a single token (`TokenKind.OR`) unconditionally — the
lexer cannot distinguish "logical or" from "norm bars," so `||x||`
becomes the token stream `OR IDENT(x) OR`. This is resolved purely by
**grammatical position**, matching how `|x>`/`<x|` are already
disambiguated: `_primary()` (where a *new* operand is expected) treats a
leading `OR` as the start of a norm expression; binary `||` is only ever
consumed by `_logical_or()`'s own loop, between two *already-parsed*
operands.

This alone was not sufficient: parsing `||a||`'s own *inner* expression
(`a`) via the ordinary `_expression()` path let `_logical_or()` see the
norm's own **closing** `||` and try to consume it as a binary operator
continuing the inner expression, producing `function result expression
must be the final item in a block` instead of a real parse. Found by
actually running `||a||` end-to-end, not just reading the grammar. Fixed
with a depth counter (`self._norm_bars_depth`, mirroring the existing
`_commutator_bracket_context` precedent for `[A, B]` vs commutator
disambiguation) that suppresses `_logical_or`'s binary-`||` matching only
while parsing between an unclosed norm-bars pair.

A second, separate gap: the typechecker's `_infer_inner` has no
`NormExpr` case, so it silently fell through to the generic
`Ty("State", "Any", DIMLESS)` fallback — wrongly typing a norm as a
*State* rather than the classical Float it actually is. Found by tracing
`_infer_inner`'s exact fallback logic (not assumed), not by a visible
test failure — the loose Float-binding path that already tolerated
LISS-0424's under-typed classical Sigma also tolerated this, so nothing
crashed, but the type was wrong. Fixed with an explicit `NormExpr` case
requiring a State-kind operand and returning `Ty("Classical", "Float",
DIMLESS)`.

A third gap, found while writing tests: the evaluator only handled
`NormExpr` as the RHS of a `/` division (the target use case), not as a
**standalone top-level bind** (`Float n = ||a||`) — `_bind` had no
`NormExpr` case at all, raising `cannot bind expr NormExpr`. Fixed by
adding one, and refactoring the shared "bind sub-expression, sum
`|amp|²` across worlds, sqrt" logic into `_compute_norm`, reused by both
the standalone-bind and the division path.

## Scope

1. `ast_nodes.py`: new `NormExpr(state: Expr, span)`.
2. `parser.py`: `_primary()` recognizes a leading `OR` token as
   `||state_expr||`; `_norm_bars_depth` counter added to `__init__` and
   checked in `_logical_or()`.
3. `typecheck.py`: `NormExpr` case in `_infer_inner` — State-kind operand
   required, returns Classical Float.
4. `evaluator.py`: `_compute_norm(joint, state_expr) -> float` (shared
   helper); `_bind`'s `NormExpr` case (standalone bind, via
   `joint.bind_const`); `_bind`'s new `BinOp(op="/", rhs=NormExpr)` case
   dispatching to `_bind_state_divided_by_norm`, which binds the
   numerator and the norm's own inner expression as **two independent
   `_bind` calls** — matching the equation's own literal repetition of
   $P_F\lvert\psi_0\rangle$ in both the numerator and inside
   $\lVert\cdot\rVert$, not an optimization that reuses one computation.

## Explicitly out of scope

- `NormExpr` (or classical Sigma) as an arbitrary sub-expression reachable
  only through `_eval_value` (which has no `Joint` access, so cannot
  itself compute a multi-world amplitude sum) — e.g. `Bool ok = ||a|| >
  0.5` used inside a larger expression tree beyond the two supported
  shapes (top-level bind; RHS of `/`). The confirmed final design for S02
  step 2 never needs this broader form.
- `project`'s own implicit renormalization removal — that is LISS-TBD-S9's
  scope; this Issue only builds the explicit `/ ||...||` mechanism the
  divison will rely on instead.

## Design verification performed

1. Confirmed the exact lexer behavior (`||` always one `OR` token) by
   reading `lexer.py` directly, not assumed.
2. `test_norm_of_a_ket_lit_is_one`: `||\|0>||` = 1.0.
3. `test_norm_of_unnormalized_literal_ket_sum_matches_sqrt_of_total_probability`:
   `||Sigma (x In {0,1}^2) { |x> }||` = 2.0 = $\sqrt{4}$, cross-checking
   LISS-0422's own "bare Sigma is unnormalized, total probability $2^n$"
   finding from the *norm* side, not just the probability side.
4. `test_state_divided_by_its_own_norm_is_a_literal_normalize`: the exact
   target shape, `X / ||X||` with `X` written twice (matching the
   equation), correctly re-normalizes an unnormalized 4-outcome equal
   superposition to total probability 1.0, 0.25 per outcome.
5. `test_binary_or_is_unaffected_by_norm_bars_disambiguation`: `a || b`
   (ordinary logical or) still parses and evaluates correctly — the depth
   counter doesn't leak outside an unclosed norm.
6. `test_norm_requires_a_state_operand`: `||<Int>||` is a `TYPE_MISMATCH`,
   not silently accepted.
7. Full regression sweep: 1532 passed (up from 1527). Spec verification:
   100.00% (161/161). Full `.sqx` corpus `staqex check` clean.

## Exit criteria

- [x] `||state_expr||` parses (disambiguated from binary `||` purely by
  grammatical position) and evaluates to $\sqrt{\sum\lvert c_x\rvert^2}$.
- [x] `<state_expr> / ||<state_expr>||` correctly renormalizes, matching
  the equation's own literal repetition rather than reusing one bind.
- [x] Ordinary `||` (logical or) is unaffected.
- [x] `||...||` requires a State operand and types as Classical Float.
- [x] Full regression sweep passes (1532); spec verification 100.00%;
  full `.sqx` corpus `staqex check` clean.
