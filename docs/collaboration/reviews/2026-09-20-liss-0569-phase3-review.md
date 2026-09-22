# LISS-0569 Phase 3 Refactor review

## Review packet

- Scope: WP-0166 / LISS-0569 classical value-body successor Phase 3.
- Approval received: `WP-0166 / LISS-0569 Phase 3 Refactor 承認`,
  2026-09-20.
- Implementation permission: granted only for the approved Phase 3 refactor;
  no semantic or public API change was authorized.
- Review isolation: `same_context` per runtime routing; weaker than
  `separate_context`.

## Refactor result

- Replaced dense one-line branches in `evaluation/classical.py` with named
  helpers for variables, binary values, attributes, enum variants, receiver
  fields, `when`, calls, unit conversion, unit arithmetic, and display-unit
  restoration.
- Preserved the explicit context boundary: no evaluator import, no copied
  mutable maps, no replacement DTOs, and no continuous/provider logic.
- Preserved private compatibility aliases and all existing evaluator consumer
  entrypoints.
- `evaluator.py` remains **3,790 lines**; `classical.py` is **425 lines**,
  below the 1,200-line structural guardrail.

## Findings and dispositions

1. The Phase 2 extraction left dense mechanical formatting that increased
   reviewer cognitive load. **Disposition: applied** by named helper
   extraction and standard multi-line control flow.
2. Compatibility aliases remain installed after class definition. **Disposition:
   already closed with evidence**; private-consumer compatibility is retained
   intentionally and remains outside the extracted module's ownership.
3. Runtime state and DTO ownership remain in `Evaluator`. **Disposition:
   already closed with evidence**; the extracted module uses context callbacks
   and runtime-type predicates only.
4. No behavior or assertion change was found in the bounded scope.
   **Disposition: already closed with evidence** after focused, adjacent, and
   full-suite reruns.

## Verification

- Focused/adjacent command: six approved LISS-0569/LISS-0568/LISS-0567/
  LISS-0566/classical/unit suites -> **38 passed**.
- Full blocking command: `PYTHONPATH=. ./.venv/bin/pytest -q` ->
  **2,179 passed in 317.81s**.
- `python3 -m compileall -q compiler/staqex/runtime` -> passed.
- `python3 scripts/check-test-lifecycle.py` -> passed (`entries=0`).
- `python3 scripts/check-document-lifecycle.py` -> passed.
- `python3 scripts/check-coverage-ledger-consistency.py` -> passed.
- `git diff --check` -> passed.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39` plus the dirty
  LISS-0569 implementation/refactor tree.
- Environment: macOS host, repository `.venv`, Python 3.14.

## Spec-to-change mapping and compatibility

- Classical dispatch, unit conversion, attribute/receiver reads, and
  constructor routing remain in the approved successor module.
- `_eval_classical_call` and `_eval_classical_op_binder` remain evaluator
  callbacks as specified.
- `values.py`, evolution, call, operator, frame, and direct Red consumers
  continue to import through their existing paths.
- No parser, typechecker, Semantic IR, QASM, provider, network, credential,
  language, or public API retirement path changed.
- No active-Red exclusions remain.

## Review result

Phase 3 refactor is **accepted**. No blocker remains within the approved
scope. This same-context review is weaker than separate-context review and
does not replace the recorded Adjudicator approval.

Final acceptance:

- `WP-0166 / LISS-0569 Phase 3 最終レビュー 承認` (2026-09-20).
- WP-0166 and LISS-0569 are marked done.
- Process review: no operating-contract deviation or operational problem
  found.

## Next gate

No further gate remains for WP-0166 / LISS-0569. Future evaluator work needs
its own approved scope.

## Evidence links

- Canonical Register: `docs/collaboration/document-register.toml`
- Representative Trace:
  `docs/collaboration/traces/2026-09-19-evaluator-classical-value-body-successor.md`
- Detailed Evidence: `tests/test_liss_0569_classical_value_red.py`
