# LISS-0551 Phase 1 Red review packet

## Review Target

- Artifact: eight existing source-fixture conformance nodes
- Current phase: Phase 1 Red
- Requested approval: accept the existing eight failures as the fixed Red batch
- Approval type: phase
- Approved scope: source setup migration only; assertions and production code
  remain unchanged
- Implementation allowed: no
- Post-review required: yes; separate Phase 2 Green / Implementation approval
- Execution batch ID: not applicable

## Canonical Evidence Re-read

- `docs/specs/staqex-active-red-remediation.md`
- `docs/issues/LISS-0551-current-source-fixture-conformance.md`
- lexical `State` migration and nested-scope decisions cited by the Issue
- the five test files containing the eight exact manifest nodes
- git attribution for the lowercase-`state` to Type-First corpus migration

## Red Contract

The existing nodes already express the required semantic assertions, so Phase
1 adds no duplicate test. The fixed batch is:

- one bounded evolve-until expression node;
- three empty Sigma/Pi identity nodes;
- two paper inner/outer notation nodes;
- one operator inner/outer boundary node;
- one pipeline associativity/state-preservation node.

All eight currently contain setup that redeclares one or more `State` names in
the same lexical scope. The current language contract rejects that setup with
`DUPLICATE_DECLARATION`; the semantic assertion cannot be evaluated as a clean
acceptance result.

## Findings and Dispositions

- Apply: adopt the eight existing failures instead of creating look-alike Red
  tests. Their exact node IDs are already machine-managed.
- Apply: Phase 2 may alter only source setup required to express legal nested
  shadowing or remove a helper-only duplicate. Assertion bodies stay unchanged.
- Apply: after setup repair, record every remaining diagnostic. QSEM or static
  QPU diagnostics are transferred to LISS-0552 rather than hidden by more test
  edits.
- Already closed with evidence: no missing test, duplicate manifest entry, or
  completed owner exists; lifecycle validation recognizes all eight.
- Out of scope: compiler/typechecker/QASM/runtime behavior changes and any
  weakening of expected semantic results.

## Failure Scenarios Reviewed

- A fixture is made green by permitting illegal same-scope redeclaration.
- An assertion is deleted or relaxed along with its setup migration.
- A residual projection diagnostic is misclassified as fixture drift.
- A new duplicate Red test obscures which node is lifecycle authority.

## Verification Result

- Direct exact-node run: 8 failed, 0 collection errors.
- All failures reach their unchanged final assertion after current compile
  diagnostics; duplicate declaration is present in the affected setup.
- No test, fixture, or production file changed in Phase 1.
- Lifecycle, document, coverage, and diff checks are run after phase metadata
  synchronization.

## Isolation

- Review isolation: `same_context`, weaker than `separate_context`.
- Planning size is M, so same-context review is permitted but does not replace
  human Adjudicator approval.

## Next Approval Required

`LISS-0551 Phase 2 Green / Implementation 承認`

