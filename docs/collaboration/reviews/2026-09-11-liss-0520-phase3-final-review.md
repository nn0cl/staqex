# LISS-0520 / WP-0137 Phase 3 Final Review

| Field | Value |
|---|---|
| Date | 2026-09-11 |
| Scope | `.sqxa` serialization, target build, and provider-neutral Runtime preflight |
| Reviewed commit | `a8431814 refactor(sqxa): clarify target artifact boundaries` |
| Isolation | `separate_context` worktree review; stronger than same-context review |
| Approval requested | `LISS-0520 Phase 3 最終レビュー 承認` |

## Canonical artifacts re-read

- `docs/issues/LISS-0520-sqxa-target-build.md`
- `docs/work-plans/WP-0137-artifact-packaging-target-build.md`
- `docs/specs/staqex-real-qpu-readiness-acceptance.md`
- `docs/architecture/adr/0219-sqxa-target-build-boundary.md`
- `compiler/staqex/sqxa.py`
- `tests/test_liss_0520_sqxa_target_build_red.py`
- `docs/collaboration/traces/2026-09-11-liss-0520-sqxa-phase3-refactor.md`
- Commit diff for `a8431814`

## Findings and dispositions

1. Phase 3 helper extraction preserves the public API, serialized payload
   shape, route mismatch behavior, expiry behavior for valid timestamps, and
   provider construction ordering. **Disposition: already closed with
   evidence.**
2. Existing consumer audit is consistent with the repository: the
   `SqxaArtifact` type has no legacy `ExecutionArtifact`/`QpuArtifact`
   consumer requiring migration, and provider SDK/network logic remains
   outside this module. **Disposition: already closed with evidence.**
3. An invalid `capability_expires_at` value could escape as `ValueError`, and a
   naive timestamp could raise `TypeError` when compared with the UTC-aware
   Runtime clock. This violated the fail-closed `SqxaFormatError` boundary for
   malformed target metadata. **Disposition: already closed with evidence.**
   The correction now rejects malformed and timezone-naive expiry values with
   `SqxaFormatError` before provider construction, and two focused tests cover
   both cases. This is a Phase 3 review correction, not a provider or live-QPU
   feature.
4. Provider-specific payload translation, approval interaction, credentials,
   SDK binaries, signing, registry, and live deployment are not implemented
   in this bounded unit. **Disposition: out of scope** under ADR 0219,
   LISS-0520, and WP-0137 exclusions; they remain separately gated work.
5. `LISS-0520` and `WP-0137` are already canonical IDs for the scientific
   Quantum Projection Issue/WP referenced by the active WP-0131 ledger. The
   new `.sqxa` Issue/WP use the same IDs with different scope and are not
   linked into the canonical register. **Disposition: apply/blocker.** Assign
   a unique approved Issue/WP identity or consolidate the two records before
   either unit is marked done; do not overwrite or revive the existing record
   implicitly.

## Blockers

The malformed-expiry correctness finding is fixed and verified, but the
duplicate canonical Issue/WP identity is a documentation/ledger blocker.

## Deterministic verification re-run

- Targeted pytest: `8 passed` after the review correction.
- `python3 -m compileall -q compiler/staqex/sqxa.py`: passed.
- `python3 scripts/check-document-lifecycle.py`: passed.
- `git diff a8431814^ a8431814 --check`: passed.

## Reviewer conclusion

The Phase 3 refactor and malformed-expiry correction are technically sound,
but final acceptance is withheld until the duplicate Issue/WP identity is
resolved. This review does not grant implementation approval for unrelated
provider work.

## Next requested approval

`LISS-0520 Phase 3 最終レビュー 再承認` after canonical ID/ledger resolution
and synchronized status update.
