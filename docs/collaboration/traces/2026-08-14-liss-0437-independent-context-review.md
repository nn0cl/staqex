# AI work trace: LISS-0437 independent review cycle

## Request and routing

The user requested an independent-context review of the existing Issue, ADR,
Spec, and WorkPlan, iterative correction, reviewer-perspective documentation,
and a new Red-test phase only after the plan was sufficiently reviewed. A
fresh subagent context was used for the first review; it was instructed to
read the operating contract and the named implementation/design artifacts,
and to make no edits.

## Evidence reviewed

- `docs/architecture/adr/0209-explicit-blackboard-evolution-surface.md`
- `docs/specs/staqex-explicit-evolution-surface.md`
- `docs/work-plans/WP-0100-explicit-evolution-surface.md`
- `docs/issues/LISS-0437-explicit-evolution-surface.md`
- S02 `examples/official/S02/main_selection.sqx`
- parser, AST, typecheck, runtime evaluator, QPU IR, and QASM lowering

## Review 1 result

The reviewer found seven issues: the contract was not frozen, explicit mode
was absent from the current semantic model, operator/state and operator-exp
capabilities crossed AST domains, dimensions and unitary validity were
underspecified, QPU realization metadata was incomplete, Red scope was too
broad, and migration/corpus preservation was incomplete.

## Corrections made

- Froze `exp(Operator)` and `Operator * State<T>` as canonical spellings.
- Defined explicit `Evolve()` as a third mode, separate from pushforward and
  the migration-only Hamiltonian shortcut.
- Defined `EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED` and the other acceptance
  diagnostics.
- Froze dimensionless exponents, real `hbar`, identity/zero behavior, and
  unitary-target rejection of unsupported non-Hermitian transforms.
- Made formal `Limit` source-preserving but MVP target-rejected.
- Narrowed Phase 1 Red to observable source/compiler contracts.
- Recorded the reviewer perspective for reuse in later design and code review.

## Next gate

Run a second fresh-context review of the corrected artifacts. If it passes,
record Phase 1 Red permission and create tests only; do not implement the
compiler in this cycle.

## Review 2 result and correction

Review 2 found the WP's remaining S02 numerical-equivalence wording, an
under-specified dimension contract, and an under-specified migration failure
mode. The WP now keeps S02 as a text/parse fixture only; the Spec defines the
domains and dimensions for state application and operator powers; and ADR
0209/Spec define the migration diagnostic as a compile error with no
executable or partial artifact. The final independent pass found no contract
blocker. Because a reviewer cannot grant phase approval, the user's explicit
request to create Red tests after sufficient review is recorded as Phase 1
Red approval: tests only, implementation and migration forbidden, with later
Green/implementation approval required.

## User approval

On 2026-08-14, the user approved the reusable meta-review perspective ledger
and the corresponding AGENTS/development-flow updates. This approval covers
the review process documentation only. It does not grant LISS-0437 Phase 2,
production implementation, technology selection, or QPU deployment approval.

## Phase 2 Green implementation

On 2026-08-14 the user explicitly approved Phase 2 implementation for
LISS-0437. The primary agent consulted the independent-review perspectives
ledger before implementation and applied all nine lenses.

Implemented files:

- `compiler/staqex/ast_nodes.py`
- `compiler/staqex/parser.py`
- `compiler/staqex/typecheck.py`
- `compiler/staqex/hir.py`
- `compiler/staqex/pipeline.py`
- `examples/showcase/S02_drug_discovery/main_selection.sqx`
- `tests/test_liss_0437_explicit_evolution_surface_red.py`

Verification:

- LISS-0437 acceptance tests: Green
- S02 compile: Green
- LISS-0436 `times N` regression slice: Green
- Hamiltonian `until` runtime slice: Green
- Python compileall: Green
- `git diff --check`: Green

Remaining work is target realization, full corpus migration, numerical
equivalence, and Phase 3 review/refinement. No QPU deployment approval is
inferred.

## Phase 2 implementation review — initial result

The first implementation review returned **Not ready**. It found that the
runtime only handled a named canonical propagator, QPU rejection could retain
previous gates, strict migration handling was not exposed, explicit unitarity
and provenance evidence were incomplete, qsem deferral was too broad, and
the source/IR boundary needed stronger evidence.

The corrections are recorded in
`docs/collaboration/reviews/2026-08-14-liss-0437-phase2-implementation-review.md`.
A fresh independent re-review is required before marking Phase 2
final-review-ready.

## Phase 2 implementation review — second result

The fresh re-review confirmed inline and named runtime execution, complete
QPU fail-closed rejection, strict migration rejection, DAG provenance, and
regression coverage. It found two residual issues: Hermiticity analysis did
not retain dimensioned coefficient symbols, and malformed explicit bodies
duplicated diagnostics. Both were corrected and directly probed; a final
independent pass remains required.

## Final independent verification

The final fresh-context check confirmed the two corrective probes and all
previous Phase 2 conditions. Its remaining `Not ready` items are the
out-of-scope QPU realization, formal `Limit` execution, broad migration, and
Phase 3 numerical equivalence. Phase 2 is complete for the approved minimum
implementation slice, with those residuals carried forward explicitly.
