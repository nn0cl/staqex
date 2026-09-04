# LISS-0446: QASM Public Entry Canonical Sharing

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor complete; public QASM ownership slice closed** |
| Discovered in | [LISS-0445](LISS-0445-scientific-semantic-consumer-migration.md) Phase 2 Green review |
| Proposed Spec | [QASM Public Entry Canonical Sharing](../specs/staqex-qasm-public-entry-canonical-sharing.md) |
| Proposed WorkPlan | [WP-0109](../work-plans/WP-0109-qasm-public-entry-canonical-sharing.md) |
| Owner | Staqex compiler / QASM boundary maintainer |
| Related ADR | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## Reason for follow-up

The direct `QASM3Emitter.emit_unit(..., semantic_ir=...)` path now consumes a
compile-owned `ScientificSemanticIR`. Public convenience facades such as
`emit_openqasm3()` and `OpenQASM3Generator.generate_detailed()` still accept a
`CompilationUnit` without retaining the `CompileResult` projection, so they may
rebuild semantic IR. LISS-0445 deliberately did not broaden its binder slice
to redesign those ownership and API boundaries.

## Planned scope

- define how public QASM facades receive or retain compile-owned semantic IR;
- preserve one canonical projection per compile and no hidden cache;
- cover direct and file/source convenience entry points;
- retain fail-closed provenance, State/Measure, Limit/Realize, and rejection
  behavior.

## Exclusions

- no provider SDK or live QPU submission;
- no S02 numerical migration or solver;
- no Algorithm Plan or H1 migration;
- no implementation until a separate Spec/WP review and typed approval.

## Exit conditions

- reviewed Spec/WP and explicit implementation approval;
- every public QASM entry point has an explicit canonical ownership contract;
- no entry point silently rebuilds or caches semantic IR;
- focused and full regression plus independent review are complete.

Dynamic QPU QASM (`emit_dynamic_qpu_qasm3`) and the CH0 QASM subset
(`emit_ch0`) are explicitly inventoried exclusions with separate owners and
contracts; they are not silently counted as migrated by this Issue.

## Investigation result

The impact inventory and bounded design are recorded in the proposed Spec and
WP-0109. The recommended direction is explicit propagation of the existing
`ScientificSemanticIR` through public QASM facades. Source/path convenience
facades should compile once and pass the resulting canonical projection;
unit-only compatibility APIs may build one projection for that invocation when
the caller has no `CompileResult`. No AST field or global cache is proposed.

Phase 1 Red and the user-approved Phase 2 Green implementation are complete
and recorded. The independent review loop reached `COMPLETE` with no remaining
review blocker.

## Phase 3 Refactor assessment

The Phase 3 refactor was assessed after Phase 2 completion. No behavior-
preserving simplification is justified: the explicit `semantic_ir` parameters
make canonical ownership visible, while collapsing the public signatures would
make the ownership boundary less legible. The formerly related LISS-0445 Red
cases are now separately recorded; unsupported explicit-evolution rejection is
handled by LISS-0503, while the existing bare `Limit` rejection code remains
unchanged.

Same-context review re-read this Issue, WP-0109, the accepted specification,
all included public-entry tests, and the emitter/facade implementation. No
blocking finding remains within the approved slice. Review isolation was
`same_context`, which is weaker than `separate_context`.

Verification: `./.venv/bin/pytest -q
tests/test_liss_0446_qasm_public_entry_red.py
tests/test_liss_0503_qasm_unsupported_evolution_rejection_red.py
tests/test_liss_0445_consumer_migration_red.py` — **28 passed**;
`py_compile` and `git diff --check` passed.

Reviewer empathy summary: every included facade exposes or forwards the
compile-owned semantic IR explicitly; compatibility callers remain bounded to
one invocation and no global cache is introduced.

Process review: no operating-contract deviation or operational problem found.

Issue complete. Dynamic QASM, CH0, provider/live-QPU, S02, and solver work
remain separately gated.
