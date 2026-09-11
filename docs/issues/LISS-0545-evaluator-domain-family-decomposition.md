# LISS-0545: Evaluator domain-family decomposition

## Metadata

- Local issue ID: LISS-0545
- GitHub issue: none
- Status/phase: proposed / phase-0-design
- Type/priority: refactor / P1
- Initial/current planning size: XL / XL
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/evaluator-domain-families`

## Summary

After orchestration extraction, split the remaining evaluator implementation by
meaningful runtime family without changing evaluation order or state ownership.

## Planned extraction units

1. `evolution.py`: ordinary/explicit/Hamiltonian evolution, Suzuki policy, grid
   evolution, and unitary resolution.
2. `operators.py`: operator tree/factory/method resolution, projectors, second
   quantization, and algebraic application.
3. `calls.py`: user/class/method call binding, partial application, frame and
   dead-coordinate handling.
4. `values.py`: pure classical expression, unit conversion, attributes,
   finiteization, inner/outer, norm, and set-comprehension helpers.

The 491-line `_bind_call` and 326-line Hamiltonian step must be decomposed by
dispatch family, not copied into another large class. Compatibility wrappers
may exist only while a unit is in flight and are removed in its Phase 3.

## Acceptance Notes

Operator semantics, units, evolution provenance, approximation obligations,
RNG order, Joint coordinate order, and diagnostics remain exact. Unsupported
families still fail closed before observable partial success.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0544
- Blocks: LISS-0550
- Related: DEC-0002, DEC-0005, Scientific Semantic IR authority

## Adjudicator Decision Points

Approve units separately. Any discovered semantic defect returns to Feature
Path and cannot be repaired inside this refactor issue.

## AI Planning Record — AIP-0545-001

- Status/date/size: proposed / 2026-09-11 / XL
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: four evaluator families; N/A token estimate
- Basis/confidence: high coupling and long dispatch methods; medium-low until
  LISS-0544 exposes the final state protocol
- Assumptions: no public API or behavior change
- Revises/Superseded by: none

## Verification

Per-family characterization, fixed-seed execution, numerical equality under
existing exactness rules, complete blocking suite, Spec Verification, import
cycles, line/function inventory, and diff checks.

## Process Review

- Outcome: not yet
- Lesson written: no
- Template-feedback path: none
