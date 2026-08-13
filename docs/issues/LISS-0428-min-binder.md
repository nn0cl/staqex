# LISS-0428: `Min` binder for $\min$, comma-separated `where` guard

## Metadata

- Local issue ID: LISS-0428
- Status: complete
- Type: Feature Path (`compiler/staqex/parser.py`, `compiler/staqex/runtime/evaluator.py`)
- Priority: P1
- Planning size: S (reuses LISS-0424/0427's classical `OpBinder` fold machinery)
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

$\min_{i<j:\,x_ix_j=1}D_{ij}\ge\theta$ needs a literal minimum-aggregate
binder. Its subscript also settles a real question this batch flagged
earlier (LISS-0424's own "explicitly out of scope" note): the guard
"$i<j:\,x_ix_j=1$" is comma/colon-juxtaposed, not `&&`-joined — the same
convention `Set F`'s own condition list uses.

## Scope

1. `parser.py`: `"Min"` added to `_OPERATOR_DSL_RESERVED_ATOMS` and both
   `Sigma`/`Pi`/`ForAll` recognition sites, reusing `_op_binder` (a
   fourth `kind` value, still the same `OpBinder` node). New
   `_op_guard_list()` — comma-separated `_op_implies()` terms folded into
   the same `OpBin(op="&&", ...)` shape writing `&&` explicitly already
   produces — is now what the `where` clause calls (previously
   `_op_implies()` directly), so **every** binder's guard (`Sigma`, `Pi`,
   `ForAll`, `Min`) gained comma-as-AND, not just `Min`'s.
2. `evaluator.py`: `_eval_classical_op_binder` generalized to a four-way
   `kind` dispatch. `Min` folds with `min(acc, term)`, using `+infinity`
   as the identity value (see decision below) — no new evaluator work was
   needed for the comma-guard itself, since it folds into the *same*
   `OpBin(op="&&")` shape the existing guard evaluation already handles.

## Design decision: empty-guard-match behavior (previously left open)

WP-0099's own investigation flagged this explicitly as undecided. Decided
now: **`Min` over a guard that matches nothing evaluates to
$+\infty$** — the standard fold identity for minimum (matching `Sigma`'s
`0` and `Pi`'s `1`), not a `KernelError`. This is not an arbitrary choice:
it reproduces the *exact* behavior of the Python code this whole
predicate is transcribed from (`_bind_feasible_predicate`/
`host/scoring.py::is_feasible`) — `if pairs and min(diversity[i][j] for
i, j in pairs) < diversity_threshold: return False` — when no pair is
selected, the diversity check is skipped entirely (vacuously satisfied),
never a hard failure. `+infinity >= theta` reproduces that same vacuous
pass.

## Design verification performed

1. `test_min_over_a_single_binding`: basic case.
2. `test_comma_separated_guard_conditions_mean_and`: hand-verified
   against the only two (i,j) pairs satisfying `i<j, i+j>3` among
   `0..3`.
3. `test_min_over_empty_guarded_domain_is_vacuously_satisfied`: confirms
   the $+\infty$ decision produces the intended vacuous pass.
4. `test_min_target_shape_diversity_threshold_over_state_coordinate`: the
   exact target shape — `Min (i In D1, j In D2) where i<j, x[i]*x[j]==1
   { D[i][j] } >= theta` over `prepare_selection(3)` — cross-checked
   against all 8 hand-enumerated patterns (2/8 False, 6/8 True), not just
   "doesn't crash."
5. Full regression sweep: 1540 passed (up from 1536). Spec verification:
   100.00% (161/161).

## Exit criteria

- [x] `Min (i In D1[, ...]) where G { body } >= theta` evaluates
  correctly, multi-binding included.
- [x] Comma-separated guard conditions mean AND, for every binder kind
  (`Sigma`/`Pi`/`ForAll`/`Min`), matching the equation's own convention.
- [x] Empty-guard-match behavior decided and verified ($+\infty$,
  matching the original Python predicate's vacuous-pass semantics).
- [x] Full regression sweep passes (1540); spec verification 100.00%.
