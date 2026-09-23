# LISS-0576: Retire shadowed evaluator method bodies

## Metadata

- Local issue ID: LISS-0576
- GitHub issue: none
- Status: ready — Phase 3 review complete; final review approval pending
- Phase: phase-3-refactor
- Type: Architecture Path structural cleanup
- Priority: normal
- Initial planning size: M
- Current planning size: M
- Reclassification reason: not applicable
- Owner/agent: Codex host agent
- Related branch: `test/liss-0576-phase1-red`

## Summary

Remove only the obsolete method bodies in `runtime/evaluator.py` that are
unconditionally replaced during module initialization by the already-active
successor functions in `runtime/evaluation/compatibility.py`. This is a
source-structure cleanup, not a behavior change or a new extraction.

The accepted candidates are:

- `_bind_finiteize`
- `_bind_finiteize_continuous`
- `_bind_field_from_host`
- `_bind_continuous_compose`
- `_execute_assignment` (the two-line recursive stub)

AST spans cover 176 lines across these five definitions; the Git diff removes
181 lines including blank separators. The
active implementations remain in `evaluation/continuous.py` and
`evaluation/assignments.py`. No successor implementation or installer is to
be modified in this issue.

## Acceptance Notes

- After import, each Evaluator hook remains bound to the same compatibility
  successor function as before.
- Existing language behavior, diagnostics, mutation ordering, runtime DTO
  identity, and public import paths remain unchanged.
- The five superseded class definitions are absent from `Evaluator`'s source
  AST after the cleanup; no duplicate implementation is moved elsewhere.
- Static/private consumer inventory and runtime identity checks cover
  compatibility aliases; existing continuous-field, finiteize, assignment,
  constructor, frame, execution, and operator characterizations remain
  applicable.
- Only removal of the five listed definitions and the issue-owned test,
  lifecycle, trace, and design records is in scope.
- No parser/typechecker, provider/QPU, QASM, language, API-retirement, or
  unrelated evaluator-family change is included.

## Dependencies

- Parent: WP-0169 / evaluator residual-body cleanup
- Depends on: none; WP-0167/WP-0168 predecessor work is merged on `main`
- Blocks: none
- Related: WP-0167, WP-0168, LISS-0568, LISS-0572

## Adjudicator Decision Points

- Phase 0 acceptance: approved 2026-09-24. Accepted the five-definition,
  behavior-preserving cleanup boundary only.
- Phase 1 Red: approved 2026-09-24. Tests and the issue-owned active-Red
  entry were added; no production implementation was changed.
- Phase 1 Red test review: approved 2026-09-24. The five structural Red
  assertions and two passing compatibility identity assertions were accepted;
  no test changes were requested.
- Phase 2 Green / Implementation: approved 2026-09-24; removed only the five
  accepted definitions. Reviewed tests and compatibility installers were not
  changed.
- Phase 3 Refactor: approved 2026-09-24. Review found no source refactor
  beyond the accepted deletion necessary; the implementation is already
  minimal and behavior-neutral.
- Next approval: `LISS-0576 Phase 3 最終レビュー 承認`.

## Context

- Included: `evaluator.py`, `evaluation/compatibility.py`,
  `evaluation/continuous.py`, `evaluation/assignments.py`, the corresponding
  `EvaluatorContext` hooks, directly calling runtime families, and
  characterization tests found by static search.
- Omitted: unrelated language semantics, parser/typechecker implementation,
  external providers, network/credentials, and broad evaluator redesign.
- Assumptions: module initialization completes before consumers obtain the
  public Evaluator class; the compatibility installers remain the canonical
  hook binding mechanism for these methods.

## AI Planning Records

### AIP-0576-001

- Status: proposed
- Created by:
  - Agent/environment: Codex host agent / local macOS worktree
  - Model as displayed: N/A — host UI did not expose a model identifier in
    the task context
  - Reasoning setting as displayed: N/A — not exposed in the task context
- Created at: 2026-09-24
- Planning size: M
- Intended execution route: host agent; deterministic AST, pytest, compile,
  and repository lifecycle tools
- Intended scope: Phase 1 structural/identity Red contract, reviewed test
  approval, then separately approved minimal deletion and regression
  verification
- Estimated token range: 8,000–14,000 input+output tokens
- Estimated token midpoint: 11,000 input+output tokens
- Token metric: estimated model input+output tokens for this bounded issue
- Estimation basis: one small structural test suite, five method removals,
  compatibility/import characterization, focused and adjacent suites, and
  required review/status evidence
- Assumptions: no behavioral discrepancy is discovered; existing test helpers
  cover the relevant language paths
- Confidence: medium
- Revises: none
- Revision reason: none
- Superseded by: none

## References

- [Core module decomposition](../specs/staqex-core-module-decomposition.md)
- [Evaluator evolution-family work plan](../work-plans/WP-0168-evaluator-evolution-family-decomposition.md)
- [Phase 3 review summary](../collaboration/reviews/2026-09-24-liss-0576-phase3-review.md)
- [AI work trace](../collaboration/traces/2026-09-24-liss-0576-phase0.md)

## Work Notes

- Phase 0 acceptance record and exact source-boundary evidence are in the
  linked AI work trace and current remeasurement section of the canonical
  decomposition specification.

## Verification

- Phase 0: AST ownership/reassignment inventory, static consumer search, and
  module/working-tree inspection; no tests or source edits were run.
- Phase 1 Red at base commit `c1f35da2` with a dirty test-only tree, macOS,
  Python 3.14.6, pytest 9.1.1:
  - `.venv/bin/python -m pytest -q tests/test_liss_0576_shadowed_bodies_red.py`
    could not launch because this isolated worktree has no `.venv`.
  - Re-run using
    `PYTHONPATH=compiler:. /Users/nn0cl/Documents/git/qpex/.venv/bin/python
    -m pytest -q tests/test_liss_0576_shadowed_bodies_red.py`: **5 expected
    failures, 0 passed**, one for each accepted shadowed definition.
  - Same interpreter and environment for
    `tests/test_liss_0576_compatibility_identity.py`: **2 passed**.
  - No unexpected failures, errors, skips, or exclusions in either focused
    run. The baseline Red is the expected presence of the five definitions;
    compatibility identity already passes.
- Phase 2 focused and adjacent regressions: **42 passed** across LISS-0576
  Red/identity and five declared neighbor suites; Python 3.14.6 / pytest 9.1.1.
  Cache was disabled because the isolated worktree cannot write to the shared
  pytest cache path.
- Spec verification: **161/161 passed** from `/private/tmp`; SV-17 writes a
  relative output path `sink`, so running from the isolated worktree was
  denied by sandbox filesystem policy. The initial cwd run had one
  environment-only suite crash, then passed with a writable temporary cwd.
- Root blocking pytest at clean commit
  `3c0706f46120eb0bac242c60eb263a38e8df4761`: **2,249 passed**, 0 failures;
  Python 3.14.6 / pytest 9.1.1. Spec verification at the same SHA: **161/161
  passed**. Lifecycle, document, coverage, diff, focused/adjacent, and compile
  checks passed. The spec runner used `/private/tmp` as cwd because SV-17
  writes the relative `sink` output; no test was excluded.
- Commit-specific rerun at `d0c9e690d9a4b685a1f94dc8c400255601ff3be9`, clean
  tree, macOS / Python 3.14.6 / pytest 9.1.1: structural suite again reported
  the same **5 expected failures**; compatibility identity suite reported
  **2 passed**. No other failures, errors, skips, or exclusions.

## Process Review

- Outcome: not yet
- Lesson written: not applicable
- Template-feedback path: none
