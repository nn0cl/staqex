# WP-0135: Google Quantum Computing Service route

| Field | Value |
|---|---|
| Status | **in_progress — technology selection approved; offline Phase 1 Red pending** |
| Parent | [WP-0131](WP-0131-multi-provider-real-qpu-connectivity.md) |
| Issues | [LISS-0518](../issues/LISS-0518-google-qcs-access-and-route-selection.md); adapter and pilot Issues TBD after approval |
| Depends on | WP-0122, WP-0123, WP-0124, WP-0131 |
| Owner boundary | Google QCS host adapter |
| Implementation permission | **None** |

## Goal

Prepare a provider-neutral route to Google quantum hardware while treating
hardware access approval as an external prerequisite.

## Scope

In: access preflight, Google Cloud project/configuration boundary, Cirq/QCS or
declared artifact route, capability profile, lifecycle/result mapping, and
manual evidence protocol.

Out: bypassing Google's approval process, credentials in the repository,
Google-specific source syntax, and claims based on simulator-only execution.

## Acceptance scenarios

- The local Kernel remains importable without Google libraries.
- Access-denied and unavailable-target states are explicit and non-retrying.
- A Google result is labeled real only when provider execution evidence exists.
- Source/artifact/result fingerprints remain compatible with other routes.

## Gate

This WP may reach offline Phase 1 without hardware access. Live pilot requires
approved Google hardware access, target selection, cost approval, and human
real-time confirmation.

## Issue graph and execution order

| Order | Issue | Phase | Exit |
|---:|---|---|---|
| 1 | [LISS-0518](../issues/LISS-0518-google-qcs-access-and-route-selection.md) | Phase 0 | verified access state and proposed artifact/API boundary |
| 2 | offline Google adapter Issue (TBD) | Phase 1–3 | optional adapter with fakes; no hardware claim |
| 3 | Google pilot Issue (TBD) | human run | created only when hardware access is confirmed |

Candidate Phase 1 test location after approval:
`tests/test_google_qcs_adapter_red.py`. Candidate implementation location:
`compiler/staqex/adapters/google_qcs.py`.

## Current next issue

- Issue: LISS-0518 Phase 0 only.
- Luna route: use the execution packet in LISS-0518.
- `blocked-access` is an acceptable completed Phase 0 disposition.
