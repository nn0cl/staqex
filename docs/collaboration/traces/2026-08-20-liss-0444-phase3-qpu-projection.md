# LISS-0444 Phase 3 representative QPU projection trace

## Gate and scope

- User approval: Phase 3 representative QPU IR/QASM projection slice approved
  2026-08-20.
- Included: provider-neutral `QpuProgram` and the QASM emitter entry path use
  the source-derived `ScientificSemanticIR`; canonical source node IDs and
  top-level provenance are retained; regression tests are updated.
- Excluded: full AST-derived instruction/shape/lowering migration, symbolic
  IR retirement, evaluator split, provider SDK, live QPU submission, S02
  numerical migration, and solver expansion.
- Required postcondition: independent read-only review and documentation
  reconciliation. A review finding cannot grant a later implementation scope.

## Implementation

- `build_qpu_ir()` accepts the canonical Scientific Semantic IR and projects
  its node IDs and provenance into the provider-neutral boundary.
- Pipeline construction passes the same canonical IR instance to QPU IR.
- QASM's QPU projection entry path builds from Scientific Semantic IR rather
  than the legacy Symbolic IR.
- The QPU provenance test compares the complete node-ID and provenance
  sequences with the canonical IR.

## Verification

- Bounded Phase 3 regression: `47 passed` before the final CQFT assertion
  correction; `32 passed` after the final targeted correction.
- Full regression after final correction: `1630 passed in 293.09s`.
- No provider, network, live-QPU, S02, or solver operation was performed.

## Independent review disposition

- Fresh read-only review: `NOT READY` for the complete consumer-wide Phase 3
  migration, with no implementation or approval authority.
- Accepted as remaining migration work: AST-derived instruction/shape and QASM
  fallback paths, Symbolic IR retirement, instruction-level provenance, QASM
  canonical consistency validation, and stronger consumer-wiring tests.
- Deferred from this approved representative slice: those findings require a
  separately bounded migration batch because they change multiple consumers
  and retirement behavior. They are recorded as open work rather than hidden
  behind the representative projection result.
- Documentation correction applied: approval and current partial Phase 3
  status are now recorded in WP-0107, LISS-0444, and the open-work register.
- Review-loop terminal state: `ABORT` for the broader migration continuation;
  the approved representative slice is verified, but the next consumer-wide
  batch requires an explicit bounded scope decision.

## Final correction and re-review

- Added a complete canonical semantic fingerprint and emitter-side mismatch
  rejection for mutated node fields, relations, and semantic metadata.
- Added an integration test proving `projection_error` yields empty QASM and
  does not enter the legacy AST fallback.
- Final independent re-review: `READY` for this approved representative batch;
  review loop terminal state `COMPLETE`.
- Consumer-wide AST authority migration, fallback retirement, Symbolic IR
  retirement, exhaustive decomposition coverage, and the individually named
  `lowering_policy`, `explicit_evolution`, and `binder_lowering` consumers
  remain deferred.

## Boundary and next decision

The representative projection is complete, but WP-0107 is not complete. The
next implementation slice must specify its consumer set, retirement proof,
instruction-level provenance contract, and acceptance tests before work
continues. Provider SDK, live QPU submission, and S02 numerical migration stay
outside this Issue.
