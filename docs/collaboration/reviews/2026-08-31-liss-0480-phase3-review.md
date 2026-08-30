# Review Summary: LISS-0480 Phase 3

## Scope and approval

- Issue: [LISS-0480](../../issues/LISS-0480-scientific-lexicon-contract.md)
- Work plan: [WP-0092](../../work-plans/WP-0092-quantum-mental-model-follow-up.md)
- Approved phase: Phase 3 Refactor
- Isolation: `same_context` because `runtime-routing.toml` is absent; this is
  weaker than a separate-context review and does not replace Adjudicator
  approval.

## Re-read artifacts

- `docs/specs/staqex-v1-quantum-mental-model-follow-up.md`
- `docs/issues/LISS-0480-scientific-lexicon-contract.md`
- `compiler/staqex/lexer.py`
- `tests/test_liss_0480_scientific_lexicon_contract_red.py`
- `tests/test_unicode_math_source_red.py`
- `tests/test_ascii_quantum_notation_red.py`
- `docs/collaboration/definition-of-done.md`

## Findings and dispositions

1. **Resolved by Adjudicator decision — accepted-spec conflict.** LISS-0480 accepts `ψ`/`φ`/`ρ` as
   display aliases, while the existing ASCII-only regression contract rejects
   those same spellings. Full pytest therefore reports a failure in
   `test_unicode_quantum_punctuation_is_rejected_as_source`. **Disposition:**
   Unicode scientific names are now formally adopted and the regression test
   is narrowed to keep punctuation/operators ASCII-only.
2. **Resolved — responsibility boundary.** `_diagnose_scientific_declaration_collisions`
   performs scope-sensitive declaration analysis in the lexer. It currently
   has no real scope tracking and can emit `LEXICON_COLLISION` for valid
   repeated names in parser-defined nested scopes. **Disposition:** removed the
   lexer check and moved collision validation to parsed block scope; same-name
   rebinding remains valid.
3. **Already closed with evidence — provenance.** The alias tokens retain both
   canonical and written spelling metadata, and the targeted tests verify both
   fields.

## Verification

- LISS-0480 plus Unicode punctuation suites: `13 passed`.
- Full repository pytest: not green; the first eight reported failures include
  the accepted-spec conflict above and pre-existing Red suites. It was not
  treated as a completion gate.
- `git diff --check`: passed before the review commit.

## Blockers

Both review blockers are resolved. LISS-0480 may be marked done after the
status and work-plan synchronization commit.

## Next requested approval

No further approval is requested for LISS-0480. Future lexicon families need
their own specification and typed phase approvals.
