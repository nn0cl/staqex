# LISS-0448 Architecture Acceptance Trace

## Decision

- User approval: `承認`, 2026-08-23.
- Accepted architecture: preserve structured `Coin`/`Mix` branch meaning in
  canonical Scientific Semantic IR; keep finite QPU realization explicit and
  fail closed; prohibit generic mixture-to-unitary fallback.
- ADR: `docs/architecture/adr/0213-canonical-mixture-branch-meaning-and-qpu-boundary.md`.
- Companion contract: `docs/specs/staqex-qpu-capability-rejection-contract.md`
  accepted for the canonical mixture/QPU boundary.

## Phase boundary

- This is Architecture approval and Spec/ADR acceptance.
- It does not approve Phase 1 Red, implementation, Phase 2 Green, Phase 3
  Refactor, or merge.
- LISS-0448 returns to a new Phase 1 Red extension for branch-rule preservation
  and legacy fail-closed coverage.

## Required evidence before implementation

- Source-derived branch pattern, else marker, control identity, and declared
  mixture rule are structurally represented.
- Semantic fingerprint changes when branch meaning changes.
- Direct legacy `Coin`/`Mix` callers are inventoried or fail closed; no CX/H+CX
  fallback remains for mixture semantics.
- Independent review confirms blackboard fidelity and explicit QPU boundary.
