# ADR 0228: Evaluator coordinate liveness boundary

## Status

Accepted — Adjudicator approved `WP-0174 / LISS-0581 Architecture boundary 承認`
on 2026-09-28.

## Context

The Evaluator retains coordinate-liveness and automatic Trace-Out helpers used
by invocation frames, pipes, evolution, eager execution, and deferred
observation. `evaluation/frames.py` duplicates coordinate-name enumeration and
function-local Trace-Out. The AST inspection/free-variable walkers currently
live in `evaluation/observation.py` and also support observation analysis.
This is a cohesive but cross-module ownership boundary whose extraction must
preserve accepted Trace-Out decisions ADR 0138/0142/0153/0158 and must not
expand into a new liveness analysis.

## Dependency Adoption Evidence

Not applicable. This decision selects no dependency, provider, datastore, or
build/test tool.

## Decision

1. Pure coordinate liveness and existing automatic Trace-Out mechanics may be
   owned by a focused `compiler/staqex/runtime/evaluation/liveness.py`
   successor.
2. The successor remains stateless: it may depend on AST DTOs and `Joint`, but
   must not import or instantiate `runtime.evaluator`, retain evaluator state,
   or create copied mutable maps. `Evaluator` remains the sole mutable runtime
   state owner.
3. Existing Evaluator private hook names needed by current consumers remain
   available as thin compatibility delegates during this migration. The
   successor owns each moved algorithm; duplicate implementation bodies may
   not remain behind the facade.
4. `_expr_has_inspect` and `_expr_free_vars` may join the liveness owner only
   as part of the same liveness analysis, with existing observation consumers
   and LISS-0561 contracts explicitly reconciled before Phase 1. Unrelated
   deferred observation/execution algorithms remain outside this boundary.
5. Preserve existing behavior exactly: function-call/frame, bare-block,
   evolve, eager-main, and deferred-main callers keep their current live-name,
   result-name, eligibility, and `Joint.trace_out` inputs. ADR 0158's
   inspect/snapshot exclusion and statement live-out contract remain unchanged.
   This ADR does not authorize broader cleanup, semantic changes, test changes,
   or source edits.
6. `_eval_set_comprehension`, runtime-plan dispatch/eligibility, host input
   resolution, static `forEach`, tensor binding, and other Evaluator residuals
   remain outside this successor.

## Consequences

Positive:

- A duplicated coordinate transformation family can have one implementation
  owner without enlarging `observation.py` or `frames.py` with unrelated code.
- Existing callers and private hook names can be preserved while actual
  consumer migration is verified.
- Liveness ownership remains separate from mutable evaluator state and from
  canonical semantic authority.

Negative:

- The migration spans multiple runtime consumers and existing structural
  contracts; consumer smoke and exact hook evidence are required.
- `Evaluator` may retain thin compatibility methods until a separate approved
  retirement decision establishes that callers no longer need them.

## Enforcement

Code review should reject:

- any changed Trace-Out retention rule, eligibility, live-out statement set,
  measurement behavior, or explicit `trace_out` semantics;
- any duplicate algorithm left in the Evaluator facade or frame module after
  the successor becomes owner;
- a second mutable state owner, copied evaluator maps, or successor dependency
  on `runtime.evaluator`;
- removal of existing private hooks without consumer inventory and a distinct
  approved compatibility decision;
- treating Phase 0 architecture acceptance as Phase 0 acceptance, Phase 1
  approval, or implementation authorization.

## Follow-up

- [LISS-0581](../../issues/LISS-0581-evaluator-coordinate-liveness-successor.md)
  and [WP-0174](../../work-plans/WP-0174-evaluator-residual-responsibility-successors.md)
  define the bounded successor. The next gate is separate LISS-0581 Phase 0
  acceptance; Phase 1 Red and implementation require their own approvals.
