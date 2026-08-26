# Kernel stub and placeholder registry

| Field | Value |
|---|---|
| Status | **working registry** — evidence-backed by direct `compile_source`/`run_source` execution; not an ADR; not implementation approval |
| Purpose | Prevent a future contributor (human or AI agent) from mistaking a name that merely *parses*, is *whitelisted*, or *appears in a passing test* for a name with real, verified semantics |
| Companion | [Physicist source-friction ledger](physicist-source-friction-ledger.md) covers a different concern — DX friction for a physicist writing source. This registry covers implementation-honesty gaps that mislead an *investigator* extending the Kernel. |
| Authority | Direct `compile_source(...)` / `run_source(...)` probes against the shipping Kernel, run and recorded on the date each entry was added |

## Why this document exists

Across several sessions of extending the S02/WP-0093 and WP-0092 work, the
same failure mode recurred: a name (a function call, a diagnostic code, a
keyword) *looks* implemented — it parses, it appears in a passing test, it
has a plausible docstring or error message — but a direct compile/run probe
shows it does something much shallower than its name suggests, or nothing at
all. Grep and static reading are not sufficient evidence that a Kernel
capability exists. **Before recommending or building on any name below (or
any name not yet catalogued), run it through `compile_source`/`run_source`
directly and read the actual diagnostics.**

## Registry

### `finiteize(lo, hi, n_bins, n_samples[, seed])`

- File: `compiler/staqex/runtime/evaluator.py::_bind_finiteize` (ADR 0185 /
  LISS-0313)
- Looks like: a mechanism for encoding a finite set of records (e.g.
  candidates) into the Kernel.
- Actually: a general-purpose continuous-PDF equal-width-histogram Monte
  Carlo primitive — it approximates a **uniform draw on `[lo, hi)`** with
  `n_bins` bins from `n_samples` draws. It has no relationship to discrete
  records, IDs, or S02 candidates.
- Verified misuse: `tests/test_s02_selection_surface_red.py` calls
  `finiteize(0.0, 1.0, 8, 16, 0)` purely to obtain "a finite State with 8
  outcomes" to feed into `prepare_selection` — the `lo`/`hi`/`n_samples`
  values carry no S02 meaning; `n_bins=8` was chosen only because it
  happened to match the fixture's candidate count in that one test.

### `prepare_selection` (pre-LISS-0324)

- File: `compiler/staqex/unitarity_check.py::_QUANTUM_OPS` (whitelist
  entry only)
- Looks like: a real state-preparation operation (it appears in the
  "quantum lineage" whitelist alongside `apply`, `capply`, `hadamard`,
  etc.).
- Actually (before LISS-0324): no evaluator implementation existed.
  Calling it at runtime failed:
  ```python
  run_source('package t\npub fn main() -> Unit {\n state x = prepare_selection(3)\n measure x\n}',
             settings={'target': 'local', 'seed': 0})
  # -> status: "failed", {'code': 'RUNTIME_ERROR', 'message': "unknown function `prepare_selection`"}
  ```
- Status: **implemented for real** by
  [LISS-0324](../issues/LISS-0324-s02-prepare-selection.md)
  (`prepare_selection(n: Int)` → equal superposition over `2^n` selection
  patterns via `Joint.bind_split`, `Evaluator._bind_prepare_selection`).
  Kept here as a worked example of the pattern: *whitelist membership is
  not evidence of implementation.*

### `project ... onto feasible(...)` — runtime execution still crashes

- Files: `compiler/staqex/pipeline.py::_append_selection_projector_region`
  (compile-time IR annotation, fixed by LISS-0322) and
  `compiler/staqex/runtime/evaluator.py` (runtime `project` op, **not**
  touched by LISS-0322)
- Looks like: after LISS-0322 fixed `constraint_ref` to be source-derived
  and to reject unknown predicate names, a program using
  `project ... onto feasible(...)` looks like a working, capability-checked
  feature — it compiles cleanly with a correct IR witness.
- Actually: LISS-0322 only touched the **Quantum Semantic IR annotation
  layer**. The runtime `project` op still evaluates the `feasible(...)`
  target as an ordinary classical function call, which always crashes:
  ```python
  compile_source(src).ok   # -> True
  run_source(src, settings={'target': 'local', 'seed': 0}).diagnostics
  # -> ({'code': 'RUNTIME_ERROR',
  #      'message': 'call cannot be classical value in Phase 2.2 value context'},)
  ```
  (verified 2026-08-05, same session as LISS-0322/LISS-0324)
- Why misleading (pre-fix): LISS-0322's own scope notes ("Real Projector
  *execution* semantics... the Static Kernel does not execute S02 programs
  end-to-end yet") already said this honestly — but a reader who only saw
  "`compile_source(...).ok == True` and `constraint_ref` looks right" could
  easily conclude the feature worked. It did not: any program using this
  syntax used to fail at execution time, unconditionally, regardless of
  what was fixed at compile time.
- **Now fixed** by [LISS-0327](../issues/LISS-0327-host-input-port-foundation.md)
  (new `HostInputPort`, ADR 0194) and
  [LISS-0328](../issues/LISS-0328-selection-projector-predicate-execution.md)
  (real `feasible(...)` execution): `project`'s runtime dispatch now
  special-cases a `feasible(...)` target (parallel to the existing `KetLit`
  case) and builds a combined predicate from `exactly_selected` (a pure
  function of the pattern's own Hamming weight),
  `pairwise_compatible`/`diversity_at_least` (looked up from a
  same-named Host-bound matrix via the new port, validated eagerly, fail-
  closed if missing/malformed), applied through the same
  `joint.project_coord` + renormalize path `project(psi, k)` already
  used. A penalty-only program with no `project ... onto` is unaffected;
  LISS-0322's IR-lowering layer is unchanged.

### `QubitRegister<N>`

- File: `compiler/staqex/runtime/evaluator.py` (comment at the `QubitRegister`
  bind case: *"Static Hilbert shape is compile-time metadata; it has no
  runtime allocation or state coordinate in the Kernel."*)
- Looks like: a real multi-qubit runtime register (it is used with
  `forEach q in register { apply(H, q) }` in shipped examples like
  `examples/basics/B11_qft_registers/`, which reads as genuine per-qubit
  gate application).
- Actually: purely a compile-time resource-shape annotation for QFT/IQFT
  lowering and static resource checks. It never becomes a Joint coordinate.
  Two further traps compound this:
  - `forEach` bodies cannot `measure` (`FOR_EACH_MEASURE_ERROR`) — you
    cannot terminally read out a register qubit-by-qubit inside the loop
    that prepared it.
  - No shipped example measures an entire register as one combined
    classical outcome; every example entangles individually-named `state`
    qubits and measures exactly one at the end.
  - `measure (a, b, c)` (a tuple of multiple state variables) parses but is
    rejected by the linear-use checker with `LINEAR_IMPLICIT_DISCARD` on
    each tuple item — it is not a working joint-measurement mechanism.

### H1 authoring layer (`h1_authoring.py`) — multiple substring/name heuristics behind real-looking diagnostic codes

`compiler/staqex/h1_authoring.py` and `Parser._parse_h1_experiment_body`
implement a **lightweight, demonstrative analysis layer** for the
`experiment { ... }` lane's tooling/diagnostic surface — not a real
AST-based semantic analyzer. Its diagnostic codes read exactly like normal
compiler errors, but several are raw pattern matches:

- **`_parse_h1_experiment_body`** (line-lexeme classification): tags a
  source *line* as `H1Mixture`/`H1Superposition`/`H1CoherentControl`/etc.
  purely by checking whether a lexeme like `"mix"` or `"superpose"` appears
  anywhere in that line's tokens — no real expression parsing, no
  typechecking. (Discovered during LISS-0320's investigation; see that
  Issue for the full write-up.)
- **`BASIS_MISMATCH_ERROR`** (fixed by
  [LISS-0326](../issues/LISS-0326-h1-basis-target-capability-diagnostics.md)):
  used to fire on
  `if "basis position_grid" in source and "state spin" in source:` — a
  **raw source-text substring check**, not an AST dependency check.
  Verified (pre-fix): renaming the identifiers to
  `grid_position`/`spin_carrier` made an otherwise-identical,
  semantically-still-mismatched program pass with zero diagnostics;
  conversely, defining both an unrelated `position_grid`-basis theory and
  an unrelated `spin` state in the *same source file*, with no actual
  dependency between them, still fired the error. **Now fixed**: the
  parser captures `basis`/`coordinate` as real `TheoryDecl` fields and a
  `prepare ... over Theory.field` binding as `H1Prepare.bound_to`; the
  diagnostic correlates each `evolve under Theory.H`'s state back to the
  `H1Prepare` that introduced it and compares its `bound_to` against the
  theory's declared domain name.
- **`TARGET_CAPABILITY_REJECT`** (same file, fixed by LISS-0326): used to
  fire on the identical pattern —
  `if "Lattice<128>" in source and "qpu:CH0_STATIC_V1" in source:` — on
  textual co-occurrence, not on whether the declared site count actually
  exceeded the named target's real capacity. Deeper investigation also
  found the fixture target name `CH0_STATIC_V1` was never a real
  registered profile in `target_capability.py` (`_FIXTURE_QUBITS`) at
  all — the diagnostic could only ever fire via the substring match, never
  via a real capability lookup. **Now fixed**: a new top-level
  `H1RealizeDecl` (`realize qpu:<target>`, previously not parsed at all —
  it produced a `PARSE_ERROR`, silently masked by the substring check
  firing regardless) is looked up via
  `target_capability.FakePhysicalTargetPort().load_profile(...)`, and the
  declared `coordinate ... Lattice<N>` size is compared against the real
  profile's `max_logical_qubits`. The existing test's fixture target was
  corrected to the real `NH5_REFERENCE` profile (max 8).
- **`NON_HERMITIAN_OPERATOR_ERROR`** (fixed by
  [LISS-0325](../issues/LISS-0325-h1-non-hermitian-operator-diagnostic.md)):
  used to fire on
  `if "i" in referenced_names and "sum" not in operator.source_tokens:` — a
  **naming-convention heuristic** (does an identifier literally spell `i`?),
  not a type-aware Hermiticity check. Verified false positive (pre-fix):
  ```staqex
  theory Valid {
    parameter i: Real
    operator H = i * Z
  }
  ```
  (`i` declared as an ordinary `Real` scalar, mathematically producing a
  Hermitian operator) used to still raise `NON_HERMITIAN_OPERATOR_ERROR`,
  because the checker only saw the identifier spelling, not its declared
  type. **Now fixed**: the condition also checks
  `"i" not in operator.parameter_types`, so a declared real parameter named
  `i` is excluded. Kept here as a worked example of the pattern: a
  naming-convention heuristic can be corrected once real structured data
  (`parameter_types`) already exists to consult — contrast with
  `BASIS_MISMATCH_ERROR`/`TARGET_CAPABILITY_REJECT` below, where no such
  structured data exists yet.

Why this pattern was misleading: all four codes described above
(`BASIS_MISMATCH_ERROR`, `TARGET_CAPABILITY_REJECT`,
`NON_HERMITIAN_OPERATOR_ERROR`, and the line-lexeme classifier) are named
and worded exactly like genuine AST/type-level static analysis, but three
of the four were raw source-text substring or identifier-spelling
heuristics. A test asserting one of these codes fires used to be evidence
only that *the specific string pattern in that test's source* triggered
the check — not evidence of a general, structurally-sound analysis.

**Real-fix status (2026-08-05):** [WP-0092](../work-plans/WP-0092-quantum-mental-model-follow-up.md)
work unit 6 closed all three diagnostic-honesty gaps.
[LISS-0325](../issues/LISS-0325-h1-non-hermitian-operator-diagnostic.md)
(`NON_HERMITIAN_OPERATOR_ERROR`) shipped, PR #359.
[LISS-0326](../issues/LISS-0326-h1-basis-target-capability-diagnostics.md)
(`BASIS_MISMATCH_ERROR` / `TARGET_CAPABILITY_REJECT`) shipped, adding real
AST fields (`TheoryDecl.basis`/`.coordinate`, `H1Prepare.bound_to`,
`H1Evolve.theory_name`, a new top-level `H1RealizeDecl`) and a
target-capability-registry lookup where none existed before. The
line-lexeme classifier (`_parse_h1_experiment_body`'s per-line
`H1Mixture`/`H1Superposition`/etc. tagging) remains a heuristic — it was
not in scope for either Issue and is unaffected.

### `system` — an already-overloaded keyword

- Established meanings already shipped:
  1. Trait/`impl` marker `System` (DEC-0005 / ADR 0082) — used in the
     `<T: Interface>` trait-dispatch model.
  2. Named register-group declaration:
     `system Name { register x: QubitRegister<N> ... }` (ADR 0105 /
     LISS-0067, `RegisterSet`).
- Risk: an external or future proposal reusing `system Example { ... }` as
  a *third*, unrelated meaning (e.g. a top-level program container, as one
  reviewed external design package proposed) would silently collide with
  both existing meanings. Always grep + directly compile a probe program
  before assuming a keyword is free to reuse.

### `observe` — retired, not merely unused

- `compiler/staqex/tokens.py::RETIRED = {"observe": "measure", ...}`.
  Verified live: compiling `observe x` produces
  `RETIRED_KEYWORD: retired \`observe\` → use \`measure\``.
- Risk: because the keyword *reads* naturally for "look at this
  mid-program," it is an easy target for a future proposal to reintroduce
  under new semantics (e.g. mid-circuit checkpoint) without realizing the
  name is already a hard, intentional retirement, not an accidental gap.
  The already-shipped non-destructive alternative is `inspect(state)` /
  `DiagnosticView<T>` (ADR 0189, PR #342).

## How to avoid adding a new entry unknowingly

Before treating any Kernel name, diagnostic code, or type as evidence that
a capability is implemented:

1. **Run it, don't just grep it.** `grep` proves a string exists; only
   `compile_source(...)` (for compile-time claims) or `run_source(...)`
   (for runtime claims) proves behavior.
2. **Check both directions.** For a diagnostic code, verify it fires on a
   real violation *and* does not fire on a real non-violation with
   different spelling — a name-based or substring-based heuristic often
   passes the first check and fails the second.
3. **A passing test proves that test's exact input works, nothing more.**
   Especially for whitelist-driven or generic-fallback code paths (any
   `Call` with an unrecognized callee, any name in a permissive set), a
   green test can be evidence of narrow compile-time plumbing rather than
   general semantics.
4. **Check whether a "fix" changed compile-time IR, runtime evaluation, or
   both.** A committed fix note should say which; if a Local Issue's own
   "Explicitly out of scope" section names execution semantics as
   deferred, treat any success at the IR/compile level as exactly that —
   compile-level only — until a runtime probe confirms otherwise.
5. **Add an entry here** when a new gap of this kind is found, with the
   verification command and output that proves it, so the next
   investigator does not have to rediscover it.
