# LISS-0566-B: Unitary and controlled-gate successor

## Metadata

- Local issue ID: LISS-0566-B
- Status: review — Phase 1 Red; test review pending
- Phase: phase-1-red
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

## Next approval

`WP-0163 / LISS-0566-B Phase 1 Red テストレビュー承認`
