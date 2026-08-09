# LISS-0028: Dynamic QPU lane

## Metadata

- Local issue ID: LISS-0028
- Status: **Phase 3 reviewed** for the rejection/capability boundary; follow-up open
- Phase: Architecture Path → Feature Path boundary slice complete
- Type: language semantics / dynamic circuit boundary
- Priority: P1
- Related: ADR 0065, ADR 0069, ADR 0071, [ADR 0193](../architecture/adr/0193-dynamic-qpu-timing-region-intent.md) (Accepted 2026-08-05), [LISS-0381](LISS-0381-dynamic-qpu-timing-region-intent.md) (timing-intent Kernel slice), [ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md) (**Accepted** 2026-08-09), [LISS-0382](LISS-0382-dynamic-mid-circuit-feed-forward.md) (mid-circuit Kernel slice), LISS-0016, LISS-0019

## Acceptance specification

- [x] Mid-circuit measurement and classical feed-forward have explicit
      semantics distinct from terminal `measure`.
      Meaning Accepted via
      [ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md)
      (2026-08-09); Kernel surface + QSem witnesses shipped by
      [LISS-0382](LISS-0382-dynamic-mid-circuit-feed-forward.md)
      (**complete** 2026-08-09). Fake-exec / physical execution remain out
      of scope (ADR 0197 Decision 7).
- [x] Dynamic control is syntactically and semantically separate from static
      `forEach`.
- [x] A target capability profile is required before submission.
- [x] Unsupported dynamic features fail explicitly; no hidden Host fallback.
- [ ] Timing, qubit reuse, controller values, and JobResult composition are
      specified. **Partial:** timing's grammar/IR shape (`dynamic qpu
      within <name>`, a `TimingRegion` witness) is Accepted via ADR 0193
      and Kernel-shipped by
      [LISS-0381](LISS-0381-dynamic-qpu-timing-region-intent.md)
      (**complete**). Controller/match surface + QSem markers shipped by
      LISS-0382 (**complete**). Qubit reuse / JobResult composition remain
      fully open.
- [ ] CPU simulator and QPU lowering share an observable semantic contract.

## Non-goals

- Selecting IBM, Amazon Braket, IQM, or another provider.
- Implementing error correction or a provider-specific control dialect.
- Relaxing the Static Hilbert Kernel's terminal-measure baseline.

## Phase 1 record

- Status: **Red complete; awaiting Phase 2 Green approval**.
- Test file: `tests/test_static_parametric_dynamic_boundaries_red.py`.
- The test uses provisional `dynamic qpu { … }` syntax to make the required
  capability boundary observable; syntax and effect markers remain reviewable.

## Phase 2 record

- Status: **Green complete; awaiting Phase 3 Refactor approval**.
- Explicit dynamic blocks are parsed and rejected with capability/unsupported
  diagnostics; no dynamic execution or Host fallback was added.
- Verification: all unit tests and SV 165/165 passed.

## Phase 3 record

- Status: **Complete for the rejection/capability boundary; follow-up open**.
- Added explicit dynamic-lane teaching documentation and preserved the
  terminal-measure/static-Kernel separation.
- Remaining: JobResult composition, qubit reuse / reset model, Fake-exec /
  OpenQASM dynamic / live provider. Mid-circuit Kernel IR+diagnostics are
  **complete** (LISS-0382); timing intent shipped (LISS-0381).

## Phase 3 review record

- The current boundary accepts the explicit `dynamic qpu { ... }` marker only
  as a capability/rejection surface; it does not execute mid-circuit control.
- Unsupported dynamic features fail with stable diagnostics and never fall
  back to Host execution or static `forEach` elaboration.
- Static Kernel programs retain terminal `measure` semantics independently of
  this lane.
- Reviewer empathy: the completed rejection boundary is now clearly separated
  from the still-undecided dynamic measurement type/effect model.
- Status: **Phase 3 reviewed; rejection/capability boundary complete**.
