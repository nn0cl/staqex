# ADR 0166: Kernel entropy, measurement sink, and source loading behind ports

## Status

**Proposed** (2026-08-01). Design candidate for
[LISS-0218](../../issues/LISS-0218-kernel-external-resource-ports.md).

This ADR **does not authorize implementation**. Red requires a separate ship
ADR and Adjudicator approval.

## Context

`CLAUDE.md` §External Resources Must Be Ports requires these to be represented
as ports *before* a concrete implementation is used:

> - Entropy / RNG source (for `measure` sampling) via `RngPort`.
> - Program source loading (file or stdin) via `SourcePort`.
> - Measurement / diagnostic sink (stdout, stderr, or files) via `MeasureSinkPort`.

The 2026-08-01 operations review found that none of the three exists:

| Required | Actual |
|---|---|
| `RngPort` | `runtime/evaluator.py` accepts a raw `random.Random \| None` and constructs `random.Random(seed)` / `random.Random()` directly |
| `MeasureSinkPort` | `stdlib/io_ops.write_sink` called directly from the evaluator; `inspect_sink` is a raw `TextIO` |
| `SourcePort` | `pipeline.compile_path` / `modules.load_module_graph` read the filesystem directly |

Ports that do exist show the intended shape and prove the pattern is workable
here: `CredentialPort` + `EnvCredentialAdapter` (ADR 0161 / LISS-0194),
`SimulatorPort`, `ObservationExecutionPort`, `PhysicalTargetPort`, and
`HostRngPort` + `HostRngAdapter` (ADR 0163 / LISS-0195).

`HostRngPort` is the complication: entropy is already behind a port on the Host
Monte Carlo lane, but Kernel `measure` sampling — the case the contract names —
is not. The two entropy paths are governed differently today.

## Dependency Adoption Evidence

Not applicable. These ports wrap the standard library and the filesystem; no
new dependency is selected.

## Decision (candidate — not accepted)

1. **Determinism is the binding constraint, not the port shape.** Every
   `--seed 0` example output, every SV report, and 200+ suites depend on the
   exact RNG call sequence. An accepted design states that seeded outputs are
   bit-identical before and after, and the ship Issue proves it by diffing
   published outputs — not by asserting it.
2. **`RngPort` is the first slice.** It is the port the contract names first and
   the only one of the three carrying a determinism obligation worth pinning.
   `MeasureSinkPort` and `SourcePort` follow as separate slices.
3. **The `HostRngPort` relationship is decided explicitly** — unified with the
   Kernel port, or kept separate because Host Monte Carlo and Kernel `measure`
   are different lanes. Silence is not an answer; two entropy governance models
   is how this drifted.
4. **The sink question is answered against the existing Host seam.** The Host
   boundary already converts results into `MeasurementEnvelope` / `JobResult`
   DTOs. The accepted design says whether `MeasureSinkPort` is a Kernel port or
   whether the Host DTO boundary is the correct seam and the contract text
   should say so.
5. **`SourcePort` states its position relative to the ADR 0054 module linker** —
   above or below `load_module_graph`.
6. **No new capability.** These ports wrap what the Kernel already does. No
   datastore, no network, no provider adapter; the MVP boundary in
   `CLAUDE.md` §Project Boundaries stands.

## Consequences

Positive:

- Closes a standing violation of the project's own architecture contract.
- Makes Kernel `measure` sampling substitutable for tests without reaching into
  evaluator internals.
- Puts Kernel and Host entropy under one governed story.

Negative:

- The evaluator constructor surface changes; every construction site and any
  suite that passes a `random.Random` is touched.
- Real risk of perturbing seeded outputs. If that happens the cost is a
  republished SV report and updated example expectations — which is why
  determinism is constraint 1 rather than a note.
- Three ports is more surface than the shipped need; hence the slice order.

## Enforcement

Code review should reject:

- A port whose adoption changes any seeded output without an explicit,
  approved decision to do so.
- A `RngPort` implementation constructed inside the evaluator rather than
  injected.
- Kernel Red started against this ADR — it is `Proposed` and authorizes nothing.
- Introducing a network, datastore, or provider adapter under cover of "it is a
  port now".
