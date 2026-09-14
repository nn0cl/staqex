# LISS-0556 Phase 1 Red test review

## Review packet

- Scope: verify the existing LISS-0485 rejection test as the approved Red
  authority for LISS-0556.
- Canonical documents: ADR 0224, LISS-0556, the LISS-0485 bridge spec, and
  WP-0161.
- Changed files: no production or test implementation changes.

## Findings and dispositions

- The valid POVM request and IR evidence tests pass — **already closed with
  evidence**.
- The rejection test fails at the missing
  `CompileResult.povm_observation_rejections` surface — **apply in Phase 2**.
- The test asserts rejection reason, effect-set identity, state domain,
  non-repair, and non-fabrication — **already closed with evidence**.
- Test weakening, fabricated outcomes, POVM mathematics, and provider/QPU
  behavior — **out of scope**.

## Verification

The complete target file returned **2 passed, 1 failed**. The failure is the
expected Red signal and is limited to the missing result attribute. No
collection error occurred.

Same-context review was used because runtime routing specifies
`same_context`; it is weaker than `separate_context` and does not replace
Adjudicator approval.

## Next approval required

Approval received: `LISS-0556 Phase 1 Red テストレビュー承認`, 2026-09-14.

The existing test is accepted as the single regression authority. The next
required approval is `LISS-0556 Phase 2 Green / Implementation 承認`.

## Evidence links

- Issue: `docs/issues/LISS-0556-povm-rejection-evidence-regression.md`
- Phase 0 review: `2026-09-14-liss-0556-phase0-architecture-review.md`
- ADR: `docs/architecture/adr/0224-povm-rejection-evidence-projection.md`
- Trace: `docs/collaboration/traces/2026-09-14-liss-0556-povm-rejection-design.md`
