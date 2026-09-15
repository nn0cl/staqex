# LISS-0547 Phase 3 Refactor Review

## Review packet

- Scope: Parser family decomposition after Phase 2 Green; no grammar or AST
  behavior change.
- Canonical documents: `docs/specs/staqex-core-module-decomposition.md`,
  `docs/issues/LISS-0547-parser-family-decomposition.md`,
  `docs/architecture/implementation-readiness.md`.
- Files re-read: `compiler/staqex/parser.py`, all files under
  `compiler/staqex/parsing/`, `tests/test_liss_0547_parser_families_red.py`,
  `docs/testing/active-red-tests.toml`, and the LISS-0547 trace.

## Findings and dispositions

1. The seven family entrypoints are explicit and importable. **Already closed
   with evidence:** the structural contract suite passes.
2. `Parser` remains the sole live cursor, diagnostic, and grammar-state owner;
   the extracted modules receive a narrow `ParserContext` protocol and do not
   import the facade. **Already closed with evidence:** dependency-direction
   and shared-context tests pass.
3. Compatibility aliases retain the existing private access paths while the
   family names become available. **Already closed with evidence:** focused
   parser behavior remains unchanged and `py_compile` succeeds.
4. The current implementation uses named legacy delegates rather than moving
   every grammar body out of `parser.py`. **Accepted as bounded disposition:**
   the remaining bodies have intertwined cursor, precedence, recovery, and
   nested-delegation dependencies; a broad move would exceed this refactor
   slice and risk changing token consumption. The next parser slice must move
   one family body with the same exact behavioral matrix.

## Blockers and known out-of-scope result

- No Phase 3 blocker was found.
- One parser-focused QASM provenance test remains a pre-existing failure and
  is outside Parser decomposition scope; it is not attributed to this change.
- Live QPU/provider tests are not applicable.

## Deterministic verification

- LISS-0547 structural suite: 4 passed.
- Parser-focused suite: 34 passed, 1 pre-existing QASM provenance failure.
- `py_compile` for `parser.py` and `parsing/*.py`: passed.
- `git diff --check`: passed.
- Test/document/coverage lifecycle checks: passed.

## Isolation and reviewer empathy

Review isolation: `same_context`, which is weaker than `separate_context`.
The smallest useful review path is visible: a future maintainer can locate a
family entrypoint, follow one shared context, and see why the compatibility
delegate remains. The main readability risk is that the legacy bodies are
still large; this is explicitly recorded as successor scope rather than
hidden behind the new package names.

## Final disposition

Adjudicator approval received: `LISS-0547 Phase 3 最終レビュー 承認`,
2026-09-15. The review is accepted and LISS-0547 may be marked done.
