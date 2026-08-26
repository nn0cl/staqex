# LISS-0437 explicit Realize boundary Red trace

## Scope

- Phase: Phase 1 Red.
- Source boundary: `Realize(source = U_formal, method, order, steps,
  error_budget)`.
- Required behavior: parser/type acceptance, visible formal-to-realized
  relation, and typed provenance.
- Excluded: finite gate synthesis, provider submission, S02 migration, and
  any implicit target-profile conversion.

## Test artifact

- `tests/test_liss_0437_realize_surface_red.py`
- Phase 2 Green implementation is now present; this file remains the Phase 1
  acceptance history.

## Review result

- Review record:
  `docs/collaboration/reviews/2026-08-15-liss-0437-realize-red-review-01.md`
- Verdict: **READY for Phase 1 Red artifacts**.
- Deterministic result: `RED suite: 2/3 failing as expected`.
- Next gate: separate Phase 2 Green approval for `Realize` implementation.

## Phase 2 Green result

- Parser/type acceptance and explicit named-argument boundary are implemented.
- Formal/realized names, method, order, steps, error budget, and source
  transform are retained in `CompileResult.evolution_provenance`.
- Direct formal `Limit` remains target-rejected; no implicit `Realize` is
  inserted.
- Evidence: `tests/test_liss_0437_realize_surface_red.py` → `GREEN: 3/3`.

## Phase 2 Green review

- The suite now includes unknown-key and mixed direct-Limit cases:
  `GREEN: 5/5`.
- Review record:
  `docs/collaboration/reviews/2026-08-15-liss-0437-realize-green-review-01.md`
- Verdict: **READY for the approved Realize Phase 2 Green scope**.
- Finite gate synthesis, provider submission, and S02 numerical migration
  remain unimplemented.
