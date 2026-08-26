# LISS-0412: struct-field coefficients in second-quantized expressions

## Metadata

- Local issue ID: LISS-0412
- Status: complete
- Type: Feature Path (bug fix; `compiler/staqex/parser.py`,
  `compiler/staqex/second_quantization.py`,
  `compiler/staqex/runtime/evaluator.py`,
  `compiler/staqex/backend/qasm/lower.py` — closes a gap in ADR 0206's
  already-Accepted, already-shipped implementation, not a new
  architecture decision, per CLAUDE.md's Bug Triage)
- Priority: P1
- Planning size: `M`
- Owner / agent: Claude Code
- Parent: independent-context source code review, second pass (this
  session, Adjudicator-requested: "個別確認し、できるだけバグを探して" →
  found; "大きいモノから" → this Issue done first)
- Branch: `feature/liss-0412-second-quantization-struct-field-coefficients`
- GitHub Issue / PR: (opened at Completion)

## Intent

A second review pass (after LISS-0410/0411) found the Jordan-Wigner
second-quantization mapping never supported a struct-field coefficient
attached to a fermionic term — two separate, independently-verified
bugs blocking the same physics need (`weights.e0 * create[0] *
annihilate[0]`):

1. **Parser**: `_second_quantized_rhs_is_op_dsl`'s bounded lookahead
   (the heuristic that decides whether a `FermionOperator`/... RHS
   should be parsed as the second-quantized OpDSL grammar) only
   recognized a bare literal or identifier as a leading coefficient
   term — a dotted struct-field chain (`weights.e0`) made it bail after
   `weights` and misroute to the wrong grammar, producing an unrelated
   `PARSE_ERROR: function result expression must be the final item in a
   block`.
2. **Resolution**: even routing around the parser bug with parentheses,
   `second_quantization.py::_scalar_value` didn't recognize `OpAttr` as
   a scalar coefficient at all, failing with
   `SECOND_QUANTIZATION_MAPPING_UNSUPPORTED: \`OpAttr\` is not covered
   by the Jordan-Wigner mapping slice`.

Both fixed together — fixing only one would still leave the natural,
unparenthesized form unusable.

## Scope

1. `parser.py::_second_quantized_rhs_is_op_dsl`: extend the coefficient-
   term lookahead to also consume a `DOT IDENT` suffix chain after a
   leading `IDENT`, so `weights.e0` (and nested `weights.inner.e0`) is
   recognized as one coefficient term the same way a bare identifier
   already was.
2. `second_quantization.py`: add a local `_static_op_attr_float`/
   `_resolve_static_attr_host` helper (deliberately duplicated rather
   than imported from `runtime.op_attr_elaboration` — this module is
   explicitly kept dependency-free of the `runtime` package, per its own
   module docstring) and an `OpAttr` case in `_scalar_value`. Threaded a
   new `objects: dict | None = None` parameter through `_scalar_value` →
   `_expand` → `jordan_wigner_map` → `resolve_mapping_expr` (all four
   functions), mirroring how `scalars` was already threaded.
3. `runtime/evaluator.py::_bind_second_quantized`: pass `self.objects`
   as the new `objects` argument to `resolve_mapping_expr`.
4. `backend/qasm/lower.py::_from_ast_patterns`: moved the
   `collect_static_operator_context(unit)` call (already added by
   LISS-0411 for `op_env` resolution) earlier in the function so its
   `objects` result is also available to the `resolve_mapping_expr` call
   inside the main bind loop — one shared computation, not duplicated.

## Explicitly out of scope

- `finite_binder.py:306`'s own `jordan_wigner_map(substituted,
  span=expr.span)` call (a second-quantized expression found *inside* a
  `sum`/`product` binder body) — this call site doesn't even thread
  `scalars` today (defaults to `None`), a separate, pre-existing,
  undemonstrated limitation. Left unchanged; `objects` defaults to
  `None` there too, matching existing behavior exactly (no regression).
- Struct-field-derived orbital *indices* (`create[weights.i]`) —
  `_orbital_index` is unaffected by this Issue; only *coefficients* were
  in scope (matching the confirmed review finding).
- Bravyi-Kitaev / Boson / Spin mappings — out of scope per this module's
  own existing "Scope" docstring, unaffected by this Issue.

## Design verification performed

1. Confirmed both bugs independently before implementing: the
   unparenthesized form failed with the unrelated `PARSE_ERROR`; the
   parenthesized workaround failed with
   `SECOND_QUANTIZATION_MAPPING_UNSUPPORTED: \`OpAttr\` is not covered`.
2. After the parser fix alone, the unparenthesized form's `PARSE_ERROR`
   was gone but the resolution error remained — confirming the two bugs
   are independent, not two symptoms of one root cause.
3. After both fixes, direct execution confirmed a struct field holding
   `1.0` produces the **identical terminal distribution** to the
   already-working literal `1.0` form — the coefficient genuinely
   reaches the mapped Hamiltonian, not silently dropped or defaulted.
4. Full regression sweep: 1472 passed (up from 1468). Spec verification:
   100.00% (161/161).

## Exit criteria

- [x] `weights.e0 * create[0] * annihilate[0]` (unparenthesized) parses
  without a spurious `PARSE_ERROR`.
- [x] The struct-field coefficient resolves through Jordan-Wigner
  mapping and runs end to end.
- [x] Struct-field and equivalent-literal-value forms produce identical
  terminal distributions (coefficient genuinely reaches the Hamiltonian).
- [x] LISS-0331/0367's existing leading-coefficient forms (bare literal,
  named Float, parenthesized compound) remain unaffected.
- [x] Full regression sweep passes (1472 passed); spec verification
  100.00% (161/161).
