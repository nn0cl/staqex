# ADR 0208: symbolic array-length function parameters (`Float[n]`/`Bool[n]`)

## Status

**Proposed** (2026-08-13) — drafted by Claude Code from a direct
Adjudicator review of `objective_hamiltonian` (S02 `main_selection.sqx`
step 3) against its own blackboard equation, continuing from LISS-0434
(which symbolized the function's `Sigma` range bounds via `n`, but left
`Float[8]` — the array *type* itself — a literal, disclosed hardcode
since `Float[n]` does not parse today). Not yet approved; no
implementation may start until Accepted and a Local Issue is
plan-approved, per CLAUDE.md's Issue-Level Autonomy rules.

## Design check

- **Scope and expected behavior:** `objective_hamiltonian`'s equation
  uses $\text{activity\_w}\in\mathbb{R}^n$ — the *same* $n$ the function's
  own `Sigma` ranges already use (LISS-0434). Its Kernel signature is
  `activity_w: Float[8]`, a literal disconnected from `n`, because
  `Float[N]…`'s array-length grammar accepts only an integer literal in
  `[…]` — there is no way to write "an array whose length is this
  function's own `n` parameter." This is the last remaining non-literal
  transcription gap in step 3, and the only reason it wasn't fixed in
  LISS-0434 is that fixing it requires new parser/typecheck capability
  (confirmed by direct testing:
  `` `Float[N]…` requires positive integer lengths `` on `Float[n]`),
  not a mechanical substitution like the range fix was.
- **Specifications and files inspected:** `compiler/staqex/parser.py`
  (`_type_ref`'s `Float[N]…`/`Bool[N]…` dims loop, hardcoded to
  `TokenKind.INT`); `compiler/staqex/typecheck.py`
  (`_check_float_array_bind`/`_check_bool_array_bind`, both written for
  top-level `Float[N]… name = …` binds, not function parameter
  declarations at all — a function's own parameter types are checked
  through a separate path this ADR must also touch; `self.semantic_values:
  dict[str, int]`, LISS-0371's existing compile-time-known-scalar tracker,
  already exists and is the natural mechanism for the static cross-check
  below); `compiler/staqex/finite_binder.py`/`runtime/evaluator.py`
  (`_resolve_operator_factory_call`'s `local_arrays`/`local_scalars`,
  LISS-0407/LISS-0434 — arrays and scalars already thread through a
  factory call correctly once bound; this ADR only widens what the
  parameter's own *type annotation* may say, not the binding mechanism
  itself). `docs/issues/LISS-0434-factory-scalar-domain-and-attr-coefficient.md`
  (the immediate predecessor, which fixed the range side of the same
  equation and explicitly disclosed this gap as deferred).
- **Component boundaries, ports/adapters, VO/DTO candidates:** Kernel
  compiler front-end (parser/typecheck) only, plus one new runtime
  fail-closed check at the point a factory call binds its own array
  parameters (`_resolve_operator_factory_call`). No new port — no
  external resource is involved.
- **Applicable constraints:** Physicist-first / source-must-denote-the-
  same-physics-as-the-blackboard (`adjudicator-language-vision.md` §2.2,
  DEC-0003) — the direct motivation. No speculative generality beyond the
  disclosed need (LISS-0432's narrower-than-Float `Bool[N]…` Host-array
  support is the immediate precedent for scoping a generalization to
  exactly what's needed, not a general feature).
- **Decisions, assumptions, unresolved ambiguities:** see Decision below.
  The compile-time-vs-runtime shape-verification question the Adjudicator
  was asked directly is resolved here as "both, layered" (Decision 3) —
  presented for confirmation, not unilaterally assumed.
- **Included and omitted AI context:** Included direct parser/typecheck
  reads confirming the exact failure point and the pre-existing
  `semantic_values` mechanism, not assumed from memory. Omitted:
  multi-dimensional symbolic arrays (`Float[n][m]`) and symbolic widths
  derived from a general expression (`Float[n+1]`) or from a non-parameter
  in-scope value — no disclosed use case needs either; see Decision 1's
  scope boundary.
- **Task routing:** Architecture review for the type-system scope
  decision; deterministic source inspection for all current-state claims;
  no external AI/model call.
- **Verification plan:** a dedicated Local Issue (own Red→Green→Refactor,
  matching LISS-0434's own pattern as a standalone Issue) once this ADR is
  Accepted: parser test (symbolic dim parses, non-parameter-reference
  still rejects cleanly), typecheck tests (both the static-match and
  static-mismatch cases against a compile-time-known caller `n`), a
  runtime test forcing the non-statically-knowable path (mismatched
  runtime array length against a dynamic `n` fails closed with a clear
  diagnostic), and `objective_hamiltonian` itself rewritten to
  `Float[n]`/`Bool[n]` with the full S02 fixture re-verified end to end
  (byte-identical output to the current `Float[8]` version, matching this
  whole line of work's own established byte-identical-output verification
  standard).

## Decision

Propose, if the Adjudicator approves, the following as one coherent
design:

1. **Scope, deliberately narrow:** a function parameter's array type may
   write `Float[n]`/`Bool[n]` (single dimension only — no `Float[n][m]`)
   where `n` names an **earlier `Int`-typed parameter of the same
   function signature** (mirroring the natural order
   `objective_hamiltonian(w, n: Int, activity_w: Float[n], …)` already
   uses). `n` must be a bare parameter reference, not a general
   expression (`Float[n+1]` stays unsupported). Non-parameter positions
   (a plain top-level `Float[n] x = …` where `n` is some other in-scope
   value) are **not** in scope — no disclosed use case needs it, and
   `Int n = 8` itself is already a literal in every case that exists
   today.
2. **Parser:** `_type_ref()`'s `Float[N]…`/`Bool[N]…` dims loop accepts
   either an `INT` literal (unchanged) or a single bare `IDENT` token per
   `[…]` (the symbolic case), recorded the same way the literal case
   already is (`TypeRef(name=<the dim's own spelling>)` — a digit string
   for the literal case, an identifier string for the symbolic case; the
   two are distinguished downstream by `str.isdigit()`, not a new AST
   node).
3. **Typecheck — layered static/runtime verification, not one or the
   other:**
   - **Declaring function's own signature:** the referenced name must
     resolve to an earlier parameter of the same function with declared
     type `Int`; otherwise a new hard diagnostic
     (`SYMBOLIC_ARRAY_LENGTH_UNRESOLVED`) at the parameter's own
     declaration site. Inside the function body, the array parameter's
     own registered shape carries the symbolic name (not a resolved
     integer) — the existing `float_arrays`/`bool_arrays` membership
     checks (e.g. `_check_operator_expr`'s `BINDER_LOWERING_UNSUPPORTED`
     gate) only test membership, not literalness, so `Sigma (i In 0..n-1)
     { activity_w[i] * Z[i] }` type-checks unchanged.
   - **Call site, when statically decidable:** if the argument bound to
     the symbolic parameter (`n`) is a compile-time-known `Int` (already
     tracked via `self.semantic_values`, LISS-0371) **and** the argument
     bound to the array parameter has a literal `Float[N]…`/`Bool[N]…`
     type, cross-check `N` against `n`'s known value at typecheck time;
     mismatch is a new hard diagnostic (`SYMBOLIC_ARRAY_LENGTH_MISMATCH`).
     This covers `main_selection.sqx`'s own call
     (`objective_hamiltonian(weights, n, activity_w, selectivity_w)`,
     where `n`'s value **is** statically known) with a real compile-time
     guarantee, not a deferred one.
   - **Call site, when not statically decidable** (the scalar argument
     is itself a runtime-only value, e.g. passed through from an outer
     function's own non-constant parameter): no static check is
     attempted; a runtime shape check is added at the point
     `_resolve_operator_factory_call` binds `local_arrays` (mirroring
     `HOST_COEFFICIENT_SHAPE_ERROR`'s own existing fail-closed
     precedent for Host-bound arrays) — a length mismatch between the
     bound array and `n`'s actual runtime value raises `KernelError`
     with a clear message, never a silent truncation/pad or an
     out-of-range crash deeper in the Sigma body.
4. **Runtime array representation is unchanged** — arrays stay plain
   Python sequences; nothing about how `local_arrays`/`local_scalars`
   thread through a factory call (LISS-0407/LISS-0434) changes. This ADR
   only widens what the parameter's own declared *type* may say, plus the
   one new runtime fallback check in Decision 3's last bullet.

## Consequences

- `objective_hamiltonian`'s last remaining hardcode (`Float[8]`) becomes
  `Float[n]`, closing the final literalness gap in S02 step 3 relative to
  its own blackboard equation.
- Two new diagnostic codes: `SYMBOLIC_ARRAY_LENGTH_UNRESOLVED` (a
  malformed symbolic reference) and `SYMBOLIC_ARRAY_LENGTH_MISMATCH` (a
  statically-provable shape disagreement at a call site).
- Explicitly out of scope, not silently precluded: multi-dimensional
  symbolic arrays, symbolic widths from a general expression or a
  non-parameter source, and symbolic widths outside function-parameter
  position. Any of these remains a future ADR amendment if a real,
  disclosed need appears — not assumed here.
- One Local Issue is required before this ADR's design is realized. It
  may not start Red until this ADR is Accepted and the Issue itself is
  plan-approved — drafting this ADR authorizes neither.
