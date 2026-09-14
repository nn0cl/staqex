# Review Summary: LISS-0554 Phase 0 Architecture

## Review packet

- Scope: make QASM emission fail closed when no compile-owned canonical
  `ScientificSemanticIR` is supplied.
- Canonical documents: QASM Public Entry Canonical Sharing Spec, Scientific
  Semantic Consumer Migration Spec, ADR 0211, ADR 0220, proposed ADR 0222,
  WP-0161, LISS-0554, and the active-Red manifest.
- Files re-read: `compiler/staqex/backend/qasm/emitter.py`,
  `compiler/staqex/backend/qasm/lower.py`,
  `tests/test_liss_0477_ast_dto_authority_retirement_red.py`, and the accepted
  LISS-0446/LISS-0501 records.

## Findings and dispositions

- `emit_unit()` rebuilds canonical IR when `semantic_ir=None` — **apply in
  Phase 2 Green**; Phase 0 fixes the boundary and acceptance evidence only.
- Missing canonical input must reject before artifact production — **apply and
  accepted as the Phase 1 contract**.
- Supplied canonical IR identity mismatch is already rejected — **already
  closed with evidence**; preserve the current guard.
- Public compile/source/path forwarding is covered by the accepted LISS-0446
  contract — **out of scope for this bounded regression**, except for unchanged
  neighbor verification.
- Dynamic QASM, CH0, provider/live-QPU, AWS, Rust, and lowerer deletion —
  **out of scope**.

## Blockers

No architecture blocker found. The current exact active-Red test fails because
raw input emits QASM, confirming the gap. Same-context review is weaker than
separate-context review and does not replace Adjudicator approval.

## Verification

- Exact node: **1 failed**; raw parsed unit returned `ok=True` with QASM.
- No test or production implementation changed in Phase 0.
- Lifecycle/static full checks are recorded after the design artifacts are
  added; implementation verification is deferred to later phases.

## Next approval required

Approval received: `ADR 0222 Architecture / LISS-0554 Phase 0 acceptance
承認`, 2026-09-14.

Next approval required: `LISS-0554 Phase 1 Red 承認`.

## Evidence links

- Issue: `docs/issues/LISS-0554-qasm-canonical-input-fail-closed-regression.md`
- Representative Spec: `docs/specs/staqex-qasm-public-entry-canonical-sharing.md`
- Parent Work Plan: `docs/work-plans/WP-0161-active-red-remediation.md`
