# LISS-0460: Transpilation, routing, and scheduling contract

| Field | Value |
|---|---|
| Status | **done — target-neutral route/schedule evidence slice complete** |
| Phase | phase-3-refactor |
| Type | backend architecture |
| Priority | P0 |
| Initial size | XL |
| Current size | XL |
| Owner | QPU projection/Host boundary |
| Parent | WP-0119; WP-0122 |
| Depends on | LISS-0458, LISS-0459 |
| Blocks | LISS-0461, LISS-0462 |
| Branch | `codex/liss-0460-transpile-route-schedule` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0460--routing-and-scheduling) |
| Implementation permission | Phase 3 refactor — bounded route/schedule slice only |
| Post-review requirement | Architecture/spec review and typed Phase 1 approval |

Decide ownership of native-gate decomposition, topology routing, SWAP policy,
measurement mapping, timing/depth scheduling, and approximation reporting.
Maintain source-to-artifact provenance and ensure routing never changes
blackboard meaning silently. Provider-specific transpilers remain adapters;
new technology choices require an ADR.
## Design detail

**In:** ownership of native decomposition, topology routing, SWAP insertion,
measurement mapping, depth/timing schedule, approximation, and source-to-
artifact mapping. **Out:** new provider/compiler selection, calibration
optimization, and silent source rewrites.

**Acceptance:** routes report inserted operations and cost; unsupported
connectivity/gates reject; logical qubits and measurements remain identifiable;
approximation/schedule metadata is explicit; rejected routes emit no artifact.

**Phase/evidence:** Phase 0 architecture decision; Phase 1 Red route fixtures;
Phase 2 one target-neutral implementation slice; Phase 3 static/dynamic
regression and review. Deliverables are ownership ADR, route model, fixtures,
cost report, and rollback rule. Planning record:
`AIP-LISS-0460-2026-08-27-001` (XL; N/A model metrics).

## Phase 1 Red artifact

User approved the Phase 1 Red gate on 2026-08-28. Added only
`tests/test_liss_0460_transpile_route_schedule_red.py`. The packet covers
deterministic routing, SWAP cost, measurement mapping, schedule depth/timing,
logical identity, provenance, and no-partial-artifact rejection for topology
and native-gate failures.

Red evidence: the existing `TargetPipelineResult` lacks the intentionally
unimplemented `cost` evidence field. Python 3.14 `py_compile` and
`git diff --check` pass; pytest is unavailable locally. Phase 2 Green requires
Adjudicator test review.

## Phase 2 Green

The Adjudicator approved Phase 2 Green after the Red test review on
2026-08-28. Extended the provider-neutral target pipeline with deterministic
cost evidence, measurement mapping, schedule depth/duration, and explicit
no-artifact/no-allocation/provider-payload fields. Measurement-aware paths add
target-neutral artifact provenance; legacy stage provenance remains compatible.
The reviewed tests were not changed.

Verification: LISS-0460 and existing target-routing integration tests pass
(11 tests); Python 3.14 `py_compile` and `git diff --check` pass. Full pytest
remains unavailable locally. Phase 3 refactor and closeout require separate
approval.

## Phase 3 closeout

The Adjudicator approved Phase 3 on 2026-08-28. Shared construction of
measurement-aware artifact evidence was extracted so success and rejection
paths consistently retain mapping and no-artifact state. Reviewed tests and
observable route/schedule behavior are unchanged.

Same-context review re-read the acceptance spec, WP-0122, LISS-0460,
`target_routing.py`, existing capability/preflight contracts, and the reviewed
tests. No blocker was found within the bounded slice: routing remains
deterministic, logical identity is preserved, cost and schedule evidence are
explicit, and unsupported routes remain atomic. LISS-0460 and existing
target-routing tests pass (11 tests); Python 3.14 `py_compile` and
`git diff --check` pass. Pytest remains unavailable locally. Review isolation
was `same_context`, weaker than a separate-context review.

Process review: no operating-contract deviation or operational problem found.

Phase 3 exit: **DONE for the bounded target-neutral route/schedule evidence
slice**. Native decomposition expansion, static/dynamic QASM conformance,
provider transpilers, and live-QPU execution remain separately gated.
