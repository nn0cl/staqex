# WP-0159: Artifact packaging and target build

| Field | Value |
|---|---|
| Status | **done — Phase 3 final review complete** |
| Type | architecture / feature contract |
| Size | L |
| Parent | WP-0119 |
| Issue | LISS-0542 |
| Depends on | WP-0121, WP-0122, WP-0123, ADR 0217, ADR 0218 |
| Blocks | Runtime provider deployment and real-QPU pilot packaging |
| Implementation permission | **Phase 3 final review approved; bounded unit complete** |

## Goal

Define and implement, after separate approval, the distinction between the
portable and target-resolved `.sqxa` packages. Runtime loads the artifact,
combines it with non-secret Host configuration, and invokes the selected
provider adapter without putting credentials or SDKs in the artifact.

## Ownership

```text
Compiler       -> portable .sqxa artifact
Target builder -> targeted .sqxa artifact
Runtime        -> load, validate, approve, execute
Adapter        -> provider SDK/API translation
```

Target build is lowering and validation, not a second semantic compiler.
Common source/semantic identity, execution policy, and provenance survive it.

## Work units

1. Accept ADR 0219 and the `.sqxa` manifest schema.
2. Add offline readers/writers with canonical bytes and fingerprints.
3. Add a fake target builder and target mismatch/expiry rejection.
4. Audit `ExecutionArtifact`, `QpuArtifact`, submit integration, CLI, and
   adapters for legacy in-memory-only assumptions.
5. Add Runtime loading tests proving config/credential separation and
   interactive approval ordering.
6. Update AWS/Azure/IBM/Google route WPs to consume targeted `.sqxa`; keep live runs
   separately gated under WP-0126.

## Exclusions

No SDK installation, credentials, provider network, real deployment, registry,
signing, or Rust runtime implementation.

## Gate sequence

Phase 0 design and ADR approval -> Phase 1 Red -> Phase 1 review -> Phase 2
Green -> Phase 2 review -> Phase 3 cross-provider review. Each phase requires
its own typed approval.

## Phase 2 Green record

Implemented the minimum provider-neutral `compiler/staqex/sqxa.py` package:
canonical portable/targeted writer and reader, fake target variant builder,
and Runtime preflight that validates target route and capability expiry before
provider construction. Secret-bearing manifests/payloads are rejected. The
targeted suite passes **6 tests**; no SDK, credential, network, or live-QPU
operation was used.

## Phase 3 Refactor record

Separated canonical payload hashing, route matching, and capability-expiry
validation into named internal helpers. This preserves the Phase 2 API and
fail-closed behavior while making the portable/targeted artifact boundary
reviewable. The repository audit found no legacy consumer requiring migration
in this issue. The six targeted tests, compilation, diff, and document checks
pass; provider SDK/network and real-device execution remain excluded. Final
review is complete. The independent review also required malformed and
timezone-naive capability expiry values to fail closed as `SqxaFormatError`;
the correction and two focused tests are included. This unit is canonically
tracked as WP-0159, leaving the existing scientific Quantum Projection
WP-0137 unchanged. Process review: no operating-contract deviation or
operational problem found.
