# LISS-0523 Phase 2 Green correction evidence

- Date: 2026-09-16
- Path: Feature Path / Phase 2 Green / Implementation correction
- Scope: source-hash observability required by the accepted X01 profile
- Approval: `LISS-0523 Phase 2 Green / Implementation 再承認`
- Implementation permission: granted for this bounded correction only

## Correction

The Phase 3 final review found that the accepted profile required source-hash
evidence, while the implementation exposed only source ID and profile. The
correction therefore:

- adds deterministic source hashes to the fixed offline X01 fixture;
- validates each mapped hash as a lowercase 64-character SHA-256 hex value;
- exposes the value as `GeospatialRecord.source_hash` and
  `MappingEvidence.source_hash`; and
- asserts both public observations in the positive contract test.

No provider SDK, network, routing, tasking, Semantic IR, QPU projection, or
other authority was added. The prior final-review blocker is not silently
rewritten; it is resolved by this bounded correction and requires a fresh
final review.

## Verification

```text
14 passed
compileall: passed
git diff --check: passed
```

## Next gate

`LISS-0523 Phase 3 最終レビュー 再承認`
