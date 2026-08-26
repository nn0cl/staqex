# Staqex AST design note

Status: **Accepted design baseline** (updated 2026-07-23 for ADR 0024
Kotlin DX / packages / `mix` / `class`).
Phase 2.1 reference implementation: `compiler/staqex/` (Python).
Hold unsealed for Kernel PoC / parser / AST / typechecker (ADR 0034).

Companions:
- Umbrella: `docs/architecture/staqex-language-spec.md` (ADR 0024)
- Sync snapshot: `docs/collaboration/agent-sync-staqex-baseline.md`
- Surface: `docs/architecture/staqex-syntax-vocabulary.md` (ADR 0017 → 0024)
- Types: `docs/architecture/staqex-type-system.md` (ADR 0018 + lifting §)
- Semantics: `docs/specs/staqex-formal-semantics-sketch.md`
- Positioning: `docs/architecture/staqex-positioning.md`

---

## 1. Design axis

Narrative, types, and formal semantics share one evaluation type for pure
statements:

\[
\llbracket \mathsf{Stmt} \rrbracket : \mathsf{Joint} \to \mathsf{Joint}
\]

Axes are typed carriers `T`; runtime bindings are `State<T>` (ADR 0018).
`Measure` is the sole exception: it may consume `RngPort` and collapse a
marginal to Dirac (classical `T` only after that point). Classical control
nodes that imply jump, discard, or early exit are **not** part of the AST.

---

## 2. First-class nodes (no `If` / `While` / `Return`)

```text
CompilationUnit = { package: PackageDecl?,
                    imports: [ImportDecl],
                    decls: [Decl],
                    entry: MainDecl?,              // pub fn main
                    // script-style: Stmt* desugars to implicit MainDecl
                    stmts: [Stmt] }

PackageDecl = { path: [Ident] }                 // com.physics.optics
ImportDecl  = { path: [Ident], name: Ident }    // import P.Name

Program     = CompilationUnit                   // preferred
            | [Stmt]                            // Kernel script sugar

Stmt        = StateBind { pat: Pat, expr: Expr }
            | Measure   { expr: Expr, sink: SinkExpr? }  // final in main
            | Snapshot { expr: Expr, sink: SinkExpr }   // non-collapsing log

Pat         = Name(Ident)
            | Tuple([Ident])                    // §Tuple bind-out

Expr        = Coin
            | Dirac(LitCarrier)
            | Lit(LitCarrier)                   // elaborates via lift → Dirac
            | Var(Ident)
            | BinOp { op: BinOp, lhs: Expr, rhs: Expr }
            | WhenExpr { ctrl: Expr, arms: PatternMatchArms }  // surface `mix`
            | Span { … }                        // deprecated alias ≡ WhenExpr
            | Evolve { seeds: [Expr], body: Block }
            | BlockExpr(Block)
            | TupleExpr([Expr])
            | Map { src: Expr, fn: FnExpr }
            | Project { src: Expr, pred: FnExpr }
            | Interfer { items: [Expr], init: Expr, fn: FnExpr }
            | Pipe { lhs: Expr, rhs: Expr }
            | Call { callee: Expr, args: [Expr] }
            | CtorCall { ty: Path, args: [Expr] }   // Foo(args) — no New
            | MethodCall { recv: Expr, name: Ident, args: [Expr] }
| Inspect { expr: Expr, label: Expr? }      // ADR 0030 passthrough

Decl        = FnDecl | ExtFnDecl | TraitDef | InterfaceDef
            | ClassDecl | MainDecl | …

TraitDef / InterfaceDef
            = { name: Ident, methods: [MethodSig] }  // e.g. System
ClassDecl   = { name: Ident, params: [TypeParam],
                ifaces: [Ident],                    // : System
                fields: [StateField],
                methods: [MethodDef],
                visibility: Visibility }
MainDecl / EntryPoint
            = { name: Ident,                 // must be `main`
                visibility: Public,
                params: [Param],             // () or (args: State<List<String>>)
                body: Block }                // last Stmt must be Measure
ExtFnDecl   = { recv: Type, name: Ident, params: [Param],
                ret: Type, body: Block }            // T.f(…)
FnDecl      = { name: Ident, … }                   // surface `fn`

StateField  = { name: Ident, ty: Type }             // State<T>
MethodDef   = { name: Ident, self: bool, params: [Param],
                ret: Type, body: Block }            // measure-free by default
FnExpr      = …

PatternMatchArms = [WhenArm]
WhenArm     = { pat: WhenPat, body: Expr }
WhenPat     = Atom(LitCarrier) | Wildcard          // `else` → Wildcard

Block       = { locals: [LocalBind], result: Expr }
LocalBind   = { name: Ident, expr: Expr }           // `let` / ancilla `_x`

BinOp       = Add | Sub | Mul | Eq | Ne | Lt | Le | Gt | Ge  // → State<Bool>
Vacuum      = …                         // State.vacuum() prep (ADR 0034)
```

Surface `mix (c) { 0 -> e0; 1 -> e1; else -> e2 }` parses to `WhenExpr`.
Historical `span` sugar maps to the same node. There is **no** `New` expr.

### Rejected nodes (do not add)

| Node | Why rejected |
|------|----------------|
| `If` / `Else` / `Switch` | Jump + discard arm ≈ early collapse |
| `While` / `For` / `Break` | Classical loop; use `Evolve` |
| `Return` / `Break` | Early exit; tears joint / forbids §4 |
| Imperative `Block` as Stmt-list with unit | Blocks are **Expr** kernels, not stack frames |
| Mid-program `Measure` as Expr | Collapse is final `Stmt` of `main` only |
| `Measure` not last in `MainDecl` | Early Collapse Error (ADR 0027) |
| Classical `Int` return from `main` | Use MeasureSinkPort; no int main |
| `Throw` / `Try` / `Catch` | Non-local escape; breaks norm / early collapse (ADR 0025) |
| `Null` / `None` literals as bottoms | Use `mix` basis labels / `Error` arms |
| `Thread` / `Async` / `Await` / `Spawn` / `Mutex` | Concurrency = `mix` / joint (ADR 0028) |
| Mid-pure `File.write` / socket send of State | Early collapse (ADR 0029) |
| Using `Measure` as a debug print of a PMF | Use `Inspect` (ADR 0030) |
| In-place field assignment / mutable `this` | Immutable capsules (ADR 0033) |

### Token triage (ADR 0035)

Canonical: `staqex-token-specification.md`. Forbidden lexemes must not
become `Ident`. Active keywords drive grammar terminals.

### Reserved (design intent)

| Surface | AST placeholder | Status |
|---------|-----------------|--------|
| `e \|> f` | `Pipe` / token `PipeOp` | Reserved — ADR 0035 |
| Curried apply | `Call` | Spec TBD |
| `map` / `project` / `interfer` | `Map` / `Project` / `Interfer` | ADR 0021 |
| `package` / `import` | `PackageDecl` / `ImportDecl` | ADR 0024 |
| `mix` | `WhenExpr` | ADR 0024 (≡ §Span) |
| `class` / `interface` / `fn` | `ClassDecl` / `TraitDef` / `FnDecl` | ADR 0024 |
| Extension `fn T.f` | `ExtFnDecl` | ADR 0024 |
| Keyword `system` / `span` / `fn` | aliases → Class / When / Fun | Retired surface |
| `pub fn main` | `MainDecl` / `EntryPoint` | ADR 0027 |

See `staqex-language-spec.md`, `staqex-abstraction-model.md`, `staqex-stdlib-combinators.md`.

---

## 3. Syntax → semantics map

| Surface | AST node | Semantic section | Denotation sketch |
|---------|----------|------------------|-------------------|
| `state p = e` | `StateBind` | §1–2 | Extend/replace coordinates via pushforward |
| `coin()` / `dirac(c)` | `Coin` / `Dirac` | §1 | Bernoulli / Dirac prep |
| `x ⊕ y` | `BinOp` | §2 | Pushforward; correlation law |
| `mix (c) { arms }` | `WhenExpr` | §3 | Controlled mixture; all positive arms kept |
| `span …` (legacy) | `WhenExpr` | §3 | Alias only |
| `{ let …; e }` | `BlockExpr` / `Block` | §4 | Pure kernel; locals traced out |
| `evolve (…) {…}` | `Evolve` | §5 | Seed + Block + outer bind |
| `let` in block | `LocalBind` | §4 | Temporary joint axis (ancilla-like) |
| `(a, b)` | `TupleExpr` | §6 | Simultaneous pushforward; skip trace-out of components |
| `state (w1,w2)=…` | `StateBind` + `Pat::Tuple` | §6 | Multi-coordinate bind-out |
| `map` / `project` / `interfer` | `Map` / `Project` / `Interfer` | §7–8 / ADR 0021 | Pure stdlib combinators |
| `interface System` | `TraitDef` | ADR 0021–0024 | Measure-free `step` |
| `class Foo : System` | `ClassDecl` | ADR 0024 | Compound joint capsule |
| `package` / `import` | `PackageDecl` / `ImportDecl` | ADR 0024 | Subsystem namespace borders |
| `fn T.f` | `ExtFnDecl` | ADR 0024 | Extension / dot-chain |
| `Foo(args)` | `CtorCall` | ADR 0024 | No `new` |
| `pub fn main(…)` | `MainDecl` | ADR 0027 | Entry; body ends with Measure |
| `measure e` / `measure e to S` | `Measure` | §9 / ADR 0027–0029 | Sole RNG; last in `main`; optional sink |
| `snapshot e to S` | `Snapshot` | ADR 0029 | Host log joint; no RngPort; joint unchanged |
| `e.inspect(…)` | `Inspect` | ADR 0030 | Debug view; identity on joint; no RngPort |
| `\|\>` / curry | reserved | — | Hold until dedicated specs |

---

## 4. Evaluation contract

```text
eval_pure    : (Joint, Stmt \ Measure) → Joint
eval_measure : (Joint, Measure, Rng) → (Joint, Atom)   // one draw
eval_program : Joint₀ ; Stmt* → Joint                  // Measure last only
```

Static rules (design intent):

1. At most one `Measure` in `MainDecl` body, and it must be the last stmt.
2. No `Measure` nested in `Expr` / `Block` / non-entry `fn`.
3. `WhenExpr` arms: ≥1; at most one `Wildcard`/`else`; concrete atoms unique.
4. Bit-control sugar only when desugar target is well-defined.
5. `Pat::Tuple` arity equals RHS `TupleExpr` arity.
6. At most one `PackageDecl` per compilation unit; imports precede decls.
7. No `New` node; construction is `CtorCall` / `Call`.

---

## 5. Suggested Rust sketch (illustrative — not implemented)

```rust
pub enum Stmt {
    StateBind { pat: Pat, expr: Expr },
    Measure { expr: Expr },
}

pub enum Expr {
    Coin,
    Dirac(i64),
    Lit(i64),
    Var(Ident),
    BinOp { op: BinOp, lhs: Box<Expr>, rhs: Box<Expr> },
    WhenExpr { ctrl: Box<Expr>, arms: Vec<WhenArm> },
    Evolve { seeds: Vec<Expr>, body: Block },
    Block(Block),
    Tuple(Vec<Expr>),
    Map { src: Box<Expr>, /* fn */ },
    Project { src: Box<Expr>, /* pred */ },
    Interfer { items: Vec<Expr>, init: Box<Expr>, /* fn */ },
    CtorCall { /* ty, args */ },
    MethodCall { /* recv, name, args */ },
}

pub struct WhenArm {
    pub pat: WhenPat,
    pub body: Expr,
}

pub enum WhenPat {
    Atom(/* LitCarrier */),
    Wildcard, // else
}

// Also: PackageDecl, ImportDecl, ClassDecl, ExtFnDecl, MainDecl.
```

Domain evaluation must thread a single `Joint`, never `HashMap<Ident, i64>`.

---

## 6. Scope relative to Kernel PoC

| Construct | In PoC A/B today | In AST design |
|-----------|------------------|---------------|
| `StateBind`, `BinOp`, `Coin`/`Dirac`, `Measure` | Yes | Yes |
| `WhenExpr` / `Block` / `Evolve` / `Tuple` | No | Yes (normative) |
| `PackageDecl` / `ImportDecl` / `ClassDecl` | No | Yes (ADR 0024) |
| `Pipe` / curry | No | Reserved only |

**Hold unsealed** (ADR 0034). Order: Kernel → When/Block → Evolve/Tuple →
`MainDecl`+measure → Vacuum/Bool compares/Prelude → packages/class → opts.

---

## 7. Open follow-ups

- Typed AST (`Expr` carrying `State<T>` / inferred carriers) — see type system §8.
- `Evolve` repetition (`times` / `until`).
- Specs for `|>`, currying.
- Package path ↔ filesystem; visibility levels.
- Extension resolution / orphan rules.
- `Lit` always lifts (ADR 0024); `dirac` remains explicit prep.
- Amplitude reinterpretation of `WhenExpr` (ADR 0016).
- `State<String>` concat fixtures (not Kernel A/B).
