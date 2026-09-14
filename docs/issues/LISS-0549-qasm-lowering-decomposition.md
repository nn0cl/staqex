# LISS-0549: QASM lowering decomposition

## Metadata

- Local issue ID: LISS-0549
- GitHub issue: none
- Status/phase: proposed / phase-0-design
- Type/priority: refactor / P1
- Initial/current planning size: L / L
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/qasm-lowering`

## Summary

Retain `backend.qasm.lower` public exports while extracting capability
preflight, semantic lowering, bounded AST compatibility, evolution lowering,
and resource verification into `backend/qasm/lowering/`.

## Planned extraction units

- `profiles.py`: target profile and immutable capability facts.
- `preflight.py`: finite, operation, limit and resource rejection.
- `semantic.py`: Scientific Semantic IR/QPU IR to circuit lowering.
- `ast_compat.py`: explicitly diagnostic-only bounded legacy pattern path.
- `evolution.py`: explicit/formal-limit/Hamiltonian lowering.
- `resources.py`: allocation and budget verification.

## Acceptance Notes

Accepted QASM, manifest/provenance, gate/qubit order, target fingerprint, and
diagnostics are byte/order identical. Unsupported meaning produces no partial
artifact or allocation. AST compatibility remains non-authoritative.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0543, LISS-0548
- Blocks: LISS-0550
- Related: QASM consumer migration and real-QPU readiness specifications

## Adjudicator Decision Points

Approve the boundary between canonical semantic lowering and bounded AST
compatibility. Any authority leak is a blocker, not a refactor exception.

## AI Planning Record — AIP-0549-001

- Status/date/size: proposed / 2026-09-11 / L
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: six lowering units; N/A token estimate
- Basis/confidence: 1,520 lines, 29 import consumers, 446-line AST path; high
- Assumptions: emitter formatting is untouched
- Revises/Superseded by: none

## Verification

Accepted/rejected QASM corpus, byte-for-byte output, allocation atomicity,
public imports, complete blocking suite, Spec Verification, cycles/diff checks.

## Process Review

- Outcome: not yet
- Lesson written: existing atomic-rejection lesson applied
- Template-feedback path: none
