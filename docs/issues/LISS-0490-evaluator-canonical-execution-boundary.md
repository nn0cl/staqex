# LISS-0490: Evaluator canonical execution boundary

| Field | Value |
|---|---|
| Status | **phase-1-red — eight evaluator boundary tests fail as intended; awaiting Phase 2 Green approval** |
| Phase | phase-1-red |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Related Issues | [LISS-0489](LISS-0489-symbolic-ir-canonical-inspection.md), [LISS-0447](LISS-0447-residual-semantic-consumer-reconciliation.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0490-evaluator-canonical-execution-boundary) |
| Existing authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md), ADR 0211 |
| Architecture approval | Approved by Adjudicator 2026-08-31; ADR 0211 boundary retained |
| Implementation permission | Phase 1 Red tests and fixture approved; no production implementation permission |
| Next approval | Phase 2 Green approval |

## Design intake

- Scope: put the runtime evaluator behind an explicit canonical semantic
  execution boundary so AST dispatch is no longer an independent semantic
  authority.
- Included context: `compiler/staqex/runtime/evaluator.py`, pipeline
  `execution_authority`, `ScientificSemanticIR`, `SemanticInspectionResult`,
  State/Measure runtime contracts, `RngPort`, `MeasureSinkPort`, ADR 0211, and
  the consumer-migration Spec.
- Omitted context: provider SDKs, QPU/AWS, Rust, solver/numerical migration,
  continuous lowering, and broad evaluator feature expansion.
- Routing: strong architecture review for boundary design and deterministic
  runtime acceptance tests; no external AI/provider output.
- Applicable lessons: canonical authority must be observable; compatibility
  paths require explicit ownership and exit evidence; no hidden semantic
  rebuild may remain behind a passing output snapshot.

## Objective

Preserve existing local evaluator behavior while making `ScientificSemanticIR`
the source-derived authority for execution eligibility, state/role transitions,
and terminal measurement. AST-specific mechanics may remain temporarily only
when the canonical semantic node and source identity are supplied explicitly.

## Proposed boundary

```text
CompileResult.scientific_semantic_ir
        │
        ▼
CanonicalExecutionRequest(semantic_ir, source, ports, policy)
        │
        ▼
Evaluator execution adapter
        ├─ State<T> remains a non-collapsed runtime carrier
        ├─ terminal Measure is the collapse boundary
        └─ RngPort / MeasureSinkPort remain external ports
```

- The compile-owned semantic snapshot is passed explicitly to the evaluator
  entry point or narrow request DTO.
- The request carries source identity/fingerprint and a validated execution
  lane, but no provider credentials or finite artifacts.
- AST nodes without a matching canonical source node are rejected before
  execution; matched AST nodes are mechanics only.
- Inspection/snapshot operations remain non-destructive and do not become a
  second evaluator authority.
- Ports remain injected interfaces; evaluator code does not import providers,
  network clients, or persistence adapters.

## Candidate DTO and invariants

`CanonicalExecutionRequest` is a design candidate, not an approved type. If
implemented, it must carry a `ScientificSemanticIR` whose authority is
`scientific_semantic_ir`, a matching source identity/fingerprint, canonical
source node IDs for every executed action, and explicit `Realize` evidence for
finite execution. Port references are interfaces, not concrete adapters.

## Acceptance scenarios for Phase 1 Red

1. Compiled local execution receives the same canonical semantic object identity
   and source fingerprint.
2. Evaluator execution without canonical semantic input rejects before state
   mutation or measurement.
3. An AST action absent or mismatched in canonical IR fails closed with no
   fabricated result, allocation, or partial measurement.
4. `State<T>` and non-terminal inspection remain uncollapsed and emit no
   `MeasureSinkPort` sample.
5. Terminal `Measure` collapses and emits through the sink exactly at that
   boundary with source provenance.
6. Exact/symbolic input without explicit `Realize` creates no finite
   allocation, gate list, or hidden numerical plan.
7. Fake `RngPort` and `MeasureSinkPort` observe only their authorized effects;
   no provider/network adapter is imported or called.
8. Repeated execution of one canonical snapshot preserves authority,
   fingerprint, and transition provenance.

## Phase split and allowed files

- Phase 1 Red: fixed evaluator boundary tests and minimal source fixtures only;
  no evaluator production changes.
- Phase 2 Green: smallest request/entry-point validation and one representative
  local execution path; preserve evaluator mechanics.
- Phase 3: split or retire AST authority paths after state, measurement, port,
  no-bypass, and unchanged-neighbor evidence.

Initial Phase 1 candidate: `tests/test_liss_0490_evaluator_canonical_execution_boundary_red.py`,
one state/terminal-measure fixture, and this Issue/Spec/WP/review records.

## Non-goals and stop conditions

No evaluator rewrite, language change, simulator backend, finiteization policy,
provider/QPU/AWS, Rust, solver, or broad example migration. Stop for a new ADR
if the boundary changes language meaning, port contracts, persistence,
concurrency, or deployment technology.

## Architecture approval request

Approve or reject the explicit canonical execution request boundary, the
AST-as-mechanics-only rule, State/Measure invariants, and provider-neutral
local scope. Approval does not authorize Phase 1 tests or implementation.

## Architecture approval result

- The explicit compile-owned `ScientificSemanticIR` execution boundary is
  accepted for this Issue.
- AST-only execution rejection, State/Measure invariants, no hidden
  finiteization, and injected-port constraints are accepted as Phase 1
  acceptance targets.
- No new language semantics, provider technology, port contract, concurrency
  model, or implementation permission is created by this approval.

## Phase 1 Red readiness

The exact Phase 1 candidate is fixed to
`tests/test_liss_0490_evaluator_canonical_execution_boundary_red.py` and one
state/terminal-measure fixture. The eight acceptance scenarios in this Issue
will be tested without changing evaluator production code. Phase 1 Red
requires a separate approval before those files are created.

Phase 1 Red approval was granted before creation.

## Phase 1 Red result

- Added `tests/test_liss_0490_evaluator_canonical_execution_boundary_red.py`
  with the eight approved scenarios.
- Added `tests/fixtures/semantic_core/evaluator_boundary.sqx`.
- Red verification: **8 failed**, with no collection errors. The failures
  expose the missing canonical evaluator input, missing no-canonical
  rejection, and missing source/port execution contract.
- No evaluator production code, port implementation, provider, or runtime
  behavior was changed.
