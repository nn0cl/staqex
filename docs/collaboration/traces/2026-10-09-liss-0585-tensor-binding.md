# LISS-0585 Tensor binding design / resumable handoff

## Request and current state

- Date: 2026-10-09
- User request: `LISS-0585 final verification／ローカルコミット・実SHAで全blocking再検証`
- Phase: Feature Path / Phase3 accepted review, authorized final verification pending outcome
- Issue/planning record: LISS-0585 / AIP-0585-001
- Branch: codex/liss-0585-tensor-binding-phase0, from refreshed origin/main
  a349a5b720c59f3a0e288c4751dd012c25514843; old delivered branch preserved
- Completed: accepted Issue/spec T01–T09, consumer/guard inventory, Phase1
  acceptance tests and bounded test-only guard migration; minimal Tensor move

## Context ledger and routing

- Included: current language §5.3/DEC-0005; evaluator/Joint/binding/context/
  compatibility; Tensor tests; shared0583 guards and0582/0584 callers; workflow
  and verification/structure policies, live process lessons
- Omitted: rank5/6, Rust implementation, external provider/SDK, private data
- Assumptions: extraction preserves existing algorithm; private hooks kept
- Open decision: human final acceptance after all-blocking success, then delivery
- Review isolation: same_context; implementation isolation: host; model IDs empty
- Tools: local rg/Git/AST-oriented source inspection/pytest; no external AI

## Applicable lessons

- Bounded-repair-guard lifecycle: inventory shared original and prerequisite
  guards before source moves; immutable baselines retained and bounded delta
  requires acceptance, not a hash refresh or new exclusion.
- Private consumers/callbacks/state ownership: keep context._bind live and
  `_bind_tensor` hook; no second state owner or copied maps.
- Compatibility/import hygiene: preserve actual wildcard exports even when
  unused inside evaluator; exact installer identity test required.
- Acceptance inventory/Red distinction: T01–T09 name minimum evidence;
  structural gaps must be reported separately from behavior regressions.
- Status drift: synchronize new Issue/spec/WP; annotate prior rank3 delivery
  wording as historical, no implied acceptance or implementation permission.
- AST traversal, external adapter/semantic projection lessons: no such changes
  proposed; out of scope, neighboring regression retained where applicable.

## AI execution record — attempt 1

- Agent/environment: Codex desktop / local macOS arm64
- Model and reasoning as displayed: N/A, stable task metadata unavailable
- Estimated tokens: 8,000–16,000, midpoint12,000, AIP-0585-001 planning only
- Actual tokens/metric/source/attribution: N/A; no task-scoped telemetry exposed
- Estimate variance: not calculable; no inferred actual usage
- Scope/result: Phase 0 design prepared; awaiting acceptance, not Green
- Attempt boundary: one cohesive design run; no implementation attempt
- Cost controls: Architecture Path for cross-file ownership/guard design;
  only directly relevant source/tests and required contracts; search and tests
  determine facts rather than speculative Rust/provider design
- Rework: none; missing historical ADR path resolved through canonical DEC-0005

## Deterministic verification

Before Markdown changes, clean SHA a349a5b720c59f3a0e288c4751dd012c25514843,
cwd /Users/nn0cl/Documents/git/qpex; Darwin27.0.0 arm64, Python3.12.6.

```text
/usr/local/bin/python3.12 -m pytest -q
  tests/test_ascii_tensor_parity_red.py
  tests/test_joint_preserve_and_harvest.py
  tests/test_qudit_slice_c_red.py
  tests/test_liss_0375_nested_when_tensor_dispatch_red.py
  tests/test_liss_0511_product_tensor_meaning_red.py
  tests/test_liss_0582_public_import_repair_red.py
  tests/test_liss_0583_guard_migration_red.py
  tests/test_liss_0583_repair_boundary_migration_red.py
  tests/test_liss_0584_repair_boundary_red.py
```

Executed as one shell command,109passed in3.35s, exit0, failures/errors/skips0,
no exclusions; raw tool output in this session. Scoped characterization plus
preservation checks only; all-blocking/root/spec/sanity not_run in Phase 0.
Precise test start/end timestamps not captured; no Phase2/final evidence claim.
Documentation checks: git diff --check and local Markdown link-path checks
passed; pytest version confirmed9.0.3. No all-blocking claim from these checks.
Main fetch succeeded; diff between previous delivered head5d7a781e and current
main a349a5b7 was empty. No predecessor merge/status mutation needed in source.

## Adjudicator decisions / next safe action

Scope / Phase0 design continuation authorized2026-10-09. Subsequently human
`LISS-0585 専用Issue/spec T01–T09・限定guard移行方針とPhase 0 acceptance承認`
accepts the dedicated Issue/spec, T01–T09, bounded guard disposition and Phase0
unchanged. AIP-0585-001 accepted as design planning only. All later execution
phases unapproved; implementation permission no. Approval sync changes only
Issue/spec/WP/trace; no new test run or full-Green claim. Historical attempt1
pending-acceptance result above describes the pre-approval design run.
Subsequently human `LISS-0585 Phase 1 Red（受入テスト作成・限定guard移行）の実行承認`
authorizes only Phase1 tests/limited guard transition on2026-10-09.
Next: obtain Red test review/acceptance. Post-review: Red tests must be
reviewed before Green; no commit/push/PR/merge authorization inferred.

## Changed files / blockers

- docs/issues/LISS-0585-evaluator-tensor-binding-successor.md (new)
- docs/specs/evaluator-tensor-binding-successor.md (new)
- docs/collaboration/traces/2026-10-09-liss-0585-tensor-binding.md (new)
- docs/work-plans/WP-0174-evaluator-residual-responsibility-successors.md
- docs/collaboration/reviews/2026-10-09-liss-0585-phase1-execution.md (new)
- docs/collaboration/reviews/2026-10-09-liss-0585-phase1-review.md (new)
- docs/collaboration/process-lessons-log.md (future-shape test lifecycle lesson)
- tests/test_liss_0585_tensor_behavior_red.py (new)
- tests/test_liss_0585_tensor_ownership_red.py (new)
- tests/test_liss_0585_tensor_guard_migration_red.py (new)
- tests/liss_0585_guard_support.py (new)
- tests/fixtures/liss_0585/original-tensor-method.txt (new)
- tests/liss_0583_guard_support.py (bounded test-only projection delegation)
- compiler/staqex/runtime/evaluation/tensor_binding.py (new stateless owner)
- compiler/staqex/runtime/evaluation/compatibility.py (exact hook wiring)
- compiler/staqex/runtime/evaluator.py (remove original body, install hook)
- docs/collaboration/reviews/2026-10-09-liss-0585-phase2-verification.md (new)

Changes uncommitted. No prior fixture/assertion/lifecycle changes; accepted
tests/support unchanged during Phase2. Blocking copy smoke requires clean
committed source; bounded local commit/rerun now explicitly approved. External/dynamic
consumer and resolved-cycle completeness remain explicitly unassessed.

## Phase1 execution continuation — same design/feature attempt

Readiness: accepted EARS/T01–T09, observable outcomes, test location `tests/`,
no external dependency, explicit Phase1 selection and existing DEC-0005 boundary.
Design intake/readiness performed before changes; implementation permission no.
Host/test-only route; same_context review configured but not yet executed.
Model/reasoning/actual usage N/A as above; no new estimate or telemetry claim.

Prepared29behavior/dispatch +28guard +4structural cases (61new cases).
Only two parse sites in existing guard helper delegate to exact Tensor
reconstruction; old hashes and assertions retained. Synthetic successor lives
only in pytest temporary trees. New immutable source evidence pinned to actual
main method, not a replacement for historical0583/0584 fixtures.
Clause/guard mapping and exact future allowed paths are in the execution entry.

Initial test setup used nonexistent `bind_one`; inspection found actual `bind`.
Corrected test import and spec's inventory label only, preserving the accepted
single-name rejection requirement. Collection error not classified as product
Red. No independent repair or scope expansion; no second implementation attempt.

Combined command: prior Phase0 nine-suite command plus
`tests/test_liss_0585_tensor_behavior_red.py`,
`tests/test_liss_0585_tensor_ownership_red.py`,
`tests/test_liss_0585_tensor_guard_migration_red.py`.
Result166passed/4failed in3.25s,170collected, exit1, errors/skips/exclusions0;
expected structural IDs exactly the four ownership functions. Existing109
baseline has no new/resolved failures. Guard positives/negatives28pass together.
Evidence is dirty HEAD a349a5b7 / macOS27.0.1 arm64 Python3.12.6 pytest9.0.3;
root/spec/sanity not_run. Lifecycle remains entries0: no Red exclusions claimed.
git diff --check passed, no production/old-fixture diff. New suite/support
sizes188/52/172/120physical lines; no numeric structure settings configured.
Record timestamps unavailable for first scoped run; no final-SHA evidence claim.
Final scoped rerun after final test edits:166pass/4same structural Red in3.16s,
exit1,170collected, errors/skips/exclusions0. UTC start2026-10-08T19:35:15.346877Z,
end19:35:18.758828Z; same dirty SHA/environment. Local Markdown path checks,
git diff --check and lifecycle entries0 checks pass. No all-blocking claim.

## Phase1 review / current handoff

Historical initial review below; latest correction/re-review record follows.

Human selected `LISS-0585 Phase 1 Red テストレビュー／acceptance`; reviewer role
re-read actual spec/suites/support and inherited diff from disk, not prior author
reasoning. Effective same_context, optional large-change absent, model empty.
Readiness retained; no corrective test/implementation edits while reviewing.
Current12-suite rerun166pass/4same expected structural Red in3.27s, exit1,
errors/skips/exclusions0. Same dirty HEAD/environment; all-blocking not_run.
review-change tool dirty-tree unknown means committed0 counts are not the actual
change size; route remains configured same_context, not a downgrade.

Additional temporary future-shape diagnostics reproduce two blockers:
R1 old-method mutation setup fails after correct body removal; R2 current-root
fixture omits the actual successor and rejects the positive as missing.
[Review packet](../reviews/2026-10-09-liss-0585-phase1-review.md) names lines,
reproduction and dispositions. Recorded migration-test-shape-invariance lesson;
apply it at the next correction intake. No review pass/acceptance claim.

Next safe action: human-authorized Phase1 test-only R1/R2 corrections, then
re-review/acceptance; implementation remains unauthorized. Existing assertions,
immutable fixtures, production and lifecycle unchanged by review. Documents
only updated; no commits/delivery. Same attempt review, not a new repair run.

## Attempt 2 — authorized test-fixture correction and re-review

- Authorization: human `はい。` to the sole R1/R2 test-only correction and
  re-review request; no implementation permission or test acceptance inferred.
- Attempt boundary: prior review found invalid future-shape fixture assumptions;
  replanned only setup, not Tensor semantics or approved guard boundaries.
- Initial/current size: M/M, unchanged; accepted AIP-0585-001 scope retained.
- Agent/environment/model/usage: same host macOS/Python; displayed model/reasoning
  and actual task tokens N/A as above. No new actual usage estimate fabricated.
- Route/context: Feature Path; R1/R2 new migration test only; applied shape-
  invariance lesson; production/Rust/rank5/6 omitted.
- Corrective edits: copy actual successor when present outside old manifest;
  restore and validate historical Tensor shape before mutating; add two root-
  shape regressions invoking actual fixture and existing negative test.
- Changed code: only tests/test_liss_0585_tensor_guard_migration_red.py compared
  with prior review,172→202physical lines; existing assertions/hash strings kept.
- Verification: new30guard pass in1.37s; combined168pass/4expected structural Red
  in3.50s,172collected, exit1, errors/skips/exclusions0; prior109pass unchanged.
- Role switch: reviewer re-read corrected file/accepted T09, independently reran
  new guard + original0583/0584 suites80pass in2.23s, exit0, no failures/skips.
- Evidence: dirty HEAD a349a5b7, Python3.12.6 pytest9.0.3/macOS27.0.1 arm64;
  no precise run timestamps, root/spec/all-sanity not_run. No full Green claim.
- Result: R1/R2 closed with evidence, same-context agent re-review passed;
  [current packet](../reviews/2026-10-09-liss-0585-phase1-review.md).
- Handoff: await human corrected Phase1 acceptance; Green approval separately.
  All original fixtures/production/lifecycle unchanged, no commits/delivery.

## Corrected Phase1 acceptance — 2026-10-09

Human `LISS-0585 Phase 1 Red テストレビュー／acceptance承認` accepts corrected
tests/support/immutable evidence and R1/R2 dispositions unchanged. Issue/spec/
WP/review/trace synchronized only. No test/source/fixture/exclusion edits or
new test execution; prior168pass/4structural Red and reviewer80pass remain scoped
historical evidence. No commit/delivery. Next safe action requires separate
Phase2 Green / implementation approval; implementation permission remained no
at that historical acceptance-only step.

## Phase2 implementation / resumable handoff — 2026-10-09

### Current state and completed work

Human `LISS-0585 Phase 2 Green／implementation承認` explicitly selects Feature
Path / Phase2 and authorizes the accepted T01–T09 minimal move. Design intake,
readiness and process lessons applied before source changes; host implementation,
same_context review routing, model IDs empty. No new ADR, dependency or state.
Current request: complete Phase2 verification, not Phase3/refactor or delivery.
Out of scope: rank5/6, Rust, semantic fixes and accepted-test changes.

The original45-line Tensor body now has one stateless context-first owner in
`evaluation/tensor_binding.py` (61physical lines); evaluator only installs its
private `_bind_tensor` hook through compatibility. Live `_bind`, imports,
algorithm and diagnostics retained. Evaluator1099→1055; compatibility323→329;
total three production owners1422→1445, responsibility split not net reduction.
All six accepted test/support/evidence hashes unchanged before/after;
binding/context and historical0583/0584 fixtures unchanged. Exact hashes and
verification states: [Phase2 packet](../reviews/2026-10-09-liss-0585-phase2-verification.md).

Dirty HEAD/base a349a5b720c59f3a0e288c4751dd012c25514843, macOS27.0.1 arm64,
Python3.12.6 `/usr/local/bin/python3.12`, pytest9.0.3, cwd as above.
Focused172pass (all four structural Red resolved), consumer37pass,
adjacent22pass, spec161/161pass. Root2513pass in324.26s, exit0;
failures/errors/skips/exclusions0. No root failures to enumerate this run.
Sanity all10 applicable non-PR steps executed:9pass/1fail, copy smoke rejects
uncommitted distributed spec. No exclusions; no all-blocking Green claim.
Root clean-main failure comparison unavailable; comparable focused172 set
resolves exactly the prior four failures. Precise root/focused timestamps
unavailable; provisional dirty-tree evidence, not actual-SHA completion.
No commit, push, PR or merge. All current changed paths listed above.

### Context ledger, next safe action and blockers

Included: accepted spec, actual consumers and preservation tests, source owners,
verification/source-quality policy and CI steps. Omitted: other candidate
families and external runtime consumers; assumptions: preserve current behavior,
including direct-AST quirks. External/dynamic consumers and fully resolved graph
unassessed, no completeness claim. Review same_context / implementation host,
no model identifier. Size M/M and accepted AIP-0585-001 unchanged; actual
token/usage metrics unavailable, no inferred measured cost.

Next safe action: obtain bounded local commit/process approval, commit only
current0585 planning/tests/source and synchronized records on the named branch,
then rerun all blocking against the actual final SHA with evidence outside the
tree. Copy smoke needs committed clean source, not relaxed assertions or a waiver.
Root completion recorded in this trace and the Phase2 packet. Phase3 and delivery
require their own later approvals. No additional implementation proposed.

## Approved local commit / SHA verification continuation — 2026-10-09

Human `LISS-0585 ローカルコミット／実SHAで全blocking再検証` selects the
single immediately proposed process gate. Feature Path / Phase2 continuation;
no source, test, fixture, exclusions, instructions or semantic edits.
Accepted-test hashes rechecked before committing; unchanged. All dirty paths
are the current0585 artifacts inventoried above; no unrelated paths staged.
Commits separate accepted tests/Phase1 evidence from source/current-state
records. Issue/spec/WP/trace sync belongs with the implementation unit.

Post-commit tests target the final local commit, clean tree, same Python3.12
environment. Evidence outside tree:
`/private/tmp/liss-0585-sha-verification.cFxPdj/result.md` and per-suite logs.
Outcome pending at record commit; the external entry will report actual SHA,
UTC times, commands and focused/consumer/adjacent/root/spec/sanity separately.
Comparable provisional results are172/37/22/2513/161 and sanity9pass/1fail.
Clean-main root baseline remains unavailable; do not infer baseline equivalence.
Process lessons applied: immutable guards/test-shape invariance, final-SHA rule,
compatibility consumers and status synchronization. Other IR/provider lessons
out of scope: no change to those owners. Same_context review / host execution,
model IDs empty; size M/M and AIP-0585-001 retained, measured usage N/A.

Next safe action: complete rerun, verify HEAD unchanged and tree clean, then
report external evidence and request separate Phase3 Refactor/review approval
if all blocking pass. On failure report it without test/assertion relaxation.
Issue remains in_progress/phase-2-green, not done; no completion-process review
or delivery claimed. No push/PR/merge authority. This section and the external
result form the resumable handoff; changed files/context/omissions listed above.

## Phase3 review / current handoff — 2026-10-09

Human `LISS-0585 Phase 3 Refactor／review` selects only this phase. Readiness
recovered from clean e5688f8071fbf7986f512cb0e96b4fcc4d8c62f0 actual-SHA
Phase2 evidence: focused172, consumer37, adjacent22, root2513, spec161,
sanity10 all pass, no exclusions. Issue/planning M/M AIP-0585-001 unchanged.
Role switched to reviewer; same_context (weaker isolation) / empty model,
host execution. Runtime config lacks large-change override/numeric budgets;
committed measurements17files/1784lines, owner-mapping/cycles remain unknown.
No source/test implementation while reviewing, no gratuitous code split.

Fresh clean-SHA focused172pass3.92s, consumer37pass1.03s, adjacent22pass0.31s,
all exit0; UTC01:57:00.624639→01:57:06.813536, same macOS27.0.1/Python3.12.6/
pytest9.0.3 environment. Logs `/private/tmp/liss-0585-phase3-review.r3gK3S`.
Root/spec/sanity evidence re-read for unchanged source/test SHA, not rerun
this turn; documentation edits are provisional, final commit gate remains.

Review changes requested: R3 actual-fixture probe reports old_body=false and
successor=true for both `unextracted` and `tensor-extracted` root-copy inputs.
Probe exit1 confirms duplicate-shape coverage, not product regression;
old-body reconstruction/mutation rejection remains effective. No runtime
blocker identified in inspected algorithm, hook identity, consumer/AST/bytes.
[Review packet and narrow correction](../reviews/2026-10-09-liss-0585-phase3-review.md).

Changed this turn: Phase3 packet, Issue/spec/WP/this trace and process lesson.
No source/test/assertion/fixture/exclusion edits, commits, push, PR or merge.
Included: canonical spec, implementation/guards, actual consumer search,
verification/source-quality policies and executable logs. Omitted: other
candidate families/Rust/providers/secrets. Assumption: preserve existing
behavior; external/dynamic consumer graph unassessed. Actual token/usage N/A,
no new architectural or technology decision. Lesson application: preserve
accepted guards and assert actual named shape before copying, not labels.

Next safe action: obtain `LISS-0585 R3 テスト設定限定修正／再レビュー` approval.
Then change only the migration-test setup/explicit shape assertions and
matched records, preserve all negatives/hashes, rerun focused and re-review
for human corrected-test acceptance. Final-SHA all-blocking and delivery
remain separate gates. Stop required by same-context-review/adjudicator-review
at accepted-test change boundary. Phase3 not passed; Issue not done, no process
completion review claimed. Recover from this packet/trace/spec/branch/diff.

## Attempt 3 — authorized R3 test-setup correction / re-review

Date2026-10-09, human `LISS-0585 R3 テスト設定限定修正／再レビュー`.
Boundary: resume after review found R3, bounded changed setup plan, not a
production repair or new architecture. Feature Path / Phase3; size M/M remains
appropriate, AIP-0585-001 unchanged. Host correction then same_context reviewer
role; empty models, no large-change override. Actual tokens/cost/variance N/A,
not available from task telemetry; no inferred usage. Existing planning estimate
remains historical, no new measured-cost claim. Context narrowed to R3 test,
immutable projection helpers, accepted T09 and the review/verification records.

Design/readiness and migration-test-shape lesson applied before edit. Exactly
23lines added to one existing regression: restore old temporary evaluator/
compatibility, remove only its copied temporary successor, assert old-body /
setup counts / successor presence for both labels and check each source shape
before actual fixture copy. All prior assertions unchanged; no runtime,
support algorithm, original fixture/hash, exclusion or instruction changes.
The only changed test SHA256 is
ee4d3cd1c91324ac62e90cfdc005abe2ae25e2a49df5c0948b220855f5f76daf;
other five accepted hashes unchanged. Original accepted test value retained in
historical Phase2 evidence; authorized strengthening recorded, not hidden.

Guard30+inherited50 pass80 in2.39s, exit0 (task output; exact times unavailable).
Unmodified reviewer probe now observes oldbody=true/successor=false for oldroot,
false/true for extracted root; exit0, UTC03:58:38.527537→03:58:38.889725.
Switched to reviewer, re-read corrected function/diff/spec/procedure, independently
reran full12focused:172pass3.77s, exit0, errors/failures/skips/exclusions0,
UTC03:59:07→03:59:11. Probe false→true resolved, focused pass inventory unchanged.
Dirty HEAD/base e5688f8071fbf7986f512cb0e96b4fcc4d8c62f0, macOS27.0.1 arm64,
Python3.12.6 pytest9.0.3; evidence directory
`/private/tmp/liss-0585-phase3-review.r3gK3S`, logs r3-shape-probe-fixed.log and
r3-focused.log. Fresh clean-main root comparison unavailable; root/spec/sanity
not_run on changed tree. Prior committed all-blocking result not current final
evidence after this accepted-test change; final-SHA rerun remains required.

R3 closed in agent re-review; no remaining finding in that bounded correction.
Test module225lines, qualitative single setup responsibility, numeric budgets
absent. Semantic graph/external consumers remain explicit broader review gaps.
Changed since e5688f80: one migration test and six matched review/status/lesson
documents from preceding/current review, all uncommitted. No new source edit,
commit, push, PR or merge. Updated packet:
[Phase3/R3 re-review](../reviews/2026-10-09-liss-0585-phase3-review.md).

Current handoff: human corrected R3 test/review acceptance required, then separate
final verification / record commit / actual-SHA all-blocking approval. No Phase3
completion, issue done or delivery claim. Production permission no additional
change; only the approved test correction performed. Included canonical spec,
reviewed artifacts and logs; omitted lower-ranked families/Rust/providers/secrets;
assumption preserve existing semantics. Review same_context (weaker isolation),
implementation host. Agent-handoff/adjudicator-review stop at corrected-test
acceptance, not infer it from permission to correct. Recover from packet/trace,
spec, branch and changed files; no separate completion process review yet.

## R3 corrected-test acceptance synchronization — 2026-10-09

Human `LISS-0585 R3修正済みテスト／再レビュー結果の受入れ` accepts corrected
test/re-review unchanged. Documentation synchronization only, no additional
execution attempt or test-run claim. Corrected test SHA256 ee4d3cd1… retained;
production and all other accepted test/support/fixture bytes unchanged.
Issue/spec/WP/review/lesson/trace synchronized; current tree remains uncommitted,
HEAD e5688f8071fbf7986f512cb0e96b4fcc4d8c62f0. Earlier acceptance-pending
statements in attempt3 are historical. No commit/push/PR/merge performed.

Handoff: bounded R3 review accepted, final verification not authorized. Next
obtain approval for local commit of the one corrected migration test plus six
matched records, actual-SHA focused/consumer/adjacent/root/spec/sanity10 and
shape-probe rerun. Save evidence outside tree; preserve accepted test bytes and
keep human final acceptance/delivery separate. Proposed scope in Phase3 packet.
Included context: accepted R3 packet/test and canonical status records;
omitted other families/Rust/providers/private data. Assumptions/routing unchanged:
same_context review (weaker isolation), host, empty models; M/M AIP-0585-001,
actual usage N/A. Issue stays in_progress/phase-3-refactor, not done. Agent-handoff
and adjudicator-review stop at the distinct final-verification approval gate.

## Authorized final-verification continuation — 2026-10-09

Human `LISS-0585 final verification／ローカルコミット・実SHAで全blocking再検証`
explicitly authorizes the named process gate. Commit only accepted R3 migration
test plus six matched documents (Issue/spec/WP/trace/review/lesson). No new
source/test/fixture/exclusion/contract change. Corrected test SHA256ee4d3cd1…
unchanged. Host deterministic execution, same_context review retained, empty
models, M/M AIP-0585-001, measured usage N/A. This continues attempt3's accepted
correction/verification, no new implementation plan.

Final outcome/logs outside tree:
`/private/tmp/liss-0585-final-verification.A0bkuv/result.md`. Outcome pending
at this record's commit. Rerun focused/consumer/adjacent/root/spec/all10 applicable
sanity and unchanged shape probe against final SHA, verify clean tree/HEAD,
preserve command/time/environment/exit/failure comparison evidence. Prior
e5688f80 results remain comparable baseline, not final corrected-test evidence.
Included accepted T01–T09/review/test and verification/commit policy; omitted
other families/Rust/providers/secrets. Dynamic external consumers/resolved cycles
remain unassessed, no completeness claim.

Next safe action: finish committed-SHA rerun and report final outcome for human
final acceptance. No push/PR/merge, no issue done before required closeout/process
review, no extra implementation authorized. This trace/packet and external
outcome form the resumable handoff without an evidence-only repository commit.
