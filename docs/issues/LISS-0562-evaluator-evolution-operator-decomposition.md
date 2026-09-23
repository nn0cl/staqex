# LISS-0562: Evaluator evolution and operator decomposition

## Metadata

- Local issue ID: LISS-0562
- Status: historical — bounded slice superseded by LISS-0566-C
- Type: Feature Path structural decomposition
- Initial planning size: L
- Current planning size: L
- Parent: WP-0162 (historical)
- Depends on: LISS-0560
- Blocks: none; successor: LISS-0566-C

## Summary

Extract evolution, Hamiltonian, explicit propagator, unitary, QFT, apply/capply,
operator tree, binder, and projection mechanics into cohesive internal families.

## Acceptance Notes

- Evolution outputs, dimension diagnostics, Suzuki/QASM lowering, and operator
  provenance remain unchanged.
- No operator evaluator becomes a second semantic authority.
- Existing host coefficient and finite-binder ports remain the same.
- Unsupported evolution remains fail-closed and atomic.

## Allowed boundary

Candidate modules are `runtime/evaluation/evolution.py` and
`runtime/evaluation/operators.py`. Shared pure numeric helpers may move only
when their owner and import direction are explicit; no vague `utils.py`.

## AI Planning Record

See `AIP-WP-0162-001` in WP-0162. Phase 1 must capture QASM and diagnostic
goldens before any extraction.

## Verification

Evolution/operator characterization, QASM goldens, provenance checks,
finite-binder consumer tests, Spec Verification, and blocking pytest.

## Phase 1 Red acceptance

Accepted on 2026-09-19:
`Feature Path / Phase 1 Red / LISS-0562 evaluator evolution and operator
decomposition 承認`.

This approval authorizes the Phase 1 Red test contract only. It does not
authorize production extraction or Phase 2 Green implementation.

## Phase 1 Red result

Added `tests/test_liss_0562_evaluator_evolution_operator_red.py` with six
contracts:

- internal `evolution` and `operators` entrypoints exist;
- the profiled evolution/operator methods leave the public `Evaluator`
  facade;
- extracted modules depend on explicit context rather than the facade or a
  second mutable state owner;
- the context declares the required evolution/operator callbacks;
- explicit Suzuki QASM output remains characterized;
- finite-binder QPU projection remains provenance-linked to the canonical
  Scientific Semantic IR.

Verification: **1 failed, 5 passed**. The single failure is the intentional
structural Red: all 28 profiled evolution/operator methods still remain on
`Evaluator`. No production source, public API, or test-exclusion file was
changed. Phase 1 test review is required before Phase 2 Green.

## Phase 1 Red test review

Adjudicator approval received on 2026-09-19:
`Feature Path / Phase 1 Red テストレビュー / LISS-0562 evaluator evolution
and operator decomposition 承認`.

The six-test contract and the intentional `1 failed, 5 passed` Red evidence
are accepted. The next gate is typed approval for Phase 2 Green /
Implementation.

## Phase 2 Green / Implementation result

Implementation approval received on 2026-09-19:
`Feature Path / Phase 2 Green / LISS-0562 evaluator evolution and operator
decomposition 実装承認`.

Implemented the first bounded extraction slice:

- separated evolution and operator implementation names from the public
  `Evaluator` facade;
- retained `runtime/evaluation/evolution.py` and
  `runtime/evaluation/operators.py` as family entrypoints;
- moved compatibility alias installation into
  `runtime/evaluation/compatibility.py`;
- preserved the single mutable-state owner and existing private compatibility
  surface.

Verification: LISS-0562 focused tests **6 passed**, adjacent
evolution/operator/QASM/finite-binder tests **33 passed**, and the full
blocking suite at the initial implementation point **2123 passed**.
`compileall` and `git diff --check` also passed.

This is a compatibility-first Green slice, not the final physical relocation
of every legacy method body. The legacy mechanics remain under explicitly
named implementation methods in `evaluator.py`; the next refactor/audit must
either move those bodies into the family modules or record an accepted
cohesion exception. Current `evaluator.py` size is **6,071 lines** (baseline
after LISS-0561: 6,065), so this slice improves ownership clarity but does
not yet claim a line-count reduction.

## Phase 3 Refactor result

Approval received on 2026-09-19:
`Feature Path / Phase 3 Refactor / LISS-0562 evaluator evolution and operator
decomposition 承認`.

Completed a bounded physical relocation of low-coupling helpers:

- moved explicit propagator recognition and joint L2 distance into
  `runtime/evaluation/evolution.py`;
- moved nested Operator-call argument conversion and set-domain projector-sum
  construction into `runtime/evaluation/operators.py`;
- moved the shared `KernelError` definition into
  `runtime/evaluation/errors.py`, while preserving the public evaluator import;
- changed compatibility wiring to install the moved functions directly.

`evaluator.py` is now **5,921 lines**, down from **6,071 lines** in Phase 2
(150 lines removed). Stateful evolution/operator lowering mechanics remain
explicitly named in `Evaluator` and are reserved for a later bounded
extraction rather than being hidden in a generic helper module.

Verification: focused tests **6 passed**, adjacent regression **29 passed**,
full blocking pytest **2,123 passed**, `compileall` passed, and
`git diff --check` passed.

## Historical disposition

Recorded on 2026-09-19 under
`WP-0162/LISS-0562〜0565 整合性整理 承認`.

This bounded predecessor slice is retained as historical evidence and is
superseded by the completed `WP-0163 / LISS-0566-C` operator-lowering
successor. Do not request a separate final review or reopen this issue; any
new evolution/operator extraction requires a new issue and design intake.
