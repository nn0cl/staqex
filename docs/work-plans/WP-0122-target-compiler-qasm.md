# WP-0122: Target compilation, routing, and QASM conformance

| Field | Value |
|---|---|
| Status | **done — bounded static/dynamic QASM readiness complete** |
| Type | feature/release work plan |
| Size | XL |
| Parent | [WP-0119](WP-0119-real-qpu-readiness-roadmap.md) |
| Issues | LISS-0459, LISS-0460, LISS-0461, LISS-0462 |
| Depends on | WP-0121 |
| Blocks | WP-0123 |
| Canonical authority | ADR 0085, 0086, 0201, 0210–0213; backend target contract |
| Owner boundary | Target projection, transpiler, scheduler, and QASM adapter |
| Implementation permission | Bounded Issues complete; provider/live-QPU work excluded |
| Scope approval | User approved all Work Plans, 2026-08-27 |
| Post-review requirement | Issue-level acceptance review and typed Phase 1 approval |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |

## Goal

Turn a valid finite artifact into a target-aware static or dynamic QASM
artifact while preserving provenance and reporting all target constraints,
decompositions, routing, depth/timing, measurement mapping, and approximation.

## Work units

- Capability/resource profile and preflight rejection (LISS-0459).
- Native-gate decomposition, topology routing, scheduling, and cost evidence
  (LISS-0460).
- Offline static QASM conformance (LISS-0461).
- Offline dynamic QASM conformance for measurement/feed-forward/reset/reuse
  (LISS-0462).

## Release exit

Supported static/dynamic subsets are explicit; offline fixtures pass; an
unsupported device or operation rejects before submit; no AST fallback or
implicit measurement remains.

## Included / excluded

Included: capability profiles, resource checks, native decomposition, topology
routing, schedule/depth evidence, static/dynamic QASM conformance, and
unsupported-target rejection. Excluded: provider SDK behavior, credentials,
real queue data, deployment, and source-semantic changes for device convenience.

## Acceptance scenarios

- A valid artifact rejects before allocation when qubit, gate, connectivity,
  timing, shot, payload, or dynamic limits are exceeded.
- Static and dynamic QASM preserve source, semantic, artifact, and measurement
  provenance; unsupported dynamic behavior is not silently downgraded.
- Routing/decomposition reports added operations, depth, timing, and
  approximation without silently changing blackboard meaning.

## Phase and evidence gates

Phase 0 freezes target envelope and ownership. Phase 1 adds Red tests with
synthetic capability profiles. Phase 2 implements one reviewed static/dynamic
slice. Phase 3 runs offline QASM validation, full regression, and independent
review; no provider network is required.

## Risks / stop conditions

Stop if routing requires an unapproved provider technology, dynamic QASM adds
implicit collapse, or an emitter falls back to an empty/alternate artifact
while reporting success.

## Required deliverables

- target capability/resource matrix with synthetic profiles;
- ownership decision for decomposition, routing, scheduling, and measurement
  mapping;
- static and dynamic QASM conformance fixtures and rejection vectors;
- target artifact provenance, depth/timing/cost report, and independent review.

## Planning record

- Planning record: `AIP-WP-0122-2026-08-27-001`.
- Author/environment: Codex host agent, local repository.
- Model/reasoning: N/A; runtime does not expose displayed per-task values.
- Planning size: XL; basis is multiple compiler/adapter boundaries and
  target-dependent semantics. Confidence: medium pending capability inventory.

## Closeout

LISS-0459, LISS-0460, LISS-0461, and LISS-0462 are complete for the bounded
provider-neutral target/preflight/routing/QASM contracts. Offline fixtures and
direct contract checks pass. Provider SDK behavior, credentials, network,
deployment, and live QPU execution remain outside this WP.
