# LISS-0466: Job lifecycle and result integrity

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor complete** |
| Phase | phase-3-refactor |
| Type | Host execution contract |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | Host Job/QpuJob boundary |
| Parent | WP-0119; WP-0123; ADR 0065, 0103, 0104 |
| Depends on | LISS-0465 |
| Blocks | LISS-0467, LISS-0468 |
| Branch | `codex/liss-0466-job-lifecycle-result-integrity` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0466--job-lifecycle-and-result-integrity) |
| Implementation permission | None |
| Post-review requirement | Acceptance-spec review and typed Phase 1 approval |

Complete the lifecycle matrix for submit/status/wait/result/cancel, unknown
jobs, timeout, cancellation, provider failures, incomplete/partial results,
attempt metadata, ordering, and structured observations. Preserve source,
semantic, and artifact fingerprints through `JobResult`; never fabricate a
successful result from an incomplete provider payload.
## Design detail

**In:** submit/status/wait/result/cancel, unknown jobs, timeout/cancel/failure,
partial results, attempts, ordering, observations, and source/semantic/artifact
fingerprints. **Out:** provider-specific DTO leakage, fabricated completion,
and changes to Kernel measurement semantics.

**Acceptance:** every provider status maps deterministically; cancellation and
timeout are distinguishable; incomplete payloads cannot produce successful
observations; result ordering and attempt metadata are retained; repeated
polling is safe and does not resubmit.

**Phase/evidence:** Phase 0 lifecycle matrix; Phase 1 Red fake-job tests; Phase
2 Host lifecycle implementation; Phase 3 fault matrix and independent review.
Planning record: `AIP-LISS-0466-2026-08-27-001` (L; N/A model metrics).

## Phase 1 Red artifact

- Added `tests/test_liss_0466_job_lifecycle_integrity_red.py` with a fake job
  port and provider-neutral job identity fixtures.
- The test-only lifecycle matrix covers successful metadata/attempt
  preservation, partial-result rejection, failed/cancelled/timeout/unknown
  state distinction, explicit cancellation, polling without resubmit, and
  missing fingerprint metadata.
- Red is confirmed by the intentionally absent
  `compiler.staqex.job_lifecycle` module. No provider SDK, credential,
  network call, or real device was used.
- Phase 2 Host lifecycle implementation remains unapproved.

## Phase 2 Green artifact

- Added `compiler/staqex/job_lifecycle.py` with provider-neutral observation
  and result-integrity contracts.
- Successful results require complete source/semantic/artifact metadata and
  exactly the expected measurement ordering. Partial, failed, cancelled,
  timeout, and unknown states remain non-success.
- Repeated observation is status/result polling only; no submit or implicit
  retry exists. LISS-0466 tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. Phase 3 fault-matrix review remains gated.

## Phase 3 closeout

- Extracted attempt normalization and common failed-result construction while
  preserving state mapping, diagnostics, ordering, and fail-closed behavior.
- LISS-0466 tests, Python 3.14 `py_compile`, and `git diff --check` pass.
- Same-context fault-matrix review found no blocker; this isolation is weaker
  than separate-context review.
- Process review: no operating-contract deviation or operational problem
  found. Provider, credentials, network, and live-QPU work remain gated.
