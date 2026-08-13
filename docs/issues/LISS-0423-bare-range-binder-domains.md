# LISS-0423: bare-range binder domains (`i In 0..n-1`), retire `Index<...>`

## Metadata

- Local issue ID: LISS-0423
- Status: complete
- Type: Feature Path (`compiler/staqex/parser.py`, `compiler/staqex/pipeline.py`
  + scripted corpus migration)
- Priority: P1
- Planning size: M (parser grammar change + hard-cutover retirement +
  ~35-file corpus migration, larger than first estimated)
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

$i,j\in\{0,\ldots,n-1\}$ in a blackboard equation is a bare range — no
"Index" type concept appears in the mathematics. `Index<a..b>` /
`Index<N>` is a Staqex-only wrapper with no equation counterpart, unlike
`{0,1}^n` which is already written with no wrapper. Retiring `Index<...>`
as a binder-domain spelling in favor of a bare range makes every
`Sigma`/`Pi`/(future `ForAll`/`Min`) binder a literal transcription of its
domain, and — because the bare-range endpoints already support arithmetic
expressions (`0..n-1`) — closes a real, separate gap: the already-shipped
S02 `objective_hamiltonian` hardcoded `Index<0..7>`, disconnected from
`Int n = 8` used two lines above it in the same file.

## Hard Stop during this Issue (real, unanticipated scope finding)

The batch record's own `approved_scope`/`disallowed_paths_notes` assumed
`Index<...>`'s binder-domain usage was confined to `objective_hamiltonian`'s
three binders (confirmed by an earlier, narrower grep). A full corpus sweep
before Green found **~35 files** (examples and, mostly, tests going back to
the language's earliest binder-related work, e.g. `test_liss0055_execution_
acceptance.py`) use `Index<...>` as a binder domain — this is exactly one of
the batch record's own stated `invalidating_triggers`. Escalated to the
Adjudicator rather than resolved unilaterally; the Adjudicator confirmed
proceeding with the full migration (recommended option), matching WP-0098's
own precedent for large mechanical corpus migrations.

## Scope

1. `parser.py::_binder_domain()`: the `Index<...>` branch (both the
   `Index<a..b>` range form and the `Index<N>` single-arg form, which
   desugared to `TypeRef(name="Index", args=[...])`) is replaced with a
   `ParseError(code="BINDER_DOMAIN_INDEX_RETIRED")` naming the exact
   rewrite. A new fallback tries `_static_index_endpoint()` (already
   supports literals, names, and `+`/`-` arithmetic — confirmed by reading
   the function, not assumed) followed by `..`, producing the same
   `IndexDomain` AST node the old `Index<a..b>` form produced — so every
   downstream consumer (`finite_binder.py::_domain_bounds`, etc.) is
   unaffected by construction. `Index<8> i = ...` **type annotations**
   (`_type_ref`, a different grammar position entirely) are untouched.
2. `pipeline.py::HARD_CODES`: added `BINDER_DOMAIN_INDEX_RETIRED` — without
   this, `CompileResult.ok` was (wrongly) `True` for a program using retired
   `Index<...>` syntax, since `ok` checks diagnostic codes against an
   explicit allowlist, not "any diagnostic present."
3. Scripted corpus migration (`In Index<a..b>` → `In a..b`, `In Index<N>` →
   `In 0..N-1`, `rev(Index<...>)` → `rev(...)`) across ~35 files.

## Real bugs found and fixed during Green

1. **My own retirement `ParseError` was silently swallowed by the parser's
   implicit-final-expression backtracking** (`parser.py`'s `_block()`,
   around the `except ParseError as e:` handler that only re-raises when
   `e.code != "PARSE_ERROR"`). I initially embedded the diagnostic code as
   *text* inside the message string instead of passing `code=` to
   `ParseError(...)`, so it silently fell back to the default
   `"PARSE_ERROR"` code, got caught by this exact recovery path, and
   surfaced as a confusing, unrelated "function result expression must be
   the final item in a block" error instead of my intended message. Found
   by actually running the retirement case end-to-end (not just reading the
   code), matching this project's own established discipline. Fixed by
   passing `code="BINDER_DOMAIN_INDEX_RETIRED"` explicitly, matching the
   existing `EVOLVE_REQUIRES_BLOCK_RUN` precedent.
2. **Migration script false positive**: `test_liss0057_periodic_boundary_
   red.py`'s `_ring_source(domain: str = "0..3", ...)` helper builds
   `Sigma (i In Index<{domain}>)` via an f-string, where `{domain}` is
   *already* a full range string (`"0..3"`, `"0..4"`), not a single number.
   The scripted migration's "no `..` in the static template text → treat as
   single-arg" heuristic incorrectly produced `Sigma (i In 0..{domain}-1)`,
   which would have substituted to the malformed `0..0..3-1` at runtime.
   Caught by reviewing the diff before running tests (not after), fixed by
   hand to `Sigma (i In {domain})`.

## Explicitly out of scope

- Category-B builtin-function renames (unchanged from the batch's original
  scope decision).
- `objective_hamiltonian`'s `Index<0..7>` → `0..7` (spelling only, per the
  migration script); threading `n` through as an explicit parameter so the
  binders read `0..n-1` instead of the still-hardcoded `0..7` was **not**
  attempted — that would change the function's signature, outside this
  Issue's stated scope (spelling retirement, not a refactor).

## Design verification performed

1. Confirmed `_static_index_endpoint()` already supported named-variable
   and `+`/`-` arithmetic endpoints (`ADR 0117`) before this Issue — the
   bare-range grammar addition needed no new endpoint-expression work, only
   removing the `Index<` wrapper requirement.
2. Confirmed the new bare-range parse path produces the *identical*
   `IndexDomain` AST node the old `Index<a..b>` form did, so
   `finite_binder.py`/`hamiltonian.py` needed zero changes.
3. Confirmed `Index<8> i = ...` (type annotation, `_type_ref`) is a
   different grammar position than `_binder_domain` and is unaffected —
   verified via `test_semantic_discrete_carriers_red.py` staying green
   untouched.
4. Confirmed `test_physics_ir_slice_b_red.py`'s `domain="Index<0..N-1>"` is
   an unrelated internal `BinderNode` string field (a different IR
   representation, not parsed Staqex source) and correctly excluded from
   migration.
5. Full regression sweep: 1518 passed (1511 + 7 new). Spec verification:
   100.00% (161/161). Full `.sqx` corpus `staqex check` clean (two
   pre-existing, unrelated `A11_noether_forge` standalone-import artifacts
   untouched, per WP-0098's own completion notes).

## Exit criteria

- [x] `i In 0..n-1` (bare range, including arithmetic/variable endpoints)
  parses and runs identically to the old `Index<0..n-1>` form.
- [x] `Index<a..b>` / `Index<N>` / `rev(Index<...>)` all fail with a clear,
  actionable `BINDER_DOMAIN_INDEX_RETIRED` diagnostic naming the rewrite,
  and correctly make `CompileResult.ok` `False`.
- [x] `Index<N> x = ...` type annotations are unaffected.
- [x] Full corpus migrated (~35 files); full regression sweep passes
  (1518); spec verification 100.00%; full `.sqx` corpus `staqex check`
  clean.
