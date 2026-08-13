# ADR 0207: literal Σ/∀/min/projector transcription for S02 selection semantics (supersedes ADR 0192/0194)

## Status

**Accepted** (2026-08-13) — approved by the Adjudicator, drafted by Claude
Code from a direct, term-by-term equation-to-program review (S02
`main_selection.sqx` step 2). Acceptance approves the physics/semantics
design (the ten decisions below) and that it supersedes ADR 0192/0194; it
does not by itself authorize implementation of any Local Issue — per
CLAUDE.md's Claude Code Issue-Level and Work-Plan Autonomy rules, each
Issue still needs the batch record
(`docs/collaboration/reviews/execution-batch-s02-step2-literal-transcription.json`)
set to `approved_for_execution` before Red may start. Full investigation
record: `/Users/nn0cl/.claude/plans/zany-juggling-hejlsberg.md` (this session's
plan file; the actual back-and-forth that produced this design is in the
session transcript, not reproduced here).

## Design check

- **Scope and expected behavior:** S02's step 2
  ($\lvert\psi_{sel}\rangle=P_F\lvert\psi_0\rangle/\lVert P_F\lvert\psi_0\rangle\rVert$,
  $P_F=\sum_{x\in F}\lvert x\rangle\langle x\rvert$) is currently realized by
  `project psi_sel onto feasible(exactly_selected=3, pairwise_compatible=true,
  diversity_at_least=0.3)` — numerically correct but opaque: the closed
  vocabulary ADR 0192/0194 chose never represents $\sum_{x\in F}$, $F$'s own
  membership predicate ($\forall$/$\min$-based), or the projector's
  renormalization as literal source, the same "opaque native primitive
  standing in for a blackboard Σ" problem `prepare_selection(n)` was for
  step 1 before LISS-0420/0421. This ADR proposes ten new/changed language
  primitives (below) so step 2 is a literal, symbol-for-symbol
  transcription, and retires `feasible(...)` entirely once the general
  capability exists.
- **Specifications and files inspected:** `compiler/staqex/parser.py`
  (`_op_binder`, `_op_guard`, `_binder_domain`, `_ket_or_outer`/`projector`
  desugaring, `TokenKind.ARROW`/`FAT_ARROW` already taken);
  `compiler/staqex/typecheck.py` (`_check_algebra_call`'s `projector`
  State-only requirement); `compiler/staqex/finite_binder.py`
  (`_fold_operator_terms`, `_OPERATOR_DSL_RESERVED_ATOMS`, `OpCall`
  currently rejected at lowering); `compiler/staqex/runtime/hamiltonian.py`
  (`OpHop`/`_eval_fock` confirmed Fock-only, not reusable for the n-qubit
  projector term); `compiler/staqex/runtime/evaluator.py`
  (`_bind_apply`'s unitary-only requirement confirms `apply` cannot carry a
  projector; `project`'s existing "Renormalize after Lüders projection"
  block, `_bind_feasible_predicate`'s real closed-vocabulary predicate
  logic); `compiler/staqex/unitarity_check.py` (`_expr_is_quantum`, already
  extended for `KetSumBinder` in LISS-0421). ADR 0192
  (`0192-s02-projector-selection-semantics.md`) and ADR 0194
  (`0194-host-input-port-and-selection-predicate-semantics.md`), both
  Accepted 2026-08-05 — this ADR supersedes both.
- **Component boundaries, ports/adapters, VO/DTO candidates:** Kernel
  compiler front-end (parser/typecheck) and runtime
  (`finite_binder.py`/`hamiltonian.py`/`evaluator.py`) only. No new port —
  `Set`/`ForAll`/`Min`/`Implies`/`||·||` are language/runtime additions, not
  external resources. `Bool[n][n]`/`Float[n][n]` Host-bound arrays reuse the
  existing `HostInputPort`/ADR 0119 coefficient-tensor path already used by
  step 3's `activity_w`/`selectivity_w` — no new Host contract.
- **Applicable constraints:** Physicist-first / source-must-denote-the-same-
  physics-as-the-blackboard (`adjudicator-language-vision.md` §2.2, DEC-
  0003). No implicit normalization (LISS-0422 precedent, extended here to
  `project` itself). No back-compat alias for retired spellings
  (`fun`→`fn`/`evolve{}.run()`/`Index<...>`-retirement precedent).
- **Decisions, assumptions, unresolved ambiguities:** see the ten numbered
  decisions below; `Min`'s empty-guard-match behavior is explicitly left
  open for the implementing Issue's own Red phase, not decided here.
- **Included and omitted AI context:** Included direct reads of every file
  above, not assumed from memory (two self-corrections happened during the
  investigation and are preserved in the transcript: an initial "$\forall$/
  $\min$ equation is unsourced invention" claim was itself wrong — it was a
  faithful transcription of the real, already-running
  `_bind_feasible_predicate`/`host/scoring.py::is_feasible` Python logic).
  Omitted: performance characteristics of eager Pauli-Z-decomposition
  unrolling at scale (deferred to the implementing Issue's own numeric
  verification, LISS-TBD-S8).
- **Task routing:** Architecture review for the semantics/scope decision;
  deterministic source inspection for all current-state claims; no external
  AI/model call.
- **Verification plan:** see `zany-juggling-hejlsberg.md`'s own
  "Verification" section — per-Issue Red→Green→Refactor, full regression +
  spec verification after each Issue, numeric cross-check of the Pauli-Z
  decomposition, byte-identical terminal-distribution check for the final
  `main_selection.sqx` rewrite against the current baseline.

## Decision

Accept, if the Adjudicator approves, all ten of the following as one
coherent design (they are interdependent — see
`zany-juggling-hejlsberg.md`'s Local Issue dependency graph):

1. **`Set F = { x In D : cond1, cond2, ... }`** — set-builder/comprehension
   producing a reusable domain value; conditions are comma-separated
   (implicit conjunction, matching the equation's own notation), not
   `&&`-joined.
2. **`Sigma (x In F)`** accepts any `Set`-typed domain, not only literal
   `{0,1}^n`.
3. **Bound-variable projector term `|x><x|`** inside a `Sigma` body over a
   `Set`/`{0,1}^n` domain, lowered via
   $\lvert x\rangle\langle x\rvert=\bigotimes_i\frac{I+(-1)^{x_i}Z_i}{2}$,
   eager per-element expansion at `finite_binder.py` lowering time.
4. **Bare-range binder domains: `i In 0..n-1`, retiring `Index<...>`** as a
   binder-domain spelling (hard cutover, no back-compat alias) — migrates
   the already-shipped `objective_hamiltonian`'s three `Sigma`/`Pi` binders
   too.
5. **Classical numeric `Sigma`** — a third result-kind for the existing
   `Sigma` keyword (Int/Float array-element sum), alongside the existing
   Operator-typed and State-typed (`KetSumBinder`) forms.
6. **`ForAll` binder (new)** — $\forall$, Bool-valued, comma-separated guard.
7. **`Min` binder (new)** — $\min$, numeric-valued, comma-separated guard;
   empty-match behavior decided during its own Issue's Red.
8. **`Implies` keyword operator (new)** for $\Rightarrow$ — not `->`/`=>`
   (both already taken: function return types/lambdas, and match arms
   respectively — confirmed by reading `tokens.py`, not assumed).
9. **`||State||` norm notation (new)** computing
   $\sqrt{\sum_x\lvert c_x\rvert^2}$, and **`State / Float` division
   (new)** (the scaling counterpart to the already-shipped
   `Float * State`, LISS-0420/0422). Together these let renormalization be
   written explicitly as `X / ||X||`, matching
   $P_F\lvert\psi_0\rangle/\lVert P_F\lvert\psi_0\rangle\rVert$ token-for-
   token, including the equation's own repetition of the numerator
   expression inside the norm.
10. **`project` drops its implicit renormalization entirely** (all forms,
    not only a new general-Operator path — the existing "Renormalize after
    Lüders projection" block is deleted, not replaced by a
    `normalize(...)` function, since decision 9 already covers explicit
    renormalization at the call site) **and gains the ability to accept a
    general multi-term `Operator`** as its projection target, not only a
    basis label. **`feasible(...)` is retired outright** (not kept
    alongside the general mechanism) — Host data moves to the plain
    `host(...)`-bound-array pattern step 3 already uses. This is why ADR
    0192/0194 are superseded rather than merely amended: their central
    premise (a closed-vocabulary predicate set) no longer has a reason to
    exist once decisions 1-9 are in place.

## Consequences

- ADR 0192 and ADR 0194 are superseded. Their `Projector<Selection>`
  closed-vocabulary design and `feasible(...)`/`_bind_feasible_predicate`
  implementation are retired once this ADR's Local Issues ship.
- `main_selection.sqx` step 2 becomes a literal, term-by-term transcription
  of the confirmed equation (recorded in `zany-juggling-hejlsberg.md`).
- The `objective_hamiltonian` function (step 3, already shipped) is touched
  incidentally by decision 4's `Index<...>` retirement — spelling only, no
  behavior change, full regression sweep is the evidence.
- Ten Local Issues (`LISS-TBD-S1`…`S11`, see `zany-juggling-hejlsberg.md`)
  are required before this ADR's design is realized. None may start Red
  until this ADR is Accepted and the corresponding batch record is set to
  `approved_for_execution` by the Adjudicator — investigation/ADR-drafting
  authorizes neither.
