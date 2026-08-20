# LISS-0447 Ordinary QASM Phase 2 Green Review 01

| Field | Value |
|---|---|
| Trigger | Fresh independent review after ordinary-QASM Green implementation |
| Independent context | Separate reviewer context; read-only inspection, no edits or approval |
| Scope | Ordinary-QASM canonical projection subcontract only |
| Verdict | **READY** |
| Phase status | Phase 2 Green complete; Phase 3 Refactor requires separate approval |

## Findings and disposition

| Priority | Finding | Evidence | Disposition |
|---|---|---|---|
| P0/P1 | No blocker found in the approved subcontract. | focused tests, emitter/QPU IR paths | resolved by verification |
| P2 | Dirty worktree makes historical change attribution non-isolatable from current state alone. | current branch status | deferred; trace scope and file evidence are explicit |
| P2 | Direct per-operation source-node assertions could be expanded beyond the existing canonical instruction checks. | QASM regression and QPU IR provenance path | deferred; implementation already attaches and validates every instruction provenance |
| Known | LISS-0446 Limit rejection test expects an obsolete code. | `test_qasm_entry_preserves_limit_rejection_without_artifacts` | deferred; outside ordinary-QASM scope and recorded as pre-existing |

## Acceptance evidence

- Scientific Semantic IR produces canonical operations for ket preparation,
  `apply`, `cnot`, `capply`, S/T/CZ, RX/RY/RZ, and terminal measurement.
- QPU IR consumes those operations and preserves canonical `source_node_id`.
- The ordinary fixture's AST fallback call is prohibited by a focused test.
- Unsupported ordinary input rejects with no QASM, gates, allocation, or
  partial program.
- Finite Suzuki/binder compatibility lowering remains outside this ordinary
  path and unchanged.
- Focused/regression command: **42 passed, 1 pre-existing failure**.
- `git diff --check`: passed.

## Reusable reviewer perspectives

- Check operation coverage at the canonical source projection, not only at the
  final QASM text.
- Verify source provenance survives every instruction conversion.
- Review fallback retirement branch-by-branch and preserve explicitly scoped
  compatibility paths.
- Assert artifact absence for unsupported inputs, including allocation state.
- Separate known failures outside the approved subcontract from new failures.

## Terminal state

`COMPLETE` for the ordinary-QASM independent review loop. This review does not
approve Phase 3 Refactor or any provider/live-QPU work.
