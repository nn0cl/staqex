# LISS-0320 `superpose` formal grammar — design, Red, Green, Refactor

## Current State

- Current phase: phase-3-refactor, complete. Status **complete** — Adjudicator
  granted Plan approval and Completion approval; PR #345
  (https://github.com/nn0cl/staqex/pull/345), CI green (3/3 checks passed),
  mergeable.
- User request: continue Staqex WP-0092 work; pick a minimal, non-mixed
  scope (`superpose` grammar OR `controlled` grammar, not both) and follow
  Feature Path DESIGN CHECK → spec update → Phase 1 approval gate.
- Canonical issue: [LISS-0320](../../issues/LISS-0320-superpose-formal-grammar.md).
- Work plan: [WP-0092](../../work-plans/WP-0092-quantum-mental-model-follow-up.md).

## Included context

- AGENTS.md, `docs/architecture/agent-quickstart.md`,
  `docs/architecture/open-work-register.md`, ADR 0189, ADR 0190, WP-0092,
  `staqex-v1-quantum-mental-model-follow-up.md` §4.
- Current shipped code: `compiler/staqex/tokens.py` (ACTIVE/RETIRED tables),
  `parser.py` (`_when_expr`, `_parse_h1_experiment_body`), `ast_nodes.py`
  (`WhenExpr`/`WhenArm`, `H1Superposition`), `typecheck.py` (WhenExpr typing),
  `runtime/evaluator.py` (`_bind_when` and other `WhenExpr` dispatch sites).
- `tests/test_quantum_composition_surface_red.py` (PR #344, already green —
  tests only the shallow H1 heuristic, not the formal grammar this Issue
  targets).

## Omitted context

- `controlled` grammar (deliberately deferred to its own Issue).
- QASM/QPU target lowering internals.
- S02 domain-specific code (unrelated benchmark).
- Rust VM (future generation, same semantics, not started).

## Model / tool routing

- Design and spec authoring: this session (Claude Sonnet 5), no external AI
  call.
- Verification: deterministic — `pytest`, `tests/spec_verification/run_all.py`,
  `git diff --check`.

## Execution record — attempt 1 (design only)

- Re-verified `main` at `c4a9756` (PR #344 merged): `pytest tests/ -q` →
  `1205 passed`; `tests/spec_verification/run_all.py` → `161/161`; `git diff
  --check` clean.
- Read PR #344's diff directly (`ast_nodes.py`, `h1_authoring.py`,
  `parser.py`) to confirm the shipped `superpose` recognition is the shallow
  `_parse_h1_experiment_body` line-lexeme scanner, not a real grammar rule —
  this determined the Issue's actual remaining scope.
- Created branch `feature/liss-0320-superpose-formal-grammar` (not on
  `main`, per AGENTS.md).
- Added spec §4.5 (Gherkin acceptance scenarios for the formal-grammar
  slice) to `docs/specs/staqex-v1-quantum-mental-model-follow-up.md`.
- Filed `docs/issues/LISS-0320-superpose-formal-grammar.md`.
- No test or implementation code written yet — stopped for Plan approval per
  CLAUDE.md "Claude Code Issue-Level and Work-Plan Autonomy."

## Execution record — attempt 2 (Plan approved → Red → Green → Refactor)

- Adjudicator granted Plan approval for LISS-0320 (bare "承認" in direct
  response to the explicit single-item Plan-approval question). Per
  CLAUDE.md Issue-Level Autonomy, proceeded through Red → Green → Refactor
  without a further per-phase check-in.
- **Phase 1 Red** (commit `06e4d6a`): added
  `tests/test_liss_0320_superpose_formal_grammar_red.py` implementing spec
  §4.5's four scenarios using the same `pub fn main()` ordinary-surface
  style as `tests/test_s02_selection_surface_red.py` (not `experiment {}`,
  which is the separate H1-heuristic path). Confirmed live baseline first:
  `superpose (control) { 0 -> |0>, 1 -> |1>, }` on the ordinary surface
  fails with `PARSE_ERROR: expected RBRACE, got \`->\`` (superpose isn't in
  any token table). 3/4 tests failed for that reason; the regression test
  (mix/when unaffected) passed unchanged, confirming baseline untouched.
- **Phase 2 Green** (commit `d375fd9`): implemented `SuperposeExpr` end to
  end — `TokenKind.SUPERPOSE` (own kind, not a `WHEN` reuse), AST
  `SuperposeArm`/`SuperposeExpr`, parser `_superpose_expr` mirroring
  `_when_expr`, typecheck arm-unification to `State<T>`. Discovered
  mid-implementation (not anticipated in the design trace) that this alone
  left `compiled.ok` false: `LINEAR_IMPLICIT_DISCARD` fired because
  `hir.py`'s linear-resource walker (`_expr_children`,
  `_consume_when_linear_uses`) only special-cased `WhenExpr`, so
  `superpose`'s control variable was never marked consumed. Fixed by adding
  `SuperposeExpr` to those two functions (mirroring `WhenExpr`'s handling
  exactly). The two `QSEM_*` diagnostics that also appeared
  (`QSEM_FINITE_EVIDENCE_MISSING`, `QSEM_APPROXIMATION_OBLIGATION_MISSING`)
  turned out to be soft/non-blocking for *every* program per
  `pipeline.py`'s own docstring ("QSEM_* diagnostics stay non-hard") — no
  fix needed there. Also discovered the Red test's evaluation-guard
  scenario imported the wrong `run_source` (`compiler.staqex.run`, which
  does not catch `KernelDiagnosticError`); corrected the import to
  `compiler.staqex.host.run_source` (the function that already converts
  `KernelDiagnosticError` into `JobResult.diagnostics`, per the existing
  `EVOLVE_UNTIL_MAX_STEPS_ERROR` precedent in
  `tests/test_evolve_until_runtime_red.py`) and matched its
  `settings={...}` call shape. No assertion was weakened. Added
  `KernelDiagnosticError("COHERENT_EXECUTION_UNSUPPORTED", ...)` in
  `runtime/evaluator.py::_bind` for `SuperposeExpr`, plus `SuperposeExpr`
  cases in the two generic walkers `_expr_has_inspect`/`_expr_free_vars`
  for consistency with every other `Expr` node type. Note: did **not**
  check every other file with `WhenExpr` references
  (`unitarity_check.py`, `physical_axioms.py`, `pipeline.py`,
  `nested_when.py`, `ir/dag.py`, `backend/qasm/lower.py`) — none were
  reached by this slice's tests, so none were touched. A future slice
  (real coherent execution, or `superpose` used in more contexts) may
  surface the same missing-case gap in one of those files.
- **Phase 3 Refactor** (same commit `d375fd9`): merged two identical
  `isinstance(expr, WhenExpr) / isinstance(expr, SuperposeExpr)` branches
  in `hir.py::_expr_children` into one `isinstance(expr, (WhenExpr,
  SuperposeExpr))` check, matching the style already used in the other
  three touched call sites. Re-ran full verification after — no behavior
  change.
- **Doc sync** (this commit): LISS-0320 exit criteria checked off, status
  → `final-review-ready` (not `complete` — no PR/merge yet, per
  `definition-of-done.md`'s Phase 3 closeout procedure); WP-0092 work unit
  2 and a new "Phase 3 closeout" section updated to match; this trace
  updated. `open-work-register.md` deliberately **not** updated yet — it
  should only describe this as shipped after Completion approval + merge.

## Adjudicator decisions

- Granted: Plan approval for LISS-0320.
- Granted: Completion approval for LISS-0320.
- Granted: push + PR authorization (explicit confirmation via AskUserQuestion
  before pushing, per this session's operating rules for actions visible to
  others). Branch pushed to `origin`; PR #345 opened.
- Pending: explicit merge confirmation — not yet requested or granted.

## Assumptions

- `superpose` needs its own `TokenKind`, not a reuse of `TokenKind.WHEN`
  (unlike `mix`), so `SuperposeExpr` is structurally distinguishable from
  `WhenExpr` at parse time.
- The evaluator guard (fail-closed diagnostic on attempted evaluation) is a
  baseline safety inclusion in this slice, not the separately-scoped
  target-lowering/capability-rejection work item.

## Open decisions

- Exact diagnostic code name for the evaluator guard — implemented as
  `COHERENT_EXECUTION_UNSUPPORTED` (the proposed name); still open for
  Adjudicator preference/rename at Completion review.
- Whether arm-pattern exhaustiveness rules should mirror `WhenExpr`'s
  `_check_when_enum_exhaustive` — resolved for this slice: deliberately
  **not** replicated (see Phase 2 Green record and LISS-0320's reviewer
  empathy summary). Open for reconsideration when a future slice makes
  `superpose` executable.
- Whether `open-work-register.md` should be updated now or only after PR
  merge — this trace defers it to post-merge, consistent with how the
  register's own job is to reflect actually-shipped state.

## Verification run (final, after Phase 3)

```text
.venv/bin/python3 -m pytest tests/test_liss_0320_superpose_formal_grammar_red.py -v
  → 4 passed
.venv/bin/python3 -m pytest tests/ -q                         → 1209 passed
.venv/bin/python3 -m pytest tests/test_h1_5_control_lane_classification_red.py \
  tests/test_quantum_composition_surface_red.py \
  tests/test_s02_selection_surface_red.py -v                  → 9 passed
.venv/bin/python3 tests/spec_verification/run_all.py          → 161/161, 100%
git diff --check                                              → clean
```

## Changed files (cumulative, this Issue)

- `docs/specs/staqex-v1-quantum-mental-model-follow-up.md` (new §4.5)
- `docs/issues/LISS-0320-superpose-formal-grammar.md` (new; now final-review-ready)
- `docs/collaboration/traces/2026-08-04-liss-0320-superpose-formal-grammar-design.md` (this file)
- `docs/work-plans/WP-0092-quantum-mental-model-follow-up.md` (work unit 2 + new Phase 3 closeout section)
- `tests/test_liss_0320_superpose_formal_grammar_red.py` (new)
- `compiler/staqex/tokens.py` (`TokenKind.SUPERPOSE`, ACTIVE entry)
- `compiler/staqex/ast_nodes.py` (`SuperposeArm`, `SuperposeExpr`, `Expr` union)
- `compiler/staqex/parser.py` (`_superpose_expr`, dispatch, statement-start predicate)
- `compiler/staqex/typecheck.py` (`SuperposeExpr` → `State<T>` inference)
- `compiler/staqex/hir.py` (linear-resource walker: `_expr_children`, `_consume_when_linear_uses`)
- `compiler/staqex/runtime/evaluator.py` (`_expr_has_inspect`, `_expr_free_vars`, `_bind` guard)

## Next safe action

PR #345 is open with CI green and `mergeable`. This completion-packet commit
(Issue/work-plan/trace synchronized to `complete`, PR #345 referenced) still
needs to land on the PR and pass CI again before merge, per
`definition-of-done.md`'s Completion gate procedure. Do not merge without a
separate explicit Adjudicator confirmation — merging to `main` was not yet
authorized as of this commit. After merge, synchronize
`docs/architecture/open-work-register.md` to reflect the shipped `superpose`
formal grammar.
