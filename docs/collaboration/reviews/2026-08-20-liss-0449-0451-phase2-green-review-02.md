# LISS-0449–0451 Phase 2 Green Independent Review 02

## Trigger

- Request: fresh independent review after correction of Review 01 findings.
- Scope: Phase 2 Green implementation for LISS-0449–0451 / WP-0112–0114.
- Branch: `codex/liss-0438-residual-reconciliation`.
- Allowed paths: QASM lowerer/emitter, Scientific Semantic IR, related tests
  and review/trace records.
- Excluded: Phase 3, merge/push, live QPU, provider SDK, S02 migration,
  credentials and network.

## Independent context

- Reviewer: fresh context `01a01f46-de30-7932-a1d6-2fd0fcf3b1f2`.
- Read-only: yes. Implementation and approval authority: none.
- Review lenses: ideal/finite boundary, capability honesty, atomic rejection,
  provenance, semantic meaning preservation, pre-allocation safety.

## Findings and disposition

1. **P1 — rejection envelopes remained inconsistent in emitter paths.**
   Several canonical-provenance, unsupported-opcode, and projection failures
   still returned nonzero qubit/bit counts without the empty allocation fields.
   **Disposition: accepted** under the existing LISS-0451 rejection contract;
   corrected by making emitter target rejections empty and provenance-bearing.
2. **P1 — ExactExponential classification was too broad.** `exp` callee name
   alone classified arbitrary exponentials as quantum exact evolution.
   **Disposition: accepted** as a design-preserving semantic guard;
   classification now requires an explicit imaginary factor and another
   source operand.
3. **P1 — finite binder resource overflow lacked rejection provenance.**
   **Disposition: accepted**; the specialized pre-allocation path now records
   reason, source evidence, required qubits, budget, and `target_plan=None`.

All dispositions are within the already approved Phase 2 scope and do not
change the ideal language, realization mechanism, provider boundary, or
Issue phase. No user escalation was required.

## Corrections and verification

- Updated `compiler/staqex/scientific_semantic_ir.py`,
  `compiler/staqex/backend/qasm/lower.py`,
  `compiler/staqex/backend/qasm/emitter.py`, and related tests.
- Focused boundary regression: **35 passed**.
- `git diff --check`: passed.

## Readiness

- Verdict returned by reviewer: `NOT READY` for the three findings above.
- After disposition/correction, the next condition is a fresh independent
  review using the current worktree. This record is not a phase approval.
- Terminal state: not terminal.
