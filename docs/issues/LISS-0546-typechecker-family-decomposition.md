# LISS-0546: Typechecker family decomposition

## Metadata

- Local issue ID: LISS-0546
- GitHub issue: none
- Status/phase: proposed / phase-0-design
- Type/priority: refactor / P1
- Initial/current planning size: XL / XL
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/typechecker-families`

## Summary

Retain `typecheck.TypeChecker`, `Ty`, and diagnostic behavior while extracting
declaration/body validation, operator algebra, dimensions, expression
inference, effects, and evolution policy into `typechecking/`.

## Planned extraction units

- `context.py`: one authoritative environment/diagnostic sink.
- `declarations.py`: duplicate, visibility, body, interface/implementation.
- `operators.py`: operator domains, indexed/binder and second-quantized checks.
- `dimensions.py`: units, arrays/tensors, promotion, conversions.
- `inference.py`: expression/call/pipe/binop/attribute inference dispatch.
- `evolution.py`: evolve and Suzuki contracts.

## Acceptance Notes

Diagnostic code, line, column, ordering, inferred types/units/effects, and
mutation of accepted AST annotations are exact pre/post matches. No subsystem
may emit directly outside the shared diagnostic sink.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0543
- Blocks: LISS-0550
- Related: type-first and scientific semantic specifications

## Adjudicator Decision Points

Approve `TypeCheckContext` ownership and unit sequence; do not combine this
branch with parser or behavior corrections.

## AI Planning Record — AIP-0546-001

- Status/date/size: proposed / 2026-09-11 / XL
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: six units; N/A token estimate
- Basis/confidence: 4,460-line class, several 200–580-line methods; medium
- Assumptions: AST and public `Ty` remain stable
- Revises/Superseded by: none

## Verification

Diagnostic goldens including neighboring positive cases, inferred annotation
snapshots, public imports, full blocking suite, Spec Verification, cycles and
diff checks.

## Process Review

- Outcome: not yet
- Lesson written: no
- Template-feedback path: none
