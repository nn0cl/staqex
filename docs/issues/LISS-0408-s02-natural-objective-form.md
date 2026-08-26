# LISS-0408: S02 objective Hamiltonian — natural physicist form

## Metadata

- Local issue ID: LISS-0408
- Status: complete
- Type: Feature Path (examples/showcase only — no compiler/evaluator
  change; LISS-0407 already shipped what this Issue needs)
- Priority: P2
- Planning size: `S`
- Owner / agent: Claude Code
- Parent: follow-on to [LISS-0407](LISS-0407-operator-resolution-unification.md)
  (Adjudicator-requested S02 review/polish)
- Branch: `feature/liss-0408-s02-natural-objective-form`
- GitHub Issue / PR: (opened at Completion)

## Intent

`main_selection.sqx`'s `objective_hamiltonian` construction was built
with plain scalar/array variables at `main()` level, explicitly because
three compiler gaps (documented in the file's own header comment)
rejected the more natural form — a named `ObjectiveWeights` struct and a
reusable factory function taking both the struct and the per-candidate
Host arrays as parameters. LISS-0407 closed all three gaps. This Issue
rewrites the example to use that natural form for real, removing the
now-stale "disclosed compiler limitations" comment and confirming the
rewrite changes nothing about the program's actual behavior.

## Scope

1. Reintroduce `struct ObjectiveWeights { activity, selectivity,
   diversity: Float }` and a proper `fn objective_hamiltonian(w:
   ObjectiveWeights, activity_w: Float[8], selectivity_w: Float[8]) ->
   Operator` factory, called inline while scaling:
   `Operator H_obj = scale * objective_hamiltonian(weights, activity_w,
   selectivity_w)` — exercising all three combinations LISS-0407 closed
   (array parameter into a `sum` binder inside the function; struct-field
   access inside the function's return; the nested call itself used
   inline inside a further Operator expression at `main` level).
2. Remove the stale "disclosed compiler limitations" header comment;
   replace with a short note pointing at LISS-0407/ADR 0206.
3. Confirm byte-identical behavior before/after (same weights, same
   Hamiltonian, same physics — only the source shape changed).

## Explicitly out of scope

- Any change to the weight values, predicate fixtures, or `host/*.py`
  runner scripts — unrelated to this rewrite.
- Any further compiler change — none needed.

## Design verification performed

1. **Confirmed byte-identical terminal measurement** for `seed=0`
   (`run_selection.py`): `(0, 1, 1, 1, 1, 1, 0, 0)`, matching the
   pre-rewrite flattened form exactly.
2. **Confirmed byte-identical benchmark report** (`benchmark_report.py`,
   `shots=20, base_seed=0`): `feasibility_rate=0.7`,
   `infeasible_shots=6`, `top_k_overlap=0.333...`,
   `mean_objective_score=0.9381428571428572`, `manifest_id` unchanged —
   every quality metric identical to the pre-rewrite form.
3. **A multi-line function signature initially tripped
   `tests/test_missing_return_annotations_red.py`'s
   `test_official_examples_have_no_legacy_untyped_declarations`** — a
   line-based regex checker that only looks at the `fn name(` line
   itself for a `->` return-type marker. `main_selection.sqx` was the
   first example anywhere in `examples/` to split a function signature
   across multiple lines; every other example keeps signatures on one
   line. Reformatted to match that established convention (one line)
   rather than weakening the checker — confirmed via
   `grep -rln '^fn \w\+($'` that no other example does otherwise.
4. Full regression sweep: 1459 passed (unchanged from LISS-0407).
   Spec verification: 100.00% (161/161).

## Exit criteria

- [x] `main_selection.sqx` uses the natural struct + factory-function
  form; stale compiler-limitations comment removed.
- [x] Byte-identical terminal measurement and benchmark report
  confirmed before/after.
- [x] Full regression sweep passes (1459 passed); spec verification
  100.00% (161/161).
