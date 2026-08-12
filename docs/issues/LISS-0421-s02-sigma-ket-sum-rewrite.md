# LISS-0421: rewrite S02 `main_selection.sqx` step 1 to the `Sigma` ket-sum

## Metadata

- Local issue ID: LISS-0421
- Status: complete
- Type: Feature Path (`examples/showcase/S02_drug_discovery/main_selection.sqx`,
  `compiler/staqex/unitarity_check.py`)
- Priority: P2
- Planning size: S (one-statement rewrite in an already-shipped example,
  plus one real compiler bug found and fixed during Green)
- Owner / agent: Claude Code
- Parent: follow-on to WP-0098 / LISS-0420 (batch
  `case-sensitive-keywords-and-sigma-binder`), explicitly deferred by that
  batch's own stated scope
- Branch: `feature/liss-0421-s02-sigma-ket-sum-rewrite`
- GitHub Issue / PR: (opened at completion)

## Intent

LISS-0420 shipped `Sigma (x In {0,1}^n) { |x> }` as a literal, blackboard-
matching way to write an equal superposition over all `2^n` selection
patterns — the exact construction S02's `main_selection.sqx` step 1 already
needed, but had to spell as the opaque native primitive `prepare_selection(n)`
until the new syntax existed. WP-0098's own investigation and LISS-0420's own
doc both explicitly deferred this rewrite as a follow-on Issue. The
Adjudicator requested it directly ("S02も更新して").

## Scope

Rewrite `main_selection.sqx`'s
`State psi_sel = prepare_selection(n)` to
`State psi_sel = Sigma (x In {0,1}^n) { |x> }` (per LISS-0420's own
recommendation: no external coefficient, since the ket-sum is already
self-normalizing and an external coefficient would apply as a redundant,
unnormalizing amplitude scale — Hard Stop 2's verified consequence).
Update the surrounding header/step-1 comments to reference the new
construction instead of the retired-from-this-file primitive.

## Real bug found and fixed during Green

`staqex check` on the rewritten file failed:

```
PREDICATE_PROJECTOR_ERROR:63: `project` requires a quantum State (Hilbert
space). Classical `coin()` filters are forbidden.
```

at the very next statement, `project psi_sel onto feasible(...)` — a
regression from the working `prepare_selection(n)` baseline.

Root cause: `compiler/staqex/unitarity_check.py`'s static-only
`_expr_is_quantum` (used by the `project` guard's `PREDICATE_PROJECTOR_ERROR`
check, `unitarity_check.py:234-258`) recognizes a variable as carrying a
coherent quantum lineage by checking the *shape of its binding expression* —
`KetLit` is recognized directly; `Call`-shaped bindings are recognized via
membership in `_QUANTUM_OPS`, which already listed `"prepare_selection"`.
`KetSumBinder` (LISS-0420's new AST node) was never added to either
recognition path, so `psi_sel = Sigma (x In {0,1}^n) { |x> }` fell through
`_expr_is_quantum` to its default `return False` — making the *now-quantum*
`psi_sel` look classical to this one static pass, which then fired the same
diagnostic it uses for a genuine `coin()`/classical-Var source.

This is the same class of gap as several other bugs found during WP-0098:
a check that recognizes validity by the *construction site* (is this
specific `Call` name in an allowlist?) rather than by *structural shape*
(does this expression denote a coherent ket lineage?). `unitarity_check.py`
is a separate static-only pass from `typecheck.py` and from the runtime
check in `evaluator.py` (which already recognizes any tuple-valued
coordinate structurally, not by origin) — this file's own recognition
logic simply hadn't been extended for the new node.

**Fix**: added `KetSumBinder` to `_expr_is_quantum`'s direct recognition
(`unitarity_check.py:493-496`), parallel to the existing `KetLit` case —
correct because a `KetSumBinder`'s body is parser-verified to be exactly
`|<bound variable>>` (LISS-0420 Hard Stop 1), i.e. structurally a ket sum,
the same coherent-lineage character as a literal `KetLit`. Both the
non-strict (`quantum`) and strict (`strict`) recognition dicts use the same
`_expr_is_quantum` function, so one added case covers both call sites.

## Design verification performed

1. Confirmed the fix is the minimal, structurally-correct one: `KetSumBinder`
   is recognized the same way `KetLit` already is (both are ket-literal-shaped
   nodes), not by adding `Sigma`/ket-sum to the `Call`-based `_QUANTUM_OPS`
   allowlist (which would be the wrong mechanism — `KetSumBinder` is not a
   `Call` node).
2. Re-ran `staqex check` on the rewritten file: clean (`ok — no hard compile
   diagnostics`).
3. Re-ran `examples/showcase/S02_drug_discovery/host/run_selection.py`
   (seeded, `seed: 0`): output is byte-identical to the pre-rewrite baseline
   captured on the merged `main` before this Issue's edit —
   `status: succeeded`, `selection pattern: (0, 1, 1, 1, 1, 1, 0, 0)`,
   `Vacuum: False`.
4. Full regression sweep: 1511 passed (unchanged count from the post-WP-0098
   baseline — this Issue only fixes a static-check gap, adds no new test
   surface of its own beyond what SV-23's existing predicate-projector
   suite already exercises). Spec verification: 100.00% (161/161),
   including `sv23-Coin-project-banned`, confirming the fix does not weaken
   the check's original purpose (a genuine classical `Coin()` source is
   still correctly rejected).

## Exit criteria

- [x] `main_selection.sqx` step 1 uses `Sigma (x In {0,1}^n) { |x> }`
  instead of `prepare_selection(n)`, matching the blackboard equation term
  for term.
- [x] `staqex check` passes clean on the rewritten file.
- [x] `run_selection.py`'s seeded terminal output is byte-identical to the
  pre-rewrite baseline.
- [x] The `unitarity_check.py` `KetSumBinder` recognition gap is fixed and
  regression-guarded by the existing full suite (no new test needed beyond
  what already exercises this file end-to-end and SV-23's existing
  predicate-projector coverage).
- [x] Full regression sweep passes (1511); spec verification 100.00%.
