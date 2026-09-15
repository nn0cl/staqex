# LISS-0454 / WP-0117 Design Intake

[DESIGN CHECK]
- Scope and expected behavior: prepare a reviewed acceptance boundary for
  hardening the already-shipped ADR-0157 polynomial fusion.
- Specifications and files inspected: ADR-0157 from the historical source
  record, PR #216, current evaluator/tests, DEC-0004/0005, open-work register,
  LISS-0454, WP-0117, and proposed ADR-0215.
- Component boundaries, ports/adapters, and VO/DTO candidates when applicable:
  evaluator optimization only; no new port, adapter, DTO, or QPU boundary.
- Applicable constraints: blackboard-first source fidelity, Never Leave the
  State, ideal meaning versus finite realization, type-first dimensions, and
  fail-closed fallback.
- Decisions, assumptions, and unresolved ambiguities: current supported scalar
  carrier inventory must be extracted before Phase 1; no new carrier is
  authorized. The proposed coefficient policy intentionally requires
  Architecture approval because it tightens numerical semantics.
- Included and omitted AI context: only the current optimizer, tests, and
  authoritative architecture records are included; historical mixed branches
  are omitted from implementation context.
- Task routing (model/assistant/tool): deterministic repository inspection and
  primary-agent design authoring; no AI provider or external dependency.
- Input/output evidence contract when AI output is involved: none; all design
  claims are path/commit grounded.
- Independent review lenses selected and why: contract completeness,
  architecture/boundary integrity, source-to-domain fidelity, type/dimension
  closure, state/physics safety, realization/fail-closed behavior,
  migration/regression safety, phase/approval discipline, evidence hygiene,
  and canonical authority/implementation reality.
- Verification plan: `git diff --check`; review ADR-0215 before Phase 1;
  implementation and test creation remain unapproved.

## Approval boundary

This packet requests Architecture review of ADR-0215 and subsequent Phase 1
approval. It does not authorize implementation, branch merge, or deletion of
the historical WP-0063 branch.

## Phase 0 acceptance — 2026-09-16

- `LISS-0454 Phase 0 acceptance` was received and recorded.
- The bounded evaluator-only scope is ready for Architecture review. Type and
  dimension authority, sequential equivalence, finite coefficient retention,
  fail-closed fallback, and diagnostic-only evidence are explicit.
- No Phase 1 test change or implementation is authorized.

## Next Safe Action

Request `ADR 0215 Architecture 承認`.

## Architecture approval — 2026-09-16

- `ADR 0215 Architecture 承認` was received and recorded.
- ADR-0215 now governs type/dimension authority, coefficient preservation,
  fail-closed fallback, sequential equivalence, and diagnostic-only fusion
  evidence.
- Phase 1 Red remains separately gated; no tests or implementation were
  changed in this decision update.

## Next Safe Action

Request `LISS-0454 Phase 1 Red 承認`.

## Phase 1 Red — 2026-09-16

- Phase 1 approval was received and two focused tests were added only.
- The tests expose coefficient trimming and non-finite coefficient acceptance
  in the current polynomial composition helper.
- Direct result: **2 failed**. Production code and existing tests were not
  changed.

## Next Safe Action

Request `LISS-0454 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review — 2026-09-16

- The two numeric-closure Red nodes were accepted unchanged.
- Their failures directly expose near-zero coefficient trimming and
  non-finite coefficient acceptance; no broader language or QPU scope is
  implied.
- No implementation permission was inferred.

## Next Safe Action

Request `LISS-0454 Phase 3 Refactor 承認`.

## Phase 3 Refactor — 2026-09-16

- Phase 3 approval was received. The refactor extracted exact-zero tail
  trimming into a shared helper used by composition and addition, while
  preserving explicit finite-value checks and fail-closed propagation.
- The focused suite passed: **7 passed**. Compile, diff, lifecycle, and
  document checks also passed. Assertions and behavior were unchanged.
- Reviewer empathy summary: the numerical policy and fallback boundaries are
  now easier to locate and review without changing the evaluator boundary.

## Next Safe Action

Request `LISS-0454 Phase 3 最終レビュー 承認`.

## Phase 3 final review — 2026-09-16

- Final review approval was received. The reviewed scope has no blockers.
- Focused and regression tests passed (**7 passed**); compile, diff, Active-Red,
  and document lifecycle checks passed.
- Review Summary is recorded at
  `docs/collaboration/reviews/2026-09-16-liss-0454-phase3-final-review.md`.
- Completion process review found no deviation; LISS-0454 and WP-0117 are
  synchronized as done.

## Phase 2 Green / Implementation — 2026-09-16

- Phase 2 implementation approval was received and the focused contract suite
  now passes: **7 passed** including the two LISS-0454 tests and the existing
  polynomial-fusion regression tests.
- `_compose_poly` now preserves finite nonzero coefficients, rejects
  non-finite inputs and intermediate results, and returns `None` for a
  non-finite projection. Additive and multiplicative helpers propagate the
  same fail-closed result, and the fusion pipeline handles it without a
  partial fused output.
- Near-zero coefficients are no longer classified as affine evidence merely
  because they are below a tolerance; diagnostic fields remain evidence only.
- Active-Red entries were removed after the exact nodes passed. Production
  implementation remained limited to the evaluator polynomial-fusion path.

## Next Safe Action

Request `LISS-0454 Phase 3 Refactor 承認`.
