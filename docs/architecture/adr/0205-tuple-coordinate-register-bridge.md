# ADR 0205: Pauli-term Hamiltonian evolution on tuple-valued coordinates

## Status

**Proposed** (2026-08-11) — Architecture Path investigation, presented for
Adjudicator Architecture approval. **Not Accepted.** Acceptance would
authorize the decision below as an architecture boundary; it would
**not** itself authorize Feature Path Red — a separate Feature Plan and
Issue-level Plan approval remain required, same as every other
Architecture Path ADR this session.

Revision note: this ADR originally proposed an `unpack_bits`/`pack_bits`
bridge (Option C in the rejected-alternatives list below). The Adjudicator
asked for the fundamentally correct fix, "将来的な負債にならないほう"
(the one that does not become future debt), even at greater implementation
size. Direct investigation found a smaller **and** more correct answer
than either the original bridge or the first-considered full
`prepare_selection` redesign — see Decision below.

Companions: [LISS-0402](../../issues/LISS-0402-s02-selection-example.md)
(discovered the incompatibility this ADR addresses, by direct execution);
[LISS-0403](../../issues/LISS-0403-s02-benchmark-report.md) (empirically
confirmed the consequence — `top_k_overlap` measures ~0 because the two
representations cannot currently interact); ADR 0192/ADR 0194
(`prepare_selection` / `project onto feasible(...)`, unchanged by this
ADR).

## Context

Building S02's first real example (LISS-0402) surfaced a genuine, load-
bearing architecture gap: `prepare_selection(n)` binds **one** Joint
coordinate whose value is an `n`-tuple; `evolve psi under H` (Pauli-term
`H`) rejects it — confirmed by direct execution:
`evolve psi1 under Z` raises `hamiltonian \`Z\` expects qubit support
{0,1}, got [(0, 1), (1, 0)]`. S02's shipped `main_selection.sqx` works
around this by evolving a **separate**, disconnected qubit pair for the
soft objective, which LISS-0403's benchmark report empirically confirmed
cannot influence which feasible selection is sampled (`top_k_overlap ≈
0`).

### What direct investigation found (not assumed)

1. **Indexed Pauli-term syntax already ships.** `Z[0]`, `X[1]`, `Z[0] *
   Z[1]` already parse (`parser.py:3112-3120`, `OpIndexed`) and already
   compile correctly to genuine multi-site Pauli strings
   (`sparse_pauli.py::_eval`, `hamiltonian.py::_eval_qubits`) — confirmed
   by compiling `Z[0] * Z[1]` and inspecting the resulting
   `PauliTerm(kinds=('Z','Z'))`. **A real, separate, previously-unknown
   bug was found in the process**: `main_selection.sqx`'s own
   `objective_hamiltonian` used bare, unindexed `Z * Z` for its
   "diversity" term — since unindexed Pauli atoms default to site 0
   (`hamiltonian.py:288`: `site = 0 if op.site is None else op.site`),
   `Z * Z` on the *same* site multiplies to the identity (`Z² = I`),
   silently contributing nothing. This ADR's fix, once shipped, corrects
   this alongside closing the architecture gap (see Consequences).
2. **The multi-qubit evolve path already does almost exactly what a
   tuple-coordinate version would need** (`evaluator.py::_hamiltonian_evolve_one_step`,
   the "Multi-qubit Pauli H on names[0..nq)" branch, lines ~1965-2039):
   for each World, it reads `nq` separate named coordinates' 0/1 bits,
   packs them MSB-first into a computational-basis index, applies
   `expm_ih_apply` (already-shipped sparse Pauli-sum Taylor evolution,
   unchanged), then unpacks the result back into `nq` separate
   coordinate assignments.
3. **Confirmed by direct execution that reading/writing one tuple's
   positions instead of `nq` separate coordinate names produces
   physically identical results to the shipped path**, to floating-point
   precision: evolved `|0⟩⊗|+⟩` under `H = Z[0] + X[0] + Z[0]*Z[1]`
   (energy-scaled) two ways — (a) via the existing shipped `evolve (q0,
   q1) under H` path, (b) via a hand-written prototype reading/writing a
   single tuple-valued coordinate's two positions using the *same*
   `compile_sparse_pauli`/`expm_ih_apply` primitives. Both gave `q0`
   marginal `{0: 0.6078963648762783, 1: 0.39210363512372154}` — identical
   to full float precision. This is the same physics, only a different
   coordinate storage shape; nothing about the Hamiltonian machinery
   itself needs to change.

## Decision

### Extend `_hamiltonian_evolve_one_step`'s multi-qubit Pauli path to accept a single tuple-valued coordinate, in addition to `nq` separate named coordinates

1. When `evolve psi under H` is called with **one** bind name whose
   Joint-assigned values are tuples of length `nq` (`nq` = the
   Hamiltonian's own inferred qubit count, `op_n_qubits`), dispatch to a
   new code path that reads/writes that one coordinate's tuple positions
   using the *exact same* `compile_sparse_pauli`/`expm_ih_apply`
   primitives the existing `nq`-separate-names path already uses —
   confirmed physically identical by direct execution (Context point 3).
   The existing `nq`-separate-names path is **completely unchanged**.
2. **No new Kernel op, no new syntax, no change to `prepare_selection`,
   `project onto feasible(...)`, or `measure`.** A physicist writes
   exactly the natural single-coordinate form:
   `state psi = project psi0 onto feasible(...); state psi = evolve psi
   under H_obj for t; measure psi`. `Z[i]`/`X[i]`/`Z[i]*Z[j]` (already
   shipped) name which selection position the Hamiltonian acts on.
3. **LINEAR treatment is unaffected** — `evolve` already consumes/moves
   its bound name under the existing generic Call/rebind machinery
   regardless of whether the underlying value happens to be a tuple; no
   `hir.py` change is needed (same "already generic" finding this
   session made repeatedly for LISS-0400/0401).
4. **Disambiguation rule**: if `len(names) == 1` and that coordinate's
   sampled value is an `int` (0/1), the existing single-qubit "legacy"
   path applies unchanged (unaffected by this ADR). If it is a `tuple`,
   the new path applies. If `len(names) > 1`, the existing `nq`-separate-
   names path applies unchanged. No source-level ambiguity: the dispatch
   is entirely determined by what is already bound to the name, which the
   evaluator already inspects for other purposes (e.g. `project`'s own
   `isinstance(..., tuple)` check, ADR 0192).

## Rejected / superseded alternatives

### (Superseded) `unpack_bits` / `pack_bits` bridge — this ADR's own original proposal

Superseded after the Adjudicator asked for the fundamentally correct fix.
A bridge would have left two representations permanently coexisting,
connected by explicit conversion statements a physicist must remember to
insert — exactly the kind of adapter-shaped debt the Adjudicator flagged.
The Decision above needs no bridge at all: one representation (a
tuple-valued coordinate) becomes usable everywhere a physicist would
naturally reach for it, including Pauli-term evolution.

### Redesign `prepare_selection` to bind `N` separate coordinates directly

Rejected — found to be **larger**, not smaller, than first assumed:
Staqex's terminal `measure` reports exactly **one** coordinate
(`Measure.expr: Expr`, singular) with all others discarded via
`tracing_out` (Born partial trace) — there is no "joint measure of
several coordinates as one combined outcome" today. Redesigning
`prepare_selection` into `N` separate coordinates would then require
*also* inventing multi-coordinate joint measurement to recover a single
reportable `n`-bit selection outcome — a change to the terminal-measure/
NLTS core, the highest-risk part of the language to touch, for a problem
this ADR's actual Decision solves without going near it. Left as a
possible **future** ADR only if the Decision above proves insufficient in
practice — not attempted now, and not needed for the S02 gap.

### New per-position addressing syntax

Not needed — `Z[i]` already ships (Context point 1); there is no syntax
gap to close, only an evolution-path gap.

## Non-goals

- Redesigning `prepare_selection` or `project onto feasible(...)`.
- Multi-coordinate joint measurement.
- Rewriting `main_selection.sqx` — a follow-on Feature Issue may adopt
  the unified single-coordinate form once this ships; not required by
  this ADR. (The `objective_hamiltonian` bare-`Z*Z` bug found in Context
  point 1 should be fixed in that same follow-on, using `Z[i]` syntax
  that already ships today, independent of whether this ADR is accepted.)
- Any change to `QubitRegister<N>`/`forEach`.

## Consequences

- Once shipped, S02's selection example (or a successor) can express the
  full hard-constraint/soft-objective workflow as **one** coordinate
  lineage: `prepare_selection` → `project onto feasible(...)` → `evolve
  under H_obj` (now addressing the *actual* selected candidates'
  positions) → `measure` — no separate, disconnected objective pair.
  `top_k_overlap` could become a meaningful, non-zero metric for the
  first time.
- Closes the gap with strictly **less** new surface than either
  previously-considered option: no new op, no new grammar, no touched
  already-shipped Issue's behavior (LISS-0324/0327/0328 unchanged; only
  `_hamiltonian_evolve_one_step`, already-generalizeable internal
  dispatch, gains one more accepted input shape).
- The disclosed `main_selection.sqx` `Z*Z`-site-collision bug (Context
  point 1) is independent of this ADR's acceptance and can be fixed
  separately at any time using already-shipped `Z[i]` syntax.

## Acceptance boundary

Acceptance of this ADR authorizes the tuple-coordinate evolution dispatch
described in Decision as an architecture boundary. It does **not**
authorize:

- Feature Path Red or any Kernel code change.
- Multi-coordinate joint measurement or any `prepare_selection`/`project`
  redesign (explicitly rejected above, not merely deferred).
- Rewriting `main_selection.sqx`.

A Feature Plan investigation (new `LISS-*`) is required before any Red,
exactly as ADR 0204 required for Continuous Lane B.

## Decision history

| Date | Event |
|---|---|
| 2026-08-11 | Proposed (as an `unpack_bits`/`pack_bits` bridge) |
| 2026-08-11 | Adjudicator requested the fundamentally correct fix regardless of size; investigation found a smaller, more correct design (tuple-coordinate Hamiltonian evolution, no new syntax) — this revision |
