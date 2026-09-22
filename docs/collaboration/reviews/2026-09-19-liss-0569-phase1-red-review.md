# LISS-0569 Phase 1 Red test review

## Review packet

- Scope: WP-0166 / LISS-0569 classical value-body successor Phase 1 Red.
- Approval received: `WP-0166 / LISS-0569 Phase 1 Red テストレビュー承認`,
  2026-09-19.
- Operating path: Architecture Path / Phase 1 Red.
- Implementation permission: not granted by this review.
- Review isolation: `same_context` per runtime routing; weaker than
  `separate_context`.

## Canonical artifacts re-read

- `docs/work-plans/WP-0166-evaluator-classical-value-body-successor.md`
- `docs/issues/LISS-0569-evaluator-classical-value-body-successor.md`
- `docs/specs/staqex-core-module-decomposition.md`
- `docs/architecture/implementation-readiness.md`
- `docs/collaboration/process-lessons-log.md`
- `docs/testing/active-red-tests.toml`
- `tests/test_liss_0569_classical_value_red.py`
- `compiler/staqex/runtime/evaluation/classical.py`
- `compiler/staqex/runtime/evaluation/values.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`
- `compiler/staqex/runtime/evaluator.py`

## Findings and dispositions

1. The Red suite contains five structural assertions that fail against the
   current implementation: missing unit/receiver successor entrypoints,
   legacy delegation in `classical.py` and `values.py`, a missing unit
   callback in the context protocol, and the remaining evaluator legacy body.
   **Disposition: already closed with evidence; these are the accepted Red
   gaps for Phase 2.**
2. Three characterization tests pass for literal evaluation, constructor /
   attribute / unit behavior, and classical binders. **Disposition: already
   closed with evidence; retain unchanged through Green.**
3. The active-Red manifest has one issue-owned entry for LISS-0569 and the
   issue phase matches `phase-1-red`. **Disposition: already closed with
   evidence; keep the entry until Phase 2 Green passes it.**
4. No production source was changed, and the approved allowed-path boundary
   is respected. **Disposition: already closed with evidence.**

## Verification

- Focused command:
  `PYTHONPATH=. ./.venv/bin/pytest -q tests/test_liss_0569_classical_value_red.py`
- Result: **5 failed, 3 passed**.
- The five failures are deterministic and correspond to the intended
  structural extraction gaps. No unexpected fixture or environment failure
  was observed.
- `python3 scripts/check-test-lifecycle.py` -> passed (`entries=1`).
- `python3 scripts/check-document-lifecycle.py` -> passed.
- `python3 scripts/check-coverage-ledger-consistency.py` -> passed.
- `git diff --check` -> passed.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`.
- Environment: macOS host, repository `.venv`, Python 3.14; working tree is
  dirty only with the LISS-0569 Phase 1 Red artifacts.
- Full blocking suite: not run; Phase 1 Red requires the bounded focused
  failure evidence, not full Green evidence.

## Spec-to-change mapping

- Successor-owned dispatch and facade retirement -> structural tests 1–5.
- Existing language/runtime behavior -> characterization tests 6–8.
- Single mutable state owner -> context and source-boundary assertions in the
  structural suite; no extracted module defines state or DTOs.
- No parser, Semantic IR, QASM, provider, network, or public API change ->
  verified by changed-file inspection.

## Review result

Phase 1 Red is **accepted and complete for this bounded scope**. The Red
assertions and characterization fixtures are reviewable and must remain
unchanged during Phase 2 unless a separately recorded contract correction is
approved. The process lesson `red-contract-scope` was applied by separating
structural failures from passing characterization cases and rerunning the
exact bounded suite.

## Next gate

Request:
`WP-0166 / LISS-0569 Phase 2 Green / Implementation 承認`.

This review does not authorize production implementation.

## Evidence links

- Canonical Register: `docs/collaboration/document-register.toml`
- Representative Trace:
  `docs/collaboration/traces/2026-09-19-evaluator-classical-value-body-successor.md`
- Detailed Evidence: `tests/test_liss_0569_classical_value_red.py`
