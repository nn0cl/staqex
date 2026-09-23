# LISS-0566-B: Unitary and controlled-gate successor

## Metadata

- Local issue ID: LISS-0566-B
- Status: done
- Phase: complete
- Type: Feature Path bounded structural decomposition
- Priority: high
- Planning size: M
- Parent: WP-0163
- Depends on: LISS-0566 Unit A
- Related branch: `codex/liss-0566-evaluator-stateful-successor`

## Scope

Extract the unitary/gate application mechanics from `runtime/evaluator.py` into
`runtime/evaluation/evolution.py` while preserving local execution, QASM,
diagnostics, private consumer hooks, and the single mutable `Evaluator` state
owner.

Included responsibilities:

- unitary matrix resolution for named gates, rotations, and operator values;
- QFT/IQFT/CQFT register-size validation and dense matrix selection;
- multi-wire `apply` and its wire/identity behavior;
- controlled `capply`/`ocapply`/mixed-polarity parsing and application;
- the tightly coupled `_split_capply_args` helper unless Phase 1 review
  approves a narrower boundary.

Excluded: Unit C operator lowering, Semantic IR changes, provider SDKs,
network, credentials, live QPU, and language-semantic changes.

## Acceptance notes

- `Evaluator` remains the only mutable runtime-state owner.
- Extracted code receives a typed context and does not import or construct the
  public evaluator facade.
- Existing private hooks remain installed through
  `evaluation/compatibility.py` until the successor facade audit.
- Fixed-seed local results, QASM output, diagnostic code/span/order, and
  atomic rejection behavior remain unchanged.

## Phase 1 Red result

Added `tests/test_liss_0566_unit_b_red.py` with seven contracts. The focused
run intentionally reports **4 failed, 3 passed**: the ownership, context, and
compatibility extraction contracts are not yet implemented, while the QFT and
controlled-gate characterization checks pass.

No production source or reviewed assertion was changed. The active-Red entry
is recorded in `docs/testing/active-red-tests.toml`.

## Phase 1 Red test review

Approved on 2026-09-19:
`WP-0163 / LISS-0566-B Phase 1 Red テストレビュー承認`.

The review accepted the four structural Red contracts and three passing
characterizations. The compatibility assertion was strengthened during review
to verify exact evaluator-to-extracted-function assignments rather than mere
name presence. The reviewed suite remains **4 failed, 3 passed** and the
active-Red entry remains owned by this issue.

Next approval required:
`WP-0163 / LISS-0566-B Phase 2 Green / Implementation 承認`.

## Phase 2 Green

Implementation approval received on 2026-09-19:
`WP-0163 / LISS-0566-B Phase 2 Green / Implementation 承認`.

Moved the Unit B gate mechanics into `runtime/evaluation/evolution.py`:

- `resolve_unitary_matrix`
- `qft_family_matrix`
- `bind_apply`
- `is_unitary_name` and `split_capply_args`
- `bind_capply`

`Evaluator` now exposes only narrow read-only callbacks for operator
definitions, operator environment, scalar environment, and static register
sizes. `evaluation/compatibility.py` preserves the established private
evaluator hooks. Unit C and Semantic IR/provider boundaries were unchanged.

Verification: Unit B focused **7 passed**, nearest QFT/apply/capply/QASM/S01
regression **20 passed**, full blocking pytest **2,136 passed**, compileall,
public baseline, Spec Verification, lifecycle, coverage-ledger, and diff
checks passed. The active-Red entry was removed after the accepted contract
became Green.

Measured size: `evaluator.py` decreased from **5,164** to **4,953 lines**;
`evaluation/evolution.py` is **1,092 lines**, below the 1,200-line module
guardrail.

Next approval required:
`WP-0163 / LISS-0566-B Phase 3 Refactor 承認`.

## Phase 3 Refactor

Approved on 2026-09-19:
`WP-0163 / LISS-0566-B Phase 3 Refactor 承認`.

Refactored Unit B without changing behavior:

- clarified the extracted gate entrypoint formatting and type contract;
- added explicit docstrings to the context-owned gate lookups;
- removed duplicate operator-definition lookup while preserving lookup order;
- normalized compatibility import and assignment formatting;
- retained the existing private evaluator aliases and single-state-owner
  boundary.

Verification: focused and nearest regression **27 passed**, full blocking
pytest **2,136 passed**, public baseline, Spec Verification **161/161**,
compileall, lifecycle, coverage-ledger, and diff checks passed. No assertion,
diagnostic, QASM, semantic-authority, or provider boundary changed.

Measured size: `evaluator.py` is **4,957 lines** and `evolution.py` is
**1,106 lines**.

Next approval required:
`WP-0163 / LISS-0566-B Phase 3 最終レビュー 承認`.

## Final review and approval

Review packet: [LISS-0566-B Phase 3 final review](../collaboration/reviews/2026-09-19-liss-0566-b-phase3-final-review.md).

Approved on 2026-09-19:
`WP-0163 / LISS-0566-B Phase 3 最終レビュー 承認`.

Unit B is complete. Unit C and the successor facade audit remain separately
gated in WP-0163; this approval does not authorize them.

## Completion process review

Process review: no operating-contract deviation or operational problem found.
