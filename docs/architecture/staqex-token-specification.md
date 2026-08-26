# Staqex token specification (Lexer / Parser)

Status: **Accepted** (2026-07-23). ADR **0035**.
Step 2 implementation input for Lexer / Parser (Hold unsealed for parser/AST).

Sources: `staqex-syntax-vocabulary.md` §3.8 vocabulary triage; AST design;
`spelling-cheat-sheet.md`; language-spec lock index.

---

## 0. Triage classes

| Class | Lexer / Parser behavior |
|-------|-------------------------|
| **Active** | Emit keyword tokens; parse as grammar terminals |
| **Forbidden** | Lexeme recognized → **hard compile error** (do not parse as Ident) |
| **Retired** | Lexeme recognized → parse may recover, but **linter/diagnostic must warn** with fix-it |
| **Reserved ops** | Tokenize now; AST may hold placeholder nodes; full semantics later |

---

## 1. Active keywords (tokenize)

Exact spellings (ASCII, case-sensitive as written):

```text
class  interface  package  import  fn
state  let  when
coin  dirac  vacuum
evolve  measure  snapshot  inspect
```

| Keyword | Role |
|---------|------|
| `class` / `interface` | Capsule / capability |
| `package` / `import` | Subsystem namespace |
| `fn` | Function / method / extension |
| `state` | Joint coordinate bind |
| `let` | Block / evolve local only |
| `mix` | Controlled mixture |
| `coin` / `dirac` / `vacuum` | Preparation (may also appear as prelude calls) |
| `evolve` | Pure evolution block |
| `measure` | Terminal collapse |
| `snapshot` | Non-collapsing checkpoint |
| `inspect` | Non-destructive debug |

**Notes for implementers:**

- `coin` / `dirac` / `vacuum` / `inspect` may be parsed as keyword **or** as
  call forms `coin()` / `dirac(e)` / `vacuum()` / `e.inspect(...)` — pick one
  consistent lexer strategy (keyword + `(` sugar is fine).
- Prelude names (`map`, `project`, `interfer`, `Math`, `File`, `Success`,
  `Error`) are **not** required to be hard keywords in Step 2; treat as
  identifiers resolved by prelude / stdlib unless a later ADR hardens them.
- Soft / contextual: `else`, `true`, `false`, `static`, `to` (in
  `measure e to …`), `times` / `for` (in `evolve … times N` /
  `evolve … for dt`) — **contextual keywords** in Parser, not exclusive
  Ident bans.

---

## 2. Forbidden keywords (hard error at Lexer or Parser)

If the source contains these as identifiers/keywords, **fail compilation**:

```text
if  switch  while  break  return
new  null
try  catch  throw
Thread  async  await
```

Suggested diagnostics (stable `code` ids later):

| Lexeme | Message |
|--------|---------|
| `if` | `Syntax Error: 'if' is forbidden in Staqex. Use 'when' for state superposition.` |
| `switch` | `… Use 'when' …` |
| `while` | `… Use 'evolve' for pure iteration …` |
| `break` / `return` | `… Early exit is forbidden; use block result / evolve …` |
| `new` | `… Construct with Foo(args); 'new' is forbidden.` |
| `null` | `… Use Result / when basis labels / Vacuum; 'null' is forbidden.` |
| `try` / `catch` / `throw` | `… Exceptions are forbidden; use Result + mix / project.` |
| `Thread` / `async` / `await` | `… Concurrency is when / joint product; threads/async are forbidden.` |

**Note (ADR 0037):** bare C-style `for (` loops remain rejected by the
parser (not a statement form). The lexeme **`for`** is a **contextual**
keyword only in `evolve (seeds…) for duration {…}` (Time / `Delta<Time>`).
It is **not** a Forbidden hard-lex error (moved out of the Forbidden set).

Do **not** silently treat Forbidden as `Ident` (that would hide axiom violations).

Related bans (may share Forbidden class in a follow-up): `None`, `synchronized`,
`Mutex`, `spawn` — align with AST rejected nodes / cheat sheet when convenient.

---

## 3. Retired keywords (linter / spell-check; auto-fix suggestion)

Lexer may still tokenize these as Ident or dedicated Retired tokens; **Parser
must not treat them as Active grammar**. Linter / `staqex check` warns:

| Retired | Suggest |
|---------|---------|
| `observe` | `measure` |
| `span` | `mix` |
| `when` | `mix` (hard diagnostic; no compatibility alias) |
| `fun` | `fn` |
| `trait` | `interface` |

Broader retired set (linter catalog, not all hard Lexer tokens): `filter` /
`given` / `fold` → `project` / `interfer`; keyword `system` → `class`;
`QSystem` / `Evolvable` → `System` (see cheat sheet).

Severity: **warning** with fix-it in Step 2 tooling; may become error in a
later style lock.

---

## 4. Reserved operators (AST placeholders)

| Lexeme | Token | AST | Semantics |
|--------|-------|-----|-----------|
| `\|>` | `PipeOp` | `Pipe` | Reserved — compose pushforwards / unitaries (spec TBD) |

Lexer **must** recognize `\|>` as one token (not `|` then `>`).

Currying remains grammar/precedence TBD; no mandatory multi-token reserved
form beyond normal `Call` chains in Step 2.

Also reserved (not operator tokens): `evolve` **`times` / `for` / `until`**
clause keywords (`for` = duration with Time dim, ADR 0037; `until` still Open).
keywords when that grammar lands — do not use as user Idents in future
keyword reservation lists.

---

## 5. Suggested token enum (illustrative)

```text
KeywordClass | KeywordInterface | KeywordPackage | KeywordImport | KeywordFun
KeywordState | KeywordLet | KeywordWhen
KeywordCoin | KeywordDirac | KeywordVacuum
KeywordEvolve | KeywordMeasure | KeywordSnapshot | KeywordInspect

ForbiddenIf | ForbiddenSwitch | … | ForbiddenAwait   // or single Forbidden(lexeme)

Ident
PipeOp          // |>
// plus LitInt, LitFloat, LitString, punctuators, …
```

---

## 6. Step 2 acceptance (Lexer / Parser)

1. All Active keywords lex distinctly from `Ident`.
2. Each Forbidden lexeme produces a compile error with a Staqex-guidance message.
3. Retired lexemes do not parse as Active; tooling emits fix-it warnings.
4. `\|>` is a single token; may appear in source only if Parser allows
   reserved `Pipe` AST (or errors “reserved / unimplemented”).
5. Kernel PoC subset may start with a smaller Active set (`state`, `coin`,
   `dirac`, `measure`, …) but **must not** accept Forbidden as Ident.
