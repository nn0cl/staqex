# WP-0130: Move the current S02 boundary sample into Basics

| Field | Value |
|---|---|
| Status | **Phase 2 Green — refactor review pending** |
| Size | M |
| Issue | [LISS-0513](../issues/LISS-0513-basic-s02-example-migration.md) |
| Parent context | [WP-0093](WP-0093-s02-language-expressiveness-and-selection.md) |
| Branch | `feature/basic-s02-migration-red` |
| Planning record | `AIP-0130-0513-001` |

## Goal

Reclassify the current S02 selection program as a Basic language-boundary
example, preserving its accepted semantic behavior while removing misleading
drug-discovery framing.

## Work units

| Unit | Scope | Exit evidence |
|---|---|---|
| U1 | Add migration acceptance tests | Red tests fail for the absent Basic artifact |
| U2 | Move and simplify the example | Basic source and README are canonical |
| U3 | Reconcile current references | tests/catalog/docs use the new path; historical evidence is preserved |
| U4 | Verify behavior | compile, local run, focused regressions, spec verification |

## Phase boundary

Phase 1 changes tests and planning evidence only. Phase 2 may move files and
update current references after Red review and implementation approval. The
new realistic S02, real molecular data, molecular Hamiltonians, VQE, provider
SDKs, and live QPU execution are excluded.

## Phase 1 Red result

- User approval: `Feature Path / Phase 1 Red / 現行S02のBasic移管 承認`, 2026-09-07.
- New acceptance suite: `tests/test_liss_0513_basic_s02_example_migration_red.py`.
- Result: **3 failed, 0 passed**; expected Red state because the Basic
  artifacts have not yet been created.
- `git diff --check` passed.
- Phase 2 implementation remains separately gated.

## AI planning record

- Status: accepted for Phase 1 Red
- Author/environment: Codex host agent; displayed model/reasoning telemetry unavailable
- Created: 2026-09-07
- Planning size: M
- Route: Feature Path, Phase 1 Red → Phase 2 migration → Phase 3 review
- Estimate: N/A; repository does not expose a reliable token estimate
- Basis: multiple example, test, and current-document references; no runtime behavior change intended
- Confidence: medium; historical/current document classification must be checked during Phase 2
