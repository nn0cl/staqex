# WP-0136: Direct-provider parity routes

| Field | Value |
|---|---|
| Status | **in_progress — direct routes deferred by approved technology decision** |
| Parent | [WP-0131](WP-0131-multi-provider-real-qpu-connectivity.md) |
| Issues | [LISS-0519](../issues/LISS-0519-direct-provider-parity-decision.md); direct adapter Issues created only for approved `add` decisions |
| Depends on | WP-0122, WP-0123, WP-0124, WP-0131 |
| Implementation permission | **None** |

## Goal

Decide when direct provider APIs add enough value beyond AWS/Azure routing to
justify separate adapters, without multiplying Staqex semantics.

## Candidate routes

| Provider | Aggregated routes | Direct route purpose |
|---|---|---|
| Quantinuum | Azure | compare direct lifecycle and dynamic capability |
| IonQ | AWS, Azure | compare direct target fidelity and metadata |
| Rigetti | AWS, Azure | compare direct compilation/result behavior |
| QuEra | AWS | compare direct neutral-atom access if available |

## Scope

In: access-route comparison, capability/profile equivalence, provider-neutral
result mapping, and a decision on which direct route is justified.

Out: implementing all four direct adapters by default, provider-specific
algorithm libraries, and D-Wave annealing.

## Acceptance scenarios

- Direct and aggregated routes for the same provider use the same semantic
  artifact contract.
- Differences in compilation, status, metadata, and measurement ordering are
  visible in the adapter evidence, not hidden in the Kernel.
- A direct route is added only after a demonstrated need and technology review.

## Recommended order

1. Quantinuum direct only if Azure access or dynamic capability is insufficient.
2. IonQ direct for route/fidelity comparison.
3. Rigetti direct for compilation and superconducting comparison.
4. QuEra direct only when AWS route evidence leaves a concrete gap.

## Issue graph and execution order

| Order | Issue | Phase | Exit |
|---:|---|---|---|
| 1 | [LISS-0519](../issues/LISS-0519-direct-provider-parity-decision.md) | Phase 0 | `add / defer / reject` per route |
| 2 | one direct adapter Issue per approved `add` | Phase 1–3 | bounded adapter behind existing ports |
| 3 | one provider pilot Issue per approved route | human run | route-specific evidence only |

No common `direct_providers.py` adapter is planned. Each approved direct route
must remain independently optional and may share only provider-neutral DTOs and
test helpers.

## Review result

Quantinuum, IonQ, Rigetti, and QuEra direct routes are recommended for
`defer`; a direct adapter requires a demonstrated gap after AWS/Azure evidence.

## Current next issue

- Issue: LISS-0519 Phase 0 only, after LISS-0516 and LISS-0517 decisions.
- Luna route: use the execution packet in LISS-0519.
- Default disposition is `defer` unless a direct route closes a documented gap.
