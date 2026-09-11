# Staqex

**Staqex** (*Quantum-Probabilistic Executable*) is a programming language that aims to
let you write quantum-computer programs the way you write theoretical-physics
formulas.

[Japanese README](README.ja.md) · [Quickstart](QUICKSTART.md) ·
[Architecture](docs/architecture/README.md) · [Language Spec](docs/specs/staqex-language-specification.md)

> **Formerly known as QPex.** Renamed to Staqex on 2026-07-29 due to a naming
> conflict. Language semantics and all ADRs are unchanged. See
> [`docs/architecture/README.md`](docs/architecture/README.md#project-rename-history)
> for the full rename record.
>
> **Kernel tags:** pin QPex-era trees to **`v0.1.1`** (last `compiler/qpex/`
> commit). Current / next Staqex Kernel line is **`v0.2.0`**.

## License

Dual-licensed under **MIT OR Apache-2.0** — see [LICENSE](LICENSE),
[LICENSE-MIT](LICENSE-MIT), [LICENSE-APACHE](LICENSE-APACHE).

## Status (honest)

| Layer | Reality |
|-------|---------|
| Collaboration / AT-TDD | Adopted from `llm-project-template` (`AGENTS.md`, ADRs 0001–0012, …) |
| Normative language surface | `docs/specs/staqex-language-specification.md` + ADRs 0013+ |
| **Runnable Kernel today** | **Python** package `compiler/staqex/` (lexer → parser → typecheck → Joint evaluator) |
| Local execution | Provider-neutral Host `run` / `submit` API backed by the local Joint simulator |
| OpenQASM target | OpenQASM 3 lowering, routing, and file emission are available offline |
| Execution artifacts | Portable and target-resolved `.sqxa` writer/reader and Runtime preflight are implemented; SDKs and credentials stay outside artifacts |
| AWS Braket | Host adapter and live job lifecycle CLI are implemented, but real-device execution is explicitly opt-in and has not been exercised by CI |
| Scientific workflow | Bounded S02 assay-cycle and quantum-vs-classical baseline comparison APIs are implemented; broader domain coverage remains in progress |
| GPU | Target is reserved and currently falls back to the CPU Joint simulator |
| Spec verification | `python3 tests/spec_verification/run_all.py` (currently 161/161 passing; keep green) |

Do **not** invent language behavior without an accepted ADR/spec and an
explicit AT-TDD phase (see `AGENTS.md`).

The source/runtime boundary is deliberate: Staqex owns source meaning,
semantic validation, finite realization policy, artifact identity, and
measurement interpretation. Host adapters own SDK/API translation,
credentials, provider job state, and transport. A provider adapter must not
silently change the source-derived meaning or turn a rejected realization into
a successful result.

## Physicist DX (surface)

Programmer tools are framed as physics units — not Java ceremony:

| Surface | Physics reading |
|---------|-----------------|
| `enum` | Exclusive geometry / bases |
| `struct` | Immutable parameter packs |
| `class` + `fun init` | Physical **system** / experimental setup (`new` Forbidden) |
| `namespace` | Theory sectors |
| default / `pub` / `_` | Module-private / public API / class-private (no `protected`) |

Details: [`docs/architecture/physicist-dx-harmony.md`](docs/architecture/physicist-dx-harmony.md),
ADR **0054–0056**, **0058**.

## Run a program

```bash
python3 -m compiler.staqex run examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx --seed 0
python3 -m compiler.staqex run examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx --seed 0
```

The CLI also supports source checks, non-destructive inspection, computation
DAG output, an interactive REPL, Unicode migration, and canonical formatting:

```bash
python3 -m compiler.staqex check examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx
python3 -m compiler.staqex inspect examples/basics/B05_phase_interference/phase_interference.sqx --seed 0
python3 -m compiler.staqex dag examples/basics/B05_phase_interference/phase_interference.sqx --dot
python3 -m compiler.staqex repl --seed 0
python3 -m compiler.staqex format path/to/program.sqx --check
python3 -m compiler.staqex migrate path/to/program.sqx --check
```

`run` executes the source on the local CPU/Joint simulator by default. The
Host API returns provider-neutral `Job` / `JobResult` objects, keeping the
Kernel's AST and `Joint` representation out of the public host result:

```python
from compiler.staqex import run_source, submit_source

source = """
pub fn main() -> Unit {
    State<Int> answer = dirac(42)
    measure answer
}
"""
job = submit_source(source, settings={"target": "local", "seed": 0})
result = job.result()
print(result.status, result.measurements)

direct = run_source(source, settings={"target": "local", "seed": 0})
print(direct.status)
```

Examples index: [`examples/README.md`](examples/README.md).

## OpenQASM and QPU boundary

OpenQASM 3 can be generated locally from a supported static circuit surface;
generation does not contact a provider:

```bash
python3 -m compiler.staqex emit-qasm \
  examples/applied/A08_entangled_compute_ancilla/main_entangled_compute_ancilla.sqx \
  -o /tmp/staqex.qasm
python3 -m compiler.staqex run \
  examples/applied/A08_entangled_compute_ancilla/main_entangled_compute_ancilla.sqx \
  --target qpu:openqasm3 -o /tmp/staqex.qasm
```

The `qpu:<profile>` target is a local compile/emission path. Unsupported
semantic projections are rejected rather than silently approximated. The
`gpu` target is currently reserved and falls back to CPU simulation.

For an explicitly authorized real AWS Braket submission, the Host-only CLI is
available:

```bash
python3 -m compiler.staqex submit-live-qpu path/to/program.sqx \
  --device-arn arn:aws:braket:REGION::device/qpu/PROVIDER/DEVICE \
  --shots 100 --cost-ceiling-usd 1.00
```

This command requires the AWS Braket SDK and credentials in the Host's normal
credential chain, displays the resolved device/shots/cost, and asks for an
interactive `y`/`yes` confirmation immediately before submission. It can
incur real cost and is not used by the local test suite. Job lifecycle
commands are available as `qpu-job-status`, `qpu-job-wait`,
`qpu-job-result`, and `qpu-job-cancel`.

`.sqxa` is the serialized execution-artifact boundary: a portable artifact can
be target-resolved into a targeted artifact carrying route/device/capability
metadata. Provider SDKs, credentials, and human approval records do not enter
the artifact. See [`compiler/staqex/sqxa.py`](compiler/staqex/sqxa.py),
[ADR 0219](docs/architecture/adr/0219-sqxa-target-build-boundary.md), and
[LISS-0542](docs/issues/LISS-0542-sqxa-target-build.md).

## Scientific workflow status

The scientific workflow work is intentionally tracked separately from the
language Kernel surface. The current bounded S02 path includes:

- measured-assay input, leakage-safe model, classical batch cycle, and
  reproducibility evidence;
- a provider-neutral quantum-vs-classical baseline comparison with candidate,
  decode/feasibility, objective, cost, and lineage checks;
- fail-closed handling for runtime rejection, missing cost, invalid decode,
  constraint violation, and mismatched lineage.

These are local Python modules and offline fixtures, not a claim of quantum
advantage or a replacement for scientific validation. They do not require a
live QPU. The current bounded comparison implementation is
[`compiler/staqex/s02_quantum_baseline_comparison.py`](compiler/staqex/s02_quantum_baseline_comparison.py);
the broader roadmap and remaining domain profiles are in
[`docs/work-plans/WP-0131-scientific-workflow-program.md`](docs/work-plans/WP-0131-scientific-workflow-program.md).

Language-spec benchmark showcase (listed last in the examples catalog):
[`examples/showcase/S01_quantum_disaster_response/`](examples/showcase/S01_quantum_disaster_response/)
— **written as a language-specification benchmark** on a disaster command-room
story (aftershocks / fire / firestorm risk included as ops secondary hazards;
[README](examples/showcase/S01_quantum_disaster_response/README.md)).

## Verify

```bash
python3 tests/spec_verification/run_all.py
python3 tests/test_modern_oop_and_visibility.py
python3 -m pytest -q tests/test_s02_assay_batch_cycle_red.py \
  tests/test_s02_quantum_baseline_comparison_red.py
```

## Agent / Adjudicator entry

1. `AGENTS.md` — operating contract  
2. `docs/architecture/agent-quickstart.md` — Fast / Feature / Architecture Path  
3. `docs/collaboration/session-start-and-resume.md` — resume without chat memory  
4. Project/runtime facts live in `docs/collaboration/project-conventions.md`; operating rules live in `AGENTS.md`

Template sync (process docs only): keep `.collaboration-template-version`;
use `llm-project-template`’s `scripts/update-ai-collaboration-files.sh`.
Product README / language ADRs are **target-owned** — not replaced by the
template README.
