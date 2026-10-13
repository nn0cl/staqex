# Evaluator closed-expression eligibility successor — accepted specification

Status: C01–C09, dedicated Issue/spec, bounded guard transition and Phase0
acceptance approved2026-10-13. Scope / Phase0 design-start approved2026-10-13.
Phase1 Red acceptance-test creation / bounded guard migration execution
approved2026-10-13. Phase1 agent test review passed2026-10-13;
human Red test acceptance approved2026-10-13. Phase2 Green / implementation
approved2026-10-13 for C01–C09 only; implementation written, provisional root2698
and focused77 pass. Sanity copy-smoke fails on uncommitted spec. No final-SHA
Green claim yet. Local commit / actual-SHA all-blocking revalidation approved
2026-10-13; result pending at record commit. No Phase3 or delivery approval.
Owner: [LISS-0588](../issues/LISS-0588-evaluator-closed-expression-successor.md).
Immutable source base: a19cc974a4e0200d74ae012c9b76d2a8f4d18b0a.

## Design note and boundary

Extract only the existing 28-line `Evaluator._is_closed` classifier into
`compiler/staqex/runtime/evaluation/closed_expressions.py`.
Accepted function: `is_closed(context: ClosedExpressionContext, expr: Expr) -> bool`.
The local declaration-only Protocol exposes `scalars: Mapping[str, Any]`,
`objects: Mapping[str, Any]`, and `_is_closed(self, expr: Expr) -> bool`.
It is a read interface, not another runtime object, cache, state owner or DTO.
Evaluator remains the sole live state owner, passed directly as context.

Evaluator imports `is_closed as _is_closed_successor` privately and replaces
the old method at its original class-body position with
`_is_closed = _is_closed_successor`. This is an ordinary bound method,
not a staticmethod. Recursion continues through `context._is_closed`, so
subclass/instance hook overrides and call order remain observable as before.
No installer, wrapper classifier or duplicated original body is proposed.

Permitted algorithm transformations are exactly function-name change,
receiver rename `self` to `context`, receiver annotation addition, and the
lazy dimensions import level adjustment from runtime to evaluation placement.
Preserve all branches, constants, expression annotations, return annotation,
comments' meaning and exception behavior. Dependencies are stdlib typing,
the existing nine AST classes (Expr, LitInt, LitFloat, LitBool, LitString,
Var, Attr, UnitConvert, BinOp), and lazy `...dimensions.UNIT_TABLE` only.
Do not import Evaluator or the broad evaluation context at runtime.

This helper is a contextual eligibility predicate, not a mathematical proof
of closure, general purity, unit validity or field existence. In particular,
a registered object suffices for its Var-based Attr branch even if that field
does not exist; a Call remains false. Do not improve these rules in this move.
No new external resource, technology or changed architecture premise is
proposed; a new ADR is not currently required. Stop if that premise changes.

## Actual consumer inventory

Static search: `rg -n '_is_closed|_maybe_capture_classical_scalar' compiler tests`.

| Consumer at base | Contract to preserve |
| --- | --- |
| evaluation/execution.py:313 | classical tuple capture uses all() of item hooks |
| evaluation/execution.py:342 | single classical binding uses the predicate |
| evaluation/binding.py:168 | Dirac chooses constant versus joint pushforward |
| evaluation/operators.py:454 | factory-local scalar eligibility; local-object fallback stays in consumer |
| evaluation/context.py:147 | existing declaration-only private callback stays unchanged |
| Evaluator._is_closed recursion | UnitConvert child and left-to-right BinOp dispatch through live hook |

There are four external invocation sites in three source consumers, plus
the protocol declaration and two recursive source sites. `_is_closed_value`
in unitarity checking is unrelated. No direct test hook was found by this
search; dynamic, external, plugin and subclass consumers are not exhaustively
known. Preserve private entrypoint rather than infer permission to retire it.
Inspect cold imports and actual consumers in later phases; parent package
initialization means a requested successor-first import is not package-free.

## Acceptance clauses / minimum Phase1 inventory

| Clause | EARS requirement and minimum cases |
| --- | --- |
| C01 | WHEN given Int/Float/Bool/String literals, SHALL return true without reading either environment; WHEN given other unsupported nodes (Call, TupleExpr, UnaryNot, Dirac, Coin), SHALL return false, not descend or evaluate. Cover every literal family and named unsupported family. |
| C02 | WHEN given Var, SHALL test only current scalar-key membership, not truthiness, scalar value type or objects membership. Cover absent, false/zero/None values, object-only name, insertion/deletion, entire-map replacement and separate Evaluator instances. |
| C03 | WHEN given Attr, SHALL preserve branch priority: Math.pi/sqrt2/inv_sqrt2 true without environment dependence; otherwise Var receiver in current objects true regardless of field existence; otherwise numeric literal receiver checks current UNIT_TABLE key membership; otherwise false. Cover three aliases, unknown Math member with/without registered Math object, arbitrary registered field, missing object, Int/Float units, Bool/String non-unit receivers, unknown unit and nested receiver. No field lookup/value evaluation or units conversion. |
| C04 | WHEN given UnitConvert, SHALL return child hook result without validating target unit. WHEN given BinOp, SHALL call lhs then rhs only if lhs is truthy, independent of operator spelling. Cover nested trees, invalid conversion target, false lhs skipping a raising rhs, recursion override/call order and propagated hook/membership exceptions. Preserve Python and-result behavior; do not coerce overridden returns to bool. |
| C05 | WHEN state or hook changes between calls, SHALL observe it without snapshots/caches, not mutate expr/maps/Joint, and never evaluate values or perform Host I/O. Keep UnitConvert/BinOp recursion through the same live context hook, including subclass and instance overrides. Cover fresh/replaced maps and a recording context; no second state owner. |
| C06 | WHEN reached through execution, binding and operator consumers, SHALL retain classical single/multi-bind capture, Dirac constant/pushforward routes, factory-local scalar and object fallback, values and existing diagnostics. Characterize all four invocation sites and retain adjacent source suites read-only. |
| C07 | Successor SHALL own the only algorithm, exact allowed dependencies and declaration-only narrow protocol. Evaluator class hook SHALL be the actual successor function; instance hook SHALL bind the same function and receiver. No old body, wrapper, duplicate hook or public export changes. Preserve lazy UNIT_TABLE access and live table membership. Cold requested imports in both orders, private hook identity and actual consumer imports required. |
| C08 | All unrelated Evaluator methods including scalar capture and partial filling, public reexports, context, consumers, compatibility.py, dimensions, AST/typechecker/parser and prior successor algorithms SHALL remain unchanged. Pin source/test readonly evidence from immutable Git; do not regenerate old manifests. |
| C09 | Guard migration SHALL allow only C07 wiring and algorithm relocation, restore original whole AST at original position, and reject altered predicates, recursion order/short circuit, eager imports, dependency additions, missing/duplicate bodies, wrong binding, extra state and unrelated changes. Exercise actual real guards and real copy fixtures on genuinely distinct pre/post shapes, with copied-successor missing/changed negatives; no hash/assertion/exclusion weakening. |

These clauses characterize existing behavior; they do not authorize adding
semantic support for unsupported nodes. Clause-to-test-node mapping is required
before Red acceptance, with structural Red distinguished from characterization.

## Accepted bounded guard transition (execution separately gated)

The 0583 evaluator projection currently restores Partial, Host, Tensor, then
foreach before checking frozen unaffected AST/imports. A new test-only0588
projection must restore this closed-expression move before that existing chain.
It must verify exact import/hook, actual successor algorithm and Protocol,
and restore the immutable original method including lazy import and signature.
No permissive AST filtering or blanket future-helper exemption.

Minimum inventoried existing test carriers for separately authorized Phase1:

- `tests/liss_0583_guard_support.py`: compose exact0588 restoration first.
- `tests/test_liss_0584_repair_boundary_red.py`: check actual installed0588
  successor in the guarded directory before source reconstruction.
- `tests/test_liss_0583_repair_boundary_migration_red.py`: copy actual0588
  successor into temporary roots when installed.
- `tests/test_liss_0585_tensor_guard_migration_red.py`: same bounded copy
  addition; 0586/0587 copy fixtures consume this function.

New0588 test/helper/immutable-fixture files may support this only after Phase1
approval. Old0583–0587 fixtures/manifests, recorded hashes, semantic assertions,
readonly boundary and lifecycle exclusions remain unchanged. Existing0587
ownership tests consume the shared projection; their partial class/body/hook
checks must remain effective. Probe inherited original-body mutation setup on
future shapes, not just passing labels. Any additional protected owner or
necessary carrier edit outside this list requires a bounded reviewed amendment.
Temporary AST proposals are never imported or installed into product sources.

## Verification plan / structure disposition

cwd `/Users/nn0cl/Documents/git/qpex`; local CPython3.12 runner
`/usr/local/bin/python3.12`. External smoke scripts must declare repository
PYTHONPATH explicitly and record environment, SHA, clean/dirty state, UTC
boundaries, exits, failure IDs and skips/exclusions. Phase0 runs documentation
checks only; no runtime Green claim or full baseline run.

Focused: new C01–C09 suites; actual private-hook/consumer/cold-import smoke
reported separately. Inherited: all0582 public import, 0583 foreach/repair
guard, 0584 repair boundary, 0585 Tensor, 0586 Host and 0587 Partial ownership
and guard-migration suites affected by the shared projection.
Adjacent source suites, read-only:

- `tests/test_prelude_pi.py`
- `tests/test_classical_float_operator_evolve_binding_red.py`
- `tests/test_liss_0305_classical_multi_bind_red.py`
- `tests/test_liss_0297_operator_freefn_struct_coeffs_red.py`
- `tests/test_liss_0434_factory_scalar_domain_and_attr_coefficient_red.py`
- `tests/test_liss0240_observe_sink_to_vs_unit_convert_red.py`
- `tests/test_gram_kilogram_scale_red.py`

All blocking after implementation/final commit:
`/usr/local/bin/python3.12 -m pytest tests/ -q`,
`/usr/local/bin/python3.12 tests/spec_verification/run_all.py`,
every applicable repository-sanity check in `.github/workflows/ci.yml` and
PR traceability when applicable. No new exclusions; report focused/inherited/
adjacent separately from whole-root/spec/sanity. Compare failure IDs in a
comparable base environment or explicitly report comparison unavailable.
Store final-SHA evidence externally; later documentation commits require rerun.

Evaluator is976 physical lines at base; the target method is28, including
signature and blank/comment lines, not executable-statement count. The
remaining large facade stays under WP-0174 responsibility planning, not claimed
fully decomposed. Measure actual successor, facade, guard and compatibility
bodies at review, not a promised net line reduction. Routing is same_context /
host with empty IDs and no enabled large_change or numeric structure budgets;
qualitative readability rules apply. Exact changed metrics, dynamic consumer
closure and whole resolved dependency graph remain unknown at design time.

## Context and gates

Included: current source/consumer/guard evidence, partial successor spec for
unaffected compatibility, collaboration policies and relevant lessons.
Omitted: scalar-capture extraction, broader type-object redesign, Rust/provider
choices, semantic changes, unrelated features/secrets and upstream templates.
No runtime LLM input/output contract applies; evidence above grounds AI design.

Dedicated Issue/spec C01–C09, bounded guard transition and Phase0 acceptance
approved2026-10-13. Accepted clauses unchanged by approval synchronization.
Phase1 Red acceptance-test creation and bounded guard-carrier migration execution
approved2026-10-13. Agent Red test review passed and human Phase1 Red test
review / acceptance approved2026-10-13. Phase2 Green / implementation
subsequently approved2026-10-13; minimal source move written, provisional
verification recorded below. Local commit / actual-SHA revalidation subsequently
approved2026-10-13; Phase3 requires separate approval.
Phase1 executed:focused73 passed/4 structural Red; root2694 passed/the same4
Red, existing341/adjacent26/spec161 pass. Sanity copy-smoke remains failed on
uncommitted spec; no full Green. Dirty base a19cc974, evidence and clause-to-node
mapping in Issue/trace. Exact tests reviewed and human acceptance approved;
all11 reviewed test artifact hashes unchanged at acceptance synchronization.
Reviewer focused73 pass/same4 Red, adjacent26 pass and future-shape inherited
setup15 pass; [review packet](../collaboration/reviews/2026-10-13-liss-0588-phase1-red-review.md).
Phase2 provisional results:focused77, inherited341, adjacent26, consumer/cold
smoke7 and root2698 all pass; spec161/161 PASS. Sanity9 pass/copy-smoke FAIL
on uncommitted distributed spec; no waiver/full Green. All11 accepted artifact
hashes unchanged, original Git AST independently compared with installed owner.
Evidence:`/private/tmp/liss-0588-red.2OSDVf/green-result.md`; dirty HEAD/base
a19cc974, not final-SHA completion evidence. Above Phase1 results are historical.
Local commit / actual-SHA all-blocking revalidation approved2026-10-13.
Actual result entry:`/private/tmp/liss-0588-sha-verification.xfHtgc/result.md`,
pending at record commit; no pass inferred. After successful committed checks,
next gate:separate Phase3 Refactor / review approval.
Phase3 review, local final-SHA verification and remote delivery remain distinct.
