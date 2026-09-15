# LISS-0559 Phase 1 Red test review

- Issue/WP: LISS-0559 / WP-0161
- Path/phase: Feature Path / Phase 1 Red
- Review isolation: same_context, per `docs/collaboration/runtime-routing.toml`
- Approval received: `LISS-0559 Phase 1 Red テストレビュー承認`, 2026-09-16
- Implementation permission: not granted by this review

## Reviewed contract

The three existing D01 nodes are the bounded acceptance contract for an
immutable S02 assay DTO: one accepted measured IC50 record, preservation of a
censored relation, and identity-collision quarantine without merging records.

## Evidence

- The three nodes were executed unchanged: **3 failed**.
- The common failure is that curated/quarantined `records` are dictionaries,
  not typed records exposing `activity_id`, `relation`, and `compound_id`.
- The collision path already emits `ASSAY_IDENTITY_COLLISION` and retains both
  raw records; the typed result surface is the missing contract.
- No external data, chemistry normalization, model fitting, database, or QPU
  behavior is implied.

## Review result

The Red suite is deterministic, minimal, and aligned with the accepted D01
profile. Phase 2 may introduce one immutable `AssayRecord` DTO and normalize
snapshot/result records to it, preserving raw input, censoring, provenance,
quarantine diagnostics, and collision records. The reviewed tests must remain
unchanged.

## Next gate

Request `LISS-0559 Phase 2 Green / Implementation 承認`.
