# WP-0133: AWS Braket provider fan-out

| Field | Value |
|---|---|
| Status | **Phase 3 reviewed and accepted; real-QPU pilot pending** |
| Parent | [WP-0131](WP-0131-multi-provider-real-qpu-connectivity.md) |
| Issues | LISS-0392, LISS-0396, LISS-0463–0466; [LISS-0516](../issues/LISS-0516-aws-braket-fanout-gap-analysis.md) |
| Related | [WP-0123](WP-0123-provider-integration-security.md), [WP-0126](WP-0126-human-real-qpu-execution.md) |
| Depends on | WP-0122, WP-0123, WP-0124, WP-0131 |
| Owner boundary | AWS Braket host adapter and provider profiles |
| Implementation permission | **Phase 3 complete; live pilot remains separately gated** |

## Goal

Use Amazon Braket as a multi-provider route while preserving one Staqex
artifact and one provider-neutral lifecycle contract.

## Initial provider matrix

| Provider | Role | First disposition |
|---|---|---|
| IonQ | trapped-ion gate model | candidate first pilot |
| Rigetti | superconducting gate model | second route comparison |
| QuEra | neutral-atom gate model | neutral-atom target comparison |

## Scope

In: Braket OpenQASM 3 submission, device capability discovery, ARN/region
configuration, S3 result retrieval, lifecycle mapping, and human-approved
pilot. Out: AWS deployment, persistent service, autonomous jobs, and provider
logic in the compiler.

## Acceptance scenarios

- OpenQASM artifact passes local and Braket target preflight.
- Device ARN, region, shots, S3 location, and cost guard are explicit.
- Repeated requests cannot create an untracked duplicate task.
- Raw counts and provider metadata are retained without secrets.
- The same artifact can be compared across two Braket providers when approved.

## Note

WP-0123 already covers bounded provider-neutral AWS hardening. This WP adds
the provider matrix and real-device route; it must not reimplement completed
security or lifecycle slices.

## Issue graph and execution order

| Order | Issue | Status/phase | Exit |
|---:|---|---|---|
| 0 | LISS-0392, LISS-0396, LISS-0463–0466 | completed evidence | reusable adapter/CLI/security baseline |
| 1 | [LISS-0516](../issues/LISS-0516-aws-braket-fanout-gap-analysis.md) | Phase 2 Green accepted | fake lifecycle/profile gap tests |
| 2 | observed-gap Issue (TBD) | blocked Phase 1–3 | only a demonstrated missing behavior |
| 3 | provider-specific pilot Issue (TBD) | blocked human run | one bounded AWS hardware result |

Candidate tests must extend the existing AWS fake-adapter suites named by
LISS-0516. A new test file is allowed only when the approved gap cannot be
expressed clearly in those suites. The approved gap tests are now recorded in
`tests/test_liss_0516_aws_braket_fanout_red.py`.

## Current next issue

- Issue: bounded AWS real-QPU pilot review after explicit human target,
  shots, cost, credential, and submission approval.
- Luna route: use the execution packet in LISS-0516.
- Stop outcome is valid: if existing code already satisfies the contract, mark
  the proposed change `already closed with evidence` and create no code Issue.

## Phase 2 implementation result

LISS-0516 now has the minimum AWS adapter implementation for lifecycle
observation and capability profiles. The scoped tests are Green; Phase 2
review is the next gate. SDK installation, authentication changes, network
access, and real-QPU execution remain out of scope.

The Phase 2 Green review found no blockers. Phase 3 found and resolved the
legacy unknown-state projection in `status()`. A follow-up audit found and
resolved the missing concrete capability surface. A real-QPU pilot remains
separately gated.
