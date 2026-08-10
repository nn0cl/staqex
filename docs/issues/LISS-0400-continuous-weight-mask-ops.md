# LISS-0400: `weight` / `mask` continuous ops

## Metadata

- Local issue ID: LISS-0400
- Status: proposed
- Phase: phase-0-design (Investigation stage; Red not authorized)
- Type: Feature Path (Kernel — `evaluator.py` Call dispatch)
- Priority: P1
- Initial planning size: `S`
- Current planning size: `S`
- Owner / agent: Claude Code
- Dependencies: LISS-0399 (`Continuous<T>` type + `field_from_host`)
- Blocks: LISS-0401 (`finiteize` needs a composed `Continuous` chain to
  finiteize against, for an end-to-end test beyond a single
  `field_from_host` value)
- Parent: [WP-0097](../work-plans/WP-0097-continuous-lane-b-ship.md)
- Related: `compiler/staqex/runtime/evaluator.py`
- Branch: `feature/liss-0400-continuous-weight-mask-ops` (opened only after
  batch approval or Issue-level Plan approval)
- GitHub Issue / PR: (opened at Completion)

## Scope

Per [ADR 0204](../architecture/adr/0204-continuous-lane-b-type-world.md)
Decision 3 — exactly two ops, both lifted unchanged in meaning from the
already Host-proven `field_compose_inject.py` (LISS-0317) semantics:

1. `weight(Continuous, Continuous[, Continuous]) -> Continuous` — pointwise
   composition.
2. `mask(Continuous, Continuous) -> Continuous` — pointwise suppression.

Both ops are pure Kernel-side bookkeeping: compose a new opaque handle
referencing its input handles + the operation name (for provenance /
`continuous_pipeline`, consumed by LISS-0401's `finiteize` extension). No
Kernel-side numeric evaluation of the underlying continuous function — that
stays Host-side, deferred until `finiteize` forces a concrete pass
(LISS-0401).

No other continuous ops in this Issue (`clip`, `normalize_field`,
`support_restrict` are explicitly deferred per ADR 0204 Decision 3 — a
later additive ADR, not this batch).

## Exit condition

- [ ] `weight`/`mask` recognized as Call forms over `Continuous` operands;
  reject non-`Continuous` operands with a clear diagnostic.
- [ ] Result is a new `Continuous` handle carrying the input handles + op
  name for later provenance assembly.
- [ ] Input roots are ordinary linear moves under `hir.py` (consumed by
  the `weight`/`mask` call, same as any other Call whose result is bound
  to a new name) — no special-case LINEAR logic beyond LISS-0399's
  `introduced`/`consumed` machinery.
- [ ] Full regression sweep unaffected outside new/targeted assertions.

## Explicitly out of scope

- `field_from_host` / the port itself (LISS-0399, depended on).
- `finiteize` extension (LISS-0401).
- Any other continuous op beyond `weight`/`mask`.
