# LISS-0459: Target capability and resource profile hardening

| Field | Value |
|---|---|
| Status | **done — target capability preflight contract slice complete** |
| Phase | phase-3-refactor |
| Type | target contract |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | Host capability boundary |
| Parent | WP-0119; WP-0122 |
| Depends on | LISS-0457, LISS-0458 |
| Blocks | LISS-0460–0462 |
| Branch | `codex/liss-0459-target-capability-profile` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0459--capability-and-resource-preflight) |
| Implementation permission | Phase 3 refactor — bounded preflight slice only |
| Post-review requirement | Acceptance-spec review and typed Phase 1 approval |

Define and verify a provider-neutral capability profile for qubits, native
gates, connectivity, measurement bases, reset/feed-forward, shots, depth,
timing, payload limits, and resource budgets. Separate declared capability from
observed calibration. Every unsupported case must reject before allocation or
artifact emission with preserved ideal meaning.
## Design detail

**In:** provider-neutral profiles for qubits, native gates, topology,
measurement, reset/feed-forward, shots, depth, timing, payload/resource
budgets, and declared-versus-observed calibration. **Out:** SDKs, live device
queries, routing implementation, and capability inferred from provider name.

**Acceptance:** each target constraint has an observable preflight result;
unsupported targets reject before allocation/emission; profile version and
provenance are retained; fake profiles cannot claim physical calibration.

**Phase/evidence:** Phase 0 inventory; Phase 1 Red synthetic profiles; Phase 2
preflight implementation; Phase 3 regression/review. Deliverables are profile
schema, fixture catalog, rejection codes, and readiness report. Planning record:
`AIP-LISS-0459-2026-08-27-001` (L; N/A model metrics).

## Phase 1 Red artifact

User approved the Phase 1 Red gate on 2026-08-28. Added only
`tests/test_liss_0459_target_capability_profile_red.py`. The packet covers
version/provenance retention, declared-only calibration, qubit/gate/topology/
measurement/reset/feed-forward/shot/depth/timing/payload/cost rejection,
allocation-before-emission safety, and nonphysical synthetic evidence.

Red evidence: the intentionally absent
`compiler.staqex.target_preflight` module produces the expected failure.
Python 3.14 `py_compile` and `git diff --check` pass; pytest is unavailable
locally. Phase 2 Green requires Adjudicator test review.

## Phase 2 Green

The Adjudicator approved Phase 2 Green after the Red test review on
2026-08-28. Added the minimal provider-neutral
`compiler/staqex/target_preflight.py` contract with synthetic capability
profiles, resource demands, and fail-closed preflight decisions. The result
retains profile version/provenance, rejects each reviewed capability/resource
dimension before allocation or provider payload creation, and never claims
physical execution. The reviewed tests were not changed.

Verification: LISS-0459 and existing target-capability integration tests pass;
Python 3.14 `py_compile` and `git diff --check` pass. Full pytest remains
unavailable locally. Phase 3 refactor and closeout require separate approval.

## Phase 3 closeout

The Adjudicator approved Phase 3 on 2026-08-28. The preflight checks were
refactored into capability and resource helpers with one shared append rule;
the reviewed tests and observable decisions remain unchanged.

Same-context review re-read the acceptance spec, WP-0122, LISS-0459,
`target_preflight.py`, existing `target_capability.py`, and the reviewed test
packet. The bounded slice has no blocker: all named dimensions remain
fail-closed, profile provenance is retained, and synthetic profiles cannot
claim physical execution. LISS-0459 and existing target-capability tests pass;
Python 3.14 `py_compile` and `git diff --check` pass. Pytest remains
unavailable locally. Review isolation was `same_context`, weaker than a
separate-context review.

Process review: no operating-contract deviation or operational problem found.

Phase 3 exit: **DONE for the bounded target capability preflight slice**.
Routing, decomposition, QASM conformance, provider queries, credentials, and
live-QPU execution remain separately gated.
