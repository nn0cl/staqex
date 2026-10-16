# TypeChecker operator判定本体の分離 — accepted specification

Status:Scope / Architecture Path Phase0 design-start approved2026-10-15.
Dedicated O01–O10,limited four-carrier guard policy and Phase0 explicitly
accepted by Adjudicator2026-10-16. Factory/alias/type boundary and281-line
cohesion disposition accepted for this bounded move. Phase2 implementation
subsequently explicitly approved and performed2026-10-16;final-SHA gates pending.
Owner:[LISS-0590](../issues/LISS-0590-typechecker-operator-body-successor.md),
under accepted [WP-0175](../work-plans/WP-0175-source-responsibility-inventory.md).
Immutable source base:`b5c96f7e4c2a846f41ac8ad5d882f0cb987cd420`.
Phase1 test/scaffolding/four-carrier execution explicitly approved2026-10-16;
Phase2 implementation separately approved2026-10-16. Other bug repair,commit,
Phase3 and delivery remain unapproved.

## Goal / non-goals

Move the sole281-physical-line `_legacy_check_operator` algorithm from
`typecheck.py:1487–1767` into the existing operator family. Preserve all existing
behavior,including diagnostically awkward paths and exceptional state timing.
This is a real body move,not another delegating facade or dead duplicate.

Out:check_unit orchestration,other inference/declaration/evolution bodies,
Ty/TypedExpr relocation/redesign,Parser/Unitarity/Rust,public API retirement,
BUG-WP0175-001/002 fixes,resource-policy changes and new operator support.
No new provider/resource/technology. Existing accepted core decomposition
direction covers the family boundary;no new ADR is presently proposed. Stop
for a new decision if implementation requires moving shared Ty or widening scope.

## Accepted ownership and dependency boundary

| Location | Accepted role (Phase2 implementation authorized2026-10-16) |
|---|---|
| `typechecking/operators.py` | Sole private algorithm `_legacy_check_operator(self: OperatorCheckContext,expr)->None`;existing public `check_operator_expr` forwarding entry retained |
| `typechecking/operator_context.py` (new) | Declaration-only `OperatorCheckContext` and structural `OperatorTypeView`;no constructors,state instances,dispatch or diagnostics policy |
| `typecheck.py` | Existing single live state owner;private import of successor;ordinary bound alias in old method position;small fresh-Ty factory |

Keep public `check_operator_expr(context,*args,**kwargs)` and its existing
TypeCheckContext annotation/import/forwarding behavior. It still dispatches to
`context._legacy_check_operator`,including a legitimate custom context callback.
Do **not** alias TypeChecker to that public wrapper:that would recurse into
itself. Bind TypeChecker to the sole private algorithm instead. Keep the existing
bottom `_check_operator_expr = _legacy_check_operator` class-attribute relation.
Thus recursive private calls still follow the live overrideable hook.

The algorithm's private name is retained specifically for existing private
hook/bound-method-name compatibility;it is not a second legacy implementation.
Retain the receiver spelling `self` as well,so existing unbound keyword calls
to either class hook are not broken merely by the move. It is still the same
live context object,not a new successor instance.
No old algorithm body stays in TypeChecker. No new compatibility installer,
global monkey-patch,wrapper around the class method or hidden state owner.

### Ty construction without a reverse facade import

Keep Ty and its public import/class identity in `typecheck.py`. Add only a
staticmethod `_operator_index_type() -> Ty` returning a **fresh**
`Ty("Meta","Index",DIMLESS)`. It owns no policy,condition or mutable data.
Replace the algorithm's exactly two direct Ty constructor expressions by
`self._operator_index_type()` at the same evaluation points,even where the
result is otherwise unused. Keep the factory in the original Ty/DIMLESS global
environment;do not cache a shared instance or replace it with `_ty_from_ref`.
The latter is a different callback with different behavior and call timing.

The type view exposes only read-only `kind`/`payload` and string presentation
needed by this walk. The context declares live `env`,`diagnostics`,
`semantic_values`,`float_arrays`,`system_registers`,`_binder_depth`,
`_active_register_set`,the factory and existing callbacks:
`_check_index_domain_expr`,`_valid_basis_domain`,`_valid_index_domain`,
`_ty_from_ref`,`_check_operator_expr`,`_require_full_rank_coeff`.
Use structural typing for the existing actual Ty values,not a replacement
runtime type. Mutable env/diagnostics/depth stay on TypeChecker;read-only map
annotations do not imply snapshots or copies.

`typechecking/context.py` and its broader TypeCheckContext remain byte-unchanged.
In particular,do not invent its missing dimension callback as part of this move.
Internal modules must not import the public typecheck facade,including through
TYPE_CHECKING,lazy imports or a shared-type backdoor. Prefer the existing AST
model and standard typing only. Preserve all previous public exports/imports;
do not remove TypeCheckContext/Any merely because the new algorithm does not use them.

## Acceptance O01–O10 (accepted2026-10-16)

### O01 — exact algorithm and sole implementation owner

Given immutable original method evidence,when the body moves,then its complete
AST including docstring and literal values remains equal under only named
normalizations:receiver/local type annotations,and the exactly two
Ty-construction→factory-call substitutions. No branch,return,comparison,callback,
diagnostic or exception scope changes. Unknown/nonmatching OpExpr forms continue
to fall through with None. Public forwarding entry does not become an algorithm
copy. No implementation function remains behind the class alias.

### O02 — finite domains and ordered diagnostics

Given IndexDomain/RevDomain,TypeRef or named binder domains,when checked,then
callback order,diagnostic code/message/span/order and continuation are unchanged.
Minimum cases:Index/Rev callback;valid/empty/invalid Basis;static-register capacity
overflow;valid/invalid/inclusive Index,empty inclusive range;other TypeRef;
named unknown/Execution/nonfinite/Meta/Discrete/Set carriers;resource threshold
exactly1,000,000 versus greater. Preserve multiple diagnostics and unconditional
`_ty_from_ref` calls after TypeRef branches. Do not add domain validation or
silently stop after appending a diagnostic.

### O03 — live binding,depth and successful restoration

Given no prior binding,a prior actual Ty,or a mapping key whose value is None,
when a binder succeeds,then temporary type assignment,depth increment,body hook,
full-rank callback,depth decrement and env restoration/pop occur in original
order. The None-valued prior key is popped as before,not newly preserved using
membership testing. Valid Basis uses `_ty_from_ref`;other binding paths create
a fresh Meta/Index Ty. Preserve both constructor evaluation sites. Nested binders
and context map replacement by callbacks must observe live owner fields;do not
cache local copies of env/diagnostics or flatten callback recursion.

### O04 — exceptional timing is preserved,not repaired

Given a body hook or full-rank callback raising Exception or BaseException,
when depth was incremented,then the `finally` decrements depth and the original
exception propagates. **The subsequent env restoration is skipped**,so the
temporary binding remains unless a callback itself changed it. Failure before
the try/increment has no new cleanup. Failures in diagnostic append,env access,
restoration or factory propagate at their existing position;no added catch,
rollback or finally around env. This scope makes no judgment that the behavior
is desirable;any later cleanup semantic change needs separate approval/tests.

### O05 — compound/indexed/call walk order and predicates

Given OpBin,walk lhs then rhs,then full-rank checks only at positive binder
depth. Given OpIndexed,walk base then index before the same coefficient,
Execution-index,multi-register ambiguity and unknown-register checks. Preserve
create/annihilate/Float-array exemptions,active-register None behavior and
register-qualified positives. Given OpCall,preserve retired I/X/Y/Z diagnostics,
Measure/log/write/send effect diagnostics,and ordered argument recursion.
Pair neighboring accepted forms with rejections;no new accepted syntax or
unitarity/evaluator/finite-lowering responsibility moves into this walk.

### O06 — public entry/private binding/type identity and consumers

Given a real TypeChecker,then its `_legacy_check_operator` and
`_check_operator_expr` are ordinary bound aliases of the sole successor,not of
the forwarding wrapper. Public entry retains positional/keyword forwarding to
a custom context as well as actual TypeChecker behavior. Recursive subclass/
instance hook overrides and unbound `self=` keyword calls remain effective.
Ty import,constructor and identity remain stable. Ty's
existing serialization path stays unchanged;fresh factory values are real Ty.
Exercise ordinary real-checker bound-method pickle round trips for both hooks;
arbitrary subclass/custom-pickle compatibility remains unassessed,not assumed.
Run cold requested import orders for typecheck/typechecking and actual pipeline/
HIR consumers. Two import orders do not prove a complete cycle-free graph.

### O07 — untouched state,facade and other contracts

Given the restored original facade shape,then every other method/import/class/
alias/state initialization is unchanged. Allow only one private successor import,
one ordinary `_legacy_check_operator` alias at the original class position and
the exact fresh-Ty factory. Preserve the bottom alias and all unrelated
TypeChecker numeric repair behavior/diagnostics. TypeCheckContext,Parser,
dimensions,AST models,HIR/pipeline/Unitarity and runtime owners are unchanged.
Public-symbol inventory derives real `__all__` or non-underscore exports,not a
hand-picked export list. No source/test deletion or new provider dependency.

### O08 — real consumer and adjacent-regression evidence

Given existing valid/invalid source programs,when compile_source and module
paths typecheck them,then ordered diagnostics/spans and resulting env/typed
evidence match the baseline;HIR still sees the same completed checker data.
Include operator binders,Basis/Index/reverse/Set domains,multi-register sites,
finite binder pipeline and inherited opaque-wire numeric rejection/legal gates.
Real mechanics fixtures for exceptional callbacks are separate from evidence
that normal source plans reach those exceptions. No broad functionality or
past-deletion/no-regression claim follows solely from structural tests.

### O09 — bounded guard transition without refreshing history

Given the immutable LISS0584/0587/0588/0589 evidence,then allow exactly the
carrier changes below. Preserve all original fixtures/hashes/path sets/semantic
assertions and their original provenance. Validate the entire live successor,
context and factory/hook wiring **before** reconstructing old source/AST.
Missing/changed/duplicate owners,extra state/imports and unrelated method edits
must still be rejected. Pre/post named shapes must be genuinely distinct copied
roots,not labels on one extracted tree. Exercise the real old guard functions,
their mutation tests and actual inherited fixture-copy setup.

### O10 — phase/verification/structure gates

Before Phase2,accept exact Phase1 behavior/ownership/consumer/guard artifacts.
After final commit,every declared blocking suite must run against that actual
clean SHA;focused success alone is not Green. No hash/assertion weakening,
blanket exclusion or skipped failed check is authorized. Resolve effective
routing on actual diff;unknown graph/owner metrics remain gaps. Phase3/final
verification/commit and remote delivery remain distinct human gates.

## Consumer inventory / provenance

Base full typecheck SHA256:
`917279f48ecb0ff4be1cdce6728b2046d1931bb5b3fc71aa76bb05f1ce58b0ca`.
Whole original method AST SHA256 (`ast.dump`,include_attributes=False):
`63f70dd610d3714f3bb10ce579b4b166acbe963bcf048c18b128f2357bbc3599`.

- Source callers:`typecheck.py:430` main check,1387 assignment/operator check,
  2349 second-quantized check;recursive body1660/1671/1672/1678/1679/1766;
  bottom private alias4629. Family public wrapper:`typechecking/operators.py:14`.
- Actual production users:`pipeline_legacy.py:61,854` creates checker;
  `hir_legacy.py:44,167` consumes Ty/TypeChecker and completed typed state.
- Existing tests:0546 family entry/exposure;0584 numeric repair/boundary;
  0587/0588/0589 readonly guards;mathematical/Basis/rev/finite binder,
  multi-register,operator-body tests. CLI/run/host use pipeline facade;
  no Python CLI entrypoint or plugin registration change is proposed.
- Static all-tracked-Python scan found the named attribute usages in the above
  production files. It is not a full receiver/dynamic/plugin graph. Whole
  unbound-function metadata/custom serialization compatibility is not proven
  by keeping a hook name;scope-specific tests must report their limits.
- External detailed discovery:`/private/tmp/liss-0590-phase0.h3JvR7/inventory.json`.
  Immutable counts and hashes needed for recovery are recorded here and Issue.

## Accepted limited guard-carrier policy

Only these **four existing test files** may be edited after explicit Phase1
execution approval;no change is made in Phase0:

1. `tests/test_liss_0584_repair_boundary_red.py`:apply exact operator/factory/
   import inverse projection before existing numeric-body masking. Preserve
   its unaffected digest,all mutation assertions and numeric signature protection.
2. `tests/test_liss_0587_partial_ownership_red.py`:readonly byte projection only.
3. `tests/test_liss_0588_closed_ownership_red.py`:readonly byte projection only.
4. `tests/test_liss_0589_capture_ownership_red.py`:readonly byte projection only.

Their loops/counts/expected hashes remain authoritative. The old readonly
manifests pin `typecheck.py` bytes,so AST-unparse equivalence is insufficient.
Use a strict reversible raw-source reconstruction:undo only the exact permitted
import,old-method→alias,factory insertion at fixed anchors;restore the immutable
original method bytes. Then the **original full-file byte hash** must match.
Unchanged outside bytes must survive reconstruction. Reject ambiguity or
unrecognized formatting instead of recomputing a baseline hash.

0589 also pins `test_liss_0588_closed_ownership_red.py` bytes. Add an exact inverse
of that carrier's named helper import/read substitution,using pinned original
carrier evidence;unrelated carrier edits must fail its original hash. There
is no recursive permission to rewrite arbitrary test files. For all non-allowlisted
readonly paths,hash the original bytes directly. New AST projection must also
retain deliberately introduced old numeric/other-method/new-state mutations;
never reconstruct the whole checker from a fixture and erase the mutation.

New test-only helper/fixtures/tests may live at `tests/liss_0590_guard_support.py`,
`tests/test_liss_0590_operator_{behavior,consumers,ownership,guard_migration}_red.py`
and `tests/fixtures/liss_0590/`. Preserve whole original method literals by parsing
the original class-indented bytes,not silently dedenting docstring content.
Pin method/source/carrier evidence with explicit base/hash. No production use
of fixtures,Git or baseline-restoration code. New copied roots include the real
typecheck/operator/context files;proposed post-shape ASTs are never runtime
implementation or proof of eventual cold imports. Existing old copy helpers
remain unchanged unless a newly demonstrated conflict receives a new bounded
disposition. No fifth carrier or manifest update is implicitly allowed.

Immutable fixture hashes (unchanged):

| Fixture | SHA256 |
|---|---|
| LISS0584 repair-boundary | d0d2c74d0552fd31a6894ea7d2908e4ea506fd639e5d986c2ed40423f3fc4bd3 |
| LISS0587 readonly | 666be68bafa1b27611f59877c7fb47778e00838c5534760118d54f86c13ccc1d |
| LISS0588 readonly | 9155dadf4440560188e58a29ae7a44b6009b2241fb6f71b3658f5748543e6bdf |
| LISS0589 readonly | e8ad62914008d2ad725c5f3f2aee04b6364ebb0dd658c55039ac4c331eeb9fe3 |

## Minimum Phase1 evidence matrix

| Clauses | Required evidence (new exact nodes named during Phase1 review) |
|---|---|
| O01/O07 | complete installed algorithm/protocol AST versus original;body absent from class;extra/missing body/import/state/context/factory negatives |
| O02 | each domain category and neighboring accepted/rejected boundary listed above;exact ordered message/span and callback trace |
| O03/O04 | prior absent/Ty/None bindings,nested success,live map replacement,fresh Ty counts;body/rank/factory/append exceptions and exceptional env/depth state |
| O05 | ordered binary/index/call children,depth-dependent full-rank timing,all exemptions,register-qualified positives and each diagnostic |
| O06 | actual class/bound aliases,custom public forwarding,override hooks,Ty identity,bound pickle and two cold import orders |
| O08 | real compile_source/binder/module/HIR smoke plus adjacent inherited suites,not only a context stub |
| O09 | real pre/post copied guards,unchanged original fixtures,raw-byte restoration,original numeric-signature/other-body/state mutations,changed/missing successor and changed-carrier negatives |
| O10 | exact reviewed bytes,readiness,final-SHA full blocking and routing record |

## Structure and verification profile

The281-line walk stays one cohesive ordered algorithm for this mechanical move;
it remains above the accepted150-line review guideline. This bounded cohesion
disposition was accepted2026-10-16,not a claim of complete TypeChecker cleanup. Splitting its
branches simultaneously would obscure equivalence. Measure actual new owner/
facade/context lengths after implementation and report them,not estimated
facade reduction only. Further internal factoring needs its own reviewed scope.
Live TOML has same_context/host,empty model IDs,no numeric/large_change override.
Inherited TypeChecker size and unknown semantic owners remain disclosed gaps.

Declared implementation blocking from repo root,Python3.12/PYTHONPATH root:
`python3.12 -m pytest tests/ -q --tb=short`,
`python3.12 tests/spec_verification/run_all.py`,and every applicable actual CI
repository-sanity step in `.github/workflows/ci.yml`,including PR traceability
in actual PR CI. No root exclusions preapproved. Phase1 reports structural
Red separately from passing characterization;does not claim full Green.

Focused:new0590 suites. Consumer/adjacent:0546,0584numeric/guard,0587–0589readonly,
mathematical/Basis/rev/finite/Set binder,multi-register,real pipeline/HIR;
add actual missing consumers discovered before removal rather than ignore them.
Full final source-clean/copy-smoke and original baseline captures remain
blocking. Compare failures with comparable baseline;capture exact SHA,dirty
state,environment,command,timing,fail/error/skip/exclusion counts. Required
isolation unavailable or unknown measurements must not be silently downgraded.

## Current gate

Human acceptance received2026-10-16:
**LISS-0590 専用Issue/spec O01–O10・限定guard移行方針とPhase 0 acceptance**。
The exact O01–O10,three-file production boundary/fresh-Ty factory,public/private
compatibility strategy,281-line cohesion rationale and four-carrier-only guard
policy are accepted. Phase1 execution was subsequently explicitly approved
2026-10-16 and tests/limited guard transition authored;no production changes.
Initial Phase1 test review2026-10-16 requested R1 correction:factory-exception
test reached an earlier conversion. Bounded correction/re-review then explicitly
approved and executed;R1 closed in same_context agent re-review after actual
site/count and negative-control verification. O01–O10 itself is unchanged.
See [review summary](../collaboration/reviews/2026-10-16-liss-0590-phase1-test-review.md).
Corrected Phase1 tests/re-review explicitly accepted by Adjudicator2026-10-16:
117nodes/exact16-artifact SHA256
`12426ae6b89a222a40eb0cf25f66cdbe018cc786d7ae75c1b5477d168dfbed3b`.
Phase2 execution/implementation subsequently approved and performed2026-10-16.
Sole body/narrow context/factory installed;accepted test bytes unchanged.
See [Phase2 verification](../collaboration/reviews/2026-10-16-liss-0590-phase2-verification.md).
Focused117/root2938/spec161 pass;source-clean/copy-smoke/final-SHA blocking
gap remains. No all-blocking/full-Green claim from dirty-tree test success.
Local commit/actual-SHA full-blocking rerun explicitly approved2026-10-16.
Current clean-SHA execution evidence is external:
`/private/tmp/liss-0590-sha.v0SnLA/verification.json`;this pre-commit record
does not predeclare its result. After all applicable checks PASS,next approval:
**LISS-0590 Phase 3 Refactor／review承認**。
Phase3/final review and remote delivery remain separately unapproved.
Clause-to-node mapping,exact authored-byte fingerprint and provisional Red
evidence live in the [representative trace](../collaboration/traces/2026-10-15-liss-0590-typechecker-operator-body.md).
The O01–O10 contract is unchanged;Phase1 acceptance did not itself authorize
implementation. Phase2 used the later explicit permission,not an inferred gate.
