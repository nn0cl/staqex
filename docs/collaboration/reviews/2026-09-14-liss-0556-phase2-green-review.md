# LISS-0556 Phase 2 Green / Implementation review

## Review packet

- Scope: restore the compiler result projection for accepted POVM rejection
  evidence.
- Canonical documents: ADR 0224, LISS-0556, the LISS-0485 bridge spec, and
  WP-0161.
- Changed production file: `compiler/staqex/pipeline.py`.
- Changed behavior: `CompileResult` now exposes diagnostic-derived POVM
  rejection records.

## Findings and dispositions

- The accepted rejection test passes with code, request identity, state domain,
  and false non-repair/non-fabrication flags — **apply and verified**.
- Projection is compiler-owned and derived from canonical diagnostics —
  **already closed with evidence**.
- Valid POVM bridge behavior and nearby mixed-state dispatch remain passing —
  **already closed with evidence**.
- Effect-matrix evaluation, repair, sampled outcomes, post-states, finite
  targets, provider/QPU/AWS, and Rust — **out of scope**.

## Verification

- LISS-0485 bridge suite: **3 passed**.
- Nearby POVM and mixed-dispatch suites: **7 passed**.
- Measurement-family aggregate: **25 passed**.
- `py_compile`, document lifecycle, test lifecycle, coverage-ledger
  consistency, and `git diff --check`: passed.

Same-context review was used because runtime routing specifies
`same_context`; it is weaker than `separate_context` and does not replace
Adjudicator approval.

## Next approval required

`LISS-0556 Phase 3 Refactor 承認`

Approval received: `LISS-0556 Phase 3 Refactor 承認`, 2026-09-14.

The readability-only cleanup was applied without behavioral change. The next
required approval is `LISS-0556 Phase 3 最終レビュー 承認`.

## Evidence links

- Issue: `docs/issues/LISS-0556-povm-rejection-evidence-regression.md`
- ADR: `docs/architecture/adr/0224-povm-rejection-evidence-projection.md`
- Phase 1 review: `2026-09-14-liss-0556-phase1-red-review.md`
- Trace: `docs/collaboration/traces/2026-09-14-liss-0556-povm-rejection-design.md`
