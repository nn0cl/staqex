# LISS-0439 example equation fidelity review

## Scope

- WorkPlan: WP-0101.
- Scope: approved example equation/source fidelity and compile readiness slice.
- Excluded: S02 numerical migration, live QPU submit, provider SDK, compiler
  redesign, and unrelated cleanup.
- Review context: fresh read-only independent context.
- Reviewer: Tesla (`01a00b96-1110-7ba1-ac52-290be08327ea`).
- Reviewer authority: no implementation or approval authority.

## Findings and disposition

### Iteration 1 — NOT READY

- P1: S01 day2 retained `Suzuki S4` wording in its Arc comment and README while
  executing an exact `exp(-i * H * dur / hbar)` propagator. Accepted and fixed
  by aligning both descriptions with the exact propagator.
- P1: the worktree contained pre-existing S02 changes while WP-0101 wording
  was too broad about unchanged S02. Accepted as a scope/evidence correction;
  WP-0101 now says this batch introduces no S02 changes and preserves existing
  user changes.
- P2: A02 retained an `identity step` comment despite coin-plus-conditional-
  shift semantics. Accepted and fixed.

### Iteration 2 — READY

- S01 day2 README, comments, and executable expression agree.
- A02 main and imported step function expose coin plus conditional shift.
- B08, A04, A05, B12, S01 route, S01 fuel, and A11 main pass the targeted
  hard-check review.
- No implicit `Limit` to `exp` conversion or hidden finiteization was added.
- S02 dirty changes are pre-existing and excluded from this batch.
- P0/P1: none.
- P2: S01 fuel can reach `EVOLVE_UNTIL_MAX_STEPS_ERROR` at seed 0 because the
  convergence predicate is not met within 64 steps. This is non-blocking for
  the accepted compile-readiness scope.

## Verification

- Runnable main entrypoints: `31/31` passed `staqex check`.
- Spec verification: `161/161`, 100%, passed.
- Focused evolution/Realize regression passed.
- `git diff --check` passed.

## Reusable perspectives

- Source-to-domain fidelity: executable source, comments, README, and Host
  source strings must describe the same equation boundary.
- Type/dimension/validity closure.
- State/physics safety.
- Realization/fail-closed boundary.
- Migration/regression safety.
- Scope and approval discipline.

## Terminal state

- `COMPLETE` for the approved WP-0101 scope.
- Reviewer verdict: `READY`.
- No user decision required for the non-blocking runtime observation.
