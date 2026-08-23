# LISS-0448 Post-Green Independent Context Review 01

## Trigger and scope

- Trigger: user approval to perform the independent Post-Green review.
- Independent context: Russell, fresh read-only reviewer
  `01a02ea2-ad96-75f0-aa5e-3802258e663f`.
- Scope: current LISS-0448 Phase 3 Refactor implementation, Issue, Spec,
  Work Plan, Phase 3 trace, current diff, focused tests, and SV/spec evidence.
- Reviewer edits: none.
- Approval authority: none.

## Findings

| Priority | Finding | Evidence | Disposition |
|---|---|---|---|
| P1 | Mixture rejection provenance exposed only reason/target plan; the contract requires mixture node, branch-child, and source-span provenance. | `compiler/staqex/backend/qasm/emitter.py`; `docs/specs/staqex-qpu-capability-rejection-contract.md:33-38` | **accepted and corrected**; focused test now pins all fields |
| P1 | The canonical projection Spec remained `proposed` while implementation records assumed an accepted Spec/ADR gate. | `docs/specs/staqex-canonical-qasm-coin-mix-projection.md` | **accepted and resolved by user decision**; Spec separately accepted 2026-08-23 |
| P2 | Phase 3 trace claimed shared code/reason constants, but legacy lowerer rejection literals remained. | `compiler/staqex/backend/qasm/emitter.py`; `compiler/staqex/backend/qasm/lower.py`; accepted Spec competing-path disposition | **accepted and clarified**; canonical QASM authority is Scientific Semantic IR; legacy lowerer is retained fail-closed compatibility boundary |
| P2 | Verification evidence lacked the exact command/test inventory. | `docs/collaboration/traces/2026-08-23-liss-0448-phase3-refactor.md` | **accepted and corrected**; exact command and 73-test scope recorded in correction trace |

## Review lenses

- Contract completeness and diagnostics.
- Architecture/boundary integrity.
- Source-to-domain fidelity.
- Realization and fail-closed behavior.
- Migration/regression safety.
- Canonical authority and projection conservation.
- Executable projection integrity.
- Phase/approval discipline and evidence hygiene.

## Deterministic checks reported by reviewer

- `git diff --check`: passed.
- Scoped focused pytest command: 68 passed.
- `python3 tests/spec_verification/run_all.py`: 161/161 passed.
- Read-only Python AST compilation: passed.
- SV-10/SV-11 public paths reject Coin/Mix without QASM, gates, allocation, or
  H+CX fallback.

## Verdict and terminal state

- Verdict: **NOT READY** for this iteration; corrections are ready for fresh
  independent re-review.
- Review loop state: **RE_REVIEW**.
- Remaining blockers: fresh independent re-review only.
- This review does not approve Phase 3 completion or merge.
