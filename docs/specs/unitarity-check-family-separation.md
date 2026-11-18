# Unitarity判定family責務分離 — Phase 0 accepted specification

Status: Phase 0 accepted; corrected GU01–GU09 Phase 1 Red cohort re-accepted
2026-10-27; exact support-path Phase 2 Green locally verified; GU supplement
Phase 3 review and committed-SHA final verification passed locally on
`2907cf452fac4c7811b35d6ee0c25eb0ddc6cc11`; the GU supplement final review
result and its acceptance-record verification at
`3ab970ad84c5d4637f7734c114ccf2afaaec4735` were accepted on 2026-11-02; the
verification-record result at
`d152534d5bcd59100d0026aecff1d899bea60434` was accepted on 2026-11-04; the
subsequent verification at
`eb4d23030d78ab354da9d307ad0514d6770ad8fd` was also accepted on 2026-11-04;
the Active-Red deadline renewal verification at
`5f1111f4181ab83ddecd871f6d9f032aa1cc0e30` was accepted on 2026-11-16; its
acceptance-record verification at
`b93361dcb7d94f5dfcde6332ac919744e41ae39b` was accepted on 2026-11-17; the
verification-record SHA result at
`49bdc21faee237a0ec4e592fed38941470e03a08` was also accepted on 2026-11-17;
the subsequent verification at
`8a364e95a46d07b7913a1b16b18cc2ebd5aa0170` was accepted on 2026-11-17; the
acceptance-record verification at
`fa1cc39cf63a44e7a5f32bcc0d394773f1dce5e2` was also accepted on 2026-11-17;
the subsequent verification at
`8973aa4874c8a7617cec4c71e22331a6c5030c7f` was accepted on 2026-11-18; the
subsequent verification at
`75d24931324be40a571d70f7d48978cbb65e28fd` was accepted on 2026-11-18; the
subsequent verification at
`c3e79ab549b13b666b031bd92508026a3d0bba40` was also accepted on 2026-11-18.
The acceptance-record commit `a544e2a96e791f45a8b1165b775a94a1985ea9bc`
passed all blocking verification and was accepted on 2026-11-18.
The verification-result acceptance commit
`eb13dae2ae0d44856835c9c75c6bd20f8c6da0a0` passed all blocking verification
and was accepted on 2026-11-18.
The subsequent acceptance-record commit
`e322afea74675e800dc24048caa7101dbf927258` passed all blocking verification
and was accepted on 2026-11-18.
The subsequent acceptance commit
`cc124bb3a8b25426a2a4747df116cb3085079bed` passed all blocking verification
and was accepted on 2026-11-18.
The subsequent acceptance-record commit
`251e94127450a1312062dd17eb7936781a6dc3df` passed all blocking verification
and was accepted on 2026-11-18.
The main unitarity checker decomposition remains unimplemented.
Owner: [LISS-0594](../issues/LISS-0594-unitarity-check-family-separation.md).
Parent: [WP-0175](../work-plans/WP-0175-source-responsibility-inventory.md).
Base observed: `93a2548ae168a70a3c3340bf79533de95828dc39` (local `main`, 2026-10-23).
Authority: accepted core module decomposition and language/operator contracts;
ADRs 0045/0052 plus specific LISS-0411 and LISS-0436 safeguards. This proposal
does not amend those authorities.

## Design note

### Target behavior / question

Move cohesive implementation responsibilities out of
`compiler/staqex/unitarity_check.py` so contributors can understand the static
unitarity pass without loading a 933-line module, while retaining the current
entry point and exact language behavior. Total source lines may stay the same.

### Requested and proposed phase

- Requested: Phase 0 investigation/design only.
- Proposed next phase: Phase 1 Red, but only after separate acceptance of this
  specification and explicit Phase 1 approval.
- Implementation allowed: no.
- Post-review: Phase 1 Red requires separate explicit execution approval and
  test review/acceptance before any Green implementation.

### Specifications, consumers, and files inspected

- `docs/collaboration/reviews/2026-10-15-source-responsibility-inventory.md`
  and its WP-0175 owner record.
- `compiler/staqex/unitarity_check.py` (933 lines at the current base).
- `compiler/staqex/pipeline_legacy.py` direct import, pass order, and
  `HARD_CODES` consumer.
- `tests/test_liss_0411_static_operator_resolution_red.py`,
  `tests/test_liss_0436_evolve_times_block_transparency_red.py`,
  `tests/test_h1_6_operation_characteristics_red.py`, operator specs and
  verification suites. Test list is a static-search inventory, not a proven
  complete runtime consumer graph.
- `docs/architecture/staqex-core-module-decomposition.md`,
  `docs/collaboration/verification-policy.md`,
  `docs/collaboration/source-code-quality.md`, and
  `docs/collaboration/runtime-routing.toml`.

### Proposed boundaries (exact module layout pending review)

Candidate cohesive responsibilities:

1. The existing `check_unitarity(unit)` facade and ordered top-level analysis
   orchestration, retaining the import used by `pipeline_legacy` and direct
   tests.
2. Quantum/strict lineage classification and classical scalar eligibility.
3. Expression-site traversal and diagnostics, including `project`, `map`,
   `apply`/`capply`/`ocapply`, `WhenExpr`, and `EvolveExpr` cases.
4. `Evolve times N` transparency proof and recursive user-function body
   classification, including memoization and cycle behavior.
5. Static Operator application and Hamiltonian Hermiticity checks, including
   LISS-0411 object-field resolution, matrix builders, dimension handling, and
   quiet exception outcomes.
6. Shared closed-expression/AST helpers, with a single owner and no circular
   imports.

These are responsibilities to disposition, not an approved one-module-per-item
layout. A cohesive grouping may be preferable. `_check_measure_target` and
`_expr_is_classical_scalar` must be explicitly kept or moved with evidence;
they may not be changed under this refactor. Avoid turning every helper into a
module or creating a context object solely to hide the current mutable maps.

### Behavior and evidence contract

Preserve entrypoint signature/return type, diagnostic dictionary shape and
ordering, existing state/Operator/scalar/object maps and their mutation
timing, lexical function scope, recursive descent order, both Operator matrix
and Hermitian checks, AST walking semantics, `_EPS`, exception handling,
whitelists, and every current positive/negative outcome. In particular:

- LISS-0411 must continue to reject known non-unitary/static-invalid operator
  use without losing struct-field coefficient resolution.
- LISS-0436 must retain fail-closed opaque-transform rejection and its current
  recursive transparency/cycle behavior.
- No full proof of all pushforwards or broader soundness guarantee is claimed.
- Existing semantics that look surprising must be recorded as observed; a
  correction needs a separate accepted scope/spec.

### Explicit ambiguities / stop conditions

- Whether classical measurement eligibility remains in this pass or moves
  with another already-existing family is a required Phase 0 disposition.
- Whether the single `_children` iterator stays with expression traversal or
  becomes a small shared AST utility is not selected yet.
- Static import searches cannot prove third-party, dynamic, plugin, or
  serialized consumers. Any newly discovered public/private consumer widens
  the test inventory before acceptance.
- The actual current source hash must be re-pinned from Git immediately before
  Phase 1; the 2026-10-15 snapshot is not an immutable implementation base.
- Any finding that requires changing diagnostic policy, tolerance, canonical
  AST, public contracts, architecture, or upstream ADRs stops this refactor
  and requests a separate Adjudicator decision.

## Accepted Phase 0 criteria U01–U10

The exact acceptance matrix U01–U10 is canonical in the linked LISS-0594
issue. The Adjudicator explicitly accepted that issue/spec and all ten clauses
on 2026-10-23. They cover immutable base/hash manifest, actual consumers and
private edges, unique implementation ownership, public and diagnostic
compatibility, shared state and recursion, numerical/exception semantics,
LISS-0411/LISS-0436 inherited safeguards, explicit classical-measurement and
AST-helper disposition, consumer/adjacent Red coverage, and final-SHA
verification/structure budgets.

Phase 0 acceptance alone authorized no test, source, or fixture change.
Separate Phase 1 Red execution approval was explicitly received 2026-10-25.
That approval permits tests and active-Red lifecycle records only; it does not
permit production changes, test acceptance, implementation, commit, or remote
delivery.

Current Phase 1 checkpoint: the characterization cohort has one intended
structural Red and 23 focused/consumer passes, but adding its separate test
module causes six inherited LISS-0591/0592/0593 exact-path guard failures in
the broad pytest suite. No predecessor guard was changed. A bounded scope/spec
supplement is required before modifying those accepted path contracts; do not
weaken their exact assertions or historical evidence.

## Guard compatibility supplement — Phase 0 accepted GU01–GU09

Status: GU01–GU09 accepted by the Adjudicator on 2026-10-26. Owner remains
[LISS-0594](../issues/LISS-0594-unitarity-check-family-separation.md).

### Design note

- Target: allow exactly the already-authored LISS-0594 Phase 1 test module
  through the existing test-path composition used by LISS-0591/0592/0593
  guard consumers, without changing any historic membership or evidence.
- Phase 0 decision: GU01–GU09 accepted 2026-10-26.
- Current phase: GU compatibility supplement Phase 3 review and committed-SHA
  final verification passed locally on `638c8956f8f1ff2d8808ef2cba68e66bd18a5922`.
  Main unitarity decomposition remains unimplemented in Phase 1 Red.
- Next gate: Adjudicator accepts the GU supplement final-verification result.
  Main-source implementation and remote delivery remain separately gated.
- Implementation allowed: prior Phase 2 authorization was exercised for the
  exact singleton support change; it does not authorize main-source changes.
- Included: exact path declaration, `new_test_paths()` composition,
  `carrier_after()` projected behavior, existing count/path invariants,
  copied-root setup and named P10/R06/F09/G07 callers.
- Omitted: production source, earlier baseline fixtures/digests, source
  evidence/carrier byte changes, blanket allowlists, unrelated issue fixes.
- Ambiguity: whether any copied-root reader outside the observed P10/R06/F09/G07
  paths consumes this inventory remains unproven; the consumer search below is
  limited to tracked repository code and tests.
- Lesson application: raw-byte-guard-normalization and
  immutable-evidence-history-prerequisite require preserving original Git
  bytes/hash evidence and not replacing failures with regenerated snapshots.
  Migration-test-shape-invariance requires independently materialized pre and
  post roots with setup assertions. Readonly-inverse-artifact-existence
  requires the exact follow-on test file to physically exist in every accepted
  root and a deletion negative. Status-drift requires the active-Red Issue
  phase to remain exactly aligned with its lifecycle entry. The recursive AST
  walker lesson is out of scope for this path-only supplement.

### Proposed acceptance clauses

| ID | Proposed requirement |
|---|---|
| GU01 | Pin the current LISS-0594 test module path and SHA-256; treat it as one exact downstream artifact, not as a new member of the historical LISS-0593 semantic cohort. |
| GU02 | Preserve the existing LISS-0591/0593 `NEW_TESTS` and `NEW_FIXTURES` sets and their 26-path composed count. Declare a separate singleton follow-on path for `tests/test_liss_0594_unitarity_family_red.py`; no wildcard/glob or general future-test acceptance. |
| GU03 | Extend `new_test_paths()` composition so the current historical path reader and `carrier_after()`-generated LISS-0591 support both admit exactly that singleton path. The projected carrier must be derived from the original accepted Git bytes using one explicit raw substitution; do not replace whole files or regenerate baseline evidence. |
| GU04 | Preserve the historic path return contract: `historical_test_paths()` returns exactly the original LISS-0591 test cohort; the follow-on file is allowed as a current dependency but never silently added to the frozen historical cohort. |
| GU05 | Add positive and negative controls: current exact path accepted; one unrelated added path rejected; absent follow-on artifact rejected; absent historic artifact rejected. Prove the check reads actual files, not only cached Git inventories. |
| GU06 | In both genuinely constructed pre and post roots, copy the LISS-0594 test artifact and run the real LISS-0591 P10, LISS-0592 R06, and LISS-0593 F09/G07 consumers. Assert source-shape and test-path inventory separately before each consumer call. |
| GU07 | Keep the six originally observed failures named and compare their node IDs after the bounded change. No assertion deletion, skip/exclusion addition, regex relaxation, or change to historical hashes is allowed. |
| GU08 | Preserve all existing LISS-0593 test node IDs and semantic-cohort assertions; only add the exact follow-on path expectation and copied-root setup needed by this supplement. Add supplement tests to the existing LISS-0594 module, avoiding a second new path. |
| GU09 | At the supplement's final actual SHA, rerun focused compatibility cases, all six inherited consumers, LISS-0594 characterization/consumer tests, adjacent suites, spec verification and the declared full blocking pytest set. Report each group, environment, SHA, node/failure comparison and dirty state separately. |

### Exact candidate dependency map (Phase 0 evidence)

1. `tests/liss_0591_guard_support.py::historical_test_paths` already composes
   `NEW_TESTS | NEW_FIXTURES | new_test_paths()` and returns only the original
   baseline paths. No additional broad bypass is needed in that API.
2. `tests/liss_0593_guard_support.py::new_test_paths` currently validates and
   returns the LISS-0593's exact ten test/fixture paths. The proposal is to add
   a separate singleton follow-on set and include it in this reader, without
   changing the existing semantic `NEW_TESTS`/`NEW_FIXTURES` constants.
3. `tests/liss_0593_guard_support.py::carrier_after` reconstructs the exact
   accepted LISS-0591 support carrier, already composing the `new_test_paths`
   reader; its result and raw substitution must be independently verified.
4. `tests/test_liss_0593_guard_composition_red.py` stages partial roots from
   the core sets and has an exact `26`-path assertion. The proposed test-only
   update must copy the singleton path separately and preserve that assertion.
   Its full-root builder already copies actual `git ls-files --others` entries.
5. The observed root failures are LISS-0591 P10, LISS-0592 R06, and LISS-0593
   F09 pre/post and G07 pre/post. LISS-0592 consumes the LISS-0591 historical
   reader; it has no separately observed test-path allowlist to broaden.

Adjudicator decision: GU01–GU09 accepted on 2026-10-26. This accepts the
compatibility supplement's Phase 0 scope and criteria; by itself it does not
authorize Phase 1 test changes or Phase 2 guard-support changes. No test or
guard file was changed as part of the Phase 0 acceptance record. Separate
supplementary Phase 1 Red execution approval was received on 2026-10-26; no
guard-support implementation approval has been granted.
