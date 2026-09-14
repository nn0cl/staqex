# LISS-0552 Phase 0 acceptance / Architecture review packet

## Review Packet

- Scope: six residual fixture nodes, local compile acceptance, QSEM advisory
  evidence, linear lifetime, and the nearest finite-QPU projection boundary
- Canonical proposal:
  `docs/specs/staqex-local-compile-finite-projection-diagnostic-isolation.md`
- Architecture proposal:
  `docs/architecture/adr/0220-local-compile-and-finite-projection-diagnostic-isolation.md`
- Current phase: Phase 0 Architecture review
- Requested approval type: Architecture approval plus Phase 0 acceptance
- Implementation allowed: no
- Post-review required: Phase 1 remains a distinct approval

## Evidence Re-read

- ADR 0212 and the Quantum Semantic IR contract
- explicit blackboard Evolve specification and ADR 0209
- operator-algebra and inner/outer runtime specifications
- `CompileResult.ok`, `HARD_CODES`, QSEM lowering, HIR linear verifier, QPU IR,
  and QASM emitter
- six exact active-Red nodes and LISS-0554 canonical-input guard

## Findings and Dispositions

- Apply: QSEM evidence codes are already non-hard, so changing only
  `HARD_CODES` cannot fix the six nodes.
- Apply: retain hard linear diagnostics and make lifetime disposal explicit in
  fixtures through `tracing_out`.
- Apply: migrate empty-domain fixtures to the accepted explicit propagator;
  do not restore the retired Hamiltonian shortcut.
- Apply: name local acceptance as `local_ok`, retain `ok` as an alias, and tag
  the two QSEM advisories with phase and blocking scope.
- Apply: enforce semantic-operation conservation in QPU IR, with QASM consuming
  the rejection instead of interpreting source meaning.
- Apply: keep LISS-0554 separate for absent/mismatched canonical input.
- Out of scope: provider SDKs, live QPU, physical inner-product algorithms,
  automatic finiteization, and a global diagnostic type migration.

## Deterministic Evidence

- Current six-node diagnostic inventory reproduced: all six include
  `LINEAR_IMPLICIT_DISCARD`; all six include both generic QSEM evidence codes;
  the three empty-domain nodes also include the retired Evolve diagnostic.
- Explicit dimensioned Evolve candidate: local compile succeeds with only
  `EMPTY_BINDER_DOMAIN_WARNING`.
- Paper inner with terminal tracing-out: local compile and local runtime
  succeed; measured value is 1.0.
- Paper outer and operator-boundary candidates with terminal tracing-out:
  local compile succeeds with only the two QSEM advisory codes.
- Neighbor target check: those canonical `inner`/`outer` inputs currently emit
  non-empty measure-only QASM, proving the operation-conservation Red gap.
- No test or production file changed during Phase 0.

## Failure Scenarios Reviewed

- QSEM advisories are promoted to source errors and ideal meaning disappears.
- Linear discard is softened merely to make local compile green.
- Retired Evolve syntax is treated as current source.
- QSEM diagnostics are hidden after local success.
- QASM silently drops unsupported canonical operations and emits the remaining
  measure instructions.
- QASM adapter grows AST/physics policy instead of consuming QPU IR rejection.
- LISS-0552 and LISS-0554 claim the same missing-canonical-input failure.

## Isolation and Blocker

- Configured review isolation is `same_context`, weaker than
  `separate_context`.
- LISS-0552 is size L, so the authoring model cannot claim an independent
  same-context approval. This packet is evidence for the human Adjudicator.
- Resolution: the Adjudicator accepted ADR 0220 and the companion acceptance
  specification on 2026-09-13. The Phase 0 blocker is cleared.
- Phase 1 remains separately gated; this approval does not authorize test
  changes or implementation.

## Adjudicator Decision

Approved on 2026-09-13 with the typed decision:
`ADR 0220 Architecture / LISS-0552 Phase 0 acceptance 承認`.

Next approval required: `LISS-0552 Phase 1 Red 承認`.
