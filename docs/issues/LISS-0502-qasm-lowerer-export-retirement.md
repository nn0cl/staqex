# LISS-0502: QASM lowerer export retirement

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0501](LISS-0501-qasm-measure-only-fallback-retirement.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0502-qasm-lowerer-export-retirement) |
| Scope approval | User approved continuation on 2026-09-02 |
| Architecture approval | Existing QASM fallback boundary |
| Phase 1 Red approval | User approved continuation on 2026-09-02 |
| Implementation permission | Phase 2 Green and Phase 3 review approved by user |
| Next approval | Next QASM/consumer migration Phase 1 Red |

## [DESIGN CHECK]

- **Scope and expected behavior:** remove the lowerer re-export from emitter;
  keep the implementation available only from its owning module.
- **Specifications and files inspected:** WP-0107, LISS-0501, QASM emitter,
  QASM lowerer, fallback tests, and migration Spec.
- **Component boundaries:** canonical QASM emits QPU IR; compatibility lowerer
  belongs to `backend.qasm.lower`, not the emitter facade.
- **Applicable constraints:** Phase 1 Red only; no lowerer deletion, provider,
  QPU, AWS, Rust, or output behavior change.
- **Decisions and ambiguities:** existing tests that monkeypatch the re-export
  must migrate to the owning module in Phase 2; explicit lowerer callers remain
  separately controlled.
- **Verification plan:** test absent emitter re-export, no canonical reference,
  owning-module availability, and provider-neutrality.

## Acceptance scenarios for Phase 1 Red

1. Given the QASM emitter module, then it does not expose the legacy lowerer.
2. Given canonical QASM emission, then `emit_unit()` does not reference or call
   the legacy lowerer.
3. Given an explicit compatibility caller, then the owning lowerer module still
   exposes `lower_unit_to_circuit`.
4. Given the emitter, then no provider SDK dependency is introduced.

## Phase boundary

Phase 1 creates only the failing API-boundary contract. Phase 2 removes the
re-export and updates tests/callers to the owning module. Phase 3 verifies
unchanged canonical and compatibility behavior.

## Phase 1 Red result

- Added `tests/test_liss_0502_qasm_lowerer_export_retirement_red.py`.
- Red verification: **1 failed, 3 passed**, with no collection errors. The
  failure proves the emitter still exposes the compatibility re-export.
- No production implementation was changed in this phase.

Human review of the Red contract is required before Phase 2 Green.

## Phase 2 Green result

- Removed the lowerer re-export from `backend.qasm.emitter`.
- Migrated fallback-test monkeypatches to the owning
  `backend.qasm.lower` module; canonical emitter behavior is unchanged.
- The owning lowerer remains available for explicit compatibility callers.
- LISS-0502 plus LISS-0501, finite projection, consumer migration, QASM
  public-entry, and resource-wiring tests **47 passed**; `py_compile` and
  `git diff --check` passed.
- One pre-existing LISS-0447 unsupported-evolution assertion remains failing
  outside this export-boundary change and is not altered here.

## Phase 3 result

- Re-read the emitter and owning lowerer boundaries after the export removal;
  no additional production refactor was necessary.
- Confirmed canonical `emit_unit()` has no direct lowerer reference and the
  lowerer remains available only from its owning module.
- Same-context review found no blocking finding.
- Verification: the bounded Phase 2 suite remained **47 passed** with the
  known independent LISS-0447 failure; `py_compile` and `git diff --check`
  passed.

Process review: no operating-contract deviation or operational problem found.

Issue complete. The next safe action is a new QASM/consumer migration Phase 1
Red contract.
