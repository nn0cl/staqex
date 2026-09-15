# LISS-0454 Phase 1 Red test review

- Issue/WP: LISS-0454 / WP-0117
- Path/phase: Feature Path / Phase 1 Red
- Review isolation: same_context, per `docs/collaboration/runtime-routing.toml`
- Approval received: `LISS-0454 Phase 1 Red テストレビュー承認`, 2026-09-16
- Implementation permission: not granted by this review

## Reviewed contract

The two new tests cover the bounded numerical-closure gaps identified by
ADR-0215: executable preservation of a nonzero finite coefficient near zero,
and rejection of a non-finite coefficient before fused projection.

## Evidence

- The focused suite was executed unchanged: **2 failed**.
- Current `_compose_poly` trims `1e-16` as though it were zero.
- Current `_compose_poly` returns a polynomial containing `inf` instead of
  selecting the safe fallback.
- No existing test assertion or production code was changed in Phase 1.

## Review result

The Red tests are deterministic and directly traceable to the accepted ADR and
Issue acceptance specification. Phase 2 may minimally harden polynomial
composition to preserve finite nonzero coefficients and reject non-finite
results, while retaining the existing supported domain and fallback path. Type
and dimension scope, QPU boundaries, and language syntax remain excluded.

## Next gate

Request `LISS-0454 Phase 2 Green / Implementation 承認`.
