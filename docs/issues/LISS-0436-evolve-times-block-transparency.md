# LISS-0436: `Evolve (vars) times N { block }` must be built from a transparent, verifiable transform

## Metadata

- Local issue ID: LISS-0436
- Status: complete
- Type: Feature Path (`compiler/staqex/unitarity_check.py`, `pipeline.py`)
- Priority: P1 (closes a real, previously-undisclosed correctness gap:
  the `times N { block }` form of `Evolve` had *no* verification of its
  own block content at all)
- Owner / agent: Claude Code
- Parent: none — a standalone Local Issue, plan-approved via the
  Adjudicator's direct critical review of `Evolve`'s own design ("Evolveに
  否定的な視点で...設計したい" — approach `Evolve` skeptically; every
  equation must be expressible in the program; wrapping an
  already-expressed equation is what should mark it for quantum-computer
  execution, not an opaque escape hatch)
- Branch/PR: (see completion note)

## Intent

`unitarity_check.py`'s own docstring already discloses: "Full proof of
every pushforward remains Deferred." Investigating what that actually
means for `Evolve (vars) times N { block }` (as distinct from `Evolve {
psi under H for dur }`, which *does* get a real Hermiticity check) found
that it meant, literally, **no check at all**: the `EvolveExpr` handling
in `_check_expr_unitarity` only branched on `expr.hamiltonian is not
None`; when `None` (the `times N` form), execution fell through to the
generic `_children` walk, which only finds *nested* checkable call sites
— it never asked whether the block's own top-level content was trustworthy
in the first place. A block that calls an arbitrary user function is
opaque under this design: nothing inspects that function's own body, so
nothing actually guarantees the wrapped transform is coherent, even
though `Evolve` is meant to be the keyword that marks "this runs on the
quantum computer."

## Scope

New check in `_check_expr_unitarity`: when `expr.hamiltonian is None` and
`expr.body is not None` (the `times N` form), every `lets`/`result`
expression in the block must satisfy `_expr_is_transparent` — built only
from:

- State arithmetic and tensor-products (`BinOp`, `TensorExpr`, `TupleExpr`)
  and literals/bare variable references,
- struct-field access (`Attr`, for coefficients),
- a call to the closed, already-unitarity-checked `_QUANTUM_OPS`
  vocabulary (`apply`/`capply`/`controlled`/`walk_shift`/etc., the exact
  set `unitarity_check.py` already defines and uses elsewhere), or
- a call to a **user-defined function whose own body satisfies this same
  constraint**, checked recursively (memoized per function name, with a
  call-cycle guard).

Anything else — an unrecognized/undefined callee, classical control flow
(`Mix`/`WhenExpr`), or any other construct not on this allowlist — fails
closed with a new hard diagnostic, `EVOLVE_BLOCK_OPAQUE_TRANSFORM`, rather
than being silently trusted.

## Real bug found and fixed during Green

The first version of this check flagged a real, previously-passing test
(`tests/test_joint_preserve_and_harvest.py::test_evolve_times_classical_float`)
as opaque, even though its `step(...)` function is a legitimate DTQW step
(`apply` then `walk_shift` then a tensor-product return). Root cause: the
function also contains `Operator CoinOp = 0.7071067811865476 * (X + Z)` —
an `Operator`-typed bind, whose RHS is parsed via the *Operator-DSL*
grammar (`OpBin`/`OpVar`/`OpPauli`), a completely different AST node
family from the general expression grammar (`BinOp`/`Var`) this check
otherwise walks. `_expr_is_transparent` had no case for these nodes, so it
fell through to `return False`. Fixed by skipping `Operator`-typed binds
entirely inside the recursive body walk — an Operator bind constructs
matrix/Hamiltonian *data*, not a State transform, so it isn't something
this check needs to verify; its actual *use* (`apply(CoinOp, c)`) is
still checked as an ordinary call, and `_check_apply_unitary` already
independently verifies the matrix itself is unitary at that call site.
This matches `check_unitarity`'s own top-level statement loop, which
already skips Operator binds the identical way (`local_operators[stmt.
names[0]] = stmt.expr; continue`) — the new recursive body walk simply
hadn't inherited that same, already-established precedent.

## Design verification performed

1. 9 dedicated tests
   (`tests/test_liss_0436_evolve_times_block_transparency_red.py`):
   pure-arithmetic block (B06's own shape), a direct closed-vocabulary
   call, a user function built from closed-vocabulary calls (B09/A02's
   real post-LISS-0435 DTQW step, the exact target shape), a user
   function that locally builds its own Operator before `apply`ing it
   (the real bug found above, now a named regression guard), an
   unrecognized/undefined callee (opaque), `Mix` inside the block
   (opaque, classical control flow), a user function that itself calls an
   opaque callee (transitively opaque, verifying the recursion), the
   `under H for dur` form confirmed unaffected, and the full corpus's
   only three `times N` usages (B06/B09/A02) confirmed to compile clean.
2. Full regression sweep: 1550 passed (1541 + 9 new). Spec verification:
   100.00% (161/161). Full `.sqx` corpus `staqex check` clean (same 2
   pre-existing, unrelated A11 artifacts).

## Exit criteria

- [x] `Evolve (vars) times N { block }`'s own block content is now
  actually verified, not silently trusted — closing a real gap
  `unitarity_check.py`'s own docstring already disclosed but this
  specific form had never addressed at all.
- [x] The verification is transitive (recursive across user-function call
  boundaries), not merely surface-level.
- [x] A real false positive found during Green (Operator-typed local
  binds) root-caused and fixed, matching an existing precedent elsewhere
  in the same file rather than inventing new handling.
- [x] The full shipped corpus (B06/B09/A02, the only three `times N`
  usages that exist) verified to still compile clean.
- [x] Full regression sweep, spec verification, and corpus check all
  clean.
