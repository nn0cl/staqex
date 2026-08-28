# LISS-0462: Dynamic QASM conformance

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor complete** |
| Phase | phase-3-refactor |
| Type | conformance |
| Priority | P1 |
| Initial size | L |
| Current size | L |
| Owner | dynamic QPU adapter |
| Parent | WP-0119; WP-0122 |
| Depends on | LISS-0456, LISS-0459, LISS-0460 |
| Blocks | LISS-0463, LISS-0465 |
| Branch | `codex/liss-0462-dynamic-qasm-conformance` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0462--dynamic-qasm-conformance) |
| Implementation permission | None |
| Post-review requirement | Acceptance-spec review and typed Phase 1 approval |

Define offline fixtures for dynamic measurement, feed-forward, reset, reuse,
branch outcomes, trace/provenance, and devices lacking dynamic support.
Confirm that unsupported dynamic behavior rejects before submission and that
QASM3 classical bits do not become hidden language-level collapse semantics.
## Design detail

**In:** QASM3 bits/conditions/reset, dynamic measurement, feed-forward, reuse,
branch outcomes, trace/provenance, and no-dynamic-capability rejection. **Out:**
implicit language measurement, provider network, and device-support claims
based only on QASM emission.

**Acceptance:** dynamic source meaning maps to explicit control and outcome
metadata; reset/reuse wires are accounted for; static-only targets reject;
unsupported branches never silently drop wires or fall back to static output.

**Phase/evidence:** Phase 0 capability/spec; Phase 1 Red offline fixtures;
Phase 2 bounded emitter/consumer slice; Phase 3 fake/simulator regression and
review. Deliverables are dynamic subset spec, fixtures, and rejection matrix.
Planning record: `AIP-LISS-0462-2026-08-27-001` (L; N/A model metrics).

## Phase 1 Red artifact

- Added `tests/test_liss_0462_dynamic_qasm_conformance_red.py`.
- Added offline fixtures under `tests/fixtures/qasm_dynamic/` for dynamic
  measurement/feed-forward/reset/reuse, branch outcomes, static-only target
  rejection, unsupported branch rejection, and missing reuse metadata.
- The intentionally absent `compiler.staqex.dynamic_qasm_conformance` module
  confirms Red before production implementation. The contract requires
  explicit control metadata, wire mapping, branch outcomes, reset/reuse
  evidence, metadata retention, and atomic rejection with no static fallback,
  artifact, allocation, or physical-execution claim.
- Phase 2 Green, provider integration, credentials, network access, and live
  QPU execution remain unapproved.

## Phase 2 Green artifact

- Added `compiler/staqex/dynamic_qasm_conformance.py` with the bounded
  standard-library validator and explicit result contract.
- Accepted inputs retain QASM and metadata while exposing measurement mode,
  outcome dependencies, wire mapping, branch outcomes, and reset/reuse wires.
- Static-only targets and unsupported branches reject atomically without QASM,
  artifact, allocation, or physical-execution claims.
- LISS-0462 contract tests and the existing dynamic QPU integration test pass;
  Python 3.14 `py_compile` and `git diff --check` pass. Phase 3 review remains
  separately gated.

## Phase 3 closeout

- Extracted diagnostic de-duplication and target-capability diagnostics into
  focused helpers without changing the reviewed contract.
- LISS-0462 contract tests, existing dynamic emission/integration tests,
  Python 3.14 `py_compile`, and `git diff --check` pass. Pytest remains
  unavailable locally.
- Same-context review found no blocker; this isolation is weaker than
  separate-context review, and the Adjudicator gate remains authoritative.
- Process review: no operating-contract deviation or operational problem
  found.
- Provider dependencies, credentials, network access, live submission, and
  physical QPU execution remain separately gated.
