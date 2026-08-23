# LISS-0448 Phase 1 Red Extension Trace

## Scope and approval

- User approval: `承認`, 2026-08-23, for the Phase 1 Red extension.
- Scope: tests and fixtures only for structured branch meaning and legacy
  fail-closed behavior under ADR 0213.
- Excluded: production implementation, Phase 2 Green, QPU/provider work,
  hidden finiteization, and unitary fallback restoration.

## Red contracts

- `WhenExpr` must retain control source identity and ordered branch rules with
  pattern/else markers and arm source identity.
- Semantic fingerprint must change when branch pattern meaning changes.
- Direct legacy `Coin`/`Mix` lowering must reject atomically and never emit
  `CX` as a compatibility pattern.

## Verification

- Focused command: `.venv/bin/python -m pytest -q
  tests/test_liss_0448_coin_mix_semantic_red.py`.
- Result: **2 failed, 3 passed**; failures are the expected Red state for
  missing production fields and fail-closed legacy behavior.
- No production files were changed for this extension.
- `git diff --check`: passed.

## Gate

- Independent review of this expanded Red contract is required before any
  Phase 2 implementation approval request.
