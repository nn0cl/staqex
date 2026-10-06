# LISS-0584 dependency / commit-scope proposal

## Review Target

- Canonical: [0584 verification](2026-10-06-liss-0584-phase2-verification.md),
  [R01–R07](../../specs/opaque-foreach-wire-arithmetic-repair.md),
  [0583 test/guard review](2026-10-05-liss-0583-phase1-review.md).
- Current phase: Feature Path / Phase 2, focused Green, sanity gap unresolved.
- Human `はい。整理して` on2026-10-06 authorizes scope organization only.
- Requested approval/type: scope approval for this separation, explicit local
  A/B/C commit execution permission, and0583 guard-carrier review/disposition.
- Implementation permission: existing minimal0584 repair only. No new source/
  test changes. Post-review yes; batch N/A. No Phase 3/push/PR/merge authority.

## Dependency Evidence

Original F05 remains in0583 successor tests, importing `loop` and `recording`
from0583 behavior tests. These are the direct584 test-carrier dependency.
The wider existing0583 package includes four structural Red deselections and
their Issue owner. Modified0582 guard tests import0583 guard support, which
loads its frozen JSON; keep them together, visibly separate from584 production.

Read-only source-clean inventory finds TWO uncommitted distributed blockers:
`docs/specs/evaluator-static-foreach-elaboration.md` and
`docs/specs/opaque-foreach-wire-arithmetic-repair.md`. The failed smoke reported
only the first. Both must be committed before smoke passes on this tree.
All other dirty collaboration paths are excluded by current distribution policy.
Do not bypass source-clean, remove specs, add exclusions or refresh hashes.

The23 current changed/untracked paths, including this proposal, are assigned
once below. This is a future allowlist, not a staged index. Additional files
or unrelated hunks require renewed inspection. Never stage the whole tree.

## A — 0583 Test/Guard Carrier (11 files)

Suggested message: `test: preserve LISS-0583 foreach contracts for Wire repair`.

```text
docs/issues/LISS-0583-evaluator-static-foreach-successor.md
docs/specs/evaluator-static-foreach-elaboration.md
docs/collaboration/reviews/2026-10-05-liss-0583-phase1-review.md
docs/collaboration/traces/2026-09-29-liss-0583-static-foreach.md
docs/testing/active-red-tests.toml
tests/test_liss_0582_public_import_repair_red.py
tests/fixtures/liss_0583/guard-baseline.json
tests/liss_0583_guard_support.py
tests/test_liss_0583_guard_migration_red.py
tests/test_liss_0583_static_foreach_behavior_red.py
tests/test_liss_0583_static_foreach_successor_red.py
```

Prerequisite: human review/disposition of the three prepared F08 guard
transitions (import projection, evaluator executable AST, compatibility AST)
in the0583 packet.0584 acceptance did not accept0583 guard migration.
Carrier disposition is not0583 feature implementation/acceptance. Preserve
current assertions/hashes and four exclusions; F05 stays unexcluded.
No0583 runtime source belongs in A. Proposed dedicated branch:
`codex/liss-0583-test-carrier` at a287be51, created only after permission.
Keep historical0583 refs unchanged.

## B — 0584 Accepted Red Contracts (4 files)

Suggested message: `test: record accepted LISS-0584 Wire arithmetic contracts`.

```text
tests/test_liss_0584_opaque_wire_arithmetic_red.py
tests/test_liss_0584_repair_boundary_red.py
tests/fixtures/liss_0584/repair-boundary.json
docs/collaboration/reviews/2026-10-05-liss-0584-phase1-review.md
```

Stack on reviewed A in the0584 branch. Existing584 test acceptance covers B.
Original F05 is not moved/duplicated. Fixture base a287be51 remains the frozen
preservation baseline, not the future tested HEAD; never rehash for new commits.

## C — 0584 Implementation and Current Records (8 files)

Suggested message: `fix: reject numeric arithmetic on opaque foreach wires`.

```text
compiler/staqex/typecheck.py
docs/issues/LISS-0584-opaque-foreach-wire-arithmetic-repair.md
docs/specs/opaque-foreach-wire-arithmetic-repair.md
docs/collaboration/traces/2026-10-05-liss-0584-opaque-wire-arithmetic-repair.md
docs/collaboration/reviews/2026-10-06-liss-0584-phase2-verification.md
docs/work-plans/WP-0174-evaluator-residual-responsibility-successors.md
docs/collaboration/process-lessons-log.md
docs/collaboration/reviews/2026-10-06-liss-0584-commit-scope.md
```

Only production change: already-approved12-line guard. WP/lessons are shared
audit/navigation for this chain, not unrelated cleanup. Stage only relevant
hunks if new edits appear. Keep status verification-pending until actual C SHA
checks pass; record docs changed afterward create another required rerun.

## Execution and Verification Boundaries

1. Obtain carrier/guard disposition and explicit local commit permission.
2. Review A's staged diff, commit on its dedicated branch and record carrier SHA.
   Choose isolated checkout or explicit-index workflow preserving all dirty
   files; no reset, old-branch merge or stash deletion is authorized.
3. Base current584 branch on A, preserve uncommitted B/C, then commit B and C.
   Do not stage/replay A twice. Safe branch/index mechanics must be checked at
   execution time; this proposal has not changed branches or index.
4. A/B are intentional Red history: F05 fails without C; B adds new Reds.
   They are not standalone mergeable snapshots. Intermediate records may link
   to eventual C records. Deliver only the verified A→B→C chain, not a separate
   carrier PR/merge;0583 implementation remains separately gated.
5. Run focused48, consumer74, lifecycle-aware root, spec and ALL non-PR sanity
   checks at C SHA, including actual copy smoke. Keep four explicit0583
   deselections, no F05 exclusion. Record evidence outside the working tree.
6. Later documentation commits require all blocking reruns at new final SHA.
   PR-only checks apply when a PR exists. Only full Green permits a separate
   Phase 3 request. No completion/final-review/push/merge authority is inferred.

## Verification / Review Limits

Prior focused48/consumer74/root2419 (4 deselections)/spec161 results remain
dirty Phase 2 evidence, not fresh or final-SHA runs. Sanity remains failed.
Organization checks imports, full path partition, links/diff, preserved hashes,
source-clean blockers and lifecycle only. No source/test/lifecycle mutation.

Host/same_context review, empty models, no enabled large-change override.
Dirty committed metrics cannot describe this uncommitted package. No policy
change or execution batch is proposed. Approval/guard disposition remains open.

Same-context reviewer reread this proposal, the original import dependencies,
source-clean policy and current dirty inventory; checked all23 paths partition
exactly11/4/8 with no omissions/duplicates. Frozen read-only dependencies and
current TypeChecker SHA256 match Phase 2; links/diff and lifecycle pass (4
entries), index remains empty. This is weaker than separate-context review.
Findings: both specs must be tracked (apply via proposed A/C); carrier guard
acceptance missing (human decision pending); final-SHA verification missing
(required after authorized commits). No source/suite rerun this organization.

## Adjudicator Checklist / Decision

- [ ] Accept11-file0583 carrier and three guard transitions for dependency
  delivery, without authorizing0583 implementation.
- [ ] Accept4-file0584 Red and8-file implementation/record groups.
- [ ] Permit local A/B/C commits and linked branch preparation explicitly.
- [ ] Intermediate Red snapshots cannot merge; all checks run at C/final SHA.
- [ ] No hash/assertion/exclusion/source-clean/later approval gate is waived.

- [x] Approved
- [ ] Approved with comments
- [ ] Rejected

## Human Approval — 2026-10-06

Human `はい。` responds to the sole preceding request naming this three-way
split,0583 guard handoff and local commits. A/B/C scope, three F08 guard-carrier
transitions and linked local branch preparation accepted. This does not accept
all0583 feature tests or authorize0583 implementation, Phase3, push/PR/merge.
The earlier pending statements above are proposal-time history. Execute only
the listed paths, preserve assertions/hashes, rerun all checks after commits.

Execution: A=a14ab3af on dedicated carrier branch, fast-forwarded into584;
B=14973d84. C/checks pending; no independent Red-snapshot delivery.
