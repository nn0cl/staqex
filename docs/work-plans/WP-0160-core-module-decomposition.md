# WP-0160: Core module decomposition

| Field | Value |
|---|---|
| Status | in progress — LISS-0543 done; LISS-0544 is unblocked |
| Architecture approval | Adjudicator approved 2026-09-11 |
| Implementation permission | LISS-0543 Phase 3 granted 2026-09-11 |

## Goal

Split the oversized Staqex Python modules into cohesive, dependency-directed
units while preserving all externally observable behavior and public imports.

## Scope

- In: regression baseline, evaluator, typechecker, parser, Scientific Semantic
  IR, QASM lowering, and remaining production modules above about 1,000 lines.
- Out: language behavior changes, provider/live-QPU work, Rust migration,
  public API retirement, and opportunistic bug fixes mixed into refactors.

## Issue Graph

| Issue | Status | Initial size | Current size | Planning record | Depends on | Blocks | Branch |
|---|---|---:|---:|---|---|---|---|
| LISS-0543 | done | L | L | AIP-0543-001 | - | 0544–0550 | `codex/liss-0543-red` |
| LISS-0544 | proposed | L | L | AIP-0544-001 | 0543 | 0545 | `refactor/evaluator-orchestration` |
| LISS-0545 | proposed | XL | XL | AIP-0545-001 | 0544 | 0550 | `refactor/evaluator-domain-families` |
| LISS-0546 | proposed | XL | XL | AIP-0546-001 | 0543 | 0550 | `refactor/typechecker-families` |
| LISS-0547 | proposed | XL | XL | AIP-0547-001 | 0543 | 0550 | `refactor/parser-families` |
| LISS-0548 | proposed | L | L | AIP-0548-001 | 0543 | 0549, 0550 | `refactor/scientific-semantic-ir` |
| LISS-0549 | proposed | L | L | AIP-0549-001 | 0543, 0548 | 0550 | `refactor/qasm-lowering` |
| LISS-0550 | proposed | XL | XL | AIP-0550-001 | 0544–0549 | - | `refactor/core-module-budget` |

## AI Planning Record

### AIP-WP-0160-001

- Status: proposed
- Created by: Codex host agent; displayed model/reasoning identifier unavailable
- Created at: 2026-09-11
- Planning size: XL
- Intended execution route: host implementation, same-context review, one
  feature-unit branch and approval sequence per issue
- Intended scope: LISS-0543 through LISS-0550 only
- Estimated token range/midpoint/metric: N/A; repository does not expose a
  compatible planning metric and this is not an elapsed-time estimate
- Estimation basis: ten production modules above 1,000 lines, 2,050 collected
  tests, 19 current failures, and high public import fan-out
- Assumptions: no public behavior change and no new dependency
- Confidence: medium; evaluator and parser state coupling can require further
  bounded subdivision
- Revises/Superseded by: none

## Recommended Order

1. LISS-0543 — establish a truthful green blocking baseline and symbol/output
   manifests.
2. LISS-0544 — extract evaluator runtime-plan orchestration, measurement, and
   dynamic-lane execution.
3. LISS-0545 — extract evaluator evolution, operator resolution, classical
   calls, and value operations in four separately reviewed units.
4. LISS-0546 and LISS-0547 — typechecker and parser may proceed independently
   after 0543, but never in the same branch.
5. LISS-0548 — split Scientific Semantic IR before QASM consumers.
6. LISS-0549 — split QASM preflight, AST compatibility, and lowering.
7. LISS-0550 — split remaining 1,000-line DTO/IR/orchestration modules and add
   enforceable structural guardrails.

## Current Next Issue

- Issue: LISS-0544
- Reason it is unblocked: LISS-0543 is done and the 19 active-Red nodes now
  have independently accepted WP-0161 ownership.
- Adjudicator approval needed: `LISS-0544 Phase 0 acceptance 承認` when core
  decomposition resumes; WP-0161 remediation is currently prioritized.

## Risks

- Python circular imports caused by moving DTOs and helpers.
- Bound methods accidentally sharing copied rather than authoritative state.
- Diagnostic ordering/source spans changing through dispatch refactors.
- Fixed-seed randomness changing because call order changes.
- QASM text changing because dictionary or traversal order changes.
- Opportunistic behavior fixes obscuring whether extraction is semantics-free.

## Verification Plan

Use `docs/specs/staqex-core-module-decomposition.md`. Record pre/post public
symbols, focused tests, full blocking suite, spec verification, deterministic
runtime snapshots, QASM goldens, import graph, line/function inventory, and
diff checks per issue.

## Process Review

- Outcome: not yet
- Lesson written: not applicable yet
- Template-feedback path: none
