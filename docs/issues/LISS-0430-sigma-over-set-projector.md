# LISS-0430: `Sigma (x In F) { |x><x| }` — Sigma over a general `Set` domain + bound-variable projector

## Metadata

- Local issue ID: LISS-0430
- Status: complete
- Type: Feature Path (`compiler/staqex/lexer.py`, `compiler/staqex/parser.py`,
  `compiler/staqex/typecheck.py`, `compiler/staqex/runtime/evaluator.py`)
- Priority: P1
- Planning size: XL (real pre-existing lexer bug fix, new Operator-value
  resolution path, Pauli-Z decomposition) — the largest single Issue in
  this batch
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

$P_F=\sum_{x\in F}\lvert x\rangle\langle x\rvert$ — the last piece needed
before $F$ (LISS-0429) can actually be turned into the literal projector
operator the equation names.

## Real, pre-existing bug found and fixed during Green (blocking, not incidental)

`|x><x|` (ADR 0169's own "Slice D" outer-product/matching-label-projector
syntax) **never actually worked**, for any use, anywhere — confirmed by
lexing it directly: `KET('|x>')`, then `LT('<')` (not `BRA`), then
`IDENT('x')`, then a `LEX_ERROR` on the trailing `|` (mis-parsed as a
fresh, unterminated ket-open). Root cause: `_can_start_primary()`
(the lexer's own heuristic for whether `<` may start a bra literal)
listed `TokenKind.KET` among the tokens that block a fresh primary
expression from starting — meaning a `<` immediately following a closed
ket was *always* read as a plain less-than operator, never as the start
of `<x|`. `_ket_or_outer` was clearly written expecting this to work
(its own logic explicitly checks for a following `BRA` token), but the
lexer could never actually produce one in this position. A full corpus
grep confirmed **zero** existing uses of `>` immediately followed by `<`
anywhere in `examples/`/`tests/`, so this was dead, unreachable code, not
a feature anything relied on working the old way. Fixed by removing
`TokenKind.KET` from the blocking set — the pre-existing space-guard
(`_peek_at(1) not in {whitespace}`) already protects the ordinary,
spaced comparison case (`|k> < 5`) regardless.

## Scope

1. `lexer.py::_can_start_primary`: the fix above.
2. `parser.py::_op_primary`: gained `KET` recognition (delegating to the
   *same* `_ket_or_outer` the general expression grammar already uses),
   previously entirely absent from the Operator-DSL's own body grammar.
3. `evaluator.py::_resolve_operator_tree`'s existing `OpBinder` case
   gained a new branch: when `kind == "Sigma"` and the domain is a named
   `OpVar` (not the pre-existing `Index`/`{0,1}^n` shapes), it is *not*
   sent through the static `_lower_operator_expr` path (which already
   fails gracefully there via a caught `ValueError`, confirmed by reading
   `lower_finite_binder_operators`'s own `except (IndexError, ValueError):
   continue`) — instead:
   - `_lookup_set_comprehension_value(name)`: finds `name`'s defining
     `Set name = { ... }` statement in `main()` and **re-evaluates** its
     `SetComprehension` directly (via LISS-0429's own
     `_eval_set_comprehension`), rather than threading the live `Joint`
     through the entire Operator-resolution call chain just to read back
     one already-computed, world-independent value. Also returns the
     domain's own `n` (needed only for the empty-`F` case below).
   - `_build_projector_sum_operator(elements, bound_variable, body,
     domain_width)`: verifies `body` is exactly `projector(Var(bound_
     variable))` (the parser-verified desugaring of `|x><x|`, matching
     `KetSumBinder`'s own precedent of restricting the body shape rather
     than accepting an arbitrary expression), then for each concrete
     `x` in `elements` builds
     $\lvert x\rangle\langle x\rvert=\bigotimes_i\frac{I+(-1)^{x_i}Z_i}{2}$
     as a literal `OpBin(*)/OpBin(+)/OpPauli` tree — **not** manually
     expanded into a flat Pauli-string sum. `hamiltonian.py`'s existing
     matrix compiler already reduces arbitrary such trees to a matrix
     (proven by the already-shipped `objective_hamiltonian`'s own
     `Z[i] * Z[j]` coupling term), so the tensor-product structure is
     left for that existing, tested path to resolve. Sums the per-`x`
     terms with `+`. Empty `F` returns `OpIdentity(kind="Sigma",
     acting_space=domain_width)` — the additive identity (zero operator),
     matching $\sum_{x\in\emptyset}=0$.
4. `typecheck.py`: `_check_operator_expr`'s named-domain validation
   (`domain_ty.kind not in {"Meta", "Discrete"}`) rejected `F` outright —
   found via direct testing (`BINDER_DOMAIN_ERROR: F is not a finite
   semantic domain`), not assumed. Traced `F`'s *actual* inferred type by
   reading `checker.env` directly: `Ty("State", "Set", DIMLESS)`, not the
   `Ty("Classical", "Set", DIMLESS)` LISS-0429's own `_infer_inner` case
   returns — the generic Type-First fallback for an unrecognized type
   head (`Set` isn't in any of the specialized branches `_check_state_
   bind`-equivalent code has) wraps the payload in `State` kind
   regardless. Fixed by checking `domain_ty.payload == "Set"` alone
   (kind-independent), the reliable signal across both shapes.

## Design verification performed (matrix-level, not just "doesn't crash")

Verification pulls `self.operators["P_F"]` after `run_unit` and compiles
it directly via `hamiltonian.compile_hamiltonian`, comparing the full
matrix against hand-computed ground truth — not routed through `apply`/
`project` (which would conflate this Issue's own correctness with S9's
not-yet-shipped general-Operator `project` support, and `apply` requires
unitary, which a genuine projector generally is not).

1. `test_ket_bra_lexes_as_projector_not_comparison`: the lexer fix itself.
2. `test_projector_matrix_matches_hand_computed_diagonal_n2`: $n=2$,
   $F=\{(1,0),(1,1)\}$ → diagonal exactly `[0,0,1,1]` (big-endian basis
   ordering), all off-diagonal entries exactly zero.
3. `test_projector_matrix_matches_target_shape_n3`: the full confirmed
   S02 `F` (all three LISS-0429 conditions together, $n=3$) → diagonal
   exactly `[0,0,0,0,0,1,1,0]`, matching `F={(1,0,1),(1,1,0)}` (indices
   5, 6) — the same ground truth LISS-0429's own test independently
   verified via `Measure F`, now cross-checked from the *operator* side.
4. `test_empty_set_gives_the_zero_operator`: confirms the `OpIdentity`
   empty-domain path materializes to the literal zero matrix, not a
   crash.
5. `test_sigma_over_set_body_must_be_bound_variable_projector`: a
   non-`|x><x|` body (e.g. a bare Pauli atom) fails with a clear error
   rather than being silently misinterpreted.
6. Full regression sweep: 1549 passed (up from 1544). Spec verification:
   100.00% (161/161). Full `.sqx` corpus `staqex check` clean (the lexer
   fix's blast radius was re-verified against the whole corpus, not just
   the targeted grep from before the fix).

## Exit criteria

- [x] `|x><x|` lexes and parses correctly (real pre-existing bug fixed).
- [x] `Sigma (x In F) { |x><x| }` resolves to the correct multi-term
  Pauli-decomposed projector operator, verified at the matrix level
  against hand-computed ground truth at two scales (n=2, n=3).
- [x] Empty `F` gives the zero operator.
- [x] Full regression sweep passes (1549); spec verification 100.00%;
  full `.sqx` corpus `staqex check` clean.
