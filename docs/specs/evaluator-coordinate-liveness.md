# Specification: Evaluator coordinate liveness and Trace-Out successor

| Field | Value |
|---|---|
| Status | Architecture boundary accepted by [ADR 0228](../architecture/adr/0228-evaluator-coordinate-liveness-boundary.md); Phase 0, Phase 1 review, Phase 2 implementation, Phase 3 refactor/same-context review, and human Phase 3 final review approved; commit and post-commit verification pending |
| Scope candidate | WP-0174 / LISS-0581 |
| Source authority | [ADR 0228](../architecture/adr/0228-evaluator-coordinate-liveness-boundary.md); [Core module decomposition](staqex-core-module-decomposition.md); accepted runtime decisions ADR 0138/0142/0153/0158 as recovered in [DEC-0005](../architecture/decision-themes/dec-0005-quantum-operations-and-runtime.md) and [WP-0064 trace](../collaboration/traces/2026-07-31-wp-0064-interprocedural-trace-out.md) |

## Purpose

Define a behavior-preserving ownership boundary for existing coordinate
liveness and automatic Trace-Out mechanics shared by the Evaluator, invocation
frames, execution, observation, pipe/block, and evolution services. The
architecture boundary is accepted; implementation and phase status are
tracked below and in the linked Issue/Work Plan.

## Phase 0 finding

On `main` at `83c93a524c7c90710ed965d231ffe85b20dc3163`,
`runtime/evaluator.py` is 1,307 physical lines with 75 class methods. The
candidate family comprises `_joint_coord_names`,
`_trace_out_dead_fn_locals`, `_main_interproc_trace_eligible`,
`_stmts_live_vars`, and `_trace_out_dead_caller_coords`. `frames.py` separately
duplicates the first two operations as module-level helpers.

Direct consumers found by static search:

| Consumer | Existing use |
|---|---|
| `runtime/evaluation/frames.py` | Captures incoming coordinates and traces function-local coordinates on each function-return shape; duplicates coordinate helpers |
| `runtime/evaluation/pipes.py` | Uses pre-live coordinates and function-local Trace-Out at bare-block exit |
| `runtime/evaluation/evolution_ops.py` | Uses pre-live coordinates and function-local Trace-Out at evolve exit |
| `runtime/evaluation/execution.py` | Checks main eligibility and traces caller coordinates after eligible function calls |
| `runtime/evaluation/observation.py` | Uses main eligibility and caller-coordinate live-out around deferred execution/measurement |
| `runtime/evaluation/context.py` | Declares private callbacks used by the above services |
| `tests/test_liss_0573_pipes_successor_red.py` | Source-inspects `_joint_coord_names` and `_trace_out_dead_fn_locals` names |
| `tests/test_liss_0561_evaluator_observation_dynamic_red.py` | Source-inspects `_expr_has_inspect` and `_expr_free_vars` ownership/hook names |

`_expr_has_inspect` and `_expr_free_vars` currently live in
`evaluation/observation.py`, are installed as Evaluator static hooks, and are
used both by the candidate main-call liveness policy and by other observation
analysis. Their ownership and compatibility treatment must be decided before
Phase 1. The design recommendation is for a focused `evaluation/liveness.py`
to own the AST read-only walkers and coordinate-liveness/Trace-Out algorithms,
with existing Evaluator hook names retained as thin compatibility delegates
while real consumers are migrated or proven direct-call safe. Do not move
unrelated deferred-execution algorithms out of `observation.py`.

## Proposed scope

In scope, if separately accepted:

- the five Evaluator methods listed above;
- the duplicate coordinate helpers in `evaluation/frames.py`;
- `_expr_has_inspect` and `_expr_free_vars` only as required to give the
  liveness module one cohesive source owner, subject to the existing LISS-0561
  compatibility/test contract;
- explicit, minimal compatibility wiring and the affected
  `EvaluatorContext` declarations;
- structural and behavior-preservation evidence for every direct consumer.

Out of scope:

- expanding, narrowing, or optimizing liveness semantics;
- whole-program SSA/interprocedural analysis, system-field liveness, density
  matrix behavior, new pruning, or any change to explicit `trace_out`;
- changing deferred execution eligibility or Runtime Plan authority;
- changes to language syntax, diagnostics, QASM/QPU/provider behavior;
- extracting `_eval_set_comprehension`, runtime-plan dispatch, host input
  resolution, `forEach`, tensor binding, or unrelated evaluator methods;
- changing `Evaluator` as the sole owner of mutable runtime state.

## Behavior-preservation contract

1. Function-call and function-return Trace-Out retains precisely the incoming
   coordinate names plus explicit result bind names; discarded coordinates
   continue to use `Joint.trace_out` and do not sample or measure.
2. Existing eligible-main interprocedural Trace-Out remains disabled for
   `inspect` expressions and snapshots. Eligibility and live-out statement
   kinds remain exactly as ADR 0158 specifies.
3. Main-call live-out remains the union of free variables from subsequent
   `StateBind`, `Measure`, `Snapshot`, and `ExprStmt` expressions as currently
   implemented; the post-call result bind names are always retained.
4. Existing bare-block and evolve exit callers preserve their established
   pre-live/result-name inputs. This proposal does not infer broader cleanup
   from their shared helper call.
5. Coordinate-name enumeration, deterministic trace-out order, retained
   `Joint` values, diagnostics, measurement timing, and terminal outputs remain
   unchanged for fixed source and seed.
6. The extracted module owns the implementation bodies. The Evaluator may
   preserve existing private hook names as thin delegates; it must not retain
   duplicate algorithms. No second mutable-state owner or copied evaluator
   maps are introduced.
7. Existing private consumers and import paths remain usable unless separately
   retired through an approved migration.

## Phase 2 implementation disposition

The approved Phase 2 moved the seven pure coordinate/AST liveness functions to
`runtime/evaluation/liveness.py`. `Evaluator` keeps thin compatibility hooks;
`frames.py` calls the pure coordinate helpers directly and no longer duplicates
them; `observation.py` imports the two shared AST walkers while retaining its
unrelated deferred-observation algorithms. `context.py`, `execution.py`,
`pipes.py`, and `evolution_ops.py` remain unchanged. The reviewed Red test file
was not modified after Phase 1 review. No liveness semantics were intentionally
changed.

All 2,280 root tests and declared spec/document/lifecycle checks passed on the
dirty worktree in Phase 2. See the [Phase 2 verification record](../collaboration/reviews/2026-09-28-liss-0581-phase2-verification.md)
for exact commands, tested SHA, environment, and limitations. Phase 3 then
split the 131-line `expr_free_vars` traversal into named binder, operator, and
ordinary-expression helpers without changing tests. The [Phase 3 review
packet](../collaboration/reviews/2026-09-28-liss-0581-phase3-refactor-review.md)
records the refactor verification and human final-review approval. Commit and
post-commit verification remain outstanding.

## Phase 0 acceptance closure

### Phase 1 file boundary

Phase 1 Red is limited to adding
`tests/test_liss_0581_evaluator_coordinate_liveness_red.py` and registering its
active cases in `docs/testing/active-red-tests.toml`. It must not edit
production modules. The Phase 1 test review is a separate gate.

If Phase 1 and its test review are approved, Phase 2 implementation may edit
only these production modules:

- `compiler/staqex/runtime/evaluation/liveness.py` (new; sole owner of the
  extracted pure algorithm bodies);
- `compiler/staqex/runtime/evaluator.py` (thin compatibility delegates and
  hook wiring only; no duplicate algorithms);
- `compiler/staqex/runtime/evaluation/frames.py` (remove duplicate helpers,
  call the successor directly).
- `compiler/staqex/runtime/evaluation/observation.py` (delegate the two AST
  walkers to the successor while retaining unrelated observation logic).

`evaluation/context.py`, `execution.py`, `pipes.py`, and `evolution_ops.py`
remain unchanged if the existing callback protocol can be retained by thin
Evaluator delegates. Any need to change those paths is a scope deviation and
requires renewed review before editing. Phase 2 may also update this spec,
Issue, Work Plan, trace, and verification records; it may not alter unrelated
tests or broaden semantics. Phase 3 has the same source boundary and requires
its own approval.

### Existing evidence and gaps

The repository lifecycle checker reports `ACTIVE_RED_LIFECYCLE_OK entries=0`:
the legacy `_red.py` files below are closed historical AT-TDD suites, not open
Red work. Their coverage is:

| Contract | Existing exact evidence | Gap / Phase 1 disposition |
|---|---|---|
| ADR 0138 function-local cleanup and result retention | `tests/test_trace_out_gc_fn_scope_red.py::test_fn_param_axis_traced_out_after_call` | Covers dead caller axis and result; no duplicate needed |
| ADR 0153 bare-block cleanup and unrelated live coordinate | `tests/test_bare_block_trace_out_red.py::test_bare_block_let_temps_traced_out`, `::test_bare_block_preserves_unrelated_live_coord` | Covered |
| ADR 0142 evolve cleanup, retained coordinates, repeated steps | `tests/test_evolve_trace_out_gc_red.py::test_evolve_let_temps_traced_out`, `::test_evolve_preserves_unrelated_live_coord`, `::test_multi_step_evolve_drops_lets` | Covered; no existing evidence found for empty/correlated-Joint edge cases, so do not claim them as already covered |
| ADR 0158 dead caller axis/result retention | `tests/test_interprocedural_trace_out_red.py::test_dead_caller_axis_traced_out_after_library_call` | Covered |
| ADR 0158 later live use while optimization remains eligible | None | Add a source-level test where a caller coordinate is used after a library call without `Inspect`/`Snapshot`; assert live coordinate and call result remain while dead callee local is absent |
| Inspect exclusion | `tests/test_deferred_pushforward_mvp_red.py::test_inspect_forces_eager_path` | Confirms eager path only; add direct eligibility assertion for the liveness policy if no existing exact assertion is found during Red review |
| Snapshot exclusion | None found in the inspected suites | Add direct eligibility assertion using a Snapshot statement |
| AST walkers and source ownership/private hooks | `tests/test_liss_0561_evaluator_observation_dynamic_red.py` method manifest; `tests/test_liss_0573_pipes_successor_red.py` callback manifest | Existing tests constrain names/ownership but do not prove new module owns bodies or that delegates preserve behavior; add focused ownership/delegate assertions |
| Pipe/block callback behavior and invocation-frame routes | `tests/test_liss_0573_pipes_successor_red.py`; `tests/test_liss_0572_frames_constructors_assignments_red.py` | Keep as adjacent regressions; inspect exact assertions during Phase 1, do not label these as comprehensive Trace-Out coverage |

No empty/correlated-Joint fixture or direct coverage of every eligibility
position was established by this static inventory. Phase 1 review must inspect
the actual AST constructors and settle the smallest reliable tests before
implementation approval.

## Acceptance scenarios for Phase 1

- Function return: local axes not present before the call or in result binds
  disappear; caller axes and returned coordinates remain.
- Bare block and evolve: the established pre-live/result behavior remains
  unchanged under the existing characterization suites.
- Eager main path: eligible function-call StateBind traces only caller axes
  absent from the subsequent statement live-out; result names remain.
- Deferred main path: the same ADR 0158 boundary is preserved through the
  existing deferred State/Measure executor.
- Eligibility exclusions: inspect in supported bind/measure/expression
  positions and Snapshot continue to disable the interprocedural optimization.
- Ownership/consumers: the successor owns the algorithms; source and runtime
  hook identity, `frames.py`, `execution.py`, `observation.py`, `pipes.py`, and
  `evolution_ops.py` consumers resolve through their actual entry points.

Candidate evidence inventory to reconcile clause-by-clause before Phase 1:
`test_trace_out_gc_fn_scope_red.py`, `test_bare_block_trace_out_red.py`,
`test_evolve_trace_out_gc_red.py`, `test_interprocedural_trace_out_red.py`,
`test_liss_0573_pipes_successor_red.py`,
`test_liss_0561_evaluator_observation_dynamic_red.py`, and
`test_liss_0572_frames_constructors_assignments_red.py`. Existing suites must
be classified as behavior evidence versus structural/lifecycle contracts;
their `_red.py` suffix alone is not current lifecycle status. Add no duplicate
tests where the exact clause is already asserted.

## Proposed ownership and dependency boundary

Candidate destination: `compiler/staqex/runtime/evaluation/liveness.py`.
It should depend on AST DTOs and `Joint`, not import `runtime.evaluator`,
instantiate `Evaluator`, or retain mutable runtime state. Observation and
frame services may depend on its pure functions; the dependency graph must be
checked against actual imports before acceptance. The compatibility facade
continues to expose required existing hook names during migration.

No new VO/DTO, external port, or adapter is indicated. The relevant value is
the existing set of live coordinate names; liveness sets are local immutable
inputs/outputs, not persistent evaluator state.

## Applicable process lessons

- `evaluator-state-ownership`: the successor is stateless; all evaluator maps
  and execution state stay on `Evaluator`.
- `private-consumer-inventory` and `decomposition-callback-boundary`: account
  for private names, context declarations, source inspections, and every
  downstream execution path before changing wiring.
- `decomposition-source-ownership` and `decomposition-boundary`: assert the
  successor owns algorithms, remove duplicate bodies, and do not grow
  `observation.py` or another sibling with an unrelated family.
- `compatibility-hook-identity-contract` and `compatibility-baseline`: inspect
  actual runtime hook installation and preserve symbols according to the
  module's real export rules.
- `acceptance-inventory-reconciliation`: map each accepted clause to an exact
  existing or proposed test before Phase 1 review.
- `status-drift`: synchronize this spec, Issue, Work Plan, and Trace at every
  later approval/status transition.

## Phase 0 decision and remaining gate

Architecture boundary and ownership are accepted by ADR 0228. The Phase 0
acceptance packet records the exact phase file boundary and the evidence/gaps
above. Phase 0 acceptance authorizes only transition to a separately approved
Phase 1 Red; it does not authorize tests, production edits, or Phase 2.
