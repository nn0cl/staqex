# Evaluator classical-scalar capture successor — accepted specification

Status: Scope / Architecture Path Phase0 design-start approved2026-10-14.
Dedicated Issue/spec S01–S09, bounded guard transition and Phase0 acceptance
approved2026-10-14. Accepted clauses unchanged. Phase1 acceptance-test creation
and limited guard migration execution approved2026-10-14 and performed.
Phase1 agent test review passed2026-10-14;human exact11 test artifacts accepted
2026-10-14,review-packet/current hashes match. Phase2 Green/implementation
explicitly approved2026-10-14;minimal move written,accepted tests unchanged.
Scoped local commit/actual-SHA all-blocking revalidation explicitly approved
2026-10-15 and passed at clean28530388. Phase3 Refactor/review explicitly
approved2026-10-15;agent review passed,no source/test changes needed. Final
verification/review-record commit/actual-SHA rerun explicitly approved2026-10-15;
all blocking passed at clean05442c40. Human final results explicitly accepted
2026-10-15. Receipt-record commit/revalidation explicitly approved2026-10-15;
outcome pending at record commit. Delivery remains separately gated.
Subsequently authorized delivery2026-10-15:PR615 merged4ff3e8e5 after all3 PR
CI jobs passed;actual merge-result main CI38698691368 all3 SUCCESS. No clause/code/
test change. Older delivery-approval-pending notes are historical.
Owner: [LISS-0589](../issues/LISS-0589-evaluator-classical-scalar-capture-successor.md).
Delivery-record commit/actual-SHA all-blocking verification approved2026-10-15;
five docs only on codex/liss-0589-delivery-closeout from merged main4ff3e8e5.
Outcome pending at record commit in
/private/tmp/liss-0589-delivery-closeout.VwjoyV/result.md. Clauses unchanged;
no record push/PR/merge authorization inferred.
Immutable source base: f14a332c8f8e6aa9e6bc7b01403f5f89da6b6044.

## Design boundary

Move only the23-physical-line `Evaluator._maybe_capture_classical_scalar`
method to `compiler/staqex/runtime/evaluation/classical_scalars.py` as
`maybe_capture_classical_scalar(context: ClassicalScalarContext, joint: Joint,
name: str) -> None`. Accepted declaration-only Protocol:
`scalars: MutableMapping[str, float | Fraction]`. Evaluator is passed directly
and remains the unique mutable owner; no new instance, copied map, cache,
DTO, policy adapter or generic numeric abstraction.

Dependencies: future annotations, stdlib Fraction/MutableMapping/Protocol and
existing `..joint.Joint`. Do not import Evaluator or broad EvaluatorContext.
Joint currently depends only on stdlib; assess actual cold package imports
later rather than treating a narrow direct import as full graph proof.
Preserve the existing `joint: Joint`, `name: str`, `-> None` annotations.
Allowed algorithm transformations: function-name change, `self` receiver
rename to `context`, receiver annotation, and corresponding member references.
All executable branches, try boundaries, returns and docstring meaning stay.

Evaluator privately imports the function as `_capture_classical_scalar_successor`
and replaces the original method at its class-body position with
`_maybe_capture_classical_scalar = _capture_classical_scalar_successor`.
Ordinary bound method, not staticmethod/classmethod, wrapper or installer.
Remove the old body; retain all existing public reexports and other imports
unless separately reviewed. No second runtime algorithm or dead legacy copy.

Why split a small method: it owns the eligibility/conversion/write policy for
bringing a finite-support Joint coordinate into the classical environment.
That policy differs from closed-expression eligibility and caller binding
eligibility. Keep its boundary named, independently characterized and small;
do not claim23 fewer executable lines or complete Evaluator decomposition.
Reject a broad utilities module and a return-value/caller-write redesign:
the latter could change repeated live-map reads and exception boundaries.
No changed architecture premise, technology or external resource proposed;
new ADR not presently needed. Stop for architecture review if that changes.

## Actual consumers / reachability limits

`rg -n '_maybe_capture_classical_scalar' compiler tests` finds the definition
and two external call sites:

| Consumer at base | Required preservation |
| --- | --- |
| evaluation/execution.py:437 | ordinary single Type-First binding; existing exclusions for state/operator/etc. and class/struct/enum names stay in caller |
| evaluation/observation.py:267 | binding while preparing observation; existing type exclusions and one-name condition stay in caller |

No declaration for this hook exists in current EvaluatorContext; do not add
one in this move. Both consumers retain their exact code and hook dispatch.
No direct test-hook use found by that static search; dynamic/external/plugin/
subclass reachability is not exhaustive. Retain private class/instance identity
and overridden hook dispatch; do not infer retirement authority from search.
Actual Joint.marginal aggregates Born mass, filters by EPS and converts Joint
Fraction coordinates elsewhere. Those behaviors are read-only dependencies,
not implemented again here. Fraction and exceptional branches require direct
hook/stub characterization as well as reachable real-Joint tests; a stub is
not proof that every language source can reach a branch.

## Acceptance clauses / minimum Phase1 inventory

| Clause | EARS requirement and minimum cases |
| --- | --- |
| S01 | WHEN name is already a scalar key, SHALL return None before any marginal call or value conversion, retaining the exact stored object. Cover zero/false/None/Fraction sentinels, raising marginal, and membership exceptions propagating. Membership, not truthiness or value type, decides. |
| S02 | WHEN marginal(name) raises an Exception, SHALL return None; BaseException outside Exception SHALL propagate. WHEN returned marginal has zero or more than one key, SHALL not convert or write. Cover real empty/missing/vacuum/multi-valued Joint, recording call name/count and fake exceptions. len() and key-iteration errors SHALL propagate because they are outside the catch. |
| S03 | WHEN marginal has exactly one key, SHALL use that key, not its probability/mass or a sampled value. Fraction SHALL be stored as the same object; other keys SHALL use float(raw). Cover real deterministic Joint including coalesced equal values, Fraction/subclass stub identity, Int/Float/Bool, numeric string and signed zero. Stub zero-mass singleton is characterized separately; no normalization/finite validation added. |
| S04 | WHEN conversion or map assignment raises TypeError/ValueError, SHALL preserve current swallowing and return None; other errors including OverflowError/RuntimeError SHALL propagate. Cover invalid string/None/object conversion, custom conversion errors, assignment errors in both Fraction and float paths. No rollback, broader catch, diagnostics or probability threshold added. Existing NaN/infinity conversion remains unchanged; do not introduce finite-value rejection. |
| S05 | WHEN maps change between calls or during marginal acquisition, SHALL read the current owner map at each original access, without caching or a second membership check. Cover whole-map replacement, marginal callback replacing map/inserting name, distinct Evaluators and repeated calls. Only the original target assignment is permitted; Joint/world state and unrelated entries stay unchanged on ordinary maps. Do not promise rollback for a custom map that mutates before raising. |
| S06 | WHEN invoked through each actual execution/observation consumer, SHALL preserve hook calls, Type-First caller eligibility, values and diagnostics. Cover method-returned duration usable by Evolve, field coefficient usable by Operator, already-known names, excluded types/multi-bind, and private instance/subclass hook overrides on both routes. Retain adjacent regression suites read-only. Source examples alone do not replace direct consumer call evidence. |
| S07 | Successor SHALL own the sole exact algorithm and narrow declaration-only Protocol with the allowed dependencies. Evaluator class hook SHALL be that function; instance hook SHALL bind the same function and receiver. No old body, wrapper, duplicate hook or extra runtime state. Require exact AST comparison with immutable Git, both cold requested import orders and actual consumer imports. |
| S08 | All unrelated evaluator bodies, imports/public exports, context, execution/observation eligibility, Joint, prior successors, typechecker/parser, old fixtures/hashes and adjacent tests SHALL remain unchanged except S09's named test-only carriers. New readonly evidence derives from immutable base Git; never regenerate prior manifests. Preserve earlier closed-expression/partial/Host/Tensor/foreach protection. |
| S09 | Guard transition SHALL allow exactly S07's move/wiring, validate actual successor in the guarded root, and restore the original whole method AST at its original position before earlier projections. Real guards and real copied fixtures SHALL accept genuinely distinct pre/post shapes and reject wrong algorithm/type/exception/order/import/hook, duplicate or missing body/successor, extra state and unrelated changes. Preserve copied-successor missing/changed negatives and original mutation setup. No hash/assertion/exclusion weakening or blanket future-helper exemption. |

Clause-to-node mapping required before human Red acceptance. Keep passing
behavior characterization separate from ownership Red. Confirm minimum cases
explicitly; unreachable source cases need named direct-hook coverage and limits,
not silent omission or a semantic fix in this extraction.

## Accepted bounded guard transition — execution separately gated

Current shared0583 projection restores closed, partial, Host and Tensor before
foreach/unaffected snapshots. A new test-only0589 helper shall restore scalar
capture before that chain, validating exact import/hook/function/Protocol.
Pin the whole original method from base Git and preserve all prior fixtures.
The new helper may construct AST-only temporary proposals, never imported or
installed into product sources during Red.

Only these existing test carriers are accepted locations for later approved Phase1:

- `tests/liss_0583_guard_support.py`: compose exact0589 restoration first.
- `tests/test_liss_0584_repair_boundary_red.py`: validate actual installed0589
  successor from the guarded directory before shared restoration.
- `tests/test_liss_0583_repair_boundary_migration_red.py`: conditionally copy
  the actual scalar successor into its temporary guarded root.
- `tests/test_liss_0585_tensor_guard_migration_red.py`: same copy addition in
  shared copied dependencies, used by0586/0587/0588 fixtures.

New0589 tests/helper/immutable fixtures require separate Phase1 authorization.
0588 C08 readonly manifest does not freeze these four carriers; its whole-facade
guard uses the shared projection and must remain effective. No edits proposed
to0588 tests/helper or earlier hashes/fixtures/lifecycle. Forward-run real
inherited mutations and copied fixtures on both source shapes before Red
review, not merely shape labels. If another required carrier/protected owner
is found, stop for bounded spec amendment; no implied general test permission.

## Verification / structure disposition

Phase0: document lifecycle, active-Red lifecycle, coverage consistency and
diff whitespace only. No runtime Green, full baseline comparison or test runs
claimed for design. cwd `/Users/nn0cl/Documents/git/qpex`;
Python `/usr/local/bin/python3.12`. External scripts declare repository
PYTHONPATH; record SHA/dirty state,environment,commands,UTC,exit/failures/skips.

Later focused S01–S09, real consumer/cold-import/hook-identity smoke and
inherited0582–0588 preservation/ownership/guard suites reported separately.
Read-only adjacent minimum:
`tests/test_classical_float_operator_evolve_binding_red.py`,
`tests/test_classical_rational_red.py`,
`tests/test_liss_0297_operator_freefn_struct_coeffs_red.py`,
`tests/test_liss_0305_classical_multi_bind_red.py`,
`tests/test_liss_0434_factory_scalar_domain_and_attr_coefficient_red.py`,
`tests/test_liss0240_observe_sink_to_vs_unit_convert_red.py`,
`tests/test_prelude_pi.py` and `tests/test_gram_kilogram_scale_red.py`.

Every blocking after implementation and final commit:
`/usr/local/bin/python3.12 -m pytest tests/ -q`,
`/usr/local/bin/python3.12 tests/spec_verification/run_all.py`,
all applicable actual `.github/workflows/ci.yml` repository sanity steps,
including PR traceability when applicable. No new exclusions. Compare failure
IDs with comparable base evidence or report comparison unavailable. Keep
actual final-SHA evidence outside tree; later commits invalidate applicability.

Base facade950 physical lines; method23 including signature/comments/blanks.
Remaining large facade under WP0174, not complete decomposition. Measure actual
successor/facade/compatibility/guard bodies at review, not facade shrink alone.
Live routing same_context/host,empty IDs, no enabled large-change section or
numeric budgets; qualitative readability applies. Re-resolve effective route
from actual final diff; unknown owners/dependencies/serialization/dynamic
reachability/full graph remain explicit gaps, not permission to downgrade.

## Context / decision gates

Included:current target/consumer/Joint/guard evidence,closed successor contract,
state-ownership and verification policy,matching lessons. Omitted:Rust,typed
object redesign,finite-number policy,measurement semantics,other splits,secrets.
No runtime AI payload contract; AI design grounded by repository/Git evidence.
Dedicated Issue/spec S01–S09, bounded guard transition and Phase0 acceptance
explicitly approved2026-10-14. Phase1 Red acceptance-test creation and bounded
guard-carrier migration execution subsequently approved2026-10-14 and performed.
Implementation allowed:no. Phase1 agent test review passed2026-10-14;
human exact-test acceptance explicitly granted2026-10-14;Phase2 Green/
implementation subsequently explicitly approved2026-10-14 and written.
Accepted clauses/tests unchanged. Next after provisional checks:scoped local
commit/actual-SHA all-blocking revalidation approval,then separately Phase3.
Human exact-test review/acceptance precedes Phase2; no phase skipping.
No source/test/commit/push/PR/merge authority granted by Scope approval.

## Phase1 current evidence

Focused119 PASS/4 expected S07 ownership Red;inherited21 suites418 PASS,
adjacent8 suites30 PASS,consumer subset10 PASS,spec161/161 PASS.
Root2817 PASS/the same4 expected S07 Red;sanity9 PASS/copy-smoke FAIL(uncommitted distributed spec).
No exclusions/waiver/full Green. Dirty HEAD/basef14a332c,external evidence:
/private/tmp/liss-0589-red.MFvkKC/result.md. Clause-to-node mapping in Issue.
All11 reviewed-candidate test/helper/fixture/carrier hashes pinned externally;
actual original Git AST and39 readonly paths independently verified unchanged.
No implementation installed. Consumer mechanics fixtures distinguish earlier
scalar capture,object preparation and unit-local scalar values from source
plan eligibility;no source reachability overclaim or silent semantic fix.

Reviewer rerun2026-10-14:focused119 PASS/same4 S07 Red,inherited418/adjacent30/
consumer10/spec161 PASS,sanity9 PASS/same copy-smoke FAIL. Independent immutable-
Git pre/post shape probe exercised actual guard/four copies and missing/changed
negatives PASS. Author root2817 PASS/same4 Red reused after unchanged11 hashes
and production audit,not rerun in review. [Agent packet](../collaboration/reviews/2026-10-14-liss-0589-phase1-red-review.md)
records weaker same_context isolation and remaining import/dynamic/dirty-
measurement gaps. No accepted clause/test/fixture/exclusion changes or Green
claim. Human exact-test acceptance and Phase2 remain separate gates.

## Phase2 current evidence

S01–S09 minimal sole-owner move written;old body removed,ordinary bound alias
retained. Original Git whole-method/facade reverse AST,39 readonly sources and
all11 accepted fingerprints PASS. Focused123/inherited418/adjacent30/consumer10/
cold-identity2/spec161 PASS. Root2821 PASS343.90s(exit0),no exclusions;
sanity9 PASS/copy-smoke FAIL on
uncommitted distributed spec. No exclusions or full committed Green claim.
Dirtyf14a332c,evidence:/private/tmp/liss-0589-green.g986cf/result.md.
Facade950→929,successor41,compatibility335 physical lines;not whole decomposition.
Later review must re-resolve effective route/structure on actual final diff.
Scope excludes semantic cleanup,full dynamic graph/private-method serialization,
Rust and new state owner. Earlier Phase1/approval-pending notes historical.

## Committed verification gate —2026-10-15

Human authorized only the scoped19-path local commit and actual-SHA rerun.
Accepted S01–S09 and11 test artifacts unchanged. All blocking and focused/
consumer/adjacent checks will run after the final local commit;outcome pending
at commit in `/private/tmp/liss-0589-sha-verification.nxLVoK/result.md`.
Earlier commit-approval-pending notes historical. No Phase3/final/delivery approval.

## Phase3 current evidence —2026-10-15

Phase3 explicitly approved;[agent review passed](../collaboration/reviews/2026-10-15-liss-0589-phase3-review.md).
S01–S09/accepted11 artifacts unchanged;no additional refactor justified.
Fresh clean28530388 root2821 PASS346.51s,focused123/inherited418/adjacent30/
consumer10/cold2/spec161/sanity10 PASS;exact Git method/facade/39 readonly/
original carrier assertions PASS. No root exclusions. Review isolation
same_context,weaker than separate_context;remaining limits disclosed in packet.
Evidence:/private/tmp/liss-0589-phase3-review.V0fZDx/result.md.
Current review records are uncommitted,not final-HEAD verification. Next request:
final verification/review-record commit/actual-SHA all-blocking rerun approval.
Earlier Phase3-permission-pending notes historical. No final or delivery authority.

## Final verification gate —2026-10-15

Human explicitly authorized review-record commit and actual-SHA all-blocking
rerun. No accepted clause/test/source change. Pending-at-record-commit outcome:
`/private/tmp/liss-0589-final-verification.uUwcHJ/result.md` and per-run JSON/logs.
Next on success:human final result acceptance,not inferred from CI/tests.
Earlier final-approval-pending notes historical. No delivery authorization.

## Final results accepted —2026-10-15

Human accepted the final results for05442c40299c001d72e883345c5fe023086b7ebe.
Root2821/spec161/sanity10 and focused123/inherited418/adjacent30/consumer10/
cold2 PASS;accepted S01–S09 and11 artifacts unchanged. Evidence:
/private/tmp/liss-0589-final-verification.uUwcHJ/result.md.
Local implementation accepted,not delivered. Older final-pending statements
are historical. Receipt records remain uncommitted;next approval:acceptance
record commit and actual-SHA all-blocking rerun. No new semantics or delivery.

Receipt commit/revalidation approval received2026-10-15;S01–S09/code/tests
unchanged. Actual receipt SHA and outcome:
/private/tmp/liss-0589-acceptance-verification.TD3hgf/result.md (pending at commit).
Earlier receipt-permission-pending notes historical;no delivery permission.

## Delivery state —2026-10-15

Authorized PR615 merged4ff3e8e5d4c596a58142375675c3c843c0433367 after PR
CI38696907811 all3 SUCCESS(root2821/spec161). Verified head5830e46c and
actual merge tree match exactly. Main merge-result CI38698691368 all3 SUCCESS,
root2821 PASS694.22s,spec161/161 and repository sanity PASS.
No new semantics/test edits or whole-decomposition claim. External evidence:
/private/tmp/liss-0589-delivery.9zAGR7/result.md. Local delivery records uncommitted.
