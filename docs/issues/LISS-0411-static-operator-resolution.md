# LISS-0411: static Operator resolution for unitarity_check.py + QASM backend

## Metadata

- Local issue ID: LISS-0411
- Status: complete
- Type: Feature Path (bug fix; `compiler/staqex/unitarity_check.py`,
  `compiler/staqex/backend/qasm/lower.py`, new
  `compiler/staqex/static_operator_resolution.py` — closes a gap in ADR
  0206's already-Accepted, already-shipped implementation, not a new
  architecture decision, per CLAUDE.md's Bug Triage)
- Priority: P0 (safety-gate bypass — the static unitarity check silently
  passed a genuinely non-unitary program instead of failing closed)
- Planning size: `M`
- Owner / agent: Claude Code
- Parent: independent-context source code review (this session,
  Adjudicator-requested); Part 2 of the resulting fix plan (Part 1,
  runtime resolver completion, is
  [LISS-0410](LISS-0410-operator-resolver-completion.md))
- Branch: `feature/liss-0411-static-operator-resolution`
- GitHub Issue / PR: (opened at Completion)

## Intent

The code review found the static `apply`/`capply` unitarity check
(`unitarity_check.py`) silently passed `Operator Bad = weights.a * X;
apply(Bad, psi)` with "ok — no hard compile diagnostics" instead of the
correct `NON_UNITARY_TRANSFORM_ERROR` a physically identical bare-literal
form already got — because `op_n_qubits`/`compile_hamiltonian` don't
understand `OpAttr`, and the resulting failure was silently swallowed by
a blanket `except (ValueError, TypeError, KeyError): return`. The QASM/
Trotter backend had the identical gap for the LISS-0407/ADR 0206
regression case (`scale * f(weights)`, which runs fine via `evolve` but
still raised the pre-ADR-0206 vague `cannot compile sparse Pauli for
OpCall` when emitted to QASM).

Both are pure static-AST passes with no live `Evaluator` state — LISS-
0410's runtime fix doesn't reach them. This Issue adds a new shared,
compile-time-only resolution module
(`static_operator_resolution.py`) used by both.

## Scope

1. `static_operator_resolution.py` (new):
   - `collect_static_operator_context(unit)` — walks `unit.main` (and
     library `FunDecl` bodies) collecting `Operator` binds, numeric
     scalar literals (both already done narrowly and separately by both
     existing callers), and — the actual missing piece — **struct-of-
     literals constructions** (`W weights = W(2.0)` / `W { a: 2.0 }`)
     into an `objects` map. Pure constant folding: only folds a struct
     when every field value is itself a numeric literal or a
     previously-folded scalar; anything dynamic (a function call, a
     Host array) is simply not added, matching the scalars-only
     behavior both callers already had.
   - `resolve_static_operator(op_ast, *, unit, operators, objects)` —
     resolves `OpAttr` (reusing `op_attr_elaboration._op_attr_float`,
     the same elaboration logic the live Evaluator uses) and inlines
     nested Operator-returning calls (a from-scratch, purely-static
     mirror of `Evaluator._resolve_op_call`/`_resolve_operator_factory_call`
     — no runtime execution, only AST substitution).
2. `unitarity_check.py`: build `objects` once via
   `collect_static_operator_context`, thread it (and `unit`) through the
   existing `operators`/`scalars` parameter-passing chain
   (`_check_expr_unitarity` and its ~9 call sites — mechanical,
   consistent with the file's existing pattern of threading state
   through recursive calls rather than instance attributes), and call
   `resolve_static_operator` in `_check_apply_unitary`/
   `_check_hamiltonian_hermitian` before `op_n_qubits`/
   `compile_hamiltonian`. The existing
   `except (ValueError, TypeError, KeyError): return` is unchanged and
   still correct for genuinely undecidable cases (this check's own
   docstring: "Full proof of every pushforward remains Deferred") — far
   fewer real programs fall into that bucket now.
3. `backend/qasm/lower.py::_from_ast_patterns`: after building `op_env`,
   resolve every entry against a freshly-collected `objects` map the
   same way, wrapped in the same fail-soft `except` (leaves the entry
   unresolved on failure, letting the downstream Trotter compiler raise
   its own error exactly as before — non-regressive).

## Explicitly out of scope

- Host-array-backed binders in the QASM path — `host("key")` values
  don't exist without a real run, a different, legitimate limitation,
  not a bug.
- `OpBinder` resolution inside a statically-inlined function call's
  return value (e.g. a no-arg factory returning `sum(...) {...}`) —
  left unresolved, falls through to the existing "can't statically
  determine" path exactly as before this Issue (not one of the review's
  three confirmed target cases).

## Design verification performed

1. **A real infinite-recursion bug found and fixed during Green**:
   folding `OpCall` inlining into the static resolver initially reused
   the *caller's* `operators` dict when resolving the callee's return
   expression — for `main_lattice_four.sqx`'s `Operator H = scale *
   damage_hamiltonian_four()`, the callee function's own **local**
   `Operator H = sum(...) {...}` shares the name `H` with the caller's
   outer `Operator H`. Resolving the callee's `return H` against the
   caller's `operators` dict resolved `H` back to the caller's own
   `scale * damage_hamiltonian_four()` expression — infinite recursion
   (`RecursionError`, confirmed via the full regression sweep, not a
   theoretical concern). Fixed by giving `_resolve_static_call` a fresh,
   function-scoped `local_operators` dict built from the callee's own
   `Operator` StateBinds, matching the live Evaluator's own
   `_resolve_operator_factory_call`/`local_ops` lexical-scoping pattern
   (a function never implicitly sees the caller's Operator names).
2. Direct execution: `Operator Bad = weights.a * X; apply(Bad, psi)`
   (`weights.a = 2.0`, genuinely non-unitary) now correctly reports
   `NON_UNITARY_TRANSFORM_ERROR` via `check_unitarity`, matching the
   already-working bare-literal form exactly. A genuinely-unitary
   struct-field Operator (`weights.a = 1.0`) is confirmed *not*
   falsely flagged.
3. Direct execution: `staqex emit-qasm` on ADR 0206's own regression
   case (`scale * f(weights)`) no longer contains `cannot compile sparse
   Pauli for OpCall` in its notes.
4. Full regression sweep: 1468 passed (up from 1464 — 4 new tests, plus
   the recursion bug found+fixed during Green). Spec verification:
   100.00% (161/161). Re-ran `staqex check` on every `.sqx` file under
   `examples/showcase/` and every `main_*.sqx` entry point under
   `examples/applied/` — all still pass cleanly, confirming no new
   false-positive diagnostics on already-shipped examples.

## Exit criteria

- [x] `unitarity_check.py` correctly flags a genuinely non-unitary
  struct-field-coefficient Operator (previously silently passed).
- [x] `unitarity_check.py` does not false-positive a genuinely unitary
  struct-field-coefficient Operator.
- [x] QASM emission no longer fails on ADR 0206's own regression case.
- [x] A real infinite-recursion bug (function-local/caller Operator
  name collision) found during Green is fixed.
- [x] Full regression sweep passes (1468 passed); spec verification
  100.00% (161/161); all showcase/applied `.sqx` entry points confirmed
  unaffected.
