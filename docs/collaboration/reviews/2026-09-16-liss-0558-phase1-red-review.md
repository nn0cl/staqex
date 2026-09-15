# LISS-0558 Phase 1 Red test review

- Issue/WP: LISS-0558 / WP-0161
- Path/phase: Feature Path / Phase 1 Red
- Review isolation: same_context, per `docs/collaboration/runtime-routing.toml`
- Approval received: `LISS-0558 Phase 1 Red テストレビュー承認`, 2026-09-16
- Implementation permission: not granted by this review

## Reviewed contract

The existing node
`tests/test_quantum_observation_contract_red.py::test_unsupported_tomography_is_rejected_as_an_observation_capability`
is the sole Phase 1 acceptance test. It requires the canonical
`OBSERVATION_UNSUPPORTED` code and rejects `LINEAR_DUPLICATE_USE` masking.

## Evidence

- The test was executed unchanged: **1 failed**.
- Actual output included `OBSERVATION_CAPABILITY_UNSUPPORTED`,
  `HOST_TYPE_IN_KERNEL_ERROR`, `QSEM_APPROXIMATION_OBLIGATION_MISSING`, and
  `QSEM_FINITE_EVIDENCE_MISSING`.
- `LINEAR_DUPLICATE_USE` was absent.
- The failure is bounded to the diagnostic-name reconciliation; no tomography
  implementation, alias, provider, or QPU behavior is implied.

## Review result

The Red node is reviewable, deterministic, and aligned with accepted ADR 0226.
It must remain unchanged for Phase 2. Green may make the minimum catalog and
conformance synchronization required by ADR 0226, without adding a second
diagnostic path or changing the Host/Kernel boundary.

## Next gate

Request `LISS-0558 Phase 2 Green / Implementation 承認`.
