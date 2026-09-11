# AI work trace: LISS-0520 Phase 3 Refactor

| Field | Value |
|---|---|
| Date | 2026-09-11 |
| Scope | LISS-0520 / WP-0137 `.sqxa` artifact packaging and target build |
| Phase | Phase 3 Refactor |
| Approval | `LISS-0520 Phase 3 承認` |
| Outcome | Final review blocked by duplicate canonical ID |

## Intent

Improve readability and make the portable-artifact, target-selection, and
Runtime preflight boundaries explicit without changing the Phase 2 contract.

## Changes

- Extracted canonical payload hashing into one helper used by writer and reader.
- Extracted expected-route validation from the file loader entry point.
- Extracted capability-expiry validation from Runtime preparation.
- Audited existing `ExecutionArtifact`, `QpuArtifact`, submit, CLI, and adapter
  references; no legacy consumer of `SqxaArtifact` exists to migrate.
- Final review correction rejects malformed and timezone-naive capability
  expiry values with `SqxaFormatError` before provider construction.

## Verification

- `UV_CACHE_DIR=/private/tmp/qpex-uv-cache uv run --with pytest python3 -m pytest -q tests/test_liss_0520_sqxa_target_build_red.py`
- Result: 8 passed after final-review correction.
- `python3 -m compileall -q compiler/staqex/sqxa.py`
- `git diff --check`

No SDK, credentials, network call, or live QPU was used.

Final review found a duplicate canonical `LISS-0520`/`WP-0137` identity with
the existing scientific Quantum Projection records. Process review is
deferred until the canonical identity and status ledger are resolved.
