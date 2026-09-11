# LISS-0557: Evaluator authority evidence contract

## Metadata

- Local issue ID: LISS-0557
- GitHub issue: none
- Status: proposed
- Phase: phase-0-design
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

## AI Planning Record — AIP-0557-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: Architecture decision then host implementation
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: accepted predecessor and successor contracts differ in
  observable storage/exception details; medium confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none

