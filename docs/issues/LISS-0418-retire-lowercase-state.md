# LISS-0418: retire lowercase `state`

## Metadata

- Local issue ID: LISS-0418
- Status: complete
- Type: Feature Path (`compiler/staqex/tokens.py`, `compiler/staqex/parser.py`
  + scripted corpus migration across `examples/`/`tests/`)
- Priority: P1
- Planning size: L (mechanical change; large migration surface, ~276 sites)
- Owner / agent: Claude Code
- Parent: WP-0098 (batch `case-sensitive-keywords-and-sigma-binder`)
- Branch: `batch/case-sensitive-keywords-and-sigma-binder` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

Per this batch's ADR 0191 amendment, `State` (already-shipped, `TYPE_HEADS`,
`compiler/staqex/dimensions.py:300-302`) becomes the sole canonical
declaration spelling. Lowercase `state` is retired, hard cutover — and,
per explicit Adjudicator direction, the freed word becomes an ordinary
available identifier (not blocked by the `RETIRED` dict's blanket
reservation the way `fun`/`public`/`trait`/`observe`/`span`/`when` are).

## Scope

1. `tokens.py`: remove `"state": TokenKind.STATE` from `ACTIVE`. `state`
   now lexes as a plain `TokenKind.IDENT` everywhere.
2. `parser.py::_stmt`: new contextual check (same pattern as the existing
   soft `match`/`reset` keywords) recognizing the *exact* old declaration
   shape — `state <name> =` or `state (<names>) =` — and raising a specific
   `STATE_KEYWORD_RETIRED` diagnostic naming the replacement. Uses a
   non-default `code=` (per the LISS-0414-discovered masking rule:
   `parser.py`'s block-statement recovery loop swallows any `ParseError`
   whose `.code` is the default `"PARSE_ERROR"`). This shape was never
   valid syntax for anything else (two bare identifiers in a row, or an
   identifier immediately followed by `(`, at statement-start position), so
   the check does not shadow legitimate identifier uses of the word
   `state` (`state = 5`, `state.field`, `foo(state)`, `state + 1`, …).
3. Scripted corpus migration (dry-run reviewed, not committed):
   `\bstate\b` → `State`, restricted to the exact old declaration shape at
   statement-initial position (not a blind word-boundary substitution,
   which would also corrupt English prose in comments — "the quantum
   state," "state history," etc. — and any embedded-docstring mentions).

## Explicitly out of scope

- Removing the now-dead `TokenKind.STATE` enum member or the
  now-unreachable `_state_bind`/`_type_ref`'s vestigial
  `tok.kind == TokenKind.STATE` branch — left in place as harmless dead
  code (nothing produces `TokenKind.STATE` anymore) rather than risking a
  wider surgical removal under this batch's already-large scope. Flagged
  here so it isn't mistaken for an oversight; a future cleanup Issue can
  remove it.

## Bugs found and fixed during Green (real, not anticipated in the plan)

Migrating the corpus from `state` to bare `State` (Type-First, no `<T>`)
exercised that surface far more broadly than ever before, exposing four
real, pre-existing gaps — all in code paths that only ever ran with a
`None`/inference-driven type before, never a `declared` type that happened
to be the maximally-generic `Ty("State", "Any", ...)`:

1. `typecheck.py::_check_payload_assign`'s "Any" tolerance allowlist was
   incomplete (missing `Bool` and others) — `State s = dirac(some_bool)`
   raised a spurious `PRODUCT_TYPE_MISMATCH`. Fixed with an unconditional
   `if declared.payload == "Any": return` early exit.
2. The single-name Type-First bind path stored the coarse `declared`
   type (`State<Any>`) in `self.env`, discarding the precise `inferred`
   type — losing information a later use of the name needed (e.g. a
   `Partial`'s own arity, breaking `FUNCTION_ARITY_ERROR`/over-arity
   rejection). Fixed: when `declared.payload == "Any"`, store `inferred`
   instead of `declared`.
3. The *separate* `EvolveExpr`-specific bind path (a structurally distinct
   branch a few lines earlier) had the identical `ty = declared` bug,
   masking a `Continuous`-seed evolve's real inferred kind behind the
   generic declared placeholder and silently skipping the
   `_assert_is_state`/`TYPE_NOT_STATE` gate that depended on `ty.kind`.
   Fixed the same way, plus separately fixed the gate condition itself
   (`hir.py`'s `_stmt_binds_state` and `typecheck.py`'s `_assert_is_state`
   call site) to trigger on "declared via bare `State`" rather than on
   `ty.kind == "State"` post-fix, since `ty` can now legitimately be a
   non-State kind when that's the honest answer.
4. `hir.py::_stmt_binds_state` unconditionally treated any bind with
   `stmt.ty.name == "State"` as a linear root needing NLTS discharge —
   correct for `State<Qubit> x = e` (an explicit, deliberate annotation)
   but wrong for bare `State x = e` (which conveys no more information
   than plain inference), causing spurious `LINEAR_IMPLICIT_DISCARD` on
   non-quantum values (e.g. a `Partial`). Fixed by falling through to the
   same precise `expr_types`-based check the `via_state_keyword` branch
   already used, restricted to the bare (no `<T>`) case.
5. The separate "H1" experimental theory/experiment authoring surface
   (`parser.py`'s line-token-based `H1Prepare`/`H1Evolve`/... recognizer,
   `h1_authoring.py`) has its own, independent keyword detection that
   literally string-matched lowercase `"state"` — unrelated to the main
   language's `TokenKind.STATE`. Silently dropped `State psi = |+>`-style
   H1 prepare statements entirely (not misclassified — omitted) until
   updated to match `"State"`.

## Design verification performed

1. Confirmed `State a = |0>` (capitalized) is unaffected — already shipped,
   zero new code needed for it.
2. Confirmed `state a = |0>` (lowercase) now raises `STATE_KEYWORD_RETIRED`
   with a message naming the exact replacement, not a masked generic
   `PARSE_ERROR`.
3. Confirmed `state` is immediately usable as an ordinary identifier
   (`Int state = 5; Int y = state + 1`) — the retirement diagnostic does
   not shadow this.
4. Corpus migration dry-run reviewed before applying; every touched
   `.sqx`/`.py` file re-verified with `staqex check` / Python syntax check
   after migration, matching LISS-0414's own established discipline.

## Exit criteria

- [x] `State` (capitalized) declarations are unaffected.
- [x] Lowercase `state` raises `STATE_KEYWORD_RETIRED` with an actionable
  message.
- [x] `state` is usable as an ordinary identifier everywhere else.
- [x] Full corpus migrated (~276+ sites, two migration passes — line-
  anchored `.sqx`/`.py` text plus a second pass for single-physical-line
  escaped-`\n` strings and f-string-interpolated forms the first pass
  couldn't reach); full regression sweep passes (1503, up from 1498);
  spec verification 100.00% (161/161); full `.sqx` corpus `staqex check`
  swept clean.
- [x] Five real, pre-existing gaps found and fixed (see above) — all in
  code paths that never ran with a `declared` "Any" State type before this
  migration made that combination common.
