# LISS-0427: `ForAll` binder for $\forall$

## Metadata

- Local issue ID: LISS-0427
- Status: complete
- Type: Feature Path (`compiler/staqex/parser.py`, `compiler/staqex/runtime/evaluator.py`)
- Priority: P1
- Planning size: S (reuses LISS-0424's classical `OpBinder` fold machinery)
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

$\forall\,i,j\in\{0,\ldots,n-1\},\,i<j:\ x_ix_j=1\Rightarrow C_{ij}=1$
needs a literal universal quantifier — Bool-valued, true iff the body
holds for every domain combination satisfying the guard.

## Scope

Reuses `OpBinder` as its AST shape (a third valid `kind` string
alongside `"Sigma"`/`"Pi"`, not a new node) and LISS-0424's classical
fold machinery (`_eval_classical_op_binder`), which already handled
multi-binding recursion, guards, and the shared `_eval_op_expr_classical`
leaf evaluator. `ForAll` folds with logical AND, short-circuiting on the
first `False`, rather than `+`/`*`.

1. `parser.py`: `"ForAll"` added to `_OPERATOR_DSL_RESERVED_ATOMS` and
   both `Sigma`/`Pi` recognition sites (general-expression `_primary()`
   and Operator-DSL `_op_primary()`), reusing `_op_binder(kind, sp)`
   unchanged apart from the fix below.
2. `evaluator.py`: `_eval_classical_op_binder` generalized from a
   `Sigma`-or-`Pi` binary choice to a three-way `kind` dispatch
   (`Sigma`→`+`, `Pi`→`*`, `ForAll`→short-circuiting logical AND).

## Real pre-existing bug found and fixed during Green

`_op_binder`'s `{0,1}^n`-domain dispatch
(`if isinstance(domain, SetPowerDomain):`) never checked `kind` at all —
so `Pi (x In {0,1}^n) { |x> }` would *also* have silently become a
`KetSumBinder` (which doesn't even record `kind`, so it always sums,
never products). This predates this Issue (LISS-0420 built `KetSumBinder`
for `Sigma` specifically, but the dispatch condition was never narrowed
to `kind == "Sigma"`) and was never caught because no shipped code used
`Pi`/`ForAll`/`Min` with a `{0,1}^n` domain — found while wiring `ForAll`
into the same dispatch point, not from a failing test. Fixed by narrowing
the condition to `kind == "Sigma"`; `Pi`/`ForAll`/`Min` with a `{0,1}^n`
domain now correctly fall through to the general `OpBinder` path, which
in turn correctly *rejects* it with a clear error (classical Sigma/Pi/
ForAll only support bare-range domains) rather than silently
mis-evaluating.

## Explicitly out of scope

- `ForAll` over a `{0,1}^n`/`Set` domain — not needed by the confirmed
  target design (only bare ranges), and the underlying classical fold
  only supports `IndexDomain` regardless of kind (LISS-0424's own scope
  boundary).

## Design verification performed

1. `test_forall_true_when_all_elements_satisfy_the_body` /
   `test_forall_false_when_one_element_fails`: basic truth cases.
2. `test_forall_target_shape_pairwise_implies_over_state_coordinate`: the
   exact target shape — `ForAll (i In D1, j In D2) where i<j {
   (x[i]*x[j]==1) Implies (...) }` over `prepare_selection(3)` — cross-
   checked against all 8 patterns hand-enumerated (2/8 False, 6/8 True),
   not just "doesn't crash."
3. `test_pi_over_set_power_domain_no_longer_silently_becomes_a_ket_sum`:
   confirms the fix — a non-`Sigma` kind with `{0,1}^n` now fails loudly
   instead of silently mis-evaluating.
4. Full regression sweep: 1536 passed (up from 1532). Spec verification:
   100.00% (161/161).

## Exit criteria

- [x] `ForAll (i In D1[, j In D2, ...]) [where G] { body }` evaluates as
  a Bool-valued universal quantifier, multi-binding and guards included.
- [x] Pre-existing `{0,1}^n`-dispatch gap (ignoring `kind`) fixed.
- [x] Full regression sweep passes (1536); spec verification 100.00%.
