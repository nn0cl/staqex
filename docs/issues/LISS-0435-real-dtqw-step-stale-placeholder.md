# LISS-0435: B09/A02's `Evolve...times N {...}` step functions were stale identity placeholders

## Metadata

- Local issue ID: LISS-0435
- Status: complete
- Type: Fast Path (corpus-only; no compiler change — the disclosed gap the
  placeholders cited no longer reproduces)
- Priority: P2
- Owner / agent: Claude Code
- Parent: none — found during a direct Adjudicator-driven critical review of
  `Evolve`'s design (does its `times N { block }` form let users write
  their equation literally, or does it force opaque function-call
  workarounds around real compiler gaps?)
- Branch/PR: (see completion note)

## Intent

Auditing every use of `Evolve (vars) times N { block }` in the corpus
(only 3: B06, B09, A02) to check whether the block content is a literal,
inspectable expression or an opaque escape hatch, found that B09's
`step_quantum_walk` and A02's `step_graph_hop` were both **identity
placeholders**, each carrying the same disclosed comment: "intermediate
`apply`/`walk_shift` binds before `return c *|* x` currently trip
`LINEAR_IMPLICIT_DISCARD` (consume-on-return gap). Real coin+shift is
unrolled in main until that language follow-up." The real DTQW coin+shift
step was never actually implemented inside the reusable function these
files exist to demonstrate — it was worked around by unrolling it directly
in `main()` instead, with the module function reduced to `return c *|* x`
(a no-op).

## Finding

Directly tested writing the real step inside the function:

```staqex
pub fn step_quantum_walk(operator: Operator, c: State<Qubit>, x: State<Position>) -> State<(Qubit, Position)> {
    State c2 = apply(operator, c)
    State x2 = walk_shift(c2, x)
    return c2 *|* x2
}
```

This compiles and runs cleanly, with **no** `LINEAR_IMPLICIT_DISCARD` — the
disclosed "consume-on-return gap" does not reproduce today. The gap was
evidently closed by unrelated linear-use work elsewhere in the project's
history (this repository has many `hir.py`/linear-use Issues in its
timeline); the corpus comment and the identity-placeholder workaround were
simply never revisited afterward. Verified for both files independently
(B09's `step_quantum_walk`, A02's `step_graph_hop`), each producing a
well-formed, non-Vacuum terminal measurement when run end to end.

## Scope

1. `examples/basics/B09_multi_file_modules/operators/walk_operators.sqx`:
   `step_quantum_walk` now performs the real coin+shift
   (`apply(operator, c)` then `walk_shift(c2, x)` then `return c2 *|*
   x2`), not `return c *|* x`. Stale comment removed.
2. `examples/applied/A02_robot_graph_planner/operators/graph_walk.sqx`:
   the identical fix for `step_graph_hop`.
3. No compiler change — this Issue is corpus-only, since the underlying
   capability already existed.

## Why this matters for `Evolve`'s own design

This was found while directly investigating whether `Evolve (vars) times N
{ block }` forces opaque, unverifiable function calls as a workaround for
real expressiveness gaps (the Adjudicator's own critique:
`unitarity_check.py`'s own docstring admits "Full proof of every
pushforward remains Deferred" — only known non-unitary *patterns* are
caught, not a general proof). For 2 of this corpus's only 3 uses of the
`times N` form, the "opaque function call" was never actually necessary —
the real, literal DTQW step was expressible all along; the placeholder
was stale documentation debt, not a live language limitation. This
narrows (but does not close) the broader question of whether `Evolve`
should be redesigned to *require* its block content to be built only from
literal arithmetic and an already-unitarity-verified closed vocabulary
(`apply`/`capply`/`controlled`/`walk_shift`/etc.) rather than arbitrary
function calls — that broader design question remains open and separate
from this Issue.

## Design verification performed

1. Both rewritten functions compile and run end to end, each producing a
   well-formed, non-Vacuum terminal measurement (verified independently,
   not just "doesn't crash").
2. `tests/test_applied_catalog_health_red.py`,
   `tests/test_liss0107_examples_linker_runtime_red.py` (the existing
   regression coverage for these exact files) both still pass — neither
   asserts a specific numeric output tied to the old identity behavior,
   only that the examples compile and produce a terminal measurement.
3. Full regression sweep: 1541 passed (unchanged count — no tests added
   or removed, only two `.sqx` corpus files edited). Spec verification:
   100.00% (161/161). Full `.sqx` corpus `staqex check` clean (same 2
   pre-existing, unrelated A11 standalone-import artifacts as every prior
   Issue in this project's recent history).

## Exit criteria

- [x] B09's and A02's `Evolve...times N` step functions perform the real,
  literal DTQW coin+shift step, not an identity placeholder.
- [x] The disclosed "consume-on-return" gap confirmed stale by direct
  testing, not assumed fixed.
- [x] Existing regression coverage for both files still passes.
- [x] Full regression sweep, spec verification, and corpus check all
  clean.
