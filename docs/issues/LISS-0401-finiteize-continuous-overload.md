# LISS-0401: `finiteize` Continuous-argument overload

## Metadata

- Local issue ID: LISS-0401
- Status: proposed
- Phase: phase-0-design (Investigation stage; Red not authorized)
- Type: Feature Path (Kernel — `evaluator.py`; reuses Host
  `EqualWidthHistogramMonteCarlo` bucketing, ADR 0163)
- Priority: P1
- Initial planning size: `M`
- Current planning size: `M`
- Owner / agent: Claude Code
- Dependencies: LISS-0399 (`Continuous<T>` type, LINEAR introduce/discard),
  LISS-0400 (`weight`/`mask`, so this Issue can finiteize a genuinely
  multi-step composed chain, not only a bare `field_from_host` value)
- Blocks: none (closes the batch)
- Parent: [WP-0097](../work-plans/WP-0097-continuous-lane-b-ship.md)
- Related: `compiler/staqex/runtime/evaluator.py` (`_bind_finiteize`),
  `compiler/staqex/host_monte_carlo.py` (`EqualWidthHistogramMonteCarlo`,
  reused unchanged)
- Branch: `feature/liss-0401-finiteize-continuous-overload` (opened only
  after batch approval or Issue-level Plan approval)
- GitHub Issue / PR: (opened at Completion)

## Scope

Per [ADR 0204](../architecture/adr/0204-continuous-lane-b-type-world.md)
Decision 4 — extend the shipped Lane A `finiteize(lo, hi, n_bins,
n_samples[, seed])` grammar (unchanged, still valid) with a second overload
accepting a `Continuous` first argument plus bins/interval/label_mode
keyword arguments. Exact keyword-argument shape is this Issue's own Red
material (ADR 0204 explicitly does not fix it).

1. `finiteize(continuous, bins = N, interval = …, label_mode = …) ->
   State` (or multi-name bind of finite States, same as Lane A).
2. Backend: a Host-side discretization pass over the composed handle chain
   (evaluates `field_from_host` → `weight` → `mask` lazily, in the order
   the handles were composed, then buckets), reusing
   `EqualWidthHistogramMonteCarlo`'s existing bucketing machinery — no new
   numerics.
3. Provenance: ADR 0074 `discretization` block (unchanged shape) plus
   `continuous_pipeline` (the op-name chain, generated from the real
   handle chain — same shape `field_compose_inject.py` hand-writes today,
   now derived instead of authored).
4. **Closes LISS-0399's LINEAR story**: `finiteize` is the consuming
   operation for a `Continuous` root. A `Continuous` root consumed by
   `finiteize` is marked `consumed` in `hir.py`, same as LISS-0399's
   `field_from_host`-then-untouched case produces `LINEAR_IMPLICIT_DISCARD`
   — this Issue proves the positive case (consumed → no discard).
5. **Known, disclosed limitation carried from ADR 0204 Decision 5**: a
   `Continuous` root may be consumed by `finiteize` at most once.
   `CH-field-fork` (one root, two independent `finiteize` calls) is **not**
   satisfied by this Issue — matches the ADR's own explicit deferral, not
   a gap introduced here.

## Exit condition

- [ ] Lane A `finiteize(lo, hi, n_bins, n_samples[, seed])` unchanged,
  full existing regression (LISS-0313) passes unmodified.
- [ ] New overload accepts a `Continuous` value; rejects non-`Continuous`
  first-argument shapes that aren't the Lane A numeric form with a clear
  diagnostic (no silent misparse between the two overloads).
- [ ] Result is an ordinary finite `State`, indistinguishable downstream
  from a Lane A `finiteize` result.
- [ ] Provenance carries `discretization` + `continuous_pipeline`.
- [ ] `hir.py`: a `Continuous` root consumed by `finiteize` does not
  produce `LINEAR_IMPLICIT_DISCARD`; an un-finiteized root still does
  (regression guard against LISS-0399's own case).
- [ ] A second `finiteize` call on an already-consumed `Continuous` root
  is rejected (or at minimum not silently accepted as a second free
  consumption) — exact diagnostic shape is Red material.
- [ ] Full regression sweep, including LISS-0313's existing finiteize
  tests, unaffected outside new/targeted assertions.

## Explicitly out of scope

- `CH-field-fork` (dual finiteize of a shared root) — explicitly deferred
  by ADR 0204 Decision 5, not fixed here.
- Any S01 showcase example wiring — a separate, later Issue once this
  batch is Green (matches ADR 0204's own sequencing note).
