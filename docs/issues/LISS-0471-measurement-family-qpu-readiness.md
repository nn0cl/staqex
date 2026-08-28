# LISS-0471: Measurement-family QPU readiness boundary

| Field | Value |
|---|---|
| Status | **done — Measurement bounded slice complete; broader capability deferred** |
| Phase | phase-3-refactor |
| Type | semantic contract |
| Priority | P1 |
| Initial size | L |
| Current size | L |
| Owner | semantic/Host measurement boundary |
| Parent | WP-0120; LISS-0457 |
| Depends on | LISS-0457 Product/Tensor bounded slice |
| Blocks | LISS-0462 |
| Branch | `codex/liss-0471-measurement-family-qpu-readiness` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0471--measurement-family-qpu-readiness) |
| Implementation permission | Phase 3 refactor — Measurement slice only |
| Post-review requirement | CI pytest and human merge review; broader capability remains separately gated |

## [DESIGN CHECK]

- **Scope and expected behavior:** classify measurement meaning from the
  source-derived Semantic IR; preserve the distinction between terminal
  collapse and dynamic measurement/feed-forward; reject unsupported dynamic
  target capability before artifact/QASM emission.
- **Specifications and files inspected:** `staqex-real-qpu-readiness-acceptance.md`,
  `staqex-dynamic-qpu-lane.md`, `staqex-dynamic-jobresult-trace.md`,
  `dynamic_measurement.sqx`, ADR 0197, ADR 0198, and the existing Semantic IR.
- **Boundaries:** compiler semantic classification and provider-neutral
  rejection only. No provider SDK, credentials, network, POVM/tomography,
  result sampling, or live QPU.
- **Decisions and ambiguities:** terminal `measure` remains the collapse
  boundary. Dynamic support is target-profile dependent. Exact target profile
  DTO and QASM emission remain owned by LISS-0462 and are not selected here.
- **Included context:** existing dynamic-lane contracts, Semantic IR markers,
  rejection diagnostics, and local fixture. **Omitted:** provider payloads,
  secrets, and unrelated execution adapters.
- **Verification:** Phase 1 adds failing tests only; offline fixture execution,
  no-artifact rejection, lane distinction, and deterministic diagnostics are
  required. Phase transitions require typed Adjudicator approval.

## Acceptance boundary

Given a source measurement meaning, classification must retain whether it is
terminal or dynamic, preserve its source identity and semantic role, and never
convert a dynamic measurement into a static terminal collapse. An unsupported
dynamic target must fail closed with the existing capability diagnostics and no
finite artifact or QASM. General POVM/tomography remains explicitly deferred.

## Phase 1 candidate scenarios

1. A static terminal measurement remains terminal and does not create a
   `DynamicMeasurementRegion` or `DynamicControlRegion`.
2. A dynamic measurement retains its dynamic semantic role and source
   provenance; it is not classified as terminal collapse.
3. An unsupported dynamic target reports the existing dynamic capability
   diagnostics and emits no artifact or QASM.
4. POVM/tomography input is rejected or deferred explicitly, without a
   fabricated finite realization.

Phase 1 Red is limited to these offline semantic/rejection assertions. No
target capability selection, numerical method, provider mapping, or
implementation is approved by this design record.

## Phase 1 Red artifact

Added [`test_liss_0471_measurement_family_readiness_red.py`](../../tests/test_liss_0471_measurement_family_readiness_red.py).
The tests define terminal/dynamic lane separation, source provenance,
unsupported dynamic-target diagnostics with empty artifact/QASM, and explicit
POVM/Tomography deferral. They reuse the existing dynamic measurement fixture
and do not change production code, provider behavior, credentials, or network
configuration.

Red evidence: the classifier module
`compiler.staqex.measurement_family_readiness` is intentionally absent, so
the pytest-independent import check confirms the intended Red state. Python
3.14 `py_compile` and `git diff --check` pass; local pytest is unavailable.

Phase 1 exit: **TESTS REVIEWED; READY FOR PHASE 2 GREEN APPROVAL**. Phase 2
Green is not approved.

## Phase 2 Green: Measurement slice

Added [`measurement_family_readiness.py`](../../compiler/staqex/measurement_family_readiness.py).
The classifier consumes canonical Scientific Semantic IR and distinguishes
terminal `Measure` from `DynamicMeasurementRegion`. Static terminal
measurement is classified as `terminal_classical`; dynamic measurement is
rejected with the existing capability diagnostics and no artifact/QASM.
Unknown measurement realizations, including POVM/Tomography, fail closed with
an explicit deferral.

The reviewed Red tests were not changed. Provider SDKs, credentials, network,
QASM emission, and live QPU execution remain out of scope.

Phase 2 verification: static terminal, dynamic rejection, and explicit
deferral direct harness checks pass; Python 3.14 `py_compile` and
`git diff --check` pass. Local pytest is unavailable because pytest is not
installed.

Phase 2 exit: **GREEN REVIEWED; READY FOR PHASE 3 REVIEW APPROVAL**. Phase 3
is not approved.

## Phase 3 refactor and closeout

Extracted dynamic diagnostic selection, terminal-measurement detection, and
decision construction into focused helpers. Assertions and behavior are
unchanged; the Red tests remain unchanged. Provider SDKs, credentials,
network, QASM emission, and live QPU execution remain out of scope.

Verification: static terminal, dynamic rejection, and POVM/Tomography
deferral direct checks pass; Python 3.14 `py_compile` and `git diff --check`
pass. Local pytest is unavailable because pytest is not installed; CI pytest
and human merge review remain required.

Process review: no operating-contract deviation or operational problem found.

Phase 3 exit: **DONE for the bounded Measurement slice**.

Planning record: `AIP-LISS-0471-2026-08-27-001` (L; N/A model metrics).
