# LISS-0472: Continuous/Open-system QPU readiness boundary

| Field | Value |
|---|---|
| Status | **done — Continuous/Open-system bounded deferral slice complete** |
| Phase | phase-3-refactor |
| Type | semantic contract |
| Priority | P1 |
| Initial size | L |
| Current size | L |
| Owner | semantic/physics realization boundary |
| Parent | WP-0120; LISS-0457 |
| Depends on | LISS-0457 Product/Tensor bounded slice |
| Blocks | future continuous target-realization work |
| Branch | `codex/liss-0472-continuous-open-system-qpu-readiness` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0472--continuousopen-system-qpu-readiness) |
| Implementation permission | Phase 3 refactor — deferral classifier slice only |
| Post-review requirement | Adjudicator approval of Phase 3 review |

## [DESIGN CHECK]

- **Scope and expected behavior:** classify continuous/open-system meaning from
  canonical Scientific Semantic IR; retain continuous domain, density/channel/
  evolution role, explicit discretization status, and provenance; reject or
  defer QPU realization when no authorized finite contract exists.
- **Specifications and files inspected:** continuous discretization contract,
  density/CPTP/Lindblad contract, LISS-0111 CPU lowering, B12 open-system
  fixture, PIR-G-LINDBLAD-001, and the real-QPU acceptance matrix.
- **Boundaries:** semantic classification and fail-closed QPU readiness only.
  No new integrator, error bound, finite encoding, provider mapping, or live
  QPU operation.
- **Decisions and ambiguities:** existing explicit discretization contracts
  remain authoritative; a CPU RK4 or grid lowering is not QPU evidence. The
  authorized numerical method, error tolerance, finite carrier, and target
  capability require a later contract/ADR.
- **Included context:** canonical IR, discretization provenance, density/
  Lindblad semantics, and local open-system fixture. **Omitted:** provider
  SDKs, credentials, network, and unrelated numerical adapters.
- **Verification:** Phase 1 adds offline failing tests only for identity,
  explicit-discretization status, and no-artifact/no-QPU-claim rejection.

## Acceptance boundary

Continuous/open-system source meaning must remain distinguishable from a finite
unitary circuit. A QPU request without an explicit authorized finite
representation must return an explicit deferral or rejection with provenance,
without hidden resolution, integrator, error tolerance, provider mapping,
artifact, or QASM. Existing CPU/Simulator execution does not imply QPU support.

## Phase 1 candidate scenarios

1. The B12 open-system source is classified as continuous/open-system with a
   density/channel/evolution semantic role.
2. An explicit discretization contract is visible in provenance and is not
   silently inferred from target capacity.
3. A QPU request without an authorized finite contract is rejected/deferred
   with `DISCRETIZATION_REQUIRED_ERROR` or the accepted target deferral reason.
4. No finite artifact, QASM, allocation, numerical method, or provider mapping
   is produced for the deferred case.
5. CPU/Simulator evidence is not reported as physical-QPU evidence.

Phase 1 is limited to these offline assertions. Numerical method selection,
error-bound algorithms, finite encoding, provider integration, and live QPU
execution remain out of scope.

## Phase 1 Red artifact

Added [`test_liss_0472_continuous_open_system_qpu_readiness_red.py`](../../tests/test_liss_0472_continuous_open_system_qpu_readiness_red.py).
The tests require canonical continuous/open-system meaning, explicit
finite-discretization status, artifact/QASM/allocation/provider-mapping
absence, and a non-physical CPU/Simulator evidence label. Unknown realization
is required to defer explicitly.

Red evidence: the classifier module
`compiler.staqex.continuous_open_system_readiness` is intentionally absent;
the pytest-independent import check confirms the intended Red state. Python
3.14 `py_compile` and `git diff --check` pass; local pytest is unavailable.

Phase 1 exit: **TESTS REVIEWED; READY FOR PHASE 2 GREEN APPROVAL**. Phase 2
Green is not approved.

## Phase 2 Green: Continuous/Open-system deferral slice

Added [`continuous_open_system_readiness.py`](../../compiler/staqex/continuous_open_system_readiness.py).
The classifier consumes compiler-derived Scientific Semantic IR and existing
mixed-state contracts to identify density/channel/Lindblad meaning. It
explicitly defers QPU realization when no authorized finite discretization is
present, with no inferred discretization, numerical method, error tolerance,
artifact, QASM, allocation, or provider mapping. Evidence is labeled
`cpu_or_simulator` and never claims physical execution.

The reviewed Red tests were not changed. Numerical lowering and Provider/QPU
integration remain out of scope.

Phase 2 verification: B12 classification, explicit deferral, non-physical
evidence, and empty-artifact checks pass; Python 3.14 `py_compile` and
`git diff --check` pass. Local pytest is unavailable because pytest is not
installed.

Phase 2 exit: **GREEN ACCEPTED; READY FOR PHASE 3 REVIEW APPROVAL**. Phase 3
is not approved.

## Phase 3 refactor and closeout

Extracted deferred-decision construction into a focused helper while keeping
canonical IR classification, evidence labels, and all no-artifact fields
unchanged. The Red tests remain unchanged. Numerical methods, error bounds,
finite encoding, Provider mapping, and live QPU execution remain out of scope.

Verification: B12 classification, explicit deferral, non-physical evidence,
and empty-artifact checks pass; Python 3.14 `py_compile` and
`git diff --check` pass. Local pytest is unavailable because pytest is not
installed; CI pytest and human merge review remain required.

Process review: no operating-contract deviation or operational problem found.

Phase 3 exit: **DONE for the bounded Continuous/Open-system deferral slice**.

Planning record: `AIP-LISS-0472-2026-08-27-001` (L; N/A model metrics).
