# LISS-0544: Evaluator orchestration decomposition

## Metadata

- Local issue ID: LISS-0544
- GitHub issue: none
- Status: done
- Phase: done
- Type/priority: refactor / P1
- Initial/current planning size: L / L
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/evaluator-orchestration`

## Summary

Keep `runtime.evaluator.Evaluator`, `EvalResult`, `KernelError`, and helper
imports compatible while extracting runtime-plan dispatch, deferred execution,
measurement, and dynamic-lane mechanics into `runtime/evaluation/` modules.

## Planned extraction units

1. `plans.py`: plan-family validation and dispatch; no mutable state owner.
2. `deferred.py`: eligibility/free-variable/deferred cone and materialization.
3. `measurement.py`: mixed/pure terminal measurement and sink projection.
4. `dynamic.py`: dynamic QPU block/arm/reset/collapse mechanics.
5. `context.py`: a narrow protocol over the single `Evaluator` state; no copied
   RNG, Joint, scalar, object, or operator maps.

Each unit receives separate Phase 3 review. `evaluator.py` remains the public
facade and orchestration owner.

## Acceptance Notes

Fixed-seed results, sink call order, diagnostics, source spans, execution
authority, and public imports are exact pre/post matches. No new `run_unit()`
compatibility path is introduced. Extracted modules do not import the facade.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0543
- Blocks: LISS-0545, LISS-0550
- Related: evaluator semantic-authority specifications

## Adjudicator Decision Points

Approve the single-state-owner context protocol and the five bounded
extractions below. Implementation remains unauthorized until the Phase 1/2/3
gates are separately approved.

## Phase 0 acceptance / Architecture review

- Review packet: [LISS-0544 Phase 0 architecture review](../collaboration/reviews/2026-09-14-liss-0544-phase0-architecture-review.md)
- Canonical specification: [Core module decomposition](../specs/staqex-core-module-decomposition.md)
- Parent work plan: [WP-0160](../work-plans/WP-0160-core-module-decomposition.md)

### Confirmed concentration

- `Evaluator` is approximately 6,669 lines and owns runtime-plan dispatch,
  deferred binds, measurement, dynamic QPU lanes, evolution, operators,
  classical calls, and value evaluation.
- `_bind_call()` is approximately 492 lines;
  `_run_legacy_ast_body()` approximately 416 lines; and
  `_hamiltonian_evolve_one_step()` approximately 327 lines.
- The public `runtime.evaluator` import surface has a broad repository fan-out
  and remains a compatibility boundary.

### Accepted extraction contracts

| Unit | Owns | Receives | Must not own |
|---|---|---|---|
| `runtime/evaluation/plans.py` | runtime-plan family selection, validation, and dispatch choice | immutable plan, unit, narrow evaluator callbacks | RNG, mutable stores, AST fallback policy |
| `runtime/evaluation/deferred.py` | eligibility, free-variable/deferred-cone analysis, deferred materialization | unit/statements, explicit state context | a second evaluator state or semantic authority |
| `runtime/evaluation/measurement.py` | terminal pure/mixed measurement and sink projection | joint, measure statement, RNG/sink callbacks | parser/typechecker policy, POVM mathematics, provider calls |
| `runtime/evaluation/dynamic.py` | dynamic QPU block/arm/reset/collapse mechanics | joint, dynamic statement, explicit context callbacks | copied RNG/state maps, compile-time semantics |
| `runtime/evaluation/context.py` | narrow protocol describing access to the one live evaluator state | protocol methods only | mutable state storage and business policy |

`Evaluator` remains the public facade and the sole owner of RNG, scalar,
function/class/object, mixed-state, POVM, register, grid, and execution-state
maps. Extracted units may mutate state only through the explicit context
protocol; they must not copy or reconstruct those maps. Internal modules must
not import `runtime.evaluator`.

### Explicitly excluded from this Issue

- evolution, operator resolution, classical calls, and value families; these
  belong to LISS-0545 after orchestration extraction;
- parser/typechecker/Scientific Semantic IR/QASM decomposition;
- language behavior changes, diagnostic changes, public import removal,
  provider/QPU/AWS integration, Rust migration, and performance work;
- new generic `utils.py` or `common.py` modules without a named cohesive
  responsibility.

### Phase 0 decision

The existing WP-0160 architecture is sufficient; no new dependency, port,
provider, or semantic authority is introduced. The implementation must be
split into reviewable feature units, beginning with characterization and
Phase 1 Red tests for runtime-plan dispatch and state ownership. Each unit
requires its own phase evidence; a passing suite does not authorize the next
phase.

- Adjudicator approval: `LISS-0544 Phase 0 acceptance 承認`, received
  2026-09-14.
- Next gate: `LISS-0544 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0544 Phase 1 Red 承認`, received 2026-09-14.
- Added four test contracts for the extraction package, plan-dispatch seam,
  context import direction, and single mutable-state ownership.
- The tests intentionally remain Red until the approved extraction exists;
  no production implementation was changed.
- Next gate: `LISS-0544 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Review packet: [LISS-0544 Phase 1 Red test review](../collaboration/reviews/2026-09-14-liss-0544-phase1-red-review.md)
- Direct verification: **3 failed, 1 passed**, with no collection errors.
- The test failures identify the absent extraction package, dispatch seam, and
  context protocol; the existing Evaluator state-owner evidence remains
  passing.
- Next gate: `LISS-0544 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0544 Phase 1 Red テストレビュー承認`, received
  2026-09-14.
- The four tests are accepted as the bounded Red contract. They preserve the
  existing public facade and explicitly require the five internal extraction
  modules plus the single-state-owner context boundary.
- The three missing-extraction failures remain the intended Green work; the
  state-owner guard remains passing.
- Next gate: `LISS-0544 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0544 Phase 2 Green / Implementation 承認`,
  received 2026-09-14.
- Added the `runtime.evaluation` package, `EvaluatorContext` protocol, and
  `dispatch_runtime_plan`; removed the duplicated plan-family selector from
  `Evaluator` while preserving the public facade and mutable state owner.
- Added explicit deferred, measurement, and dynamic context contracts as
  bounded follow-up seams; their stateful bodies remain in `Evaluator` until
  their own extraction review.
- Verification: LISS-0544 **4 passed**; runtime-plan/canonical/callable/
  dynamic suites **21 passed**; broader evaluator selection **50 passed with 2
  pre-existing LISS-0486 active-Red failures**; static/lifecycle/coverage/diff
  checks passed.
- Next gate: `LISS-0544 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0544 Phase 3 Refactor 承認`, received
  2026-09-14.
- Re-read the extracted package, the `Evaluator` facade, and the import graph.
  The dispatch selector is cohesive, the context contract is explicit, and no
  extracted module imports back into the facade.
- No additional production refactor was necessary in this bounded phase:
  changing the remaining stateful bodies would cross the separately named
  deferred, measurement, and dynamic extraction seams. Readability and the
  single-state-owner invariant are therefore preserved without behavior drift.
- Verification: focused LISS-0544 and adjacent runtime suites **25 passed**;
  `py_compile`, lifecycle, coverage-ledger, and `git diff --check` passed.
- Next gate: none; final review approved 2026-09-14.

## AI Planning Record — AIP-0544-001

- Status/date/size: accepted / 2026-09-14 / L
- Agent/route: Codex host, model display unavailable; host + same-context review
- Scope/estimate: the five units above; N/A token estimate
- Basis/confidence: 6,571-line class and 93-file import blast radius; medium
- Assumptions: public facade and state identity remain stable
- Revises/Superseded by: none

## Verification

Public-symbol manifest, runtime-plan tests, fixed-seed Spec Verification suites,
sink/diagnostic snapshots, full blocking pytest, compile/import-cycle checks.

## Phase 3 final review result

- Review packet: [LISS-0544 Phase 3 final review](../collaboration/reviews/2026-09-14-liss-0544-phase3-final-review.md)
- Adjudicator approval: `LISS-0544 Phase 3 最終レビュー 承認`, received
  2026-09-14.
- The bounded decomposition is accepted. No behavior-changing refactor remains
  for this issue; deferred, measurement, and dynamic body extraction remain
  separately named follow-up work.

## Process Review

- Outcome: complete; phase evidence, review, and lifecycle records are aligned.
- Lesson written: no new lesson; `evaluator-state-ownership` was applied.
- Template-feedback path: none
- Process review: no operating-contract deviation or operational problem found.
