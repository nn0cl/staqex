# LISS-0556 Phase 0 acceptance / Architecture review packet

## Review packet

- Scope: restore the accepted POVM rejection-evidence projection at the local
  compiler result boundary.
- Canonical documents: ADR 0224, the LISS-0485 POVM bridge Issue and spec,
  the active-Red remediation spec, and WP-0161.
- Files re-read: `compiler/staqex/measurement.py`,
  `compiler/staqex/pipeline.py`, and
  `tests/test_liss_0485_povm_observation_bridge_red.py`.
- Changed files: Phase 0 documents and active-Red phase metadata only; no
  production or test implementation changed.

## Findings and dispositions

- `CompileResult.povm_observation_rejections` is absent while the accepted
  LISS-0485 test requires it — **apply: result projection in Phase 2**.
- `POVM_DOMAIN_MISMATCH` already preserves the rejection code, source span,
  requested effect-set identity, and source state domain — **already closed
  with evidence; reuse the diagnostic as the source**.
- Repairing the mismatch, evaluating POVM effects, or fabricating an outcome or
  post-state would violate the accepted bridge — **out of scope and forbidden**.
- Provider/QPU/AWS integration, finite-target generation, tomography, and Rust
  implementation — **out of scope; separate reviewed work**.

## Deterministic verification

The exact active-Red node was run:

```text
.venv/bin/python -m pytest -q tests/test_liss_0485_povm_observation_bridge_red.py::test_povm_rejection_preserves_reason_without_repair_or_fabricated_outcome
```

It failed at the accepted result surface with:

```text
AttributeError: 'CompileResult' object has no attribute 'povm_observation_rejections'
```

The compiler had already produced the expected rejected compilation. This
failure is the Phase 0 regression evidence; the implementation test remains
Red until Phase 1 is approved.

Same-context review was used because runtime routing specifies
`same_context`; it is weaker than `separate_context` and does not replace
Adjudicator approval.

## Remaining blockers

- Architecture approval of ADR 0224 and Phase 0 acceptance.
- Phase 1 Red approval before changing the test or implementation.

## Approval result

Approval received: `ADR 0224 Architecture / LISS-0556 Phase 0 acceptance
承認`, 2026-09-14. ADR 0224 is accepted.

## Next approval required

Approval received: `LISS-0556 Phase 1 Red 承認`, 2026-09-14.

The existing acceptance test is authorized for the Red phase. The next
required review is `LISS-0556 Phase 1 Red テストレビュー承認`.

## Evidence links

- Issue: `docs/issues/LISS-0556-povm-rejection-evidence-regression.md`
- ADR: `docs/architecture/adr/0224-povm-rejection-evidence-projection.md`
- Parent spec: `docs/specs/staqex-v1-quantum-mental-model-follow-up.md`
- Trace: `docs/collaboration/traces/2026-09-14-liss-0556-povm-rejection-design.md`
