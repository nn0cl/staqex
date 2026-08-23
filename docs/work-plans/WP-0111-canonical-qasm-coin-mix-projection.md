# WP-0111: Canonical QASM `Coin`/`Mix` Projection

| Field | Value |
|---|---|
| Status | **final-review-ready** |
| Issue | [LISS-0448](../issues/LISS-0448-canonical-qasm-coin-mix-projection.md) |
| Specification | [Canonical QASM `Coin`/`Mix` Projection](../specs/staqex-canonical-qasm-coin-mix-projection.md) |
| Related | [WP-0109](WP-0109-qasm-public-entry-canonical-sharing.md), [WP-0110](WP-0110-residual-semantic-consumer-reconciliation.md) |
| Branch | `codex/liss-0448-canonical-qasm-coin-mix-projection` |

## Approved current scope

- Record and explain the six PR #557 SV-10/SV-11 CI failures.
- Design the canonical treatment of `Coin`/`Mix` QASM input.
- Add no production implementation until the proposed Spec and any ADR are
  accepted and Phase 1 Red is separately approved.

## Exclusions

- No AST fallback restoration.
- Explicit source-declared finite Suzuki/binder compatibility lowering remains
  allowed; implicit Suzuki inference remains prohibited.
- No provider SDK, live QPU, credentials, network, S02, solver, or syntax work.
- No merge of PR #557 based on this planning record.

## Proposed phases

1. **Phase 0 Design:** define the source-owned `Coin`/`Mix` semantic form and
   capture an ADR if the architecture boundary changes.
2. **Phase 1 Red:** add focused tests proving semantic preservation first and
   finite QPU projection behavior separately.
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

## Fixed Phase 1 Red inventory

- `tests/test_liss_0448_coin_mix_semantic_red.py`;
- fixture `tests/fixtures/canonical_coin_mix/mixture_semantics.sqx`;
- structural `Coin`/`Mix`/branch fields and QPU rejection preservation;
- exact rejection code `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` and reason
  `mixture_projection_unavailable`;
- no QASM/gates/instructions/allocation/allocated qubits/partial program on
  unsupported finite projection;
- the six existing SV-10/SV-11 H+CX expectations as the conformance boundary:
  `sv10-openqasm-bell`, `sv10-cli-emit-qasm`, `sv10-target-qpu-emit`,
  `sv11-qasm3-syntax`, `sv11-gate-map`, and `sv11-cli-openqasm3`.

Test IDs:

- `test_liss_0448_coin_builds_structural_semantic_node`;
- `test_liss_0448_mix_preserves_branch_children_and_provenance`;
- `test_liss_0448_qpu_rejection_preserves_ideal_semantic_result`.
- The six SV-10/SV-11 cases above must be updated only after the focused Red
  contract is present; their accepted result is explicit rejection, not
  Bell-style H+CX emission.

## Stop conditions

Stop and request Architecture/User judgment if the chosen implementation
changes ADR 0211, the Scientific Semantic IR authority, QPU capability
semantics, explicit Realize/Limit policy, or the language surface.

## Approval record

- User approved separation of the CI conflict into a new Issue/Phase on
  2026-08-20.
- User approved Phase 1 Red on 2026-08-22. This authorizes test/fixture work
  only; it does not authorize Phase 2, production implementation, ADR
  acceptance, or merge.

## Phase 2 Green evidence

- User approved Phase 2 Green and implementation on 2026-08-23.
- Production changes are limited to canonical Coin/Mix semantic metadata,
  mixture relation classification, and atomic static-QASM capability
  rejection.
- Focused and related boundary tests: **73 passed**.
- Full spec verification: **161/161 passed (100%)**.
- Phase 3 refactor is recorded in `docs/collaboration/traces/2026-08-23-liss-0448-phase3-refactor.md`.
- Review 02 identified that generic branch traversal loses pattern/else/rule
  meaning and that the legacy lowerer can still emit `CX` for a copy-shaped
  mixture. ADR 0213 accepts the expanded boundary.
- Phase 1 Red extension review loop completed with terminal state `COMPLETE`.
- Phase 2 Green is approved by the user and implemented; independent
  post-Green review is now required before Phase 3.

## Phase 1 Red extension

- Tests added: `test_liss_0448_mix_preserves_control_and_branch_rules` and
  `test_liss_0448_legacy_mix_lowering_is_fail_closed`.
- Focused Green result: **8 passed** after implementing canonical control,
  ordered branch rules, arm source spans, fingerprint sensitivity, and
  fail-closed legacy lowering.
- Full spec verification: **161/161 passed (100%)**.
- Required next review: independent post-Green review; Phase 3 remains
  separately gated.

## Phase 3 Refactor closeout

- User approved Phase 3 Refactor on 2026-08-24.
- Refactor is limited to rejection-policy readability in the legacy lowerer;
  no semantic or target behavior changed.
- Status is `final-review-ready` pending final review and completion packet.
