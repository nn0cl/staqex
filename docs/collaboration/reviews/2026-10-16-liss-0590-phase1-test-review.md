# LISS-0590 Phase1 Red test review

Status: **agent_pass — R1 closed after authorized correction/re-review**.
Human corrected-test acceptance received2026-10-16;Phase2 later separately
approved/performed. Current implementation gate belongs to Phase2 verification.
Date:2026-10-16 Asia/Tokyo. Initial review below is historical;current evidence
and approval target are in the final R1 re-review section.

## Review packet

- Scope:Feature Path/Phase1 Red O01–O10 tests and approved four-carrier migration.
- Canonical documents:[spec](../../specs/typechecker-operator-body-successor.md),
  [Issue](../../issues/LISS-0590-typechecker-operator-body-successor.md),
  [WP0175](../../work-plans/WP-0175-source-responsibility-inventory.md).
- Re-read from disk:whole spec,new four suites/helper,original method and
  carriers,actual carrier diff,immutable baseline,TypeChecker Ty/construction
  callbacks,inherited copy helpers,author trace and deterministic output;
  readiness/testing/verification/quality/routing/lessons and review templates.
- Reviewer isolation:same_context,explicitly weaker than separate_context.
  Reviewer role only;no continued test authorship or implementation.
- Reviewed16-test-artifact SHA256:
  `7817b20c89a9a177141ea659799a5ffe499b8152418fa08e96e0f68ee4ce7754`.
  Audit confirms unchanged authored bytes and all221production files equal Git
  b5c96f7e4c2a846f41ac8ad5d882f0cb987cd420. No fifth carrier edit.

## Findings / dispositions

### R1 [P2] Factory exception case fails in an earlier type conversion (closed below)

Location:`tests/test_liss_0590_operator_behavior_red.py:159–160`.
Applicable contract:O04 and the explicit minimum O03/O04 evidence matrix
require factory-exception timing,not merely any exception before binding.

`where="factory"` globally replaces `typecheck.Ty` with `fail`,but uses
`TypeRef("Index",["2"])`. Its unconditional `_ty_from_ref` runs before the
operator's binding constructor. Independent profiling of the existing exact
test for **both RuntimeError and Abort(BaseException)** records:

`_legacy_check_operator:1595 → _ty_from_ref:2492 → _semantic_ty_from_ref:2555 → fail`.

Thus the two cases pass without reaching either original operator constructor
(1493/1657),or the future `_operator_index_type` call. Their current empty-event,
zero-depth/absent-binding expectations cannot distinguish this earlier failure
from the intended site. This is a test evidence gap,not a newly diagnosed
production semantic defect. Whole-AST guards are valuable but do not make the
claimed explicit exception scenario executed.

Disposition:**apply — pending author correction/permission**. Isolate type/domain
conversion from the injected constructor failure;exercise actual constructor
sites (including the two-site IndexDomain path) with call-site/count evidence,
Exception/BaseException propagation,exact callback order and env/depth timing.
Use real original Ty values before injection where needed. Keep source frozen,
original fixtures/hashes/four-carrier policy and expected structural Reds.
Re-review corrected exact bytes before human acceptance. No repair made here.

### Other reviewed boundaries

- O01/O07/O09:independently derived the whole method from immutable Git,
  preserved class-indented literals and verified exactly two Ty substitutions.
  Actual temporary pre/post trees differ and inverse to original source bytes.
- Actual0584 numeric guard and all original unrelated-body/signature/state
  mutations pass on both roots. Four actual inherited fixture-copy functions
  (0583foreach,0585tensor,0586host,0587partial) execute and their real F05 guards
  pass for origins with either operator shape. Those old copies intentionally
  do not include TypeChecker;this is not a claim that they copy its new owner.
- Missing/changed/duplicate successor/context/factory/alias/import and changed
  readonly/carrier/evidence negatives are present. Original old fixture hashes,
  readonly counts22/29/39 and numeric-mask assertions are unchanged.
- O02/O03/O05:domain/resource boundaries,live state,successful and exceptional
  restoration,ordered binary/index/call callbacks and neighboring accepted forms
  are mapped to named tests in the trace;R1 prevents full O04 acceptance.
- O06/O08:real aliases,variadic custom forwarding,instance/subclass overrides,
  unbound `self=`,plain bound/Ty pickle,cold requested imports and actual source/
  finite/Set/register/module/HIR consumers are exercised. Not whole dynamic
  import-graph,arbitrary pickle or exhaustive past-deletion evidence.
- O10:phase separation and exact bytes are visible;no exclusions/old fixture
  refresh/claim of final committed Green. No spec change is needed for R1.

## Verification / comparison

External evidence:`/private/tmp/liss-0590-review.CLg6Ys/` with command/cwd,
SHA/dirty state,start/end UTC,exit/environment and stdout/stderr per label.
macOS27.0.1 arm64,CPython3.12.6,pytest9.0.3;repo root/PYTHONPATH root;
SHA/base b5c96f7e4c2a846f41ac8ad5d882f0cb987cd420,dirty tests/docs.

- Fresh focused:97PASS/4expected structural failures,7.51s;no errors/skips/
  exclusions. Same4IDs as author run;R1 is a false-positive case,not a fifth
  pytest failure. Expected missing owner/context/body removal/factory unimplemented.
- Fresh inherited:162PASS12.02s. Fresh combined adjacent/consumer:90PASS0.90s;
  fresh spec161/161PASS.
- Fresh independent-probe:Git method/AST/two constructor sites,strict pre/post
  raw inverse,original guard mutations,eight real copy-fixture invocations PASS;
  two profiling traces reproduce R1. No proposed production algorithm executed.
- Audit:exact16artifact fingerprint and221unchanged production files PASS.
- Full root **not rerun in this reviewer turn**:read author's actual root JSON/
  output,2918PASS/4same expected failures358.27s at the same unchanged artifact
  fingerprint. Historical source-clean sanity9PASS/1FAIL(uncommitted inventory
  TSV);current metadata checks recorded in trace. Neither is full Green or
  actual-final-commit evidence. Comparable whole-root baseline rerun unavailable.
- New/resolved runtime failures:none in the rerun scoped suites versus author
  results;unassessed broader baseline/dynamic coverage remains explicit.

## Structure / effective route / lessons

`review-change.py --base b5c96f7e --head HEAD` records committed diff0 and
**unknown dirty-tree measurements**;0 is not the actual pending change size.
Exact dirty test inventory comes from audit instead. Live TOML has same_context/
host,empty model IDs and no enabled large_change or numeric structure settings;
same_context applies without inventing a lower isolation. No unavailable
required isolated review was waived. Test modules63–245lines/helper234;functions
under150lines. Original281-line cohesive-body disposition remains accepted for
future implementation;no facade reduction claimed. Full graph/semantic-owner
metrics remain unknown.

Applied lessons:immutable guard provenance,actual pre/post setup,minimum-case
reconciliation,private consumer/identity/public exports,live state,explicit
external PYTHONPATH,structural Red separation,status sync and final-SHA rules.
R1 reuses the red-fixture-interface lesson:prove the failure reaches its named
boundary before calling it acceptance evidence. Recorded in live lesson log.

## Review Target / next gate

- Current phase:Phase1 Red review;outcome changes_requested,not accepted.
- Approved scope:this review only;tests/source/fixtures remain unchanged.
- Requested approval:**LISS-0590 Phase 1 Red R1テスト限定修正／再レビュー**。
- Approval type:phase (bounded Phase1 test correction),not implementation.
- Implementation allowed:no. Post-review required:yes,corrected exact-test
  review,then human test acceptance and separate Phase2 approval. Batch:N/A.
- Blockers:R1 correction;later committed source-clean/full blocking gates.
- Adjudicator checklist:confirm named-site correction,unchanged runtime/old
  guards and scope,review isolation/evidence limits,and separate acceptance.
- Decision:human pending;do not request acceptance of the current false-positive
  case or proceed to Phase2. No new ADR/technology choice required.

## Evidence links

- Representative [trace / handoff](../traces/2026-10-15-liss-0590-typechecker-operator-body.md).
- Canonical Register:not changed;this is derived review evidence,not a new rule.
- Detailed evidence:external independent-probe.out/json,focused,inherited,
  adjacent-consumers,spec,audit,routing and metadata checks under named directory.

## R1 authorized correction / re-review (current)

Adjudicator explicitly approved **LISS-0590 Phase 1 Red R1テスト限定修正／再レビュー**。
Author corrected only `tests/test_liss_0590_operator_behavior_red.py`,then
froze tests and switched to reviewer. Same_context remains weaker than isolated
review;no model override/large-change configuration or new permission inferred.

**R1 disposition:already closed with evidence.** No remaining agent-review
findings for this bounded correction. No source semantic defect repaired.

- Remove the two misdirected factory parameter cases from the generic exception
  test;all other generic cases/assertions are AST-identical under that deletion.
- Add `operator_type_sites` and the exact new node
  `test_o04_factory_failure_reaches_named_operator_site` (O04/O03).
  TypeRef's prerequisite conversion returns a preconstructed real Ty;IndexDomain
  uses the real operator's first/second constructor sites separately.
- Eighteen cases:three path/failure-position combinations × RuntimeError/Abort
  × absent/None/real-Ty prior binding. Assert exact same exception instance,
  actual algorithm code/call line and argument tuple,ordered callback/count
  evidence,no body/rank entry,unchanged original env mapping/content/identity
  and pre-existing depth2. The None-valued key remains on these pre-binding
  failures;this does not change the successful-restoration pop contract.
- Call sites derive from the actual method AST,not frozen future line numbers;
  the probe distinguishes a direct old Ty call from the accepted one-frame
  fresh-Ty factory after a later authorized move. No future algorithm executed.
- Independent reviewer profiling observes all18cases at original Git sites1493
  and/or1657,never the prior `_semantic_ty_from_ref` site. Two test-only negative
  controls remove conversion isolation or suppress the injected exception;
  both are rejected (wrong-callback assertion / DID NOT RAISE),not false PASS.
- Independent original-Git/pre/post inverse/real numeric guard and eight
  inherited-copy fixture checks still pass. No helper/carrier/fixture change.

Current exact16-test-artifact SHA256:
`12426ae6b89a222a40eb0cf25f66cdbe018cc786d7ae75c1b5477d168dfbed3b`.
Corrected behavior SHA256:
`b32dae02ae0dac82f5402e1c861a44055fe4b04db0fcf00698305af00abde5f3`.
Scope audit compares to the saved pre-correction file and entry fingerprints:
**only behavior.py changed;other15test artifacts unchanged;all221production
files unchanged**. Remaining behavior AST unchanged. No exclusions/old hashes
or accepted O01–O10 clauses weakened. Original101nodes minus2misdirected nodes
plus18corrected nodes =117nodes;the16additional passing cases are not a runtime
feature. Expanded exact IDs:external collect.out.

External current evidence:`/private/tmp/liss-0590-r1.Fcvuau/` (run.py captures
command/cwd/SHA/dirty/env/UTCtime/exit/out/err). Same source SHA/baseb5c96f7e,
macOS27.0.1arm64,CPython3.12.6/pytest9.0.3,PYTHONPATH repo root.
Fresh focused113PASS/4same expected ownership Reds8.20s;R1 exception subset
30PASS0.47s,reviewer rerun30PASS0.48s (54deselected by explicit -k selection,
not an approved root exclusion). Inherited162PASS12.12s;adjacent-consumer90PASS
1.01s;spec161/161PASS. No errors/skips or root exclusions. Current full-root
and final metadata results are recorded in the representative trace.

Fresh corrected full-root:2934PASS/4same expected ownership Reds351.71s,
exit1,no errors/skips/exclusions. Compared with old2918PASS,the+16matches the
new test inventory;failure IDs match exactly. Fresh sanity9PASS/1copy-smokeFAIL
(uncommitted inventory TSV),PR-only check N/A locally. Full Green/final-SHA
completion is not claimed. All results use the corrected fingerprint above.

Structure:behavior316physical lines,longest top-level function46lines;new
helper/test remain one operator-behavior responsibility in the approved file,
with separately named failure scenarios. Live numeric thresholds unset;retain
cohesive test family rather than expand file scope. Other suites/helper remain
63/89/104/234lines. Unknown full dynamic graph/semantic metrics unchanged;
dirty committed-diff0 from review-change.py is not actual pending change size.
No missing required isolated review downgraded. Existing failure-boundary lesson
is now applied with actual site/count and negative-control evidence.

### Accepted Phase1 Review Target

- Current phase:Phase1 Red corrected-test re-review,agent pass;human acceptance received2026-10-16.
- Artifact:current exact16-artifact fingerprint,117nodes and this re-review.
- Subsequent Phase2 approval received2026-10-16;current next gate is in Phase2 verification.
- Approval type:phase/test acceptance (received). Approved scope:corrected Phase1
  exact tests/re-review. This acceptance alone did not authorize implementation.
- Post-review required:yes,Phase2 then separate review/final verification gates.
  Batch:N/A. Human corrected-test decision:accepted2026-10-16;Phase2 separately approved.
- Remaining blockers:current Phase2 source-clean/actual-SHA verification;
  eventual source-clean/copy-smoke and actual-final-SHA full-blocking gates.
  Current expected Red and uncommitted inventory TSV do not mean full Green.
- Checklist:confirm correct failure sites,unchanged old evidence/state behavior,
  scoped artifact bytes,review isolation limits and separate future gates.

Human acceptance records the current corrected16-artifact fingerprint above,
not the historical initial fingerprint. No runtime/test/fixture edits accompany
this acceptance;Phase2,commit and remote delivery are not inferred approvals.

Later Phase2 execution/implementation explicitly approved and performed2026-10-16.
This Phase1 acceptance remains historical authority for unchanged test bytes;
current implementation/final-SHA gate is owned by [Phase2 verification](2026-10-16-liss-0590-phase2-verification.md).
No Phase3 or delivery approval follows from either this test review or CI.
