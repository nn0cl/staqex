# LISS-0548 Phase 2 Green Review

## Review packet

- Scope: internal Scientific Semantic IR family boundaries and stable facade.
- Canonical documents: decomposition spec, Scientific Semantic Core spec,
  consumer migration spec, ADR 0211, and LISS-0548 issue/trace.
- Changed files: `scientific_semantic_ir.py`, the new
  `compiler/staqex/scientific_semantic/` package, the LISS-0548 Red tests,
  lifecycle ledger, and phase documentation.

## Findings and dispositions

1. The facade exports the prior public DTO/function surface and internal
   modules do not import the facade. **Already closed with evidence:** the
   structural suite passes and existing imports collect.
2. Model DTOs are owned by `model.py`; family entrypoints are explicit.
   **Already closed with evidence:** the four LISS-0548 tests pass.
3. The source implementation is currently retained in `legacy.py` and family
   modules forward to it. **Accepted bounded disposition:** this preserves
   behavior and provides an acyclic migration seam; Phase 3 must not claim
   that every body has already moved. Body migration remains successor scope.
4. The original `source_id` keyword contract was initially lost by the facade
   wrapper and was restored before Green evidence. **Applied:** compatibility
   verification now includes the keyword path.

## Blockers and known failures

- No decomposition blocker remains.
- Two existing QASM expectation tests fail with the pre-existing
  `E_QPU_CANONICAL_PROVENANCE` result instead of their expected projection
  diagnostic; they are outside this issue and no workaround was added.
- Live QPU/provider verification is not applicable.

## Deterministic verification

- LISS-0548 structural suite: 4 passed.
- Semantic-core/consumer suite: 50 passed, 2 pre-existing failures.
- `py_compile`: passed.
- `git diff --check`: passed.
- Document and coverage-ledger checks: passed.
- Review isolation: `same_context`, weaker than `separate_context`.

## Next approval

Request: `LISS-0548 Phase 3 Refactor 承認`.
