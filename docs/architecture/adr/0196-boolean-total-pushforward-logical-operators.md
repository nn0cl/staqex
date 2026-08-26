# ADR 0196: `&&` / `||` as total-pushforward Boolean operators (general expression position)

## Status

**Accepted** (2026-08-07) — Architecture Path decision, approved by the
Adjudicator. Investigated while triaging LISS-0338's deferred "Related,
not blocking" gaps (originally logged as `&&` unsupported in expression
position); found to be a documented, intentional design deferral, not
an oversight bug — this ADR is the design work
`docs/architecture/staqex-type-system.md` itself names as required
before any Kernel implementation. Acceptance approves the semantic
decision and grammar-insertion approach; it does not by itself
authorize implementation — the Local Issue named in §Follow-up still
needs its own separate Plan approval, per CLAUDE.md's Issue-Level
Autonomy.

## Design check

- **Scope and expected behavior:** general-expression `&&`/`||` between
  two `Bool`-carrier operands (`Classical<Bool>` or `State<Bool>`),
  usable anywhere a normal binary expression is (function bodies,
  `return` statements, `when`/`mix` guards, etc.) — not the existing,
  separate Operator-DSL binder-guard `&&`/`||` (`sum(...) where i < j
  && ...`), which already works and is out of scope here. Proposed
  semantics: a **total pushforward**, exactly like every other
  `State<T>` binary op already shipped (`+`, `-`, `*`) — both operands
  always evaluated, in every Joint world, combined via the ordinary
  Boolean truth table; **no classical short-circuit** (no
  conditionally skipping the right operand's evaluation based on the
  left operand's value).
- **Specifications and files inspected:**
  `docs/architecture/staqex-type-system.md` §3 carrier table (`Bool`:
  "no short-circuit ops") and §MVP-allowed ops / §Deferred-research
  tables — the authoritative, **already-existing** normative statement
  on this exact question: `&&`/`||`/`!` marked "as pushforward TBD";
  short-circuit `&&`/`||` explicitly listed under "Deferred / research
  (do not implement in Kernel)" with the reason given verbatim:
  "Classical short-circuit = early discard; must be total pushforward
  / `when`." `docs/architecture/staqex-language-spec.md` line 309/704
  (`when` is not classical short-circuit `switch`; general note on
  short-circuit `if`) — confirms the same non-discard principle applies
  project-wide, not just to this one operator pair.
  `docs/architecture/decision-themes/dec-0002-state-first-semantics-and-measurement.md`
  (current accepted surface: "Every overloaded op on `State<T>` is a
  pushforward on the joint, never an early collapse" — the general
  principle this ADR applies to `&&`/`||` specifically) and
  `dec-0003-language-surface-and-physicist-first-dx.md` ("legacy `if`
  ... exception-style control are not part of the language" — confirms
  no accidental reintroduction of classical branching semantics via
  this operator). `compiler/staqex/parser.py`: confirmed live —
  `TokenKind.AND`/`TokenKind.OR` are lexed but matched **only** inside
  `_op_guard`/`_op_guard_and` (the Operator-DSL binder-guard
  sub-grammar, `_op_expression`'s own chain); `_expression`'s chain
  (`_expression → _pipe → _comparison → _term → _factor → _unary`) has
  no logical-OR/logical-AND precedence level at all. Confirmed live via
  a minimal repro (`return a && b` inside a `Bool`-returning free
  function): the parser silently stops the `return` expression at `a`,
  then attempts to parse `&& b` as the start of a new statement,
  surfacing as the unrelated-looking `RETURN_NOT_TERMINAL` diagnostic
  — not a direct "unsupported operator" error, which is why this read
  as a vague "not supported" gap rather than an intentional deferral
  until this investigation traced it to the type-system spec's own
  explicit table. `grep` confirmed only one existing test
  (`test_binder_compound_where_red.py`) references `&&` at all, and it
  exercises the existing, separate, unaffected Operator-DSL guard
  grammar — no existing test asserts general-expression `&&` must fail
  to parse, so this proposal does not contradict any current
  intentional-failure contract.
- **Component boundaries, ports/adapters, and VO/DTO candidates:**
  Kernel-internal language surface only (lexer already emits the
  tokens; parser's general-expression grammar; `typecheck.py`'s
  `_infer_binop`; `evaluator.py`'s classical and State pushforward
  evaluation). No new port — this is pure language semantics, no
  external resource involved.
- **Applicable constraints:** Never Leave the State (no operator may
  introduce a hidden classical branch or early-discard escape hatch).
  No silent reinterpretation of the existing Operator-DSL `&&`/`||`
  tokens — this proposal adds a **separate** grammar production
  reachable only from general-expression context, leaving the
  Operator-DSL binder-guard meaning completely untouched (same pattern
  already used elsewhere in this grammar for tokens whose meaning
  depends on Operator-DSL vs. general-expression context). Matches the
  precedence structure the Operator-DSL guard grammar already
  establishes (`_op_guard` → `_op_guard_and` → `_op_comparison`, i.e.
  OR binds loosest, AND next, comparison innermost) — reused for the
  new general-expression levels rather than inventing a different
  ordering.
- **Decisions, assumptions, unresolved ambiguities:**
  - **Decided by this proposal:** total-pushforward semantics (both
    operands always evaluated; truth-table combination per Joint
    world for `State<Bool>`, or directly for `Classical<Bool>`); new
    precedence levels `_logical_or`/`_logical_and` inserted between
    `_pipe` and `_comparison` in `_expression`'s chain.
  - **Explicitly out of scope, left for a separate future decision:**
    unary `!` (logical NOT) — `staqex-type-system.md`'s own table
    groups `&&`/`||`/`!` together as "TBD," but `!`'s pushforward
    semantics (simple per-world negation) is a smaller, independent
    question with its own precedence-level and grammar-token
    considerations; bundling it here would widen this ADR's surface
    without a driving need (no LISS-0338 finding named `!` as blocking
    anything). A future ADR or a small addendum to this one, once
    accepted, can add it.
  - **Unresolved, flagged for the Adjudicator:** whether `Never Leave
    the State`'s "no classical short-circuit" principle should also
    extend to disallowing short-circuit **evaluation-order guarantees**
    entirely (i.e., must implementations be free to evaluate `right`
    before `left`, since nothing may depend on order without violating
    total-pushforward purity?), or whether left-to-right evaluation
    order should still be a documented guarantee for predictability
    even though both sides always run. This proposal defaults to
    guaranteeing left-to-right evaluation order (matching every other
    existing `BinOp` in the language) since nothing in the type-system
    spec's language suggests order should be unspecified, but flags
    this as worth an explicit Adjudicator confirmation rather than a
    silent default.
- **Included and omitted AI context:** Included direct reads of the
  authoritative type-system spec's own deferred-ops table (the
  decisive evidence for this ADR's premise), the current parser's
  actual precedence chain (confirmed via source, not assumed), and a
  live repro of the current failure mode. Omitted: no external
  AI/model call was used for this design check — the semantic
  reasoning (why short-circuit conflicts with pushforward purity) is
  derived directly from the project's own already-accepted principle
  ("every overloaded op ... is a pushforward ... never an early
  collapse"), not invented here.
- **Task routing:** Architecture review for the semantics decision;
  deterministic source inspection for all current-state claims; no
  external AI/model call for this design check.
- **Verification plan:** After acceptance, a Local Issue (own Plan/
  Completion approval) implements: (1) `_logical_or`/`_logical_and`
  parser levels; (2) `typecheck.py` cases for `Classical<Bool>
  &&/|| Classical<Bool> -> Classical<Bool>` and `State<Bool> &&/||
  State<Bool> -> State<Bool>` (dimension-check: both operands must
  already be `Bool`-payload, no implicit truthiness coercion from
  other types); (3) `evaluator.py` pushforward evaluation (elementwise
  truth-table application, per Joint world for the State case); (4) a
  test explicitly demonstrating **non**-short-circuit evaluation (e.g.
  both operands are evaluated even when the left alone would determine
  the classical short-circuit answer in a conventional language),
  since that is this ADR's whole point and the easiest property to
  accidentally regress if a future implementer reaches for Python's own
  `and`/`or` short-circuit operators without noticing the difference.

## Context

LISS-0338 (A11's rewrite) found `&&` unusable in expression position
and logged it as a small, deferred "classical-language gap" alongside
two other unrelated small findings. Triaging that backlog (this
session, after WP-0095's completion) started from the assumption this
was an oversight bug of the same shape as the three siblings already
fixed (LISS-0349/0352/0353 — each a narrow, single-function fix
mirroring already-correct sibling code). Investigating it live instead
surfaced that `&&`/`||` have **zero** grammar support outside the
Operator-DSL's own binder-guard sub-grammar, and tracing *why* led to
`staqex-type-system.md`'s own explicit table: short-circuit `&&`/`||`
are listed under "Deferred / research (do not implement in Kernel)"
with the stated reason that classical short-circuit conflicts with
this project's core "Never Leave the State" pushforward principle.
This is not a bug to patch — it is the specific, named research item
the type-system spec itself says must be designed (as a "total
pushforward") before any Kernel implementation is appropriate. This
ADR is that design work.

## Decision proposal

### 1. New grammar precedence levels, general-expression context only

Insert `_logical_or` and `_logical_and` into `_expression`'s existing
chain, between `_pipe` and `_comparison`:

```text
_expression → _pipe → _logical_or → _logical_and → _comparison → _term → _factor → _unary → ...
```

`_logical_or` matches `TokenKind.OR` (`||`), `_logical_and` matches
`TokenKind.AND` (`&&`) — the same tokens the lexer already emits, and
the same relative precedence (OR loosest, AND tighter) the
Operator-DSL's own `_op_guard`/`_op_guard_and` already establishes for
its separate sub-grammar. This is a **new, separate** production
reachable only from `_expression` (general classical/state expression
context); `_op_expression` (Operator-DSL context) is completely
unchanged — the existing binder-guard `&&`/`||` keeps its current
meaning and code path.

### 2. Total-pushforward semantics — no short-circuit, ever

For `Classical<Bool> op Classical<Bool>` (`op` ∈ `{&&, ||}`):
type-checks to `Classical<Bool>`; both operands are evaluated
unconditionally; the result is the ordinary Boolean truth-table
combination.

For `State<Bool> op State<Bool>`: type-checks to `State<Bool>`; both
operands are evaluated as an ordinary pushforward over every world in
the Joint (exactly the same execution shape `+`/`-`/`*` already use for
other `State<T>` binary ops — no special-casing, no early pruning of
any world based on one operand's value); the truth-table combination
is applied per-world. This is the concrete meaning of "total
pushforward": nothing about `&&`/`||` differs mechanically from any
other already-shipped `State<T>` binary operator except which truth
table it applies.

Mixed `Classical<Bool> op State<Bool>` is rejected with the same
`EXPECT_CLASSICAL_ONLY_ERROR`-style diagnostic every other
classical/quantum mixing attempt already receives (ADR-established
Born-rule boundary, unchanged by this proposal — no new mixing rule
invented here).

### 3. `!` (logical NOT) — explicitly deferred, not decided here

`staqex-type-system.md`'s table names `!` alongside `&&`/`||` as
"pushforward TBD," but this proposal deliberately does not include it
— no LISS-0338 finding named it as blocking anything, and its
pushforward semantics (simple per-world negation, no binary-operand
truth table) is independent enough to warrant its own, smaller,
separate ADR (or an addendum to this one) once this proposal is
accepted, rather than widening this decision's surface now.

## Robustness audit — does this survive a physicist expanding, transforming, or composing expressions freely?

Requested explicitly (2026-08-07) before implementation could proceed:
does introducing `&&`/`||` risk a *silent* breakdown somewhere else in
the Kernel once a physicist starts algebraically expanding, rewriting,
or composing expressions that now include them — not just "does the
operator itself work in isolation"? Checked every existing Kernel pass
that pattern-matches on a specific, enumerated operator set, since
those are exactly the places a new operator could either be silently
mishandled or silently ignored in a way that produces a wrong answer
rather than an explicit rejection.

- **Operator Fusion (ADR 0137/0141/0143/0157, `_parse_poly` /
  `_compose_poly_pipe`)**: confirmed live in source
  (`evaluator.py::_parse_poly`) — this pass recognizes exactly `+`,
  `-`, `*`, numeric literals, and the pipe parameter; any other
  `BinOp.op` (including the proposed `&&`/`||`) falls through to an
  explicit `return None`, and every caller of `_compose_poly_pipe`
  already treats `None` as "not eligible for fusion, fall back to the
  unfused per-stage evaluation path." **Fails closed, not silently
  mishandled** — a pipe chain containing `&&`/`||` simply does not get
  the fusion optimization (correct, if slightly slower); it does not
  get miscompiled as if it were arithmetic.
- **Trace-Out GC (ADR 0138/0142/0153/0158, `_trace_out_dead_fn_locals`
  / `_trace_out_dead_caller_coords`)**: confirmed live in source — this
  pass operates purely on Joint-coordinate **liveness** (is a named
  coordinate still referenced downstream), never on which operator
  produced a coordinate's value. It is operator-agnostic by
  construction, so a `State<Bool>` coordinate produced via `&&`/`||` is
  traced exactly like any other `State<T>` coordinate — no special
  case needed, no risk found.
- **Runtime pushforward dispatch (`_apply_op`)**: confirmed live in
  source — this is the single function every `BinOp` (classical and
  State alike) routes through at evaluation time, and it already
  **fails closed** on any unrecognized `op` string
  (`raise KernelError(f"unknown op {op}")`) rather than silently
  returning a wrong value. Adding `&&`/`||` here is two new branches in
  an already-exhaustive, already-fail-closed dispatch — the existing
  architecture, not a new safety mechanism this ADR has to invent.
- **Non-short-circuit evaluation is already mechanically guaranteed by
  the existing calling convention**, not something `&&`/`||`'s
  implementation has to separately enforce: every `BinOp` evaluator
  call site (confirmed in `_eval_value`) already evaluates `lhs` and
  `rhs` fully, unconditionally, *before* calling `_apply_op(op, l, r)`
  — `_apply_op` only ever receives two already-computed values, never
  unevaluated sub-expressions. There is no lazy/short-circuit control
  flow anywhere in this call path to accidentally inherit; a future
  implementer would have to *deliberately* write new short-circuiting
  code to violate total-pushforward purity, not merely reach for a
  convenient existing helper.
- **Operator-DSL / general-expression grammar boundary**: confirmed
  live in source (`parser.py`) — `_op_expression()`/`_op_guard()` are
  invoked only from specific, syntactically fixed call sites (e.g.
  inside `Operator`-typed bindings, `sum(...)`/`product(...)` binder
  bodies, Operator-DSL index/argument positions), never as a
  speculative "try this grammar, fall back to that one" dispatch from
  general-expression parsing. The parser always knows which grammar it
  is in from surrounding syntax, so the two separate `&&` meanings
  (Operator-DSL guard vs. this ADR's new general-expression operator)
  cannot collide or be misparsed into each other.
- **Composes correctly with this session's own recent fixes**:
  LISS-0352 (Classical relational comparisons now correctly type as
  `Classical<Bool>`, not `Classical<Float>`) means an expression like
  `a > b && c < d` already produces two well-typed `Classical<Bool>`
  operands for this ADR's `&&` to consume — the two fixes compose
  without any additional bridging work.

No breaking interaction found in any pass audited. This does not
prove the *absence* of every possible future issue — it is a targeted
audit of the specific mechanisms (operator whitelists, short-circuit
risk, grammar ambiguity) most likely to silently break under exactly
the kind of free algebraic composition a physicist would do, not an
exhaustive proof of correctness for every possible future Kernel pass.

## Consequences

- `&&`/`||` become usable in ordinary function bodies, `return`
  statements, and anywhere else a general Boolean expression is
  needed — closing LISS-0338's originally-logged gap, correctly
  understood as a design-deferral closure rather than a bug fix.
- The Operator-DSL's existing binder-guard `&&`/`||` is completely
  unaffected — different grammar production, different code path,
  same existing meaning.
- Establishes total-pushforward as the concrete, implementable pattern
  for *any* future Boolean/logical operator this language adds (`!`
  included, when it gets its own decision) — not just precedent for
  these two.
- `docs/architecture/decision-themes/dec-0002-state-first-semantics-and-measurement.md`
  (current accepted surface page) will need a short addition recording
  this decision once accepted, per ADR 0188's rule that new ADRs must
  also update their affected `DEC-*` page — not done in this proposal
  itself, since the page states "Accepted current surface" and should
  only change after Architecture approval, not alongside a still-
  Proposed ADR.

## Rejected alternatives

### Classical short-circuit semantics (conventional imperative `&&`/`||`)

Rejected — not a style preference but a direct conflict with this
project's own already-accepted principle (`dec-0002`: "every
overloaded op on `State<T>` is a pushforward on the joint, never an
early collapse") and the type-system spec's own explicit instruction
not to implement it. Short-circuit evaluation means some worlds' right
operand is never evaluated depending on the left operand's per-world
value — an early, value-dependent discard, exactly the pattern Never
Leave the State forbids elsewhere in the language.

### Reusing the Operator-DSL's existing `&&`/`||` grammar/token handling for general expressions too

Rejected. The Operator-DSL binder guard (`sum(...) where i < j && ...`)
is a **compile-time predicate over index combinations**, not a runtime
value operator over `Bool`-carrier values at all — it has no Joint,
no worlds, no pushforward concept in play. Collapsing the two into one
grammar production would make the same token mean two structurally
different things depending on context in a way that is harder to
reason about than keeping them as two separate, independently-correct
productions (the pattern this grammar already uses elsewhere for
context-dependent token meaning).

## Follow-up work required after acceptance

1. New Local Issue (next free `LISS-####`), parented to this ADR:
   `_logical_or`/`_logical_and` parser levels; `typecheck.py` cases for
   both `Classical<Bool>` and `State<Bool>`; `evaluator.py` pushforward
   evaluation for both; a test explicitly asserting non-short-circuit
   evaluation (both operands always run). Own Plan/Completion approval,
   per CLAUDE.md's Issue-Level Autonomy — this ADR's acceptance does
   not itself authorize that Issue's implementation.
2. Update `dec-0002-state-first-semantics-and-measurement.md` with a
   short line recording the accepted decision, per ADR 0188's
   DEC-page-update rule — done as part of that same Local Issue's
   Refactor phase, not before.
3. Separately, not blocking this ADR: a future ADR (or addendum) for
   unary `!`'s pushforward semantics, if and when needed.

## Acceptance boundary

Acceptance of this ADR approves the semantic decision (total-
pushforward, non-short-circuit `&&`/`||` in general expression
position, `!` explicitly excluded) and the grammar-insertion approach
(new `_logical_or`/`_logical_and` levels, Operator-DSL guard grammar
untouched). It does **not** authorize any implementation — the Local
Issue named in Follow-up still needs its own separate Plan approval,
per CLAUDE.md's Issue-Level Autonomy.
