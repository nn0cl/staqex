# LISS-0503: Unsupported evolution QASM rejection

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0502](LISS-0502-qasm-lowerer-export-retirement.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0503-unsupported-evolution-qasm-rejection) |
| Scope approval | User approved continuation on 2026-09-02 |
| Phase 1 Red approval | User approved continuation on 2026-09-02 |
| Implementation permission | Phase 2 Green and Phase 3 review approved by user |
| Next approval | Next QASM/consumer migration Phase 1 Red |

## Acceptance scenarios

Unsupported explicit evolution must reject with `E_QPU_CANONICAL_PROVENANCE`,
empty QASM, no gates, no allocation, and no provider behavior. Supported finite
projections remain unchanged; target-specific realization is separate.

## Phase 1 Red result

Added `tests/test_liss_0503_qasm_unsupported_evolution_rejection_red.py`.
Verification: **3 failed, 1 passed**, no collection errors. No production
implementation was changed.

## Phase 2 Green design and implementation

The canonical QASM entry now evaluates the already-built `ScientificSemanticIR`
and canonical `QpuProgram` before invoking the QASM realization path. When an
explicit evolution is present but the canonical program has no executable
instructions, the entry returns the stable
`E_QPU_CANONICAL_PROVENANCE` rejection. The rejection is atomic: QASM is empty,
the circuit contains no gates, and allocation has not started.

This guard is intentionally provider-neutral and does not attempt to infer a
finite evolution, select a provider, or call the legacy lowerer. Canonical
finite projections with executable instructions continue through the existing
QPU path.

Verification: **35 passed** across the LISS-0503 acceptance tests and the
LISS-0447, LISS-0444, LISS-0445, and LISS-0456 regression slices; compile and
diff checks also pass. Phase 3 same-context review is the next gate.

## Phase 3 review result

Re-read the acceptance spec, canonical emitter boundary, rejection circuit
helper, dedicated Red tests, and Phase 2 review. The implementation remains a
single readable guard between canonical QPU IR construction and realization;
no further refactor is warranted. Behavior and assertions are unchanged.

Reviewer empathy summary: an unsupported explicit-evolution source now has one
observable, provider-neutral failure path, while a supported finite projection
still has one obvious route to QASM. The issue does not claim target-specific
evolution support.

Same-context review: no blocking finding. Isolation was `same_context`, which
is weaker than `separate_context`.

Verification: **35 passed**, `.venv/bin/python -m py_compile` passed, and
`git diff --check` passed.

Process review: no operating-contract deviation or operational problem found.

Issue complete. The next safe action is a new QASM/consumer migration Phase 1
Red contract.
