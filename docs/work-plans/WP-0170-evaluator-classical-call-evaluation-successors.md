# WP-0170: Evaluator classical call evaluation successors

| Field | Value |
|---|---|
| Status | in_progress — final review approved; commit/final-SHA verification pending |
| Size | L |
| Parent | Evaluator residual-body follow-up to WP-0169 |
| Canonical proposed specification | [Evaluator classical call evaluation](../specs/evaluator-classical-call-evaluation.md) |
| Candidate issue | [LISS-0577](../issues/LISS-0577-evaluator-classical-call-evaluation-successor.md) |
| Implementation permission | Phase 2 accepted; Phase 3 Refactor approved 2026-09-24 and complete |
| Current Next Issue | LISS-0577 commit and final-SHA blocking verification |

## [DESIGN CHECK]

- Scope and expected behavior: investigate and specify extraction of the
  remaining classical function/method call evaluator bodies while preserving
  runtime behavior and the single `Evaluator` state owner; Phase 1 adds only
  accepted structural and behavioral tests.
- Specifications and files inspected: Core module decomposition spec, merged
  WP-0169/LISS-0576 records, `evaluator.py`, `evaluation/classical.py`,
  `evaluation/execution.py`, `evaluation/context.py`, and relevant process,
  quality, verification, and branch policies.
- Component boundaries, ports/adapters, and VO/DTO candidates: propose a
  focused `evaluation/classical_calls.py`; `Evaluator` retains state and DTO
  ownership; the module-local context proposal is accepted.
- Applicable constraints: no language/provider/QPU change; no copied mutable
  state; no implementation before accepted specification, reviewed Red tests,
  and explicit implementation approval.
- Decisions, assumptions, and unresolved ambiguities: proposed family is four
  call-evaluation methods; Phase 0 accepted the module-local protocol boundary
  and compatibility-hook shape.
- Included and omitted AI context: as recorded in LISS-0577.
- Task routing: host agent and deterministic source/AST/import tools; review
  follows `runtime-routing.toml`.
- Input/output evidence contract: not applicable; this is runtime evaluator
  decomposition, not AI-generated application output.
- Verification plan: Phase 0 consumer/import/state inventory; later phases
  must run structural Red, behavior characterization, actual consumer import
  smoke, adjacent regression, and all-blocking tests with SHA/environment
  evidence.

## Issue graph

| Issue | Status | Size | Depends on | Branch |
|---|---|---:|---|---|
| LISS-0577 | in_progress — final review approved; commit verification pending | L | WP-0169/LISS-0576 complete | `codex/liss-0577-classical-call-evaluation` |

## Proposed sequence

1. Architecture approval: accepted 2026-09-24 for the four-method classical
   call boundary, state/DTO ownership, successor module, and compatibility
   entrypoints.
2. Phase 0 acceptance: accepted 2026-09-24. The consumer/test inventory,
   local context protocol proposal, and exact allowed paths are accepted.
3. Phase 1 Red: approved and test-reviewed/accepted 2026-09-24. Focused pytest
   reported 3 expected structural failures and 3 passing characterizations.
4. Phase 2 Green: approved and implemented 2026-09-24. Focused LISS-0577: 6
   passed; consumers: 32 passed; adjacent: 16 passed; all-blocking: 2,255
   passed in 331.53s. Tested on dirty tree at base SHA `9b2e2e0f`; commit-specific
   rerun remains required.
   `classical_calls.py` was 329 lines; Phase 2 Green was accepted 2026-09-24.
5. Phase 3 Refactor: approved and completed 2026-09-24. Consolidated repeated
   method lookup and return-expression selection; the accepted module boundary
   and assertions remain unchanged. It is 324 lines; the advisory 300-line
   disposition is due before issue closure. Focused/consumer/adjacent tests:
   54 passed; all-blocking: 2,255 passed, 0 failed. See [Review
   Summary](../collaboration/reviews/2026-09-24-liss-0577-phase3-refactor-review.md).
6. Final Adjudicator review: approved 2026-09-24, including the bounded
   324-line structure disposition; no further module split requested.
7. Commit and final-SHA blocking verification: pending before the Issue/WP
   can be marked done.

No later phase is authorized by this proposal. Classical operator expressions,
operator projection, runtime-plan orchestration, state-preserving `when`, and
other evaluator families remain separate candidates.
