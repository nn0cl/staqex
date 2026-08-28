# LISS-0461: Static OpenQASM conformance

| Field | Value |
|---|---|
| Status | **done — static QASM conformance slice complete** |
| Phase | phase-3-refactor |
| Type | conformance |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | QASM adapter |
| Parent | WP-0119; WP-0122 |
| Depends on | LISS-0456, LISS-0459, LISS-0460 |
| Blocks | LISS-0463, LISS-0465 |
| Branch | `codex/liss-0461-static-qasm-conformance` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0461--static-qasm-conformance) |
| Implementation permission | Phase 3 refactor — bounded static conformance slice only |
| Post-review requirement | Acceptance-spec review and typed Phase 1 approval |

Define the supported static QASM subset and offline conformance fixtures for
Bell, parameterized gates, measurement, QFT/basic decomposition, rejection,
provenance, and resource limits. Validate emitted syntax and target envelope
without connecting to a provider. No provider-specific feature is implied.
## Design detail

**In:** supported static OpenQASM subset, Bell/parameterized/measurement/QFT
fixtures, syntax validation, resource/provenance checks, and negative cases.
**Out:** provider network, provider-specific extensions, dynamic control, and
real-device acceptance.

**Acceptance:** emitted QASM parses and matches the declared subset; source,
semantic, artifact, and measurement identity are recoverable; unsupported
inputs reject before submit; no empty-program success fallback occurs.

**Phase/evidence:** Phase 0 freeze subset; Phase 1 Red offline fixtures; Phase
2 one emitter/conformance slice; Phase 3 full offline corpus and independent
review. Deliverables are subset spec, fixture corpus, parser results, and
rejection matrix. Planning record: `AIP-LISS-0461-2026-08-27-001` (L; N/A
model metrics).

## Phase 1 Red artifact

User approved the Phase 1 Red gate on 2026-08-28. Added offline fixtures under
`tests/fixtures/qasm_static/` for Bell, parameterized terminal measurement,
dynamic-control rejection, and empty-program rejection, plus
`tests/test_liss_0461_static_qasm_conformance_red.py`.

The packet covers declared subset acceptance, parameter/measurement and
source-artifact metadata retention, unsupported dynamic rejection, and no
QASM/artifact/allocation fallback. Red is confirmed by the intentionally
absent `compiler.staqex.qasm_conformance` module. Python 3.14 `py_compile`
and `git diff --check` pass; pytest is unavailable locally. Phase 2 Green
requires Adjudicator test review.

## Phase 2 Green

The Adjudicator approved Phase 2 Green after the Red test review on
2026-08-28. Added the standard-library-only
`compiler/staqex/qasm_conformance.py` validator for the declared static subset.
It preserves QASM and metadata on accepted Bell/parameterized terminal
measurement inputs and rejects dynamic control, empty programs, and unsupported
gates without artifact/allocation fallback. The reviewed tests and fixtures
were not changed.

Verification: the LISS-0461 contract test passes; Python 3.14 `py_compile` and
`git diff --check` pass. Existing QASM pytest tests were not runnable because
pytest is unavailable locally; the SV11 suite was not runnable standalone
because its `harness` import requires the suite runner. Phase 3 refactor and
closeout require separate approval.

## Phase 3 closeout

The Adjudicator approved Phase 3 on 2026-08-28. Shared rejection construction
and static-header validation were extracted without changing reviewed tests or
observable conformance behavior.

Same-context review re-read the acceptance spec, WP-0122, LISS-0461, the
validator, static fixtures, existing QASM emitter/facade, and related tests.
No blocker was found within the bounded static subset. The contract test,
Python 3.14 `py_compile`, and `git diff --check` pass. Existing pytest QASM
tests remain unavailable locally; SV11 requires its suite runner. Review
isolation was `same_context`, weaker than a separate-context review.

Process review: no operating-contract deviation or operational problem found.

Phase 3 exit: **DONE for the bounded static QASM conformance slice**. Dynamic
QASM, provider extensions, credentials, network access, and live-QPU execution
remain separately gated.
