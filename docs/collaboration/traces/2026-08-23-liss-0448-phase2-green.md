# LISS-0448 Phase 2 Green Trace

- Approval: user approved Phase 2 Green and implementation on 2026-08-23.
- Branch: `codex/liss-0448-canonical-qasm-coin-mix-projection`.
- Scope: canonical Coin/Mix branch meaning and fail-closed legacy QPU
  projection under accepted ADR 0213 and the accepted LISS-0448 Spec.
- Phase 3 approval: not granted.

## Implemented

- Added source spans to parsed `WhenArm` nodes.
- Preserved `control_source_node_id`, ordered immutable `branch_rules`, and
  arm provenance in the canonical Scientific Semantic IR.
- Included branch meaning in `semantic_fingerprint` and ideal meaning identity.
- Resolved variable controls to their source state expression, preserving
  `Coin` identity rather than the intermediate variable spelling.
- Removed the legacy copy-pattern `WhenExpr` → `CX` fallback; unsupported
  mixture lowering now rejects atomically.

## Verification

- Focused LISS-0448 harness: **8 passed**.
- Full spec verification: **161/161 passed (100%)**.
- `py_compile` passed for modified Python modules.
- `git diff --check` passed.
- Reviewed tests were not changed during Green.

## Boundaries and remaining work

- No provider SDK, live QPU, network, datastore, or hidden finiteization was
  introduced.
- Legacy lowerer remains a compatibility boundary and now fails closed for
  Coin/Mix; inventory/migration or retirement remains follow-up work.
- Independent post-Green review is required before any Phase 3 refactor.
