# LISS-0420: unify `sum`/`product` into `Sigma`/`Pi`, State-typed ket-sum

> **Amended by [LISS-0422](LISS-0422-sigma-literal-unnormalized-correction.md).**
> This Issue's ket-sum was shipped as self-normalizing (equal probability
> weight per branch). Adjudicator review during LISS-0421 found this wrong
> against the bare blackboard `Sigma` symbol, which denotes a literal,
> unnormalized sum — normalization is the equation's own separate,
> explicit coefficient, not something `Sigma` should supply implicitly.
> LISS-0422 corrected `_bind_ket_sum_binder` accordingly; "Hard Stop 2" and
> the "self-normalizing" framing below are the historical record of the
> (incorrect) original decision, kept as-is rather than rewritten.

## Metadata

- Local issue ID: LISS-0420
- Status: complete
- Type: Feature Path (`compiler/staqex/ast_nodes.py`, `compiler/staqex/parser.py`,
  `compiler/staqex/typecheck.py`, `compiler/staqex/runtime/evaluator.py`,
  `compiler/staqex/finite_binder.py`, `compiler/staqex/runtime/hamiltonian.py`,
  `compiler/staqex/runtime/sparse_pauli.py` + scripted corpus migration)
- Priority: P1
- Planning size: XL (new AST/typecheck/evaluator capability, not a pure
  rename — the capstone of WP-0098)
- Owner / agent: Claude Code
- Parent: WP-0098 (batch `case-sensitive-keywords-and-sigma-binder`)
- Branch: `batch/case-sensitive-keywords-and-sigma-binder` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

Unify the Operator-DSL `sum`/`product` binder with a new State-typed
"ket-sum" capability under one `Sigma`/`Pi` keyword pair, closing the gap
this whole batch originated from: Staqex had no way to write a State as a
literal sum over basis kets
($\lvert\psi_0\rangle=\frac{1}{\sqrt{2^n}}\sum_{x\in\{0,1\}^n}\lvert x\rangle$).

## Two Hard Stops during this Issue (real, unanticipated design decisions)

Per CLAUDE.md's Hard Stop rule, both surfaced mid-work and were escalated
rather than resolved unilaterally:

1. **How does `|x>` bind to the loop variable's runtime value?** The
   target syntax `Sigma (x In {0,1}^n) { |x> }` needs `|x>` to mean "the
   ket whose label is the bound variable `x`'s current value" — but
   `KetLit` (ADR 0038) was designed for a fixed, small literal-label
   vocabulary only (`0`/`1`/`+`/`-`/`i`/bitstrings), with no mechanism
   for a bound-variable label. Presented two options (extend `KetLit`'s
   grammar/semantics vs. a separate `ket(x)`-style function form); the
   Adjudicator chose to extend `KetLit`'s scope.

   **Scope actually shipped** (narrower than "fully extend `KetLit`"):
   rather than making `KetLit` accept an arbitrary bound-variable label
   in general, `Sigma`'s ket-sum body is required to be *exactly*
   `|<the bound variable>|` — checked by the parser
   (`_op_binder`: `if str(ket_tok.literal) != variable: raise
   ParseError(...)`) — and the *evaluator* interprets that specific,
   syntactically-verified case by enumerating the domain directly
   (`_bind_ket_sum_binder`), never generically resolving an arbitrary
   ket label against scope at runtime. `KetLit`'s own AST node and
   general-purpose evaluation (`_bind_ket`) are completely untouched.
   A genuinely general "ket parametrized by any bound variable/expression"
   capability remains future work if ever needed elsewhere.

2. **How does the external coefficient `(1.0/sqrt(2.0^n)) *
   Sigma(...)...` get applied at runtime?** Found, by direct execution,
   that `classical_scalar * <State-producing expr>` (e.g. `2.0 * |0>`)
   was not evaluable at all before this Issue (`KernelError: cannot
   evaluate KetLit as value`) — and separately, that `Sigma (x In
   {0,1}^n) { |x> }` alone is *already* self-normalizing (identical
   construction to `prepare_selection(n)`), so an explicit external
   coefficient is mathematically redundant when applied literally.
   Presented the tension (auto-normalize vs. literal-apply-and-allow-
   unnormalized-output); the Adjudicator chose literal application, with
   generalization.

   **Verified consequence, confirmed by direct execution**: `Sigma (x In
   {0,1}^n) { |x> }` alone gives `total probability == 1.0` (matches
   `prepare_selection(8)` exactly); `(1.0/sqrt(2.0^n)) * Sigma (...) {
   |x> }` gives `total probability == (1/2^n)` (the coefficient applied
   as an amplitude scale on top of the already-normalized sum, squaring
   into probability space) — an honest, unnormalized result, matching
   this codebase's own established precedent that the runtime never
   silently enforces normalization (LISS-0410: `apply(Bad, psi)` with a
   non-unitary `Bad` already produced an unnormalized `marginal={1:
   4.0}`, not a `KernelError`). **Recommendation for any future rewrite
   of `main_selection.sqx`'s own step 1** (out of scope for this batch):
   write the ket-sum *without* the redundant external coefficient.

## Scope

1. `parser.py`: `_OPERATOR_DSL_RESERVED_ATOMS` and the `_op_primary`
   dispatch renamed `sum`/`product` → `Sigma`/`Pi`. `_op_binder`'s domain-
   membership keyword changed from lowercase `in` (`TokenKind.IN`) to
   `In` (`TokenKind.IN_SET`, LISS-0416). New `_set_power_domain()` lets
   `_binder_domain()` accept `{0,1}^n` as a binder domain. When the
   domain is a `SetPowerDomain`, `_op_binder` dispatches to the new,
   single-binding-only `KetSumBinder` (body must be a bare `|<bound
   var>>`) instead of the existing multi-binding `OpBinder` path.
2. `parser.py::_primary` (general expression grammar): `Sigma`/`Pi`
   recognized there too (not just inside `_op_primary`), reusing the
   same `_op_binder`, so a State-typed ket-sum is reachable directly from
   `State x = ...` / general-expression position, not just from inside
   an `Operator`-typed context.
3. `ast_nodes.py`: new `KetSumBinder(variable: str, domain:
   SetPowerDomain, span: Span)` — deliberately separate from `OpBinder`
   (not reused), so every existing `OpBinder`-consuming code path
   (typecheck's `_check_operator_expr`, `finite_binder.py`,
   `hamiltonian.py`, QASM lowering, …) is provably unaffected by
   construction, not by care.
4. `typecheck.py`: `KetSumBinder` infers `Ty("State", "Any", DIMLESS)`
   (matching `prepare_selection`'s own inferred type).
5. `runtime/evaluator.py`: `_bind_ket_sum_binder` — structurally
   identical to `_bind_prepare_selection` (equal-weight
   `itertools.product` over the domain's labels). New, narrowly-scoped
   `classical_scalar * <State-producing expr>` amplitude-scaling bind
   path (`_bind_scaled_state`, gated by `_is_state_producing_bind_expr`)
   — see Hard Stop 2's "verified consequence" above for why this is
   deliberately narrow (`KetLit`/`KetSumBinder` only), not a general
   classifier over every State-producing node type.
6. `finite_binder.py`, `runtime/hamiltonian.py`, `runtime/sparse_pauli.py`:
   `OpBinder.kind`/`OpIdentity.kind` string comparisons (`"sum"`/
   `"product"`) updated to `"Sigma"`/`"Pi"` — these consume the *existing*
   Operator-typed binder's `kind` field, unrelated to the new
   `KetSumBinder` node.
7. Scripted corpus migration: the Operator-DSL `sum (i in D) { ... }` /
   `product (i in D) { ... }` binder shape (including its own `in` →
   `In`), matched by a balanced-paren scan requiring the specific
   `IDENT in` shape immediately inside the parens — not a blind
   word-boundary substitution, which would have corrupted Python's own
   `sum(...)`/`itertools.product(...)` builtin calls throughout the host
   scripts and test harness (a real false-positive class found during
   Green, before the migration was run, via a dry-run review).

## Explicitly out of scope

- Per-term coefficients *inside* a State-typed ket-sum body (`Sigma (x
  In {0,1}^n) { w[x] * |x> }`) — would need indexing a classical array
  by a tuple-valued bound variable, a separate future capability. The
  external-coefficient mechanism (Hard Stop 2) covers the *uniform*
  weighting case, which is what this batch's originating example needed.
- Multi-binding State-typed ket-sums (`Sigma (x In D1, y In D2) { ... }`)
  — the target use case is single-variable only.
- Category-B builtin-function renames (unchanged from the batch's
  original scope decision).
- Rewriting `main_selection.sqx` itself to the new syntax — a follow-on
  Issue, per WP-0098's own stated scope.

## Design verification performed

1. Confirmed `Sigma (x In {0,1}^n) { |x> }` alone produces a properly
   normalized (total probability 1.0) equal superposition, and its
   `marginal` is byte-identical to `prepare_selection(n)`'s own output
   for the same `n` and seed — direct cross-check, not just "doesn't
   crash."
2. Confirmed the external-coefficient case's exact numeric consequence
   (probability scales by the coefficient squared, verified via direct
   execution) — this is now the honest, documented, and tested behavior,
   not a discovered-then-ignored surprise.
3. Confirmed the existing Operator-typed `Sigma`/`Pi` binder (single-
   binding, multi-binding with `where` guard, `Pi` product) is byte-for-
   byte unaffected in *behavior*, only spelling — full regression sweep
   is the evidence, not a targeted re-derivation.
4. **Regression found and fixed during Green**: an initial, broader
   `_is_state_producing_bind_expr` (matching `Coin`/`Vacuum`/`WhenExpr`/
   `SuperposeExpr`/`TensorExpr` in addition to `KetLit`/`KetSumBinder`)
   silently reopened a boundary LISS-0273 deliberately closed —
   `Float bad = Coin() * 0.5` must fail (a State-forming call is not a
   valid classical operand), and previously did so because `_eval_value`
   simply could not evaluate `Coin()`. Caught by the full regression
   sweep (`test_liss_0273_classical_call_in_expr_red.py`), not
   anticipated during design. Narrowed to `KetLit`/`KetSumBinder` only —
   both safe to include since nothing pre-existing relied on either
   crashing at this layer.
5. **Corpus migration false-positive found before running**: a dry-run
   review of the `sum`/`product` binder-shape migration found it would
   have matched Python's own `sum(...)`/`itertools.product(...)` builtin
   calls throughout `examples/**/host/*.py` and the test harness — fixed
   by requiring the specific `IDENT in` shape immediately inside the
   parens (the real Operator-DSL binder signature; Python's `sum()`/
   `product()` never has this exact shape) before running the migration,
   not after.
6. Full regression sweep: 1511 passed (up from 1503). Spec verification:
   100.00% (161/161). Full `.sqx` corpus `staqex check` swept clean.

## Exit criteria

- [x] `Sigma (x In {0,1}^n) { |x> }` parses, typechecks, and runs,
  producing a normalized equal superposition identical to
  `prepare_selection(n)`.
- [x] `classical_coefficient * Sigma (...) { |x> }` applies the
  coefficient literally as an amplitude scale (verified numeric
  consequence, documented, tested).
- [x] Existing Operator-typed `Sigma`/`Pi` binder (single/multi-binding,
  guards, `Pi` product) unaffected beyond the `sum`/`product`→`Sigma`/`Pi`
  and `in`→`In` spelling change.
- [x] The LISS-0273 classical/State boundary regression found during
  Green is fixed and regression-guarded.
- [x] Full corpus migrated; full regression sweep passes (1511); spec
  verification 100.00%; full `.sqx` corpus `staqex check` swept clean.
