# LISS-0465: Provider-neutral submit integration hardening

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor complete** |
| Phase | phase-3-refactor |
| Type | adapter integration |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | AWS Braket adapter / Host use case |
| Parent | WP-0119; WP-0123; ADR 0202–0203 |
| Depends on | LISS-0461, LISS-0462, LISS-0463, LISS-0464 |
| Blocks | LISS-0466 |
| Branch | `codex/liss-0465-provider-submit-hardening` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0465--submit-integration) |
| Implementation permission | None |
| Post-review requirement | Provider/security review and typed Phase 1 approval |

Verify the existing adapter against the provider-neutral `QpuSubmitPort`:
request/artifact identity, idempotency, payload mapping, timeout, transient
versus permanent errors, and no accidental submit on check/dry-run. Use fake
ports and recorded structural fixtures only. Real credentials and real device
calls are excluded.
## Design detail

**In:** mapping `ExecutionArtifact` to `QpuSubmitPort`, request/artifact
identity, idempotency, payload limits, timeout, transient/permanent errors,
dry-run behavior, and fake-provider fixtures. **Out:** provider changes,
real credentials, real device calls, and physics decisions in the adapter.

**Acceptance:** identical request identity follows the accepted idempotency
contract; artifact fingerprint reaches the request; check/dry-run performs zero
submit calls; provider failures map to typed outcomes; unsupported payloads
reject before network invocation.

**Phase/evidence:** Phase 0 mapping/ADR review; Phase 1 Red fake-port tests;
Phase 2 adapter hardening; Phase 3 fault-injection, regression, and review.
Planning record: `AIP-LISS-0465-2026-08-27-001` (L; N/A model metrics).

## Phase 1 Red artifact

- Added `tests/test_liss_0465_provider_submit_hardening_red.py` with a fake
  provider port and structural QPU artifact fixtures.
- The test-only contract covers artifact/request identity, idempotency
  deduplication, dry-run zero-submit behavior, pre-network target/payload
  rejection, and typed transient/permanent failures without implicit retry.
- Red is confirmed by the intentionally absent
  `compiler.staqex.submit_integration` module. No provider SDK, credential,
  network call, or real device was used.
- Phase 2 adapter hardening remains unapproved.

## Phase 2 Green artifact

- Added `compiler/staqex/submit_integration.py` around the injected
  provider-neutral submit port.
- The adapter validates payload size and target before invocation, preserves
  request/artifact identity, deduplicates identical idempotency keys, keeps
  dry-run/check at zero calls, and maps transient/permanent failures without
  implicit retry.
- LISS-0465 contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. No provider SDK, credential, network call, or real
  device was used. Phase 3 fault-injection review remains gated.

## Phase 3 closeout

- Extracted provider-failure classification into a focused helper without
  changing typed outcomes, retry behavior, or submit-call counts.
- LISS-0465 contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. Same-context fake fault-injection review found no
  blocker; this isolation is weaker than separate-context review.
- Process review: no operating-contract deviation or operational problem
  found.
- Real provider SDK, credentials, network, and physical submission remain
  separately gated.
