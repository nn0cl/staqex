# Scientific Semantic pure-family body migration — accepted F01–F10

Status: F01–F10/limited guard policy and Phase0 explicitly accepted2026-10-22
JST. Phase1 Red and subsequent R1 test-only correction/re-review explicitly
authorized. R1 relation-field cases and N1 mixed inspection input added;agent
re-review closes both. Corrected focused252:243 PASS/9 Red,inherited431 PASS/
2 path-guard failures,adjacent28 PASS,spec161 PASS;root3495 PASS/11FAIL.
Prior3503 node IDs retained plus3 PASS;failure IDs unchanged,error/skip/excluded0.
Human corrected-test review/acceptance explicitly approved2026-10-22 JST for
cohort496c5d8a…116c1c and the [current re-review](../collaboration/reviews/2026-10-22-liss-0593-phase1-r1-review.md).
Phase2 Green/implementation subsequently explicitly approved and exact reviewed
three-source/three-carrier changes applied. Focused252 PASS,but inherited433
has2 new guard-consumer failures (message compatibility and synthetic inventory);
Green not achieved. Root3506:3504 PASS/2 FAIL,same two new inherited failures;
all prior11 failures resolved,no test IDs removed,error/skip/excluded0. Copy smoke also
refuses the uncommitted distributed spec. Supplemental guard-consumer Scope/
Phase0 design subsequently approved;G01–G09/2-file repair policy and supplemental
Phase0 explicitly accepted2026-10-23 JST;that acceptance did not authorize Red.
Supplement Red subsequently authorized2026-10-23 JST;append-only composition
tests authored/executed. Focused335:330PASS/5live-contract Red;root3589:
3582PASS/7FAIL (5new+2adopted),original3506nodes retained plus83,error/skip/excluded0.
Live helper/caller,production,pure-family tests and fixed evidence unchanged
during Red. The original composition231line prefix/assertions remain intact.
Adjudicator explicitly accepted the reviewed supplement Phase1 Red cohort
`cb85f98ae0752650b6dac5ff494ee6967586c74c58395ca3b3a24a0a78b8851c` on
2026-10-23 JST. Agent review packet:
[LISS-0593 supplement review](../collaboration/reviews/2026-10-23-liss-0593-supplement-phase1-review.md).
This is Phase1 test acceptance only;repair Green/implementation remains
unauthorized pending separate approval. Phase2 implementation subsequently
approved and applied to the two named guard helpers. Focused335,inherited433,
adjacent28,root3589,spec161 and compileall pass. Repository sanity has one
source-clean copy-smoke failure because this dedicated spec remains uncommitted;
therefore no full all-blocking Green claim. Evidence:
`/private/tmp/liss-0593-phase2-20261023-result.json`.
Accepted F01–F10 clauses are unchanged;no failure waiver or Phase3 authority.
Owner: [LISS-0593](../issues/LISS-0593-scientific-semantic-pure-family-batch.md).
Parent: [WP-0175](../work-plans/WP-0175-source-responsibility-inventory.md).
Baseline: `103fba434ab01db5534981bd5784d833a457b222`, 2026-10-22 JST.
Authority: accepted [core decomposition](staqex-core-module-decomposition.md).

## Purpose and bounded candidates

Make each selected responsibility readable without opening the 1,803-line
Scientific Semantic legacy implementation. Total line reduction is not a goal.
Do not delete compatibility imports, redesign types, or fix unrelated behavior.

| Unit | Original function / lines at baseline | Sole implementation destination |
|---|---|---|
| A: identity | `semantic_fingerprint`, 294–360, 67 physical lines | existing `scientific_semantic/fingerprint.py` |
| B: read-only views | `build_inspection`,1544–1552,9 lines; `build_rejection`,1555–1564,10 lines | existing `scientific_semantic/builder.py` |

Scope: three functions, 86 definition-span lines; no new production file.
These are lower-risk product candidates, not a claim that their guard migration
is already safe. Units share the same legacy compatibility and guard boundary
and form one Issue; they remain separately characterized and reviewable.

AST inspection: fingerprint uses ScientificSemanticIR, hashlib and json;
views use existing model constructors and Any annotations. None mutates shared
state or calls the legacy builder, runtime, provider, or a sibling algorithm.
Builder's unrelated `build_scientific_semantic_ir` wrapper must retain its
behavior; a local legacy import there can avoid an eager builder/legacy cycle.
Keep annotations and observable wildcard exports at existing module paths.
Retain legacy imports even if locally unused when they form exported names.

## Accepted acceptance F01–F10

| ID | Requirement / minimum evidence |
|---|---|
| F01 | Move the three complete algorithms, including literal/comment/order content, to the destinations above. Legacy retains compatibility bindings, not duplicate algorithms. Compare raw Git bodies as well as AST. |
| F02 | Fingerprint retains complete payload fields, node/relation/operation order, None handling, JSON sort_keys/separators/default=str, UTF-8 and SHA256. Test populated and empty models, independent mutations of every serialized field, and unchanged failure behavior; compare with baseline execution. |
| F03 | Inspection retains node order, role-lane stable deduplication, dimensions and all/empty exactness. Rejection retains None for empty diagnostics and first-code/default conversion, node IDs, spans and message_key; test empty/populated/duplicate/malformed inputs against baseline. |
| F04 | Preserve callable signatures, public/private import paths, wildcard names, model class/object identity and results. Cover public facade, family and legacy paths; record scoped pickle/import compatibility and its limits, not whole-repository proof. |
| F05 | Destinations own the algorithms without importing the public facade or importing legacy to execute the moved algorithms. Preserve builder's unrelated wrapper via an explicit local import if needed. Run cold import orders and resolved eager/lazy dependency audit. No new persistent state, dependency or authority. |
| F06 | Outside the three approved production files, bytes remain unchanged. Preserve all non-target declarations and existing exported imports in those files; only reviewed binding/import wiring changes. Freeze baseline files/raw bodies from Git; never regenerate historical manifests to accept a move. |
| F07 | Compose existing frozen-source readers through an exact test-only inverse for these three files. Validate actual requested-file existence and the complete authorized post-shape before restoring baseline bytes. Preserve raw newlines, comments and unrelated bytes. No blanket path exclusion or arbitrary AST normalization. |
| F08 | B06's current no-project-import test on the 0591 inverse requires explicit disposition: permit only a named pure test-inverse dependency and recursively verify its stdlib-only closure, no compiler imports and no exec/eval/compile. Preserve the existing parser inverse checks. This is a proposed test-contract supplement, not a silently approved exception. |
| F09 | Exercise real 0590/0591 readers, frozen-production loops and 0592 consumers on distinct pre/post copied roots. Pair positives with missing-file, raw newline/comment/body/order/wiring/extra-import mutations and unrelated source/test mutations. All old assertions retain their original protection via an independently verified inverse. |
| F10 | Human accepts reviewed Red tests before implementation. Focused/consumer/adjacent and all-blocking verification are separate; rerun every blocker after final commit, preserve SHA/environment/IDs/results externally, and require Phase3/human final review and separate delivery approval. |

## Consumer and guard inventory

- Public `scientific_semantic_ir.py` imports the family entrypoints. Existing
  pipeline uses both views at `pipeline_legacy.py:935,974,1048,1049`.
- Fingerprint consumers: qpu_ir, physics_ir_lower, symbolic_ir,
  runtime/evaluator, QASM emitter, realization_artifact and semantic tests.
  Read old/family/private legacy paths too; static search is not proof of every
  dynamic consumer or runtime monkeypatch contract.
- 0590,0591,0592 baseline manifests freeze all three target files. Existing
  0590 ownership reads through its readonly_bytes; 0591 P10 currently reads raw
  bytes directly; 0592 boundary uses the 0591 reader. All must exercise the
  same bounded validation, not bypass their assertions.
- Proposed carrier allowance, only after reviewed Red acceptance:
  `tests/liss_0590_guard_support.py`, `tests/liss_0591_guard_support.py`,
  `tests/test_liss_0591_ownership_red.py`. Changes limited to reader dispatch,
  exact historical-carrier/path composition and F08's explicit closure check.
  Add new `tests/liss_0593_guard_support.py` (stdlib-only raw inverse),
  `tests/test_liss_0593_pure_families_red.py`,
  `tests/test_liss_0593_guard_composition_red.py`, and immutable evidence under
  `tests/fixtures/liss_0593/`. Existing baseline hashes/fixtures stay untouched.
- If these three carriers cannot preserve every inherited assertion/copy
  consumer, stop and revise scope; do not discover-and-edit further carriers.

Phase1 interpretation:the three existing carriers remain unchanged until Red
acceptance,as required above. Red may author the exact proposed substitutions
as test-only data and execute TEST plumbing on copied roots;it must not import
or execute the proposed production shape. No new active-Red exclusion.

## Accepted scenario interpretation / Red matrix

These Given/When/Then scenarios unpack F01–F10 without changing their clauses.
Given immutable baseline103fba43 and its existing DTOs/consumers,when the three
functions are called or their sole-owner/import contracts are checked,then
their original behavior/imports persist and only the named owners hold bodies.
Given distinct pre/post raw copies and each real frozen-source reader,when a
valid copy is read,then original bytes are recovered;when a file/body/comment/
newline/wiring or unrelated artifact changes,then the inherited guard rejects
it. Data/state stay owned by the existing model/context;no provider is involved.

| Clause | Phase1 evidence / test names |
|---|---|
| F01/F05 | `test_f01_f05_sole_owner_contains_the_complete_original_algorithm` (3 intended structural Reds),cold consumer imports,whole-source shape check |
| F02 | `test_f02_*`:empty/populated,each serialized core/node/relation/operation/realization field,including `test_f02_each_serialized_relation_field_is_preserved[kind/node_ids]`;sequence/projection boundary,JSON/default/hash bytes,circular/malformed inputs |
| F03 | `test_f03_*` and malformed boundary:order/stable lanes,empty/all exactness,mixed-lanes-exactness-dimensions input,first/default diagnostic,spans and shared tree identity |
| F04 | `test_f04_*`:actual wildcard/signatures/model identity,baseline callable pickles,cold imports through actual consumers |
| F06 | other production path/hash inventory,original Git evidence/raw algorithms and non-target declarations |
| F07 | `test_f07_*`:both actual staged readers,intact/missing sibling artifacts,exact pre/post raw validation and carrier inverse |
| F08 | closure positive plus transitive compiler/test/relative import and exec/compile/dynamic-import negatives |
| F09 | `test_f09_*`:6 live-reader integration Reds until carrier acceptance,staged pre/post real readers/frozen loops/0592 cohort,source/test mutation controls |
| F10 | readonly phase boundary,unaltered prior assertions/fixtures,no exclusions,and explicit phase/evidence records |

## Declared commands and evidence

cwd repository root;Python3.12 with existing pytest/numpy/PyYAML;full Git
history required. No new dependency or pytest exclusion. Capture SHA,dirty
state,environment,times,exit,JUnit counts/IDs outside Git.

- focused:`python3.12 -m pytest tests/test_liss_0593_pure_families_red.py tests/test_liss_0593_guard_composition_red.py -q`.
- inherited:`python3.12 -m pytest tests/test_liss_0590*.py tests/test_liss_0591*.py tests/test_liss_0592*.py -q`.
- adjacent:`python3.12 -m pytest tests/test_liss_0448_coin_mix_semantic_red.py tests/test_liss_0476_symbolic_ir_consumer_migration_red.py tests/test_liss_0488_physics_ir_canonical_projection_red.py tests/test_liss_0458_realization_artifact_contract_red.py tests/test_liss_0548_scientific_semantic_ir_red.py -q`.
- root:`python3.12 -m pytest tests/ -q` (active-Red ledger currently empty).
- spec:`python3.12 tests/spec_verification/run_all.py`.
- Green/final also require full repository-sanity workflow commands,compileall,
  raw/export/import closure audit,effective routing and document checks under
  the previously declared full-blocking profile. Not all are Red exit claims.

JUnit arguments only add external diagnostic artifacts. During Red,report the
three ownership gaps and six live-carrier integration gaps separately from
old guard test-path failures caused by adding the approved new tests. All
remain visible blockers for Green;no assertion or old baseline is relaxed.

## Proposed execution envelope, not an approved batch record

- Proposed ID: `BATCH-0175-A`; Issue set: LISS-0593 only.
- Design branch: `codex/liss-0593-pure-semantic-batch-design`.
  Execution branch after explicit bounded-batch approval: `batch/BATCH-0175-A`.
- Allowed production: only `compiler/staqex/scientific_semantic/{legacy.py,
  fingerprint.py,builder.py}`. Tests limited to the named carriers/additions.
  Documentation limited to this spec, Issue, representative trace, WP-0175,
  and this batch's review/verification records.
- Proposed operations: exact body migration, compatibility wiring, approved
  test-only guard composition, characterization, verification and record sync.
  Proposed phases: Red, Green, Refactor, each still subject to its distinct
  human gate; a batch record never pre-accepts unwritten tests.
- Expiry proposal: seven days from explicit batch approval. Approval commit,
  timestamp and actual expiry are not assigned yet. Create execution JSON
  only after approval; do not label this proposal approved_for_execution.
- Stop on changed behavior/output/signatures/exports, DTO relocation, authority
  or state-owner changes, new dependencies/cycles, guard weakening, extra
  paths/functions, unknown consumers or new regressions. No source rewrite,
  bug repair, architecture/policy change, commit/push/merge permission inferred.
- Post-review required: yes. Host implementation, same_context agent review
  under current routing, human phase/test/final acceptance remain distinct.

## Verification plan

Before Red, record exact commands/cases and complete clause-to-test matrix.
Focused: both families, each consumer path and pre/post guard controls above.
Adjacent: canonical Coin/Mix/semantic consumers, physics/QPU projection,
realization and existing 0548/0590/0591/0592 contracts. Full blockers:
root pytest with declared active-Red selection, spec verification, repository
sanity workflow, compileall, scoped import/export/raw-body/guard audit,
document lifecycle, coverage ledger, whitespace and effective routing.
Full history is an execution prerequisite. No new exclusion is approved.

Phase0 is design/static inventory only; fresh baseline checks are recorded in
the trace. This document is not an all-blocking Green or complete test review.

Historical initial Phase1 evidence:/private/tmp/liss-0593-red-20261022.Sv1yMV/result.json;
original cohort8ebc79765ab51be5fa9a4032d6958f07ef85913c3a33b7382b27cc509b4fe52d.
Authorized R1 correction/re-review evidence:/private/tmp/liss-0593-r1-20261022.7b3vun/;
corrected cohort496c5d8a11a57a6ce2c42262812d684dcb8f99a2c2e015cd0eb027486a116c1c.
Current existing-test-path Reds are0591 P10 and0592 R06 test-cohort validation;
the approved proposal must pass both after its separately authorized application.
They remain blocking;historical hashes/fixtures and exclusions are unchanged.

## Guard-consumer supplement G01–G09 — accepted Phase0

Scope/design start explicitly approved2026-10-22 JST after the exact accepted
Phase2 move exposed two additional inherited consumers. G01–G09/2-file repair
policy and Phase0 explicitly accepted2026-10-23 JST;table SHA256
56d9c156baa4647b0329d2fb36fd36614d1ad4d9d2726db421f81763fc55498c.
Red execution subsequently explicitly authorized2026-10-23 JST;helper/caller
repair was unauthorized at that checkpoint. The separately approved Phase2
implementation is recorded below. This supplement does
not rewrite accepted F01–F10 or declare current implementation Green. It is
a test-guard compatibility specification under the same Issue,not a new
runtime boundary or architecture/technology decision. No new ADR is needed
for this bounded test-only proposal. No implementation permission yet.

### Preconditions / cause / boundary

Given original Git103fba43,accepted corrected cohort496c5d8a…116c1c and the
installed six-file Phase2 shape pinned in authorized-shapes.json,when the
unchanged0591 B04/B05 and B08 tests run,then two failures reproduce:

- B04/B05's valid old-carrier positive passes and mutation is rejected,but
  the0593 inverse raises `unauthorized carrier edit` before the0591 caller's
  required `unapproved carrier change` diagnostic.
- B08's synthetic positive uses public NEW_TESTS/NEW_FIXTURES containing only
  0591 additions (6Python+10fixtures). The actual predicate separately unions
  0593's3Python+7fixtures,so the fixture fails before extra/missing negatives.

These are different contracts from raw byte projection. Preserve both existing
test functions byte-for-byte;do not edit a regex or bless missing real files.
Production's already-moved3 algorithms/DTOs/imports stay fixed. The source-clean
copy-smoke refusal is separate and must not be waived by this supplement.

### Selected design / alternative disposition

1. Make the caller's rejection diagnostic explicit via a keyword-only
   `rejection_message` parameter on the0593 historical-carrier inverse. Keep
   its existing default;the0591 historical_test_bytes caller passes its exact
   original diagnostic. The membership predicate and actual-file read stay
   identical. Do not catch arbitrary AssertionError or translate missing-file/
   evidence errors,which would obscure unrelated failures.
2. Make0591's exported NEW_TESTS/NEW_FIXTURES describe the same composed known
   additions that its strict predicate already requires. Derive each union
   from the original0591 literal set and the named pure0593 helper's respective
   constant,using private import aliases. No new path,permissive subset check,
   duplicated hardcoded inventory or compiler import. Keep explicit real0593
   artifact existence validation even though its union is algebraically redundant.

Static equality checked:old6+10 plus semantic3+7 gives26 additions;the proposed
declared union equals the current strict union exactly. This changes the
description exposed to fixture consumers,not the accepted real-tree path set.
The0593 helper remains stdlib-only and imports no0591 module,so the named
0591→0593 dependency does not create a reverse edge.

Alternative considered:edit0591 migration tests to change the regex or inject
0593 fixture names. Rejected:changes original protection/call-site contract,
adds a fourth existing carrier and leaves public inventory divergent. The
selected design preserves that entire old test file and all its assertions.

### Accepted requirements / minimum persistent evidence

| ID | Requirement / minimum evidence |
|---|---|
| G01 | Freeze current production3-file hashes and remaining code at the Phase2 checkpoint;accepted F01–F10/raw algorithms,all seven0593 fixtures and older evidence remain unchanged. Scope only the two inherited compatibility gaps;no runtime behavior/new path/dependency or implicit phase approval. Record actual code hashes,not HEAD alone because the checkpoint is dirty. |
| G02 | On an intact real original or corrected carrier,the inverse returns original raw bytes. On unauthorized carrier bytes,the helper default still reports `unauthorized carrier edit`;the actual0591 historical_test_bytes caller reports `unapproved carrier change` where its pre-existing assertion requires it. Keyword-only diagnostic selection cannot change acceptance or swallow file-read/hash/parse failures. Adopt unchanged B04/B05 across all6original carriers and add explicit default/context/missing-file controls. |
| G03 | Public0591 NEW_TESTS equals original0591 test additions union the exact3semantic test paths;NEW_FIXTURES equals original0591 fixture additions union the exact7semantic fixture paths. Keep them separate sets,with private aliases and no mutation of the0593 constants or baseline data. Their union must equal the previously approved26path closed-world predicate,not introduce more accepted files. Cover real and synthetic inventories and shared-module cold imports. |
| G04 | Retain exact equality for actual additions and subset-presence of original test paths;retain new_test_paths actual-file existence checks. Adopt unchanged B08 positive/extra/missing controls;add named extra-path,each10semantic inventory-path deletion,and real-artifact deletion with a listing that still claims presence. Both Python and fixture paths must be exercised. No blanket exclusions,filename ignores,optional missing semantic set or fixture-only bypass. |
| G05 | Update only exact0591 repaired-post carrier generation and the corresponding caller/constant composition. The inverse accepts immutable original-pre bytes and the one corrected-post shape;the old failing0591 Phase2-post variant is not an additional permitted shape. Derive a stale-post negative by undoing the named new substitutions and verify its recorded Phase2 hash;unchanged0590/ownership carrier bytes need no new version. Original snapshots/hashes are not regenerated,or rewritten to designate the new post as historical. Test distinct pre/corrected-post raw roots,plus stale-post/comment/newline/body/import mutation rejection. |
| G06 | Leave tests/test_liss_0591_guard_migration_red.py and every existing consumer/fixture/assertion unchanged. Read-only adopt its two failing nodes,do not duplicate them as competing acceptance authority. Supplement Red additions go only in tests/test_liss_0593_guard_composition_red.py,retaining existing assertions/cases;exact proposed TEST plumbing may be staged there without applying live helper/caller changes. After reviewed Red acceptance and explicit Green,repair code edits are limited to tests/liss_0593_guard_support.py and tests/liss_0591_guard_support.py. No fourth existing carrier,new file or production edit. |
| G07 | Preserve F08 stdlib-only recursive helper closure and its no-exec/eval/compile/compiler-import rule;0591 may import only the already named0593 pure helper. The declaration-level constant dependency is explicit and acyclic;retain parser inverse,raw requested-file/sibling validation and unaffected carrier dispatch. Run actual0590/0591/0592 readers,original copied-root/frozen loops and their unrelated source/test negatives on pre/corrected-post shapes. |
| G08 | Phase1 reviews reconcile G01–G09 with named persistent cases and both inherited nodes;run both old B04/B05 and B08 unchanged,including their positives before negatives. Add counterexamples proving a permissive inventory predicate,ignored artifact deletion,wrong diagnostic and stale-post acceptance are rejected. In Green,preserve the reviewed composition tests byte-for-byte;only the explicitly accepted helper/caller implementation,including the helper's exact carrier generator,may change. Keep separate pre-supplement and corrected cohort hashes;the old496c5d8a…116c1c receipt remains historical evidence,not silently updated. |
| G09 | Separate focused/consumer/adjacent/root/spec/repository-sanity/compileall and raw/import/export audit. Zero new failures,errors,skips or exclusions required for Green. All3506 current nodes remain plus genuinely new supplement cases;compare IDs and all failures. Actual source-clean copy smoke and actual-final-SHA reruns remain blockers needing later explicit commit authority;no bypass or temporary synthetic clean-source claim. Phase3/final/delivery still require separate approvals. |

### Proposed phase execution boundary / reviewer checklist

- Current approval:G01–G09/2-file repair policy and supplemental Phase0 accepted
  by the Adjudicator2026-10-23 JST. Supplement Red execution,agent review and
  human test acceptance subsequently completed for the pinned cohort.
- Red,when separately authorized:append the G-case matrix/tests and exact
  staged test-only proposal to the existing composition test only;leave live
  helper/caller and all existing consumers unchanged. It is expected that the
  two adopted old nodes stay Red. Do not execute proposed production code.
- Test review/human acceptance occurred before any repair Green request. If staged
  setup cannot preserve original assertions within these paths,stop again for
  disposition,not broader edits. No new active-Red exclusion is proposed.
- Green (subsequently approved and applied2026-10-23 JST):apply the accepted keyword-only helper
  diagnostic/caller argument and declarative constant union;update the exact
  0591 post projection in that same helper. Preserve every reviewed assertion
  and all other code. No broad exception adapter,no baseline refresh.
- Future reviewer checks:exact26path union,all6old carrier controls,default vs
  caller diagnostics,real/synthetic/declared-missing distinctions,pre/post/stale
  raw shapes and original copy consumers. Five current production import-order
  successes are prior scoped evidence,not a substitute for repair verification.

Commands remain the declared focused/inherited/adjacent/root/spec profiles;
supplement cases stay in the existing focused composition file. Root/sanity
after final commit must run on the real SHA. Full Git history and the existing
Python environment remain prerequisites. No calibrated token/time estimate;
L/L planning retained under AIP-0593-001 with this supplement's risk update.

Stale0591 Phase2 carrier raw SHA256,for independent negative-control provenance:
`ceb6de3592e42f3fa9cca29157d58ee65fe3840f6da9798debf5bf64336fd489`.
This is a failing-checkpoint identifier,not a new accepted carrier or a fixture
to regenerate. Persistent tests must derive the stale shape from exact raw
substitutions,not depend on an ephemeral external receipt directory.

Decision:**LISS-0593 guard-consumer補足仕様 G01–G09・2-file修復方針とPhase0 acceptance**
explicitly approved2026-10-23 JST. Type:design/spec/phase acceptance;scope:the
two named guard-consumer gaps. Clauses/table unchanged from the reviewed proposal.
Supplement Red execution,agent review and human test acceptance completed
2026-10-23 JST for exact cohort
`cb85f98ae0752650b6dac5ff494ee6967586c74c58395ca3b3a24a0a78b8851c`.
Phase2 implementation separately approved and applied2026-10-23 JST;both
inherited failures are resolved. Pytest focused335/inherited433/adjacent28/root3589,
spec161 and compileall pass with zero failures/errors/skips/exclusions. Repository
sanity is9/10:source-clean copy smoke refuses the uncommitted dedicated spec.
Full all-blocking Green is therefore not established. Next requested approval:
**LISS-0593 ローカルコミット／実SHAで全blocking再検証承認**. This enables only
the authorized local commit and actual-SHA reruns;no Phase3 or remote delivery
approval is inferred. Full evidence:
`/private/tmp/liss-0593-phase2-20261023-result.json`.

### Supplement Red scenario matrix / current evidence

Given unchanged installed Phase2 helpers/production and immutable original
evidence,when the new live diagnostic/public-set/exact-post/stale rejection
contracts are checked,then five named assertions remain Red until approved
repair Green. Given distinct raw pre/post roots and staged TEST plumbing,
when intact inputs are read,then original bytes and strict inventories persist;
when each named artifact/message/raw shape changes,then its contract rejects.
Proposed TEST modules alone execute in temporary roots,never proposed production.

| Clause | Persistent evidence |
|---|---|
| G01/G06 | `test_g01_g06_production_and_original_consumer_contracts_remain_fixed`,old231line prefix/pure-family/production/non-repair carriers frozen;external before.json checks all other933 compiler/test artifacts |
| G02 | `test_g02_live_keyword_only_diagnostic_api` Red;12 staged default/context pre/post cases,3 missing/hash cases;unchanged B04/B05 six-carrier functions reused in G07 and readonly inherited runs |
| G03 | 2 `test_g03_live_public_inventory_matches_exact_composed_contract` Reds;fixed3/7semantic oracle/immutability case;2 staged cold module orders with exact26path declaration |
| G04 | 20 `test_g04_staged_each_semantic_path_requires_listing_and_real_artifact` controls (10listing/10actual deletions) plus original extra/missing controls;unchanged B08 reused in G07 and inherited runs |
| G05 | 2 live Reds:exact repaired generator/installed caller and stale-post rejection;30 pre/corrected raw mutation cases,independent stale reconstruction/hash rejection and actual0591 caller rejection |
| G07 | 2 `test_g07_original_consumers_and_negative_controls_on_repaired_copied_roots` cases with genuine production pre/post raw shapes,old frozen loops/all6old carriers/B08,unrelated source/test and parser SyntaxError;existing F08 closure negatives retained |
| G08 | 4 boundary-specific counterexamples (permissive inventory,ignored actual deletion,wrong diagnostic,stale accepted);intact counterpart first and exactly2fault calls prove positive/negative reachability rather than setup failure |
| G09 | External focused/inherited/adjacent/root/spec/compileall receipts with original node-ID preservation;no exclusion or failure waiver;source-clean/final-SHA/full sanity remain later blockers |

Only tests/test_liss_0593_guard_composition_red.py changed:231→633lines,
maximum function span38unchanged. Retain the bounded single-file test scope,
with separately named setup/contracts/cases and grouped parametrization;do
not add an unapproved helper module to reduce visible length. No numeric
structure budget is configured. This is authored evidence,not agent review.
New supplement ten-artifact cohort:
`cb85f98ae0752650b6dac5ff494ee6967586c74c58395ca3b3a24a0a78b8851c`.
Old496c5d8a…116c1c remains historical;other9artifacts/7fixtures unchanged.
Evidence:/private/tmp/liss-0593-guard-red-20261023.7un5D4/.
Inherited433:431PASS/2same failures;adjacent28PASS;spec verifier/compileall exit0.
Fresh final preservation checks confirm all other933artifacts and accepted
F/G tables unchanged,all original root node IDs retained;26relative links,
document/active-Red(entries0)/coverage lifecycle and whitespace PASS.
Tested dirty HEAD103fba434ab01db5534981bd5784d833a457b222,CPython3.12.6,
pytest9.0.3,numpy2.4.6,PyYAML6.0.3,macOS27.0.1arm64. Not final-SHA evidence
or full sanity:source-clean copy refusal remains open. Test review not executed.

## Deferred candidates

Nine pure source-classification helpers (114 span lines) are promising but
would introduce another owner/path and a broader boundary; deferred from this
first envelope. Stateful TypeChecker/Parser methods, scientific canonical
builder/projections, runtime plan, Realize policy and QASM lowering are out.
