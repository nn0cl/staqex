# LISS-0404: Pauli-term Hamiltonian evolution on tuple-valued coordinates

## Metadata

- Local issue ID: LISS-0404
- Status: complete
- Phase: phase-3-refactor
- Type: Feature Path (Kernel — `evaluator.py` only)
- Priority: P1
- Initial planning size: `M`
- Owner / agent: Claude Code
- Parent: [ADR 0205](../architecture/adr/0205-tuple-coordinate-register-bridge.md)
  (Accepted 2026-08-11)
- Depends on: none (additive to shipped, unchanged code)
- Related: `compiler/staqex/runtime/evaluator.py`
  (`_hamiltonian_evolve_one_step`), `compiler/staqex/runtime/sparse_pauli.py`
  (reused unchanged)
- Blocks: a follow-on S02 example rewrite (not this Issue's scope)
- Branch: `feature/liss-0404-tuple-coordinate-evolve`
- GitHub Issue / PR: (opened at Completion)

## Intent

Ship ADR 0205's Decision: let `evolve psi under H` (Pauli-term `H`) accept
a single tuple-valued Joint coordinate (as `prepare_selection` produces),
in addition to the already-shipped `nq`-separate-named-coordinates form.

## Design verification already performed (ADR 0205 investigation, not repeated here)

The ADR's own Context section already contains this Issue's grounding,
confirmed by direct execution before the ADR was presented for
Architecture approval:

1. `Z[i]`/`X[i]`/`Z[i]*Z[j]` indexed Pauli syntax already ships and
   compiles to genuine multi-site `PauliTerm`s (`sparse_pauli.py`,
   `hamiltonian.py::_eval_qubits`).
2. The existing `nq`-separate-names evolve path
   (`evaluator.py:1965-2039`) packs `nq` named coordinates' 0/1 bits into
   a computational-basis index, applies `expm_ih_apply` (unchanged), and
   unpacks the result back into `nq` coordinate assignments.
3. **Verified by direct execution that reading/writing one tuple
   coordinate's positions instead of `nq` separate names, using the
   identical `compile_sparse_pauli`/`expm_ih_apply` primitives, produces
   physically identical results to float precision** — evolved `|0⟩⊗|+⟩`
   under `H = Z[0] + X[0] + Z[0]*Z[1]` (energy-scaled) both ways; both
   gave `q0` marginal `{0: 0.6078963648762783, 1: 0.39210363512372154}`.

## Plan-locked decisions

1. In `_hamiltonian_evolve_one_step`, after the `nq < 0` (grid) branch
   and before the existing `if len(names) < nq: raise KernelError(...)`
   check, insert a new branch: if `len(names) == 1` and the coordinate's
   sampled Joint value is a `tuple`, dispatch to a new
   `_hamiltonian_evolve_tuple_coordinate(joint, src, nq, terms, t)`
   method instead of falling into the `nq`-separate-names path.
   `compile_sparse_pauli` is called once, identically to the existing
   `nq`-separate-names path (same `op_ast`/`env`/`scalars`/`n_qubits`
   arguments) — no duplicated compilation logic.
2. `_hamiltonian_evolve_tuple_coordinate` mirrors the existing
   `nq`-separate-names loop structure exactly (group Worlds by non-`src`
   assigns; build a `2**nq`-length amplitude vector from the tuple's
   positions MSB-first; `expm_ih_apply`; unpack back into a new tuple
   assignment) — the verified-identical prototype from the ADR
   investigation, adapted from a throwaway script into the real method.
3. **Disambiguation is automatic, not source-visible**: a coordinate
   bound to an `int` (0/1) still uses the existing single-qubit legacy
   path or the `nq`-separate-names path (`len(names) > 1`) exactly as
   today; a coordinate bound to a `tuple` uses the new path. No new
   diagnostic code, no new grammar — the dispatch is determined by what
   is already bound to the name, the same signal `project`'s own
   `isinstance(..., tuple)` check already uses (ADR 0192).
4. `len(sample) != nq` (tuple width doesn't match the Hamiltonian's own
   inferred qubit count) fails closed with a clear `KernelError` —
   mirrors the existing `len(names) < nq` message shape.
5. No `hir.py`, `typecheck.py`, parser, or AST change — confirmed
   unnecessary: LINEAR consumption of `evolve`'s bound name already goes
   through the existing generic Call/rebind machinery regardless of the
   underlying value's shape (same "already generic" pattern as
   LISS-0400/0401 this session).

## Explicitly out of scope

- Rewriting `main_selection.sqx` to use the new unified single-coordinate
  form, or fixing its disclosed `Z*Z` same-site bug — a separate,
  follow-on S02 Issue (not blocked by this one; that fix only needs
  already-shipped `Z[i]` syntax).
- `prepare_selection`/`project onto feasible(...)`/`measure` — unchanged,
  per ADR 0205's own Non-goals.
- Multi-coordinate joint measurement — explicitly rejected by ADR 0205,
  not deferred.

## Draft test scenarios (Plan review only, not yet normative)

1. `evolve psi under H` where `psi` is a tuple-valued coordinate (from
   `prepare_selection`) and `H` uses `Z[i]`/`X[i]`/`Z[i]*Z[j]` succeeds
   and produces a real, non-trivial amplitude redistribution (not a
   no-op).
2. Cross-check regression: the result matches an equivalent
   `nq`-separate-named-coordinates `evolve` to float precision, for the
   same initial state and Hamiltonian (the ADR's own verified prototype,
   promoted to an automated test).
3. Tuple width mismatch (`len(sample) != nq`) fails closed with a clear
   diagnostic, not a crash or silent truncation.
4. Existing single-qubit legacy path and `nq`-separate-names path both
   remain byte-for-byte unaffected — full regression sweep, plus a
   targeted re-run of any existing `evolve`-related tests.
5. Full regression sweep unaffected outside new/targeted assertions.

## AI planning record (size M)

- Status: Plan drafted, awaiting Plan approval.
- Confidence: high — the core mechanism was already verified by direct
  execution (not assumption) during the ADR 0205 investigation, including
  a numeric cross-check against the existing shipped path to float
  precision.

## Exit criteria

- [x] Plan approval (2026-08-11).
- [x] Phase 1 Red (2026-08-11):
      `tests/test_liss_0404_tuple_coordinate_hamiltonian_evolve_red.py` —
      2 of 4 tests failed for the stated reason (`Operator needs 2 qubit
      wires, bind has 1` — the tuple-coordinate dispatch did not exist
      yet); the other 2 (width-mismatch fail-closed, existing path
      unaffected) passed immediately, confirming those cases were never
      broken. One test needed a fixture correction *during* Green
      confirmation, not scope drift: an exact-equality assertion hit
      ordinary last-digit floating-point summation-order noise
      (`0.39210363512372154` vs `0.3921036351237215`, ~1e-16 relative)
      between the hand-built `World` list and the real compile→run
      pipeline — switched to `math.isclose`, same assertion intent, not
      weakened.
- [x] Phase 2 Green (2026-08-11): new tuple-coordinate dispatch branch in
      `_hamiltonian_evolve_one_step` + new `_hamiltonian_evolve_tuple_coordinate`
      method, exactly per Plan. All 4 pass.
- [x] Phase 3 Refactor: reviewed diff — matches the Plan exactly
      (`evaluator.py` +83 lines, purely additive, no existing line
      changed outside the one new `if` branch's insertion point); removed
      one unnecessary import alias for readability, no behavior change.
- [x] Full regression sweep re-run: **1450 passed** (2026-08-11), up from
      1446 by exactly the 4 new tests.
- [ ] Completion approval.
