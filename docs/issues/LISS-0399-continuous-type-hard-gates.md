# LISS-0399: `Continuous<T>` type + `ContinuousFieldPort` + hard gates

## Metadata

- Local issue ID: LISS-0399
- Status: complete
- Phase: phase-3-refactor (Green/Refactor complete under batch approval
  `execution-batch-wp-0097.json`)
- Type: Feature Path (Kernel — `TypeChecker` + `hir.py`; Host — new port)
- Priority: P1
- Initial planning size: `M`
- Current planning size: `L` (reclassified 2026-08-10 after direct-execution
  investigation showed the "hard gates" are not free byproducts of existing
  type-checking — see Design verification below)
- Owner / agent: Claude Code
- Dependencies: [ADR 0204](../architecture/adr/0204-continuous-lane-b-type-world.md)
  (**Accepted**)
- Blocks: LISS-0400 (`weight`/`mask` need a `Continuous` value to operate
  on), LISS-0401
- Parent: [WP-0097](../work-plans/WP-0097-continuous-lane-b-ship.md)
- Related: `compiler/staqex/typecheck.py`, `compiler/staqex/hir.py`,
  new `compiler/staqex/continuous_field.py` (port), new
  `compiler/staqex/adapters/continuous_field_*.py` (test/fake adapter)
- Branch: `feature/liss-0399-continuous-type-hard-gates` (opened only after
  batch approval or Issue-level Plan approval)
- GitHub Issue / PR: (opened at Completion)

## Scope

The smallest unit that makes `Continuous<T>` genuinely testable: the type
itself, a minimal producing operation, and the hard gates that keep it out
of `measure`/`evolve`/Joint/QPU (ADR 0204 Decisions 1–2). Combining the
type and its minimal producer in one Issue avoids an untestable
type-with-no-constructor intermediate state.

1. `Continuous<T>` recognized as a distinct Type-First carrier (`state`-bind
   inference, mirrors `State<T>`; MVP payload tag `Field`).
2. New `ContinuousFieldPort` (provider-neutral Host port, mirrors
   `RngPort`/`HostInputPort`): `field(source: str, domain: str,
   provenance: Mapping[str, Any]) -> ContinuousFieldHandle`.
3. Kernel-callable `field_from_host(source, domain, provenance = {…}) ->
   Continuous<Field>`, dispatched through the port. Runtime representation
   is the opaque handle only — never a Joint `World`.
4. `hir.py` linear-use tracking: `Continuous` roots are `introduced`; an
   unconsumed root produces `LINEAR_IMPLICIT_DISCARD` (no consuming
   operation exists yet in this Issue, so Red/Green exercises this via a
   `field_from_host` result that is simply never touched again).
5. Hard-gate diagnostics (`CONTINUOUS_ESCAPE_ERROR`): a `Continuous` value
   used as the operand of `measure`, inside `evolve`, in any Joint-forming
   expression, or in any QPU/QASM emission path.

## Design verification performed before Red

1. **`Controller` is the closest existing precedent for a new Type-First
   annotation getting its own `Ty.kind`** (`typecheck.py:504-514`): a
   dedicated `if tname == "Controller": ... Ty("Controller", carrier,
   DIMLESS)` branch, not a generic fallback. `Continuous` follows the same
   pattern: `if tname == "Continuous": ... Ty("Continuous", payload_tag,
   DIMLESS)`. `Ty.__str__` (`typecheck.py:95-118`) needs a matching
   `elif self.kind == "Continuous"` branch — confirmed its current final
   `else` silently mislabels any unrecognized kind (including the
   already-shipped `"Controller"`) as `State<…>` in diagnostic text; adding
   an explicit branch for `Continuous` avoids repeating that pre-existing,
   undisclosed, out-of-scope display quirk.
2. **Confirmed by direct compilation that "hard gates" are not a free
   byproduct of existing type-checking.** Using the already-shipped
   `Controller` kind as a stand-in non-`State` value (since `Continuous`
   itself doesn't exist yet to test with), two real programs were compiled:
   - `state r = evolve bit under H for 1.0` (`bit: Controller<Bit>`)
     produced **no type-mismatch diagnostic at all** — compiled unit
     accepted, execution ordinarily proceeds.
   - `apply(X, bit)` similarly produced **no diagnostic**.
   Grep confirms `Measure` statements are **never type-checked** anywhere
   in `typecheck.py` today (`grep -n "isinstance(stmt, Measure)"` matches
   exactly one unrelated site — `MEASURE_IN_FUNCTION_ERROR`, about
   forbidding `measure` inside non-`main` functions, not about the
   *operand's* type). This means the ADR 0204 "hard gates (compile-time
   rejection, not just documentation)" requirement needs genuinely new
   validation code at each site — it is not already covered by existing
   type-mismatch machinery.
3. **Scope narrowed to the three concretely-confirmed-permissive sites**:
   `measure`, `evolve …under…`, and the `apply`/gate-Call family
   (`apply`/`cnot`/`toffoli`/`capply`/`ocapply`/`controlled` — the same
   name set `dynamic_capability.py`'s `_call_quantum_targets` already
   enumerates for an unrelated purpose, reused here as the authoritative
   "these are the quantum-gate Call forms" list rather than inventing a
   second one). Other conceivable Joint-forming sites (`KetLit`, `Coin`,
   tensor literals) take **literal labels or no operand**, not a
   `Var` reference to an arbitrary prior binding — there is no realistic
   syntactic path for a `Continuous`-kinded value to reach them, so they
   are not gated by this Issue (disclosed, not silently assumed safe).
4. **`_stmt_binds_state` (`hir.py:280-318`) does not currently recognize a
   `Continuous`-typed declared bind** (`stmt.ty.name in {"State",
   "DensityState"}` — `"Continuous"` is not in that set), so a
   `Continuous`-typed `state` bind would **not** enter LINEAR tracking at
   all without an explicit extension. Adding `"Continuous"` to that set is
   the minimal change that makes `_check_state_bind` mark it `introduced`,
   after which the **already-generic, kind-agnostic** `_discard_diags`
   (diffs `introduced - consumed`) produces `LINEAR_IMPLICIT_DISCARD` for
   free when unconsumed — confirmed by reading `_discard_diags`'s
   implementation, which never inspects `Ty.kind` at all.
5. **Gate implementation location: `typecheck.py`, not `hir.py`.**
   `TypeChecker` already owns `self.env: dict[str, Ty]` with live Ty-kind
   lookups; `hir.py`'s `_analyze_block` only receives a read-only
   `module_symbols` snapshot and is architecturally about LINEAR resource
   tracking, not Ty-kind validation (matching the existing division of
   labor: `typecheck.py` decides types, `hir.py` decides linear
   consumption). The new `CONTINUOUS_ESCAPE_ERROR` checks are added to
   `TypeChecker.check_unit`'s existing per-statement loop (a new `Measure`
   branch, since none exists) and to wherever `evolve` and the gate-Call
   family are already inferred (`_infer_evolve`, `_infer`'s `Call`
   dispatch) — exact insertion points confirmed during Red against the
   real statement-processing loop structure already read above
   (`typecheck.py:289+`).

## Exit condition

- [x] `Continuous<T>` recognized as a distinct Type-First carrier, not
  confused with `State<T>` (`typecheck.py` `tname == "Continuous"` branch,
  mirrors `Controller`).
- [x] `ContinuousFieldPort` + a fake test adapter exist; `field_from_host`
  dispatches through it, unchanged Kernel-side numerics (no Kernel math on
  the field itself) — new `compiler/staqex/continuous_field.py`.
- [x] `hir.py` tracks `Continuous` roots as `introduced`; an unconsumed
  root produces `LINEAR_IMPLICIT_DISCARD` (`_stmt_binds_state` extended).
- [x] `measure`/`evolve` use of a `Continuous` value fails closed —
  **discovered during Green: free via the already-existing, generic
  `_assert_is_state` allowlist check (`TYPE_NOT_STATE`)**, once
  `Continuous` is a real distinct `Ty.kind` outside that allowlist; no new
  diagnostic code needed for these two sites.
- [x] `apply`/gate-Call family use of a `Continuous` value produces the
  new `CONTINUOUS_ESCAPE_ERROR` (generic per-argument check in `_infer`'s
  Call-argument loop, scoped to reject only `Continuous`-kind — verified
  by direct testing this does **not** affect `Wire`-kind `forEach`
  elements, which are a different, pre-existing non-`State` kind not in
  `_assert_is_state`'s allowlist either; reusing that allowlist here would
  have broken shipped `forEach`/`apply` examples, so a narrower dedicated
  check was used instead). Explicitly forward-compatible with LISS-0400/
  0401: `field_from_host`/`weight`/`mask`/`finiteize` are named exempt so
  those Issues' own Continuous-accepting Call forms are not blocked by
  this Issue's own gate.
- [x] Full regression sweep unaffected outside new/targeted assertions:
  **1431 passed**, up from 1424 by exactly the 7 new tests.

## Explicitly out of scope

- `weight`/`mask` (LISS-0400).
- `finiteize` extension / real LINEAR consumption (LISS-0401).
- A real (non-fake) `ContinuousFieldPort` adapter — this Issue ships the
  port contract + a fake/test adapter only, same precedent as every other
  Host port in this project (concrete adapters are a separate, later
  concern, not required to ship the port itself).
