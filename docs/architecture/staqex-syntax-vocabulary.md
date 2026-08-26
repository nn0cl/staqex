# Staqex surface syntax and vocabulary (intermediate baseline)

Status: **Working baseline** (updated 2026-07-23, ADR 0024 / **0037**).
Supersedes provisional MVP `let` / `observe` / `fair_bit`, and migrates
`span` → `mix`, keyword `system` → `class`. Kernel PoC *laws* unchanged.
Umbrella: `staqex-language-spec.md`. Type-First + dims:
`staqex-dimensional-types.md` (ADR 0037).

Persona: a quantum researcher reading narrative code beside Dirac / density /
controlled-unitary notation.
Keyboard law: lowercase ASCII keywords, short (≈4–6 letters), home-row friendly.
Quantity declarations are **Type-First** (`Length x = …`), not `val x: Length`.

Normative companions:
- Agent sync: `docs/collaboration/agent-sync-staqex-baseline.md`
- Language Law: `docs/architecture/staqex-positioning.md`
- Types: `docs/architecture/staqex-type-system.md` (ADR 0018)
- Dimensions: `docs/architecture/staqex-dimensional-types.md` (ADR 0037)
- Naming style: `docs/style-guide/naming-conventions.md` (ADR 0023)
- Semantics: `docs/specs/staqex-formal-semantics-sketch.md`
- AST: `docs/architecture/staqex-ast-design.md`
- ADR 0017 (surface vocabulary)

---

## 1. Wedge (unchanged)

Never Leave the State. Deferred measurement is Language Law, not an optimizer
trick. No mid-program classical escape via `if` / early measure.

---

## 2. Vocabulary map

| Role | Keyword / form | Letters | Mathematical narrative |
|------|----------------|---------|------------------------|
| Bind a state coordinate | `state` | 5 | Object lives in joint state space |
| **Type-First quantity bind** | **`Q name = expr`** | — | Quantity heads the line (ADR **0037**) |
| Fair Bernoulli prep | `coin()` | 4 | $\frac12\lvert0\rangle+\frac12\lvert1\rangle$ (PMF shadow) |
| Dirac prep | `dirac(c)` | 5 | $\delta_c$ / $\lvert c\rangle$ (phase-0 MVP) |
| Controlled mixture | **`mix`** | 4 | Same law as former `span` / §Span |
| Time evolution block | `evolve` | 6 | Pure state update $U$ / pushforward pipeline |
| Terminal collapse | `measure` | 7* | Projective sampling collapse (sole RNG) |
| Model capsule | **`class`** | 5 | Immutable joint package (`: System`) |
| Capability | **`interface`** | 9 | e.g. `System` (ADR 0021) |
| Namespace / subsystem | `package` / `import` | — | $\mathcal{H}_A$ border (ADR 0024) |
| Function | `fn` | 3 | `fn` abolished (ADR 0026) |
| Entry point | `main` | 4 | `pub fn main` (+ optional State args) |
| Measure sink | `measure e to …` | — | Terminal collapse + host write (ADR 0029) |
| Checkpoint log | `snapshot` | 8 | Non-collapsing host log (ADR 0029) |
| Debug inspect | `inspect` | 7 | Non-destructive PMF view (ADR 0030) |
| Vacuum | `vacuum()` / `State.vacuum()` | — | Empty support (ADR 0034) |
| Pipeline (reserved) | `\|>` | — | Compose ops $U_2 U_1\lvert\psi\rangle$ |
| Former `span` / `system` | — | — | Retired surface; see ADR 0024 |

\*`measure` is 7 letters; accepted as physics-native over shorter aliases to
avoid PPL `observe` (conditioning) collision. Former provisional name
`observe` means the same collapse law; **surface spelling is now `measure`**.

### Forbidden classical surface

| Rejected | Why |
|----------|-----|
| Top-level `let` as the main binder | Reads as classical scalar binding; use `state` |
| `if` / classical `switch` | Jump + discard branch ≈ early observation; use `mix` |
| `while` / `for` / `break` | Classical loops; use `evolve` |
| `return` | Early exit collapses narrative continuity |
| Mid-program `measure` | Violates Never Leave the State |

`let` **may** appear **inside** an `evolve` block for local names that exist
only for the duration of that pure evolution; they escape only via the block’s
final expression (possibly a tuple / joint).

---

## 3. Forms

### 3.1 State preparation

```staqex
state c = coin()
state x = dirac(5)
```

### 3.2 `mix` (replaces `if` / classical `switch`; former `span`)

Binary sugar:

```staqex
state z = mix (c) {
    0 -> x + 10
    1 -> x + 20
}
```

Multi-arm (match-style — normative general form):

```staqex
state z = mix (c) {
    0 -> x + 10,
    1 -> x + 20,
    else -> x + 30,
}
```

Meaning (MVP): pushforward mixture over control atoms; every positively weighted
arm’s support is kept. Not classical short-circuit. Amplitude-linear reading is
ADR 0016 lift.

### 3.3 Block expression (state transformer kernel)

```staqex
{
    let a = z * 2
    let b = a + 5
    b
}
```

A block is $\llbracket\mathsf{Block}\rrbracket:\mathsf{Joint}_{\mathrm{in}}\to\mathsf{Joint}_{\mathrm{out}}$:
local `let` axes are ancilla-like; axes not in the result expression are
**traced out** at the boundary (not measured). No `return` / `break`.
See semantics §4.

### 3.4 Evolve (seed + block + bind-out)

```staqex
state w = evolve (z) {
    let a = z * 2
    let b = a + 5
    b
}
```

- No `return`.
- Last expression is the extracted state.
- Multi-name extract keeps correlation via tuple / joint:

```staqex
state (w1, w2) = evolve (z) {
    let a = z * 2
    let b = a + 5
    (a, b)
}
```

### 3.5 Terminal measure

```staqex
measure w1
```

Only at program end (Kernel Law: zero `RngPort` calls before this point).

### 3.6 `class` / `interface System` / generics

See `staqex-language-spec.md`, `staqex-abstraction-model.md`, ADR 0019–0024.
Surface: `class Foo : System` and `interface System`. Methods are immutable
pure transformers. Inheritance rejected. Keyword `system` / `trait` are
retired spellings.

### 3.7 Stdlib combinators (ADR 0021)

| Name | Role |
|------|------|
| `map` | Pushforward on supports |
| `project` | Subspace projection + renormalize (≠ `measure`) |
| `interfer` | Combine / interfere a list of `State<_>` |

Retired normative spellings: `filter`, `given`, `fold`, `QSystem`.

### 3.8 Token triage (Lexer / Parser — ADR 0035)

Normative token map: `docs/architecture/staqex-token-specification.md`.

| Class | Behavior | Examples |
|-------|----------|----------|
| **Active** | Keyword tokens | `class`, `interface`, `package`, `import`, `fn`, `state`, `let`, `mix`, `coin`, `dirac`, `vacuum`, `evolve`, `measure`, `snapshot`, `inspect` |
| **Forbidden** | Hard compile error | `if`, `switch`, `while`, `for`, `break`, `return`, `new`, `null`, `try`, `catch`, `throw`, `Thread`, `async`, `await` |
| **Retired** | Hard diagnostic + migration hint | `observe`→`measure`, `span`→`mix`, `when`→`mix` (no alias), `fn`→`fn`, `trait`→`interface` |
| **Pipeline op** | Left-associative callable application | `\|>` → `Pipe`; `lhs \|> f(a)` means `f(lhs, a)` |

```staqex
// state y = x |> phase(theta) |> evolve_under(H, 1.0.s)

// currying — still open (Call chains)
// state y = rot(theta)(x)
```

---

## 4. Narrative example (full)

```staqex
state c = coin()
state x = dirac(5)

state z = mix (c) {
    0 -> x + 10,
    1 -> x + 20,
    else -> x + 30,
}

state (w1, w2) = evolve (z) {
    let a = z * 2
    let b = a + 5
    (a, b)
}

measure w1
```

---

## 5. Open questions

| # | Topic | Status |
|---|--------|--------|
| 1 | `evolve` repetition: `times N` / `until … max N` | **Done** — ADR 0079 / LISS-0012 |
| 2 | Formal semantics core + §Span/Block/Evolve/Tuple | **Done** |
| 3 | PoC A/B fixtures | **Done** |
| 4 | Numeric literals vs mandatory `dirac(c)` | TBD |
| 5 | `mix` amplitude-linear reading | MVP mixture done; lift = ADR 0016 |
| 6 | AST design note (multi-arm) | **Done** |
| 7 | `\|\>` / currying specs | **Pipeline MVP done; partial application open** — ADR 0080 / LISS-0013 |
| 8 | Agent sync handoff doc | **Done** |
| 9 | Type system (`State<T>` / lift) | **Done** — ADR 0018 |
| 10 | Generics / `interface` / `class` | **Done** — ADR 0019 + 0024 |
| 11 | `map` / `project` / `interfer` / `System` | **Done** — ADR 0021 |
| 11b | Packages / Kotlin DX / universal lift | **Done** — ADR 0024 |
| 12 | `State<String>` / `Float` / `/` ops | **Open** |

---

## 6. Kernel PoC surface (minimal)

PoC A/B do **not** require `mix` / `evolve` / packages yet:

```staqex
state x = coin()
state y = x + x
measure y
```

```staqex
state a = dirac(1)
state b = dirac(2)
state c = a + b
state d = c * c
state e = d - a
measure e
```
