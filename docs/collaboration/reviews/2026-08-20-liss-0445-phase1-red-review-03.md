# LISS-0445 Phase 1 Red Independent Review 03

| Field | Value |
|---|---|
| Trigger | Fresh independent review after Review 02 corrections |
| Context boundary | New read-only reviewer; no edits, implementation, or approval |
| Result | **READY / COMPLETE** |
| Approval status | Phase 1 Red approved and complete; Phase 2 Green and implementation not approved |

## Verification

- `.venv/bin/pytest -q tests/test_liss_0445_consumer_migration_red.py`
  returned **5 failed, 7 passed**, with no collection errors.
- `git diff --check` passed.
- The fixed Red suite contains executable negative tests for caller-injected
  `EquationNode` authority and string DTO coercion.
- The Algorithm Plan check exercises the compile-owned plan at the projection
  boundary rather than requiring Python type identity.
- No Phase 1 production implementation was added; the dirty-worktree
  baseline is explicitly recorded in the trace.

## Final disposition

The five failures are intentional and identify the approved migration gaps:

1. diagnostic binder projection is rebuilt;
2. binder projection is built more than once during compilation;
3. the two Algorithm Plan representations are not yet connected at the
   projection boundary;
4. the H1 compiler path bypasses the canonical semantic result; and
5. ordinary QASM still reaches the AST fallback.

Caller DTOs and string equation payloads are now covered as non-authoritative
inputs. H1 structure/provenance, full QASM instruction provenance, and complete
`Realize` method/order/steps/error-budget retention are deferred to Phase 2
Green and do not block this Red phase.

## Reusable reviewer perspectives

- Verify canonical authority at an execution boundary, not by module or type
  naming alone.
- Require executable negative evidence for caller DTO and string-form bypasses.
- On a dirty worktree, record base commit, branch, and pre-existing paths.
- Separate Red boundary/rejection evidence from Green provenance completeness.

## Terminal state

`COMPLETE`: all Phase 1 Red review findings are resolved or explicitly
deferred within scope; no review blocker remains. This closes the review loop
only. Phase 2 Green requires a new typed user approval.
