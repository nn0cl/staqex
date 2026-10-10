# WP-0174: Evaluator residual responsibility successors

| Field | Value |
|---|---|
| Status | active — LISS-0582 and LISS-0584 repair done; residual candidates require separate gates |
| Size | M |
| Parent | WP-0160 / core module decomposition |
| Scope approval | Evaluator residual-responsibility Architecture Path Phase 0 investigation approved 2026-09-28 |
| Completed candidate | LISS-0581 — coordinate liveness and Trace-Out successor; architecture accepted by ADR 0228 |
| Current Next Issue | LISS-0586 final verification / record commit approved; actual-SHA rerun pending |

## Goal

Continue reducing Evaluator-owned implementation bodies by selecting cohesive
successors from current consumer/state evidence, not by line count alone.
Preserve source meaning, public/private compatibility, diagnostics, and
Evaluator's unique mutable-state ownership.

## Inventory and order proposal

| Rank | Residual responsibility | Evidence | Disposition |
|---:|---|---|---|
| 1 | Coordinate liveness and Trace-Out: five Evaluator helpers and duplicate frame helpers | Shared consumers in frames, pipes, evolution, execution, observation; tied to existing ADR 0138/0142/0153/0158 behavior | LISS-0581 done; implementation commit passed 2,280 tests; PR delivery pending GitHub CI and merge |
| 2 | Runtime-plan eligibility/projection: callable eligibility, Operator-attribute walk, unit projection, first-family checks | Extracted policy retained; ten public imports restored | LISS-0582 done; PR #604 merged at 458fcbe6, PR/main CI and merge-result local checks passed; no retirement waiver |
| 3 | Static `forEach` expansion | Actual body migrated to dedicated successor, live binding callbacks and hook preserved | LISS-0583 done; PR #607 merged a349a5b7, merge-result CI passed (confirmed2026-10-08) |
| 4 | Tensor binding | Original algorithm moved to stateless61-line successor; exact private hook retained | LISS-0585 done; PR608 merged a661fb17, PR/main CI success |
| 5 | Host coefficient-array resolution | 42-line body crosses HostInputPort, finite binder and scientific input validation/provenance | LISS-0586 Phase3 review passed; clean c334766f all-blocking pass, final gate pending |
| 6 | Partial-call filling and small classical-state helpers | `_fill_partial` 31 lines; `_is_closed` 28; `_maybe_capture_classical_scalar` 23 | Keep separate until actual consumers, state writes, and feature ownership show a cohesive unit |
| Excluded | `_eval_set_comprehension` | Explicitly retained as dispatch/consumer in accepted classical Operator-evaluation spec | Do not reopen in this WP absent a new scope decision |

Ranks express investigation priority, not a committed roadmap. LISS-0585 now
has its accepted dedicated Phase 0 design. Lower-ranked candidates require their own
consumer/architecture intake and do not become authorized by this Work Plan.

## Issue Graph

| Issue | Status | Initial size | Current size | Planning record | Depends on | Blocks | Branch |
|---|---|---|---|---|---|---|---|
| [LISS-0581](../issues/LISS-0581-evaluator-coordinate-liveness-successor.md) | done — PR #603 merged and CI passed | M | M | AIP-0581-001 | ADR 0228 accepted | - | `feature/liss-0581-red` (deleted after merge) |
| [LISS-0582](../issues/LISS-0582-evaluator-runtime-plan-eligibility.md) | done — PR #604 merged; repaired-head and main CI passed | M | M | AIP-0582-002 | extraction retained; no later dependency | later dependency delivery still separately gated | `codex/liss-0582-repair-closeout` (documentation only) |
| [LISS-0583](../issues/LISS-0583-evaluator-static-foreach-successor.md) | done — PR #607 merged; main CI passed | M | M | AIP-0583-002 / accepted003 | LISS-0582 and LISS-0584 delivered | - | `codex/liss-0583-phase1-rereview` |
| [LISS-0584](../issues/LISS-0584-opaque-foreach-wire-arithmetic-repair.md) | done — reviewed repair/final verification passed; PR #606 tracks delivery | M | M | AIP-0584-001 | LISS-0582 done; A carrier a14ab3af | LISS-0583 Green/delivery until successful606 delivery | `codex/liss-0584-opaque-wire-arithmetic-phase0` |
| [LISS-0585](../issues/LISS-0585-evaluator-tensor-binding-successor.md) | done — PR608 merged; PR/main CI passed | M | M | AIP-0585-001 accepted | LISS-0583/0584 delivered | - | `codex/liss-0585-tensor-binding-phase0` |
| [LISS-0586](../issues/LISS-0586-evaluator-host-coefficient-resolution.md) | review — Phase3 passed; final verification approved, outcome pending | M | M | AIP-0586-001 accepted | LISS-0585 delivered | - | `codex/liss-0586-host-coefficient-phase0` |

## Current rank-5 design gate — 2026-10-09

Latest2026-10-11: final verification / six-record local commit / actual-SHA
all-blocking rerun explicitly approved. Source/tests unchanged. Outcome pending
at this record commit; evidence `/private/tmp/liss-0586-final.A6F6q8/result.md`.
Final result acceptance and delivery remain separate; no done claim. Earlier
pending-final-verification statements below are historical.

Latest2026-10-10: separate Phase3 approved; [review passed](../collaboration/reviews/2026-10-10-liss-0586-phase3-review.md)
without source/test changes. Fresh clean c334766f focused154/consumer37/adjacent20/
root2573/spec161/sanity10pass; original AST and scoped lazy-import/compileall
checks pass. Final verification / record commit / actual-SHA rerun approval
pending. No issue/WP done or delivery claim. All prior source-clean failure and
approval-pending statements below are historical. Validation responsibility
follow-up remains proposed, not mixed into this move.

Human `LISS-0586 ローカルコミット／実SHAで全blocking再検証承認` separately
approves bounded commits and actual-head all-blocking rerun. Result pending at
this record commit; resume from `/private/tmp/liss-0586-sha-verification.JBY9g4/result.md`
for actual SHA and outcome. After success request separate Phase3 review;
no source/test change or delivery authority. Older commit-pending notes historical.

Human Phase2 Green/implementation separately approved. Original Host body moved
to55-line successor, evaluator1055→1014lines, exact private hook retained.
Accepted test bytes unchanged; focused154/consumer37/adjacent20/spec161pass,
root2573pass, sanity9pass/1fail (uncommitted distributed spec).
[Current packet](../collaboration/reviews/2026-10-09-liss-0586-phase2-verification.md)
requests local commit / actual-SHA all-blocking rerun before Phase3. No full
Green, Phase2 completion, commit or delivery claim. Earlier gate notes historical.

Human `Phase 1 Red テストレビュー／acceptance承認（H04の扱いを含む）`
accepts the unchanged reviewed tests and unreachable-name disposition.
Phase1 accepted; next gate is separate Phase2 Green/implementation approval.
No source/test changes, commit or delivery authorized. Earlier pending notes
below describe prior gates, not current acceptance status.

[Phase1 same-context review](../collaboration/reviews/2026-10-09-liss-0586-phase1-review.md)
passed unchanged: fresh focused56pass/4structural Red, regression94pass and
independent original-AST/future-setup probes pass. Human test acceptance/H04
disposition pending; no Green/implementation authority.

Phase1 Red execution separately approved; [execution/test-review entry](../collaboration/reviews/2026-10-09-liss-0586-phase1-execution.md)
records new56pass/4expected structural Red, inherited63pass and consumer /
adjacent31pass. Runtime unchanged; bounded test-only integration only. Human
test acceptance / H04 unreachable-name disposition pending, no implementation
or delivery approval. Earlier execution-pending notes below are historical.

Human rank5 Scope/Phase0 start approved. [H01–H09 dedicated specification](../specs/evaluator-host-coefficient-resolution-successor.md)
accepts stateless input orchestration, existing typed validation, exact private
hook and bounded inherited-guard transition. Existing selected10 suites90pass
at a661fb17; root/spec/all-sanity not_run. Human
`LISS-0586 専用Issue/spec H01–H09・限定guard移行方針とPhase 0 acceptance`
accepts the dedicated design unchanged2026-10-09. Phase1 execution approval
pending; no new tests, implementation, commit or delivery authorized.
[Representative trace](../collaboration/traces/2026-10-09-liss-0586-host-coefficients.md).

Prerequisite0585 delivered: [PR608](https://github.com/nn0cl/staqex/pull/608)
merged a661fb1778e97eda3d35fd1615fd8928c031f062 after all3PRchecks passed.
[Main CI37896296489](https://github.com/nn0cl/staqex/actions/runs/37896296489)
completed success at that merge SHA. Local main synced clean before new scope.
Actual delivery-head e61f5c27 all-blocking evidence and merge-tree equivalence:
`/private/tmp/liss-0585-delivery.ruClfG/result.md`. Earlier pending-delivery
statements below describe their record commits, not current open work.

## Follow-up backlog: Host validation responsibility and diagnostic precedence

- Recorded2026-10-09 at the Adjudicator's request; status:proposed,
  phase:phase-0-design (not started), planning size:TBD.
- Canonical planning record: this section. Related:LISS-0586 / H04;
  execution dependency:LISS-0586 completion. Does not block the current
  behavior-preserving extraction or authorize implementation.
- Evidence: `compiler/staqex/runtime/evaluator.py::_resolve_host_coefficient_arrays`
  passes the same Host key as tensor `name` and provenance `input_id`.
  For a blank key with a non-None value, argument construction rejects the
  provenance ID before the tensor name validator executes. Missing values
  instead reach the existing missing-coefficient diagnostic. The tensor name
  validator remains reachable through direct construction with valid provenance;
  it is not established as dead code or eligible for deletion.
- Question to resolve: should coefficient identity and input provenance identity
  remain coupled, who owns each validation, and which diagnostic takes precedence?
  Current fail-closed behavior is established; a functional defect is not
  established merely by overlapping validation.
- Future scope: inventory all constructor/resolver consumers and accepted
  diagnostic contracts; propose explicit identity/validation responsibilities
  and precedence before any behavior change. Do not preselect new types or
  remove checks as part of this backlog entry.
- Acceptance planning: preserve rejection of invalid input, missing-input
  behavior, exception codes/messages/causes, valid Float/Bool behavior and
  direct-constructor coverage unless a separately reviewed specification
  explicitly approves a compatibility change. Add boundary and precedence
  tests under the normal Phase0/Red/Green/Refactor gates.
- Decision points: separate Scope/Phase0 approval, reviewed specification,
  compatibility disposition and subsequent phase/implementation approvals.
  Issue ID and branch will be allocated when this follow-up is selected.
- Current priority: finish LISS-0586's behavior-preserving split first; this
  follow-up must not silently expand H01–H09 or alter the reviewed Red tests.

## Historical rank-4 design gates — 2026-10-09

Delivery approved via human `受入れ記録コミット・再検証・push／PR作成・CI成功後のマージ`.
Accepted local feature done, process review recorded in Issue; final delivery
SHA/local checks/PR/CI/merge outcomes pending at this record commit:
`/private/tmp/liss-0585-delivery.ruClfG/result.md`. Latest origin/main remains
a349a5b7, no rebase required. Lower ranks remain separately gated.

Current final outcome: clean b5aad393 focused172/consumer37/adjacent22/root2513/
spec161/sanity10 and shape probe pass; human `LISS-0585 最終レビュー結果の受入れ`
accepts it unchanged. Delivery pending, no push/PR/merge. Acceptance sync is
uncommitted; future record commit needs actual-SHA rerun. Earlier notes historical.

Current: Phase2 actual-SHA e5688f80 focused172/consumer37/adjacent22/root2513/
spec161/sanity10 pass. Human separately selects Phase3 Refactor/review;
[R3 re-review passed](../collaboration/reviews/2026-10-09-liss-0585-phase3-review.md):
the pre-extraction fixture parameter inherits the extracted checkout, so both
cases copied the same root shape after Green. Human authorized the test-only
correction/re-review: explicit shape construction/assertions now close R3;
guard/inherited80 and focused172 pass, original assertions retained. Human
`LISS-0585 R3修正済みテスト／再レビュー結果の受入れ` accepts it unchanged.
Final verification/local commit/rerun separately approved via
`LISS-0585 final verification／ローカルコミット・実SHAで全blocking再検証`;
outcome pending at record commit, entry point
`/private/tmp/liss-0585-final-verification.A0bkuv/result.md`. No production change,
Phase3 completion or delivery claim. Earlier gate notes below historical.

Human `LISS-0585 Phase 2 Green／implementation承認` separately authorizes
the minimal accepted move; implemented without changing accepted tests.
Evaluator1099→1055lines; successor61lines, compatibility329lines. Focused172,
consumer37, adjacent22, root2513 and spec161 pass. Sanity9pass/1fail because
distributed-copy source-clean rejects the uncommitted dedicated spec.
[Current Phase2 packet](../collaboration/reviews/2026-10-09-liss-0585-phase2-verification.md)
records bounded local commits and actual-SHA all-blocking rerun, separately
authorized by human `LISS-0585 ローカルコミット／実SHAで全blocking再検証`.
The post-commit outcome entry point is
`/private/tmp/liss-0585-sha-verification.cFxPdj/result.md` (pending when this
record is committed); Phase3 and delivery are not authorized. The following
Phase0/1 notes retain their historical context.

[Phase1 same-context review](../collaboration/reviews/2026-10-09-liss-0585-phase1-review.md)
passed after human-authorized R1/R2 correction: future-shape old-body mutation
and guarded-tree copy now work in both root shapes. New30guard and inherited50
checks pass together; full scoped168pass/4structural Red. Human corrected-test
acceptance approved2026-10-09 unchanged; Green remains separate. No production changes.

Human `続けて` authorizes the single proposed Tensor binding Scope/Phase0 design.
[T01–T09 dedicated spec](../specs/evaluator-tensor-binding-successor.md) accepts
stateless ownership, exact private-hook wiring and a bounded preservation-guard
transition without fixture/hash relaxation. Scoped existing baseline109passed;
root/spec/all-sanity not_run. Human explicitly accepted dedicated Issue/spec,
T01–T09, bounded guard disposition and Phase0 on2026-10-09 unchanged;
Subsequent human Phase1 execution approval authorizes tests/limited guard
migration only. [Execution entry](../collaboration/reviews/2026-10-09-liss-0585-phase1-execution.md)
reports166pass/4expected structural Red, no previous assertion/fixture changes;
test acceptance, implementation and delivery remain separate. See the
[representative trace](../collaboration/traces/2026-10-09-liss-0585-tensor-binding.md).

## Historical rank-3 design/delivery gates — 2026-10-05/06

PR607 subsequently merged at a349a5b720c59f3a0e288c4751dd012c25514843;
merge-result CI run37452920283 passed, confirmed2026-10-08. Earlier pending
approval/delivery descriptions below retain their historical evidence context.

Current Phase 3 explicitly approved2026-10-06; [agent review passed](../collaboration/reviews/2026-10-06-liss-0583-phase3-review.md).
No source/test refactor needed; clean9165d6d1 fresh root2450/focused165/consumer77/
spec161/sanity10 all pass. Final record commit and actual-SHA rerun approval pending;
no issue done/delivery claim. Earlier Phase 2/pending Phase 3 statements historical.

Current guard Phase 2 explicitly approved2026-10-06 and implemented; focused165,
reviewer33, consumer77/spec161 pass. Local sanity9pass/1source-clean failure;
root2450pass without exclusions, committed all-blocking gate pending. [Current evidence](../collaboration/reviews/2026-10-06-liss-0583-guard-phase2-verification.md).
Prior pending guard implementation/test gates below are historical.

Current supplemental Scope / Phase 0 design and
[G01–G07](../specs/evaluator-static-foreach-repair-guard-migration.md) accepted
unchanged2026-10-06. Supplement Phase 1 execution explicitly approved; new27
cases prepared (24pass/3expected Red). Focused161pass/4fail, consumer77pass;
[agent test review](../collaboration/reviews/2026-10-06-liss-0583-guard-phase1-review.md)
passed; human `LISS-0583 guard移行 Phase 1 Red テストレビュー／acceptance承認`
accepts new27 tests/review unchanged2026-10-06. Guard Phase 2 implementation
approval pending. Acceptance sync documentation only; no fresh test-run claim.
Three exact path byte→AST protections accepted, five byte guards
and immutable fixture retained; semantics and tests unchanged. Feature Phase 2
is parked unchanged, no new guard edit or phase permission inferred.

Current Phase 2 approved and implemented2026-10-06. Focused94, consumer77 and
spec161 pass; root2422pass/1fail without exclusions after retiring four passing Red
entries.0584 readonly repair-base guard freezes three moved owners and is not
part of the accepted F08 migration; request bounded design/spec disposition.
Copy smoke rejects uncommitted distributed spec; no full Green or done
claim. [Current packet](../collaboration/reviews/2026-10-06-liss-0583-phase2-verification.md)
requests guard Scope/Phase 0 first, then local commit/all-blocking rerun before Phase 3. Earlier
pending Phase 1/2 statements below are historical.

Current re-review2026-10-06: explicit human Phase 1 re-review execution approval;
agent review passes on main6d1b851b,90pass/4structural Red, consumer/adjacent77pass.
Original F05 arithmetic now passes unchanged; no new failure IDs in compared
focused set. Subsequent human Phase 1 Red test review/acceptance approval accepts
the full packet unchanged. Phase 2 implementation approval remains pending;
implementation permission no.
Root/spec/sanity not_run this review. [Representative packet](../collaboration/reviews/2026-10-05-liss-0583-phase1-review.md)
and trace contain current evidence. Older delivery-pending wording below is
historical; merged0584 is a prerequisite, not dependent0583 approval.

Current closeout2026-10-06:584 final clean db897ca7 passed every local blocking
suite and final human review; separate delivery approval creates
[PR #606](https://github.com/nn0cl/staqex/pull/606). Issue/spec/trace synchronized,
same-context completion process review recorded. Record-head and merge-result
evidence external `/private/tmp/liss0584-delivery-*` / `liss0584-merge-*`; no
future CI/merge pass inferred. Next583 full Red test acceptance remains separate.
WP remains active. All pending584 phase statements below historical.

Current final gate2026-10-06: human final verification approved six-file record
commit and all-blocking rerun. Results `/private/tmp/liss0584-closeout-*` must
identify actual final SHA; no pass inferred before execution. After success,
delivery still separately gated; no584 Issue completion or583 implementation.

Latest2026-10-06: separate584 Phase3 approved; no source/test refactor needed.
[Current584 Phase3 packet](../collaboration/reviews/2026-10-06-liss-0584-phase3-review.md)
records fresh focused48/consumer74/spec161/sanity10 at909 and distinguishes
prior909 root2419 evidence. Final verification / bounded record commit approval
pending. Earlier statuses below historical; no Issue/WP done or delivery claim.

Current2026-10-06: approved A/B/C locally committed, C=6517c208 all checks pass,
including formerly failing copy smoke. Synchronization-head rerun evidence is
external under `/private/tmp/liss0584-final-*`; then request separate Phase3.
Earlier pending scopes/sanity failures below are historical, no delivery claimed.

Human `Scope／Phase 0設計開始承認` approves design/inventory only. Existing
local LISS-0583 tipb09e3e06 and its historical approvals are retained, not
treated as current repaired-main delivery or new phase authorization. The
[current accepted specification](../specs/evaluator-static-foreach-elaboration.md)
records F01–F08, twelve public imports missing from the old tip, complete
behavior-test requirements and bounded repair-guard disposition. Scoped65 and
adjacent41 baseline tests passed at a287be51; historical scoped evidence, not a
fresh run during acceptance sync. Human `Phase 0 acceptance」の承認` accepts
the dedicated Issue/spec F01–F08 and bounded guard disposition unchanged.
Phase 1 Red execution / limited guard migration separately approved. New tests:
89 passed / 5 failed (four structural, one F05 arithmetic contract mismatch);
consumer/adjacent77 passed on a287be51 + dirty tests/docs. Compiler unchanged.
Next: [test review / F05 disposition](../collaboration/reviews/2026-10-05-liss-0583-phase1-review.md);
implementation allowed no. No automatic deferral or test waiver.

Human `修復の設計開始承認` selects separate repair design on2026-10-05.
LISS-0584 accepted R01–R07 covers inferred-Wire numeric binary validation,
alias/nesting detection and positive neighbors. Existing failing F05 test is
retained, not weakened/excluded. Fresh repair design baseline:1expected failure,
adjacent21passed / numeric12passed; scoped only, no full Green. Human
`専用Issue/spec R01–R07 と Phase 0 acceptance` accepts the dedicated target
unchanged on2026-10-05. Subsequent explicit Phase 1 execution prepares48 cases:
24 expected Red/24 passed; consumer/adjacent74 passed, no source changes.
Human `LISS-0584 Phase 1 Red テストレビュー／acceptance` accepts the
[0584 packet](../collaboration/reviews/2026-10-05-liss-0584-phase1-review.md)
unchanged2026-10-06. Subsequent explicit Phase 2 implementation approval executes
the12-line numeric guard: focused48, consumer/adjacent74 and spec161 pass.
Sanity copy smoke rejects the pre-existing uncommitted0583 spec; full Green
not established. [Current584 verification/handoff](../collaboration/reviews/2026-10-06-liss-0584-phase2-verification.md)
requests reviewed dependency/document separation and commit permission, not
Phase 3 or delivery approval.
Human `はい。整理して` authorizes scope organization2026-10-06;
[A/B/C proposal](../collaboration/reviews/2026-10-06-liss-0584-commit-scope.md)
is prepared (11/4/8 files), not executed. Carrier guard disposition/local
commit permission remain pending; all-blocking sanity gap is not waived.
Phase 2 root2419 pass (4 approved0583 deselections); spec161 pass; sanity fails
copy smoke. Committed test dependency separation remains open.0583 Phase 1
test acceptance remains separate.0583 implementation and a new ADR are not authorized.

## Current repair closeout — 2026-10-05

Separate human delivery approval executed: PR #604 merged at
`458fcbe69b9161be21c2b8f92c8cd2838539e6f9` after all repaired-head PR CI
checks passed. All actual merge-result local blocking checks and main CI also
passed. Subsequent `続けて` authorizes documentation-only synchronization,
not rank 3–6 implementation or later dependency propagation. LISS-0582's
completion process review is recorded in its Issue; WP-0174 remains active.
See the [current trace](../collaboration/traces/2026-09-29-liss-0582-runtime-plan-eligibility.md)
for exact SHAs, environments, CI links and verification boundaries.

## Historical repair gates — 2026-10-05

Scope/Phase 0 start and unchanged [R01–R07 specification](../specs/evaluator-public-import-compatibility-repair.md)
accepted 2026-10-05; human `修復仕様 R01–R07 と Phase 0 acceptance` received.
Restore original-object re-exports, not old bodies or a weakened baseline.
Phase 1 execution separately approved; new repair tests: 14 expected failures /
23 passes. Consumer regression 8 pass; adjacent 52 pass. No production or frozen
baseline edits, commit/push/merge. Same-context review passed on unchanged tests;
human `Phase 1 Red acceptance を承認` received 2026-10-05.
Separate `Phase 2 Green／implementation` approved 2026-10-05. Import-only
repair passes focused37 / consumer8 / adjacent52 and spec161; capture/cmp
byte-equal. Full root2322 passed provisionally, no exclusions. Next: Phase 3
Refactor/review separately approved 2026-10-05; code review passed, no source
or test refactor required. Phase 2 final-SHA checks passed at93c1c86a; review
record commit checks passed atc2112a4f. Human final local verification/review
approved 2026-10-05; no source/test change, final status-commit checks required.
Next: separate delivery authorization, then repaired-head CI; no Issue/WP done
before R06/R07 and completion process review. See the
[review packet](../collaboration/reviews/2026-10-05-liss-0582-repair-phase3-review.md).
Red execution/review/implementation remain separately gated. Prior completion
is historical; delivery approval is not a CI waiver.

## Verification and approval gates

- Phase 0 was a static AST/consumer/spec inventory; it authorized no tests or
  source edits at that time.
- Before Phase 1: accept the successor boundary and Phase 0 packet; inspect
  lifecycle state of existing `_red.py` tests; confirm the exact phase path
  matrix; and obtain separate Phase 1 Red approval. The acceptance inventory
  identifies two coverage gaps: eligible post-call live-out retention and
  Snapshot exclusion, plus structural ownership/delegate assertions.
- Before Phase 2: reviewed Red, separate Phase 2 Green/Implementation approval.
- Before Phase 3: separate Phase 3 approval; inspect body ownership behind any
  compatibility hook and run actual consumers/adjacent suites.
- LISS-0581 Phase 2: implementation and all-blocking tests passed on the dirty
  worktree; see the [verification record](../collaboration/reviews/2026-09-28-liss-0581-phase2-verification.md).
  This is provisional evidence, not final-commit verification. The 131-line
  free-variable walker was moved intact; any readability restructuring belongs
  to the separately approved Phase 3 review, not an assumed Phase 2 expansion.
- Completion: deterministic verification tied to final commit SHA, all
  blocking suites rerun after final commit, status synchronized, process review.
- LISS-0581 Phase 3: `expr_free_vars` is decomposed into named binder, operator,
  and expression-node walkers without changing tests or intended traversal
  behavior. See the [Phase 3 review packet](../collaboration/reviews/2026-09-28-liss-0581-phase3-refactor-review.md).
  Human final review is approved; commit and post-commit verification remain
  pending.

## Applicable process lessons

The detailed application is recorded in LISS-0581 and its proposed spec:
state ownership; private-consumer inventory; narrow callbacks; true successor
ownership; compatibility identity/export rules; clause-to-test reconciliation;
and status drift prevention.

## Planning record

### AIP-0581-001

- Status: proposed
- Created by: Codex desktop, local repository worktree
- Model/reasoning as displayed: N/A; not surfaced by host
- Created: 2026-09-28
- Planning size: M
- Intended route: host agent for bounded stateless decomposition; same-context
  review if the runtime-routing policy requires an agent review packet;
  deterministic AST/import checks and runtime suites for verification.
- Scope: one cross-module liveness family, its compatibility hooks and direct
  consumers; no semantic expansion.
- Estimated context tokens: 8,000–14,000; midpoint 11,000 (planning estimate,
  not actual usage).
- Basis: five small evaluator methods, duplicate frame helpers, reuse by five
  runtime services, existing liveness AST hooks, and direct characterization
  consumers. Verification requires behavior suites across four established
  Trace-Out paths and broad blocking tests.
- Assumptions: approved semantics remain unchanged; existing tests can be
  mapped/reused; no new shared mutable state.
- Confidence: medium; AST walker ownership and live `_red.py` status require
  Phase 0 acceptance reconciliation.
- Revises/supersedes: none.
