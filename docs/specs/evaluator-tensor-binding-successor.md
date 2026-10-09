# Evaluator Tensor binding successor

Status: accepted — dedicated Issue/spec T01–T09, bounded guard disposition and
Phase 0 acceptance explicitly approved by human on2026-10-09. Requirements
unchanged. Phase 1 Red execution explicitly approved2026-10-09 and tests
prepared; [execution/test-review entry](../collaboration/reviews/2026-10-09-liss-0585-phase1-execution.md)
reports166passed/4structural Red. [Phase1 review](../collaboration/reviews/2026-10-09-liss-0585-phase1-review.md)
passed after human-authorized R1/R2 test-only corrections:168pass/4structural Red.
Human corrected-test acceptance and separate Phase2 implementation explicitly
approved2026-10-09; minimal move implemented, all-blocking verification pending.
[Phase2 provisional results](../collaboration/reviews/2026-10-09-liss-0585-phase2-verification.md).
T01–T09, accepted tests, assertions and guard disposition unchanged.
Owner: [LISS-0585](../issues/LISS-0585-evaluator-tensor-binding-successor.md),
WP-0174 rank 4. Scope/design continuation authorized by human `続けて` after
the single Tensor binding Phase 0 proposal. Phase1 execution approval does not
authorize test acceptance, Green implementation or later delivery.

## [DESIGN CHECK]

- Scope and expected behavior: Architecture Path / Phase 0; separate the
  cohesive `_bind_tensor` body without changing existing semantics or errors.
- Specifications and files inspected: language specification §5.3, DEC-0005;
  evaluator, Joint, binding/context/compatibility; Tensor behavior tests and
  LISS-0582/0583/0584 preservation guards. Baseline main a349a5b7.
- Component boundaries, ports/adapters, and VO/DTO candidates: proposed
  `runtime/evaluation/tensor_binding.py`, context-first
  `bind_tensor(context, joint, names, expr)`. Reuse Joint/World/TensorExpr;
  no new VO, state owner, external resource, adapter, provider or dependency.
- Applicable constraints: preserve source meaning, private callbacks, public
  imports, ordering, diagnostics and existing foreach/eligibility behavior.
- Decisions, assumptions, and unresolved ambiguities: retain `_bind_tensor`
  through an exact installer mapping; bounded guard disposition below is
  accepted for later separately approved Red preparation, not immediate
  permission to change assertions. Out-of-tree overrides unknown.
- Included and omitted AI context: directly affected runtime and acceptance
  evidence included; rank 5/6, Rust implementation, providers and secrets omitted.
- Task routing: host design, deterministic search/AST/pytest; configured review
  same_context, implementation host, empty model IDs; large-change override absent.
- Input/output evidence contract: Markdown proposal only; assertions must map
  to T01–T09 at Red review. No AI output enters the runtime.
- Verification plan: scoped baseline below; distinct Phase 0 acceptance, Red
  execution, test acceptance, Green implementation, Refactor, final and delivery gates.

## Current authority and actual consumers

[Language specification](staqex-language-specification.md#53-combinators-selected)
describes independent tensor products / wire relabeling;
[DEC-0005](../architecture/decision-themes/dec-0005-quantum-operations-and-runtime.md)
requires joint/worldline-preserving execution. This proposal does not redefine
tensor semantics, normalization, coalescing thresholds or the compiler surface.

| Owner / consumer | Current contract and disposition |
|---|---|
| evaluator.py `_bind_tensor`, lines 502–546 | 45 physical lines, including signature/docstring; sole body to extract |
| evaluation/binding.py `bind_names` | TensorExpr and direct `tensor` Call dispatch through context._bind_tensor; keep both paths and alias arity diagnostic |
| evaluation/binding.py `bind` | single-name TensorExpr rejection remains unchanged |
| evaluation/context.py `_bind_tensor`, `_bind` | existing declarations suffice; no protocol change proposed |
| runtime/joint.py `World`, `Joint`, `_coalesce` | reuse existing representation and interference/coalescing, do not move or rewrite |
| evaluation/compatibility.py and evaluator setup | add one exact private hook installer/import/setup, retain all existing mappings |
| run.py / pipeline / runtime facade | actual consumer smoke and source execution, not just direct successor import |
| tests/test_joint_preserve_and_harvest.py, test_qudit_slice_c_red.py | tuple binding in evolution/qudit programs |
| tests/test_ascii_tensor_parity_red.py, test_liss_0375_nested_when_tensor_dispatch_red.py, test_liss_0511_product_tensor_meaning_red.py | adjacent compiler grouping/alias/rejection and semantic-IR conservation |
| LISS-0582 public-import repair, LISS-0583 guard suites, LISS-0584 repair boundary | source-ownership preservation consumes evaluator/compatibility AST via shared guard support |

Static search finds two calls in bind_names and the context declaration. This
is a discoverable lower bound, not proof that external/private overrides do not
exist. Keep overridable context._bind and the callable private hook. Existing
Evaluator public export identities remain frozen; locally unused imports are
not automatically removable. No new public evaluator import is proposed.

## Accepted requirements T01–T09

| ID | Behavior and minimum executable acceptance inventory |
|---|---|
| T01 | Exactly two output names required; 0/1/3 names raise the existing exact tensor-bind KernelError before side callbacks. Direct `tensor` Call wrong arity and single-name TensorExpr retain their current exact diagnostics in binding.py. |
| T02 | Two Var operands on the existing Joint relabel each world, preserving shared amplitude, correlations, unrelated assignments and unrelated coordinate phases. Move source phases to corresponding output names; test nontrivial complex amplitudes/phases and multiple correlated worlds. Never form independent marginals in this branch. |
| T03 | Missing left/right coordinates raise the existing exact coordinate diagnostic at the first offending world; no independent binder calls. Input Joint/World dicts are not mutated. Empty incoming Joint in the Var branch stays empty. |
| T04 | Other operand shapes call the live context._bind on fresh Joint.unit() with name `_T`, left then right, and pass each original Expr unchanged. Test literals and mixed Var/non-Var through recording callbacks; propagate first/second callback errors at the existing point. Do not add callback caching, prevalidation, state copies or rollback. |
| T05 | Independent results form the ordered Cartesian product, left outer/right inner, with multiplied complex amplitudes and only the two requested assignments, then existing _coalesce. Test multi-world order, equal assignments/coalescing and cancellation. Keep existing independent-path coordinate-phase handling; do not introduce phase propagation as an extraction fix. Both callbacks run before the empty-side check, including empty left/right/both. Result is independent of incoming unrelated Joint worlds as in the current body. |
| T06 | Preserve assignment overwrite order for existing output names, identical output names, identical source names and swapped/reused names as current direct-runtime characterization. No new collision validation or compiler admission. These edge cases do not expand the language spec. |
| T07 | Successor owns the only implementation body; Evaluator has no duplicate `_bind_tensor` body. Exact installer maps Evaluator._bind_tensor to the identical bind_tensor function; real bind_names TensorExpr/alias dispatch reaches it. No runtime evaluator import, retained mutable state or copied maps in successor; context and Joint type references may be type-only. |
| T08 | Frozen evaluator wildcard/direct import names and object identities remain unchanged; preserve TensorExpr and every other intentional re-export. Actual cold consumer imports, source execution, and adjacent regressions are blocking. New imports in evaluator use underscore aliases. |
| T09 | Only tensor body extraction and its exact wiring change. Preserve every other executable body/import, foreach hook protections, all immutable fixtures, five repair-byte dependencies, TypeChecker and runtime-plan eligibility contracts. Review the bounded guard transition below before changing tests; prove real guard authorized positives and unauthorized negatives, not a rejecting-all substitute. |

EARS: When tuple tensor binding executes, the runtime shall preserve the
existing relabel-or-independent branch, evaluation order, world amplitudes and
diagnostics. When extraction changes ownership, callers shall retain the
private hook and public import compatibility without a second implementation.

## Accepted boundary and structure disposition

Use a stateless function with existing typed arguments, not a new service
object or broad utility module. `_bind` remains a narrow callback to the live
Evaluator, including subclass overrides. A private import of
`install_tensor_binding_compatibility` in evaluator plus its setup call and a
single mapping in compatibility.py follows the established foreach pattern.
binding.py and context.py remain unchanged. Installer function metadata will
reflect successor ownership; callable argument shape and behavior are retained,
not the former function object's identity with its old body.

Measured baseline physical sizes: evaluator 1099, binding 244, context 278,
compatibility 323. This extracts one 45-line responsibility, not a claim that
Evaluator's remaining responsibilities are fully separated. Numeric structure
settings absent: qualitative disposition is dedicated tensor ownership rather
than adding algebra to binding's dispatcher. Compatibility remains wiring only.
Resolved cycles, dynamic graph and out-of-tree consumers are unknown, not zero.
Future review must measure actual successor bodies as well as the facade.

## Accepted bounded guard disposition

At the Phase0 baseline, `tests/liss_0583_guard_support.py` projects exactly the foreach move;
its evaluator/compatibility unaffected-AST checks intentionally include the
tensor method. The shared checks are called by LISS-0582 repair tests,
LISS-0583 guard/migration tests and LISS-0584 readonly repair tests. A tensor
move would fail these guards even if behavior is preserved.

After dedicated spec acceptance and separate Red execution approval only:

1. Preserve original guard-baseline and repair-boundary JSON fixtures and their
   hashes/provenance byte-for-byte; never replace the historical base with main.
2. Introduce a narrowly specified tensor projection that reconstructs the old
   tensor method in its original class position from immutable evidence, and
   strips only the exact new private installer import/setup and compatibility
   import/mapping. Delegate all unaffected comparisons to existing foreach
   protections; permit no unrelated import, body, state or context change.
3. Preserve guard API names, current real consumer call sites, metadata checks,
   existing foreach positives/negatives and repair-byte checks. A test-only
   support addition and bounded projection change require explicit diff review;
   existing acceptance assertions are not waived. No runtime Git prerequisite.
4. Test the actual shared and readonly guards on temporary copies: current shape
   and approved tensor-extracted shape accepted; wrong/duplicate installer,
   wrong setup, changed/reintroduced tensor body, modified original exports,
   unrelated body/state and all existing foreach mutations rejected. Missing
   successor or changed successor algorithm must fail ownership/body evidence.
5. Freeze the original moved algorithm as executable AST, allowing only the
   declared self→context/signature/ownership changes; pair it with behavior
   assertions. Positive and negative results must pass together after Green.

The preservation boundary is executable AST/import identity, not comment or
formatting byte identity for evaluator/compatibility. Original byte-frozen
dependencies stay byte-frozen. Exact additional guard-support allowed paths
and clause-to-test matrix must be enumerated at Red review before Green.
No generic future-extraction exemption, hash refresh or exclusion is proposed.

## Phase 0 evidence and later verification

Clean main a349a5b720c59f3a0e288c4751dd012c25514843; macOS Darwin27.0.0 arm64,
Python3.12.6, pytest9.0.3. Scoped existing baseline: 109 passed in3.35s, exit0,
failures/errors/skips0. Exact command in the representative trace. No source,
test, fixture or lifecycle change. Root/spec/all-sanity not_run this Phase 0;
this is not whole-repository Green or verification of a future successor.

Later blocking commands: `python3 -m pytest tests/ -q` with only explicitly
accepted active-Red selectors from `scripts/check-test-lifecycle.py`;
`python3 tests/spec_verification/run_all.py`; every applicable Repository sanity
step in `.github/workflows/ci.yml`, including distributed-copy smoke after
commit. Declare focused/consumer/adjacent selectors at Red review. Rerun all
blocking after the final commit, identify actual SHA/environment and compare
failures. CI/human review and push/merge remain separate approvals.

Human approval: `LISS-0585 専用Issue/spec T01–T09・限定guard移行方針とPhase 0 acceptance承認`.
Acceptance changes no requirement or guard assertion. Human subsequently
`LISS-0585 Phase 1 Red（受入テスト作成・限定guard移行）の実行承認`
authorizes test-only preparation and exact guard migration. Human subsequently
`LISS-0585 Phase 1 Red テストレビュー／acceptance承認` accepts corrected tests,
R1/R2 dispositions and exact guard mapping unchanged. Human subsequently
`LISS-0585 Phase 2 Green／implementation承認` authorizes the minimal accepted
move, implemented without test changes. Human subsequently
`LISS-0585 ローカルコミット／実SHAで全blocking再検証` authorizes bounded
local commits and the actual-SHA all-blocking rerun. Results will be retained
outside the tree as linked by the Phase2 packet; no Phase3 or delivery authorization.
