# WP-0161: Active-Red contract remediation

| Field | Value |
|---|---|
| Status | done — LISS-0551–0559 completed |
| Phase | done |
| Parent trigger | LISS-0543 completion blocker |
| Canonical specification | [Active-Red remediation](../specs/staqex-active-red-remediation.md) |
| Architecture approval | Adjudicator approved 2026-09-12 |
| Implementation permission | none |

## Goal

Give all 19 active-Red nodes truthful feature-level ownership, distinguish
fixture drift and superseded contracts from product regressions, and remove
each exclusion through independently approved work.

## Scope

- In: exact nodes currently in `docs/testing/active-red-tests.toml`, their
  accepted contracts, directly implicated compiler/runtime/host modules, and
  lifecycle ownership.
- Out: LISS-0544–0550 module decomposition, new language features, provider or
  deployment work, and historical-document revival.

## Issue Graph

| Issue | Status | Initial/current size | Planning record | Depends on | Blocks | Branch |
|---|---|---:|---|---|---|---|
| LISS-0551 fixture conformance | done — final review approved 2026-09-13 | M / M | AIP-0551-001 | - | 0552 | `codex/liss-0551-fixture-conformance` |
| LISS-0552 projection diagnostic isolation | done — final review approved 2026-09-14 | L / L | AIP-0552-001 | 0551 | - | `codex/liss-0552-projection-diagnostics` |
| LISS-0553 symbolic compatibility supersession | done — final review approved 2026-09-14 | M / M | AIP-0553-001 | - | - | `codex/liss-0553-symbolic-contract` |
| LISS-0554 QASM canonical fail-closed | done — final review approved 2026-09-14 | M / M | AIP-0554-001 | - | - | `codex/liss-0554-qasm-canonical-input` |
| LISS-0555 interfer node contract | done — final review approved 2026-09-14 | M / M | AIP-0555-001 | - | - | `codex/liss-0555-interfer-contract` |
| LISS-0556 POVM rejection projection | done — final review approved 2026-09-14 | M / M | AIP-0556-001 | - | - | `codex/liss-0556-povm-rejection` |
| LISS-0557 evaluator authority evidence | done — final review approved 2026-09-16 | M / M | AIP-0557-001 | - | - | `codex/liss-0557-evaluator-authority` |
| LISS-0558 observation diagnostic name | done — final review approved 2026-09-16 | S / S | - | - | - | `codex/liss-0558-observation-diagnostic` |
| LISS-0559 S02 assay DTO | done — final review approved 2026-09-16 | M / M | AIP-0559-001 | - | - | `codex/liss-0559-s02-assay-dto` |

## AI Planning Record — AIP-WP-0161-001

- Status/created: proposed, 2026-09-11
- Agent/environment: Codex host agent; displayed model/reasoning unavailable
- Planning size/route: XL; host implementation, configured same-context review,
  separate feature-unit branch per Issue
- Intended scope: classification and remediation of exactly 19 nodes
- Estimate: N/A; repository exposes no compatible token-planning metric
- Basis: 19 direct failures across test fixtures, pipeline, Semantic IR, QASM,
  evaluator, and scientific-data DTOs; high contract-conflict uncertainty
- Assumptions/confidence: later accepted specs outrank completed Issue prose;
  medium confidence until each Phase 0 review resolves its named conflict
- Revises/Superseded by: none

## Recommended Order

1. Architecture approval and manifest ownership handoff; then close LISS-0543.
2. LISS-0551 fixture conformance.
3. LISS-0552 only for residual projection diagnostics revealed by 0551.
4. LISS-0553 and LISS-0555 contract supersession reviews before changing their
   old assertions.
5. LISS-0554, 0556, and 0559 product regressions.
6. LISS-0557 evaluator ownership decision and LISS-0558 diagnostic sync.

## Current Next Issue

- Issue: none within WP-0161.
- Reason: LISS-0551–LISS-0559 are complete and all Active-Red exclusions owned
  by this work plan have been removed.
- Approval needed next: none; a new task requires a separate scope/design
  intake.

## Risks

- Treating a later compatibility contract as a regression against an older
  retirement assertion.
- Updating a fixture and accidentally weakening its semantic assertion.
- Restoring mutable evaluator state instead of preserving result evidence.
- Fixing a QASM fallback by rebuilding canonical meaning from AST.
- Returning mutable assay mappings while claiming immutable typed records.

## Verification Plan

The canonical spec's per-node direct run, nearest-neighbor suite, full blocking
suite, Spec Verification, lifecycle checks, and documentation checks apply to
every issue. Test changes require explicit replacement evidence in review.

## Process Review

- Outcome: WP-0161 completed after LISS-0559 final review; no operating-contract
  deviation or operational problem found.
- Lesson written: existing status-drift, authority-boundary, and
  acceptance-boundary lessons applied
- Template-feedback path: none
