# Process Lessons Log

Target-owned. Created from `docs/templates/process-lesson.md`. Do not store
secrets. Policy: `docs/collaboration/process-lessons.md`.

Record meta-level patterns only. No session transcripts.

## Lesson

- Date: 2026-09-27
- Class: acceptance-inventory-reconciliation
- Pattern: a passing reviewed suite can still omit cases explicitly listed as
  minimum evidence in its accepted specification when the review does not map
  each listed clause to a named test.
- What later design or implementation must do: maintain a clause-to-test
  matrix for every explicit minimum test inventory; before accepting Red,
  identify the exact test for each item or record the approved reason it is
  unreachable/out of scope. Reconcile again before declaring Green.
- Source issue or work plan: LISS-0579 / WP-0172
- Status: applied in the bounded Phase 1 contract correction and accepted test
  review; carry forward to later acceptance inventories

## Lesson

- Date: 2026-09-24
- Class: compatibility-hook-identity-contract
- Pattern: a structural compatibility test can assert that import names and
  evaluator attribute strings occur in a file while never proving that the
  installer maps the intended successor function to the hook or that runtime
  class attributes have successor identity.
- What later design or implementation must do: inspect the actual installer
  mapping (AST or equivalent), verify the installer is used by evaluator
  setup, and assert runtime hook identity against the successor function once
  the successor module exists. A raw substring check is insufficient.
- Source issue or work plan: LISS-0578 / WP-0171
- Status: applied in the Phase 1 Red correction and Phase 2 compatibility
  identity checks.

## Lesson

- Date: 2026-09-24
- Class: status-drift
- Pattern: a canonical architecture specification can retain an obsolete
  phase-approval statement after an Issue records that implementation has
  completed, leaving the architecture entry point inconsistent with the live
  work state.
- What later design or implementation must do: when recording a phase
  transition, search and update every canonical specification that states the
  approval or implementation status in the same reviewable unit; do not limit
  synchronization to the Issue, work plan, and trace.
- Source issue or work plan: LISS-0576 / WP-0169
- Status: applied in LISS-0577 Phase 0 and Phase 3, and reapplied in LISS-0579
  Phase 3 final review (canonical spec, Issue, WP, test lifecycle wording, and
  trace synchronized at approval and review transitions)

## Lesson

- Date: 2026-09-23
- Class: refactor-branch-preservation
- Pattern: a broad formatting patch can move a branch-local return while
  leaving common focused characterization tests green; downstream
  specification nodes then expose the regression.
- What later design or implementation must do: keep behavior-sensitive edits
  scoped to a whole function or helper, inspect the exact resulting branch
  structure immediately, and run the declared specification suite before
  accepting the refactor.
- Source issue or work plan: LISS-0575 / WP-0168
- Status: applied in LISS-0575 and LISS-0577 Phase 3

## Lesson

- Date: 2026-09-22
- Class: red-fixture-interface
- Pattern: a Red characterization can initially fail because its fixture uses
  a neighboring execution API's result shape rather than the target suite's
  established contract, obscuring the intended product gap.
- What later design or implementation must do: reuse the nearest authoritative
  test API, distinguish fixture failures from product failures, and rerun the
  exact bounded suite before review.
- Source issue or work plan: LISS-0573 / WP-0167
- Status: applied

## Lesson

- Date: 2026-09-22
- Class: decomposition-callback-boundary
- Pattern: a body migration can pass the main consumer suite while a private
  consumer still depends on an entrypoint implicit in the original facade,
  such as frame restoration or operator resolution.
- What later design or implementation must do: inventory private consumers
  before body removal and promote each required behavior to an explicit
  successor entrypoint or narrow context callback; verify structural ownership
  and consumer smoke after the move.
- Source issue or work plan: LISS-0572 / WP-0167
- Status: applied

## Lesson

- Date: 2026-09-19
- Class: red-contract-scope
- Pattern: a decomposition Red suite can legitimately combine expected
  structural failures with passing characterization cases, but a malformed
  fixture can be mistaken for a product gap if it is not corrected and rerun
  before review.
- What later design or implementation must do: label structural and
  characterization nodes separately, repair only demonstrably invalid setup,
  rerun the exact bounded suite, and preserve the intended failure count as
  evidence for the next implementation gate.
- Source issue or work plan (adopter's own ID, if any): LISS-0567 / WP-0164
- Status: applied

## Lesson

- Date: 2026-09-18
- Class: private-consumer-inventory
- Pattern: extracting private evaluator methods can make focused structural
  tests pass while silently breaking existing characterization consumers that
  still discover underscore-prefixed attributes.
- What later design or implementation must do: inventory private imports and
  test hooks before extraction; if the private surface is retained temporarily,
  make the compatibility role explicit and keep it out of the new dispatch
  ownership.
- Source issue or work plan (adopter's own ID, if any): LISS-0560 / WP-0162
- Status: applied in Phase 2 and Phase 3

## Lesson

- Date: 2026-09-16
- Class: boundary-completeness
- Pattern: external geospatial and sensor standards can carry enough familiar
  vocabulary to tempt an adapter into inferring domain decisions such as road
  passability or execution readiness.
- What later design or implementation must do: freeze one versioned mapping
  profile with source identity, unknown/invalid handling, and explicit negative
  non-inference tests; keep external vocabulary in Metadata Graph evidence and
  route execution meaning through the accepted Semantic IR/use-case boundary.
- Source issue or work plan (adopter's own ID, if any): LISS-0523 / WP-0140
- Status: applied

## Lesson

- Date: 2026-09-16
- Class: contract-trace
- Pattern: numerical optimizer behavior can appear equivalent while silently
  deleting small but nonzero coefficients or admitting non-finite values into
  an executable projection.
- What later design or implementation must do: express coefficient-preservation
  and fail-closed non-finite handling as focused executable Red contracts, then
  verify the exact nodes before implementation; do not rely on diagnostic
  degree classification as semantic evidence.
- Source issue or work plan (adopter's own ID, if any): LISS-0454 / WP-0117
- Status: applied

## Lesson

- Date: 2026-09-14
- Class: evaluator-state-ownership
- Pattern: extracting runtime behavior from a large evaluator can create a
  second mutable state owner even when public behavior initially passes.
- What later design or implementation must do: keep all mutable runtime maps
  in `Evaluator`, pass a narrow explicit context to extracted services, and
  verify that extracted modules do not reconstruct or retain unsynchronized
  copies.
- Source issue or work plan (adopter's own ID, if any): LISS-0544 / WP-0160
- Status: applied in Phase 0 design

## Lesson

- Date: 2026-09-14
- Class: compatibility-authority-boundary
- Pattern: an old absence assertion can mistake a derived compatibility payload
  for a second semantic authority after a canonical IR migration.
- What later design or implementation must do: supersede such assertions only
  with explicit authority/provenance and negative-artifact checks; retain the
  compatibility surface only while its diagnostic-only role is machine-
  checkable and its removal has a separate consumer decision.
- Source issue or work plan (adopter's own ID, if any): LISS-0553 / WP-0161
- Status: applied

## Lesson

- Date: 2026-09-13
- Class: diagnostic-scope-versus-readiness
- Pattern: non-hard target-evidence diagnostics may coexist with local compile
  success, but local success is not proof that a downstream artifact producer
  conservatively projected every semantic operation.
- What later design or implementation must do: classify diagnostic blocking
  scope explicitly and verify downstream operation conservation plus an empty
  rejection envelope; never use a local compile boolean as target
  authorization.
- Source issue or work plan (adopter's own ID, if any): LISS-0552 / WP-0161
- Status: applied in Phase 0 design, Phase 1 Red, Phase 2 Green, and Phase 3
  Refactor; the tests and full blocking suite separately prove local
  acceptance, diagnostic scope, semantic-operation conservation, and target
  artifact rejection.

## Lesson

- Date: 2026-09-13
- Class: quantitative-traceability
- Pattern: a review record can conflate the number of acceptance nodes with
  the number of changed source declarations even when the underlying diff is
  correct.
- What later design or implementation must do: label the unit of every count
  in phase evidence and derive changed-line or artifact counts from the
  committed diff before final review.
- Source issue or work plan (adopter's own ID, if any): LISS-0551 / WP-0161
- Status: applied

## Lesson

- Date: 2026-09-12
- Class: residual-diagnostic-ownership
- Pattern: repairing invalid test setup can expose a second, independent
  semantic failure; forcing the original fixture issue to make every adopted
  node Green would weaken assertions or expand implementation scope silently.
- What later design or implementation must do: rerun the exact nodes after a
  fixture migration, remove passing nodes from lifecycle exclusion, and move
  each residual failure with its complete diagnostic inventory to the smallest
  accepted successor issue.
- Source issue or work plan (adopter's own ID, if any): LISS-0551 / WP-0161
- Status: applied

## Lesson

- Date: 2026-09-12
- Class: red-contract-reuse
- Pattern: a lifecycle-managed failing node may already provide the complete
  Phase 1 acceptance contract; adding a second test creates competing authority
  without improving evidence.
- What later design or implementation must do: adopt and review the existing
  exact node when its assertion is still authoritative, then limit Green to the
  setup or implementation gap identified by that node.
- Source issue or work plan (adopter's own ID, if any): LISS-0551 / WP-0161
- Status: applied

## Lesson

- Date: 2026-09-12
- Class: test-lifecycle-ownership
- Pattern: a test-infrastructure issue cannot both finish and remain the open
  owner of unrelated feature-level active-Red exclusions.
- What later design or implementation must do: assign every active Red to the
  smallest feature-remediation issue before final infrastructure review; the
  lifecycle mechanism validates ownership but does not become a permanent
  umbrella owner.
- Source issue or work plan (adopter's own ID, if any): LISS-0543 / WP-0161
- Status: applied

## Lesson

- Date: 2026-09-11
- Class: compatibility-baseline
- Pattern: a structural-refactor baseline can miss reachable imports when it
  substitutes a hand-selected notion of public symbols for the language's
  actual export rules.
- What later design or implementation must do: derive compatibility manifests
  from the runtime's real export behavior (`__all__` when present, otherwise
  every non-underscore module name in Python), then preserve intentional
  retirement as a separately approved migration.
- Source issue or work plan (adopter's own ID, if any): LISS-0543 / WP-0160
- Status: applied

## Lesson

- Date: 2026-09-11
- Class: regression-authority-lifecycle
- Pattern: Phase 1 test filenames retained a `_red.py` suffix after Green and
  completion, while CI excluded that suffix globally. Completed acceptance
  contracts could regress without failing the merge gate.
- What later design or implementation must do: represent active Red state with
  explicit issue-linked lifecycle metadata, make completed contract tests
  blocking, and reject stale exclusions automatically. A filename is not an
  authoritative phase ledger.
- Source issue or work plan: repository-wide source-code review; follow-up WP-A
- Status: applied

## Lesson

- Date: 2026-09-10
- Class: boundary-completeness
- Pattern: fake-port tests can pass after a port extension while a concrete
  adapter implementation still lacks the new method.
- What later design or implementation must do: every port extension must be
  checked against all concrete implementations and include a deterministic
  concrete-surface regression assertion without requiring live credentials.
- Source issue or work plan (adopter's own ID, if any): LISS-0516 / WP-0133
- Status: applied

## Lesson

- Date: 2026-09-10
- Class: authority-boundary
- Pattern: adding a new safe observation API does not close an unsafe legacy
  projection that remains reachable through an existing port method.
- What later design or implementation must do: when a contract tightens,
  audit every legacy entry point and its delegated callers; test unknown and
  failure states through each externally reachable projection.
- Source issue or work plan (adopter's own ID, if any): LISS-0516 / WP-0133
- Status: applied

## Lesson

- Date: 2026-09-10
- Class: phase-acceptance-boundary
- Pattern: a provider adapter Phase 2 change can satisfy new contract tests
  while accidentally regressing the existing adapter surface.
- What later design or implementation must do: Phase 2 Green evidence must
  include the new approved gap suite plus the nearest existing adapter
  regression suite and the provider-neutral contract suite.
- Source issue or work plan (adopter's own ID, if any): LISS-0516 / WP-0133
- Status: applied

## Lesson

- Date: 2026-09-10
- Class: phase-acceptance-boundary
- Pattern: a Red suite can contain multiple valid gap tests while its direct
  runner reports only the first failure, weakening phase acceptance evidence.
- What later design or implementation must do: bounded direct runners must
  execute every named test, report each failure, and exit non-zero only after
  complete failure collection.
- Source issue or work plan (adopter's own ID, if any): LISS-0516 / WP-0133
- Status: applied

## Lesson

- Date: 2026-08-31
- Class: authority-boundary
- Pattern: a compatibility projection can retain legacy DTO nodes while still
  making the canonical semantic authority explicit and machine-checkable.
- What later design or implementation must do: preserve compatibility only
  with an explicit diagnostic-only role and negative authorization metadata;
  never let retained DTOs silently become execution or finiteization authority.
- Source issue or work plan (adopter's own ID, if any): LISS-0487 / WP-0107
- Status: applied

## Lesson

- Date: 2026-09-07
- Class: migration-boundary
- Pattern: moving a representative example can make current paths correct
  while historical specifications and ADRs intentionally retain the former
  identity.
- What later design or implementation must do: classify references as current
  or historical before editing; update executable/current navigation references
  and preserve historical evidence unless the accepted scope explicitly
  requires a historical rewrite.
- Source issue or work plan (adopter's own ID, if any): LISS-0513 / WP-0130
- Status: applied

## Lesson

- Date: 2026-08-26
- Class: status-drift
- Pattern: ISSUE and work-plan status stayed `review` or `in_progress` after
  the work had already merged to `main`. Later agents treating the ledger as
  current work would resume closed process changes.
- What later design or implementation must do: when a process PR merges,
  update the issue and work-plan status in the same context or immediately
  after. Leftover `review` / `in_progress` after merge is ledger drift, not
  open work.
- Source issue or work plan (adopter's own ID, if any): LISS-0024
- Status: applied

## Lesson

- Date: 2026-09-21
- Class: red-contract-scope
- Pattern: a decomposition Red suite can mix structural migration gaps with
  passing runtime characterizations; without naming both sets, a reviewer
  cannot distinguish an intentionally failing contract from a behavior
  regression.
- What later design or implementation must do: enumerate every intended
  structural failure, preserve at least one positive characterization for
  each retained behavior family, and report the two result sets separately
  before Green authorization.
- Source issue or work plan: LISS-0571 / WP-0167
- Status: applied

## Lesson

- Date: 2026-09-22
- Class: decomposition-boundary
- Pattern: installing a successor through a compatibility facade can leave a
  dead duplicate implementation in the original class, making the measured
  split look complete while preserving two possible authorities.
- What later design or implementation must do: after successor installation,
  remove the old body in the refactor phase, assert the facade has no duplicate
  dispatcher definition, and re-run actual private consumers plus the full
  blocking suite.
- Source issue or work plan: LISS-0571 / WP-0167
- Status: applied

## Lesson

- Date: 2026-09-22
- Class: red-contract-scope
- Pattern: a multi-family structural extraction needs separate positive
  characterizations for invocation frames, constructors, and assignments;
  otherwise one passing class/function example can conceal a broken mutation
  or receiver-restoration boundary.
- What later design or implementation must do: name each structural gap,
  inventory its private consumers, and retain at least one passing
  characterization for every family before Green authorization.
- Source issue or work plan: LISS-0572 / WP-0167
- Status: applied

## Lesson

- Date: 2026-09-08
- Class: coverage-authority-boundary
- Pattern: a completed representation or small demonstration can be mistaken
  for complete scientific workflow coverage; importing richer metadata can
  also accidentally create a second executable semantic authority.
- What later design or implementation must do: separate metadata authority,
  source-derived execution meaning, profile-specific capability, and scientific
  validation. Track each domain's positive execution and neighboring rejection
  evidence; keep successor scope distinct from completed example migrations.
- Source issue or work plan: LISS-0514 / WP-0131
- Status: applied in design; implementation application remains per phase gate

## Lesson

- Date: 2026-09-23
- Class: decomposition-source-ownership
- Pattern: a facade test can pass before extraction when it inspects only the
  facade class, while the original implementation remains in its source module
  and compatibility wiring still imports that module.
- What later design or implementation must do: assert symbol ownership in the
  designated successor and absence from the original module; check compatibility
  imports structurally, and count independent gaps rather than derivative
  missing-file assertions.
- Source issue or work plan: LISS-0575 / WP-0168
- Status: applied in the corrected Phase 1 Red contract

## Lesson

- Date: 2026-09-15
- Class: decomposition-boundary
- Pattern: a public-facade decomposition can satisfy ownership and dependency
  contracts while retaining a large legacy implementation bridge; describing
  that bridge as a complete migration would create false completion evidence.
- What later design or implementation must do: name every retained bridge
  explicitly, verify its public compatibility and authority direction, and
  record body-by-body migration as successor scope with its own snapshots.
- Source issue or work plan (adopter's own ID, if any): LISS-0549 / WP-0160
- Status: applied

## Lesson

- Date: 2026-09-07
- Class: acceptance-boundary
- Pattern: a fail-closed semantic-family check can overmatch a valid neighboring
  representation, such as treating Hamiltonian coefficient terms as a direct
  non-unitary transform.
- What later design or implementation must do: pair every negative projection
  assertion with positive neighboring forms and scope rejection to the exact
  source ownership/context that is unsupported.
- Source issue or work plan (adopter's own ID, if any): LISS-0511 / WP-0128
- Status: applied

## Lesson

- Date: 2026-09-03
- Class: phase-acceptance-boundary
- Pattern: a canonical consumer migration can appear successful for supported
  projections while an unsupported semantic family still produces a partial
  artifact through a compatibility path.
- What later design or implementation must do: include an explicit unsupported
  acceptance scenario for each consumer migration and verify atomic,
  provider-neutral rejection before declaring the boundary complete.
- Source issue or work plan (adopter's own ID, if any): LISS-0503 / WP-0107
- Status: applied

## Lesson

- Date: 2026-08-28
- Class: review-boundary-observability
- Pattern: a safe internal classification API was integrated into a command,
  but the command discarded the disposition metadata needed for human review.
  Unit tests therefore passed while the operational review boundary remained
  opaque.
- What later design or implementation must do: define and test the observable
  command/report contract separately from the pure classifier, preserving
  classification, reason, and source path for every reviewed record.
- Source issue or work plan (adopter's own ID, if any): LISS-0473 / WP-0090
- Status: applied

## Lesson

- Date: 2026-08-26
- Class: other
- Pattern: two local issues shared one LISS ID. Filename uniqueness is not
  the same as ID uniqueness; skipped numbers must stay unused.
- What later design or implementation must do: assign the next free ID only
  after listing existing `docs/issues/LISS-*` files and their metadata IDs.
  Do not reuse a skipped or colliding number. If a collision is found, keep
  the earlier claim on the ID and renumber the later file.
- Source issue or work plan (adopter's own ID, if any): LISS-0024
- Status: applied

## Lesson

- Date: 2026-09-08
- Class: coverage-authority-boundary
- Pattern: a completed representation or small demonstration can be mistaken
  for complete scientific workflow coverage; importing richer metadata can
  also accidentally create a second executable semantic authority.
- What later design or implementation must do: separate metadata authority,
  source-derived execution meaning, profile-specific capability, and scientific
  validation. Track each domain's positive execution and neighboring rejection
  evidence; keep successor scope distinct from completed example migrations.
- Source issue or work plan: LISS-0514 / WP-0131
- Status: applied in design; implementation application remains per phase gate
