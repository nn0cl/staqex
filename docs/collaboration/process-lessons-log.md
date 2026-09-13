# Process Lessons Log

Target-owned. Created from `docs/templates/process-lesson.md`. Do not store
secrets. Policy: `docs/collaboration/process-lessons.md`.

Record meta-level patterns only. No session transcripts.

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
