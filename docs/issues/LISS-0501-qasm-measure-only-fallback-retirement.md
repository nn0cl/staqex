# LISS-0501: QASM fallback retirement proof

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0500](LISS-0500-symbolic-legacy-builder-retirement.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0501-qasm-measure-only-fallback-retirement) |
| Scope approval | User approved continuation on 2026-09-02 |
| Architecture approval | Existing QASM fallback boundary in LISS-0444/WP-0107 |
| Phase 1 Red approval | User approved continuation on 2026-09-02 |
| Implementation permission | Phase 2 Green and Phase 3 refactor approved by user |
| Next approval | Next QASM/consumer migration Phase 1 Red |

## [DESIGN CHECK]

- **Scope and expected behavior:** remove the direct AST fallback branch from
  the canonical QASM entry; measure-only input already uses canonical Measure.
- **Specifications and files inspected:** WP-0107, LISS-0444, LISS-0500,
  migration Spec QASM fallback boundary, QASM emitter, canonical QPU IR, and
  fallback regression tests.
- **Component boundaries:** canonical QPU IR determines executable
  instructions; QASM emits them. The legacy lowerer remains an explicit
  compatibility symbol only.
- **Applicable constraints:** Phase 1 Red only; no provider/QPU/AWS, Rust,
  target allocation, or lowerer deletion.
- **Decisions and ambiguities:** measure-only canonical programs already emit
  canonical Measure without invented gates; ordinary finite gate and
  Suzuki/binder paths remain supported and separately tested.
- **Verification plan:** test the canonical entry source has no direct lowerer
  call, measure-only canonical output, ordinary projection behavior, and
  explicit legacy symbol isolation.

## Acceptance scenarios for Phase 1 Red

1. Given the canonical QASM entry, its implementation contains no direct AST
   lowerer branch.
2. Given a canonical measure-only program, then source-derived Measure QASM is
   emitted without an invented `H` gate.
3. Given an ordinary finite canonical gate program, then existing canonical
   QASM output remains supported.
4. Given an explicit compatibility caller, then the legacy lowerer symbol
   remains isolated and callable.

## Phase boundary

Phase 1 adds only the failing retirement proof. Phase 2 will remove the direct
fallback branch while preserving ordinary finite canonical projections.
Lowerer deletion for explicit compatibility callers and other unsupported
families remain separate work.

## Phase 1 Red result

- Added `tests/test_liss_0501_qasm_measure_only_fallback_retirement_red.py`.
- Red verification: **1 failed, 3 passed**, with no collection errors. The
  failure proves the canonical QASM entry still contains a direct AST fallback
  branch; the measure-only projection itself already passes.
- No production implementation was changed in this phase.

Human review of the Red contract is required before Phase 2 Green.

## Phase 2 Green result

- Removed the direct `lower_unit_to_circuit()` fallback branch from canonical
  `QASM3Emitter.emit_unit()`.
- Preserved the module-level lowerer symbol as an explicit compatibility
  re-export for separately controlled legacy callers; canonical emission does
  not invoke it.
- Measure-only input continues to emit canonical Measure QASM without an
  invented gate, and ordinary finite/Suzuki/binder projections remain intact.
- LISS-0501 plus finite projection, consumer migration, and QASM public-entry
  tests **36 passed**; `py_compile` and `git diff --check` passed.
- Lowerer deletion for explicit legacy callers and other unsupported-family
  migration remain separate work.

## Phase 3 result

- Extracted canonical executable-instruction detection into
  `_has_executable_canonical_instructions()`.
- Marked the lowerer import as an explicit compatibility export; the
  canonical `emit_unit()` path contains no direct lowerer call.
- Same-context review found no blocking finding.
- Verification: LISS-0501 plus finite projection, consumer migration, QASM
  public-entry, and static-QASM regressions **40 passed**; `py_compile` and
  `git diff --check` passed.

Process review: no operating-contract deviation or operational problem found.

Issue complete. The next safe action is a new QASM/consumer migration Phase 1
Red contract.
