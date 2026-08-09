# LISS-0391: OpenQASM 3 emission for the Dynamic QPU lane

## Metadata

- Local issue ID: LISS-0391
- Status/phase: **Green/Refactor complete** (2026-08-10) — proceeding to
  completion without a mid-work pause per Adjudicator direction
  ("完成まで止めないので", given together with the Decision 4 choice)
- Type: Feature Path (Kernel — new QASM lowering path; no language
  surface change, no Kernel execution semantics change)
- Priority: P2
- Initial planning size: `L`
- Owner / agent: Claude Code
- Program: [ADR 0201](../architecture/adr/0201-openqasm-dynamic-lane-emission.md)
  (Accepted 2026-08-10, PR [#496](https://github.com/nn0cl/staqex/pull/496))
- Parent: ADR 0201
- Depends on: LISS-0387/0388/0389/0390 (all **complete**) — the Dynamic
  lane's Kernel meaning this emission path re-expresses in QASM3
- Related: `compiler/staqex/backend/qasm/emitter.py`
  (`QASM3Emitter`, Static QPU surface, unaffected by this Issue);
  `compiler/staqex/backend/qasm/circuit.py` / `lower.py` (confirmed
  Static-QPU-only, not extended by this Issue — see Plan-locked
  decision 1)
- Blocks: none
- Branch: `feature/liss-0391-openqasm-dynamic-emission`
- GitHub Issue / PR: none yet

## Intent

Implement ADR 0201: emit OpenQASM 3 text for a `dynamic qpu` block's
mid-circuit `measure`, `match`, and `reset` constructs, using QASM3's own
native vocabulary (classical `bit`, `if`, `reset`) — available whenever
the program compiles, independent of any Fake profile gate, making no
`physical_execution_claimed` claim.

## Explicitly out of scope

- Any change to the Static QPU emitter/lowering/routing pipeline
  (`emitter.py`/`lower.py`/`circuit.py`/`router.py`) — confirmed
  structurally Static-only; this Issue does not extend or touch it.
- Physical qubit routing / topology for Dynamic-lane wires (ADR 0201 did
  not decide this; a dynamic block's wires are emitted as named QASM3
  qubits directly, unrouted — routing is Static-QPU-surface machinery
  for large physical circuits, not applicable to the Dynamic lane's
  local, block-scoped wires).
- Live provider submission of the emitted text (ADR 0127 boundary,
  untouched).
- Any change to Kernel execution (ADR 0200), capability law (ADR
  0199/0388/0390), or `JobResult`/`dynamic_trace` (ADR 0198/0389).

## Plan-locked decisions

1. **Separate lowering path, no shared-IR extension:** a new module
   (`compiler/staqex/backend/qasm/dynamic_emitter.py`) walks the first
   `DynamicQpuStmt`'s AST directly and emits QASM3 text, **not** through
   `Circuit`/`Gate`/`route_circuit` — those are confirmed Static-QPU-only
   (flat gate list, no conditional-block representation, physical
   routing machinery that doesn't apply to Dynamic-lane's local wires).
   This matches ADR 0201's own deferral of "exact Circuit-IR
   conditional-block representation" by not forcing the question at all.
2. **Wire naming:** Dynamic-lane wires keep their **source names** as
   QASM3 qubit identifiers (`qubit q;`, not `q[i]` indices) — more
   physicist-readable than the Static emitter's generic indexing, and
   avoids inventing an index-assignment scheme this Issue doesn't need.
3. **Mapping (ADR 0201 Decision 3):**
   - `state wire = |0>` → `qubit wire;` declaration.
   - `Controller<T> c = measure wire` → `bit c; c = measure wire;`.
   - `match c { pattern => { … } … }` → one `if (c == pattern) { … }`
     block per arm (general for any arm count, not limited to two-arm
     `if`/`else`).
   - `reset wire` → `reset wire;` (QASM3 native).
   - `apply(OP, wire)` inside arms/block → QASM3 gate call, reusing
     `emitter.py`'s existing `_QASM_GATE_NAMES` mapping (H/X/Y/Z/CX/RX/RY/RZ)
     for consistency with the Static emitter's vocabulary.
4. **Availability (ADR 0201 Decision 4):** emission requires only
   successful compilation (`compiled.unit is not None`, no blocking
   `HARD_CODES` diagnostics reached the dynamic block) — independent of
   `dynamic_fake_profile`/any Host settings gate.
5. **No physical claim:** the new emission function returns text +
   `EmitResult`-shaped metadata; nothing in this path reads or sets
   `physical_execution_claimed` anywhere.

## Acceptance reference

[`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md) §
"Acceptance scenarios — OpenQASM dynamic-lane emission (ADR 0201,
LISS-0391)".

## Exit criteria

- [x] Plan drafted, proceeding per Adjudicator "don't stop" direction
      (2026-08-10).
- [x] Phase 1 Red (2026-08-10):
      `tests/test_liss_0391_openqasm_dynamic_emission_red.py` — 3 of 4
      tests failed for the stated reason (`ModuleNotFoundError`, the
      module did not exist yet). The 4th
      (`test_static_qasm_emitter_is_unaffected`) failed for an unrelated
      reason on first write (an invalid Staqex source fixture, a test
      authoring mistake caught and fixed by copying a known-good fixture
      from `test_qpu_ir_lowering_green.py` before Green began) — not a
      LISS-0391 defect.
- [x] Phase 2 Green (2026-08-10): new module
      `compiler/staqex/backend/qasm/dynamic_emitter.py`
      (`emit_dynamic_qpu_qasm3`) — a separate lowering path, not routed
      through `Circuit`/`Gate`/`route_circuit`. One implementation bug
      found and fixed during Green (not Red): `_emit_call` initially
      treated the Call's callee name as the gate operator, but
      `apply(X, wire)`'s operator is `args[0]`, not the callee (`apply`
      itself) — fixed once, confirmed against the actual `apply(...)`
      call shape. All 4 tests pass; no test edited to force it.
- [x] Phase 3 Refactor: reviewed the new file — clean, no changes needed.
- [x] Spec (`staqex-dynamic-qpu-lane.md`) synced with the real Gherkin;
      status table updated.
- [x] Full regression sweep re-run: **1391 passed** (2026-08-10), up from
      1387 by exactly the 4 new tests. Static QPU `QASM3Emitter` /
      `lower_unit_to_circuit` / `Circuit` confirmed untouched (no diff to
      those files).
- [ ] Completion approval.
