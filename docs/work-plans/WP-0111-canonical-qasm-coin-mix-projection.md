# WP-0111: Canonical QASM `Coin`/`Mix` Projection

| Field | Value |
|---|---|
| Status | **proposed** |
| Issue | [LISS-0448](../issues/LISS-0448-canonical-qasm-coin-mix-projection.md) |
| Specification | [Canonical QASM `Coin`/`Mix` Projection](../specs/staqex-canonical-qasm-coin-mix-projection.md) |
| Related | [WP-0109](WP-0109-qasm-public-entry-canonical-sharing.md), [WP-0110](WP-0110-residual-semantic-consumer-reconciliation.md) |
| Branch | Design intake only on `codex/liss-0438-residual-reconciliation` |

## Approved current scope

- Record and explain the six PR #557 SV-10/SV-11 CI failures.
- Design the canonical treatment of `Coin`/`Mix` QASM input.
- Add no production implementation until the proposed Spec and any ADR are
  accepted and Phase 1 Red is separately approved.

## Exclusions

- No AST fallback restoration.
- No provider SDK, live QPU, credentials, network, S02, solver, or syntax work.
- No merge of PR #557 based on this planning record.

## Proposed phases

1. **Phase 0 Design:** decide Option A or B in the Spec and capture an ADR if
   the architecture boundary changes.
2. **Phase 1 Red:** add only focused tests for the accepted direction.
3. **Phase 2 Green:** implement the canonical projection or explicit rejection
   under a new approval.
4. **Phase 3 Refactor:** simplify only after independent review and green full
   spec verification.

## Verification

- Reproduce the six failures with `python3 tests/spec_verification/run_all.py`.
- `.venv/bin/pytest` for the focused QASM/semantic suites.
- `python3 tests/spec_verification/run_all.py` must reach 100% after the
  accepted implementation or accepted conformance update.
- `git diff --check` and independent context review are required.

## Stop conditions

Stop and request Architecture/User judgment if the chosen implementation
changes ADR 0211, the Scientific Semantic IR authority, QPU capability
semantics, explicit Realize/Limit policy, or the language surface.

## Approval record

- User approved separation of the CI conflict into a new Issue/Phase on
  2026-08-20.
- This approval authorizes documentation/design intake only; it does not
  authorize Phase 1 Red, production implementation, ADR acceptance, or merge.
