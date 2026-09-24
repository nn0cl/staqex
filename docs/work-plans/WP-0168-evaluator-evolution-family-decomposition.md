# WP-0168: Evaluator evolution-family decomposition

| Field | Value |
|---|---|
| Status | done — LISS-0575 merged and verified |
| Size | L |
| Parent | WP-0167 / evaluator successor decomposition |
| Scope approval | Unit A scope accepted 2026-09-22 |
| Implementation permission | approved 2026-09-23; Phase 2 executed |
| Candidate issue | LISS-0575 |
| Current Next Issue | none — this work plan is complete |

## [DESIGN CHECK]

Decompose the active `runtime/evaluation/evolution.py` family while retaining
Evaluator as the mutable state owner and preserving all explicit-evolution,
unitary, Hamiltonian, grid, convergence, and private-hook behavior.

### Phase plan

1. Phase 0: measure actual families, imports, private consumers, callbacks,
   and exact allowed paths.
2. Phase 1 Red: add structural contracts and evolution characterizations.
3. Phase 2 Green: extract the smallest approved successors and install
   compatibility wiring.
4. Phase 3 Refactor: simplify boundaries, verify consumers, and complete
   same-context review.

### Candidate units

- A1 `unitary_ops.py`: unitary resolution, named gates, QFT, apply, CNOT,
  C-apply.
- A2 `evolution_ops.py`: explicit propagator and evolve/until orchestration.
- A3 `hamiltonian_evolution.py`: Hamiltonian, tuple-coordinate, grid, and
  provenance operations.

No candidate may copy Evaluator-owned maps or instantiate Evaluator. Phase 0
must decide whether these are three modules or a smaller evidence-backed split.

## Unit A Architecture Path scope approval

- Approval: `WP-0168 / Unit A evolution-family decomposition Architecture Path
  scope approval` (2026-09-22).
- Investigation/design only; implementation is unauthorized.
- Next approval: `WP-0168 / LISS-0575 Phase 0 acceptance 承認`.

## Unit A Phase 0 acceptance

- Approval: `WP-0168 / LISS-0575 Phase 0 acceptance 承認` (2026-09-22).
- Accepted the three-unit split: A1 unitary operations, A2 evolution
  orchestration, and A3 Hamiltonian/grid evolution.
- Accepted ownership and callback boundaries: Evaluator owns mutable runtime
  state and provenance; successors use `EvaluatorContext` and do not import
  or instantiate Evaluator.
- Accepted allowed paths and consumer inventory are recorded in LISS-0575.
- Next approval: `WP-0168 / LISS-0575 Phase 1 Red 承認`.

## Unit A Phase 1 Red

- Approval: `WP-0168 / LISS-0575 Phase 1 Red 承認` (2026-09-23).
- Added only the bounded LISS-0575 structural/characterization suite and
  active-Red ledger entry. Production implementation remains unauthorized.
- The initial contract was reviewed and corrected: facade ownership now checks
  source symbol locations, compatibility wiring checks AST imports from each
  successor, and the behavioral suite includes all three accepted families.

## LISS-0575 Phase 1 Red test review

- Approval: `WP-0168 / LISS-0575 Phase 1 Red テストレビュー承認`
  (2026-09-23).
- Review packet:
  `docs/collaboration/reviews/2026-09-23-liss-0575-phase1-red-review.md`.
- Result: accepted. Corrected run: **5 failed, 10 passed**. Structural
  failures cover three source ownership gaps, successor imports, and context
  callbacks; ten runtime characterizations pass.
- Lifecycle, document, coverage-ledger, and diff checks passed. No production
  implementation was added or authorized.
- Next approval: `WP-0168 / LISS-0575 Phase 2 Green / Implementation 承認`.

## LISS-0575 Phase 2 Green / Implementation

- Approval: `WP-0168 / LISS-0575 Phase 2 Green / Implementation 承認`
  (2026-09-23).
- Extracted the approved A1/A2/A3 families into separate successor modules,
  wired the legacy Evaluator hooks from those modules, and declared their live
  Evaluator state/callback contract in `EvaluatorContext`.
- Reviewed Red tests unchanged: **15 passed**. Consumer smoke passed, adjacent
  regression passed (**46 tests**), spec verification passed (**161/161**), and
  final CI-equivalent all-blocking suite passed (**2,242 tests**).
- `evolution.py`: 1,106 → 27 lines. Successors: unitary 329, evolution 318,
  Hamiltonian/grid 426; context 275 lines. Lifecycle, document, coverage,
  compile, and diff checks passed.
- Final run is provisional on the dirty implementation tree; retest after the
  final commit is required by verification policy.
- Next approval: `WP-0168 / LISS-0575 Phase 3 Refactor 承認`.

## LISS-0575 Phase 3 Refactor

- Approval: `WP-0168 / LISS-0575 Phase 3 Refactor 承認` (2026-09-23).
- Refactored the Hamiltonian path into duration, operator-resolution,
  single-Pauli, and non-qubit-basis helpers; dispatcher body is 137 lines
  (was 326). Consolidated bounded-evolution provenance construction.
- Reviewed same-context with no unresolved findings/blockers. The reviewed
  Phase 1 assertions remain unchanged. Phase 3 verification: focused and
  adjacent 63 passed, consumer smoke passed, spec 161/161, all blocking 2,242
  passed in 316.58s, plus lifecycle/coverage/compile/diff checks.
- Final verification remains provisional: branch is dirty at base SHA
  `e8e63ec25420660a28556eeab5ba3a605ef45812`; commit-specific blocking rerun
  is required.
- Final review approval received: `WP-0168 / LISS-0575 Phase 3 最終レビュー
  承認` (2026-09-23). No further phase approval is pending.
- Historical next action (superseded by final closeout below): commit and
  rerun blocking tests against the final SHA.

## Final closeout

- Final implementation commit: `fbe5e768301f514b99824c4211bb63883076d5b6`;
  merged to `main` by PR #596 as
  `66da78c824b5e5ce97fdf35b0ff9c79d7eec9df3`.
- Final blocking verification on the implementation SHA: **2,242 passed**;
  focused + adjacent: **63 passed**; consumer import/hook smoke passed; spec
  verification **161/161**. PR CI workflow run `35873796171` completed
  successfully.
- Process review: stale post-merge status was corrected in this reviewable
  documentation update. Existing Definition of Done covers this requirement;
  no template feedback or additional reusable lesson is proposed.
- WP-0168 is complete. Residual `evaluator.py` responsibilities require a
  separate successor scope and do not implicitly extend this plan.
