# ADR 0222: QASM canonical-input fail-closed boundary

## Status

Accepted — Adjudicator approved `ADR 0222 Architecture / LISS-0554 Phase 0
acceptance 承認` on 2026-09-14.

## Context

QASM is an output adapter over the provider-neutral canonical `QpuProgram`.
`ScientificSemanticIR` is the semantic authority. The current
`QASM3Emitter.emit_unit()` path accepts a raw `CompilationUnit` without a
compile-owned semantic projection and rebuilds `ScientificSemanticIR` from the
AST. That allows an artifact producer to proceed without proving canonical
ownership and permits source meaning to be interpreted twice.

## Decision

`QASM3Emitter.emit_unit()` must fail closed immediately when
`semantic_ir is None`. It returns an empty rejection envelope with
`E_QPU_CANONICAL_PROVENANCE` before AST source-shape inspection, QPU
projection, routing, target metadata, gate creation, allocation, or QASM
rendering.

The public unit-only compatibility facade is a separate boundary. It may build
one invocation-local `ScientificSemanticIR` from the unit, without storing or
caching it, and must then pass that object explicitly to `emit_unit()`. The
facade is the only owner of this compatibility build; the emitter never
rebuilds missing authority.

When a projection is supplied, its existing source-unit identity check remains
mandatory. A mismatched projection is rejected with the same empty envelope.
Canonical public source/path/CLI facades must pass the compile-owned
`ScientificSemanticIR`; their accepted QASM bytes and diagnostics remain
unchanged.

The AST lowerer remains available only to explicitly approved compatibility
callers. Dynamic QASM, CH0, provider/live-QPU submission, and lowerer removal
are separate boundaries.

## Acceptance contract

1. Raw parsed unit + no semantic IR → `ok=False`,
   `E_QPU_CANONICAL_PROVENANCE`, empty QASM, empty gates, no allocation.
2. Supplied IR from another unit → same rejection and no partial artifact.
3. Unit-only public facade → at most one invocation-local canonical build,
   followed by the same accepted QASM behavior and bytes.
4. Direct emitter missing-IR path never calls `build_scientific_semantic_ir`,
   `build_qpu_ir`, routing, or the AST lowerer.

## Consequences

- QASM cannot fabricate canonical meaning from an unowned AST.
- Source/path convenience APIs must retain and forward their compile result.
- Unit-only compatibility calls become explicitly unsupported at this emitter
  boundary rather than silently rebuilding semantic authority.
- No provider, AWS, live-QPU, Rust, solver, or language-syntax decision is
  introduced.

## Approval boundary

This ADR records Architecture approval and LISS-0554 Phase 0 acceptance.
Phase 1 Red, Phase 2 Green/Implementation, and Phase 3 Refactor require
separate typed approvals.
