# LISS-0401: `finiteize` Continuous-argument overload

## Metadata

- Local issue ID: LISS-0401
- Status: complete
- Phase: phase-3-refactor (Green/Refactor complete under batch approval
  `execution-batch-wp-0097.json`)
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
- GitHub Issue / PR: [#514](https://github.com/nn0cl/staqex/pull/514) (batch)

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

- [x] Lane A `finiteize(lo, hi, n_bins, n_samples[, seed])` unchanged,
  full existing regression (LISS-0313, 9 tests) passes unmodified.
- [x] New overload `finiteize(continuous, lo, hi, n_bins[, seed])` —
  **positional grammar chosen** (mirrors Lane A's own positional style
  instead of introducing kwargs parsing, which nothing else in this
  batch uses); discriminated at evaluation time by whether the first
  argument's currently-bound value is a `ContinuousFieldValue`, not by
  arity (both forms take 4-5 args) — no silent misparse, confirmed by
  the Lane A regression guard passing unchanged.
- [x] **New `ContinuousFieldPort.discretize(value, lo, hi, n_bins, seed) ->
  Mapping[label, mass]` port method** (extends the LISS-0399 port rather
  than reusing `HostMonteCarloPort`, per this Issue's own dependency —
  the Kernel passes the *whole* composed handle tree to the Host, which
  is the only party able to actually evaluate it; the Kernel never runs
  `EqualWidthHistogramMonteCarlo` itself for this path, since that
  requires a real Python callable draw function the Kernel does not
  have — a real (non-fake) adapter would reuse it internally, matching
  every other Host-port precedent in this project of shipping the port +
  a fake, not a real adapter, in the Feature Issue).
- [x] Result is an ordinary finite `State`, indistinguishable downstream
  from a Lane A `finiteize` result (`joint.bind_split`, same as Lane A).
- [x] Provenance carries `discretization` (ADR 0074 shape) +
  `continuous_pipeline` (built by a new pure Kernel-side tree walk,
  `continuous_field.continuous_pipeline_ops`, no Host call).
- [x] `hir.py`: a `Continuous` root consumed by `finiteize` does not
  produce `LINEAR_IMPLICIT_DISCARD`; an un-finiteized root still does.
- [x] A second `finiteize` call on an already-consumed `Continuous` root
  is rejected with `LINEAR_DUPLICATE_USE` — **new dedicated check**
  (`_check_finiteize_continuous_reuse`, mirrors `_check_reset_stmt`'s
  pattern) was required: discovered during Red that the generic
  Call-argument consumption path (`_mark_linear_var_use`) silently
  no-ops on an already-consumed root (it is a plain set add), so
  `weight`/`mask`'s "free" LINEAR handling in LISS-0400 does not extend
  to duplicate-use detection — a real, narrow gap, not assumed away.
- [x] Full regression sweep, including LISS-0313's existing finiteize
  tests, unaffected outside new/targeted assertions: **1440 passed**, up
  from 1435 by exactly the 5 new tests.

## Explicitly out of scope

- `CH-field-fork` (dual finiteize of a shared root) — explicitly deferred
  by ADR 0204 Decision 5, not fixed here.
- Any S01 showcase example wiring — a separate, later Issue once this
  batch is Green (matches ADR 0204's own sequencing note).
