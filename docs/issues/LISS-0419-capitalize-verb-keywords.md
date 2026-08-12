# LISS-0419: capitalize ten verb keywords

## Metadata

- Local issue ID: LISS-0419
- Status: complete
- Type: Feature Path (`compiler/staqex/tokens.py`, `compiler/staqex/parser.py`,
  `compiler/staqex/stdlib/prelude.py` + scripted corpus migration across
  `examples/`/`tests/`)
- Priority: P1
- Planning size: L (mechanical; large migration surface, ~2400+ sites)
- Owner / agent: Claude Code
- Parent: WP-0098 (batch `case-sensitive-keywords-and-sigma-binder`)
- Branch: `batch/case-sensitive-keywords-and-sigma-binder` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

Per this batch's ADR 0191 amendment: capitalize the remaining ten
blackboard-verb keywords — `evolve`→`Evolve`, `measure`→`Measure`,
`mix`→`Mix`, `coin`→`Coin`, `dirac`→`Dirac`, `inspect`→`Inspect`,
`vacuum`→`Vacuum`, `snapshot`→`Snapshot`, `superpose`→`Superpose`,
`forEach`→`ForEach`. Hard cutover via the existing `RETIRED` dict
mechanism (`tokens.py`), matching the `fun`→`fn`/`public`→`pub` precedent
— unlike LISS-0418's `state`, these ten stay reserved (not freed as
ordinary identifiers) once retired.

## Scope

1. `tokens.py`: move the ten lowercase spellings into `RETIRED` (pointing
   at their capitalized replacement); register the ten capitalized
   spellings in `ACTIVE`, mapped to the *same* `TokenKind` values the
   lowercase forms used — no parser grammar change needed for the keyword
   dispatch itself, since it dispatches on `TokenKind`, not lexeme.
2. `parser.py`: new `_expect_effect_name()` accessor for the `effects {
   ... }` clause — effect labels are a closed vocabulary that now
   includes several of these keyword spellings (`Inspect`, `Measure`, …),
   and `_expect_ident_like()` alone rejects any keyword token.
3. `parser.py`: the separate "H1" experimental theory/experiment
   authoring surface (line-token-based `H1Prepare`/`H1Evolve`/`H1Mixture`/
   `H1Superposition`/`H1Measure` recognizer, `_looks_like_h1_scope`) has
   its own independent lowercase keyword detection — updated to match
   the new capitalized spellings.
4. `stdlib/prelude.py`: `PRELUDE_PREP`/`PRELUDE_DEBUG` name sets updated
   to the capitalized spellings.
5. `runtime/evaluator.py`, `typecheck.py`, `hir.py`, `qpu_ir.py`,
   `pipeline.py`, `cli.py`: several scattered lowercase-literal keyword
   checks outside the main lexer table (bind-position `op ==` dispatch,
   `LINEAR_CONSUME_KINDS`, provenance labels, a REPL auto-`measure`
   helper) updated for consistency.
6. Scripted corpus migration (word-boundary, `(?<!\.)` dot-exclusion for
   Python attribute access, `//`/`#` comment-line exclusion, plus a
   second pass for single-physical-line escaped-`\n` strings) across
   `examples/`/`tests/`.

## Bugs found and fixed during Green (real, not anticipated in the plan)

The corpus-wide migration script exercised far more of the codebase than
a hand-audit would have, surfacing several genuine false-positive classes
and one real pre-existing collision:

1. **Python attribute access** (`result.measure`, `envelope.vacuum`) —
   an early, unqualified word-boundary substitution incorrectly
   capitalized `.measure`→`.Measure` etc. across ~285 sites before this
   was caught and the whole migration reverted and redone with a
   `(?<!\.)` negative lookbehind.
2. **Python keyword arguments and dataclass fields**
   (`MeasurementEnvelope(vacuum=True)`, `ShotOutcome.vacuum: bool`) — the
   dot-lookbehind doesn't protect `name=value`/`field: type` positions;
   found and reverted by hand after test failures (`TypeError:
   unexpected keyword argument 'Vacuum'`).
3. **OpenQASM3 *output* text** (`"c[0] = measure q[0];"`) — OpenQASM3's
   own `measure` keyword is a *target-language* convention, completely
   independent of Staqex's source spelling; several test assertions
   checking generated QASM text were incorrectly capitalized and
   reverted (`test_qasm3_codegen.py`, `test_openqasm_ch0_integrated_red.py`,
   `test_liss_0391`/`test_liss_0393`, `test_parametric_circuit_runtime_red.py`,
   `test_quantum_observatory_capstone.py`, `sv10`/`sv11` spec suites).
4. **Internal DAG/IR node-kind labels** (`dag.summary()["kinds"]` →
   `"coin"`, `"measure"`; `hir.py`'s `LINEAR_CONSUME_KINDS`; internal
   runtime log-line prefixes like `f"snapshot:{sink}:{marg}"`) — these
   are implementation-internal category labels, not re-derived from
   parsed source text; test assertions checking them were reverted where
   wrong (kept capitalized only where a genuinely-updated internal
   constant, like `LINEAR_CONSUME_KINDS`, was the intentional fix).
5. **Pre-existing use of a capitalized word as an ordinary identifier**
   — a real, unavoidable consequence of retiring lowercase `coin`: code
   that already wrote `Operator Coin = (X + Z) * inv_sqrt2` (legal
   before, since only lowercase `coin` was reserved) now collides with
   the new `Coin` keyword. Found via `PARSE_ERROR` in
   `test_prelude_pi.py`, `walk_operators.sqx`, `graph_walk.sqx`,
   `test_liss0107_examples_linker_runtime_red.py`, and
   `sv20_dtqw_apply.py` — all five renamed the variable to `CoinOp`.
6. **Coincidental English-prose collision with a test's substring check**
   — `main_disaster_response.sqx` had a pre-existing comment
   ("Evolve times from domain pressures…") that coincidentally matched a
   test's `assert "Evolve times" not in text` check (verifying the spine
   contains no trivial identity `Evolve times N { }` loop). Reworded the
   comment rather than weakening the test.
7. **`prelude.py`'s own `PRELUDE_PREP`/`PRELUDE_DEBUG` registries** were
   still lowercase, causing `SV-08/sv08-prelude` to fail
   (`Coin missing from prelude`) — a genuine compiler-source gap, not a
   test-migration artifact.

## Explicitly out of scope

- `parser.py:2390`'s `.inspect(...)` postfix-method-call check (a
  different, lowercase, method-style naming convention, distinct from
  primary-position keyword usage) — left unchanged; not exercised by any
  failing test, and postfix `.method()` names are a separate convention
  from primary keywords (matching `evolve{...}.run()`'s own lowercase
  `.run()`).
- Cosmetic case-ID slugs in `tests/spec_verification/suites/*.py`
  (e.g. `"sv13-Evolve-parse"`) — capitalized by the corpus migration,
  left as-is; these are report labels, not re-checked against any
  expected value, and read fine either way.

## Design verification performed

1. Confirmed all ten keywords retire correctly (`RETIRED_KEYWORD`
   diagnostic naming the capitalized replacement) and the capitalized
   forms parse to the identical `TokenKind`/AST shape as before.
2. Confirmed `effects { Inspect, Measure }`-style effect rows parse.
3. Confirmed the H1 experimental authoring surface's own statement
   recognition (`H1Prepare`/`H1Evolve`/`H1Mixture`/...) still dispatches
   correctly on the new capitalized spellings.
4. Full regression sweep: 1503 passed (unchanged count from LISS-0418 —
   this Issue is a pure spelling migration, no new tests needed beyond
   what LISS-0415–0418 already added). Spec verification: 100.00%
   (161/161). Full `.sqx` corpus `staqex check` swept clean.

## Exit criteria

- [x] All ten keywords retired (hard cutover, `RETIRED_KEYWORD`
  diagnostic); capitalized forms are the sole valid spelling.
- [x] `effects { ... }` clauses accept the closed-vocabulary keyword
  spellings as effect labels.
- [x] The separate H1 authoring surface's own keyword detection updated.
- [x] Full corpus migrated (~2400+ sites); every false-positive class
  found during Green (Python attribute access, kwargs/dataclass fields,
  QASM output text, internal IR labels, a real pre-existing identifier
  collision, one prose collision) identified and corrected.
- [x] Full regression sweep passes (1503); spec verification 100.00%;
  full `.sqx` corpus `staqex check` swept clean.
