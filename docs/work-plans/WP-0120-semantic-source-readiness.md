# WP-0120: Semantic and source-to-QASM readiness

| Field | Value |
|---|---|
| Status | **in progress — LISS-0455/LISS-0456/LISS-0457 Product/Tensor, LISS-0471 Measurement, and LISS-0472 Continuous/Open-system slices complete; broader family work deferred** |
| Type | feature/release work plan |
| Size | XL |
| Parent | [WP-0119](WP-0119-real-qpu-readiness-roadmap.md) |
| Issues | LISS-0455, LISS-0456, LISS-0457, LISS-0471, LISS-0472 |
| Depends on | WP-0118 governance baseline |
| Blocks | WP-0121, WP-0122 |
| Canonical authority | ADR 0211; scientific semantic consumer migration specification |
| Owner boundary | Compiler semantic layer and QASM entry ownership |
| Implementation permission | None; design and inventory only |
| Scope approval | User approved all Work Plans, 2026-08-27 |
| Post-review requirement | Issue-level acceptance review and typed Phase 1 approval |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |
| Current next | Proceed to next roadmap WP or design additional family slice; no family-wide implementation |

## Goal

Make source meaning and the canonical Scientific Semantic IR sufficiently
stable that every supported public QASM path consumes one owned projection.
Classify product/tensor, continuous/open-system, and measurement families as
supported, separately gated, or deferred without widening Coin/Mix semantics.

## Work units

1. Reconcile the open-work ledger and completed assets (LISS-0455).
2. Inventory and migrate public QASM entry ownership and legacy bypasses
   (LISS-0456).
3. Produce family-specific meaning and QPU-readiness dispositions (LISS-0457).
4. Validate the Measurement-family terminal/dynamic boundary (LISS-0471).
5. Validate the Continuous/Open-system QPU deferral boundary (LISS-0472).

## Release exit

Accepted semantic coverage matrix, no stale completion claims, canonical IR
ownership tests, explicit unsupported-family dispositions, and independent
review. No provider, artifact, or real-device work is included.

## Included / excluded

Included: source-to-IR inventory, public QASM facade ownership, legacy-path
classification, product/tensor/continuous/open-system/measurement disposition,
and acceptance specifications. Excluded: finite artifact serialization,
routing, SDKs, credentials, and unapproved syntax changes.

## Acceptance scenarios

- A supported source program produces one compile-owned Scientific Semantic IR
  identity consumed by each selected QASM entry point.
- A legacy AST/DTO or caller-injected string cannot override canonical meaning.
- Unsupported meaning remains inspectable with provenance and is rejected before
  QASM/artifact emission; `State<T>` and terminal `measure` remain unchanged.

## Phase and evidence gates

Phase 0 produces the inventory and accepted scope. Phase 1 adds reviewed Red
tests only. Phase 2 migrates one bounded consumer slice after implementation
approval. Phase 3 records independent review, full regression, rollback
evidence, and register synchronization. Deliverables are the coverage matrix,
fixtures, migration diff, and trace/review records.

## Risks / stop conditions

Stop if the work changes ADR 0211, `Realize`, `State<T>`, terminal `measure`,
or source syntax. A passing ordinary QASM fixture does not prove deferred
meaning-family support.

## Required deliverables

- canonical consumer inventory with owner, disposition, and retirement proof;
- accepted family coverage matrix and representative `.sqx` fixtures;
- reviewed Red test list and one bounded migration diff;
- independent review packet and synchronized Issue/register status.

## Planning record

- Planning record: `AIP-WP-0120-2026-08-27-001`.
- Author/environment: Codex host agent, local repository.
- Model/reasoning: N/A; runtime does not expose displayed per-task values.
- Planning size: XL; basis is multiple semantic consumers and architecture
  boundaries. Confidence: medium pending inventory review.

## Approval

Architecture/specification approval precedes Phase 1 Red; implementation
approval is limited to reviewed consumer slices.
