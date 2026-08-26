# WP-0094 Tensor hardening — Phase 1 Red handoff

## Current State

- Current phase: Complete; PR #339 merged 2026-08-04.
- User request: continue the remaining ASCII quantum notation implementation.
- Scope: Tensor alias parity, binary arity, left association, factor order, and
  tensor/arithmetic grouping.
- Out of scope: Unicode source policy, ket/bra lexing, quantum semantics, QPU
  adapters, and formatter presentation.

## Completed

- Added `tests/test_ascii_tensor_parity_red.py` from the accepted WP-0094
  acceptance scenarios.
- Confirmed four expected failures against the current implementation:
  alias AST parity, compile-time alias arity, arithmetic grouping, and
  classical-constructor separation. The left-association/factor-order parser
  assertion already passes.
- Commit: `7a0cdc2` on `codex/wp0094-tensor-hardening`.

## Next Safe Action

Post-merge status is recorded in WP-0094, ADR 0191, the accepted ASCII
specification, and the open-work register. No further implementation is
pending for this work unit.

## Open Decisions

- `TENSOR_ARITY_ERROR` and `TENSOR_GROUPING_ERROR` are the accepted diagnostics.
- Completion evidence: PR #339 and passing CI checks.
