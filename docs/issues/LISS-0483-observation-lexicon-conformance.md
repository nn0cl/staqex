# LISS-0483: Observation and lexicon conformance closure

| Field | Value |
|---|---|
| Status | **in_progress — prior correction merged; source-evidence Red ready for review** |
| Phase | phase-1-red (source-evidence follow-up) |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | LISS-0480, LISS-0481, LISS-0482 |
| Implementation permission | Prior correction merged; new source-evidence production change awaits test review |
| Next approval | Source-evidence Green and explicit update of four legacy synthetic-success test cases |

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

Historical slice: merged via PR #577 (`da011801`). Full regression at that
boundary: 1913 pass. Current follow-up is described below.

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

New suite: 5 failed, 1 passed before implementation; after the bounded Green
change it is 6 passed. Existing 0480–0482 suites are 16 passed, 2 failed:
two old 0482 assertions required the literal `preserved` value and the
synthetic lane phrase. This was subsequently resolved explicitly in
`d4ca0747`: the combined 0480–0483 suites now pass 24 tests.
Inputs retain semantic IR but explicitly carry finite-evidence and approximation
obligation diagnostics; these tests do not claim successful finite lowering.
The former 0482 test expected the literal `preserved`. The authorized update
compares actual canonical values. This was an implementation/test
discrepancy against the spec's preservation requirement, not a grammar change.

The full aliases/Mix/Superpose/controlled/when/projection matrix remains open.
This bounded regression suite does not close LISS-0483.
Resume evidence: [trace](../collaboration/traces/2026-09-05-liss-0483-conformance-red.md).

## Current source-evidence follow-up

Branch: `codex/liss-0483-source-evidence`; size M.
[Cross-feature matrix](../testing/liss-0483-conformance-matrix.md) now maps
all requested families to named tests or explicit gaps. Selected existing
suites: 46 pass. New suite
`tests/test_liss_0483_observation_source_evidence_red.py`: 5 expected failures.
Four invalid fragments are accepted with invented IDs; a real projection
is omitted from the inventory. Production and legacy tests remain unchanged.

Green completed: synthetic fallback is removed, real projection evidence is
retained, and the four old 0481 synthetic-success cases explicitly assert
closed rejection. The focused source-evidence and related suites pass 24
tests. No grammar or finite-realization authority changed. Remaining matrix
gaps keep this Issue and WP open.

The follow-up also validates multiple commutators and rejects compile-invalid
lexicon inputs. The focused lexicon suite passes 13 tests after its fixture was
made terminally valid. Broader nested-scope alias semantics remain open.
