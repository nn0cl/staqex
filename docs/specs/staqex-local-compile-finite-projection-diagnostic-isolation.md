# Staqex local compile and finite-projection diagnostic isolation

| Field | Value |
|---|---|
| Status | Proposed — Phase 0 acceptance and ADR 0220 Architecture approval required |
| Owner | WP-0161 / LISS-0552 |
| Depends on | LISS-0551 complete |
| Architecture proposal | [ADR 0220](../architecture/adr/0220-local-compile-and-finite-projection-diagnostic-isolation.md) |

## Purpose

Preserve ideal/local source acceptance independently from optional finite-QPU
projection while keeping linear resources hard, migration syntax honest, and
every target artifact fail-closed. This specification reconciles the six
active-Red nodes transferred from LISS-0551 without erasing diagnostics or
making QASM readiness synonymous with `CompileResult.ok`.

## Observed Baseline

- `QSEM_FINITE_EVIDENCE_MISSING` and
  `QSEM_APPROXIMATION_OBLIGATION_MISSING` are not members of `HARD_CODES`; by
  themselves they already coexist with `CompileResult.ok == True`.
- All six residual nodes fail because `LINEAR_IMPLICIT_DISCARD` is hard.
- The three empty-domain fixtures additionally retain the migration-only
  `EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED` spelling.
- Current-source variants using explicit propagator evolution and explicit
  `Measure ... tracing_out ...` compile locally without weakening linear-use
  policy.
- A locally accepted `inner`/`outer` source with QSEM evidence diagnostics can
  currently emit measure-only QASM. That is an unsafe missing-projection
  conservation check, not permission to promote the QSEM diagnostics to local
  compile errors.

## Normative Boundary

### Local compile

1. `CompileResult.local_ok` is the source/kernel acceptance signal.
2. `CompileResult.ok` remains a compatibility alias for `local_ok`.
3. Syntax, typing, dimensions, lexical scope, effects, and linear-resource
   diagnostics in `HARD_CODES` make both properties false.
4. The two generic QSEM evidence diagnostics remain visible and non-hard at
   the local compile surface. The `CompileResult` copy of each carries
   `severity = "advisory"`,
   `phase = "quantum-semantic-lowering"`, and
   `blocking_scope = "finite-projection"`. The pure QSEM lowering result stays
   authoritative and is not mutated to make local compilation succeed.
5. A caller must not infer QASM/QPU readiness from either local property.

### Linear and algebraic source

1. `LINEAR_IMPLICIT_DISCARD` remains hard; this Issue does not suppress it.
2. `inner(phi, psi)` and `outer(psi, phi)` are algebraic, non-measuring uses.
   They do not discharge the linear lifetime of the named states.
3. A fixture that finishes with other values must explicitly dispose of those
   states through the accepted terminal `tracing_out` surface.
4. This bounded Issue does not decide whether a future physical realization of
   an inner product is destructive, approximate, or multi-copy.

### Empty-domain identity and Evolve

1. Empty `Sigma`/`Pi` remains an identity plus
   `EMPTY_BINDER_DOMAIN_WARNING`, not a hard compile error.
2. The fixture uses current explicit evolution: dimensioned `scale`, `dt`,
   `U = exp(-i * (scale * H) * dt / hbar)`, and
   `Evolve() { U * psi }.run()`.
3. The accepted `H` binding remains the empty-domain identity so the existing
   acting-space and matrix assertions stay authoritative.
4. No-register execution/QASM still rejects with
   `IDENTITY_ACTING_SPACE_UNDETERMINED`; an explicit register permits local
   finite matrix materialization.
5. The retired Hamiltonian shortcut is not restored or reclassified.

### Finite target projection

1. QPU IR projection, not the QASM adapter, owns semantic-operation coverage
   and target-readiness classification.
2. Every retained canonical semantic operation must be represented by a
   meaning-preserving finite projection or produce a deterministic projection
   error.
3. An unprojected `inner`, `outer`, or other unsupported algebraic operation
   uses `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` with reason
   `semantic_operation_projection_unavailable` and source node IDs.
4. QASM consumes the QPU projection result. On rejection it returns empty QASM,
   zero gates/instructions, `allocation_started is False`, no allocated
   qubits, and no partial program.
5. LISS-0554 remains distinct: it rejects a missing or mismatched
   compile-owned canonical input. LISS-0552 rejects a present canonical input
   whose operations are not conservatively projected.

## Six-node Fixture Matrix

| Existing node family | Phase 1 fixture correction | Preserved assertion/result |
|---|---|---|
| empty Sigma warning | explicit dimensioned propagator | warning present; local compile succeeds |
| empty Pi warning | explicit dimensioned propagator | warning present; local compile succeeds |
| explicit-register identity | same, keeping `Operator H` as identity | acting space 4; 16×16 identity matrix |
| paper inner | terminal `tracing_out phi, psi` | `inner(Var(phi), Var(psi))`; runtime result 1.0 |
| paper outer | terminal `tracing_out psi, phi` | paper ket/bra labels preserve `outer` AST |
| operator inner/outer | terminal `tracing_out psi, phi` | state/operator type boundary compiles |

No Python assertion is removed or relaxed. The source fixture changes happen
in Phase 1 before implementation, so Phase 2 does not modify reviewed tests.

## Acceptance Scenarios

### A — ideal/local acceptance stays available

Given valid source whose only diagnostics are the two generic QSEM evidence
obligations, when it is compiled locally, then `local_ok` and `ok` are true and
the tagged advisory diagnostics remain inspectable.

### B — local hard failures remain hard

Given the same source with an unconsumed linear state, when it is compiled,
then `LINEAR_IMPLICIT_DISCARD` remains present and both local acceptance
properties are false.

### C — current Evolve spelling preserves empty identity

Given empty Sigma/Pi and the explicit propagator fixture, when local compile
and finite binder lowering run, then only the warning remains, `H` is the fold
identity, and explicit acting-space evidence controls materialization.

### D — algebraic borrow is explicit at lifetime end

Given paper or function-shaped `inner`/`outer`, when the remaining named states
are explicitly traced out at terminal measurement, then local compile succeeds
without pretending the algebraic operation measured those states.

### E — local success is not target success

Given locally accepted `inner`/`outer` source and a compile-owned canonical IR,
when QPU/QASM projection is requested without a supported finite projection,
then projection rejects with the named code/reason/provenance and leaves no
artifact or allocation.

### F — canonical-input absence remains separately owned

Given no canonical IR or an IR belonging to another compilation unit, when
QASM is requested, then LISS-0554's canonical-provenance contract applies;
LISS-0552 does not rebuild meaning from AST.

## Phase Plan

### Phase 1 Red

- Correct the six test source fixtures according to the matrix while
  preserving their assertions.
- Add focused contracts for `local_ok`, exact QSEM advisory metadata, hard
  linear diagnostics, and atomic QPU rejection for retained unsupported
  semantic operations.
- Remove a six-node active-Red exclusion only after that exact node passes;
  new target-boundary tests must fail for the missing implementation.

### Phase 2 Green

- Add `CompileResult.local_ok` and keep `ok` as its compatibility alias.
- Add the exact metadata when the two QSEM diagnostics are classified for the
  local `CompileResult`; preserve the pure lowering result unchanged.
- Add semantic-operation conservation/rejection to QPU IR projection and make
  QASM consume that result; no adapter-local interpretation of physics.

### Phase 3 Refactor

- Centralize diagnostic metadata and projection rejection construction only
  where this removes real duplication.
- Preserve public codes, source identity, diagnostic ordering, and artifact
  bytes for supported neighboring inputs.

## Verification Profile

- six exact transferred nodes and new focused acceptance tests;
- `inner` runtime value 1.0 and explicit-register 16×16 identity;
- neighboring hard linear-use tests and strict Evolve migration tests;
- supported canonical measure/gate QASM byte compatibility;
- unsupported semantic-operation rejection envelope and LISS-0554 canonical
  input guards;
- full blocking pytest, Spec Verification, active-Red lifecycle, document
  lifecycle, coverage ledger, compileall, and diff checks.

## Exclusions

- provider SDKs, credentials, network, live QPU, target selection, and AWS;
- new language syntax, automatic finiteization, or inferred approximation;
- physical inner-product algorithm selection or multi-copy state semantics;
- global replacement of diagnostic dictionaries with a new type;
- changing accepted target behavior unrelated to the six nodes and their
  nearest fail-closed QPU boundary.
