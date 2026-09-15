# LISS-0557: Evaluator authority evidence contract

## Metadata

- Local issue ID: LISS-0557
- GitHub issue: none
- Status: done
- Phase: done
- Type: runtime contract reconciliation
- Priority: P1
- Initial/current planning size: M / M
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0557-evaluator-authority`

## Summary

Reconcile two LISS-0486 assertions with the later runtime-plan architecture:
whether canonical identity belongs on mutable `Evaluator.semantic_ir` or on
the execution result/plan, and whether invalid authority raises `ValueError`
or the stable `KernelDiagnosticError` boundary.

## Phase 0 design intake

### [DESIGN CHECK]

- Scope and expected behavior: reconcile LISS-0486 with the accepted
  LISS-0490/0493 runtime-plan boundary. One compile-owned
  `ScientificSemanticIR` must be the execution authority; absent, synthetic,
  or caller-injected authority must fail before runtime effects. Identity and
  rejection evidence must be observable without creating a second mutable
  semantic owner.
- Specifications and files inspected: ADR 0211, LISS-0486, LISS-0490,
  LISS-0491–0494, the Scientific Semantic consumer-migration specification,
  active-Red remediation specification, runtime execution model, evaluator,
  pipeline, canonical evaluator tests, and project conventions.
- Component boundaries, ports/adapters, and VO/DTO candidates: the pipeline
  owns source-derived `ScientificSemanticIR`; an internal immutable
  `CanonicalExecutionEvidence` carried by the runtime result/plan owns the
  observable authority identity, source identity, and fingerprint. Evaluator
  owns execution mechanics and injected `RngPort`/`MeasureSinkPort` effects.
  `Evaluator.semantic_ir` may remain only as a read-only compatibility view.
- Applicable constraints: preserve `State<T>` before terminal `Measure`, port
  effects, diagnostics, provenance, and local result envelopes. Keep
  `E_EVALUATOR_CANONICAL_AUTHORITY` as the stable rejection code and use
  `KernelDiagnosticError` as the runtime boundary. No `run_unit()` restoration,
  AST authority, provider/QPU/AWS, Rust, release policy, or broad evaluator
  decomposition.
- Decisions, assumptions, and unresolved ambiguities: recommend immutable
  result/plan evidence as canonical, with a read-only evaluator observation
  during migration. Whether `KernelDiagnosticError` should inherit
  `ValueError` for existing catch compatibility is an explicit ADR decision;
  it must not create a second rejection path or mutable injection setter.
- Included and omitted AI context: included authority boundaries, runtime
  plan, evaluator entrypoints, result envelope, ports, and predecessor tests.
  Omitted provider delivery, solver, syntax, historical narratives, and broad
  evaluator decomposition.
- Task routing (model/assistant/tool): Architecture Path design by the host
  with same-context review; deterministic caller inventory, AST inspection,
  identity assertions, exception hierarchy checks, and focused runtime tests.
- Input/output evidence contract when AI output is involved: inputs are the
  accepted ADR/spec contracts and current evaluator/pipeline behavior. Outputs
  are this decision note, a proposed ADR, Phase 1 Red tests, caller inventory,
  no-effect rejection evidence, and a review packet.
- Verification plan: freeze current caller and exception behavior; Red must
  assert one compile-owned identity, no setter/injection authority, result/plan
  evidence, fail-closed no-effect rejection, and the stable diagnostic code.
  Green changes only the minimum authority surface; Refactor verifies
  State/Measure, ports, provenance, and no `run_unit()`/AST bypass.

### Recommended architecture decision

Adopt ADR 0225: canonical authority is immutable execution evidence owned by
the compile-to-runtime request/result, while `Evaluator.semantic_ir` is at
most a read-only compatibility observation. Use `KernelDiagnosticError` with
`E_EVALUATOR_CANONICAL_AUTHORITY` as the authoritative failure boundary; any
`ValueError` catch compatibility must be an explicit exception-hierarchy/API
decision.

## Acceptance Notes

- One compile-owned Scientific Semantic IR identity must reach execution and be
  observable without introducing duplicate mutable evaluator authority.
- Caller-injected objects fail before plan execution or effects.
- Preserve stable diagnostic code `E_EVALUATOR_CANONICAL_AUTHORITY` and no
  fabricated result; exception-class compatibility requires explicit decision.
- Do not reintroduce `run_unit()` or AST semantic authority.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0486, LISS-0491–0499, WP-0107

## Adjudicator Decision Points

- Choose the canonical observable identity surface and public exception
  compatibility before altering either test or implementation.

## Verification

Two active nodes, runtime-plan source identity, result execution authority,
no-effect rejection, and `run_unit()` absence.

## Architecture review result

- Scope approval: `LISS-0557 Phase 0 acceptance / Architecture review`,
  received 2026-09-16.
- Same-context review confirms this is an authority/API compatibility decision,
  not a reason to restore mutable evaluator authority.
- Proposed ADR 0225 records immutable execution evidence as the canonical
  observable surface, a read-only compatibility view during migration, and
  `KernelDiagnosticError` as the coded failure boundary.
- ADR 0225 was accepted: `ADR 0225 Architecture 承認`, received 2026-09-16.
- No Phase 1 test creation or implementation is authorized by this architecture
  approval. Same-context isolation is weaker than `separate_context`.
- Next gate: `LISS-0557 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0557 Phase 1 Red 承認`, received 2026-09-16.
- The two pre-existing LISS-0486 active nodes were adopted as the exact Red
  contract; no duplicate test file was created.
- Direct execution: **2 failed, 1 passed**, with no collection errors. The
  failures expose the missing `Evaluator.semantic_ir` authority observation
  and the existing `KernelDiagnosticError` versus historical `ValueError`
  compatibility mismatch.
- No production implementation or test assertion was changed.
- Active-Red ownership is recorded in `docs/testing/active-red-tests.toml`.
- Next gate: `LISS-0557 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0557 Phase 1 Red テストレビュー承認`, received
  2026-09-16.
- The two LISS-0486 nodes were accepted as the bounded authority/API
  compatibility contract. Their historical `ValueError` wording is now an
  explicit ADR 0225 implementation decision surface, not an implicit override
  of the coded diagnostic boundary.
- No implementation permission is inferred from this review.
- Next gate: `LISS-0557 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0557 Phase 2 Green / Implementation 承認`,
  received 2026-09-16.
- Added a setter-free `Evaluator.semantic_ir` compatibility observation backed
  by the canonical object received for the current run.
- Added immutable `CanonicalExecutionEvidence` to `EvalResult`, carrying the
  exact IR identity, authority, source identity, and semantic fingerprint.
- Made `KernelDiagnosticError` explicitly compatible with legacy `ValueError`
  catches while preserving `E_EVALUATOR_CANONICAL_AUTHORITY` and fail-closed
  behavior before runtime effects.
- `run_unit()` and AST semantic authority were not restored.
- Verification: LISS-0486, LISS-0490, and LISS-0494 suites **15 passed**;
  compilation, diff, lifecycle, document, and coverage checks passed.
- Next gate: `LISS-0557 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0557 Phase 3 Refactor 承認`, received 2026-09-16.
- Cleared the read-only authority observation before each canonical invocation
  so a rejected caller-injected request cannot expose stale authority from a
  previous successful run.
- Same-context review rechecked the result evidence, exception hierarchy,
  State/Measure boundary, ports, and no-`run_unit()`/AST-authority boundary.
- Verification: focused LISS-0486/0490/0494 suites **15 passed**;
  stale-authority clearance check passed; compilation, diff, lifecycle,
  document, and coverage checks passed.
- No Phase 3 blocker remains. Next gate:
  `LISS-0557 Phase 3 最終レビュー 承認`.

## Completion

- Final review approval: `LISS-0557 Phase 3 最終レビュー 承認`, received
  2026-09-16.
- LISS-0557 is closed. The two Active-Red entries were removed after the
  canonical authority evidence and compatibility boundary passed.

## AI Planning Record — AIP-0557-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: Architecture decision then host implementation
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: accepted predecessor and successor contracts differ in
  observable storage/exception details; medium confidence

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Lesson written: canonical authority and compatibility-boundary lessons applied
- Template-feedback path: none
