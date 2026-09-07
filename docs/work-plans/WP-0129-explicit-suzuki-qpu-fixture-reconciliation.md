# WP-0129: Explicit Suzuki finite-QPU fixture reconciliation

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor and final review complete** |
| Size | M (initial/current) |
| Issue | [LISS-0512](../issues/LISS-0512-explicit-suzuki-qpu-fixture-reconciliation.md) |
| Specification | [Explicit evolution surface](../specs/staqex-explicit-evolution-surface.md) |
| Parent context | [WP-0107](WP-0107-scientific-semantic-core.md) / [LISS-0444](../issues/LISS-0444-scientific-semantic-core.md) |

## Goal

Make the finite Suzuki projection acceptance test represent the current
source-visible evolution and finite-realization contract. Separate fixture
drift from any remaining canonical QPU implementation gap.

## Work units

| Unit | Scope | Exit evidence |
|---|---|---|
| U1 | Replace the legacy implicit Suzuki fixture with explicit `exp` + `Realize` + `Evolve()` source | fixture matches accepted spec |
| U2 | Preserve canonical instruction/provenance/fingerprint assertions | focused tests fail only at the intended missing projection boundary |
| U3 | Run neighboring explicit-step and rejection suites | no regression and no over-broad semantic rejection |
| U4 | Record Red result and review packet | Phase 2 decision point is explicit |

## Phase 1 allowed paths

- `tests/test_liss_0444_finite_instruction_projection_red.py`
- this WorkPlan and [LISS-0512](../issues/LISS-0512-explicit-suzuki-qpu-fixture-reconciliation.md)
- the 2026-09-07 Phase 0 trace

Production code, provider integration, live execution, and unrelated failing
families are excluded.

## Phase 2 allowed paths

- `compiler/staqex/scientific_semantic_ir.py`
- `compiler/staqex/backend/qasm/emitter.py`
- `tests/test_liss_0444_finite_instruction_projection_red.py`
- `tests/test_higher_order_suzuki_green.py`
- this WorkPlan, LISS-0512, and the representative trace

## Approval gate

Phase 1 Red approval was received from the user on 2026-09-07. Phase 2 Green
requires a new typed approval after the Red tests are reviewed. Phase 3 and
consumer-wide migration remain outside this WorkPlan.

## Phase 1 Red result

- User approval: `Feature Path / Phase 1 Red / explicit Suzuki・finite QPU fixture reconciliation 承認`, 2026-09-07.
- The fixture now uses explicit `exp` + `Realize` + `Evolve()` source.
- Focused suites: **19 passed, 3 failed**; `git diff --check` passed.
- Red evidence identifies a canonical finite-gate projection gap, a no-partial
  artifact gap for invalid explicit policy, and the corresponding QASM
  canonical-projection gap.
- Explicit step-count and neighboring QPU rejection/provenance suites remain
  green. No production implementation was performed.

## Phase 2 Green result

- User approval: `Feature Path / Phase 2 Green / LISS-0512 canonical explicit-Realize finite QPU projection 承認`, 2026-09-07.
- Added canonical explicit-Realize finite Suzuki operations to the Scientific
  Semantic IR projection; QASM consumes those operations without AST fallback.
- QASM now reports typed canonical projection errors before generic
  no-executable-projection diagnostics.
- Invalid/unresolved policy now removes all executable and terminal
  instructions before QPU emission.
- Focused verification: **64 passed**; spec verification **161/161**; diff
  check passed.
- Full regression remains **1932 passed, 16 failed** in unrelated open
  semantic-family/consumer-migration tests.

Phase 3 Refactor approval was received through the user's subsequent
`承認` response after the Phase 2 result.

## Phase 3 Refactor result

- Extracted the shared canonical Suzuki operation/provenance helper used by
  explicit and compatibility finite projections; behavior is unchanged.
- Same-context review packet: [LISS-0512 Phase 3 review](../collaboration/reviews/2026-09-07-liss-0512-phase3-review.md).
- Verification: focused **64 passed**, Spec Verification **161/161**,
  compileall passed, and `git diff --check` passed.
- Final Adjudicator review approval: `LISS-0512 Phase 3 最終レビュー 承認`, 2026-09-07.
- Merged to `main` via PR #582 (`cfcde2a9`); all required CI checks passed.
- Process review: no operating-contract deviation or operational problem found.
- Current Next Issue: none within WP-0129; broader consumer migration and
  provider/live-QPU work remain separately scoped.
