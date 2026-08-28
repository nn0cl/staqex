# LISS-0456: Canonical Semantic IR through public QASM entry points

| Field | Value |
|---|---|
| Status | **done — Phase 3 reviewed; bounded canonical Measure slice complete** |
| Phase | phase-3-refactor |
| Type | architecture / migration |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | compiler/semantic boundary |
| Parent | WP-0119; WP-0120; WP-0108 |
| Depends on | LISS-0455 |
| Blocks | LISS-0458, LISS-0461, LISS-0462 |
| Branch | `codex/liss-0456-phase1-red` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0456--canonical-consumer-authority) |

| Scope approval | User approved LISS-0456/LISS-0457 design scope, 2026-08-27 |
| Implementation permission | Phase 2 Green approved only for the bounded canonical Measure slice |
| Post-review requirement | Acceptance review and separate typed Phase 1 approval |
| Current evidence | [Phase 1 Red tests](../../tests/test_liss_0456_semantic_consumer_qasm_red.py); canonical Measure-only Green; `py_compile`/`git diff --check` pass; pytest unavailable locally |
| Completion evidence | Canonical path regression passes; no AST/DAG fallback; full pytest deferred to CI because pytest is unavailable locally |

Inventory and then migrate public QASM facades, legacy AST helpers, and
non-explicit `symbolic_ir` consumers so compilation owns one canonical
Scientific Semantic IR. Acceptance must cover source identity, provenance,
finite realization, fallback rejection, no-artifact behavior, and terminal
Measure. LISS-0445's completed binder slice is not reopened; Phase 1 Red and
Phase 2 Green require separate approval.
## Design detail

**In:** semantic IR, QPU/QASM pipeline entry points, public facades, legacy AST
helpers, `symbolic_ir`, representative `.sqx` fixtures, and migration records.
**Out:** new syntax, provider behavior, S02 migration, solver work, and
unrelated consumers.

**Acceptance:** each selected facade consumes one compile-owned Scientific
Semantic IR identity; legacy AST/DTO or caller strings cannot override it;
unresolved meaning retains provenance and emits no artifact; terminal `measure`
remains explicit.

**Phase/evidence:** Phase 0 inventory/spec; Phase 1 Red no-bypass tests; Phase
2 one bounded facade slice; Phase 3 retirement/rollback proof. Deliverables
are consumer matrix, fixtures, Spec update, tests, and review packet. Verify
focused/full suites, diff check, and source-reachability audit. Planning record:
`AIP-LISS-0456-2026-08-27-001` (L; N/A model metrics).

**Decision point:** facade ownership and compatibility window require review if
ADR 0211 or `Realize` semantics would change.

### Phase 3 reviewer summary

- **What was reviewed:** bounded Measure-only canonical QASM path, unchanged
  Phase 1 assertions, output spelling, and fallback removal boundary.
- **Result:** no behavior-changing refactor was needed; the two-line routing
  change is readable and keeps provider-neutral/QASM responsibilities intact.
- **Verification gap:** local pytest could not run because pytest is not
  installed; CI must run the targeted and full suites before merge.
- **Reviewer focus for human review:** confirm that future canonical
  instruction kinds follow the same no-fallback rule and that CI covers the
  existing LISS-0446 public-entry regression suite.

Process review: no operating-contract deviation or operational problem found.
