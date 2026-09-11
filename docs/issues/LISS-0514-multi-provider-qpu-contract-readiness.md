# LISS-0514: Multi-provider QPU contract readiness

| Field | Value |
|---|---|
| Status | **in_progress — Phase 3 complete; provider pilot review pending** |
| Phase | phase-3-complete |
| Type | architecture / contract |
| Priority | P0 |
| Initial size | M |
| Current size | M |
| Parent | WP-0131 |
| Depends on | WP-0122, WP-0123, WP-0124 |
| Blocks | LISS-0515–LISS-0519 and provider Phase 1 work |
| Implementation permission | None |
| Post-review requirement | Provider-specific Phase 0/technology review and pilot approval |
| Design artifact | [Multi-provider QPU execution contract](../specs/staqex-multi-provider-qpu-execution-contract.md) — accepted baseline |

## Objective

Produce the reviewed provider-neutral contract that every provider route must
implement without changing Staqex semantics.

## Phase 0 scope

- Reconcile existing `QpuSubmitPort`, `QpuJobPort`, `JobRequest`, `JobStatus`,
  `JobResult`, and `RunEvidence` with WP-0131.
- Define separate identities for `access_route`, `hardware_provider`, and
  `device_id`.
- Define the minimum capability, lifecycle, result, error, idempotency, and
  evidence matrices shared by all routes.
- Identify reuse versus genuine contract gaps; do not edit production code.

## Deliverable

A proposed specification under `docs/specs/` containing EARS/Gherkin scenarios,
DTO invariants, failure mappings, and explicit no-artifact/no-submit behavior.

Current artifact: [multi-provider QPU execution contract](../specs/staqex-multi-provider-qpu-execution-contract.md).
The approved direction is to keep AWS/provider credentials in the Host
execution environment and represent per-run human approval as a separate,
non-secret `HostSubmissionApproval` evidence record. The specification now
fixes lifecycle observation mapping and capability freshness/expiry rules. It
is accepted as the architecture baseline. Phase 2 Green is reviewed; Phase 3
approval and provider implementation permission remain separate.

## Luna execution packet

- Model: `gpt-5.6-luna`; reasoning: `high`.
- Include: this Issue, WP-0131, real-QPU readiness spec, hybrid workflow,
  DEC-0006, implementation readiness, `compiler/staqex/qpu_submit.py`, and
  existing related tests.
- Omit: provider SDK manuals, credentials, unrelated compiler modules, and
  live provider output.
- Allowed changes: this Issue, WP-0131, one new proposed spec, and the task
  trace only.
- Output: `[DESIGN CHECK]`, gap table, proposed scenarios, changed files,
  deterministic checks, and requested approval type.
- Stop after Phase 0. Do not create tests or implementation.

## Deterministic verification

- `python3 scripts/check-doc-links.py` when available.
- `git diff --check`.
- `rg -n "access_route|hardware_provider|device_id"` over the proposed spec.

## Phase 1 Red and Phase 2 Green result

Added `tests/test_liss_0514_multi_provider_qpu_contract_red.py` with five
provider-neutral contract tests. Phase 1 Red was confirmed by the missing
`compiler.staqex.qpu_contract` module. Phase 2 added the minimum
`compiler/staqex/qpu_contract.py` implementation and the direct script runner
now passes all five tests. No provider SDK, credentials, network call, or
real-QPU call was used.

## Phase 2 Green review

The same-context re-review confirms that the canonical status is synchronized,
identity/required-capability checks are present, and all seven scoped tests are
executed by the direct runner. See the [Phase 2 Green review summary](../collaboration/reviews/2026-09-10-liss-0514-phase2-green-review.md).

Phase 3 refactoring is complete and reviewed in the [Phase 3 review summary](../collaboration/reviews/2026-09-10-liss-0514-phase3-review.md).
