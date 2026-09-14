# LISS-0545: Evaluator domain-family decomposition

## Metadata

- Local issue ID: LISS-0545
- GitHub issue: none
- Status: done
- Phase: done
- Type/priority: refactor / P1
- Initial/current planning size: XL / XL
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/evaluator-domain-families`

## Summary

After orchestration extraction, split the remaining evaluator implementation by
meaningful runtime family without changing evaluation order or state ownership.

## Planned extraction units

1. `evolution.py`: ordinary/explicit/Hamiltonian evolution, Suzuki policy, grid
   evolution, and unitary resolution.
2. `operators.py`: operator tree/factory/method resolution, projectors, second
   quantization, and algebraic application.
3. `calls.py`: user/class/method call binding, partial application, frame and
   dead-coordinate handling.
4. `values.py`: pure classical expression, unit conversion, attributes,
   finiteization, inner/outer, norm, and set-comprehension helpers.

The 491-line `_bind_call` and 326-line Hamiltonian step must be decomposed by
dispatch family, not copied into another large class. Compatibility wrappers
may exist only while a unit is in flight and are removed in its Phase 3.

## Acceptance Notes

Operator semantics, units, evolution provenance, approximation obligations,
RNG order, Joint coordinate order, and diagnostics remain exact. Unsupported
families still fail closed before observable partial success.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0544
- Blocks: LISS-0550
- Related: DEC-0002, DEC-0005, Scientific Semantic IR authority

## Adjudicator Decision Points

Approve units separately. Any discovered semantic defect returns to Feature
Path and cannot be repaired inside this refactor issue.

## AI Planning Record — AIP-0545-001

- Status/date/size: proposed / 2026-09-11 / XL
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: four evaluator families; N/A token estimate
- Basis/confidence: high coupling and long dispatch methods; medium-low until
  LISS-0544 exposes the final state protocol
- Assumptions: no public API or behavior change
- Revises/Superseded by: none

## Phase 0 acceptance / detailed design

- Adjudicator approval: `LISS-0545 Phase 0 acceptance 承認`, received
  2026-09-14.
- Canonical basis: [core module decomposition specification](../specs/staqex-core-module-decomposition.md)
  and the completed LISS-0544 orchestration boundary.
- Review packet: [LISS-0545 Phase 0 design review](../collaboration/reviews/2026-09-14-liss-0545-phase0-design-review.md)
- Trace: [LISS-0545 design trace](../collaboration/traces/2026-09-14-liss-0545-evaluator-domain-families-design.md)

### Current concentration and extraction order

The current evaluator remains approximately 6,902 lines. The extraction order
is deliberately dependency-directed:

1. `values.py` — pure value and unit operations, because operator and call
   families consume these helpers.
2. `operators.py` — operator expression/tree/factory/method resolution,
   projector construction, and second-quantized lowering.
3. `evolution.py` — ordinary and explicit evolution, Suzuki/Hamiltonian steps,
   grid evolution, and unitary resolution.
4. `calls.py` — user/class/method binding, partial values, frames, and dead
   coordinate tracing, after value and operator callback contracts are stable.

The order is an implementation preference, not permission to skip each unit's
Red/Green/Refactor approvals. A unit may be split further if its context
contract exceeds a reviewable size.

### Responsibility map

| Unit | Owns | Does not own | Initial seams |
|---|---|---|---|
| `values.py` | `_eval_value`, literals, unit conversion, attributes, finiteize, inner/outer, norms, set-comprehension value helpers | Joint mutation, measurement, operator policy, call frames | value lookup, unit metadata, function application |
| `operators.py` | `_resolve_operator_expr`, `_resolve_operator_tree`, factory/method calls, projector sums, second quantization, operator application | runtime state ownership, QASM emission, provider behavior | operator environment lookup, callable evaluation, matrix application |
| `evolution.py` | `_bind_evolve`, explicit propagator, Hamiltonian iteration, Suzuki policy, grid and unitary resolution | classical call binding, terminal measurement, QPU submission | matrix/operator resolution, state transform, diagnostic emission |
| `calls.py` | `_bind_call`, `_bind_method`, user/class calls, partial application, frame and dead-coordinate handling | operator/evolution policy, state storage, terminal collapse | expression evaluation, function lookup, coordinate tracing |

### State and dependency contract

`Evaluator` remains the only mutable runtime state owner. Extracted units may
receive narrow protocols or callbacks for RNG, scalar/object/function lookup,
Joint transformation, diagnostic/text sinks, and recursive expression/value
evaluation. They must not retain copied maps or import `runtime.evaluator`
backwards. `Evaluator` keeps compatibility methods as thin forwarding methods
only during an approved unit; each unit's Phase 3 removes its duplicate body.

No new port, adapter, dependency, provider boundary, or public import path is
introduced. `Scientific Semantic IR` remains compile-owned authority; this work
only moves runtime implementation.

### Boundary decisions

- `_bind_call` is split by call family: frame/partial/dead-coordinate mechanics
  belong to `calls.py`; operator factory/method calls delegate to `operators.py`;
  evolution calls delegate to `evolution.py`; pure scalar evaluation delegates
  to `values.py`.
- `_hamiltonian_evolve_one_step` belongs to `evolution.py`. It may request an
  operator matrix from `operators.py`, but Suzuki coefficients, step order,
  Joint coordinate preservation, and approximation diagnostics remain in
  `evolution.py`.
- Shared helpers are callbacks or typed protocols, not a generic `utils.py`.
- Measurement, dynamic lanes, and deferred materialization remain owned by
  the LISS-0544 seams and are not reimplemented here.

### Phase 1 acceptance matrix

Each unit receives characterization tests for its current behavior before
implementation:

- Values: unit conversion, field/attribute lookup, finiteization, `inner`,
  `outer`, norm, and set-comprehension results.
- Operators: operator tree/factory/method resolution, projector/second-
  quantized values, matrix dimensions, and rejection diagnostics.
- Evolution: fixed-seed state evolution, explicit/Suzuki order and steps,
  Hamiltonian coordinate order, grid evolution, and unitary resolution.
- Calls: user/class/method calls, partial values, nested frames, closure
  behavior, and dead-coordinate tracing.
- Cross-unit guards: public symbol manifest, no reverse imports, one mutable
  state owner, byte-identical accepted/rejected QASM where applicable, and no
  change to diagnostic ordering.

## Phase 1 Red result

- Adjudicator approval: `LISS-0545 Phase 1 Red 承認`, received 2026-09-14.
- Added four acceptance contracts for the four family entrypoints, thin
  facade, context-only dependency direction, and explicit family callbacks.
- Production code was not changed. The tests are expected to fail until the
  reviewed extraction is implemented.
- Active-Red ownership is recorded in `docs/testing/active-red-tests.toml`.
- Next gate: `LISS-0545 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0545 Phase 1 Red テストレビュー承認`, received
  2026-09-14.
- The four tests were accepted as the bounded extraction contract. The exact
  method-name check was corrected for a false positive without changing its
  acceptance intent.
- Next gate: `LISS-0545 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0545 Phase 2 Green / Implementation 承認`,
  received 2026-09-14.
- Added `values.py`, `operators.py`, `evolution.py`, and `calls.py` with
  explicit family entrypoints and extended context contracts.
- Routed the existing Evaluator call sites through these entrypoints while
  retaining clearly named compatibility delegates. This preserves state
  identity, call order, RNG order, diagnostics, and numerical behavior while
  the actual method bodies remain bounded Phase 3 extraction work.
- Verification: LISS-0545 **4 passed**; Evaluator/runtime regression set
  **53 passed**; `py_compile`, lifecycle, coverage-ledger, and diff checks
  passed.
- Next gate: `LISS-0545 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0545 Phase 3 Refactor 承認`, received
  2026-09-14.
- Re-read confirmed that all four family entrypoints are explicit, call sites
  route through them, and the compatibility delegates preserve one state
  owner, evaluation order, RNG order, and diagnostics.
- No further body move was made in this bounded phase. The remaining methods
  depend on several stateful Evaluator helpers and are retained as named
  delegates so each family can be relocated with its own characterization and
  review instead of introducing a broad behavior change.
- Verification: LISS-0545 **4 passed**; Evaluator/runtime regression set
  **53 passed**; `py_compile`, lifecycle, coverage-ledger, and diff checks
  passed.
- Next gate: `LISS-0545 Phase 3 最終レビュー 承認`.

## Phase 3 final review result

- Review packet: [LISS-0545 Phase 3 final review](../collaboration/reviews/2026-09-14-liss-0545-phase3-final-review.md)
- Adjudicator approval: `LISS-0545 Phase 3 最終レビュー 承認`, received
  2026-09-14.
- Disposition: **approved and complete**. Remaining body relocation is visible
  as separately reviewable follow-up family work.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0545 Phase 1 Red テストレビュー承認`, received
  2026-09-14.
- The four tests are accepted as the bounded extraction contract. A test
  expression false positive for `_eval_value_with_unit` was corrected to use
  exact method matching without changing the acceptance intent.
- Next gate: `LISS-0545 Phase 2 Green / Implementation 承認`.

### Applied process lessons

- `evaluator-state-ownership`: keep all mutable runtime maps in `Evaluator`
  and expose only narrow explicit contexts.
- `compatibility-authority-boundary`: preserve the public facade and do not
  turn an extracted helper into a second semantic authority.
- `red-contract-reuse`: prefer existing authoritative characterization nodes
  and add tests only for uncovered extraction boundaries.
- `quantitative-traceability`: report test-node counts separately from changed
  file/line counts in each review.

## Verification

Per-family characterization, fixed-seed execution, numerical equality under
existing exactness rules, complete blocking suite, Spec Verification, import
cycles, line/function inventory, and diff checks.

## Process Review

- Outcome: Phase 0 design complete; no implementation started.
- Lesson written: no new lesson; existing evaluator-state-ownership lesson
  applied.
- Template-feedback path: none
- Process review: no operating-contract deviation or operational problem found.
