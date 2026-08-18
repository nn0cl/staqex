# LISS-0442: S02 and representative-example migration inventory

| Field | Value |
|---|---|
| Status/phase | **Phase 0 approved — investigation only** |
| WorkPlan | [WP-0105](../work-plans/WP-0105-s02-corpus-migration-inventory.md) |
| Specification | [S02 and representative-example migration inventory](../specs/staqex-s02-corpus-migration-inventory.md) |
| Scope approval | User approval recorded 2026-08-18 |
| Implementation approval | **Not granted** |

## Objective

Determine which remaining example and S02 changes are needed to preserve the
blackboard equation in source while keeping classical, mathematical, quantum,
finite-realization, and Host responsibilities explicit.

## In scope

- read-only inventory of the official example corpus and S02 lanes;
- source-to-equation correspondence and semantic-role classification;
- compile/run and existing regression evidence;
- exact/approximate/finite-target provenance classification;
- future migration priorities and separate Issue recommendations.

## Out of scope

- source, compiler, test, benchmark, or numerical-result changes;
- automatic finiteization or hidden `Limit` conversion;
- provider SDK, credentials, network, or live QPU submission;
- QPU resource claims beyond existing provider-neutral diagnostics;
- changing S02 weights, duration, seed, baseline, or acceptance metrics.

## Acceptance conditions

- S02 `main_selection.sqx` remains compileable and its exact local and finite
  target lanes remain distinct.
- Existing S02 fixed-seed baseline and benchmark tests remain unchanged.
- Representative examples are classified with path-based evidence.
- Every gap is assigned a priority and a proposed follow-up boundary.
- Any implementation candidate is explicitly marked as requiring a new phase
  approval.

