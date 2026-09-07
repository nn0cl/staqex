# LISS-0511 Phase 2 Green Review

| Field | Value |
|---|---|
| Scope | Bounded product/tensor canonical-meaning projection |
| Phase reviewed | Phase 2 Green |
| Verdict | **READY for the bounded slice; NOT READY for Phase 3 or broader completion** |
| Isolation | `same_context` — weaker than `separate_context` |

## Canonical documents and files re-read

- [LISS-0511](../../issues/LISS-0511-product-tensor-meaning-preservation.md)
- [WP-0128](../../work-plans/WP-0128-product-tensor-meaning-preservation.md)
- [Product/Tensor Spec](../../specs/staqex-semantic-ir-product-tensor-preservation.md)
- [WP-0113](../../work-plans/WP-0113-semantic-ir-meaning-preservation.md)
- ADR 0211 and ADR 0212
- `compiler/staqex/scientific_semantic_ir.py`
- `tests/test_liss_0511_product_tensor_meaning_red.py`
- `tests/fixtures/semantic_meaning/product_tensor.sqx`
- [Phase 1 trace](../traces/2026-09-07-liss-0511-product-tensor-red.md)

## Findings and dispositions

### F1 — Structural tensor dimension marker is not resolved dimension evidence

- Evidence: tensor nodes expose `tensor[unknown,unknown]`.
- Disposition: **out of scope for this bounded slice**. The marker makes the
  unresolved state explicit and prevents claiming a numeric dimension. Actual
  carrier/dimension resolution requires a separate accepted contract.
- Phase 3 blocker: do not claim full tensor meaning preservation until resolved
  dimensions or an explicit unresolved-dimension contract is accepted.

### F2 — Non-unitary rejection covers only the bounded direct scalar/Pauli form

- Evidence: projection rejection recognizes direct `OpLit` + `OpPauli`
  operator-product children. Named, nested, or other non-unitary products are
  not covered by this slice.
- Disposition: **out of scope for this bounded slice**. No implicit expansion
  into numerical or unitary realization is allowed.
- Phase 3 blocker: broader product classification needs its own acceptance
  matrix and no-artifact tests before fallback retirement.

### F3 — Full repository regression did not complete cleanly

- Evidence: the long run was interrupted in documentation compression after
  `1169 passed` and `9 failures`; focused and related suites were green.
- Disposition: **open verification blocker for Phase 3**, not a bounded Green
  failure. The reported failures are outside LISS-0511's focused/related
  families, but a clean full run has not been established.

### F4 — Compatibility field and canonical structure are separated explicitly

- Evidence: `meaning_kind="mathematical_product"` remains unchanged while
  `product_kind` carries `operator_product` or `tensor_product`; the new field
  participates in semantic fingerprints.
- Disposition: **already closed with evidence**. This honors the existing
  authority-boundary lesson without retaining a DTO as execution authority.

## Deterministic verification

- LISS-0511 focused suite: **4 passed**.
- Related product/semantic/QPU suites: **39 passed**.
- Specification verification: **161/161 (100%)**.
- `py_compile`: passed.
- `git diff --check`: passed.
- Full pytest: not a clean completion; see F3.

## Process lessons applied

- Compatibility projections remain explicitly non-authoritative; the existing
  `mathematical_product` value is retained only for compatibility while the
  canonical `product_kind` is fingerprinted and tested.
- Unsupported-family acceptance is explicit and atomic for the bounded form;
  broader forms remain rejected from completion claims.
- Status records distinguish bounded Green from Phase 3 and broader work.

## Remaining blockers and next approval

No blocker prevents the bounded Phase 2 Green record. F1–F3 prevent a Phase 3
completion claim. The next requested approval type is **Phase 3 Refactor
approval**, only after the Adjudicator accepts the bounded dispositions and
the full-regression verification plan.

