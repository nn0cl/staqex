# ParseError serialization repair — accepted R01–R07

Status:accepted2026-10-17;R01–R07,limited guard policy,0591 dependency policy
and Phase0 explicitly accepted by Adjudicator. Scope/design-start authorized
proper repair,not accepting failure. Phase1 execution separately approved2026-10-17;
Red authored;R1 test-only correction/re-review approved and executed2026-10-18.
Agent re-review passed;corrected tests explicitly accepted2026-10-18.
Phase2 Green/implementation approved2026-10-18;exact repair implemented,
focused Green. Local commit/actual-SHA all-blocking revalidation approved2026-10-18;
clean342ea6cc all-blocking passed. Phase3 approved/executed2026-10-18;agent
review passed without source/test edits. Review-record commit/actual-SHA rerun
approved2026-10-18;outcomes external,not pre-claimed in verification target.
Owner:[LISS-0592](../issues/LISS-0592-parseerror-serialization-repair.md).
Parent:[WP-0175](../work-plans/WP-0175-source-responsibility-inventory.md).
Source base:22335a5768c17a41eb94682e7dd14d3e6df004bd.
Dependent:[LISS-0591](../issues/LISS-0591-parser-operator-primary-successor.md).

## Goal / cause / scope

Restore a real successful default pickle round-trip for the existing ParseError,
without weakening LISS0591 P08 or mixing grammar extraction with behavior repair.
Current constructor requires message,line,col,but BaseException.args only stores
message. Default reconstruction therefore calls it without line/col. Protocols
0–5 fail loads,as do copy.copy/deepcopy at the base;dumps succeeds. This does not
imply normal compilation/diagnostics are broken.

Keep class in compiler.staqex.parser,public signature and normal construction
unchanged. Accepted design:explicit `ParseError.__reduce__` with original
type,constructor fields,args and normal instance state;private module-level
`_restore_parse_error(error_type,message,line,col,args)` reconstructs compatible
class and restores args independently. Dictionary state applied after allocation
retains custom code/attributes/notes and normal pickle memo handling. No mutable
global registry,copyreg patch,custom Unpickler,test-only reducer or external SDK.
Exact method/helper AST and raw source boundary must be frozen during Red review,
not silently broadened in Green. No implementation prototype executed in Phase0.

Allowed production delta:only addition of that reducer/private helper in
parser.py;existing constructor and every grammar/token/recovery method unchanged.
No class relocation,error-factory introduction,operator extraction or change to
message/code/Span formatting. No provider/port/new dependency/technology/ADR.
Class remains large because the separate0591 migration is intentionally not
performed here;owner WP0175,remaining grammar addressed at later family gates.

## Acceptance R01–R07 (accepted2026-10-17)

| ID | Given / when / then; minimum Red inventory |
|---|---|
| R01 | Given actual ParseError with empty/ASCII/Unicode/newline message,default/custom code,and representative coordinates,when default pickle and each protocol0..HIGHEST_PROTOCOL dump/load it,then restored type is exact original class and message,line,col,code,args,str and repr remain equal;fresh object,not shared cached instance |
| R02 | Given real errors raised by Parser._expect and operator-primary cardinality paths,when serialized and loaded in a fresh Python interpreter importing the public class,then restoration succeeds and catching through public ParseError works. Include both requested facade-first/parsing-family-first import orders,not only same-process object equality |
| R03 | Given pickleable extra attributes,nested mutable metadata,exception notes and independently changed args versus message,when round-tripped,then full instance state and args survive without normalization/drop;aliasing/self-reference in ordinary extra state survives memoization. copy.copy gives fresh exception with shallow state references;deepcopy preserves value while separating nested mutable state. Original remains unchanged |
| R04 | Given existing constructor calls/default/custom code and invalid missing arguments,when ordinary construction/raise/catch occurs,then signature,args,str/repr,fields and existing TypeError behavior remain unchanged. AST/error/import class identities preserved. No broadened optional line/col or positional code argument to work around pickle |
| R05 | Given normal valid and invalid sources,when pipeline,module loading and access metadata consumers run through their existing entrypoints,then status and exact ordered diagnostics retain code/message/line/col and prefix formatting. Compare immutable baseline in same environment;fake serialization results or bypassing actual ParseError are insufficient |
| R06 | Given original parser/production/guard evidence,when exact approved reducer/helper are added,then historical readonly guards still accept only this shape and reject changed constructor,grammar,reducer/helper args/state behavior,extra import/state,missing helper and changed original evidence. All previous TypeChecker positive/negative and actual temporary-copy guards stay effective |
| R07 | Given completed repair,when all focused,consumer,adjacent and all blocking suites run at final actual clean SHA,then all pass without exclusions/weakening;capture diagnostics/export/AST/hash evidence and make repaired baseline available for0591. P08 remains successful AST/error round-trip;dependent scope resumes only after compatible-baseline handoff accepted |

Subclasses with additional required constructor arguments/custom serialization,
unpickleable user attributes and arbitrary cyclic constructor args are outside
the base-class guarantee;no such project subclass was found in scoped search.
Older blobs emitted by the broken default reducer already lack construction
arguments:do not claim this new writer retroactively makes those loads valid.
If external stored blobs need migration,stop and specify a separate recovery
contract. No untrusted pickle input is accepted or loaded by production as part
of this change;tests use only self-generated trusted data.

## Accepted guard preservation policy — exact two existing carriers

parser.py is byte-frozen by0587/0588/0589 and0590 manifests. Keep all their
original hashes/fixtures and original TypeChecker evidence immutable.

1. `tests/liss_0590_guard_support.py`:only parser.py reads route through new
   standalone0592 test-only inverse (no import cycle with0590). This verifies
   exact reducer/helper AST and removes only their approved raw blocks before
   comparing old parser bytes. Existing TypeChecker/carrier logic untouched.
2. `tests/test_liss_0590_operator_ownership_red.py`:its readonly source loop uses
   the verified reader for parser.py. Existing production-path allowance remains
   unchanged because this repair adds no production file. All other assertions
   untouched. Pin both original carrier files and exact permitted substitutions.

No0585 copy-helper,0590 migration-test or0587/0588/0589 carrier edits proposed.
The repair adds no imported production module,so no new parser dependency file
needs copying. New0592 tests must invoke the real0587/0588/0589/0590 guards and
inherited copy fixtures on genuinely distinct raw Parser pre/post roots,crossed
with TypeChecker shapes where supported;assert shape before/after copy so a
copy cannot erase the selected repaired state. Negative controls include full
raw mutations outside the repair and altered reducer/helper/state contracts.
No guard assertion/hash relaxation or generic whole-file replacement.
Additional protected-path need returns to bounded design approval.

## Integration with0591 — accepted prerequisite policy

0592 must establish a reviewed repaired baseline before0591 starts authoring
its extraction tests. Keep accepted P01–P10 behavior and successful P08;do not
characterize failure as success. The old22335a57 measurement remains historical.
At prerequisite handoff,pin new actual SHA,whole source hashes,exports and
ParseError repaired methods as readonly0591 evidence;no stale baseline copying.
0591's existing3-carrier future policy must explicitly compose verified0592
inverse with its primary-body inverse,without replacing0592 tests/evidence.
Reconcile that composition and source-base amendment for human acceptance
before resuming0591. Neither this dependency nor prior0591 Phase1 authorization
approves repair tests/implementation or new dependent acceptance text.

## Verification / review gate

Fresh read-only2026-10-17 evidence at22335a57,macOS27.0.1 arm64/Python3.12.6:
12 pickle-load failures (6 protocols ×2 codes),2 copy/deepcopy failures,
real bracket-cardinality ParseError fields retained. External probe:
`/private/tmp/liss-0592-phase0.V3uVCF/probe-data.json`;command metadata/stdout/err:
`/private/tmp/liss-0591-phase0.8hzegU/repair-phase0-probe.*`.
Probe exit0 means defect inventory finished,not repaired product Green.
No fresh root/spec/regression suite this design turn;previous results historical.

Later required checks:dedicated R01–R07 tests;actual pickle subprocess/copy tests;
0590/0585–0589 real guard and copy suites;existing0547,Pauli/factory,DiracF/D,
PQN/binder regressions;root `python3.12 -m pytest tests/ -q --tb=short`;
spec `python3.12 tests/spec_verification/run_all.py`;all applicable sanity steps
from .github/workflows/ci.yml;compileall,exports/scoped cycle/whole-source inverse
audit and committed review-change routing. Focused versus all-blocking,actual
SHA/environment/times/failures/exclusions separate;rerun all blocking after final
commit. Review.same_context is weaker than separate_context,no enabled override;
full dynamic graph/custom serialization remain unassessed,not zero.

Received2026-10-17:**LISS-0592 修復仕様R01–R07・限定guard移行方針・0591依存方針とPhase 0 acceptance**.
Type:design/phase acceptance. Approved scope:real serialization repair design.
Phase1 execution explicitly received2026-10-17 and tests authored.
Review and R1 correction/re-review approved/executed2026-10-18;R1 closed in agent review.
Corrected-test acceptance explicitly received2026-10-18,cohort pinned below.
Phase2 implementation explicitly approved2026-10-18;bounded repair executed.
Local commit/actual-SHA revalidation explicitly approved2026-10-18.
Phase3 explicitly approved/executed2026-10-18;agent review passed.
Final verification/review-record commit/actual-SHA rerun approved2026-10-18.
If all blocking passes,next:**LISS-0592 最終レビュー結果の受入れ**.
Implementation allowed:only approved repair,now written. Post-review required:
yes,review-record commit/actual final-SHA all blocking,human final acceptance/delivery.
Batch:N/A. No failure-preservation amendment to0591 P08 authorized or made.

## Phase1 execution evidence —2026-10-17 (not test acceptance)

R01–R07 table,guard policy and dependency policy above unchanged.
Test files under tests/;guard constants REDUCER/RESTORER in
`liss_0592_guard_support.py` freeze the exact proposed AST/raw addition for
review. Temporary source shapes are parsed/compared only,never imported,
compiled or executed. Only two accepted existing carriers were edited.

| Clause | Authored evidence / current status |
|---|---|
| R01 | test_liss_0592_serialization_red.py::test_r01_all_protocols_restore_actual_class_and_fields —56 behavioral Red nodes,default plus protocols0–5 |
| R02 | same file::test_r02_real_raised_errors_round_trip_in_fresh_import_orders —6 behavioral Red nodes,real _expect/bracket/brace cardinality errors,two import orders |
| R03 | same file::test_r03_pickle_preserves_extra_state_aliases_notes_and_independent_args / test_r03_copy_semantics_preserve_original_and_mutable_state —7+2 behavioral Red nodes |
| R04 | same file::test_r04_* plus test_liss_0592_boundary_red.py::test_r04_* —7 passing constructor/invalid-call/export/class/AST checks |
| R05 | test_liss_0592_consumers_red.py —9 real pipeline/_parse_file/find_module_info snapshots and1 altered-evidence rejection pass;valid/error status and full ordered diagnostics pinned |
| R06 | test_liss_0592_guard_migration_red.py —17 passing distinct-shape/copy/mutation/evidence nodes;boundary file has2 passing preservation nodes and1 expected missing-repair structural Red |
| R07 | boundary tests freeze production/old tests/exports;293 inherited+39 adjacent pass. Full blocking/final actual clean SHA and accepted repaired-baseline handoff are later obligations,NOT satisfied by Phase1 |

Dedicated final:72 expected failures/36 passes (108 total);71 reconstruction
failures plus1 structural failure. All108 collected,no skip/xfail/exclusion.
Normal consumer source named cardinality in corpus is an invalid operator
declaration and produces the baseline block-expression diagnostic;actual
cardinality exceptions themselves are independently exercised directly by R02.
Consumer snapshot was generated only after checking every compiler file against
Git22335a57;full status/diagnostics stored in immutable consumer-baseline.json.
SHA256:180fb8c72fabd8f20ee54efbe1c9940ce29fd28abb9edb7496cdd9011b5738ae.
Original source/carrier manifest SHA256:
dfc6c92bc7ca9d5f0a46c181fec1cde0613e1ab35b995100d737ff63d075d45a.

Actual dirty HEAD22335a5768c17a41eb94682e7dd14d3e6df004bd,
macOS27.0.1 arm64/CPython3.12.6/pytest9.0.3. Focused run
2026-10-16T18:37:42Z–18:37:54Z (JST2026-10-17),exit1 expected Red;
inherited293 exit0,adjacent39 exit0. Full command/environment/dirty-state/output
in `/private/tmp/liss-0591-phase0.8hzegU/r592-focused-final.*`,
`r592-inherited.*`,`r592-adjacent.*`. No final commit or all-blocking claim.
Root/spec/all-sanity not_run;Phase1 does not authorize making them Green by
exclusion or executing a prototype repair. User test review/acceptance and
separate Green implementation approval remain mandatory.0591 remains blocked.

## Initial Phase1 review disposition —2026-10-18 (historical)

[Same-context review](../collaboration/reviews/2026-10-18-liss-0592-phase1-review.md)
requires changes. R01–R07 and accepted policies unchanged. R1:new parser inverse
uses read_text() and normalizes raw newlines,accepting unapproved LF→CRLF/CR
changes on both original/proposed roots(all6 independent mutations reproduced).
This fails R06 exact raw preservation despite unchanged72 expected Red/36 pass
and293 inherited/39 adjacent passes on fresh dirty22335a57 verification.
No current source corruption/runtime grammar regression is claimed.
Proposed test-only correction:preserve raw bytes through the inverse and add
newline negatives on both shapes;keep fixtures/hashes/raw approved additions
unchanged. Review did not edit tests or implement repair. R1 fix/re-review,
human corrected-test acceptance and separate Green approval remain distinct.

## Current R1 corrected-test disposition —2026-10-18

Explicit R1 test-only correction/re-review approval received and executed.
Only new guard read_text→read_bytes().decode("utf-8") and6 parametrized
byte-written newline negatives added in the authorized migration test. Both
pre/post shapes and direct/inherited readers tested;equal AST does not waive
raw byte preservation. Before correction6 negatives fail;after correction6 pass.
Independent Git-built positive4/negative12 reader checks pass;R1 closed in agent
re-review. Exact AST/raw approved additions and all fixtures/hashes unchanged.

Current114 nodes:72 expected Red/42 passes,0 errors/skips/exclusions. Original108
node IDs/outcomes unchanged,new6 negatives pass;inherited293/adjacent39 pass.
R06 migration module now23 passing nodes;other clause mapping above remains
historical evidence with no acceptance requirement weakened. R07 clean final
SHA/all blocking and0591 repaired-baseline handoff remain open. Same-context
review is weaker isolation,not human acceptance. No production repair executed.
Corrected12-artifact cohort SHA256:
3d77b2159acb72ad9aae73f347e3f85c20492098706bbca58f20618fb765029e.
Full current evidence and exact two-file hash/diff check in
[review packet](../collaboration/reviews/2026-10-18-liss-0592-phase1-review.md).
Human corrected-test acceptance received2026-10-18 for this exact12-artifact
cohort and R1 re-review. Acceptance does not change R01–R07/guard/dependency
clauses or authorize implementation,commit,remote delivery or0591 resumption.
Next:separate Phase2 Green/implementation approval. No runtime rerun in this
metadata-only turn;R1 results above remain historical,not a new full Green.

## Phase2 implementation evidence —2026-10-18

Explicit Phase2 Green/implementation approval received. Only parser.py adds
reviewed reducer/private restorer;signature/constructor/error/grammar bytes
outside those raw additions unchanged. Standard pickle applies copied dictionary
state after construction,retaining independent args,custom code/notes/ordinary
state graph;no custom Unpickler,registry or production loading entrypoint.
15 physical lines added,whole source3679→3694. Accepted12-artifact cohort
3d77b215…65029e and all fixtures/hash authority unchanged. No new imports/modules;
actual pipeline/modules/access consumers and both requested cold import orders
preserve public ParseError identity. Scoped import equality is not full dynamic
graph proof. Large Parser retained for separately gated0591 migration.

Fresh114 focused/293 inherited/39 adjacent/spec161 pass at dirty22335a57;
same114 IDs,72 prior Red resolved/0 new failures. Root3052 pass (0 errors/skips).
All-blocking not Green:copy smoke rejects uncommitted distributed repair spec,
same exact failure reproduced before implementation;other9 applicable sanity
checks pass. PR committed traceability N/A until PR/actual commits. No bypass,
exclusion,waiver or finalized0591 baseline. Final actual-SHA full rerun still
required. Scope/authority/results in representative trace;no commit/remote
permission inferred from implementation. Next:local commit/actual-SHA all
blocking approval,then later Phase3/final gates. R01–R07 unchanged.

## Authorized actual-SHA verification boundary —2026-10-18

Human local commit/all-blocking revalidation approval received (ISS-0592 typing
resolved to unique LISS-0592 target). Commit related24-file unit only;frozen
test cohort/source/acceptance unchanged. This record belongs to the commit
about to be tested,so outcomes and exact SHA live outside Git after verification
under `/private/tmp/liss-0592-sha-20261018.hlxElM/` and runner sha592 labels.
No future result is claimed here. Verify root/spec/all applicable CI sanity,
consumer/adjacent/guard/import/compile/audit and committed routing at actual
clean SHA;no new commit afterward in this gate. If successful,next is separate
Phase3 approval,not execution/delivery or0591 repaired-baseline acceptance.

## Current Phase3 evidence —2026-10-18

[Review packet](../collaboration/reviews/2026-10-18-liss-0592-phase3-review.md):
same-context agent review passed,no new actionable finding. Exact repair and
accepted tests/fixtures/clauses unchanged;no additional refactor warranted.
Clean342ea6ccd41191c6b321f5fce705e2712f83ebd3 rerun:114 focused,293 inherited,
39 adjacent,3052 root,161 spec and11 applicable local sanity checks pass;
0 failures/errors/skips/exclusions. Consumer/import/raw+AST/probe/frozen cohort
checks pass;external p3-592 evidence in packet. R07 final-record SHA validation/
human acceptance/0591 baseline handoff remain open. Current record edits are
not a new verified final commit or remote CI.
