# LISS-0458: Finite realization and executable artifact contract

| Field | Value |
|---|---|
| Status | **done — finite realization/artifact contract slice complete** |
| Phase | phase-3-refactor |
| Type | architecture / contract |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | realization/QPU IR boundary |
| Parent | WP-0119; WP-0121; ADR 0210–0213 |
| Depends on | LISS-0455, LISS-0456, LISS-0457 |
| Blocks | LISS-0459, LISS-0460, LISS-0461 |
| Branch | `codex/liss-0458-realization-artifact-contract` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0458--realization-and-artifact-atomicity) |
| Implementation permission | Phase 3 refactor — bounded contract slice only |
| Post-review requirement | Acceptance-spec review and typed Phase 1 approval |

Specify `RealizePlan` and `ExecutionArtifact` semantics without prematurely
adding types: dimensions, basis order, numeric finiteness, Suzuki policy,
approximation/error metadata, source/semantic fingerprints, ordered
instructions, duplicate preservation, and atomic no-artifact rejection. Decide
serialization and artifact ownership. Direct `Limit` remains rejected and no
implicit finiteization is allowed.

## Design detail

**In:** `RealizePlan`/`ExecutionArtifact`, canonical bytes, finite numbers,
dimensions, basis order, Suzuki policy, approximation/error data, fingerprints,
provenance, ordering, duplicates, and atomic rejection. **Out:** provider
payloads, routing, credentials, persistence, and direct `Limit` execution.

**Acceptance:** symbolic inspection produces no finite artifact; explicit
`Realize` succeeds only for valid finite dimensions/numbers/budget; unsupported
or non-unitary projection rejects before allocation/emission and retains source
provenance; canonical fingerprints are stable.

**Phase/evidence:** Phase 0 contract/ADR; Phase 1 Red serialization/rejection
vectors; Phase 2 minimum implementation; Phase 3 cross-consumer and rollback
review. Deliverables are schema, vectors, rejection matrix, and trace.
Planning record: `AIP-LISS-0458-2026-08-27-001` (L; N/A model metrics). New
DTOs need architecture approval.

## Phase 1 Red artifact

User approved the Phase 1 Red gate on 2026-08-27. Added only
`tests/test_liss_0458_realization_artifact_contract_red.py`. The test packet
covers symbolic/no-artifact rejection, explicit finite policy metadata and
provenance, instruction order and duplicate preservation, invalid finite
policy atomic rejection, and stable canonical serialization/fingerprints.

Red evidence: the intentionally absent
`compiler.staqex.realization_artifact` module produces the expected failure.
Python 3.14 `py_compile` and `git diff --check` pass; pytest is unavailable
locally. The reviewed tests remain unchanged and Phase 2 Green is not
authorized until Adjudicator test review.

## Phase 2 Green

The Adjudicator approved Phase 2 Green after the Red test review on
2026-08-27. Added the minimal provider-neutral
`compiler/staqex/realization_artifact.py` contract and threaded source identity
through the canonical Scientific Semantic IR for path compilation. The
implementation validates explicit finite plans, preserves policy/provenance,
creates stable canonical bytes and fingerprints, and returns no allocation or
provider payload on rejection. The reviewed tests were not changed.

Verification: the Red contract runs successfully as a plain Python test;
Python 3.14 `py_compile` and `git diff --check` pass. Full pytest remains
unavailable locally. Phase 3 refactor and closeout require separate approval.

## Phase 3 closeout

The Adjudicator approved Phase 3 on 2026-08-28. The refactor keeps semantic
fingerprints independent from filesystem source paths, separates source
fingerprint derivation, and centralizes atomic rejection construction. The
reviewed acceptance tests and externally observable behavior are unchanged.

Same-context review: canonical acceptance spec, WP-0121, LISS-0458, the
realization module, Scientific Semantic IR, pipeline, and reviewed tests were
re-read. No blocker was found within the bounded contract slice. LISS-0449,
Scientific Semantic IR integration, and LISS-0458 direct tests pass; Python
3.14 `py_compile` and `git diff --check` pass. Full pytest remains unavailable
locally. Review isolation was `same_context`, which is weaker than a separate
context review.

Process review: no operating-contract deviation or operational problem found.

Phase 3 exit: **DONE for the bounded finite realization/artifact contract
slice**. Provider integration, routing, credentials, live execution, and
broader numerical realization remain separately gated.
