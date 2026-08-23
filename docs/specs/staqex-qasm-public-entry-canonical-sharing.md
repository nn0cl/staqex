# Staqex QASM Public Entry Canonical Sharing Specification

| Field | Value |
|---|---|
| Status | **Phase 2 Green complete — independent review COMPLETE** |
| Issue | [LISS-0446](../issues/LISS-0446-qasm-public-entry-canonical-sharing.md) |
| WorkPlan | [WP-0109](../work-plans/WP-0109-qasm-public-entry-canonical-sharing.md) |
| Authority | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## [DESIGN CHECK]

- **Scope and expected behavior:** public local QASM entry points must preserve
  the compile-owned `ScientificSemanticIR` when one already exists; a source or
  path facade must compile once and pass its canonical projection downstream.
- **Inspected context:** LISS-0445/WP-0108, ADR 0211, `QASM3Emitter`, backend
  and public QASM facades, `codegen_qasm`, CLI emit paths, tests, and spec
  verification suites.
- **Boundary:** `ScientificSemanticIR` remains the semantic authority;
  `QpuProgram` remains the provider-neutral executable projection; QASM is an
  output adapter. No AST cache or global semantic cache is permitted.
- **Applicable constraints:** physicist-first source fidelity, explicit
  `Realize`, State safety, terminal `Measure`, fail-closed rejection, no
  provider/live-QPU/S02/solver work.
- **Ambiguity boundary:** whether unit-only compatibility APIs should become
  strict and require a compiled projection is deferred; the compatibility
  option below preserves existing callers without hiding ownership in state.
- **Review lenses:** canonical authority, projection conservation, migration
  safety, API/ownership boundary, phase discipline, and evidence hygiene.

## Normative requirements

1. A facade receiving a compile-owned `ScientificSemanticIR` must pass that
   same object to QPU/QASM projection and must not rebuild it.
2. Source/path convenience facades must retain the `CompileResult` long enough
   to pass `compiled.scientific_semantic_ir` to the emitter.
3. Unit-only compatibility calls may create one source-derived projection for
   that invocation when no compile result is available, but may not store it in
   the AST, a module-global cache, or an implicit process cache.
4. All QASM output and rejection behavior must remain unchanged except for
   eliminating duplicate semantic construction.
5. Live QPU submission, provider adapters, dynamic-QPU semantics, S02, solver,
   and unrelated QASM fallback retirement are outside this Spec.

## Public entry inventory

| Entry | Current ownership | Proposed disposition | Key impact |
|---|---|---|---|
| `QASM3Emitter.emit_unit` | accepts `CompilationUnit`; optional IR now exists | retain explicit IR parameter | direct compile-owned path is available |
| backend `emit_openqasm3` | unit-only wrapper | add/pass optional IR | wrapper currently rebuilds |
| `codegen.openqasm.emit_openqasm3` | delegates to backend wrapper | forward optional IR | compatibility wrapper |
| `OpenQASM3Generator.generate_detailed` | unit-only facade | accept/forward optional IR | primary public API |
| `OpenQASM3Generator.generate` | delegates to detailed | accept/forward optional IR | preserve output API |
| `generate_from_source` | compiles then discards IR | pass compile-owned IR | source convenience path |
| `StaqexCompiler.compile_to_qasm3` | compiles path then discards IR | pass compile-owned IR | path convenience path |
| `generate_openqasm3` | unit-only convenience wrapper | forward optional IR | compatibility wrapper |
| CLI `cmd_run` / `cmd_emit_qasm` | compile then pass unit only | pass compile-owned IR | local delivery path |
| `live_submit` | compile then emit unit | defer | live/provider boundary excluded |
| `emit_dynamic_qpu_qasm3` | direct dynamic-lane AST emitter | explicit exclusion | dynamic-QPU semantics require a separate boundary decision |
| `emit_ch0` | separate CH0 QASM subset emitter | explicit exclusion | separate owner/subset contract; no change in this Issue |

## Acceptance boundary

- Phase 1 Red proves every listed local entry and explicit exclusion is
  inventoried and that a compile-owned projection is not rebuilt at each
  included facade.
- Phase 2 Green passes the projection through the backend, codegen facade,
  source/path helpers, and CLI without changing QASM semantics.
- Phase 3 verifies the compatibility caller matrix, no-cache behavior, full
  regression, and independent review.

## Observable acceptance matrix

| Scenario | Required observation |
|---|---|
| compile-owned IR passed to each included facade | `build_scientific_semantic_ir` is not called; the same IR object reaches the emitter |
| source/path/CLI convenience flow | source is compiled once; the resulting `CompileResult.scientific_semantic_ir` is forwarded |
| unit-only call with `semantic_ir=None` | at most one local canonical build; no AST or process cache |
| `generate()` delegates to `generate_detailed()` | no second canonical build and identical `EmitResult` behavior |
| valid State program | QASM payload, terminal `Measure`, and State provenance remain unchanged |
| bare `Limit` | same rejection code; empty QASM/circuit gates/instructions and no allocation |
| explicit `Realize` | same finite policy/provenance and output behavior as before |
| capability/rejection input | same diagnostic code and no partial executable artifact |
| mismatched unit and supplied IR | explicit caller-contract rejection or a documented pairing token; never silent mixed-source emission |

The last row is an API ownership contract to be fixed during Phase 1 Red; it
must not be resolved by rebuilding the IR in the facade.

## Approval state

This Spec was accepted for Phase 1 Red and the user separately approved Phase
2 Green implementation. It does not authorize technology selection, live
submission, or a new architecture. Phase 2 implementation is complete; the
independent review loop reached `COMPLETE`; no subsequent phase is approved.
