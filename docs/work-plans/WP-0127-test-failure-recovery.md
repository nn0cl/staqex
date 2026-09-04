# Work Plan: Current pytest failure recovery

## Goal

Restore the current test suite to the accepted language/runtime contracts without weakening the Scientific Semantic IR or blackboard/QPU boundaries.

## Scope

- In: the 13 failures observed in the full pytest run, grouped by shared runtime/spec behavior; regression tests; deterministic verification.
- Out: real AWS/Braket execution, Rust migration, unrelated historical tests that are not reproduced by the current suite.

## Issue Graph

| Issue | Status | Initial size | Current size | Planning record | Depends on | Blocks | Branch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LISS-0504 | review | M | M | AIP-0127-0504-001 | - | - | codex/wp-0127-test-failure-recovery |
| LISS-0505 | ready | M | M | AIP-0127-0505-001 | - | - | codex/wp-0127-test-failure-recovery |
| LISS-0506 | ready | M | M | AIP-0127-0506-001 | - | - | codex/wp-0127-test-failure-recovery |
| LISS-0507 | ready | M | M | AIP-0127-0507-001 | - | - | codex/wp-0127-test-failure-recovery |
| LISS-0508 | ready | M | M | AIP-0127-0508-001 | - | - | codex/wp-0127-test-failure-recovery |
| LISS-0509 | ready | M | M | AIP-0127-0509-001 | - | - | codex/wp-0127-test-failure-recovery |

## AI Planning Records

### AIP-0127-0504-001 through AIP-0127-0509-001

- Status: accepted
- Created by: host agent; model/reasoning telemetry unavailable in repository
- Created at: 2026-09-04
- Planning size: M each
- Intended execution route: Feature Path, Phase 1 regression confirmation → Phase 2 minimal fix → Phase 3 refactor/verification
- Intended scope: one cohesive failure family per local issue, no provider or Kernel-boundary expansion
- Estimated token range: N/A
- Token metric: N/A
- Estimation basis: multiple files and runtime/spec contract checks
- Assumptions: current accepted specifications and existing failing tests are authoritative
- Confidence: medium; failures may expose shared canonical-runtime regressions

## Recommended Order

1. LISS-0504 — continuous discretization provenance
2. LISS-0505 — inspect/deferred pushforward
3. LISS-0506 — Jordan-Wigner mapping provenance
4. LISS-0507 — linked operator factory runtime
5. LISS-0508 — free-function and struct argument binding
6. LISS-0509 — mixed measurement dispatch

## Current Next Issue

- Issue: LISS-0505
- Reason it is unblocked: existing Red tests reproduce the failure and no external dependency is required.
- Adjudicator approval needed: implementation is explicitly authorized by the current request; no real-provider approval is needed.

## Risks

- A shared canonical-runtime change may affect already-green spec verification.
- Some tests may encode superseded expectations and require an accepted-spec comparison before changing either tests or implementation.

## Verification Plan

- Targeted Red/Green tests for each issue.
- `python3 tests/spec_verification/run_all.py` after each cohesive family and at completion.
- Full `pytest -q` to completion.
- `git diff --check` and branch/status inspection.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
