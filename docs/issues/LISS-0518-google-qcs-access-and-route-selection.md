# LISS-0518: Google QCS access and route selection

| Field | Value |
|---|---|
| Status | **in_progress — technology selection approved; offline Phase 1 Red pending** |
| Phase | phase-0-design |
| Type | provider access / technology selection |
| Priority | P1 |
| Initial size | M |
| Current size | M |
| Parent | WP-0135 |
| Depends on | LISS-0514 |
| Blocks | Google adapter Phase 1 Issue and Google real-QPU pilot |
| Implementation permission | None |

## Review outcome

Recommend an offline `cirq-google`/Quantum Engine adapter contract. Live
execution remains access-dependent because approved-group membership, project,
and processor visibility are unknown. See the [provider technology-selection review](../collaboration/reviews/2026-09-10-provider-technology-selection-review.md).

## Objective

Determine whether Google hardware access is obtainable and define an offline
adapter contract that remains useful if live access is unavailable.

## Phase 0 scope

- Verify current QCS access requirements from official Google documentation.
- Define the Cirq/QCS or other documented artifact and API boundary.
- Separate simulator readiness, syntax/capability validation, and physical-QPU
  evidence.
- Record an explicit `blocked-access` disposition when hardware access is not
  approved; do not invent a device or schedule.

## Luna execution packet

- Model: `gpt-5.6-luna`; reasoning: `high`; official Google documentation only.
- Include: this Issue, WP-0135, common contract, dependency policy, and minimal
  QPU artifact contracts.
- Omit: credentials, Google Cloud project data, nonpublic material, and code.
- Allowed changes: this Issue, WP-0135, one access/adoption note, and trace.
- Output: access state, artifact/API mapping, compatibility state, blockers,
  offline next tests, and approval request.
- Stop before SDK installation, project creation, tests, or cloud calls.

## Verification

- Access claims cite current official documentation with capture date.
- `git diff --check` and documentation-link check pass.
