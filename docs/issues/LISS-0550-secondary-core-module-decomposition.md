# LISS-0550: Secondary core-module decomposition and guardrails

## Metadata

- Local issue ID: LISS-0550
- GitHub issue: none
- Status/phase: proposed / phase-0-design
- Type/priority: refactor / P2
- Initial/current planning size: XL / XL
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/core-module-budget`

## Summary

After primary boundaries stabilize, split the remaining production modules
around or above 1,000 lines and enforce reviewability without speculative
layers.

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

## Process Review

- Outcome: not yet
- Lesson written: no
- Template-feedback path: none
