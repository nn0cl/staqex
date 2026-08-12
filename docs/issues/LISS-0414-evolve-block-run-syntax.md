# LISS-0414: `evolve` Hamiltonian-form requires `{ ... }.run()`

## Metadata

- Local issue ID: LISS-0414
- Status: complete
- Type: Feature Path (surface-syntax parser change only —
  `compiler/staqex/parser.py`; no AST/typecheck/hir/evaluator/QASM
  change, since the produced `EvolveExpr` node is identical to what the
  old bare form produced. Closer to the `fun`→`fn` / `public`→`pub`
  keyword-migration precedent than to ADR 0206-class architecture work,
  per this Issue's own scope decision below — handled as a direct Issue,
  not a standalone ADR)
- Priority: P2
- Planning size: `M` (parser change is small; the bulk of the work is
  migrating ~290 pre-existing call sites across `examples/` and `tests/`)
- Owner / agent: Claude Code
- Parent: Adjudicator language-design critique (this session)
- Branch: `feature/liss-0414-evolve-block-run-syntax`
- GitHub Issue / PR: (opened at Completion)

## Intent

The Adjudicator raised a readability concern about the bare Hamiltonian
form of `evolve`:

> プログラムとして読む人間にとってevolveだけキーワードが書かれてもそれが
> 操作なのか分からないのでは？操作なのか、変数なのか、宣言なのか、分から
> ない。

A reader unfamiliar with Staqex cannot tell, at a glance, whether
`evolve` in `state a = evolve a under H for dur` is an operation, a
variable, or a declaration — there is no bracketing or call syntax
signaling "this is an operation," unlike `apply(H, psi)`. `evolve` is a
real, unambiguous keyword to the parser (no grammar ambiguity), but the
bare, unbracketed clause syntax gives a human reader no visual signal.

The Adjudicator's own proposed fix:

> evolveを知らない人には変数名にも見えるからダメです。evolve()にして。
> もし()内にたくさん書く予定があるなら例えばevolve{}.run()などにする

Given `under`/`for`/`using Suzuki(...)`/`until ... max ...` is enough
content that a bare `()` would read poorly, the Adjudicator selected
`evolve{ ... }.run()` from a set of concrete options presented for this
Issue.

### Physics correction found during this session's discussion

Mid-design, the Adjudicator asked to verify the physics directly:

> 今話題にしているevolveに関わる操作が黒板上でどう書かれるから問題になっ
> ているのかを確認したい。evolveは量子コンピュータ上の操作だと思っている
> ので式には出てこないのではと思っている。

This was correct, and corrects an imprecise justification given earlier
in the same discussion (that `evolve X under H for t` "mirrors how a
physicist reads a blackboard sentence"). The actual physics is
$|\psi(t)\rangle = U(t)|\psi(0)\rangle$ with $U(t)=e^{-iHt/\hbar}$ —
operator-on-ket, structurally identical to `apply(U, psi)`. `evolve`
itself does not appear in the blackboard equation; `under H for t` is
really just *how U is constructed* (Hamiltonian + duration, via
exponentiation) before being applied, not a distinct verb with its own
blackboard spelling.

Two paths were presented given this correction:

1. Keep `evolve` as the verb; only fix the bracketing/operation-
   signaling problem (`evolve{...}.run()`).
2. Decompose `evolve` into an explicit U-construction expression +
   `apply(U, psi)`, removing the `evolve` verb entirely as more
   physically honest.

The Adjudicator chose to finish with option 1 ("1で完了させて") —
keep `evolve` as the verb, fix only the syntax-signaling problem. Option
2 (decomposing `evolve` into explicit U-construction + `apply`) remains
open as a possible *future* Architecture Path topic if ever revisited,
but is explicitly not part of this Issue's scope.

## Scope

Investigation confirmed `evolve` has 4 grammar forms
(`parser.py::_evolve_expr`, `ast_nodes.py::EvolveExpr`):

1. `evolve (seeds) times N { body }` — already block-bracketed.
2. `evolve (seeds) for dt { body }` — already block-bracketed.
3. `evolve psi under H for t [using Suzuki(...)] [until pred [max N]]` —
   bare, no bracketing. The ambiguous, by far most common form.
4. `evolve (psi, phi) under H for t ...` — tuple-seed variant of #3,
   also bare.

Only forms #3/#4 were in scope; #1/#2 already have `{ }` and are
unaffected.

New syntax:

```
evolve { <seed-or-tuple> under H for t [using Suzuki(...)] [until pred [max N]] }.run()
```

### Implementation

`parser.py::_evolve_expr` now dispatches to a new
`_evolve_hamiltonian_block` when it sees a leading `{`, parsing
`{ seeds under H for t [using ...] [until ... [max ...]] }`, then
requiring a literal `.run()` suffix — `.run` is a fixed, required token
sequence parsed explicitly by `_evolve_expr` itself, not a generic
postfix method call, so `evolve{...}` alone (no `.run()`) and
`evolve{...}.somethingElse()` are both rejected with a specific
diagnostic. The bare `under` form (no leading `{`) is rejected with a
new `EVOLVE_REQUIRES_BLOCK_RUN` diagnostic code naming the exact
required replacement — hard cutover, no back-compat alias, matching this
project's own `fun`→`fn`/`public`→`pub` keyword-migration precedent
(`RETIRED_KEYWORD`, `lexer.py`).

Both new `ParseError` raises use a non-default `code=` kwarg
(`EVOLVE_REQUIRES_BLOCK_RUN`) deliberately: `parser.py`'s block-statement
loop silently swallows and retries any `ParseError` whose `.code` is the
default `"PARSE_ERROR"` (treating it as a possible "implicit final
expression" situation), which would otherwise mask this diagnostic
behind a much more confusing generic error.

No new AST node — `_evolve_hamiltonian_block` returns the identical
`EvolveExpr` shape the old bare form produced, so no
typecheck/hir/evaluator/QASM-backend change was needed; this is a pure
surface-syntax change.

The old grammar's dead, unused sub-feature (an optional trailing
`{ body }` after `under...for...[until...max...]`) had zero real usage
anywhere in `examples/`/`tests/` and was dropped — a deliberate,
disclosed decision, not a silent regression.

### Migration

~290 call sites across `examples/` and `tests/` used the old bare form.
Migrated via a scratch Python script (not committed), in two rounds:

- Round 1 corrupted Python `f"""..."""` test files by inserting
  un-escaped `{`/`}`, which Python's own f-string interpolation then
  tried to parse as expressions. Caught by `pytest` collection failures;
  all `.py` changes from round 1 were reverted.
- Round 2 tracked, per line, whether the line was inside an f-prefixed
  triple-quoted string literal and emitted doubled braces (`{{`/`}}`)
  for the migration's own newly-inserted wrapper braces in that case
  only (existing clause text never contains braces, so nothing else
  needed escaping).
- One false-positive match was found and hand-fixed: a plain descriptive
  Python string in `tests/spec_verification/suites/sv17_quantum_mechanics_syntax.py`
  (`"evolve |0> under X for π/2 → |1>"`, a `CaseResult` label, not real
  Staqex source) coincidentally matched the migration pattern and was
  corrupted; reverted to its original text.
- A few docstrings/comments referencing the old syntax as backtick-quoted
  example text were also mechanically (and incorrectly) rewritten mid-
  sentence by the same pattern match; hand-fixed to read correctly with
  the new syntax (`test_explicit_trotter_steps_red.py`,
  `test_liss_0399_continuous_type_hard_gates_red.py`,
  `test_liss_0410_operator_resolver_completion_red.py`).

## New/updated tests

`tests/test_liss_0414_evolve_block_run_syntax_red.py` (7 tests):
bare-seed and tuple-seed-with-Suzuki `{ }.run()` forms parse and run;
`until ... max ...` form parses and runs; the old bare form is rejected
with `EVOLVE_REQUIRES_BLOCK_RUN`; a missing `.run()` suffix is rejected;
the already-bracketed `times N { body }` and `for dt { body }` forms are
unaffected (regression guards).

## Design verification performed

1. Confirmed the new `{ }.run()` forms (bare seed, tuple seed + Suzuki,
   until/max) parse and execute correctly, producing a measurement.
2. Confirmed the old bare form now raises `EVOLVE_REQUIRES_BLOCK_RUN`
   with a message naming the exact required rewrite, not a generic
   `PARSE_ERROR`.
3. Confirmed a missing `.run()` suffix after `evolve{...}` is rejected.
4. Confirmed forms #1/#2 (`times N { body }`, `for dt { body }`) are
   completely unaffected, including a bare `under` form nested *inside*
   a `times N { body }` body (outer dispatch reached correctly; only the
   inner bare form is rejected).
5. Full regression sweep: 1483 passed (up from the pre-Issue 1476
   baseline + 7 new tests). Spec verification: 100.00% (161/161).
6. Full `.sqx` corpus swept with `staqex check`; all migrated files pass.
   Pre-existing failures (negative-test fixtures under
   `tests/spec_verification/fixtures/` designed to trigger forbidden-
   construct errors, a lexer-error migration fixture, and two
   `A11_noether_forge` files that only resolve their relative imports
   when compiled as part of the full linked module, not standalone) were
   confirmed untouched by this Issue's migration and pre-date it.
7. Spot-checked `staqex run` output on rewritten `.sqx` files
   (`B04_evolve_not_loops`, `S01_main_morning_collect`, `A03_h2_vqe`) —
   output unchanged from the pre-migration behavior.

## Exit criteria

- [x] `evolve { <seed> under H for t [using ...] [until ... [max ...]] }.run()`
  parses and runs for bare-seed and tuple-seed forms.
- [x] The old bare `evolve ... under ... for ...` form is rejected with
  a specific, actionable diagnostic (`EVOLVE_REQUIRES_BLOCK_RUN`), not a
  masked generic `PARSE_ERROR`.
- [x] `evolve{...}` without `.run()` is rejected.
- [x] Forms #1/#2 (`times N { body }`, `for dt { body }`) unaffected.
- [x] All ~290 pre-existing call sites across `examples/` and `tests/`
  migrated to the new syntax.
- [x] Full regression sweep passes (1483 passed); spec verification
  100.00% (161/161); full `.sqx` corpus `staqex check` clean.
