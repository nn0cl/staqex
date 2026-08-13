# LISS-0434: factory-parameter Sigma domains + per-term struct-attr coefficients

## Metadata

- Local issue ID: LISS-0434
- Status: complete
- Type: Feature Path (`compiler/staqex/runtime/op_attr_elaboration.py`,
  `compiler/staqex/runtime/evaluator.py`; `examples/showcase/S02_drug_discovery/main_selection.sqx`)
- Priority: P2 (literalness/expressiveness gap, not a correctness defect
  in shipped behavior — `objective_hamiltonian` already worked correctly
  with its hardcoded `0..7`/post-hoc `w.activity *` shape; this Issue
  makes it match the blackboard equation literally, per this session's
  own established standard)
- Planning size: M
- Owner / agent: Claude Code
- Parent: none — outside WP-0099's own scope (`main_selection.sqx` steps
  1/3/4/5 were explicitly out of scope there beyond step 2's own
  mechanical needs); a standalone Local Issue, plan-approved via the
  Adjudicator's direct Socratic review and explicit "A。... 書き直して"
  instruction, following the same equation-review discipline WP-0099
  itself was born from
- Branch: (continues on `batch/s02-step2-literal-transcription`, since
  WP-0099's own PR #549 is still open for post-review; this Issue's own
  commits are clearly separated)
- GitHub Issue / PR: (part of PR #549, or a follow-on — see completion
  note)

## Intent

Reviewing step 3's own equation
$$H_{obj}/\text{scale} = w_{activity}\sum_{i=0}^{n-1} \text{activity\_w}_i Z_i + w_{selectivity}\sum_{i=0}^{n-1}\text{selectivity\_w}_i X_i + w_{diversity}\!\!\sum_{0\le i<j\le n-1}\!\! Z_iZ_j$$
against `objective_hamiltonian` (unchanged by WP-0099, since it was out
of that batch's scope) found two real, if previously undiscovered until
directly pointed at, non-literal gaps:

1. `0..7` (four instances) and `Float[8]` (two parameter types) were
   hardcoded, disconnected from `n` — the same width step 1/2 now spell
   symbolically throughout the rest of the file, since LISS-0421 made `n`
   a real, named blackboard quantity there.
2. `w.activity`/`w.selectivity`/`w.diversity` were pulled out of their
   respective `Sigma`s as a post-hoc scale of an already-built Operator
   (`w.activity * z_field`), not written as each Sigma's own per-term
   coefficient the way `activity_w[i]` already was — mathematically
   equivalent by distributivity, but not a literal transcription: every
   other per-term factor lived inside the Sigma; `w_*` being the one
   exception outside it was a real, if invisible-until-pointed-at,
   asymmetry.

## Scope

1. `n: Int` added as an `objective_hamiltonian` parameter; all four
   `0..7` range bounds become `0..n-1` (bare-range binder domains,
   already general per LISS-0423 — no new grammar needed there).
   `Float[8]` (the array *type*) stays a literal fixture-width hardcode:
   `Float[n]` (a function-parameter-referenced array-length type) does
   not parse today (`` `Float[N]…` requires positive integer lengths ``,
   confirmed by direct testing) — a real, deeper, separate compiler gap
   this Issue does not open, disclosed rather than silently worked
   around.
2. `w.activity`/`w.selectivity`/`w.diversity` moved inside their
   respective `Sigma` bodies as literal per-term coefficient factors;
   `return` becomes the plain three-term sum `z_field + x_field +
   coupling`, matching $(\ldots)+(\ldots)+(\ldots)$ exactly.
3. `main_selection.sqx`'s call site passes `n` positionally
   (`objective_hamiltonian(weights, n, activity_w, selectivity_w)`).

## Real bugs found and fixed during Green

Both are pre-existing gaps in `_resolve_operator_factory_call`
(`evaluator.py`), never exercised before because no shipped factory
function had ever combined a *scalar-parameter-bound* `Index` binder
domain with an *array-indexed* body, or a struct-attr coefficient inside
a binder body at all, in the same call:

1. **A factory's own scalar parameter (e.g. `n`) could not bound a
   `Sigma`/`Pi` binder's own `Index` range** (`Sigma (i In 0..n-1)`).
   `_resolve_operator_factory_call` calls `self._resolve_operator_expr`
   on the RAW (unsubstituted) statement first, only folding the call's
   own `local_scalars` into the *result* afterward (via
   `_materialize_op`) — but `_resolve_operator_expr`'s own eager static
   lowering pass tries to resolve the binder's domain bounds in that
   *same* first pass, failing closed
   (`KernelError: cannot lower Operator binder: static Index endpoint
   'n' is not a binder or register size`) before the later substitution
   ever runs. Compounding this,
   `op_attr_elaboration.py::_map_op_tree`'s own `OpBinder` case never
   mapped `domain` at all (only `body`/`guard`) — so even *had*
   substitution run early, it would not have reached `n` inside
   `0..n-1` in the first place. Fixed both: added `_map_binder_domain`
   (folds `IndexDomain.start`/`.end`, recursing through `RevDomain`) to
   `_map_op_tree`'s `OpBinder` case, and reordered
   `_resolve_operator_factory_call` to fold `local_scalars`/struct attrs
   into each `Operator`-typed statement *before* the first resolution
   pass, not only after.
2. **A struct-attr parameter (`w.activity`) could not appear as a Sigma's
   own per-term coefficient**, only as an already-resolved value outside
   the binder (`KernelError: cannot lower Operator binder: binder body
   is outside the accepted Pauli slice` — the eager first pass saw a raw
   `OpAttr` leaf where only a literal/array-indexed/scalar-var
   coefficient was accepted). Fixed by the same reordering: `w.activity`
   is now folded to a literal (via `materialize_op_attrs`) before the
   first resolution pass sees it, not only in the second.
   `extra_arrays` also needed threading into that same first pass
   (`_resolve_operator_expr` gained an `extra_arrays` parameter,
   forwarded to `_lower_operator_value`) — the callee's own
   param-name-rekeyed `Float[N]…` array (LISS-0407) was previously only
   available to the *second* pass, but the first pass now also needs it
   once it succeeds far enough (past the domain fix) to reach the
   array-indexed body.

Both fixes are narrow and additive: `_map_binder_domain` only touches
`IndexDomain`/`RevDomain` (named-Set domains, `OpVar`, are unchanged,
since they carry no `OpExpr` sub-nodes to fold); the reordering in
`_resolve_operator_factory_call` calls the *same* substitution functions
that already ran on the *result*, just also on the *input* — no new
substitution semantics invented.

## Design verification performed

1. `tests/test_liss_0434_factory_scalar_domain_and_attr_coefficient_red.py`
   (4 tests): a factory-scalar-bound single-binder Sigma, a two-binder
   Sigma with a comparison guard (`objective_hamiltonian`'s own coupling
   shape), a struct-attr-as-per-term-coefficient combined with both of
   the above in one call (the exact target shape), and
   `main_selection.sqx`'s own rewritten `objective_hamiltonian` — all
   verified against hand-computed diagonal matrix entries (not just
   "doesn't crash"), matching this whole session's own established
   rigor.
2. `main_selection.sqx` recompiled clean and re-run end to end: selection
   pattern at seed 0 is `(0, 1, 1, 1, 1, 1, 0, 0)` — byte-identical to
   the pre-rewrite hardcoded-`0..7`/post-hoc-`w.activity*` version and to
   the pre-batch baseline LISS-0433 already confirmed, verifying the
   rewrite is a pure literalness improvement, not a physics change.
3. Full regression sweep, spec verification, full `.sqx` corpus
   `staqex check` — see completion note below.

## Exit criteria

- [x] `objective_hamiltonian`'s `0..7`/`Float[8]`-range hardcodes replaced
  with `n`-parameterized `0..n-1`, matching step 1/2's own established
  symbolic-width convention.
- [x] `w_activity`/`w_selectivity`/`w_diversity` written as each Sigma's
  own literal per-term coefficient, not a post-hoc external scale.
- [x] The two real, previously-latent gaps this surfaced in
  `_resolve_operator_factory_call`'s substitution ordering found, fixed,
  and covered by dedicated tests verified against hand-computed ground
  truth.
- [x] `main_selection.sqx` end-to-end output confirmed unchanged
  (byte-identical selection pattern at seed 0).
- [x] `Float[n]` parameterized array-length types confirmed NOT to parse
  today — disclosed as a real, separate, deeper gap, not silently worked
  around or opened as unplanned extra scope in this Issue.
