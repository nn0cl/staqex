# LISS-0516: AWS Braket fan-out gap analysis

| Field | Value |
|---|---|
| Status | **Phase 3 reviewed and accepted; real-QPU pilot pending** |
| Phase | phase-3-complete |
| Type | provider inventory / gap analysis |
| Priority | P0 |
| Initial size | M |
| Current size | M |
| Parent | WP-0133 |
| Depends on | LISS-0514; LISS-0392; LISS-0396; LISS-0463–LISS-0466 |
| Blocks | AWS provider-profile Phase 1 Issue and AWS real-QPU pilot |
| Implementation permission | Phase 3 complete; live pilot remains separately gated |

## Review outcome

Reuse the existing Braket adapter and OpenQASM 3 route. IonQ remains a pilot
candidate, not a selected device; current account availability and price are
unknown. See the [provider technology-selection review](../collaboration/reviews/2026-09-10-provider-technology-selection-review.md).

## Objective

Determine exactly what remains after the shipped AWS Braket adapter and Host
hardening, then select one first hardware provider without reopening completed
work.

## Phase 0 scope

- Inventory existing AWS adapter, CLI, tests, and acceptance evidence.
- Compare current IonQ, Rigetti, and QuEra device capability envelopes using
  official AWS documentation.
- Identify only observed gaps in capability discovery, target profile,
  artifact submission, result mapping, evidence, and human pilot procedure.
- Recommend one first device with cost/availability assumptions marked.

## Luna execution packet

- Model: `gpt-5.6-luna`; reasoning: `high`; official AWS documentation only.
- Include: this Issue, WP-0133, listed completed Issues, AWS adapter/CLI, their
  tests, and the common contract.
- Omit: other provider SDKs, credentials, live AWS calls, and broad source.
- Allowed changes: this Issue, WP-0133, one gap-analysis note, and trace.
- Output: `reuse / gap / deferred` matrix, source links, candidate device,
  exact next test files, and approval request.
- Stop if no genuine gap is demonstrated. Do not reimplement shipped code.

## Verification

- `python3 -m py_compile compiler/staqex/adapters/aws_braket.py`.
- Run existing AWS fake-adapter tests named in the gap analysis.
- `git diff --check`; no network or real submission.

## Phase 1 Red result

Added `tests/test_liss_0516_aws_braket_fanout_red.py` with three fake-client
tests covering raw `CANCELLING`/unknown state preservation and separation of
AWS route, hardware provider, and device capability profile. The direct runner
fails at the intentionally absent `AwsBraketAdapter.status_observation` method,
confirming Red. No SDK, credentials, network, or real submission was used.

The direct runner was corrected to collect and report all three failures. The
re-review accepted the Phase 1 Red evidence. See the [review summary](../collaboration/reviews/2026-09-10-liss-0516-phase1-red-review.md).

## Phase 2 Green implementation

Added the minimum Host adapter implementation: raw lifecycle observation uses
the provider-neutral mapper, and Braket device capability snapshots produce a
TTL-bound `CapabilityProfile` with separate route, hardware provider, and
device identities. The three scoped fan-out tests and existing LISS-0392 fake
adapter tests pass. No SDK, network, credentials, or real submission was used.

The [Phase 2 Green review](../collaboration/reviews/2026-09-10-liss-0516-phase2-green-review.md)
found no blockers. Phase 3 initially found and then resolved the legacy
unknown-state projection. A follow-up audit found and resolved F2: the real
Braket client now implements the required `device_capabilities()` surface.
See the [Phase 3 review](../collaboration/reviews/2026-09-10-liss-0516-phase3-review.md).
