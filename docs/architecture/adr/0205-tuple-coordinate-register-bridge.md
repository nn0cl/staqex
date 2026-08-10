# ADR 0205: Tuple-coordinate ↔ register bridge (`unpack_bits` / `pack_bits`)

## Status

**Proposed** (2026-08-11) — Architecture Path investigation, presented for
Adjudicator Architecture approval. **Not Accepted.** Acceptance would
authorize the type/gate/op decisions below as an architecture boundary;
it would **not** itself authorize Feature Path Red — a separate Feature
Plan and Issue-level Plan approval remain required, same as every other
Architecture Path ADR this session.

Companions: [LISS-0402](../../issues/LISS-0402-s02-selection-example.md)
(discovered the incompatibility this ADR addresses, by direct execution);
[LISS-0403](../../issues/LISS-0403-s02-benchmark-report.md) (empirically
confirmed the consequence — `top_k_overlap` measures ~0 because the two
representations cannot currently interact); ADR 0192/ADR 0194
(`prepare_selection` / `project onto feasible(...)`, unchanged by this
ADR).

## Context

Building S02's first real example (LISS-0402) surfaced a genuine, load-
bearing architecture gap, not a corner case: **Staqex has two mutually
incompatible representations of "an n-qubit register" today.**

| Representation | Produced by | Supports | Does not support |
|---|---|---|---|
| N separate named coordinates | `QubitRegister<N>` + `forEach` (`__foreach_{element}_{index}` wires, `evaluator.py::_run_foreach`) | Individual `apply`, Pauli-term `evolve under H` | No aggregate "restrict to a feasible subset" predicate — nothing gathers the N wires back into one collective handle after `forEach` completes |
| One tuple-valued coordinate | `prepare_selection(n)` (`evaluator.py::_bind_prepare_selection`, `Joint.bind_split(name, {pattern: weight ...})`) | `project ... onto feasible(...)` (ADR 0192/0194, filters by inspecting the tuple) | `evolve under H` with an ordinary Pauli-term Hamiltonian — confirmed by direct execution: `evolve psi1 under Z` raises `hamiltonian \`Z\` expects qubit support {0,1}, got [(0, 1), (1, 0)]` |

On the blackboard, "prepare n qubits, restrict to a feasible subspace,
evolve under a weighted Hamiltonian, observe" is **one** continuous
physical process on **one** object. S02's shipped `main_selection.sqx`
(LISS-0402) can only express this today by splitting it into two
*independent* Joint coordinates — the hard-constraint selection and the
soft-objective evolution never interact. LISS-0403's benchmark report
empirically measured the consequence: `top_k_overlap ≈ 0` across 20 shots
— the objective evolution has no channel through which to influence which
feasible selection gets sampled, purely because of this representational
split, not because of any physics the language intends to forbid.

This is exactly the "小手先の転用で表現力に制約を掛けたくない" pattern
this project has rejected before (ADR 0199 Amendment `reset` keyword):
the fix should not paper over the split with a workaround inside `project`
or `evolve`'s existing dispatch; it should give physicists an honest,
explicit way to cross between the two representations when they need to.

## Decision

### 1. Two new Kernel ops: `unpack_bits` and `pack_bits`

- `unpack_bits(psi, n)` — where `psi` is a tuple-valued Joint coordinate
  (e.g. from `prepare_selection`) and `n` is its known width — binds `n`
  new ordinary qubit-valued coordinates from `psi`'s tuple, one per
  position, preserving each World's amplitude exactly (a per-World
  pushforward: `assign[q_i] = assign[psi][i]`, no new probability mass
  introduced or removed). Bound as a multi-name `state (q0, q1, …, qn-1)
  = unpack_bits(psi, n)` — reuses the existing multi-name `StateBind`
  shape (`LISS-0228`/`ADR 0228`-style), no new binding grammar.
- `pack_bits(q0, q1, …, qn-1)` — the inverse: binds one new tuple-valued
  coordinate from `n` ordinary qubit coordinates, same per-World identity
  (`assign[psi][i] = assign[q_i]`). Bound as an ordinary single-name
  `state psi = pack_bits(q0, …, qn-1)`.
- Both are **honest, explicit, physically inert relabelings** — they
  change which coordinate names index the same underlying World
  information, not the amplitudes or the Born distribution. No new Joint
  primitive is needed; both lower to existing `bind_pushforward`/
  `bind_multi`-shaped per-World transforms already used throughout
  `evaluator.py`.
- After `unpack_bits`, the `n` qubit coordinates are ordinary — they
  accept `apply`, Pauli-term `evolve under H`, and (per this ADR's own
  Non-goals) are *not* automatically re-gathered for `project onto
  feasible(...)`; a physicist who needs the projector again after
  evolving calls `pack_bits` first.

### 2. `prepare_selection` / `project onto feasible(...)` remain unchanged

ADR 0192/ADR 0194's shipped predicate semantics, grammar, and runtime
behavior are untouched. This ADR is additive: it does not redesign
`prepare_selection` into N separate coordinates (Option A, considered and
rejected below) or touch already-shipped, tested Kernel code
(LISS-0324/0327/0328).

### 3. LINEAR treatment

`unpack_bits`/`pack_bits` consume their input root(s) and introduce their
output root(s), using exactly the existing generic Call-consumption
machinery (`hir.py`'s `_mark_linear_var_use`/multi-name bind handling) —
confirmed by this session's own LISS-0400 precedent that ordinary Call
consumption already covers a new Call form with no special-case hir.py
code, as long as the bound names are recognized linear carriers (already
true for `State`-typed binds; no `Continuous`-style new `Ty.kind` is
needed here since both sides of the bridge are ordinary `State` values).

## Rejected / deferred alternatives

### Option A: Redesign `prepare_selection` to bind N separate coordinates directly

Rejected for this ADR's scope, not rejected as wrong forever. This would
be the more complete unification (one representation, not two) — a
physicist would never need to know a bridge exists. But it requires
either (a) changing `prepare_selection`'s and `project onto
feasible(...)`'s already-shipped, tested representation
(LISS-0324/0327/0328), risking regression in accepted behavior, or (b)
inventing a persistent "Register" value that both `forEach`-expanded
wires and `project`'s predicate logic can address collectively — a
capability `QubitRegister<N>`/`forEach` does not have today either
(`forEach`'s wires are compiler-internal synthetic names, `__foreach_*`,
with no runtime handle gathering them back into one collective object
after the loop ends). Either path is a materially larger, riskier change
than this ADR's bridge. Left as a possible **future** ADR if the bridge
proves too indirect in practice — not foreclosed, not attempted now.

### Option B: Teach `evolve`/Pauli Hamiltonians to act on tuple-valued coordinates directly

Rejected — would need new per-position addressing syntax inside Operator
expressions (e.g. `Z[2]` to mean "Z on tuple position 2"), a genuinely
new piece of Operator-algebra grammar, not an additive Call. Larger
surface than Option C's plain data-shape conversion; deferred, not ruled
out permanently.

### Do nothing (leave the split as the only option)

Rejected — this is the status quo LISS-0402/0403 already found and
disclosed as a real, load-bearing expressiveness gap; the Adjudicator
explicitly asked for a fix plan, not a re-confirmation of the finding
(unlike Joint rational mode / trait-effect, which had no concrete
requirement behind them, this gap has one: S02 itself).

## Non-goals

- Redesigning `prepare_selection` or `project onto feasible(...)`
  (Option A).
- New Operator-algebra addressing syntax (Option B).
- Automatic/implicit conversion between the two representations —
  `unpack_bits`/`pack_bits` are always explicit statements, never
  inferred.
- Any change to `QubitRegister<N>`/`forEach`.
- Rewriting `main_selection.sqx` — a follow-on Feature Issue may use the
  bridge once shipped; not required by this ADR.

## Consequences

- Once shipped, S02's `main_selection.sqx` (or a successor version) could
  write the hard-constraint/soft-objective workflow as a **single**
  coordinate lineage: `prepare_selection` → `project onto feasible(...)`
  → `unpack_bits` → `evolve under H_obj` (now addressing the *actual*
  selected candidates' qubits, not a disconnected pair) → `pack_bits` →
  `measure`. This would let `top_k_overlap` become a meaningful, non-zero
  metric for the first time, because the objective evolution could
  finally influence which feasible pattern the terminal `measure`
  reports.
- Two new Kernel ops means two new Feature Path Issues at minimum
  (`unpack_bits`, `pack_bits`) — sizing/ordering is Feature Plan
  investigation work, not decided here, matching this ADR's own
  Acceptance boundary below.
- Does not resolve Option A's more complete unification; a future ADR may
  still revisit that if the bridge proves awkward in practice (e.g. if
  most programs end up unpacking immediately after every
  `prepare_selection`, suggesting the split should never have existed).

## Acceptance boundary

Acceptance of this ADR authorizes the `unpack_bits`/`pack_bits` op
shapes, their LINEAR treatment, and the Option A/B rejection reasoning
above as an architecture boundary. It does **not** authorize:

- Feature Path Red or any Kernel code change.
- A decision on Option A (full `prepare_selection` unification) — left
  open, not decided either way.
- Rewriting `main_selection.sqx` to use the new ops.

A Feature Plan investigation (new `LISS-*`, work-plan investigation
process) is required before any Red, exactly as ADR 0204 required for
Continuous Lane B.

## Decision history

| Date | Event |
|---|---|
| 2026-08-11 | Proposed — Architecture Path investigation following the Adjudicator's request for a fix plan after the S02 physicist/veteran-engineer expressiveness analysis |
