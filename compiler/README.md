# Staqex compiler (shipping Kernel)

Python package under `compiler/staqex/` — the runnable implementation of the
language surface exercised by `examples/` and SV suites.

| Module | Role |
|--------|------|
| `lexer.py` / `parser.py` / `typecheck.py` | Frontend |
| `modules.py` / `access.py` | Import linker + `pub` / `_` visibility (ADR 0054 / 0058) |
| `runtime/` | Joint Kernel evaluator (`struct` copy / `class` ref / `fun init`) |
| `stdlib/` | Prelude, `Math.*`, I/O sinks |
| `ir/` | Computation DAG IR (ADR 0032) |
| `codegen/` / `codegen_qasm.py` | OpenQASM 3 (`OpenQASM3Generator`, `StaqexCompiler.compile_to_qasm3`) |
| `backend/qasm/` | Circuit lower / route / emit (ADR 0036) |
| `cli.py` | `run` / `check` / `inspect` / `dag` / `emit-qasm` / `repl` / `migrate` / `format` / live QPU job commands |
| `host.py` | Provider-neutral local `Job` / `JobResult` boundary and simulator execution |
| `sqxa.py` | Portable/target-resolved `.sqxa` artifact writer, reader, and Runtime preflight |
| `s02_*` | Bounded scientific S02 input/model/batch/comparison APIs; offline and provider-neutral |

```bash
python3 -m compiler.staqex emit-qasm examples/applied/A08_entangled_compute_ancilla/main_entangled_compute_ancilla.sqx
python3 -c "from compiler.staqex import StaqexCompiler; print(StaqexCompiler().compile_to_qasm3('examples/applied/A08_entangled_compute_ancilla/main_entangled_compute_ancilla.sqx'))"
python3 tests/test_qasm3_codegen.py
python3 tests/spec_verification/run_all.py
```

The local simulator and OpenQASM emission do not require cloud credentials.
The AWS Braket Host adapter is an explicit live-QPU boundary; submission
requires the Braket SDK, Host credentials, device configuration, cost ceiling,
and interactive approval. CI and the local scientific workflow fixtures do not
contact a real QPU. GPU execution is currently reserved and falls back to the
CPU Joint simulator.

Human entry: repo-root `QUICKSTART.md`. Design harmony:
`docs/architecture/physicist-dx-harmony.md`.
