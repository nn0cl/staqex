# Staqex Quickstart (developers)

Product onboarding for humans and agents working **in this repository**.
This is **not** the collaboration-template adoption guide
(`docs/collaboration/adoption-guide.md`).

**Design orientation:** Staqex is a language **for physicists** (blackboard
first; programmer DX second). See
[`docs/architecture/adjudicator-language-vision.md`](docs/architecture/adjudicator-language-vision.md)
and [`docs/architecture/physicist-dx-harmony.md`](docs/architecture/physicist-dx-harmony.md).

[日本語](QUICKSTART.ja.md) · [README](README.md)

## 0. Prerequisites

- Python 3.11+ recommended (stdlib only for the Kernel path used here)
- Repo root as cwd

## 1. Run an official example

```bash
python3 -m compiler.staqex run examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx --seed 0
python3 -m compiler.staqex run examples/basics/B08_operators_hamiltonians/operators_hamiltonians.sqx --seed 0
python3 -m compiler.staqex run examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx --seed 0
```

**Teaching face (WP-0089 / LISS-0303):** single-file basics use the **default**
experiment profile (ADR **0182**) — no package / `main` wrapper required.
B08 is the chalk north star (`evolve under H`, `measure … tracing_out …`).
**`evolve` needs real physical units (ADR 0195):** `H`'s coefficients
must already be real Joules and the duration real seconds by the time
they reach `evolve` — B08's own `Energy J = 1.0.eV to J` /
`Energy h = 0.5.eV to J` lines aren't decoration, they're required.
Skipping them and using bare dimensionless weights instead overflows
the evolution step budget with a
`evolve magnitude |H*t/hbar| ~= 2**N exceeds ...` error; scale any raw
weights with the same `Energy scale = <value>.eV to J; Operator H =
scale * H_raw` two-step pattern before evolving.
Bind forms (`state` / bare / Type-First):
[bind-decision-tree](docs/architecture/bind-decision-tree.md).
Official sample style (constructors, free-fn vs class, package depth):
[surface-style-guide](docs/architecture/surface-style-guide.md).

Multi-file examples use `import` + path linking (ADR **0054**) with short
package root **`examples.…`**
([package-root-naming](docs/architecture/package-root-naming.md)).
No `module-info.sqx` is required for local scripts (ADR **0058** revised).

Failure vocabulary (world-line vs Job vs capability) — three different
“fail” words, do not conflate:

| Layer | Means |
|---|---|
| World-line `Err` / `when` | Mixture branch in Joint (B03) |
| Host Job failure | Job/result lifecycle outside Kernel |
| Capability reject | Target cannot place the program (QPU honesty) |

Details: [ADR 0175](docs/architecture/decision-themes/dec-0003-language-surface-and-physicist-first-dx.md).

**Soft `QSEM_*` diagnostics (not failures):** many successful `run`/`compile`
paths still emit soft codes such as `QSEM_FINITE_EVIDENCE_MISSING` or
`QSEM_APPROXIMATION_OBLIGATION_MISSING`. These are **IR honesty obligations**
for Semantic/Physics lowering — they mean “this path is not claiming exact
symbolic evidence,” **not** “the program failed.” Hard failures use codes in
`HARD_CODES` (e.g. `LINEAR_*`, `WHEN_NONEXHAUSTIVE`, `PARSE_ERROR`) and stop
execution. Teaching demos that seed-0-print a measured value while soft QSEM
lines appear are still **green** for learning chalk.

## 2. Keep the conformance gate green

```bash
python3 tests/spec_verification/run_all.py
```

OOP / visibility AT-TDD:

```bash
python3 tests/test_modern_oop_and_visibility.py
python3 tests/test_enum_support.py
python3 tests/test_encapsulation_and_module_info.py
```

## 3. Minimal valid program (experiment profile)

```staqex
// staqex-profile: experiment
state x = dirac(0)
measure x
```

```bash
python3 -m compiler.staqex run path/to/file.sqx --seed 0
```

Packaged multi-file form remains valid: `package examples.demo` +
`pub fn main() -> Unit { … }`.

**Vocabulary note:** the binding keyword `state` and the type `State<T>` both
appear; mid-program values stay in the joint until terminal `measure`.

## 4. Physicist-facing structure (optional multi-file)

```staqex
package examples.demo
namespace Topology.SSH {
  pub enum BoundaryCondition { Periodic, Open }
  pub struct SSHParams { val v: Float, val w: Float }
  pub class SSHSystem {
    var _t: Float = 0.0
    pub val params: Topology.SSH.SSHParams
    fn init(p: Topology.SSH.SSHParams) {
      this.params = p
    }
    pub fn step() {
      this._t = this._t + 0.1
      Float done = 1.0
    }
  }
}
pub fn main() -> Unit {
  Topology.SSH.SSHParams p = Topology.SSH.SSHParams(0.5, 1.5)
  Topology.SSH.SSHSystem s = Topology.SSH.SSHSystem(p)
  Float ok = s.step()
  measure ok
}
```

Rules of thumb: method keyword is **`fn`** (`fun` is Retired); no `new`; no
`protected`; hide with `_`; export libraries with `pub`. Prefer `struct` for
parameter packs; `class` for true physical systems.

## 5. Where to read next

| Need | Document |
|------|----------|
| Agent workflow | `AGENTS.md`, `docs/architecture/agent-quickstart.md` |
| Language axioms | `docs/architecture/staqex-language-axioms.md` |
| Normative syntax/semantics | `docs/specs/staqex-language-specification.md` |
| Physicist ↔ DX harmony | `docs/architecture/physicist-dx-harmony.md` |
| Architecture map | `docs/architecture/README.md` |
| Examples | `examples/README.md` |
| Template process (Adjudicator) | `docs/collaboration/adoption-guide.md` |
