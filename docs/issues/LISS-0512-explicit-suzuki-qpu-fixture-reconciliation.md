# LISS-0512: Explicit Suzuki finite-QPU fixture reconciliation

| Field | Value |
|---|---|
| Status/phase | **done — Phase 3 refactor and final review complete** |
| Type / priority | feature follow-up / P1 |
| WorkPlan | [WP-0129](../work-plans/WP-0129-explicit-suzuki-qpu-fixture-reconciliation.md) |
| Specification | [Explicit evolution surface](../specs/staqex-explicit-evolution-surface.md) |
| Related | [LISS-0444](LISS-0444-scientific-semantic-core.md), [LISS-0017](LISS-0017-higher-order-suzuki.md) |
| Branch | merged to `main` via [PR #582](https://github.com/nn0cl/staqex/pull/582) |
| Depends on | Phase 0 design trace dated 2026-09-07 |

## Objective

Reconcile the finite Suzuki canonical-projection fixture with the accepted
explicit-evolution and source-visible finite-realization contracts. The test
must not use the retired implicit Hamiltonian shortcut or omit approximation
evidence while claiming canonical QPU instructions.

## Acceptance boundary

- The fixture declares an explicit evolution operator and an explicit
  `Realize(source = ..., method = "suzuki", order = 2, steps = ..., error_budget = ...)` policy.
- The expected canonical QPU projection retains source-node identity,
  Suzuki order/steps, gate provenance, instruction fingerprint, and terminal
  measurement provenance.
- Invalid Suzuki order and instruction/measurement fingerprint mutation remain
  fail-closed with empty or rejected artifacts.
- Explicit `steps` remains a deterministic override and is never silently
  clamped or changed to tolerance mode.

## Exclusions

No provider SDK, AWS/Braket credentials, network, live QPU, Rust migration,
`evolve until`, empty-domain identity, Dirac sugar, or unrelated
semantic-family migration is included in this slice.

## Phase 1 Red plan

- Update only the Suzuki source fixture to the accepted explicit surface.
- Keep the existing canonical instruction and provenance assertions unchanged
  so any missing canonical finite projection is visible as a real Red gap.
- Keep the binder fixture unchanged because its focused test currently passes;
  it is not evidence for widening this issue.
- Run the focused LISS-0444, explicit-step, QPU rejection, and provenance
  suites. Do not alter production code to make the tests pass.

## Phase 1 Red result

- Replaced the legacy implicit-Hamiltonian fixture with explicit `exp` plus
  source-visible `Realize(..., method = "suzuki", order = 2, steps = 2,
  error_budget = 1e-4)` and `Evolve() { U_qpu * psi }`.
- Focused verification: **19 passed, 3 failed**.
- The three intentional Red gaps are: canonical finite gates are not present
  in compile-owned QPU IR, invalid explicit Suzuki retains a terminal Measure
  instruction instead of an entirely empty executable artifact, and QASM
  cannot emit the compliant finite projection without reporting canonical
  projection unavailability.
- Invalid/unresolved policy rejection and fingerprint mutation checks retain
  their fail-closed behavior. Explicit-step neighboring tests remain green.
- No production code, provider, network, or live-QPU behavior was changed.

Phase 2 must decide separately whether to wire explicit `Realize` into the
canonical finite projection and whether invalid policy rejection must remove
the terminal measurement as part of atomic artifact absence.

## AI planning record

- Planning record: `LISS-0512-PLAN-01`
- Status: active for Phase 1 Red
- Authoring environment: Codex local workspace
- Model/reasoning: N/A; deterministic fixture and test reconciliation
- Planning size: M (initial/current)
- Estimated token range: N/A; bounded by one fixture/test area and existing
  acceptance artifacts
- Basis: accepted source contract is known; current canonical QPU behavior for
  explicit `Realize` must be measured by the Red suite before implementation
  scope is decided.

## Approval and next gate

User approval received:
`Feature Path / Phase 1 Red / explicit Suzuki・finite QPU fixture reconciliation 承認`.

## Phase 2 Green result

- User approval: `Feature Path / Phase 2 Green / LISS-0512 canonical explicit-Realize finite QPU projection 承認`, 2026-09-07.
- The Scientific Semantic IR canonical projection now recognizes the accepted
  explicit `exp` + Suzuki `Realize` + `Evolve()` shape and emits finite Suzuki
  gate operations with source-node and comment provenance.
- The QASM emitter now propagates canonical projection errors before the
  generic no-executable-projection diagnostic, preserving the typed finite
  evolution rejection code while keeping the artifact empty.
- Invalid or unresolved Suzuki policy produces no QPU instructions, including
  no terminal Measure, and QASM fails closed without invoking the AST lowerer.
- Focused LISS-0512 and neighboring realization/projection suites: **64
  passed**. Spec verification: **161/161**. `git diff --check` passed.
- Full regression: **1932 passed, 16 failed**. Remaining failures are outside
  LISS-0512 in open semantic-family and consumer-migration suites.

Phase 3 Refactor requires a separate approval and review. Provider SDKs, live
QPU execution, and consumer-wide migration remain excluded.

## Phase 3 Refactor result

- Extracted shared canonical Suzuki operation/provenance construction for the
  explicit and compatibility finite paths without changing assertions or
  output behavior.
- Same-context review packet: [2026-09-07 LISS-0512 Phase 3 review](../collaboration/reviews/2026-09-07-liss-0512-phase3-review.md).
- Post-refactor verification: focused **64 passed**, Spec Verification
  **161/161**, compileall passed, and `git diff --check` passed.
- Final Adjudicator review approval: `LISS-0512 Phase 3 最終レビュー 承認`, 2026-09-07.
- Merged to `main` via PR #582; merge commit `cfcde2a9`.
- Required CI passed: Kernel root suites, Repository sanity, and Spec verification.
- Process review: no operating-contract deviation or operational problem found.
- Status is synchronized as complete; provider SDK, live QPU, and Rust work remain excluded.
