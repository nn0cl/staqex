# LISS-0442: S02 and representative-example migration inventory

| Field | Value |
|---|---|
| Status/phase | **Phase 0 complete — Phase 1 Red not approved** |
| WorkPlan | [WP-0105](../work-plans/WP-0105-s02-corpus-migration-inventory.md) |
| Specification | [S02 and representative-example migration inventory](../specs/staqex-s02-corpus-migration-inventory.md) |
| Scope approval | User approval recorded 2026-08-18 |
| Implementation approval | **Not granted** |
| Independent review | [2026-08-19 Phase 0 review](../collaboration/reviews/2026-08-19-liss-0442-phase0-review.md) |
| Re-review | [2026-08-19 Phase 0 re-review](../collaboration/reviews/2026-08-19-liss-0442-phase0-rereview-02.md) |
| Final review | [2026-08-19 Phase 0 final review](../collaboration/reviews/2026-08-19-liss-0442-phase0-rereview-03.md) |

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

The Phase 0 inventory result is recorded in the linked Spec under “Phase 0
inventory result”. The official corpus boundary is the 26 SV-09 entrypoints
plus one README case;
S02 is a separate showcase lane because it needs HostInputPort data and has a
finite-target comparison lane.

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

## Review disposition

The independent reviewer reported `NOT READY`. Findings were accepted as
design-preserving documentation corrections: record the actual inventory,
define the corpus/S02/WP-0104 boundaries, include deterministic evidence, and
add architecture/type/state safety lenses. No finding authorizes Phase 1 Red,
implementation, numerical migration, Provider SDK work, or live QPU submit.

The subsequent correction loop reached `COMPLETE`: the final independent
review returned `READY`, all findings were resolved in documentation/evidence,
and no review blocker remains. This closes only LISS-0442 Phase 0. Phase 1
Red and implementation remain unapproved.
