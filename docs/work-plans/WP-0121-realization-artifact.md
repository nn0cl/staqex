# WP-0121: Finite realization and executable artifact

| Field | Value |
|---|---|
| Status | **in progress — LISS-0458 bounded artifact contract complete; remaining WP-0121 acceptance gaps open** |
| Type | feature/release work plan |
| Size | L |
| Parent | [WP-0119](WP-0119-real-qpu-readiness-roadmap.md) |
| Issues | LISS-0458 |
| Depends on | WP-0120 |
| Blocks | WP-0122, WP-0123 |
| Canonical authority | ADR 0210–0213; ideal-expression/realization boundary specification |
| Owner boundary | UseCase realization boundary and provider-neutral QPU IR |
| Implementation permission | LISS-0458 Phase 3 complete; remaining WP-0121 work separately gated |
| Scope approval | User approved all Work Plans, 2026-08-27 |
| Post-review requirement | Issue-level acceptance review and typed Phase 1 approval |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |

## Goal

Define the provider-neutral boundary from ideal/source meaning to a finite
realization plan and executable artifact, including dimensions, basis order,
numeric validity, Suzuki/approximation metadata, fingerprints, provenance,
serialization, and atomic no-artifact rejection.

## Release exit

Accepted contract and fixtures distinguish symbolic inspection from explicit
`Realize`; unsupported or non-finite paths fail before allocation/emission;
ordered instructions and duplicate entries remain stable; source meaning is
retained on rejection.

No provider SDK, routing policy, credentials, or live execution is included.

## Included / excluded

Included: finite-plan schema, artifact envelope, canonical bytes, fingerprints,
provenance, numeric validation, resource preflight, and no-artifact rejection.
Excluded: device gate sets, topology routing, provider jobs, credentials,
persistence, and implicit `Limit` conversion.

## Acceptance scenarios

- Symbolic inspection does not create a finite artifact; explicit `Realize`
  does so only when dimensions, basis order, numerics, and budget are valid.
- Non-finite values, unsupported meaning, non-unitary projection, or budget
  overflow reject before allocation/emission while preserving provenance.
- Canonical fingerprints are stable; instruction order and duplicates remain
  observable.

## Phase and evidence gates

Phase 0 accepts the artifact contract. Phase 1 adds Red tests for serialization
and rejection. Phase 2 implements only the reviewed contract slice. Phase 3
verifies cross-module consumers, rollback/no-artifact behavior, and independent
review. Evidence includes specs, fixtures, fingerprint vectors, and a rejection
matrix.

## LISS-0458 closeout synchronization

LISS-0458 is complete for the bounded finite realization/artifact contract
slice. The WP remains in progress because the full release exit still needs
explicit resource-preflight/budget-overflow coverage and any remaining
cross-consumer acceptance evidence. No provider, credential, routing, or live
QPU work is implied.

## Risks / stop conditions

Stop if the artifact becomes a second semantic authority, finiteization becomes
implicit, or provider payloads leak into the provider-neutral contract.

## Required deliverables

- accepted `RealizePlan`/artifact envelope contract or explicit decision not
  to add those types;
- canonical serialization vectors and provenance/fingerprint fixtures;
- rejection matrix proving no allocation/no artifact;
- reviewed Red/Green/Refactor records and cross-consumer regression evidence.

## Planning record

- Planning record: `AIP-WP-0121-2026-08-27-001`.
- Author/environment: Codex host agent, local repository.
- Model/reasoning: N/A; runtime does not expose displayed per-task values.
- Planning size: L; basis is a cross-boundary contract with numeric and
  provenance invariants. Confidence: medium pending ADR/spec review.
