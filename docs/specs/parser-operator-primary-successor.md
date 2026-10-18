# Parser operator-primary本体分離 — accepted specification

Status: accepted / P01–P10,limited guard policy and Phase0 accepted2026-10-16.
Scope/Architecture Path Phase0 design-start explicitly approved2026-10-16.
Dedicated Issue/spec and bounded ownership/error-factory/structure dispositions
explicitly accepted by Adjudicator2026-10-16. Phase1 test/limited-guard execution
approved2026-10-16;baseline readiness check exposed P08 conflict below before
any test/guard edits. Execution paused for bounded specification disposition.
Owner:[LISS-0591](../issues/LISS-0591-parser-operator-primary-successor.md),
parent:[WP-0175](../work-plans/WP-0175-source-responsibility-inventory.md).
Immutable source base:`22335a5768c17a41eb94682e7dd14d3e6df004bd` (PR618/main CI passed).
Authority:accepted [core decomposition](staqex-core-module-decomposition.md).
Phase1 test/guard permission is bounded by this specification;no implementation,
commit or remote delivery permission.

### Current blocker — P08 baseline compatibility

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
Next:0592 final result accepted at2c1a3cae;acceptance-record/SHA and delivery
gates remain,then0591 repaired-
baseline handoff acceptance. Implementation allowed:no for0591. Post-review
required:yes,then resume bounded Phase1 execution under agreed baseline,followed by
test review/exact acceptance,Phase2 implementation,Phase3,final verification and
delivery gates. Batch:N/A. BUG-WP0175-001/002 stay plan-owned and unapproved.

Repair Phase1 execution separately approved/authored2026-10-17;tests/limited
two-carrier plumbing only,no production change. Current results and next review
gate owned by0592 Issue/spec/trace. This does not revise P01–P10 or accept a
new0591 baseline;0591 stays blocked until actual repair/reviewed handoff.
