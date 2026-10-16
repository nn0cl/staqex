# LISS-0590: TypeChecker operator判定本体の分離

## Metadata

- Local issue ID:LISS-0590
- GitHub issue:none
- Status:review — Phase2 implementation/local verification record;actual-SHA results external,Phase3 unapproved
- Phase:phase-2-green
- Type:behavior-preserving body extraction
- Priority:WP0175 first candidate,operator walk only
- Initial/current planning size:L/L;reclassification:none
- Owner:Codex host / Adjudicator
- Branch:codex/liss-0590-typechecker-operator-phase0
- Specification:[O01–O10](../specs/typechecker-operator-body-successor.md)
- Planning record:AIP-0590-001 (accepted2026-10-16)

## Scope / dependencies

Scope/Phase0 design-start explicitly approved2026-10-15. Parent WP0175 inventory
I01–I08 accepted;depends on that accepted design and delivered source main
b5c96f7e4c2a846f41ac8ad5d882f0cb987cd420. Parent's five approved/uncommitted
design documents are carried intact on this dedicated branch;they are not
committed baseline evidence. No commit/remote delivery approval inferred.
LISS0546 family API and LISS0584 numeric repair remain accepted predecessor
contracts,not reopened implementations. No global blocker from WP0175's two
unrelated missing-callback bugs;do not repair them here.

Dedicated Issue/spec O01–O10,limited four-carrier guard policy and Phase0
explicitly accepted2026-10-16. This accepts the scoped factory/alias/type
boundary and281-line cohesion disposition,not test creation/guard edits or
implementation. Original scope/design-start date2026-10-15 remains unchanged.

In:sole281-line `_legacy_check_operator` body,existing operator family boundary,
ordinary private aliases,small original-Ty constructor callback,new narrow
declaration-only context and exact four-carrier guard design. Out:other checker
bodies,Ty relocation,Parser,Unitary pass,Rust,behavior/exception cleanup,
additional test carriers,old manifest/hash refresh and implementation.

## Observations / acceptance mapping

- Base typecheck:4690 physical lines;method1487–1767=281. File hash
  `917279f48ecb0ff4be1cdce6728b2046d1931bb5b3fc71aa76bb05f1ce58b0ca`;
  full method AST `63f70dd610d3714f3bb10ce579b4b166acbe963bcf048c18b128f2357bbc3599`.
- Static self dependency inventory:13 existing names (7 state fields and6
  callbacks). Exactly2 Ty constructor calls. New narrow context adds only the
  pure fresh-Ty factory,no second state owner. Detailed signatures/contract in spec.
- O01/O07:actual body ownership and unchanged restored facade/public names.
- O02/O05:ordered domain/tree checks and diagnostics;not mathematical policy repair.
- O03/O04:live state and successful/exceptional ordering,including env not
  restored after a raised body/rank callback while depth is decremented.
- O06/O08:real private alias/public forwarding/pipeline/HIR behavior and import/
  ordinary bound pickle evidence. No arbitrary serialization/graph proof inferred.
- O09:0584numeric AST boundary plus0587/88/89typecheck byte guards;0589also
  pins0588ownership test bytes. Only four named test carriers accepted for
  separately approved Phase1 execution.
- O10:exact accepted tests and actual-final-SHA full blocking/routing gates.

Minimum cases and guard policy have one canonical definition in the spec;
Phase1 will map each to exact named nodes,not claim a future suite already exists.
No tests written or changed during this Phase0.

## AI planning — AIP-0590-001

- Status:accepted2026-10-16 with dedicated O01–O10/guard/Phase0 acceptance;
  created2026-10-15,Codex desktop host;scope/estimates unchanged.
- Initial/current size:L/L. Cross-file body/type boundary and four inherited
  guard carriers plus behavior/private state compatibility require broad verification.
- Intended route:host design/implementation only when separately approved;
  review.same_context/weaker,model IDs empty,no enabled large-change override.
- Model/reasoning as displayed:N/A,stable identifiers not exposed to this record.
- Estimate token range/midpoint/metric:N/A,no calibrated estimator. Actual usage/
  source/variance:N/A,unavailable. Not an ETA or delivery promise.
- Intended scope:O01–O10 only,source frozen atb5c96f7e and parent design accepted.
- Assumptions:Ty stays in facade;fresh-Ty callback avoids reverse import;
  live owner and ordered recursion preserved;no new architecture premise.
- Confidence:high for source/guard inventory,medium for strict raw-source guard
  inverse until pre/post Phase1 setup probes,unknown for exhaustive dynamic graph.
- Revisions/superseded by:none. Re-scope instead of expanding allowed paths if
  another inherited guard/copy conflict or required type relocation is discovered.

## Verification / approval

Read-only static consumer/AST/manifest audit and existing focused baseline
execution are recorded in [trace](../collaboration/traces/2026-10-15-liss-0590-typechecker-operator-body.md).
No proposed runtime implementation,Phase1 tests or complete local blocking run
executed in design phase. Prior main CI is baseline evidence,not current dirty-doc Green.

Human approval received2026-10-16:dedicated Issue/spec O01–O10,bounded four-carrier
guard policy,factory/alias/type boundary and Phase0 acceptance. Current approved
scope:accepted design only. Implementation allowed:no. Post-review required:yes,separate Phase1
execution then exact test acceptance,Phase2/review/final/commit/delivery gates.
Batch:N/A. No technology selection or new ADR accepted by agent judgment.
The Phase1 execution gate above was explicitly approved2026-10-16. Current
state supersedes the historical Phase0-only statements:Phase1 tests/scaffolding
and exactly four approved carriers changed;production remains byte-unchanged.
Next gate: **LISS-0590 Phase 3 Refactor／review承認** only after actual-SHA all-blocking PASS.
Exact-test acceptance and Phase2 implementation approval remain separate.
Process review:not yet,Issue is review/not done. Existing body-ownership,
private-consumer,immutable-guard,live-state,typed-approval and final-SHA lessons
applied;no new rule/lesson written for this scoped design.

## Phase1 author evidence —2026-10-16

Four new suites:`test_liss_0590_operator_{behavior,consumers,ownership,guard_migration}_red.py`,
new test-only helper and seven immutable fixtures under `tests/fixtures/liss_0590/`.
Original method/carriers are pinned to b5c96f7e,not regenerated successor evidence.
Only0584repair and0587/88/89ownership carriers changed;old expected hashes,
fixtures,counts and mutation assertions are unchanged. No fifth carrier edit.

Focused:97PASS/4expected structural Red;inherited162PASS;adjacent36PASS;
consumer/numeric49PASS;Set-binder5PASS;spec161/161PASS.
Full root:2918PASS/4expected structural Red,358.27s;no errors/skips/exclusions.
Repository sanity9PASS/1FAIL(copy-smoke:
pre-existing uncommitted inventory TSV);PR-only traceability N/A locally.
No skips/exclusions in focused suites. Full root result and exact artifact
fingerprint/clause-node mapping are in the representative trace below.
All evidence is dirty-tree b5c96f7e,not final committed Green. Source audit:
all221production files exactly match base. No commit/push/PR/merge performed.
This is an author handoff,not an agent review pass or human test acceptance.

## Phase1 test review —2026-10-16

[Review summary](../collaboration/reviews/2026-10-16-liss-0590-phase1-test-review.md):
same_context/weaker review **changes_requested**. R1[P2]:factory-exception
cases inject into global Ty but fail earlier in `_semantic_ty_from_ref`,before
the intended operator constructor/future factory. Both exception classes were
profiled;test PASS is not evidence that this O04 minimum scenario executes.
Disposition:apply,pending bounded Phase1 test correction and re-review approval.
No test/source/fixture changes in review;exact16-artifact fingerprint unchanged.
Fresh focused97PASS/4expected Red,inherited162PASS,adjacent-consumer90PASS,
spec161/161PASS;independent Git/pre-post/actual copy-fixture checks PASS.
Full root not rerun in review;author run above remains dated evidence,not Green.
Human acceptance/implementation/commit/delivery remain unapproved. Issue not done.

## R1 authorized correction / re-review —2026-10-16 (current)

Explicit bounded Phase1 correction/re-review approval received and executed.
Only behavior.py changes among16test artifacts:replace2misdirected cases with
18named-site cases across3paths/2failure types/3prior bindings. Record actual
algorithm code/call-site/count,callback order and unchanged env/depth at failure.
Independent18-case profiling and2rejecting negative controls PASS;R1 closed in
agent re-review,same_context/weaker. Remaining15artifacts and221production files
unchanged. No accepted O01–O10/old hash/fixture/carrier changes or exclusions.
Focused113PASS/4expected structural Reds;inherited162PASS;adjacent-consumer90PASS;
spec161/161PASS. Current root/all-sanity results and exact corrected fingerprint
are in trace/review. No full Green or human acceptance claimed;no implementation,
commit or delivery performed. L/L,AIP0590-001 unchanged;Issue remains review.

Corrected full-root2934PASS/4same expected Red351.71s;no errors/skips/exclusions.
Fresh sanity9PASS/1copy-smokeFAIL(uncommitted inventory TSV),not full Green.
Current exact16-artifact fingerprint:
12426ae6b89a222a40eb0cf25f66cdbe018cc786d7ae75c1b5477d168dfbed3b.

## Corrected Phase1 human acceptance —2026-10-16 (current)

Adjudicator explicitly accepted **LISS-0590 Phase 1 Red 修正済みテストレビュー／acceptance**。
Accepted artifact:exact16test artifacts/fingerprint12426ae6... above,117nodes,
R1 corrected exception-site evidence and agent re-review. R1 remains closed.
This accepts the test boundary,not Phase2 execution/implementation,commit or
delivery. Source/tests/fixtures unchanged in this metadata-only acceptance turn.
Current state:ready/phase-1-red accepted,awaiting separate Phase2 implementation
approval. Post-review required:yes,later Phase2/Phase3/final verification gates.
Copy-smoke/uncommitted inventory TSV and final-SHA full blocking remain gaps,
not exclusions or waived failures. Issue not done;planning size L/L unchanged.

## Phase2 implementation —2026-10-16 (current)

Explicit Phase2 Green/implementation approval received and executed within
O01–O10. Three production files only:operators.py sole281-line body,new39-line
operator_context.py,typecheck.py ordinary alias/fresh-Ty factory. TypeChecker
4690→4416lines,operators310;no duplicate algorithm/state owner or reverse import.
AST against original Git matches under exactly approved normalizations;facade
raw inverse matches original bytes;219other production files unchanged.
Accepted16-test-artifact fingerprint12426ae6... unchanged;no tests/fixtures/
carrier assertions or exclusions modified. R1 remains closed.

[Phase2 verification](../collaboration/reviews/2026-10-16-liss-0590-phase2-verification.md):
focused117PASS,inherited162PASS,adjacent-consumer90PASS,spec161/161PASS.
Full-root2938PASS362.93s,no errors/skips/exclusions;all4structural Reds resolved.
Current source hashes in verification/trace. All-blocking not
Green:repository-sanity copy-smoke still fails on inherited uncommitted inventory
TSV. No waiver,commit or remote action. Phase2 completion/final-SHA verification
remains pending;next separate permission is local commit/all-blocking rerun,
not Phase3. Proposed commit cohort explicitly bounded in verification record.
L/L,AIP0590-001 unchanged;Issue not done. Phase3/final review/delivery unapproved.

## Authorized local commit / actual-SHA verification —2026-10-16 (current)

Explicit local commit/full-blocking rerun approval received for the declared
30-file cohort (3production/16accepted test artifacts/11related records).
No source/test changes in this step;accepted digest12426ae6... and production
hashes match Phase2 verification. Record prepared before commit;actual tested
SHA,clean-tree evidence and post-commit outcomes are stored outside the tree at
`/private/tmp/liss-0590-sha.v0SnLA/verification.json` and per-command JSON/logs.
Do not infer a PASS from this planned reference;read the actual SHA record.

Issue review/phase2-green,not done. Once root/spec/all applicable sanity pass
on the clean actual commit,the next approval is Phase3 Refactor/review. A failed
required run remains blocking instead. No Phase3 work,push,PR or merge authorized.
No evidence-only commit after verification;any later HEAD change requires reruns.
