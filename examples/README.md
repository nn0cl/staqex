# Staqex Official Examples

Physics-oriented sample programs for **Staqex（スタケックス）**.

Axiom: **Never Leave the State** — every mid-program value is `State<T>`;
collapse happens only at terminal `measure`.

## Catalog v2

| Track | Path | Status |
|-------|------|--------|
| **Basics** | [`basics/`](basics/) | B01–B15 — language axioms through multi-register |
| **Applied** | [`applied/`](applied/) | A01–A11 — integration and domain toys |
| **Showcase** | [`showcase/`](showcase/) | Language-spec benchmark programs (see last row below) |

Start with [`basics/README.md`](basics/README.md) for the curriculum path, then
[`applied/README.md`](applied/README.md) for integration capstones. Showcase
programs are **not** the onboarding path — they exist to stress language
expressiveness on a realistic product story.

Catalog spec: [`docs/specs/staqex-examples-catalog-v2.md`](../docs/specs/staqex-examples-catalog-v2.md).  
Conventions: [`docs/collaboration/examples-catalog-conventions.md`](../docs/collaboration/examples-catalog-conventions.md).

## Showcase (last — language-spec benchmark)

| ID | Path | Note |
|----|------|------|
| **S01** | [`showcase/S01_quantum_disaster_response/`](showcase/S01_quantum_disaster_response/) | **Written as a language-specification benchmark.** Reality-first Quantum Disaster Response OS (tonight → morning → day-2), including aftershocks / urban fire / firestorm risk. Full story: [locked scenario](../docs/specs/staqex-v1-s01-locked-scenario.md). [README](showcase/S01_quantum_disaster_response/README.md). |

```bash
python3 -m compiler.staqex run examples/showcase/S01_quantum_disaster_response/main_disaster_response.sqx --seed 0
```

Older `showcase/quantum_matter_discovery/` is salvage only (superseded mission).

## Program structure

Every example is a structured compilation unit:

```staqex
package examples.…

pub fn main() -> Unit {
    // Type-First binds, evolve, measure — never top-level script soup
}
```

Top-level executable statements are rejected (`TOPLEVEL_EXECUTION_ERROR`, SV-16).

## Kernel note (stance a)

The evaluator is a **complex-amplitude Joint** runtime: each world carries
$c\in\mathbb{C}$ with Born weight $|c|^2$. `phase` / `cis` / `Complex.cis`
attach phases; `interfer` sums amplitudes then takes $|\sum c_i|^2$
(destructive cancel → vacuum). `diffuse` is Grover inversion-about-mean.

Surface vocabulary: `Mix` / `map` / `project` / `interfer` / `phase` /
`diffuse` / `Inspect` / `Measure` / `Evolve`.

## Run

```bash
python3 -m compiler.staqex check examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx
python3 -m compiler.staqex run examples/basics/B05_phase_interference/phase_interference.sqx --seed 0
python3 -m compiler.staqex run examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx --seed 0

# Portable source → OpenQASM sketch (ADR 0036)
python3 -m compiler.staqex emit-qasm examples/applied/A08_entangled_compute_ancilla/main_entangled_compute_ancilla.sqx

# all official examples + backend tests (SV-09 / SV-10)
python3 tests/spec_verification/run_all.py
```

## Host Job API

Staqex source does not contain `Job` or `Task` operations. A host program may
submit the same source through the provider-neutral local API; this is also the
boundary where a future simulator service or QPU adapter will connect.

```python
from compiler.staqex import submit_source

source = """
pub fn main() -> Unit {
    State<Int> answer = dirac(42)
    measure answer
}
"""

job = submit_source(source, settings={"target": "local", "seed": 0})
print(job.id, job.status())
result = job.result()  # waits for completion in a remote adapter
print(result.status, result.measurements[0].value)
```

For a blocking local or CLI-style call, use `run_source(source, settings=…)`.
`JobResult` contains measurement envelopes and host metadata; it does not
expose the Kernel's `Joint` or AST. Provider SDKs, credentials, retries, and
sessions are intentionally outside this example and remain future Host
Adapter work.
