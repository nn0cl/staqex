# LISS-0478: Interfer/phase/branch meaning preservation

| Field | Value |
|---|---|
| Status | **Phase 1 Red complete; Phase 2 Green approval required** |
| Phase | phase-1-red |
| Parent | WP-0113 |
| Design authority | [Meaning Preservation Specification](../specs/staqex-semantic-ir-meaning-preservation.md#residual-follow-up-design-liss-0478) |
| Depends on | LISS-0450 bounded Coin/when slice |
| Implementation permission | None |
| Next approval | Typed Phase 2 Green approval |

## Scope

Define canonical semantic roles for interference, phase, branch/control
relationships, operand identity, exactness, and provenance. Define explicit
unsupported finite projection behavior.

## Acceptance scenarios

- Branch/control identity survives semantic projection.
- Phase is not discarded or reinterpreted as classical probability.
- Unsupported finite projection retains source meaning and emits no artifact.
- Source-derived nodes remain inspectable without QPU support.

## Exclusions and stop conditions

No gate synthesis, numerical approximation, provider, QPU, or Hilbert-space
storage choice. Stop for ADR review if approximation or new representation is
required.

## Phase 1 candidate files

Representative `.sqx` fixtures, meaning-role assertions, negative projection
tests, and this Issue/spec/review record only.

## Phase 1 Red evidence

- Added `tests/fixtures/semantic_meaning/interfer_phase_branch.sqx`.
- Added `tests/test_liss_0478_interfer_phase_branch_meaning_red.py` with three
  acceptance scenarios covering distinct meaning, operand/phase/branch
  metadata, and atomic unsupported QPU projection.
- Red verification: **3 failed**, with no collection errors.
- The failures identify the intended missing Green behavior: `interfer` is
  currently classified as a generic expression, operand structure is not
  exposed as a dedicated semantic contract, and QASM emits a fallback circuit.
- No production implementation, gate synthesis, numerical approximation,
  provider behavior, or QPU execution was changed.
