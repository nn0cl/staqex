# LISS-0566: Evaluator stateful evolution/operator successor

## Metadata

- Local issue ID: LISS-0566
- Status: review — Phase 3 final review complete; Adjudicator approval pending
- Phase: phase-3-refactor
- Type: Architecture Path successor / structural decomposition
- Priority: high
- Initial planning size: XL
- Current planning size: XL
- Owner/agent: Codex host agent
- Parent: WP-0163 / WP-0162 successor
- Depends on: LISS-0562, LISS-0560
- Blocks: successor facade/budget audit
- Related branch: `codex/liss-0566-evaluator-stateful-successor`

## Summary

Continue the physical decomposition of `runtime/evaluator.py` for the
stateful evolution and operator lowering families. Preserve `Evaluator` as
the only mutable runtime-state owner and retain all public/private compatibility
surfaces while moving implementation bodies into cohesive internal modules.

## Acceptance Notes

- Fixed-seed local execution, measurements, stdout, diagnostics, and
  provenance remain unchanged.
- Accepted QASM and rejected-input behavior remain byte/diagnostic identical.
- Scientific Semantic IR remains the compile-owned semantic authority.
- Extracted modules receive explicit context/callbacks and do not construct or
  cache a second `Evaluator` state owner.
- No provider SDK, network, credential, filesystem, or live-QPU behavior is
  introduced.

## Phase 0 profile and decomposition

The current `evaluator.py` is **5,921 lines** with **136 definitions**. The
remaining LISS-0562 stateful surface is split into three implementation units:

| Unit | Methods | Body lines | Candidate owner | Main state/callback boundary |
|---|---:|---:|---|---|
| A — evolution execution | 10 | ~800 | `evaluation/evolution.py` | `Joint`, `operators`, `scalars`, `objects`, grid Hamiltonians, `_bind`, value/unit evaluation, provenance |
| B — unitary/gate application | 4 | ~225 | `evaluation/evolution.py` | unitary resolution, QFT register sizes, apply/capply wire validation, `operators`/`scalars` |
| C — operator resolution/lowering | 11 | ~513 | `evaluation/operators.py` | operator maps, structs/classes/objects, finite-binder arrays, scalar evaluation, assignment callbacks |

Unit A contains the high-risk Hamiltonian loop and must be implemented as a
bounded sub-unit before B. Unit B is lower risk once the unitary resolver has
an explicit context contract. Unit C must preserve factory/method-call local
bindings and finite-binder materialization; it is not a generic AST utility
layer.

## Context contract decisions

`Evaluator` remains the live context. The extracted functions may call only
declared narrow callbacks for orchestration:

- evolution: `_bind`, `_bind_evolve_hamiltonian`, `_bind_explicit_evolve`,
  `_bind_user_fun`, `_eval_times`, `_eval_max_steps`,
  `_eval_until_predicate`, `_eval_value_with_unit`, and provenance/state
  setters;
- unitary/gate: `resolve_operator`/operator maps, static register sizes,
  scalar environment, and explicit wire validation helpers;
- operator: operator/scalar/object/class/struct environments, array context,
  `_eval_set_comprehension`, `_exec_assign`, receiver resolution, and the
  canonical operator-tree recursion callback.

No extracted function may import `runtime.evaluator`, instantiate `Evaluator`,
or retain mutable maps after the call. Compatibility aliases remain installed
in `evaluation/compatibility.py` until the final facade audit.

## Phase 1 Red contract

Phase 1 added only the Unit A structural tests, this issue, the work plan,
the active-Red lifecycle entry, and the trace. Tests assert:

1. the Unit A manifest and evolution module ownership;
2. no public facade import or second evaluator construction in extracted code;
3. the Unit A callback/context declaration;
4. private consumer compatibility for evolution paths;
5. fixed-seed evolution and QASM characterization before extraction;
6. the existing operator projection remains a characterization dependency but
   does not expand this Unit A structural scope.

## Phase 1 Red result

Added `tests/test_liss_0566_evaluator_stateful_successor_red.py` with six
Unit A contracts. The focused run intentionally reports **3 failed, 3
passed**:

- the Unit A evolution entrypoint is not yet present;
- the 10 Unit A implementation bodies remain in `Evaluator`;
- the successor callback contracts are not yet declared;
- the no-facade dependency and QASM/operator characterization contracts pass.

No production source, public API, or test-exclusion rule was changed.

## Phase 1 Red test review

Approved on 2026-09-19:
`Feature Path / Phase 1 Red テストレビュー / LISS-0566 stateful evolution and
operator lowering successor 承認`.

The six-test contract and intentional **3 failed, 3 passed** Red evidence are
accepted. The active-Red entry remains until the approved Green unit passes.
Phase 2 is narrowed to Unit A only; Unit B and Unit C require their own
bounded implementation approval.

## Phase 2 Green — Unit A

Implementation approval received on 2026-09-19:
`Feature Path / Phase 2 Green / LISS-0566 Unit A evolution execution
implementation 承認`.

Physically moved the ten Unit A evolution execution methods into
`runtime/evaluation/evolution.py` and retained the existing private evaluator
surface through direct compatibility wiring. `Evaluator` remains the only
mutable state owner; the extracted functions receive the evaluator context and
do not import or construct the public facade.

`evaluator.py` decreased from **5,921** to **5,164 lines** (**757 lines
removed**). The remaining Unit B unitary/gate methods and Unit C operator
lowering methods remain explicitly out of this Green scope.

Verification: LISS-0566 focused tests **6 passed**, adjacent evolution/QASM/
finite-binder regression **58 passed**, public-symbol baseline passed,
full blocking pytest **2,129 passed**, compileall passed, and lifecycle/diff
checks passed. The active-Red entry was removed after the accepted contract
became green.

## Phase 3 Refactor — Unit A

Approved on 2026-09-19:
`Feature Path / Phase 3 Refactor / LISS-0566 Unit A evolution execution
承認`.

Refactored the extracted Unit A module without changing runtime behavior:

- renamed the ten internal `*_evolution_legacy_*` implementation functions to
  responsibility-oriented names such as `bind_evolve`,
  `hamiltonian_evolve_one_step`, and `evolve_precomputed_grid`;
- added explicit `EvaluatorContext` annotations to the extracted callbacks;
- kept the evaluator's established private names in
  `evaluation/compatibility.py`, so consumers retain the compatibility
  surface while the module no longer presents legacy names as its primary
  implementation API;
- left Unit B, Unit C, the single mutable `Evaluator` state owner, and the
  semantic/QASM boundaries unchanged.

Verification: focused Unit A and adjacent characterization **12 passed**, full
blocking pytest **2,129 passed**, public-symbol baseline passed,
compileall, active-Red lifecycle, document lifecycle, coverage-ledger
consistency, and `git diff --check` passed. No behavior or public surface
change was introduced. `evaluator.py` remains **5,164 lines** and the
extracted `evolution.py` is **861 lines**.

## Phase 3 Final Review

Review packet: [LISS-0566 Phase 3 final review](../collaboration/reviews/2026-09-19-liss-0566-phase3-final-review.md).

The same-context review found no implementation blocker. The canonical
decomposition evidence was synchronized to the measured `evaluator.py` size.
The review used `same_context`, which is weaker than `separate_context`; it
does not replace Adjudicator approval.

- Next approval required: `LISS-0566 Phase 3 最終レビュー 承認`.
- Completion process review is pending until the issue is accepted as done.

## Adjudicator Decision Points

- Phase 0 accepted on 2026-09-19:
  `Architecture Path / Phase 0 acceptance / evaluator stateful evolution and
  operator lowering successor 承認`.
- Next approval required: `Feature Path / Phase 3 最終レビュー / LISS-0566
  Unit A evolution execution 承認`.
- Phase 2 Green requires a separate implementation approval for one named unit.
- Return to Architecture review if callbacks require shared mutable state,
  public DTO changes, semantic-authority movement, or a new dependency.

## AI Planning Record

### AIP-LISS-0566-001

- Status: accepted for Phase 0 design
- Created by: Codex host agent
- Model/reasoning: N/A; host does not expose identifiers
- Created at: 2026-09-19
- Planning size: XL
- Intended route: Architecture Path Phase 0, then Feature Path bounded units
- Intended scope: stateful evolution, unitary/gate, and operator lowering only
- Estimate: N/A; no compatible token-planning metric exposed
- Basis: 1,538 measured body lines, 25 methods, mutable-state fan-out, and
  QASM/local execution preservation requirements
- Assumptions: extraction remains semantics-preserving; no behavior fixes
- Confidence: medium
- Revises: AIP-WP-0162-001 for the successor slice

## Verification

Phase 1/2/3 units must run focused characterization, nearest evolution and
operator tests, public-symbol baseline, fixed-seed runtime snapshots, QASM
goldens, Spec Verification, full blocking pytest, compileall, import-cycle,
test-lifecycle, coverage-ledger, and `git diff --check`.

## Process Review

- Outcome: not yet; Unit A final review remains open
- Lesson written: no new lesson; evaluator-state-ownership and private-consumer
  inventory lessons applied
- Template-feedback path: none
