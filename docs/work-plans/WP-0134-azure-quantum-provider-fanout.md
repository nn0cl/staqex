# WP-0134: Azure Quantum provider fan-out

| Field | Value |
|---|---|
| Status | **in_progress — technology selection approved; Phase 1 Red pending** |
| Parent | [WP-0131](WP-0131-multi-provider-real-qpu-connectivity.md) |
| Issues | [LISS-0517](../issues/LISS-0517-azure-quantum-route-selection.md); adapter and pilot Issues TBD after approval |
| Depends on | WP-0122, WP-0123, WP-0124, WP-0131 |
| Owner boundary | Azure Quantum host adapter and target profiles |
| Implementation permission | **None** |

## Goal

Connect Staqex to Azure Quantum without confusing the Azure access route with
the underlying QPU provider.

## Initial provider matrix

| Provider | Role | First disposition |
|---|---|---|
| Pasqal | neutral atom | primary Azure pilot candidate |
| Quantinuum | trapped ion | dynamic/high-fidelity follow-up |
| IonQ | trapped ion | route-parity comparison |
| Rigetti | superconducting | route-parity comparison |

## Scope

In: Azure workspace/target configuration, QIR or OpenQASM route decision,
capability profiles, lifecycle/result mapping, and human-approved pilot.

Out: Microsoft/Azure semantics in Staqex, deployment infrastructure, dynamic
claims before target evidence, and automatic provider selection.

## Acceptance scenarios

- Azure route and underlying provider are separately recorded in evidence.
- Pasqal capability differences are explicit and do not redefine Yaqumo
  semantics.
- Quantinuum mid-circuit support is opt-in and capability-checked.
- Missing workspace, target, permission, or cost configuration fails closed.

## Gate

Adjudicator selects the first Azure provider and approves the required SDK/API
technology before Phase 1 Red.

## Issue graph and execution order

| Order | Issue | Phase | Exit |
|---:|---|---|---|
| 1 | [LISS-0517](../issues/LISS-0517-azure-quantum-route-selection.md) | Phase 0 | approved access route, provider, artifact/API, SDK decision |
| 2 | Azure adapter acceptance Issue (TBD) | Phase 1–3 | optional adapter and fake lifecycle mapping |
| 3 | Azure provider-profile Issue (TBD) | Phase 1–3 | bounded selected-device capability profile |
| 4 | Azure pilot Issue (TBD) | human run | one reviewed real result envelope |

Candidate Phase 1 test location after approval:
`tests/test_azure_quantum_adapter_red.py`. Candidate implementation location:
`compiler/staqex/adapters/azure_quantum.py`.

## Review result

Azure Quantum job API with QIR v1 is the recommended common route. Provider
and device remain unselected until workspace target evidence is available.

## Current next issue

- Issue: LISS-0517 Phase 0 only.
- Luna route: use the execution packet in LISS-0517.
- Pasqal is a candidate, not an accepted selection.
