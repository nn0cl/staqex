# LISS-0566-D Phase 1 Red Test Review

## Review metadata

- Date: 2026-09-19
- Scope: bounded call-binding/frame contracts for Unit D
- Approval: `WP-0163 / LISS-0566-D Phase 1 Red テストレビュー承認`
- Isolation: `same_context`; weaker than `separate_context`
- Review model: host reviewer; no separate model configured

## Artifacts re-read

- `docs/issues/LISS-0566-D-facade-structure-audit.md`
- `docs/work-plans/WP-0163-evaluator-stateful-successor.md`
- `docs/specs/staqex-core-module-decomposition.md`
- `tests/test_liss_0566_unit_d_red.py`
- `compiler/staqex/runtime/evaluation/calls.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`
- `compiler/staqex/runtime/evaluator.py`
- `docs/testing/active-red-tests.toml`

## Findings and disposition

1. The eight contracts are bounded to call-binding/frame ownership and do not
   authorize unrelated evaluator extraction. **Accepted.**
2. Four structural gaps fail for the intended pre-Green reasons: successor
   entrypoints are incomplete, `_legacy_bind_call` remains on `Evaluator`, the
   calls module still delegates to the legacy body, and compatibility wiring
   still points to the legacy method. **Accepted as intentional Red.**
3. Four characterization/boundary contracts pass: context callbacks,
   no-public-facade dependency, function-call behavior, and method-call
   behavior. **Accepted with evidence.**
4. No assertion weakens unsupported behavior, no provider/QPU dependency is
   introduced, and no active-Red ownership is ambiguous. **Closed with
   evidence.**

No blocker was found. The expected result is **4 failed, 4 passed**. The
Active-Red manifest names `LISS-0566-D` and the current Phase 1 Red review.

## Deterministic verification

- Focused command: `pytest tests/test_liss_0566_unit_d_red.py -q`
- Result: **4 failed, 4 passed**; collection succeeded
- Active-Red lifecycle: passed with one owned entry
- `git diff --check`: passed
- Production source changes: none

## Review result

The Phase 1 Red contract is accepted. Phase 2 may implement only the reviewed
call-binding/frame boundary and must preserve the four passing
characterizations. It must not move `_run_legacy_ast_body` wholesale or add a
second mutable state owner.

Next requested approval:
`WP-0163 / LISS-0566-D Phase 2 Green / Implementation 承認`.
