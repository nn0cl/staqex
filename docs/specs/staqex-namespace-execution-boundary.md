# Staqex namespace execution boundary

| Field | Value |
|---|---|
| Status | **Accepted scope — final-review-ready** |
| Issue | [LISS-0440](../issues/LISS-0440-namespace-execution-boundary.md) |
| WorkPlan | [WP-0102](../work-plans/WP-0102-namespace-execution-boundary.md) |
| Authority | Existing language specification and `pub fn main` contract; Phase 2 implementation and Phase 3 review approved 2026-08-17 |

## Contract

`namespace` contributes names and declarations. It does not execute a
statement sequence during module loading or declaration processing.

Allowed namespace members are limited to declaration forms already accepted by
the shipping grammar. Executable statements must appear inside a callable or
the existing compilation-unit entry body. New top-level `Parameter`, `Operator`,
or `Realize` declarations are not introduced by this specification.

The runnable entry remains at compilation-unit scope. The following is a
conceptual shape, not a Phase 1 compile fixture:

```staqex
pub fn main() -> Unit {
  State psi_final = evolve_once(psi_initial)
  measure psi_final
}
```

## Required behavior

| Case | Result |
|---|---|
| `namespace` with declarations only | Accept |
| compilation unit with existing `pub fn main` | Accept as runnable entry |
| library unit without `main` | Accept as non-entry unit |
| unrecognized executable member directly in namespace | Existing `PARSE_ERROR`; no new namespace diagnostic in this spec |
| mutable global `State<T>` policy | Deferred; no new diagnostic in this spec |
| QPU/Host submission during namespace initialization | Deferred; Phase 1 does not add a Host boundary diagnostic |
| namespace-qualified entry selection | Deferred; not introduced by this spec |

## Non-goals

This specification does not introduce global mutable memory, static constructors,
implicit module initialization, provider integration, or a new class system.
