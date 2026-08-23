# LISS-0448 Phase 1 Red Extension — Independent Review 03

- Trigger: fresh re-review after correction commit `167817ff`.
- Review mode: independent, read-only; no implementation or phase approval.
- Scope: self-contained Red tests/fixtures, source anchoring, canonical branch meaning, fingerprint sensitivity, and fail-closed legacy projection.
- Branch: `codex/liss-0448-canonical-qasm-coin-mix-projection`.
- Phase: Phase 1 Red extension.

## Inspected artifacts

- `tests/test_liss_0448_coin_mix_semantic_red.py`
- `tests/fixtures/canonical_coin_mix/`
- `compiler/staqex/scientific_semantic_ir.py`
- `compiler/staqex/backend/qasm/lower.py`
- `docs/specs/staqex-canonical-qasm-coin-mix-projection.md`
- `docs/architecture/adr/0213-canonical-mixture-branch-meaning-and-qpu-boundary.md`
- commits `3d265ea9` and `167817ff`

## Findings

| Priority | Finding | Evidence | Disposition |
| --- | --- | --- | --- |
| P1 | Arm source-span expectation is one line early: the fixture arms are on lines 6 and 7, while the test expects 5 and 6. Runtime arm provenance is still `(0, 0)`, so the contract remains intentionally Red after correcting the expected source lines. | `tests/fixtures/canonical_coin_mix/mixture_semantics.sqx:6-7`; `tests/test_liss_0448_coin_mix_semantic_red.py` | accepted — correct only the test expectation to `(6, 5)` and `(7, 5)` |
| P1 | Legacy copy-pattern Mix still emits a CX fallback instead of rejecting. | `compiler/staqex/backend/qasm/lower.py`; `legacy_mix_fallback.sqx` | accepted — preserve as Phase 2 implementation target |
| P1 | Canonical IR lacks required `control_source_node_id` and ordered `branch_rules`. | `compiler/staqex/scientific_semantic_ir.py`; Red test AttributeError | accepted — preserve as Phase 2 implementation target |
| P2 | Pattern and else mutations are present, but fingerprints remain unchanged until branch meaning is represented in canonical IR; control/rule mutations are not yet separate. | Red fingerprint test | accepted — current Red scope is sufficient to expose the missing branch-rule encoding; control/rule expansion may follow only within Phase 1 if needed |

## Self-contained boundary

The Red tests and all three fixtures are contained in commits `3d265ea9` and `167817ff`. The test is partially source-anchored: branch order is tied to Dirac source lines, while arm source spans are an explicit missing-provenance contract.

## Readiness verdict

`NOT READY` for Phase 2 until the single test expectation correction is recorded and a fresh review confirms no remaining Red-boundary inconsistency. The remaining failures are implementation targets, not reasons to alter the accepted architecture.

## Reusable review lenses

Contract completeness; source-to-domain fidelity; canonical authority; realization-boundary/fail-closed behavior; phase discipline; evidence hygiene; projection conservation.

## Corrections and next review

Correct only the arm line expectations, run the bounded Red harness and diff check, then perform another fresh independent review. No production change or Phase 2 transition is authorized.

## Terminal state

`RE_REVIEW`.

## Approval status

Phase 1 Red extension is approved. Phase 2 Green approval is not granted.
