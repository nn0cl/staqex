# Physicist mental model × programmer DX

Parent orientation:
[`adjudicator-language-vision.md`](adjudicator-language-vision.md)
(Adjudicator vision; physicist-first; ideal form first).

Staqex aims at **both**, with an explicit priority:

1. **Physicist mental model (primary)** — blackboard surface (states, operators,
   dimensions, exclusive classifications). This is a language **for
   physicists**; when physicist reading and programmer convenience conflict,
   prefer the physicist's form (ADR 0095: machine convenience never shapes the
   surface). The source must **denote the same physics** as the blackboard
   thought process — including intentional expansion, rewrite, and combination
   of formulas; machine-forced dialect shift is forbidden
   ([vision §2.2](adjudicator-language-vision.md)).
2. **Programmer DX (secondary, non-optional)** — `enum` / `struct` /
   `namespace` / visibility so large simulations stay typed and maintainable.
   DX must not rewrite the physics spelling into enterprise ceremony.

Importing Java ceremony (`protected`, mandatory `module-info`) fails (1).
Omitting structure fails (2). Every DX feature must have a **physics reading**.
Honest gaps: [`physicist-source-friction-ledger.md`](physicist-source-friction-ledger.md).
Pedagogy north star (**Accepted**): [`physicist-minimal-dialect.md`](physicist-minimal-dialect.md).

| DX feature | Physics reading |
|------------|-----------------|
| `enum` | Mutually exclusive geometry / bases (`Periodic` \| `Open`) |
| `struct` | Immutable parameter packs (\(v,w,\hbar\)) — **default for data** |
| `class` | **Physical system** (setup + evolving state / builds \(H\)), not DTO |
| `fn init` + `Type(…)` | Experimental setup (no `new`) — avoid for pure parameter bags |
| `namespace` | Theory sectors (`Topology`, `Hamiltonian`, …) |
| default / `pub` / `_` | Local law visible; library API marked `pub`; internals `_` |

**Struct-first teaching (WP-0088 / LISS-0268):** prefer `struct`/`enum` for
geometry and coefficients; use `class` when the type owns Hamiltonian or
evolving setup. Mutable “Tracker” counters are **not** the E-lane face — Host
or demoted demos only. De-enterprise look:
[`surface-modernization-north-star.md`](surface-modernization-north-star.md).
| `module-info` | Optional metadata only — **not required for scripts** |
| `QubitRegister<N>` | Static tensor-product degrees of freedom, \(\mathcal{H}_2^{\otimes N}\) |
| `Param<T>` | Symbolic circuit parameter, bound by Host submission |
| `dynamic qpu` | Explicit future hardware-control lane, not ordinary Kernel flow |

## Access (ADR 0058 revised)

- Default = module-private (no keyword noise on everyday equations).
- `pub` = export across modules.
- Leading `_` = class-private → `PRIVATE_ACCESS_VIOLATION_ERROR`.
- Cross-module use of non-`pub` → `MODULE_PRIVATE_ACCESS_ERROR`.
- No `protected`, no inheritance — compose parameters / systems.
- Method keyword is **`fn`** (`fun` is Retired; ADR 0066).

## Roadmap status (Kernel)

| Phase | Step | Status |
|-------|------|--------|
| 1 Geometry & parameters | 1.1 `enum` | **Shipped** |
| 1 | 1.2 `struct` | **Shipped** |
| 2 Domain & encapsulation | 2.1 `namespace` | **Shipped** |
| 2 | 2.2 visibility (`pub` / `_`) | **Shipped** |
| 3 Stateful systems | 3.1 `class` / `this` / `fn init` | **Shipped** |
| Open systems | ADR 0057 density / Lindblad | **Phase 3 reviewed: numeric and one-qubit symbolic jumps; general lowering pending** |
| Static Hilbert Kernel | ADR 0069 / LISS-0029 | **Phase 3 reviewed: `QubitRegister<N>` and MVP resource boundary** |
| Parametric Circuit | ADR 0070 / LISS-0027 | **Phase 3 reviewed: type/diagnostic boundary; QPU binding pending** |
| Dynamic QPU lane | ADR 0071 / LISS-0028 | **Phase 3 reviewed: rejection/capability boundary; execution pending** |


## `inspect` vs `measure`, and lane choice (LISS-0219)

- **`inspect` is not measurement.** It is a non-collapsing diagnostic / teaching
  view. Terminal collapse remains **`measure`** only (Never Leave the State).
  Naming pattern in samples: prefer `viewed_* = inspect(...)` over verbs that
  sound like readout.
- **Hamiltonian lane:** when the source is an operator / many-body Hamiltonian,
  prefer `evolve … under H` (and related Algebraic forms). Do **not** rewrite a
  paper Hamiltonian as gates “because that is what runs.”
- **Circuit lane:** when the mission is circuits (`QubitRegister`, `apply`,
  `Param`, QASM), use the Static/parametric QPU surfaces honestly.
- **Crossing lanes** in one example requires an Honesty note naming both dialects.

## Entry points

- Humans: `QUICKSTART.md` / `QUICKSTART.ja.md`
- Spec: `docs/specs/staqex-language-specification.md` §6.4–§6.5
- Example: `examples/applied/A06_topological_edge_memory/`
- Tests: `tests/test_modern_oop_and_visibility.py`
- Honest gaps today:
  [`physicist-source-friction-ledger.md`](physicist-source-friction-ledger.md)
  (where source still breaks equations or drifts from research reading)

Verification: `python3 tests/spec_verification/run_all.py`
