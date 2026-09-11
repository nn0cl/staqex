# LISS-0544: Evaluator orchestration decomposition

## Metadata

- Local issue ID: LISS-0544
- GitHub issue: none
- Status/phase: proposed / phase-0-design
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

Approve the single-state-owner context protocol and each bounded extraction.
Implementation remains unauthorized until LISS-0543 is done and Phase 3 is
explicitly approved.

## AI Planning Record — AIP-0544-001

- Status/date/size: proposed / 2026-09-11 / L
- Agent/route: Codex host, model display unavailable; host + same-context review
- Scope/estimate: the five units above; N/A token estimate
- Basis/confidence: 6,571-line class and 93-file import blast radius; medium
- Assumptions: public facade and state identity remain stable
- Revises/Superseded by: none

## Verification

Public-symbol manifest, runtime-plan tests, fixed-seed Spec Verification suites,
sink/diagnostic snapshots, full blocking pytest, compile/import-cycle checks.

## Process Review

- Outcome: not yet
- Lesson written: no
- Template-feedback path: none
