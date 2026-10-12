# Evaluator partial filling successor — accepted specification

Status: P01–P09 and bounded guard transition accepted2026-10-12;
Phase0 accepted. Phase1 Red execution and test review/acceptance approved2026-10-12.
Phase2 Green/implementation separately approved2026-10-12; minimal extraction
implemented without changing accepted test bytes. Local commit / actual-SHA
all-blocking revalidation separately approved2026-10-12. Clean951e5426 passed
root2621/spec161/sanity10; actual-SHA result:
`/private/tmp/liss-0587-sha-verification.fYIOBG/result.md`.
Phase3 Refactor/review separately approved2026-10-12; agent review passed,
no product/test changes required. [Current review](../collaboration/reviews/2026-10-12-liss-0587-phase3-review.md).
Final review-record commit/actual-SHA verification explicitly approved2026-10-12.
Result pending at record commit; actual final SHA and all-blocking result:
`/private/tmp/liss-0587-final-verification.rTeCvx/result.md`.
Final verification passed at clean4812c29a (root2621/spec161/sanity10,
focused48/inherited143/adjacent16 and consumer smoke).
Human final-result acceptance received2026-10-12. Lesson-only process-review
disposition for the resolved external smoke launch issue agreed2026-10-13;
acceptance-record commit/revalidation explicitly approved2026-10-13.
Outcome pending at record commit; final SHA/result:
`/private/tmp/liss-0587-acceptance-verification.dYd4JN/result.md`.
Local accepted slice recorded done subject to that check; remote delivery not authorized.
Accepted P01–P09 unchanged; not a delivered-completion claim.
Agent Phase1 review passed2026-10-12; human accepted the unchanged reviewed artifacts:
[review packet](../collaboration/reviews/2026-10-12-liss-0587-phase1-red-review.md).
Historical Red execution evidence:focused44 pass/4 intended Red; root2617 pass/same4 Red;
inherited143/adjacent16/spec161 pass. Dirty tests/docs at base b5ad7402;
details and clause-to-node inventory in Issue/trace. Historical dirty Green focused48 pass,
inherited143/adjacent16/spec161 and root2621 pass; copy-smoke fails on
uncommitted distributed spec. No full Green claim:
[Phase2 evidence](../collaboration/reviews/2026-10-12-liss-0587-phase2-verification.md).
Owner: [LISS-0587](../issues/LISS-0587-evaluator-partial-filling-successor.md).
Immutable source base: b5ad7402c184a3a79440271e02dd423c53d8bc36.
Authority: rank6 Scope/Phase0 design and dedicated Issue/spec acceptance,
2026-10-12; Phase1 test-only execution separately approved2026-10-12.

## Boundary and observed consumers

Accepted owner:`compiler/staqex/runtime/evaluation/partial_calls.py` for
`PartialValue` and `fill_partial(partial, fill_args)` only. The existing
dataclass is mutable despite its docstring; preserve fields, defaults,
constructor, repr, equality and mutability, not a speculative frozen type.
Evaluator re-exports the exact same class and retains static `_fill_partial`.
Preserve class `__module__` as `compiler.staqex.runtime.evaluator` for old
pickle paths; metadata compatibility is explicit, not runtime policy.
Successor must not import Evaluator, own maps, evaluate expressions or bind calls.
No new protocol/factory/service is needed for this pure operation.

Observed consumer inventory (static search at base):

| Consumer | Existing contract | Proposed disposition |
| --- | --- | --- |
| evaluation/calls.py:97 | calls context._fill_partial, then stores partial or binds Call | unchanged |
| evaluation/context.py:89 | declaration-only callback | unchanged |
| Evaluator._make_partial_value | constructs PartialValue | same class re-export |
| evaluation/binding.py:77,223 | name-based partial dispatch and tuple pipe filling | unchanged |
| evaluation/pipes.py:134 | name/fields, one-hole fused stage | unchanged |
| Evaluator._fill_partial | class and instance static-call compatibility | exact static successor mapping |
| evaluator module export | public PartialValue name without __all__ | same import and class identity |

Search `rg -n 'PartialValue|_fill_partial' compiler tests --glob '*.py'`
found no direct test hook/import at intake. This is not proof of absent external,
plugin or dynamic consumers. Runtime cold-import, export and serialization
checks must supplement static search. Calls/binding/pipes remain orchestrators.

## Acceptance clauses and minimum Red inventory

- P01: WHEN slots contain holes, filling SHALL consume arguments left-to-right,
  preserve occupied Expr identities/order and preserve the input slots and args.
  Cover interleaved holes, first/last holes and fresh output-list identity.
- P02: WHEN fewer than all holes are filled, result SHALL be a fresh same-class
  PartialValue with the original fun_name and remaining None slots. Cover
  repeated stepwise calls and original-instance nonmutation.
- P03: WHEN all holes are filled, result SHALL be Call with Var(fun_name),
  filled Expr identities/order, and both Var/Call span from fill_args[0].span.
- P04: WHEN args are empty or exceed hole count, SHALL raise existing KernelError
  with exact message ``Partial `<name>` expects 1..<need> remaining args, got <n>``
  (literal backticks around the interpolated name). Cover zero holes with empty
  and nonempty args, one-hole overfill and input nonmutation on error.
- P05: WHEN used through existing source programs, one-hole pipe, stepwise call,
  multi-hole tuple pipe and fused partial routes SHALL retain their results,
  compile diagnostics and linear move behavior. Reuse existing suites read-only.
- P06: WHEN imported through evaluator or successor, PartialValue SHALL be one
  class, with old name/module identity, dataclass behavior and old/new pickle
  round trips. Evaluator class and instance `_fill_partial` SHALL expose the
  successor as a static function, without injecting self or hiding a duplicate body.
- P07: Successor SHALL own the only PartialValue class and fill algorithm;
  dependencies limited to dataclasses, AST Expr/Call/Var and shared KernelError.
  No evaluator back-reference, lazy factory import, extra mutable-state owner,
  wrapper algorithm or generalized helper abstraction. Verify both cold import orders.
- P08: All unrelated Evaluator methods, public exports, context, consumers,
  scientific validation and Host/Tensor/foreach successors SHALL remain unchanged.
  No change to `_is_closed`, scalar capture, parsing, type checking or pipe policy.
- P09: Guard transition SHALL allow exactly the P06/P07 class/body move and
  static wiring, reconstruct old AST from immutable base evidence, and reject
  changed algorithm, dataclass fields/decorators, duplicate/missing bodies,
  wrong hook mapping, changed class module, extra state and unrelated edits.
  Existing baseline hashes/fixtures SHALL remain unchanged. Exercise actual
  pre/post root fixtures and real existing guards, not just shape labels.

## Accepted bounded guard transition (Phase1 test-only execution)

Existing `tests/liss_0583_guard_support.py` restores Host and Tensor before
comparing imports and unaffected Evaluator AST to its frozen baseline.
0582/0583/0584/0585/0586 acceptance consumers also invoke this chain.
A new test-only0587 projection before these restorations shall check exact
successor dataclass/algorithm and static mapping, remove only approved new
wiring/re-export, then restore original PartialValue and static method at
their base positions. No blanket exemption for future moves.

New fixture bytes come from the immutable base above, whole AST including
docstrings must match; do not dedent multiline literals silently. Copy every
new successor/projection dependency into temporary guarded trees. Reconcile
all existing source snapshots and readonly guards in Red; any unexpected
protected owner requires a new bounded disposition, not hash relaxation.
Allowed Phase1 edits, separately approved2026-10-12: new0587 acceptance/projection
tests and immutable fixtures, plus precisely inventoried guard-carrier/copy
fixtures required to exercise this projection. No production edits or
assertion/exclusion weakening. Exact changed test list must be reported in Red.

## Verification plan and gaps

cwd repository root, CPython3.12 with pytest; local and GitHub versions recorded
per run. Focused:new P01–P09 suites. Consumer smoke:existing calls/binding/pipes,
class/instance hooks and cold imports. Adjacent:tests/test_function_partial_holes_red.py,
tests/test_stepwise_partial_fill_red.py, tests/test_multi_hole_partial_pipe_red.py,
tests/test_liss0238_multi_hole_partial_pipe_lhs_move_red.py,
tests/test_call_partial_fusion_red.py, tests/test_partial_float_indexing_red.py,
tests/test_liss_0201_partial_hole_keyerror_red.py.
All blocking:`python3 -m pytest tests/ -q`,
`python3 tests/spec_verification/run_all.py`, all repository-sanity checks from
`.github/workflows/ci.yml`, plus PR traceability when applicable. No new exclusions.
After final commit rerun all blocking at actual SHA, compare failure IDs with
base in comparable environment; keep evidence external. Focused != full Green.

Current structure baseline:Evaluator1014 physical lines; proposed moved bodies
31+7 lines, not a promised total-line reduction. Measure facade, successor,
compatibility and test guard bodies at review. Live routing has same_context /
host, empty model IDs, no enabled large_change section or numeric budgets;
qualitative structure rules still apply. Existing large evaluator retained
only outside this bounded slice; WP-0174 owns remaining responsibilities.
Dynamic consumers/resolved graph and future exact changed-file metrics remain
unknown until verification. No complete coverage or Green claim at Phase0.

## Out of scope and next gates

Other rank6 helpers, new partial semantics, frozen representation, retiring
public/private compatibility, Rust, provider integration and broader guard
cleanup are excluded. Dedicated Issue/spec P01–P09, guard-policy review and
Phase0 acceptance approved2026-10-12. Phase1 execution, test acceptance, Phase2 implementation,
Phase3 review and remote delivery each remain separate human gates.
