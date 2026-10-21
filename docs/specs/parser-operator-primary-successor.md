# Parser operator-primary本体分離 — accepted specification

Current2026-10-21: R2 final review/result human-accepted at clean71e09655;
all blocking passed,no product/test changes in review/acceptance.
[Phase3 packet](../collaboration/reviews/2026-10-21-liss-0591-r2-phase3-review.md).
Acceptance-record5b62ab1a passed all local blocking;delivery authorized,PR621
created. Delivery now blocked by31 root-CI Git-history failures;no merge.
CI-history repair Scope/Phase0 design-start approved2026-10-21;
[CI01–CI07 supplement](liss-0591-ci-history-repair.md) and Phase0 accepted2026-10-21.
Phase1 execution separately approved/completed:shallow31FAIL/52PASS and
history-only83PASS,same SHA/nodes/bytes. CI repair Red agent review passed;
human Red acceptance received2026-10-21. Phase2 CI implementation separately
approved/applied;clean repair commitdf5e6062 passed all local blocking,including
copy smoke. CI Phase3 review agent_pass;uncommitted review records require final
record-SHA verification,now authorized2026-10-21 with external outcome pending.
No remote Green. Accepted P/B/E unchanged.
The chronological approval history below does not supersede this current gate.

Historical status: P01–P10 accepted2026-10-16; supplemental B01–B10 / exact6-carrier
policy and Phase0 accepted2026-10-19. Resumed Phase1 executed2026-10-19;
R1 corrected/re-reviewed and closed;179 nodes:4 expected structural Red /
175 PASS. Human corrected-test acceptance received2026-10-19;
Phase2 implementation approved/executed2026-10-19;verification blocked on
R2 public-export/EOF consistency,not all-blocking Green. See final section.
R2 Scope/Phase0 design-start and E01–E08/limited3-new-test correction policy
accepted2026-10-19. R2 Phase1 test-only execution approved/completed2026-10-19;
202 focused nodes:157 PASS/45 Red. R2 test review passed and human corrected-test
acceptance received2026-10-21. R2 Phase2 implementation approved/executed;
focused/regression/root checks pass dirty. Local commit/actual-SHA checkpoint
approved2026-10-21;Phase3 remains gated by its external verification record below.
Scope/Architecture Path Phase0 design-start explicitly approved2026-10-16.
Dedicated Issue/spec and bounded ownership/error-factory/structure dispositions
explicitly accepted by Adjudicator2026-10-16. Phase1 test/limited-guard execution
approved2026-10-16;baseline readiness check exposed P08 conflict below before
any test/guard edits. Execution paused for bounded specification disposition.
Owner:[LISS-0591](../issues/LISS-0591-parser-operator-primary-successor.md),
parent:[WP-0175](../work-plans/WP-0175-source-responsibility-inventory.md).
Immutable source base:`22335a5768c17a41eb94682e7dd14d3e6df004bd` (PR618/main CI passed).
Authority:accepted [core decomposition](staqex-core-module-decomposition.md).
Phase2 implementation permission is bounded to the3 agreed production paths;
no accepted-test amendment,Phase3,commit or remote delivery permission.

### Historical blocker — P08 baseline compatibility (resolved by0592/handoff)

At unchanged source22335a57,default `pickle.loads(pickle.dumps(ParseError(...)))`
raises `TypeError: ParseError.__init__() missing 2 required positional arguments:
'line' and 'col'`. Representative OpLit/Span round-trip succeeds. P08's
successful error round-trip expectation was not validated during Phase0 and
conflicts with the accepted no-ParseError-constructor-change boundary.
This is a baseline/design mismatch,not an extraction regression. Accepted
P08 text remains unchanged pending human disposition;no serializer fix,
custom reducer,skipped assertion or new test implemented to disguise it.
Canonical mismatch/disposition record:child Issue section `P08 readiness conflict`.
Update2026-10-17:human requests actual repair rather than failure preservation.
Defect ownership transfers to [LISS-0592](../issues/LISS-0592-parseerror-serialization-repair.md)
and its [accepted repair contract](parseerror-serialization-repair.md) (2026-10-17).
Successful P08 remains unchanged.0591 waits for reviewed repair and agreed
new baseline/inverse composition;no failure-preservation amendment proceeds.

## Supplemental Phase 0 — repaired baseline / guard composition (accepted)

Human2026-10-19 authorized **LISS-0591 修復済みベースライン／guard合成方針のScope・Phase 0設計開始**.
That design-start authorization alone did not accept the amendment or resume Red.
Subsequently received2026-10-19:**LISS-0591 修復済みベースライン・B01–B10／限定6-carrier方針とPhase 0 acceptance**.
Type:phase/design acceptance. B01–B10 and the exact6 existing carrier dispositions
are accepted unchanged. That receipt alone did not authorize resumed execution.
Separate resumed Phase1 execution approval subsequently received2026-10-19;
implementation,commit and remote delivery remain unauthorized. P01–P10 below
remain unchanged.

### B01–B10 accepted amendment (2026-10-19)

| ID | Required boundary / later evidence |
|---|---|
| B01 | Pin delivered main `dca93187f50594b0417ae88067154baaf3c0ea7c` (records PR620, all3 PR/main CI successful) as the repaired source/test base. Original `22335a57` remains immutable historical evidence, not the source copied into the new implementation. Repair PR619/main442ce6ff provenance remains intact |
| B02 | Preserve every live ParseError constructor/reducer/restorer byte, class path/identity, independent args/state/copy behavior and actual public exports at the repaired base. Keep successful P08 unchanged. Capture the complete repaired source/production path/export manifests and original method from actual Git before Red authoring |
| B03 | Use a one-way, test-only composition: current Parser → inverse of exact0591 extraction → repaired Parser → existing0592 inverse → original22335 parser. The first inverse must preserve repair presence/absence, not remove/add repair blocks. Validate sole successor/context/import/alias/factory and exactly3 constructor substitutions before raw reconstruction. No whole-file snapshot substitution, AST-unparse normalization, newline conversion or stale baseline replacement |
| B04 | Preserve every existing fixture/hash, all0592 behavioral assertions, original test node identities and failure controls. Three additional0592 plumbing carriers below require explicit acceptance; do not silently replace0592's tests/evidence. New0591 immutable evidence records the exact repaired-base originals of all6 carriers and the10-file0592 namespace plus its2 old carriers (12-artifact accepted cohort); reconstruct them before verifying historical digests |
| B05 | Exactly6 existing test paths may receive bounded plumbing, as specified below. No further existing test/support/fixture edits. New support must validate exact accepted deltas even in carriers that themselves call it; a live inverse cannot certify arbitrary edits to its own body. Pin expected baseline bytes and exact substitutions independently in new immutable evidence and persistent negative controls |
| B06 | Keep import direction acyclic:0590 reader →0592 parser inverse → pure0591 extraction inverse;0590 operators reader →pure0591 inverse. New pure inverse imports stdlib/evidence only, never0590/0592 helpers, production Parser, or runnable proposals. No dynamic fallback that accepts a changed file because a helper is missing |
| B07 | Real copy closure includes current parser/operators/new context when present. Keep distinct Parser extraction pre/post and TypeChecker pre/post roots, and historical repair absent/present roots. Assert selected shapes before/after every real copy. For existing0592 AST-only tests, normalize extraction before constructing historical repair shapes, without inventing a runnable implementation or discarding the selected repair flag |
| B08 | Historical source/path/test fingerprint checks use verified views only: reverse exact carrier deltas, validate context before projecting its one authorized path, and reject every unexpected production/test addition or deletion. New0591 tests/support/fixtures need an explicit closed path manifest, reconciled at Red review; no broad filename exemption. Keep actual repair-presence and runtime export checks on live production, not a projected view |
| B09 | Before Red acceptance, independently exercise exact positive pre/post shapes, changed/missing successor/context, alias/factory/callback/order/grammar/reducer/restorer/constructor changes, comments, whole/mixed CRLF and CR, changed evidence, unexpected paths and each extra carrier edit. Call real inherited0585/0587–0590/0592 consumers and copy utilities. Map P01–P10 and B01–B10 to named nodes; do not count a mutation rejected for missing setup as effective protection |
| B10 | Fresh focused repair114 and inherited/adjacent checks establish baseline only. Later Green/Refactor require actual consumers/cold imports/P08, full root/spec/all applicable sanity at final actual SHA, raw/AST/source audits and routing/structure dispositions. No exclusions, reduced assertions or renewed blanket hash allowed. Any seventh carrier or wider production boundary returns to design acceptance |

### Exact six existing carrier dispositions (accepted;Phase1 execution gated)

1. `tests/liss_0590_guard_support.py`: keep its parser read routed through0592;
   route only parsing/operators evidence through the0591 inverse, validate the
   exact new parser context, and copy live Parser closure in temporary shape
   construction without changing TypeChecker shape selection/algorithm.
2. `tests/test_liss_0590_operator_ownership_red.py`: preserve readonly loop and
   TypeChecker assertions; add only the exact validated parser context to path
   allowance. Existing TypeChecker context allowance is unchanged.
3. `tests/test_liss_0585_tensor_guard_migration_red.py`: only
   `copy_guarded_dependencies` copies live parser/operators/context when present;
   all Tensor setup/assertions and manifests remain unchanged. Assert Parser
   shape preservation through real callers; do not overwrite a chosen shape
   with an independently selected incompatible origin.
4. `tests/liss_0592_guard_support.py`: only the input to
   `original_parser_bytes` first uses verified0591 extraction normalization,
   and `assert_carriers` compares verified pre0591 carrier views to its unchanged
   expected0592 substitutions. Reducer/restorer verification, original raw/AST
   hashes, `make_shape`, immutable evidence access and `carrier_after` stay intact.
5. `tests/test_liss_0592_boundary_red.py`: only frozen readonly reads, production
   path-set view and retained-test enumeration/bytes use exact validated0591
   projections. Preserve historical expected hash/fingerprint, original cohort
   order and all actual repair/export checks. New0591 paths are checked against
   the closed manifest before their omission from the historical cohort;
   existing test bytes, including0585 plumbing, are reconstructed, not exempted.
6. `tests/test_liss_0592_guard_migration_red.py`: only `dependency_root` adds the
   exact live context to the copied closure when present, before normalization.
   Keep all existing114 repair nodes/parameters/assertions/mutations unchanged.
   New0591 tests cross extraction with these unchanged real repair callers.

This accepted supplement supersedes the *future* three-carrier policy below.
The0592 two-carrier repair policy remains historical repair authority;
this separately reviewed successor disposition owns later test-only plumbing,
not another repair or permission to regenerate its originals. No change to
the3 permitted production paths,117-line algorithm or narrow context contract.

### Current measurements / verification limits

At clean `dca93187`,macOS27.0.1 arm64/CPython3.12.6/explicit PYTHONPATH:
parser3694 physical lines,Parser class3504,selected method117 lines3386–3502;
operators14. Selected AST equals original22335 method. Parser SHA256
`9222a47056c521c11f345242f4c4adcc37c4fbb05bb102a2fd224fcdd1e08d16`;
operators SHA256 `ace62fc91ee6b50ddc8d0df21f5c47ebfe116f5c2852b0493a81fd1bc3ff280b`.
223 tracked compiler files; exact file/export/repair cohort hashes in
`/private/tmp/liss-0591-phase0.8hzegU/baseline591-probe-20261019.out`.
Probe confirms protocol0–5,copy/deepcopy and both existing raw readers restoring
exact Git22335;this is not a post-extraction compatibility proof.
Fresh existing suites at the same clean SHA:repair114 PASS,inherited293 PASS,
adjacent39 PASS,spec161/161 PASS. Detailed command/timing/environment/exit records
are `baseline591-{repair,inherited,adjacent,spec}-20261019.*` alongside the probe.
Root/all-sanity not rerun in Phase0;prior main CI is distinct historical evidence.

Future shape/copy closure and whole dynamic dependency graph are not proven
by this design. Parser remains above prior class guideline;retain its other
grammar/orchestration with WP0175 owner and revisit next family gate. No
postimplementation size or net-line-reduction claim. Routing same_context
(weaker),host,empty model IDs;no enabled large-change override. Re-measure
actual final diff,including implementation bodies/records,at later reviews.

## Goal and bounded ownership

Move the sole117-physical-line `Parser._legacy_parse_operator_expression`
(`parser.py:3371–3487`) to the existing `parsing/operators.py` family.
Despite its historical name,this is **operator primary**,not the whole operator
precedence grammar. Preserve the whole branch algorithm,including its mixed
OpExpr/Expr outputs,early returns,token consumption,errors and callback order.

| Location | Accepted design responsibility (not implementation permission) |
|---|---|
| `parsing/operators.py` | Sole private `_legacy_parse_operator_expression(self: OperatorParseContext)` algorithm;existing public forwarding entry unchanged |
| `parsing/operator_context.py` (new) | Declaration-only narrow Protocol;no state instances,grammar,dispatch,error conversion or Parser import |
| `parser.py` | Sole live Parser state,existing other grammar and public imports;private successor import,ordinary bound alias in old method position,small error factory |

Keep `parse_operator_expression(context: ParserContext,*args,**kwargs)` exactly
as a forwarding compatibility API:custom context callbacks and argument forwarding
remain valid. Do not bind Parser to that wrapper (which would recurse). Instead
bind `_legacy_parse_operator_expression` to the private sole algorithm and retain
the bottom `Parser._op_primary = Parser._legacy_parse_operator_expression` relation.
Keep `self` receiver spelling for unbound keyword calls;both hooks remain ordinary
bound methods,not staticmethods,class methods or new stateful services.

### Narrow context and unchanged error identity

Algorithm reads `_prev: Token | None` and invokes exactly these11 existing
callbacks:`_span`,`_match`,`_check`,`_advance`,`_expect`,`_peek`,
`_op_expression`,`_ket_or_outer`,`_comma_op_expr_items`,`_algebra_call`,`_op_binder`.
Declare them structurally using existing Token/TokenKind/Span/OpExpr/Expr types;
mixed grammar results must not be coerced to one AST family. The context may
use a mixed-result union or narrow Any where existing list signatures require
it;do not add AST classes or new runtime validation to satisfy annotations.
Cursor `tokens/i/_prev`,diagnostics,profile/name-resolution state stay on Parser;
callbacks remain overrideable/live. Do not cache snapshots or rewind on failure.
Broader `parsing/context.py` and `parsing/__init__.py` remain byte-unchanged.

`ParseError` is currently defined in `parser.py`,not a shared error module.
Keep that class,constructor,attributes,public path and identity unchanged. Add
only a static `_operator_parse_error(message: str,line: int,col: int) -> ParseError`
returning fresh `ParseError(message,line,col)` in the original facade globals.
Replace exactly three direct constructor expressions in the moved body by
`self._operator_parse_error(...)`,at unchanged raise evaluation points
(base lines3390,3399,3485). Protocol declares an Exception-returning callback,
without importing Parser/ParseError. Keep `_expect` and other callbacks unchanged:
their own ParseErrors still originate there. No catches,new codes,recovery,
shared cached exception or error-factory policy. Custom global monkey-patches
of unrelated AST constructors across modules are not a guaranteed API;public
class identity and actual parser exception construction are retained.

Successor imports only existing AST/token types and narrow context;no public
parser facade import,including TYPE_CHECKING/lazy backdoors. Keep every original
public facade import,even if newly internally unused. No new resource/port,
provider,package,technology or ADR is proposed. Stop for architecture decision
if the move requires changing AST/error identity or shared state ownership.

## Acceptance P01–P10 (accepted2026-10-16)

| ID | Required behavior/evidence; minimum Phase1 inventory |
|---|---|
| P01 | Sole successor owns whole original method AST,literals/comments evidence pinned from immutable Git. Only receiver/result annotations and exactly3 ParseError→factory substitutions normalize. Original class body removed,exact import/alias/factory;no duplicate algorithm or new grammar |
| P02 | Parenthesized recursion returns actual child;INT/FLOAT become existing OpLit with original float conversion;ket uses `_advance` then `_ket_or_outer`. Compare result identity/shape/Span and callback order,including nested parentheses and ket/bra helper exceptions |
| P03 | Bracket/brace forms invoke `_comma_op_expr_items` with correct closer;exactly2 items call `_algebra_call` with original list/Span. Empty/1/3-item cases preserve exact respective messages and opener positions. Include trailing comma,missing closer and child error;helper failures precede cardinality check |
| P04 | IDENT dispatch:all Sigma/Pi/ForAll/Min go to binder;P/Q/N remain OpVar (not Fock atom AST),attributes before repeated indices;hop consumes exactly(INT,COMMA,INT,RPAREN). I/X/Y/Z bare atoms,zero/multiarg calls,one optional indexed atom,ordinary identifiers/calls/dotted/indexed chains all retain early-return and consumption limits. Include cases whose trailing tokens intentionally remain unconsumed |
| P05 | Existing `_op_expression` precedence,unary,postfix dagger,binder domain/where/Implies and reserved-name factory heuristic unchanged. Parser.parse/compile_source positive and neighboring rejection regression includes Pauli/factory,PQN shadow,Dirac,commutators and binder programs;test direct primary separately so generic expression bypass does not fake coverage |
| P06 | Both actual Parser hooks identify the sole function and bind same instance;public variadic forwarding preserves custom callbacks,args/kwargs and exceptions. Narrow context has declarations only. ParseError factory is static,fresh,exact actual class/attributes/code/args;instrument all3 real successor error sites with site/count and failure controls,not an earlier `_expect` exception |
| P07 | No added rollback/catch:success/failure preserves exact `i`,`_prev`,token-list identity,diagnostics and unrelated fields;exceptions from all11 callbacks,argument conversion,error construction and BaseException propagate at original point. Direct/bound/unbound receiver hooks and recursive live overrides retain timing |
| P08 | Preserve actual Python public exports/import identity for parser,parsing.operators and parsing package,including imported AST/token names. Three production imports (pipeline_legacy,modules,access),nested Parser creation and both requested cold import orders must work;AST/error pickle round-trip representative values,not arbitrary user serialization completeness |
| P09 | Limited guard migration below protects authorized pre/post Parser shapes while rejecting unrelated-body/signature/state/import/error/message/callback/order mutations,wrong alias,duplicate body,missing/mutated successor/context and changed immutable evidence. Preserve existing TypeChecker guard positives/negatives and real inherited temporary-copy setups |
| P10 | All other production bytes unchanged;only parser.py,parsing/operators.py,new operator_context.py allowed. Existing frozen evidence/assertions/exclusions retained except exact reviewed P09 carrier plumbing. Fresh focused,consumer,adjacent,all blocking at final actual SHA;structure/routing gaps and final merge verification explicit |

P02–P07 require clause-to-named-test reconciliation before Red acceptance.
Do not treat passing structural strings or two fixture labels as real execution
or distinct shape evidence. Expected structural Reds must be listed separately
from passing characterizations;unrelated failures remain blocking.

## Accepted limited guard migration policy (P09)

Observed frozen manifests reference parser.py at0587,0588,0589 and0590;
0590 additionally freezes `parsing/operators.py` and production path membership.
Preserve every original manifest/hash and original TypeChecker/method evidence.
Do not update parser hashes to the new implementation or exempt a whole file.

Accepted Phase1-only carriers,exactly3 existing paths:

1. `tests/liss_0590_guard_support.py`:route only parser-owned reads through new
   0591 test evidence reconstruction;preserve old TypeChecker/carrier logic.
   Its temporary `make_shape` copies actual Parser dependency closure explicitly
   when present,without changing the independently selected TypeChecker shape.
2. `tests/test_liss_0590_operator_ownership_red.py`:readonly loop uses verified
   reconstruction for changed Parser paths;production path allowance adds only
   the exact new parser context,validated by0591 owner contract. No unbounded
   additions and no changes to TypeChecker assertions.
3. `tests/test_liss_0585_tensor_guard_migration_red.py`:only
   `copy_guarded_dependencies` gains explicit copies of current parser.py,
   parsing/operators.py and parser context when present. Do not alter Tensor
   shape construction,assertions or historical manifests.

Existing0587/0588/0589 readonly carriers already call0590.readonly_bytes,so they
need no direct rewrite. Existing0590 guard migration tests remain read-only and
must still construct distinct TypeChecker roots. New0591 tests must call those
real carriers/copy utilities against genuinely distinct **Parser** pre/post
temporary roots;do not let a copy overwrite the chosen Parser shape. Copy
new context/owner dependencies before guard invocation,assert exact owner/alias/
context presence,then retain missing/mutated-owner negatives. Cross Parser
pre/post with TypeChecker pre/post where supported;never import AST-only proposals.

New test-only0591 support must inverse exactly the reviewed parser import,
alias,factory and3 constructor substitutions,validate whole successor/context,
and return the original raw parser/operators bytes. Unrelated bytes must not
be erased by whole-file substitution. Keep original0590 helper and ownership
carrier snapshots pinned,and assert only these named plumbing differences.
Fixture originals live in new0591 evidence files with immutable Git provenance;
no existing fixture is regenerated. Production-path checks retain every previous
path and reject any unexpected extra besides the exact new context.

Phase0 authorizes **none** of these edits. Dedicated spec acceptance must include
this policy;separate Phase1 execution approval then permits tests/scaffolding
only. If actual copy closure or pinned carrier protection requires another
existing path,stop and request bounded design amendment instead of broad edits.

## Consumer,structure and verification disposition

Base parser3679 physical lines,Parser class3504,selected body117. Existing
operators14. No estimated successor size is a measured postimplementation result.
Parser remains over1200-class guideline after this bounded move:retain live
orchestration/other grammar this issue,owner WP0175/Adjudicator,next family gate
must revisit. This is not full Parser decomposition or a net-line reduction claim.
Selected117-line algorithm is below150-function guideline;no need to split its
branches merely to hit a number. New owner/context should stay below1200.
Live routing:same_context/weaker,host implementation,empty modelIDs,no enabled
large-change override. Recompute committed metrics after implementation;semantic
owner mapping/full dynamic graph/cycles/custom serialization remain gaps.

Fresh Phase0 baseline at22335a57,macOS27.0.1 arm64,Python3.12.6,explicit PYTHONPATH:
existing adjacent10 suites46PASS,inherited5 suites45PASS,spec161/161PASS.
External AST/import/attribute/manifest inventory and14 direct actual-context
observations (not acceptance tests) in `/private/tmp/liss-0591-phase0.8hzegU/`.
Static search does not prove all dynamic consumers. Whole-root/all-sanity not
rerun in Phase0;prior main CI success is baseline evidence,not dirty-design Green.

For later Phase2/3,declare and run root `python3.12 -m pytest tests/ -q --tb=short`,
spec `python3.12 tests/spec_verification/run_all.py`,every applicable sanity step
from `.github/workflows/ci.yml`,new P01–P10 suites,inherited0585–0590 guard/copy
regressions,above adjacent suites,actual consumer smoke,compileall,Git-derived
whole AST/raw-source/export audit,cold imports and committed review-change route.
No active-Red or other exclusion approved here. Exact commands/environment/
counts/failures/exclusions and comparable baseline failures must be recorded;
post-final-commit all blocking required separately from focused success.

## Approval boundary

Received: **LISS-0591 専用Issue/spec P01–P10・限定guard移行方針とPhase 0 acceptance**
on2026-10-16. Type:phase/design acceptance. Approved scope:operator-primary design.
Phase1 execution approval received2026-10-16;paused at baseline P08 discrepancy.
Previous failure-preservation proposal superseded by human repair direction2026-10-17.
Historical gate before Phase2 (2026-10-19):0592 records PR620/main dca93187 delivered,PR/main CI
successful;B01–B10 repaired-baseline/guard composition and exact6-carrier policy
accepted. Resumed0591 Phase1 separately authorized/executed;R1 test-only
correction/re-review authorized/completed and corrected-test acceptance received
2026-10-19. Next:separate Phase2 Green/implementation approval.
Implementation allowed:no for0591. Post-review
required:yes,then resume bounded Phase1 execution under agreed baseline,followed by
test review/exact acceptance,Phase2 implementation,Phase3,final verification and
delivery gates. Batch:N/A. BUG-WP0175-001/002 stay plan-owned and unapproved.

Repair Phase1 execution separately approved/authored2026-10-17;tests/limited
two-carrier plumbing only,no production change. Current results and next review
gate owned by0592 Issue/spec/trace. This does not revise P01–P10 or accept a
new0591 baseline;0591 stays blocked until actual repair/reviewed handoff.

## Phase1 execution —2026-10-19 (review pending)

Received **LISS-0591 Phase 1 Red再開（P01–P10・B01–B10受入テスト作成／限定6-carrier移行）の実行承認**.
Only test/scaffolding plus status records authored. Production remains exact
Git `dca93187f50594b0417ae88067154baaf3c0ea7c`. Existing6 carriers match the
closed substitutions in new support;all other existing tests/fixtures unchanged.
No seventh carrier,hash regeneration,assertion weakening or exclusion.

New closed inventory:4 test modules,2 support modules and10 fixtures under
`tests/fixtures/liss_0591/` (baseline.json,original-primary.txt,
original-operators.txt,carrier-0.txt through carrier-5.txt,behavior.json).
The new baseline captures actual Git source/exports/production/test provenance;
behavior.json records actual unchanged Parser observations,not proposed code.
`NEW_TESTS`/`NEW_FIXTURES` enforce exactly these paths.22-artifact cohort
(16 new plus6 existing carriers) SHA256:
`82458c74523978e6ea16cf7dcd32c3bdc4c2e2b15926a470aa1c171c72ed414d`.
Per-file hashes/independent audit:external red591-audit-20261019.out.

### Clause-to-test reconciliation

All filenames below use `tests/test_liss_0591_` prefix and `_red.py` suffix.
Parameterized source IDs and individual cases are retained in JUnit evidence.

| Clause | Named evidence |
|---|---|
| P01 | ownership::test_p01_sole_successor_owns_original_algorithm_and_declaration_context;test_p01_facade_body_removed_exact_alias_factory_and_raw_inverse;guard_migration::test_b01_p01_fixture_and_inverse_algorithm_match_independent_git_ast |
| P02 | behavior::test_p02_p05_exact_ast_span_errors_callback_order_cursor_and_remainder (numeric,parentheses,ket/bra source IDs);test_p02_parenthesized_and_ket_helpers_return_exact_child_identity |
| P03 | same exact-observation test (all bracket/brace cardinalities,trailing comma,missing closer,child failure);test_p03_items_list_and_span_identity_reach_algebra_after_helper;P07 helper exceptions |
| P04 | same exact-observation test (P/Q/N,hop,Pauli/call/index/dotted/remainder IDs);test_p04_all_binder_names_keep_live_callback_and_original_span |
| P05 | behavior::exact observation expression IDs;test_p05_postfix_dagger_at_token_boundary_keeps_repeated_adjoint;consumers::test_p05_real_parse_and_compile_adjacent_operator_binder_families;existing adjacent9 suites |
| P06 | ownership::test_p06_both_actual_hooks_are_ordinary_bound_sole_successor;test_p06_static_fresh_factory_all_three_real_sites_and_failure_controls;consumers::test_p06_public_variadic_forwarding_uses_live_custom_callback_and_exceptions;context raw declaration contract in P01 |
| P07 | behavior::test_p07_all_eleven_callback_exceptions_propagate_without_cursor_or_state_rollback (11 callbacks×RuntimeError/KeyboardInterrupt);test_p07_float_conversion_failure_is_after_advance_and_not_caught;test_p07_hop_integer_conversion_failure_consumes_original_arguments_first;test_p07_receiver_forms_share_actual_instance_and_state;test_p07_recursive_primary_uses_live_override;P06 factory failures |
| P08 | consumers::test_p08_actual_pipeline_module_access_nested_parser_consumers;test_p08_all_original_public_exports_and_reexport_identity;test_p08_ast_and_actual_repaired_parseerror_roundtrip;test_p08_two_requested_cold_import_orders;unchanged0592 repair suite |
| P09 | all53 guard_migration nodes:8 extraction×TypeChecker×repair real copy roots,distinct-shape/copy normalization,14 owner/wiring/repair mutations,15 raw newline variants,6 extra carrier edits,2 production path cases,closed test inventory,5 evidence mutations,independent Git AST |
| P10 | ownership::test_p10_unrelated_production_and_all_six_carriers_keep_frozen_bytes;external Git/cohort audit;later actual-clean-SHA/all-blocking obligations remain |
| B01/B02 | independent Git AST/evidence plus baseline.json/P08/P10;repair114 unchanged node outcomes |
| B03/B04/B05 | guard_migration::eight distinct shapes;each_of_six_carriers_rejects_extra_edits;immutable_evidence_mutations_are_rejected;P10 exact carrier audit |
| B06 | ownership::test_b06_pure_inverse_has_no_project_import_or_executable_proposal;real historical readers exercised by guard tests |
| B07 | guard_migration::test_b03_b07_real_readonly_copy_consumers_cross_eight_distinct_shapes;test_b07_distinct_primary_roots_and_repair_normalization_are_real |
| B08 | production_path_projection_rejects_unexpected_additions;closed_new_test_inventory_rejects_extra_or_missing_paths;historical fingerprint checks retained in0592 boundary |
| B09 | all positive/negative guard nodes above;both real parser readers;independent Git AST reversal counts exactly3 factory substitutions |
| B10 | focused171 (4 expected Red/167 PASS),repair114/inherited293/adjacent39/spec161;root/all-sanity/final-commit evidence not_run,not waived |

New test modules:ownership6 nodes (4 structural Red/2 PASS),behavior92 PASS,
consumers20 PASS,guard_migration53 PASS. Expected Red reasons:sole successor/
context absent,facade still owns method,bound successor not installed,static
factory absent. No collection errors/skips. Factory-site runtime controls are
authored but remain behind the missing-factory Red until real implementation;
AST-only shape success is not runtime proof of that new boundary.

Authoring corrections retained in trace:initial copy overwrite/distinct-target
setup defects and ignored .DS_Store enumeration were corrected test-only before
review. Existing protected behavior/assertions were not weakened. Repaired
normalization happens inside the approved0592 dependency_root only after copying
and validating context;existing0592 make_shape/114 node assertions stay intact.
Daggers are tested as existing TokenKind.DAGGER inputs;unsupported Unicode
lexer spelling is not silently assumed as a source-level success contract.

Environment:dirty source SHA dca93187,macOS27.0.1 arm64/CPython3.12.6/pytest9.0.3,
explicit PYTHONPATH. Full commands/times/exits/failures:external
`/private/tmp/liss-0591-phase0.8hzegU/red591-*-20261019.{json,out,err}`;
focused JUnit `/private/tmp/liss-0591-red-20261019.P2SI2B/focused-final.xml`.
No Green/review pass/acceptance or full-coverage claim. Next:explicit Phase1
test review execution,then exact-artifact human acceptance before implementation.

## Phase1 review disposition —2026-10-19

Human-approved review execution performed,same_context/weaker. Result:requires
changes,R1 [P2]. The named0591 readonly operators reader accepts deleted
original operators.py on unextracted repaired/unrepaired roots by returning
the original fixture;its parser-only raw-root allowance is not sufficient
validation for an explicit named operators read. Existing0590 reader rejects
the same deletion,so this is not evidence that all guard/CI paths accept it.
P09/B08/B09 require a persistent pre-shape missing-file control and actual
existence check before normalization. No change to accepted P/B clauses.

171 nodes still4 expected structural Red/167 PASS;repair114/inherited293/
adjacent39/spec161 pass. Independent probe and full disposition:
[review packet](../collaboration/reviews/2026-10-19-liss-0591-phase1-review.md).
No tests/source changed during review. Next:R1 test-only correction/re-review
approval (only2 new0591 test files plus records),then corrected-test acceptance.

## R1 corrected-test disposition —2026-10-19

Explicit R1 test-only correction/re-review approval received. Only the2 named
new0591 test files changed:one requested-file existence assertion and8 appended
nodes (`guard_migration::test_r1_named_operators_read_requires_actual_file_on_all_shapes`).
P09/B08/B09 now have normal/deleted named reads on both readers,repair pre/post,
extraction pre/post;historical parser-only inverse remains valid. Original
P01–P10/B01–B10 clauses,fixtures/hashes,6 existing carriers and production bytes
unchanged. Mapping above describes original171 nodes;these8 supplement it.

Fresh179 nodes:4 same expected structural Red/175 PASS,0 errors/skips. Repair114,
inherited293,adjacent39,spec161/161 pass. Same reviewer probe input operations
now reject all4 deletion controls and retain4 normal positives. R1 closed in
same-context agent re-review;not human test acceptance or implementation approval.
Corrected22-artifact cohort:
`68d6eef02b5e18a01ed4e3f4fef22c95ae740c71a57881b56b65708f3f1b5547`.
Full commands/dirty SHA/environment/hash comparison and limitations in
[updated review](../collaboration/reviews/2026-10-19-liss-0591-phase1-review.md).
Next:human corrected-test acceptance,then separate Green implementation approval.

## Human corrected-test acceptance —2026-10-19

Received **LISS-0591 Phase 1 Red 修正済みテストレビュー／acceptance承認**.
Type:phase/test acceptance. Human accepts corrected22-artifact cohort
`68d6eef02b5e18a01ed4e3f4fef22c95ae740c71a57881b56b65708f3f1b5547`,
including the R1 existence check/8 persistent nodes and same-context re-review.
P01–P10/B01–B10,6-carrier bounds and successful P08 remain unchanged.
Prior179 nodes (4 expected Red/175 PASS),repair114/inherited293/adjacent39/
spec161 results retain their original dirty-SHA/environment attribution;no
runtime suite rerun for this metadata-only receipt. Full blocking not claimed.
Implementation allowed:no;post-review required:yes;batch:N/A. Next:explicit
Phase2 Green/implementation approval;commit and remote delivery remain separate.

## Phase2 integration finding / R2 proposal —2026-10-19

Phase2 implementation explicitly approved and executed on the3 named production
paths. Original P01–P10/B01–B10 and accepted22 test artifacts unchanged. Focused
179 PASS does not imply all-blocking Green:unchanged0592 R04 requires the exact
original public exports of parsing/operators.py. Required successor imports
introduce9 extra non-private names. New0591 whole-module raw equality currently
rejects any additional export declaration;its required trailing blank also
fails diff whitespace verification. This was not covered by Phase1 composition.

Proposed supplemental design,NOT approved:preserve exact original public export
set using `__all__ = ['Any', 'ParserContext', 'annotations',
'parse_operator_expression']`;amend only new0591 expected module wiring with
paired wrong/missing-declaration controls;normalize only new successor EOF to
one newline. Retain0592 exact equality,all immutable fixtures/hashes,facade raw
inverse and P/B behavior. No test changes or further source fix authorized by
this proposal. Next:explicit R2 Scope/Phase0 design-start,then reviewed design
and separately approved test correction/re-review before implementation resumes.
Current evidence/remaining gates:[trace](../collaboration/traces/2026-10-16-liss-0591-parser-operator-primary.md).

## R2 supplemental Phase 0 — E01–E08 (accepted2026-10-19)

Human approved **LISS-0591 R2 公開export／EOF整合のScope／Phase 0設計開始承認**
on2026-10-19. Architecture Path,bounded agreement correction only. This receipt
authorizes design,not acceptance of this supplement,test changes,implementation,
Phase3,commit or remote delivery. P01–P10/B01–B10 remain unchanged. E clauses
propose a precise successor-wiring disposition under P08/P09 and B02/B09,
not a relaxation of the persistent compatibility contract. Subsequent human
E01–E08/policy acceptance received2026-10-19;receipt below. Design-start alone
did not grant it,and neither receipt authorizes execution.

### Design Note / context and decision boundary

- Target:exact repaired-base public export set/identity and whitespace-clean
  successor must coexist with complete algorithm/raw-facade preservation.
- Current phase:R2 Phase0 design accepted;original Phase2 remains blocked.
  Next proposed phase:R2 test-only correction/re-review after separate execution
  approval. No acceptance-test correction or implementation executed by this receipt.
- Included:live operators/Parser context,0591 raw inverse/shapes/consumers,
  unchanged0592 R04,Git dca93187 and immutable manifests,Phase2 failure evidence.
- Omitted:other grammar,Rust,providers,unrelated ADR history,secrets;no external
  AI payload or new technology/resource/port/VO/DTO.
- Routing:host design/deterministic probes;future required review same_context
  (weaker),implementation host,empty model IDs,no enabled large-change override.
- Input/output:actual Git/current bytes and failed verification → proposed
  clauses/test map/approval boundary. AST-valid proposed bytes are not execution
  or proof that a future correction passes consumers.
- Decision:explicit `__all__` controls wildcard/declared public exports;it does
  not delete imported attributes from `vars(module)` or promise an unchanged
  `dir(module)`. Original4 attributes/identities stay available. Imported new
  implementation dependencies do not become additional supported public API.
- Alternative rejected for this proposal:private aliases would require wider
  constructor/TokenKind annotation/reference substitutions in the frozen body.
  Adding one explicit export declaration preserves the accepted whole algorithm.
  Do not delete imports or change0592 equality to subset containment.
- ADR:N/A;existing ownership/error/state/public-API policy unchanged. Any actual
  API retirement,identity change,extra carrier or wider body edit stops for design.

### E01–E08 accepted supplement (2026-10-19)

| ID | Required boundary / evidence |
|---|---|
| E01 | Derive original operators exports from actual dca93187/immutable manifest:exactly `Any`, `ParserContext`, `annotations`, `parse_operator_expression`. Preserve each attribute and identity. Actual declared/wildcard export set must equal,not merely contain,this set. Retain0592 R04 and its fixture/assertions byte-for-byte |
| E02 | Add exactly the literal `__all__` block below after the3 successor import lines and their following blank,before the sole successor function. Keep original14-line module prefix and public variadic wrapper unchanged. No runtime deletion,dynamic export filtering,private renaming,catch,second algorithm or new imports |
| E03 | Remove exactly one final LF from the new successor serialization,which currently ends with2 LF;result must end with exactly1 LF. Assert that expected source suffix before this one-byte removal is the pinned2-LF suffix. Do not `strip`/normalize arbitrary input or fixture bytes. Inverse still restores original-primary evidence including its original following blank. Parser/context and all immutable evidence remain byte-unchanged |
| E04 | New0591 raw guard requires exactly E02/E03 for the extracted shape;do not accept both the flawed Phase2 serialization and corrected serialization as alternatives. Preserve pre-extraction original14-line shape,repair pre/post distinction,existence checks and full raw/AST inverse. Validate successor/context before returning historical evidence;no broad __all__/whitespace removal |
| E05 | Test correction scope is exactly3 new0591 paths below;no existing6 carrier change or seventh carrier,no fixture/hash regeneration,new filename,baseline/export widening or exclusion. Retain all existing179 node identities,R1 paired existence controls,original behavior and failures. Record the new reviewed cohort separately;never replace the historical accepted68d6…5547 fingerprint |
| E06 | Pair intact extracted roots with missing/wrong/extra-name/duplicate export declarations and missing-final-LF/extra-final-LF/whole-or-mixed-CRLF mutations. Invoke actual0591 parser and readonly operators readers,and inherited0590/0592 readers;both intact positives and mutation rejections must be effective. Cross repair pre/post;retain actual TypeChecker×Parser copy-shape coverage. Add live exact-export and wildcard identity checks,not imports of AST-only proposals |
| E07 | Test-only correction must reproduce current export mismatch as a blocking Red,not classify it as an expected waiver. Existing0592 R04 already provides the authoritative runtime failing node;adopt it without duplication/changes. New exact0591 consumer assertion and successor-shape checks may add related Red. Enumerate actual node IDs/results after execution;do not promise a fixed failure count now. Human corrected-test acceptance precedes renewed Phase2 implementation approval |
| E08 | Later implementation changes only operators.py with the declaration/one-byte EOF correction;no Parser/context/body semantics edits. Verify focused,repair114,inherited293,adjacent39,actual consumers/cold imports/pickle,root/spec/all applicable sanity,raw/AST/cohort/export audits and diff whitespace. Final actual-commit-SHA all-blocking rerun remains required;uncommitted-copy smoke is not bypassed. Phase3/delivery stay separate |

Exact accepted future module block (literal order/spelling are guard wiring;
the compatibility contract is exact export set and original object identity):

```python
__all__ = [
    "Any",
    "ParserContext",
    "annotations",
    "parse_operator_expression",
]
```

### Accepted test-only correction paths / clause-to-test plan

| Test file | Authorized change only after future execution approval |
|---|---|
| `tests/liss_0591_guard_support.py` | Add exact E02 declaration to expected new-module wiring;derive algorithm suffix by removing only the one explicitly verified trailing LF. Keep immutable original evidence,raw inverse,baseline hash,carrier substitution maps and closed path inventory unchanged |
| `tests/test_liss_0591_guard_migration_red.py` | Append paired E04/E06 export/EOF positive-negative controls across actual readers and repair pre/post roots. Preserve all existing cases/R1 controls. Existing shape builder uses the corrected expected serialization;never import those AST-only roots |
| `tests/test_liss_0591_consumers_red.py` | Strengthen current P08 subset assertion to exact equality for all3 original modules and retain original attribute/reexport identity assertions. Add actual operators wildcard export/identity coverage in fresh process;exclude new implementation names. Do not change original compile/callback/serialization/cold-order assertions |

E01/E07 additionally adopt unchanged
`tests/test_liss_0592_boundary_red.py::test_r04_actual_public_exports_and_class_identity_stay_available`.
E02/E03/E04 map to existing P01 raw/AST ownership plus new exact serialization
controls;E05 maps to independently pinned22-artifact before/after diff and old
179-node comparison;E06 maps to actual reader/copy and live wildcard tests;
E08 maps to later all-blocking evidence. Exact added node names/counts are a
Phase1 deliverable,not an invented result of this design.

This changes3 of the16 new0591 artifacts,not any of the6 existing carriers.
The remaining19 artifacts of the22-artifact cohort must remain byte-identical.
The whole0592 namespace including its already-approved plumbing is unchanged
relative to this R2 design entry. Existing fixture/hash authorities remain intact.

### Evidence,risks and requested acceptance

Read-only design probe confirms original4 manifest names match Git source
provenance,current9 additional globals,old raw equality rejects declaration-only
and EOF-only proposals,and proposed in-memory AST is valid. Proposal not run
or installed. Source/tests unchanged at dirty HEAD dca93187. Prior Phase2
focused179 PASS/root3230 PASS+1 FAIL remain historical evidence,not fresh design
Green. Runtime/root/spec/all-sanity not rerun for this documentation-only phase.
Later copy closure/dynamic graph and corrected implementation success remain
unproven;Parser3584/class3392 structure disposition stays WP0175-owned.

Received2026-10-19:**LISS-0591 R2補足仕様E01–E08・限定3新規テスト修正方針とPhase 0 acceptance**.
Approval type:phase/design acceptance. Implementation allowed:no. Post-review:
yes;execution batch:N/A. Acceptance does not itself authorize test correction.
After acceptance:request R2 Phase1 test-only execution,review/corrected-cohort
human acceptance,then separate R2 Phase2 implementation approval. No new
Issue/ADR required for this bounded supplement;widening returns to design.

### Human R2 Phase0 acceptance receipt —2026-10-19

Human message uses `ISS-0591`;resolved to LISS-0591,the unique immediately
preceding approval target. E01–E08 and exact3-new-test correction policy accepted
unchanged. E table-row SHA256:
`8a32ec5ed774117f4c8c9903b2ef2cec8528b857f33b2606541b8d680ba1897a`.
P01–P10/B01–B10,immutable fixtures,existing6 carriers and accepted22-artifact
cohort68d6…5547 unchanged. This is design acceptance,not acceptance of future
corrected tests or implementation permission. Source/runtime failures remain
blocking. Next:**LISS-0591 R2 Phase1 Red（限定3新規テスト修正）の実行承認**;
then review/exact-cohort human acceptance before separate Phase2 permission.
No source/test edit,commit,remote action or runtime rerun for this receipt.

## R2 Phase1 execution —2026-10-19 (test review pending)

Received **LISS-0591 R2 Phase1 Red（限定3新規テスト修正）の実行承認**.
Only the accepted3 new-test paths changed plus spec/Issue/WP/trace records.
Production and all other tests/fixtures,including existing6 carriers and19 other
cohort artifacts,unchanged from R2 entry. No implementation/commit/remote action.

- Support adds literal E02 declaration to expected module wiring;checks pinned
  algorithm ends exactly2 LF before removing one LF in new serialization only.
  Raw original evidence,facade inverse,baseline hash,carrier maps unchanged.
- Consumer test strengthens original P08 subset→exact equality for all3 modules;
  all prior identity/behavior assertions remain. New actual fresh-process
  wildcard test verifies exact4 names and typing/context/future/wrapper identities.
- Guard tests append22 nodes:repair pre/post ×11 cases. Every case first proves
  intact positives through0591 parser/operators,0590 parser/operators and0592
  parser readers;20 negative cases reject missing/wrong/extra/duplicate export
  blocks,missing/extra LF,whole/mixed CRLF,whole CR and old flawed Phase2 bytes.
  Actual Git roots are used,not the intentionally failing live owner as setup.

### E-clause / authored node reconciliation

| Clause | Evidence |
|---|---|
| E01/E07 | strengthened `consumers::test_p08_all_original_public_exports_and_reexport_identity`;new `consumers::test_e01_e06_actual_operator_wildcard_exports_keep_exact_names_and_identity`;unchanged0592 R04 adopted |
| E02/E03/E04/E06 | new `guard_migration::test_e02_e03_e04_e06_exact_owner_exports_and_eof_through_real_readers` ×22;existing raw/AST ownership and newline controls retained |
| E05 audit | independent scope/cohort audit;all179 original node identities retained,guard file original prefix unchanged,consumer prefix differs only at accepted equality assertion,other support AST unchanged except expected serialization/constant |
| E06 setup | above actual5-reader paired controls;unchanged R1 ×8 PASS;external data-only corrected-input replay of original8 copy shapes and1 distinct-shape case PASS,not runtime execution |
| E08 gate | production unchanged;later implementation/final-SHA all-blocking obligations remain,not satisfied by Phase1 |

New focused inventory202 = original179 +23 added (22 guards/1 wildcard).
Results:157 PASS/45 Red,0 errors/skips. Red causes:43 exact successor-wiring
rejections plus2 actual export failures (strengthened P08/new wildcard).
Original179 now135 PASS/44 Red;previous dirty Green179 all PASS. These are new
blocking failures after the accepted test correction,not excluded/waived tests.
Many shape/mutation cases stop at invalid live-origin setup;do not count those
rejections as independent effective mutation protection. New22 Git-root cases
prove paired5-reader positives/negatives independently;future live Green needed.

Separate suites:controls30 PASS (22 new guards+8 existing R1,53 deselected),
repair114:90 PASS/24 FAIL (23 wiring+unchanged R04 export),inherited293:
287 PASS/6 FAIL (wiring),adjacent39 PASS,spec161/161 PASS. Prior comparable
repair113/1 and inherited293/0 results become23 and6 additional wiring failures;
original export failure persists. All failures remain blocking outside Phase1;
no root/all-sanity/final-SHA run or full-Green claim for this test-only phase.

Candidate22-artifact cohort (NOT human-accepted):
`467971d66fb895fc6364d40b8f5580b9c62f715c247fe2832c892885f5030bb9`.
Historical accepted68d6…5547 remains intact as provenance,not overwritten.
Per-file hashes,all failure IDs,new23 IDs and test commands/environment/times:
`/private/tmp/liss-0591-phase0.8hzegU/r2red591-*-20261019.{json,out,err}`;
JUnit/audit inputs at `/private/tmp/liss-0591-r2-red-20261019.rRzW1N/`.
Dirty HEAD dca93187,macOS27.0.1 arm64,CPython3.12.6,pytest9.0.3,explicit
PYTHONPATH. Next:**LISS-0591 R2 Phase1 Red テストレビュー実施承認**.
Type:phase/review execution,implementation allowed:no;post-review:yes;batch:N/A.
No agent review pass or corrected-test acceptance claimed by authoring evidence.

## R2 Phase1 review disposition —2026-10-21

Explicit review-execution approval received. Same-context/weaker reviewer pass,
no actionable test finding;human exact-cohort acceptance pending. Candidate
`467971d66fb895fc6364d40b8f5580b9c62f715c247fe2832c892885f5030bb9`
unchanged. Independent inverse of only3 R2 test changes recovers accepted68d6…5547.
Git-derived raw/source probe and actual readers:20 positives/120 rejections;
unchanged8 copy shapes+1 distinct case pass on data-only input,not runtime code.
Fresh focused202 remains157 PASS/45 Red;repair114 remains90 PASS/24 FAIL.
Extended inherited428:422 PASS/6 wiring failures;adjacent31/42 and spec161 PASS.
Different regression selections are not substituted for historical293/39 evidence.
No test/source/fixture changes,no full-Green or implementation approval.
[Review/evidence/limitations](../collaboration/reviews/2026-10-21-liss-0591-r2-phase1-review.md).
Next:**LISS-0591 R2 Phase1 Red テストレビュー／acceptance承認**;
then separate renewed Phase2 permission. Existing live failures are not waived.

## Human R2 Phase1 test acceptance —2026-10-21

Received **LISS-0591 R2 Phase1 Red テストレビュー／acceptance承認**.
Type:phase/test acceptance of reviewed22-artifact cohort
`467971d66fb895fc6364d40b8f5580b9c62f715c247fe2832c892885f5030bb9`.
E01–E08/P01–P10/B01–B10,all fixtures,existing6 carriers and source unchanged.
Review evidence retains its original SHA/environment;no runtime rerun for this
metadata receipt,no Green/failure waiver. Next:**LISS-0591 R2 Phase2 Green／implementation承認**.
Future source scope:only operators.py literal export declaration/one-byte EOF
correction under E02/E03/E08. Implementation allowed:not yet;post-review:yes;
batch:N/A. No source/test edit,commit or delivery permission inferred.

## R2 Phase2 execution / verification —2026-10-21

Received **LISS-0591 R2 Phase2 Green／implementation承認**. Applied only the
accepted literal __all__ declaration and removal of exactly one terminal LF in
operators.py. Parser/context,algorithm,all22 accepted test artifacts,fixtures,
existing6 carriers and P/B/E clauses unchanged. Independent raw before/after
equation and whole Git algorithm AST audit PASS. Actual3 module public export
sets match original manifests;successful wildcard/identity/cold-order/error
serialization and actual private/public consumers now execute in focused/root.

Dirty HEAD dca93187f50594b0417ae88067154baaf3c0ea7c,macOS27.0.1 arm64,
CPython3.12.6/pytest9.0.3,explicit PYTHONPATH. Fresh focused202,repair114,
extended inherited428,adjacent42,root3254 and spec161/161 PASS. Root0 failures/
errors/skips,0 exclusions,423.08s. Compared same-ID reviewer JUnits:45 focused,
24 repair and6 inherited failures resolved;no missing/new/remaining failures
in those comparable suites,all their nodes present in root. Wider suite names
remain distinct from historical293/39 selections;root runs all tests without
active-Red exclusions. Prior whole-root detailed XML unavailable;not a claim
of exact old-root ID comparison or universal behavior coverage.

Compileall,raw/AST/cohort/export/path audit and whole diff whitespace PASS.
Source sizes:parser3584,Parser class3392,operators143,context20,algorithm117;
residual Parser responsibilities remain WP0175-owned,next family gate.
Local applicable sanity9 PASS/1 FAIL:copy smoke rejects uncommitted distributed
spec. PR-only committed traceability not applicable locally,not bypassed or
certified by base=head0 diff. Actual final-SHA all-blocking evidence outstanding;
no Phase2 full-Green/Phase3/final review claim. Source-clean failure is retained,
not a product repair or reason to weaken tests/commit without approval.

Full commands,UTC times/exits/environment/JUnits/compare/cohort hashes:
`/private/tmp/liss-0591-r2-green-20261021.d47y2j/`.
Accepted22-artifact fingerprint remains
`467971d66fb895fc6364d40b8f5580b9c62f715c247fe2832c892885f5030bb9`.
Next:**LISS-0591 R2 ローカルコミット／実SHAで全blocking再検証承認**.
Type:bounded local commit/verification authorization;no further implementation
or test changes,Phase3,remote push/PR/merge authority inferred. Post-review:yes;
batch:N/A. Later source-clean actual-SHA pass precedes Phase3 approval request.

## Approved local checkpoint / actual-SHA verification —2026-10-21

Received **LISS-0591 R2 ローカルコミット／実SHAで全blocking再検証承認**.
Scope:commit the related reviewed feature unit locally,then verify its final
actual SHA. No source/test correction,Phase3,push/PR/merge permission inferred.
Index audit additionally detects the immutable original-primary.txt final blank
at line118,which ordinary unstaged diff checks did not inspect while untracked.
E03 explicitly retains that original evidence/following blank. Preserve its
accepted hash,not trim it or relax production checks. Full feature-diff whitespace
must report exactly that pinned fixture finding;source/other-file whitespace
must pass. This is the existing E03 evidence boundary,not a general exemption.
Separate reviewed test,implementation and record commits keep phase changes
visible. Accepted22-artifact467971d6…0bb9 and all P/B/E clauses remain unchanged.

This checkpoint is written before committing;it does not assert future success.
Current run outcome/actual final SHA/clean-tree evidence is authoritative only in
`/private/tmp/liss-0591-r2-sha-20261021.2BHEPI/result.json` and associated logs.
All blocking suites are rerun after the final record commit;no post-run tracked
record change is permitted without another final-SHA rerun. If temporary evidence
is absent,verification must be repeated,not inferred from this plan.

After a successful all-blocking record:request
**LISS-0591 R2 Phase3 Refactor／review承認**. Otherwise stop on the actual failure.
Implementation allowed:no further edits;post-review:yes;batch:N/A. Final reviewer
pass/human acceptance and delivery remain separate. Issue stays open at the
Phase2/Phase3 review gate;not done or remotely delivered by this checkpoint.

## R2 Phase3 review disposition —2026-10-21

Received **LISS-0591 R2 Phase3 Refactor／review承認**. Feature Path reviewer
execution only;same_context/weaker. Agent pass,no new blocking findings.
No source/test/fixture/6-carrier/acceptance-clause changes. Accepted22-artifact
467971d6…0bb9 retained. Git-derived owner bytes/full facade inverse and narrow
declaration context independently audited without importing migration guard.
Fresh clean26da7f2948020e6f579a2af1b3c27d7a648ea565:focused202,repair114,
inherited428,adjacent42,root3254,spec161/161,sanity11/11 PASS. Same comparable
node IDs,pytest0 failures/errors/skips/exclusions. Export/EOF/error/consumer/
cold-import/serialization/guard controls pass;E03 immutable fixture whitespace
finding remains separately disclosed,not a whole-diff exit0 claim.
Detailed [review packet](../collaboration/reviews/2026-10-21-liss-0591-r2-phase3-review.md)
and external verification preserve environment,argv/times,findings and gaps.
Other grammar remains Parser-owned,class3392 with WP0175 next-family revisit.
These later review records are uncommitted and need final actual-SHA rerun.
Next:**LISS-0591 R2 final verification／レビュー記録コミット・実SHAで全blocking再検証承認**.
Type:phase/final-verification plus bounded local record commit. Implementation
allowed:no further source/test changes;post-review:yes;batch:N/A. No human
final acceptance,push/PR/merge authority inferred;Issue/WP remain open.

## Approved final verification checkpoint —2026-10-21

Received **LISS-0591 R2 final verification／レビュー記録コミット・実SHAで全blocking再検証承認**.
Type:phase/final verification and bounded local record commit. Commit only the
6 related review/status/lesson records;no product/test/fixture changes. Then
rerun focused,repair,inherited,adjacent,root,spec,all applicable sanity,compile,
Git/raw/cohort/export audits and actual committed routing at that final SHA.
This receipt precedes execution and asserts no future success. Authoritative
result:`/private/tmp/liss-0591-final-20261021.mCidKl/result.json`,with per-command
logs/JUnits. Missing evidence requires rerun. No tracked post-run edits without
another full rerun. Next only after success:human **LISS-0591 R2 最終レビュー結果の受入れ**.
Implementation allowed:no;post-review:yes;batch:N/A. No push/PR/merge permission.

## Human final-result acceptance —2026-10-21

Human **ISS-0591 R2 最終レビュー結果の受入れ** resolves to the unique
LISS-0591 target. Accepts final review/result at clean
`71e0965540f0409d6a867f972c177a245a482c76`,not future record-SHA verification
or delivery. External `/private/tmp/liss-0591-final-20261021.mCidKl/result.json`
confirms focused202/repair114/inherited428/adjacent42/root3254/spec161/sanity11
PASS,pytest0 failures/errors/skips/exclusions,same Phase3 IDs. Accepted22-artifact
467971d6…0bb9 and P/B/E clauses unchanged;E03 fixed-evidence whitespace and
documented residual structure/dependency limitations remain explicit.
Records only updated;runtime not rerun for this receipt. Next:
**LISS-0591 R2 受入れ記録コミット・実SHAで全blocking再検証承認**.
Type:bounded local acceptance-record commit/verification. Implementation:no;
post-review:yes;batch:N/A. No commit,push/PR/merge permission inferred.

## Acceptance-record checkpoint authorization —2026-10-21

Received **LISS-0591 R2 受入れ記録コミット・実SHAで全blocking再検証承認**.
Commit only5 related acceptance/status records,then rerun all declared blocking
suites at the new actual SHA. Product/test/fixture/clause/cohort bytes frozen.
This pre-run receipt claims no future success. Actual result and full command/
SHA/environment/timing/JUnit evidence:
`/private/tmp/liss-0591-accepted-20261021.WUeVn4/result.json`.
No tracked post-run edit without another full rerun;missing evidence requires
revalidation. After success,next gate:push/PR/CI/successful-merge authorization.
Implementation:no;post-review:yes;batch:N/A. No remote authority inferred.

## Delivery blocker — CI checkout history (2026-10-21)

PR621 HEAD5b62ab1a pushed after explicit delivery approval. CI39574222927:
root31FAIL/3223PASS,sanity/specSUCCESS;PR remains open,not merged. All31
failures occur before guard assertions,when git show cannot read pinned
22335a57/dca93187 parser evidence. Kernel checkout fetch-depth1 confirmed
in actual log;local full history had hidden this runner precondition gap.
Temporary same-SHA shallow clone:31 same failures/52PASS;only fetching full
history,without source/test changes,then83/83PASS. This is scoped diagnostic
evidence,not a remote retry or permission to weaken Git-provenance checks.
Detailed evidence:`/private/tmp/liss-0591-delivery-20261021.xNStH4/`.
Proposed kernel-tests checkout fetch-depth0 needs explicit bounded design and
phase approval;no workflow/source/test fix performed. P/B/E remain accepted.
Next:**LISS-0591 CI履歴取得修正のScope／Phase 0設計開始承認**.
