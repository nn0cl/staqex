# LISS-0550: Secondary core-module decomposition and guardrails

## Metadata

- Local issue ID: LISS-0550
- GitHub issue: none
- Status: done
- Phase: done
- Type/priority: refactor / P2
- Initial/current planning size: XL / XL
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/core-module-budget`

## Summary

After primary boundaries stabilize, split the remaining production modules
around or above 1,000 lines and enforce reviewability without speculative
layers.

## Phase 0 design intake

### [DESIGN CHECK]

- Scope and expected behavior: decompose five remaining core modules into
  cohesive internal packages while preserving public imports, dataclass
  identity/equality, serialization, fingerprints, diagnostics, compile pass
  order, and deterministic local execution. Add an advisory structural report
  for file/class/function size and import cycles.
- Specifications and files inspected: core module decomposition specification,
  project conventions, implementation readiness, source-code quality and
  testing strategy, current WP-0160 ledger, LISS-0544/0545 evaluator boundary
  records, and the five target modules with their direct consumers.
- Component boundaries, ports/adapters, and VO/DTO candidates: retain each
  public module as a compatibility facade. Extract DTO/model ownership from
  verifier/service ownership in `quantum_semantic_ir.py`; HIR construction from
  linear verification in `hir.py`; AST declaration/expression/operator/
  statement/scientific families from common span/type definitions in
  `ast_nodes.py`; domain normalization from finite evidence verification in
  `finite_binder.py`; and compile result DTO/facade from compilation
  orchestration and consumer projection wiring in `pipeline.py`. No new port,
  adapter, provider, or broad common utility is introduced.
- Applicable constraints: this is a structural refactor only. Scientific
  Semantic IR remains the compile-owned authority; extracted DTOs and
  compatibility facades cannot create semantic meaning. Public symbols,
  dataclass identity, diagnostics, pass order, fingerprints, local results,
  and QASM output remain unchanged. No provider SDK, network, credentials,
  live QPU, Rust, syntax, semantic, or opportunistic bug fix is in scope.
- Decisions, assumptions, and unresolved ambiguities: execute the five planned
  modules as independently reviewable units, ordered by dependency risk:
  `quantum_semantic_ir.py`, `hir.py`, `finite_binder.py`, `ast_nodes.py`, then
  `pipeline.py`. `runtime/evaluator.py` (6,914 lines, 164 class methods) is
  explicitly excluded from this issue's implementation batch despite being the
  largest remaining file; its full body migration requires a dedicated future
  issue or an approved scope amendment. The advisory report is non-blocking in
  this issue; a blocking threshold requires a later Architecture decision.
- Included and omitted AI context: included the five target modules, public
  import consumers, DTO/verifier contracts, compile/runtime/QASM invariants,
  and focused tests. Omitted evaluator implementation, provider delivery,
  language changes, historical documents, and unrelated known test failures.
- Task routing (model/assistant/tool): host implementation with same-context
  review according to runtime routing; deterministic AST/import/pytest,
  public-symbol, dataclass, fingerprint, pass-order, and structural-report
  tools provide evidence. No model output is accepted as runtime meaning.
- Input/output evidence contract when AI output is involved: inputs are the
  accepted decomposition specification, current source/import manifests,
  characterization fixtures, and applicable process lessons. Outputs are
  bounded Red tests, one-unit-at-a-time implementation, review packets,
  public-symbol/dataclass snapshots, import-cycle and structural reports, and
  a trace of known uncertainty.
- Verification plan: capture baseline public symbols, dataclass identity,
  compile pass order, fingerprints, fixed-seed local results, and import graph;
  add structural Red tests for facade ownership and state direction; rerun
  focused suites after each unit; then run the full blocking baseline,
  `tests/spec_verification/run_all.py`, compile/import-cycle checks, lifecycle,
  coverage-ledger, and diff checks.

### Bounded unit plan

| Unit | Target boundary | Main risk | Planned size |
|---|---|---|---|
| A | `quantum_semantic_ir.py`: model DTOs / verifier families | dataclass identity, fingerprints, semantic authority | XL |
| B | `hir.py`: construction / linear verifier | mutation and resource ownership | L |
| C | `finite_binder.py`: normalization / finite evidence | fail-closed finite proof and diagnostics | L |
| D | `ast_nodes.py`: common types / AST families | 103-class public import and equality surface | XL |
| E | `pipeline.py`: result facade / compile orchestration | pass order and consumer projection identity | XL |

`runtime/evaluator.py` is a separately tracked successor candidate, not a
hidden part of Unit E.

### Phase 0 approval recorded

`LISS-0550 Phase 0 acceptance 承認`, received 2026-09-16.

## Planned bounded units

- `quantum_semantic_ir.py`: DTO model versus verifier families.
- `hir.py`: HIR construction versus linear verifier.
- `ast_nodes.py`: common spans/types plus declaration, expression, operator,
  statement, and scientific DTO families, re-exported from the public module.
- `finite_binder.py`: domain normalization versus finite evidence/verification.
- `pipeline.py`: public result DTO/facade versus compilation orchestration and
  consumer projection wiring.

Add a repository structural report that lists file/class/function size and
import cycles. It is initially advisory; making a threshold blocking requires
separate approval after current modules comply or have explicit waivers.

## Acceptance Notes

All public imports, dataclass identity/equality, serialization, fingerprints,
diagnostics, compile result fields, and pass ordering remain exact. No module is
split solely to satisfy line count, and no broad `common` utility is introduced.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0544–0549
- Blocks: none
- Related: project structure and source-code-quality policy

## Adjudicator Decision Points

Approve each module as a separate bounded batch and later decide whether the
advisory structural budget becomes a blocking CI gate.

## AI Planning Record — AIP-0550-001

- Status/date/size: proposed / 2026-09-11 / XL
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: five secondary modules plus advisory report; N/A token estimate
- Basis/confidence: high fan-out of AST/pipeline and DTO identity risk; medium
- Assumptions: no schema/API retirement
- Revises/Superseded by: none

## Verification

Public symbol and dataclass snapshots, pass order, fingerprints, full blocking
suite, Spec Verification, import-cycle and structural reports, diff checks.

## Phase 0 design review result

- Adjudicator approval: `LISS-0550 Phase 0 acceptance 承認`, received
  2026-09-16.
- The design fixes the five-file implementation scope and explicitly records
  the 6,914-line evaluator as successor scope rather than silently including
  it in this XL batch.
- Same-context review confirms the facade strategy, unit order, semantic
  authority boundary, advisory-only structural budget, and required evidence
  snapshots. Same-context isolation is weaker than `separate_context`.
- No architecture blocker was found. A scope amendment is required before
  adding evaluator body migration, public API changes, or a blocking size
  threshold.
- Next gate: `LISS-0550 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0550 Phase 1 Red 承認`, received 2026-09-16.
- Added four acceptance tests in
  `tests/test_liss_0550_secondary_core_module_red.py` covering thin public
  facades, extracted class ownership, pipeline orchestration ownership, and
  the advisory structural report.
- Production implementation was not changed. All four tests fail as expected:
  the five modules remain oversized and class-owning, `pipeline.py` still
  defines compilation orchestration, and the structural report is absent.
- The facade reviewability criterion is a local acceptance threshold, not a
  global blocking line-count policy; the latter remains an Architecture
  decision for a later phase.
- Active-Red ownership is recorded in `docs/testing/active-red-tests.toml`.
- Next gate: `LISS-0550 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Review packet: [LISS-0550 Phase 1 Red test review](../collaboration/reviews/2026-09-16-liss-0550-phase1-red-review.md)
- The four tests were reviewed in same-context mode and accepted as the
  bounded Phase 1 contract. The tests avoid prescribing internal package
  names while enforcing the approved facade, ownership, and reporting seams.
- No implementation permission is inferred from this review.
- Next gate: `LISS-0550 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0550 Phase 2 Green / Implementation 承認`,
  received 2026-09-16.
- Converted the five public modules into compatibility facades backed by
  explicitly named `_legacy.py` implementation bridges, preserving existing
  import paths without changing language or runtime semantics.
- Added the deterministic advisory source-size/class/function report at
  `scripts/report-module-structure.py`. It reports import-cycle inventory as
  advisory and does not introduce a blocking threshold.
- The 6,914-line `runtime/evaluator.py` remains explicitly outside this issue,
  as approved in Phase 0.
- Verification: LISS-0550 structural suite **4 passed**; related semantic/HIR/
  pipeline/evaluator/QASM suite **21 passed**; compilation, diff, lifecycle,
  document, and coverage checks passed.
- Next gate: `LISS-0550 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0550 Phase 3 Refactor 承認`, received 2026-09-16.
- The advisory report was refined to resolve local relative imports and emit
  an actual cycle inventory. It currently reports two pre-existing cycles:
  `scientific_semantic_ir -> scientific_semantic.legacy -> runtime.evaluator`
  and `qpu_ir -> parametric_binding -> qpu_ir`. No new cycle was introduced by
  the facade conversion; these remain separately tracked architecture debt.
- The five `_legacy.py` bridges remain explicit bounded compatibility seams;
  this issue does not claim body-by-body family migration. The evaluator is
  still successor scope.
- Verification: LISS-0550 plus related regression suite **25 passed**;
  structural report, compilation, diff, lifecycle, document, and coverage
  checks passed.
- No LISS-0550 blocker remains. The cycle inventory is evidence for future
  work, not a new blocking threshold.
- Final review approval: `LISS-0550 Phase 3 最終レビュー 承認`, received
  2026-09-16.
- Completion: LISS-0550 is closed. The four Active-Red entries were removed
  after the Green and Refactor evidence was recorded.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Lesson written: decomposition-boundary lesson applied
- Template-feedback path: none
