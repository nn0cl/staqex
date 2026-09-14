# ADR 0221: Symbolic compatibility view authority boundary

## Status

Accepted — Adjudicator approved `ADR 0221 Architecture / LISS-0553 Phase 0
acceptance 承認` on 2026-09-14.

## Context

The accepted LISS-0489 and LISS-0500 contracts make
`ScientificSemanticIR`/`SemanticInspectionResult` the canonical meaning and
inspection authority. Existing non-explicit callers still need the historical
`symbolic_ir` dictionary shape. The current compile result therefore exposes a
derived dictionary, while the old LISS-0476 Red assertion requires it to be
absent.

## Decision

During the bounded migration window, `CompileResult.symbolic_ir` may be
present for non-explicit exact/symbolic compilation only as a derived,
diagnostic-only compatibility view.

The view MUST:

1. identify `ScientificSemanticIR` as its canonical authority;
2. preserve compile-owned source node identity and semantic fingerprint;
3. retain only inspection/compatibility data and no executable or finite
   artifact;
4. never authorize execution, `Realize`, allocation, QPU/QASM projection, or
   collapse; and
5. be built without a direct AST semantic walk or a call to
   `build_symbolic_ir(unit)`.

The old `symbolic_ir is None` assertion is superseded only for this narrow
reason. It is replaced by positive authority/provenance checks and negative
authorization/artifact checks. Explicit legacy callers remain isolated. Final
removal of the compatibility field requires a separate consumer inventory,
deprecation/removal decision, and migration evidence.

## Consequences

- Existing dictionary consumers continue to work during migration.
- Canonical authority is testable rather than inferred from output equality.
- A compatibility dictionary cannot silently become an execution or target
  artifact input.
- LISS-0553 does not change finiteization, QASM, provider, AWS, Rust, or
  simulator execution behavior.

## Rejected alternatives

- Immediate deletion of `symbolic_ir`: breaks remaining consumers without a
  caller inventory and exceeds this issue's bounded scope.
- Keeping the old absence assertion: conflicts with the accepted derived-view
  contract.
- Rebuilding the dictionary directly from AST: recreates the parallel semantic
  authority rejected by LISS-0489/LISS-0500.

## Approval boundary

This ADR records Architecture approval and LISS-0553 Phase 0 acceptance. It
grants no permission to change tests or production code. Phase 1 Red, Phase 2
Green/Implementation, and Phase 3 Refactor require their own typed approvals.
