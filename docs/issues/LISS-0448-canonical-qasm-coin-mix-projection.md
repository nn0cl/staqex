# LISS-0448: Canonical QASM Projection for Coin/Mix Programs

| Field | Value |
|---|---|
| Status | **Phase 2 Green complete; post-Green review complete; Phase 3 pending** |
| Phase | **phase-2-green** |
| Type / priority | feature follow-up / P1 |
| Initial size | M |
| Current size | M |
| Owner | Staqex compiler maintainers |
| Parent / related | Related to [LISS-0446](LISS-0446-qasm-public-entry-canonical-sharing.md) and [LISS-0447](LISS-0447-residual-semantic-consumer-reconciliation.md) |
| WorkPlan | [WP-0111](../work-plans/WP-0111-canonical-qasm-coin-mix-projection.md) |
| GitHub | Not created |
| Branch | `codex/liss-0448-canonical-qasm-coin-mix-projection` |

## Problem

The current canonical QASM boundary intentionally rejects `Coin`/`Mix` source
programs when their meaning is not represented by the Scientific Semantic IR
QPU projection. Existing SV-10/SV-11 conformance cases still expect the retired
ordinary AST fallback to emit Bell-style OpenQASM. PR #557 records this as a
design-boundary CI failure rather than reintroducing an implicit fallback.

## Objective

Design and, after separate phase approval, implement source-owned canonical
meaning for `Coin`/`Mix`, followed by an explicit target projection only when a
meaning-preserving finite realization exists. The language and semantic IR must
not remove `Coin`/`Mix` merely because a QPU target is currently unable to run
them.

## Acceptance direction

- The chosen direction is recorded in an accepted Spec/ADR decision before
  production implementation.
- If supported, `Coin`/`Mix` semantics are represented in the canonical
  Scientific Semantic IR and projected to QPU IR without an AST fallback.
- If the finite target realization is unsupported, SV-10/SV-11 assert the
  explicit capability rejection while the ideal semantic representation remains
  available.
- No QASM, gate, allocation, or partial program is produced on rejection.
- The Phase 1 rejection contract is exact: code
  `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE`, reason
  `mixture_projection_unavailable`, and empty QASM, QPU instructions, gates,
  allocation, allocated qubits, and partial program.
- The local spec verification gate is green with no hidden compatibility path.

## Exclusions and decision points

- No provider SDK, live QPU submission, credentials, or network integration.
- No S02 numerical migration, solver work, or syntax redesign.
- Do not change ADR 0211 or the explicit Realize/Limit policy implicitly.
- Architecture/User judgment is required if supporting `Coin`/`Mix` changes the
  canonical IR model, QPU capability boundary, or existing ADR contract.
- LISS-0449 and LISS-0450 define the shared boundary and meaning contract;
  this Issue must not independently narrow the language surface.

## Current evidence

- PR [#557](https://github.com/nn0cl/staqex/pull/557) has the canonical
  consumer migration and deliberately retains fail-closed QASM behavior.
- CI Spec verification reports 155/161; the six failures are SV-10/SV-11
  `Coin`/`Mix` expectations.
- Repository-local `python3 tests/spec_verification/run_all.py` reproduces the
  same six failures.

## Phase 1 Red boundary

The Red inventory covers the three focused LISS-0448 tests plus the six live
SV-10/SV-11 cases (`sv10-openqasm-bell`, `sv10-cli-emit-qasm`,
`sv10-target-qpu-emit`, `sv11-qasm3-syntax`, `sv11-gate-map`, and
`sv11-cli-openqasm3`). The conformance cases must be changed only to assert
the accepted capability rejection; they must not restore H+CX fallback.

## AI planning record

- Date: 2026-08-20
- Environment: Codex desktop, repository-local analysis
- Size: M; multiple QASM/IR/spec tests with one bounded semantic decision
- Route: local source inspection, deterministic spec verification, independent
  review before implementation
- Estimate: N/A until the canonical representation decision is accepted
- Confidence: medium; the current rejection is clear, but the correct
  `Coin`/`Mix` QPU meaning requires architecture review

## Approval record

- User approved Phase 1 Red on 2026-08-22.
- Independent design review 01 returned NOT READY with five findings; all
  findings were accepted as in-scope acceptance/documentation corrections.
- Phase 1 Red permits tests and fixtures only. It does not authorize Phase 2,
  production implementation, ADR acceptance, or merge.

## Phase 2 Green evidence

- User approved Phase 2 Green and implementation on 2026-08-23.
- The minimum implementation preserves `Coin` and `Mix` in the canonical
  Scientific Semantic IR and marks unsupported static QASM projection with
  `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` and reason
  `mixture_projection_unavailable`.
- Rejection is atomic: QASM, gates, instructions, allocation, allocated
  qubits, and partial program remain empty.
- Rejection provenance includes the mixture node, branch child IDs, and source
  span as required by the accepted capability-rejection contract.
- Focused LISS-0448 and related semantic/QASM boundary tests: **73 passed**.
- Full spec verification: **161/161 passed (100%)**.
- Phase 3 refactor is recorded in the [refactor trace](../collaboration/traces/2026-08-23-liss-0448-phase3-refactor.md).
- The canonical projection Spec was separately accepted by the user on
  2026-08-23, but Review 02 identified a required branch-meaning expansion.

## Architecture decision and implementation

- ADR 0213 was accepted by the user on 2026-08-23.
- The expanded branch-meaning boundary is accepted under ADR 0213.
- Phase 2 Green implementation is complete: canonical branch rules and arm
  provenance are retained, fingerprints include branch meaning, and the
  legacy copy-pattern path rejects atomically instead of emitting CX.

## Phase 1 Red extension evidence

- User approved the Phase 1 Red extension on 2026-08-23.
- Added tests for canonical control identity, ordered branch rules, semantic
  fingerprint sensitivity, and legacy fail-closed behavior.
- Red result before implementation: **4 failed, 4 passed** in the focused
  LISS-0448 file.
- Green result: **8 passed** in the focused LISS-0448 file and **161/161** in
  full spec verification.
- User approved Phase 2 Green and implementation on 2026-08-23.
- Next safe action: independent post-Green review; Phase 3 remains separately
  gated.
