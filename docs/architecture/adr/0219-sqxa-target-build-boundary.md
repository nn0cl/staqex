# ADR 0219: `.sqxa` target-build boundary

| Field | Value |
|---|---|
| Status | **Accepted** (2026-09-10) — typed Architecture approval received |
| Date | 2026-09-10 |
| Scope | Staqex artifact packaging and provider-runtime handoff |
| Related | ADR 0217, ADR 0218, WP-0121, WP-0122, WP-0131 |

## Context

The compiler output and a provider-ready deployment payload have different
target payloads, but share source identity, semantic identity, provenance, and
execution policy across AWS Braket, Azure Quantum, IBM Quantum, Google QCS,
and direct provider routes.

## Decision proposal

1. `.sqx` means **Staqex source**.
2. `.sqxa` means **Staqex eXecution Artifact**. It is the only serialized
   Staqex execution package, and may be portable or target-resolved.
3. Target build does not change Scientific Semantic IR or source meaning. It
   validates capabilities, lowers to the target format, applies declared
   routing/decomposition, and records target-specific provenance and hashes.
4. A target-resolved `.sqxa` contains a common section plus a target section.
   The common section is preserved from the portable artifact; the target
   section contains target-specific payload and metadata.
5. Provider SDKs, credentials, and approval prose are never stored in `.sqxa`.
   SDKs and credentials belong to the Runtime execution environment and its
   provider adapter.

## Execution model

```text
.sqx -> compiler -> .sqxa -> target build -> targeted .sqxa -> Runtime -> provider
```

The Runtime may accept a portable `.sqxa` and perform target build locally, or
accept a pre-built targeted `.sqxa`. It must reject an artifact whose target
identity or capability fingerprint does not match the Runtime request.

## Consequences

- Portable compilation remains independent of provider SDKs.
- Target-specific validation happens before credentials/network access.
- The Runtime has one execution entry point and one artifact extension.
- `.sqxa` manifest schema and target-build cache policy require a separate
  acceptance specification.

## Non-decisions

This proposal does not select SDK versions, provider devices, deployment
topology, artifact signing technology, or persistent artifact storage.
