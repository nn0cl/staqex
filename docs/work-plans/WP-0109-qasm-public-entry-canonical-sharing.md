# WP-0109: QASM Public Entry Canonical Sharing

| Field | Value |
|---|---|
| Status | **Phase 2 Green complete — independent review COMPLETE** |
| Issue | [LISS-0446](../issues/LISS-0446-qasm-public-entry-canonical-sharing.md) |
| Specification | [QASM Public Entry Canonical Sharing](../specs/staqex-qasm-public-entry-canonical-sharing.md) |
| Parent | [WP-0108](WP-0108-scientific-semantic-consumer-migration.md) |
| ADR | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## Recommended execution order

1. Independently review this proposed Spec/WP and the public-entry inventory.
2. Phase 1 Red: add fixed ownership/no-rebuild tests only.
3. Phase 2 Green: propagate the existing `ScientificSemanticIR` through local
   QASM facades and source/path/CLI convenience flows.
4. Phase 3 Refactor: simplify compatibility signatures only if regression and
   independent review justify it.

## Proposed Phase 1 Red scope

- `tests/test_liss_0446_qasm_public_entry_red.py`;
- any fixed fixture required by that test;
- this Issue/Spec/WP and review/trace records;
- no production implementation, provider, network, live QPU, S02, solver, or
  test weakening.

## Proposed Phase 2 Green scope

- `compiler/staqex/backend/qasm/emitter.py`;
- `compiler/staqex/codegen/openqasm.py`;
- `compiler/staqex/codegen_qasm.py`;
- `compiler/staqex/cli.py`;
- focused tests and documentation for this Issue.

`compiler/staqex/live_submit.py` is explicitly excluded and requires its own
provider/live-QPU boundary decision.
`compiler/staqex/backend/qasm/dynamic_emitter.py` and
`compiler/staqex/backend/qasm/ch0_emit.py` are inventoried explicit exclusions
with separate ownership/subset contracts.

## Acceptance conditions

- source/path facade compilation retains and forwards the canonical IR;
- all local public wrappers forward the optional IR without rebuilding it;
- unit-only compatibility calls perform at most one local build and do not
  cache the result in AST or process state;
- Red tests measure compile/build call count and object identity for every
  included facade, not only rendered QASM text;
- QASM text, rejection codes, State/Measure behavior, and Realize boundaries
  remain unchanged;
- bare `Limit`, explicit `Realize`, capability rejection, and no-artifact
  behavior are asserted at included entry points;
- focused, related, and full regression pass, followed by independent review.

## Stop conditions

Stop for user/Architecture judgment if the design requires breaking the public
API, changing `ScientificSemanticIR` authority, adding a cache or new
technology, touching live submission/provider adapters, or altering QASM
fallback/Realize semantics.

The pairing contract for a caller-supplied `CompilationUnit` and
`ScientificSemanticIR` must be fixed during Phase 1 Red. A mixed-source pair
must reject explicitly or carry a deterministic pairing token; rebuilding the
IR is not an acceptable fallback.

Phase 1 Red and the separately approved Phase 2 Green implementation are
complete. The independent review loop reached `COMPLETE`; no subsequent phase
is approved.

## Phase 3 Refactor disposition

Phase 3 was evaluated using the recommended conservative disposition:

- no production refactor is justified by the current implementation;
- explicit `semantic_ir` parameters are retained because they expose canonical
  ownership rather than hiding it behind a convenience abstraction;
- the three known LISS-0445 Red failures prevent claiming a full Phase 3 Green
  baseline and remain outside WP-0109;
- Phase 3 is deferred, with no new implementation or scope expansion.
