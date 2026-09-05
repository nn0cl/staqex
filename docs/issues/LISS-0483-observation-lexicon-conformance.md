# LISS-0483: Observation and lexicon conformance closure

| Field | Value |
|---|---|
| Status | **in_progress — bounded Phase 1 Red reproduced; test review required** |
| Phase | phase-1-red (bounded regression slice) |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | LISS-0480, LISS-0481, LISS-0482 |
| Implementation permission | None |
| Next approval | Bounded Red test review; resolve legacy assertion conflict before Green |

## Scope

Build the cross-feature conformance matrix for aliases, `mix`, `superpose`,
`controlled`, `when` retirement, inspection, projection, and terminal measure.
Map each proof to a deterministic test and preserve shipped behavior.

## Acceptance scenarios

- Every accepted spelling and observation operation has one observable path.
- Deferred forms reject explicitly with stable diagnostics.
- Source meaning and review-boundary metadata remain observable.
- Conformance does not imply provider or hardware support.

## Exclusions and stop conditions

No normative grammar change, provider, QPU, Rust, or broad example rewrite.
Stop when a test exposes an ADR/spec conflict; resolve it before Phase 1.

## Phase 1 candidate files

Cross-feature fixtures, proof matrix, conformance Red tests, and documentation
links only.

## Bounded Red evidence (2026-09-05)

The Adjudicator's continuation authorized the previously proposed test-only
slice. Size M; branch `codex/liss-0483-conformance-red`.
Implementation remains unauthorized. Dependencies 0480–0482 are shipped,
but the following conformance defects remain; their prior passing tests are
not evidence of complete semantic preservation.

Test file: `tests/test_liss_0483_observation_lexicon_conformance_red.py`.

| Proof | Test | Observed |
|---|---|---|
| Comments create no semantic operations | `test_comment_does_not_create_commutator_operation` | Red |
| Written operands survive display mapping | `test_commutator_display_retains_actual_operands` | Red |
| Comments cannot change observation lane acceptance | `test_comment_does_not_change_observation_lane_acceptance` | Red |
| Canonical values, including unknowns, survive mapping | `test_mapping_retains_semantic_values_including_unknowns` (two fields) | Red ×2 |
| Mapping does not imply execution | `test_mapping_remains_diagnostic_only` | Pass |

New suite: 5 failed, 1 passed. Existing 0480–0482 suites: 18 passed.
Inputs retain semantic IR but explicitly carry finite-evidence and approximation
obligation diagnostics; these tests do not claim successful finite lowering.
The existing 0482 test expects the literal `preserved`. Review must authorize
replacing those assertions with actual canonical values before Green; do not
silently edit previously reviewed tests. This is an implementation/test
discrepancy against the spec's preservation requirement, not a grammar change.

The full aliases/Mix/Superpose/controlled/when/projection matrix remains open.
This bounded regression suite does not close LISS-0483.
Resume evidence: [trace](../collaboration/traces/2026-09-05-liss-0483-conformance-red.md).
