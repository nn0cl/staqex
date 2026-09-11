# LISS-0517: Azure Quantum route selection and provider fan-out

| Field | Value |
|---|---|
| Status | **in_progress — technology selection approved; Phase 1 Red pending** |
| Phase | phase-0-design |
| Type | provider technology selection |
| Priority | P0 |
| Initial size | M |
| Current size | M |
| Parent | WP-0134 |
| Depends on | LISS-0514 |
| Blocks | Azure adapter Phase 1 Issue and Azure real-QPU pilot |
| Implementation permission | None |

## Review outcome

Recommend Azure Quantum's job API with QIR v1 as the common artifact route.
Pasqal, Quantinuum, IonQ, and Rigetti remain candidates; no provider or device
is selected without workspace target evidence. See the [provider technology-selection review](../collaboration/reviews/2026-09-10-provider-technology-selection-review.md).
| Post-review requirement | Phase 1 Red approval |

## Objective

Select the first Azure Quantum route and underlying hardware provider while
preserving separate route/provider/device identities.

## Phase 0 scope

- Compare Pasqal, Quantinuum, IonQ, and Rigetti only at the capability and
  access-contract level.
- Recommend one initial provider; Pasqal is the default candidate for
  neutral-atom coverage, not a preselected technology.
- Decide the initial artifact/API route and optional SDK boundary.
- Define Azure workspace/target configuration, lifecycle/result mapping,
  permission, region, cost, and credential preflight requirements.

## Luna execution packet

- Model: `gpt-5.6-luna`; reasoning: `high`; official Microsoft and named
  provider documentation only.
- Include: this Issue, WP-0134, common contract, dependency policy, and minimal
  QASM/QIR contracts.
- Omit: credentials, account data, unrelated providers, and implementation.
- Allowed changes: this Issue, WP-0134, one adoption/selection note, and trace.
- Output: route/provider/device matrix, selected/rejected alternatives,
  compatibility state, source links, and approval request.
- Stop before SDK installation, tests, or Azure calls.

## Verification

- Every capability statement names route, hardware provider, target, source,
  and capture date.
- `git diff --check` and documentation-link check pass.
