# LISS-0437 finite Limit realization Red trace

## Approval and scope

- User approved finite `Limit` realization implementation on 2026-08-15.
- Current artifact status: Phase 2/3 Green acceptance draft; not a Phase 1
  Red artifact.
- Scope: provider-neutral finite `product` and finite `suzuki` realization
  acceptance tests.
- Excluded: live QPU submission, S02 numerical migration, and provider SDKs.

## Acceptance artifact

- `tests/test_liss_0437_limit_realization_red.py`
- Product policy: positive steps, written product retained, approximate plan
  and resource estimate.
- Suzuki policy: positive order/steps, explicit error budget, approximate plan
  and resource estimate.

## Gate

- No implementation was performed.
- The approved finite realization slice is now implemented.
- Product/Suzuki success-plan tests are intentionally separated from Phase 1
  source-preservation and rejection tests.

## Finite gate synthesis result

- `suzuki` explicit `Realize` produces a finite provider-neutral gate plan and
  retains method/order/steps/error budget/resource provenance.
- `product` is rejected for QPU gate synthesis as non-unitary rather than
  silently replaced by Suzuki.
- Evidence: `tests/test_liss_0437_limit_realization_red.py` → `GREEN: 2/2`.
- Live provider submission remains excluded.
