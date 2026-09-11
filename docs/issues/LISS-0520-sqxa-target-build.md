# LISS-0520: `.sqxa` serialization and target build

| Field | Value |
|---|---|
| Status | **Phase 3 Refactor complete — final review pending** |
| Phase | phase-3-refactor |
| Type | architecture / artifact contract |
| Priority | P0 |
| Size | L |
| Parent | WP-0131; WP-0119 |
| Depends on | WP-0121, WP-0122, ADR 0217, ADR 0218 |
| Blocks | Runtime target deployment and provider pilot packaging |
| Acceptance authority | Proposed ADR 0219; real-QPU readiness acceptance |
| Implementation permission | **Phase 3 refactor complete; final review pending** |

## Design check

- Scope: define portable and target-resolved `.sqxa` variants, plus
  target-build and Runtime loading contracts.
- Boundaries: compiler emits `.sqxa`; target builder emits targeted `.sqxa`; Runtime
  loads artifacts and invokes provider adapters; SDKs remain outside Kernel.
- Invariants: common identity/provenance survives target build; lowering does
  not alter Scientific Semantic IR; mismatches fail closed; secrets never
  enter artifacts.
- Omitted: live provider calls, SDK installation, credential provisioning,
  signing, registry, and deployment infrastructure.
- Applied lessons: audit every `ExecutionArtifact`/`QpuArtifact` consumer;
  include positive portable/target cases and atomic rejection; run all named
  contract tests.

## Acceptance scenarios

1. A valid finite source produces a stable portable `.sqxa` with common identity and
   provenance.
2. Target build produces a targeted `.sqxa` with target identity, capability
   fingerprint, payload format, and target fingerprint.
3. AWS, Azure, IBM, and Google payloads may differ while common identity and
   execution policy remain equivalent.
4. Target mismatch, expired capability, unsupported operation, or malformed
   manifest produces no deployable targeted `.sqxa`.
5. Runtime loads targeted `.sqxa`, reads non-secret Host config, requests interactive
   approval, and passes credentials only through the provider SDK chain.
6. No artifact contains credentials, SDK binaries, approval prose, or hidden
   provider selection.

## Planned phases

| Phase | Deliverable | Gate |
|---|---|---|
| 0 | ADR, manifest/schema, ownership, naming review | typed Architecture approval |
| 1 Red | offline serialization, target variant, mismatch and secret-leak tests | typed Phase 1 approval |
| 2 Green | minimal writer/reader and one fake target builder | typed Phase 2 approval |
| 3 | cross-provider review, legacy audit, docs sync | typed Phase 3 approval |

## Phase 1 Red artifact

Added `tests/test_liss_0520_sqxa_target_build_red.py`. The intentionally
missing `compiler.staqex.sqxa` module makes the suite Red. The tests define the
single `.sqxa` format, portable/targeted manifest variants, common identity
preservation, target mismatch rejection, and secret-bearing artifact rejection.
No production implementation, SDK call, credential access, or provider
network is included.

## Phase 1 Red review

Review packet: [2026-09-10 LISS-0520 Phase 1 Red review](../collaboration/reviews/2026-09-10-liss-0520-phase1-red-review.md).
The review findings were corrected and re-reviewed: target metadata,
capability expiry, provider non-contact, and isolated direct-runner paths are
covered. Phase 2 remains unauthorized until separate approval.

## Phase 2 Green record

Added `compiler/staqex/sqxa.py` with the minimum provider-neutral `.sqxa`
artifact model, canonical writer/reader, fake target variant builder, and
Runtime preflight. Common source/semantic identity and provenance are retained;
target route, device, capability expiry, payload format, and target fingerprint
are recorded separately. Target mismatch, expired capability, and secret-bearing
artifact cases fail closed before provider construction/access. A pre-existing
test variable typo was corrected from `provider` to `FakeProvider` without
weakening the contract. Targeted pytest passed **6 tests**; AST, diff, and
document lifecycle checks passed. No SDK, credentials, network, or live QPU
call was used.

## Phase 3 Refactor record

Refactored the provider-neutral implementation without changing its public
contract: canonical payload hashing, expected-route validation, and capability
expiry validation now have explicit helpers at the serialization/runtime
boundary. The legacy consumer audit found no `SqxaArtifact` integration that
would require changing `ExecutionArtifact`, `QpuArtifact`, submit orchestration,
or provider adapters. Targeted tests, compilation, diff, and document checks
passed. Provider SDKs, credentials, network access, and live-QPU execution
remain out of scope. Final review is still required.

## First implementation slice after approval

Implement only the provider-neutral package model and a fake target builder.
Do not install SDKs or call AWS/Azure/IBM/Google.
