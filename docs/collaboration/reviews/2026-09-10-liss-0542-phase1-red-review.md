# LISS-0542 Phase 1 Red review

| Field | Value |
|---|---|
| Date | 2026-09-10 |
| Review isolation | same_context |
| Scope | `.sqxa`-only serialization and target-build Red tests |
| Human request | Phase 1 Red review / approval |
| Result | **Accepted after correction; Phase 2 remains unauthorized** |
| Implementation permission | None; Phase 2 remains unauthorized |

## Reviewed artifacts

- ADR 0219: `.sqxa` target-build boundary
- LISS-0542 and WP-0159
- `tests/test_liss_0542_sqxa_target_build_red.py`
- ADR 0217 capability freshness and ADR 0218 Host approval boundary

## Findings

### F1 — target metadata acceptance is under-specified in tests (P1)

The targeted-variant test asserts `artifact_kind`, route, and common identity,
but not the required device identity, capability fingerprint, payload format,
or target fingerprint. Add assertions for each target manifest field before
Phase 1 Red approval.

### F2 — capability expiry rejection is not represented (P1)

LISS-0542 scenario 4 includes expired capability rejection and ADR 0217 makes
freshness fail-closed. Add an offline Red scenario proving that an expired
target capability cannot produce or load a deployable targeted `.sqxa`.

### F3 — provider non-contact is not observable (P1)

The target-mismatch test checks a loader exception but has no fake provider
port or call counter. Add a Runtime boundary assertion that target mismatch
fails before adapter/provider construction or invocation. This must remain
offline and use a fake port.

### F4 — direct runner uses a shared `/tmp` path (P2)

The direct runner passes a fixed `/tmp` path to tests that write named files.
Use an isolated temporary directory per test when the runner becomes
executable, preventing cross-test contamination and parallel collisions.

## Positive review observations

- The single `.sqxa` extension is consistently represented in the reviewed
  test names and target filename.
- Common source and semantic identity preservation is explicitly asserted.
- Secret-bearing payload rejection is represented without real credentials.
- The test module is standard-library executable and has no SDK/provider
  dependency.
- `py_compile`, `git diff --check`, and document lifecycle checks passed.

## Re-review — 2026-09-10

The Red test packet was corrected and re-read. F1 is closed by assertions for
device, capability fingerprint, payload format, and target fingerprint. F2 is
closed by the expired-capability scenario. F3 is closed by the provider-factory
construction counter and zero-call assertion. F4 is closed by a fresh
`TemporaryDirectory` for every direct-runner test.

`py_compile`, `git diff --check`, and the document lifecycle check pass. The
direct runner remains Red at the intentionally absent `compiler.staqex.sqxa`
production module boundary. No SDK, credentials, provider network, or live
submission was used.

## Disposition

Phase 1 Red is **accepted after correction**. Phase 2 implementation remains
unauthorized and requires a separate typed Phase 2 approval.
