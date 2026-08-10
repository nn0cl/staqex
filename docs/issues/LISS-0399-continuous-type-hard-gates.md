# LISS-0399: `Continuous<T>` type + `ContinuousFieldPort` + hard gates

## Metadata

- Local issue ID: LISS-0399
- Status: proposed
- Phase: phase-0-design (Investigation stage; Red not authorized)
- Type: Feature Path (Kernel — `TypeChecker` + `hir.py`; Host — new port)
- Priority: P1
- Initial planning size: `M`
- Current planning size: `M`
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

## Exit condition

- [ ] `Continuous<T>` recognized as a distinct Type-First carrier, not
  confused with `State<T>`.
- [ ] `ContinuousFieldPort` + a fake test adapter exist; `field_from_host`
  dispatches through it, unchanged Kernel-side numerics (no Kernel math on
  the field itself).
- [ ] `hir.py` tracks `Continuous` roots as `introduced`; an unconsumed
  root produces `LINEAR_IMPLICIT_DISCARD`.
- [ ] `measure`/`evolve`/Joint-forming/QPU-emission use of a `Continuous`
  value produces `CONTINUOUS_ESCAPE_ERROR`.
- [ ] Full regression sweep unaffected outside new/targeted assertions.

## Explicitly out of scope

- `weight`/`mask` (LISS-0400).
- `finiteize` extension / real LINEAR consumption (LISS-0401).
- A real (non-fake) `ContinuousFieldPort` adapter — this Issue ships the
  port contract + a fake/test adapter only, same precedent as every other
  Host port in this project (concrete adapters are a separate, later
  concern, not required to ship the port itself).
