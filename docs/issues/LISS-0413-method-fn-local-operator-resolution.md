# LISS-0413: class-method-local and library-fn-local Operator resolution

## Metadata

- Local issue ID: LISS-0413
- Status: complete
- Type: Feature Path (bug fix; `compiler/staqex/runtime/evaluator.py`
  only — closes a gap in ADR 0206's already-Accepted, already-shipped
  implementation, not a new architecture decision, per CLAUDE.md's Bug
  Triage)
- Priority: P1
- Planning size: `S`
- Owner / agent: Claude Code
- Parent: independent-context source code review, second pass (this
  session); the two remaining findings deferred from
  [LISS-0412](LISS-0412-second-quantization-struct-field-coefficients.md)
  ("大きいモノから" — do the bigger one first)
- Branch: `feature/liss-0413-method-fn-local-operator-resolution`
- GitHub Issue / PR: (opened at Completion)

## Intent

The second review pass found two more Operator-consuming code paths
with the exact same shape as LISS-0410's original finding:
`Evaluator._bind_method` (`evaluator.py:3717`) and `_bind_user_fun`
(`evaluator.py:4145`) both stored a *local* `Operator` StateBind's raw
AST directly (`self.operators[stmt.names[0]] = stmt.expr`), with no
call to `_resolve_operator_expr` at all — unlike the top-level `main`
bind dispatch (line ~484) and, inside `_bind_user_fun` itself, the
Operator-typed *parameter* binding a few lines above (line ~4094),
which already resolves. A struct-field coefficient in a class method's
or library `fn`'s own local `Operator` bind raised `cannot compile
operator node OpAttr` even though the identical struct read already
worked fine at module (`main`) level.

## Scope

Two one-line changes, both replacing `self.operators[stmt.names[0]] =
stmt.expr` with `self.operators[stmt.names[0]] =
self._resolve_operator_expr(stmt.expr)`:

1. `Evaluator._bind_method` (`evaluator.py:3717`).
2. `Evaluator._bind_user_fun` (`evaluator.py:4145`).

`_resolve_operator_expr` defaults its `objects` parameter to
`self.objects` (module scope) when not given — the same scope the
review confirmed is already legitimately reachable from inside a method
or library `fn` body for ordinary classical field reads, and is now
resolved for Operator coefficients too, for free (no new scope-building
logic needed).

## Explicitly out of scope

- Object-typed *method/fn parameters* used as an `OpAttr` host (e.g. a
  struct passed as a parameter, then read via the parameter name inside
  a local `Operator` bind) — not exercised by the review's confirmed
  repro (which used the already-legitimate module-level `self.objects`
  scope) or by this Issue's tests. `_resolve_operator_factory_call`'s
  richer param-name-rekeyed `attr_objects` pattern (LISS-0297/LISS-0410)
  remains the only path with that capability; extending `_bind_method`/
  `_bind_user_fun` to match is a separate, undemonstrated generalization,
  not attempted here.
- Passing a live `State`/Joint coordinate as a method parameter — a
  separate, pre-existing, unrelated limitation noted during the review
  (`_bind_method`'s param-binding loop has no `bind_pushforward` path
  for Joint coordinates), not this bug class.

## Design verification performed

1. Confirmed both gaps directly before implementing: a struct-field
   coefficient in a class method's local `Operator` bind, and in a
   library `fn`'s local `Operator` bind, both raised `cannot compile
   operator node OpAttr`; the literal-coefficient sibling in the
   identical method/fn shape succeeded, isolating the bug precisely to
   the missing resolution call.
2. Confirmed the fix produces the identical terminal result as the
   equivalent literal-coefficient form (struct field holding `2.0`
   matches a hand-written `2.0` literal exactly) — the coefficient
   genuinely reaches the Operator, not silently dropped or defaulted.
3. Full regression sweep: 1476 passed (up from 1472). Spec verification:
   100.00% (161/161).

## Exit criteria

- [x] A struct-field coefficient in a class method's local `Operator`
  bind resolves and runs.
- [x] A struct-field coefficient in a library `fn`'s local `Operator`
  bind resolves and runs.
- [x] Both match the equivalent literal-coefficient form's result
  exactly.
- [x] The already-working literal-coefficient form inside a class method
  remains unaffected.
- [x] Full regression sweep passes (1476 passed); spec verification
  100.00% (161/161).
