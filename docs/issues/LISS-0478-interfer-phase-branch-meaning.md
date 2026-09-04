# LISS-0478: Interfer/phase/branch meaning preservation

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor |
| Parent | WP-0113 |
| Design authority | [Meaning Preservation Specification](../specs/staqex-semantic-ir-meaning-preservation.md#residual-follow-up-design-liss-0478) |
| Depends on | LISS-0450 bounded Coin/when slice |
| Implementation permission | Phase 2 Green and Phase 3 Refactor approved |
| Next approval | None for this bounded slice; numerical/QPU realization remains separate |

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

## Phase 2 Green evidence

- `SemanticNode` now records `interfer` as a distinct `interference` meaning
  with quantum role, operand source IDs, relative-phase metadata, and branch
  relationship.
- QASM emission rejects an unsupported coherent-interference projection before
  canonical fallback and returns no QASM or allocated circuit artifact.
- The Red acceptance tests were updated only for the finalized two-operand
  contract; no gate synthesis or phase approximation was introduced.

## Phase 3 Refactor and verification

- Refactor keeps the semantic metadata on the canonical node and includes it in
  semantic fingerprints and ideal-meaning identity.
- Verification: `tests/test_liss_0478_interfer_phase_branch_meaning_red.py`,
  `tests/test_liss_0448_coin_mix_semantic_red.py`, and
  `tests/test_scientific_semantic_core_red.py`: **44 passed**.
- Full local regression: **1879 passed**.
- Spec verification: **161/161 passed**.
- No real QPU, provider SDK, network, or numerical realization was used.

Process review: no operating-contract deviation or operational problem found.
Isolation: same_context; weaker than separate_context.
