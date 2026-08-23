# LISS-0448 Post-Green Independent Context Review 02

## Trigger and scope

- Trigger: fresh re-review after accepted Review 01 corrections.
- Independent context: Confucius, fresh read-only reviewer
  `01a02ec9-575d-7d63-8d1d-3bf97e90f577`.
- Scope: current accepted Spec, canonical IR branch fidelity, public and
  legacy QPU projection paths, authority chain, and deterministic evidence.
- Reviewer edits: none.
- Approval authority: none.

## Findings

| Priority | Finding | Evidence | Disposition |
|---|---|---|---|
| P1 | Canonical IR loses blackboard branch meaning: `WhenArm.pat` and `is_else` are skipped, and the mixture stores only an undifferentiated descendant tuple instead of control/branch rule and weights. | `docs/specs/staqex-canonical-qasm-coin-mix-projection.md:46`; `compiler/staqex/scientific_semantic_ir.py:262,325`; `tests/fixtures/canonical_coin_mix/mixture_semantics.sqx:5` | **Architecture/User decision required** |
| P1 | The retained legacy AST lowerer still emits `CX` for a copy-pattern `WhenExpr`, contradicting the accepted no-unitary-fallback disposition. | `docs/specs/staqex-canonical-qasm-coin-mix-projection.md:94`; `compiler/staqex/backend/qasm/lower.py:902-912` | pending disposition; likely fail-closed correction or explicit retirement/inventory |
| P2 | The accepted Spec cites the QPU capability-rejection contract while that contract remains `proposed`, leaving the authority chain ambiguous. | `docs/specs/staqex-canonical-qasm-coin-mix-projection.md:85`; `docs/specs/staqex-qpu-capability-rejection-contract.md:5`; `docs/architecture/open-work-register.md:27` | **Architecture/User decision required** |

## Deterministic evidence

- Focused and related tests: **73 passed**.
- Full spec verification: **161/161 passed**.
- `git diff --check`: passed.
- Public canonical QASM path rejects with empty artifacts and provenance.
- A changed branch pattern produced the same ideal semantic fingerprint.
- Direct legacy path for Mix without preceding Coin produced `CX, Measure`.

## Verdict and terminal state

- Verdict: **NOT READY**.
- Review loop state: **ABORT pending Architecture/User decision**.
- Remaining blockers: preserve branch pattern/control/mixture-rule meaning in
  canonical IR; make every retained legacy path fail closed or explicitly
  retire/inventory it; clarify the authority chain; then run fresh re-review.

## Reusable perspectives

- Blackboard/source-to-domain fidelity.
- Canonical authority and implementation reality.
- Projection conservation and authority reachability.
- Realization/fail-closed behavior.
- Architecture/boundary integrity.
- Evidence and phase discipline.
