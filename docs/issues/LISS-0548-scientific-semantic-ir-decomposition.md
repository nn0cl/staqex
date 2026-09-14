# LISS-0548: Scientific Semantic IR decomposition

## Metadata

- Local issue ID: LISS-0548
- GitHub issue: none
- Status/phase: proposed / phase-0-design
- Type/priority: refactor / P0
- Initial/current planning size: L / L
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/scientific-semantic-ir`

## Summary

Keep `scientific_semantic_ir.py` as the canonical public facade while moving
model, fingerprint, runtime-plan, QPU-projection, finite-realization, and
algorithm-plan implementation into `scientific_semantic/`.

## Planned extraction units

- `model.py`: immutable semantic DTOs only.
- `fingerprint.py`: canonical serialization and identity.
- `builder.py`: source-derived semantic graph construction.
- `runtime_plan.py`: runtime execution projection.
- `qpu_projection.py`: finite QPU projection and rejection evidence.
- `realization.py`: explicit finite/evolution/algorithm records.

## Acceptance Notes

Scientific Semantic IR remains the sole compile-owned authority. Fingerprints,
node/source IDs, provenance, approximation and finite evidence, runtime plans,
QPU projections, and rejection ordering are exact. No compatibility DTO gains
execution authority.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0543
- Blocks: LISS-0549, LISS-0550
- Related: ADR 0211 and consumer-migration specification

## Adjudicator Decision Points

Architecture approval is required for DTO ownership and acyclic dependency
direction. Each consumer is audited before moving exports.

## AI Planning Record — AIP-0548-001

- Status/date/size: proposed / 2026-09-11 / L
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: six semantic units; N/A token estimate
- Basis/confidence: 2,008 lines and 14 direct import consumers; high
- Assumptions: facade owns backwards-compatible imports
- Revises/Superseded by: none

## Verification

Semantic serialization/fingerprint snapshots, every known consumer, positive
and unsupported projection cases, full suite, Spec Verification, cycles and
diff checks.

## Process Review

- Outcome: not yet
- Lesson written: existing semantic-authority lessons applied
- Template-feedback path: none
