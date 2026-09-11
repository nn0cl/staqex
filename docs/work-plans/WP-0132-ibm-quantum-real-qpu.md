# WP-0132: IBM Quantum real-QPU route

| Field | Value |
|---|---|
| Status | **in_progress — technology selection approved; Phase 1 Red pending** |
| Parent | [WP-0131](WP-0131-multi-provider-real-qpu-connectivity.md) |
| Issues | [LISS-0515](../issues/LISS-0515-ibm-quantum-route-selection.md); adapter and pilot Issues TBD after approval |
| Depends on | WP-0122, WP-0123, WP-0124, WP-0131 |
| Owner boundary | IBM host adapter; Kernel remains provider-neutral |
| Implementation permission | **None** |
| Acceptance | Bell/GHZ artifact, lifecycle, result mapping, and evidence on an IBM QPU |

## Goal

Connect a supported Staqex static artifact to IBM Quantum Platform or IBM
Cloud, observe the job lifecycle, and recover terminal measurement results.

## Scope

In: IBM target capability profile, OpenQASM/QIR route decision, optional SDK
packaging, credential/configuration boundary, fake adapter, human-operated
pilot, and evidence handoff.

Out: IBM-specific semantics in the Kernel, autonomous submission, dynamic
feature claims, and broad benchmark claims.

## Acceptance scenarios

- Bell and GHZ compile without IBM imports in the Kernel.
- Unsupported gates, shots, or dynamic features fail before submission.
- IBM status/result states map to provider-neutral `JobStatus`/`JobResult`.
- A human-approved run records device, job, artifact fingerprint, shots, raw
  counts, and limitations.

## Issue graph and execution order

| Order | Issue | Phase | Exit |
|---:|---|---|---|
| 1 | [LISS-0515](../issues/LISS-0515-ibm-quantum-route-selection.md) | Phase 0 | approved IBM route, artifact, SDK/API, device candidate |
| 2 | adapter acceptance Issue (TBD) | Phase 1–3 | optional IBM adapter behind existing ports |
| 3 | provider-specific pilot Issue (TBD) | human run | one reviewed real result envelope |

Candidate Phase 1 test location after approval:
`tests/test_ibm_quantum_adapter_red.py`. Candidate implementation location:
`compiler/staqex/adapters/ibm_quantum.py`. These paths are proposals, not
implementation permission.

## Current next issue

- Issue: LISS-0515 Phase 0 only.
- Luna route: use the execution packet in LISS-0515.
- Blocked by: IBM technology-selection approval and account/device evidence.

## Gate

Select IBM device, SDK/API route, cost ceiling, and artifact format before
Phase 1 Red. Real execution requires WP-0126-style human confirmation.
