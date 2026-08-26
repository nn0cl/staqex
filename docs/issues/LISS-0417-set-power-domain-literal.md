# LISS-0417: `{0,1}^n` set-power domain literal

## Metadata

- Local issue ID: LISS-0417
- Status: complete
- Type: Feature Path (`compiler/staqex/ast_nodes.py`, `compiler/staqex/parser.py`,
  `compiler/staqex/typecheck.py`)
- Priority: P2
- Planning size: S
- Owner / agent: Claude Code
- Parent: WP-0098 (batch `case-sensitive-keywords-and-sigma-binder`)
- Branch: `batch/case-sensitive-keywords-and-sigma-binder` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

Writing $x\in\{0,1\}^n$ directly, matching how the equation reads (rather
than an abstracted domain type name like `Bits<n>`, per the Adjudicator's
explicit direction during this batch's design review), needs a literal
set-power domain expression. No such syntax existed anywhere in the grammar.

## Scope

1. `ast_nodes.py`: new `SetPowerDomain(labels: list[int], width: Expr,
   span: Span)` node, added to the `Expr` union.
2. `parser.py::_primary`: new production, `{` INT (`,` INT)* `}` `^` power —
   `{0,1}^n` is the target shape; `{0,1,2}^n` (a literal qudit domain) parses
   identically for free, since the label set isn't hardcoded to two members.
   No existing grammar used bare `{` in expression position (confirmed:
   `_primary` had no `LBRACE` branch before this Issue), so this is purely
   additive.
3. `typecheck.py`: new `Ty` kind `"Domain"` (`Ty.__str__` branch added,
   matching the existing pattern for `"Continuous"`); `_infer_inner` types
   `SetPowerDomain` as `Ty("Domain", "BitTuple<{0,1}>", DIMLESS)` (labels
   embedded in the payload string), requiring the width expression be
   dimensionless.

## Explicitly out of scope

- Any evaluator/runtime consumption — reserved ahead of its consumer
  (LISS-0420's `Sigma`/`Pi` binder domain), matching LISS-0416's own
  "reserve ahead of use" pattern. A program that tries to actually *use* a
  `SetPowerDomain` value at runtime today has no defined behavior; this
  Issue only makes it parse and typecheck.
- Arbitrary set-literal domains beyond a literal integer label list (e.g. no
  `{a, b}^n` with named/computed labels) — out of scope; the target use case
  is always a literal computational-basis label set.

## Design verification performed

0. **Bug found and fixed during this Issue's own Green phase**: an initial
   implementation added an unconditional `if self._check(TokenKind.LBRACE):
   ...` branch early in `_primary`, intercepting *every* `{` before the
   pre-existing ADR 0153/Slice F bare-block-vs-anticommutator disambiguation
   (`parser.py:2500-2515`) ever ran — `Operator C = {X, Y}` (an existing,
   shipped anticommutator expression) broke, since `{X, Y}` isn't an integer
   label set and my new branch raised before falling through. Caught by the
   full regression sweep (7 failures in `test_dirac_slice_f_red.py`/
   `test_dirac_slice_g_red.py`/`test_liss0234_dirac_paper_var_sugar_red.py`),
   not anticipated during design. Fixed by removing the early interception
   and instead extending the *existing* disambiguation point itself: after
   parsing the brace items, check for a trailing `^` (all items must be
   integer literals) before falling through to the untouched anticommutator
   path — `{0,1}^n` and `{X, Y}` now correctly disambiguate on the same
   `{` token, at the same parse point, matching how bare-block vs.
   anticommutator already disambiguate today.
1. Confirmed `{0,1}^n` (and `{0,1,2}^n`) parse without `PARSE_ERROR` and
   typecheck without `TYPE_MISMATCH`, via a minimal ADR-0180 inferred bind
   (`d = {0,1}^8`) — the only statement form that accepts an unconstrained-
   type RHS at top level without requiring a runtime-consumed value.
2. Confirmed a non-dimensionless width (e.g. `{0,1}^(1.0.s)`) is rejected
   with `TYPE_MISMATCH`.
3. Confirmed `{` in expression position was previously always a
   `PARSE_ERROR` (no prior grammar used it) — this Issue is purely additive,
   no existing construct's parsing changed.
4. Regression guard: full suite unaffected.

## Exit criteria

- [x] `{0,1}^n` parses to a `SetPowerDomain` node and typechecks as
  `Domain<...>`.
- [x] A non-dimensionless width is rejected with `TYPE_MISMATCH`.
- [x] No existing construct's parsing is affected.
- [x] Full regression sweep passes; spec verification 100.00%.
