# LISS-0503 Phase 2 Green Review

## Scope and gate

Review the minimum implementation for unsupported explicit-evolution rejection
at the canonical QASM boundary. Phase 3 refactoring and completion approval
remain pending.

## Findings

### F1 — Canonical provenance guard

`QASM3Emitter.emit_unit()` checks the existing canonical semantic IR and QPU
program before realization. An explicit evolution without executable canonical
instructions is rejected with the stable `E_QPU_CANONICAL_PROVENANCE` code.

### F2 — Atomic rejection

The rejection returns empty QASM and an empty rejection circuit, so no gate
emission or allocation can occur on the unsupported path.

### F3 — Supported projection compatibility

Finite canonical projections retain executable instructions and continue to the
existing QPU realization route. The regression slices for LISS-0444, LISS-0445,
and LISS-0456 pass.

### F4 — Boundary remains narrow

The implementation does not infer evolution semantics, select a provider, or
restore the retired direct lowerer path. Target-specific evolution remains a
separate work item.

## Verification

The dedicated acceptance and regression command completed with **35 passed**.
`py_compile` and `git diff --check` are required before Phase 3.

## Phase 3 same-context review

The implementation was re-read independently of the authoring notes. The
guard is the smallest readable change, assertions and behavior remain
unchanged, and no additional refactor is warranted.

Reviewer empathy summary: unsupported explicit evolution has one clear
provider-neutral failure path; supported finite projections retain one clear
QPU realization path.

- F1: already closed with evidence — canonical guard is present and tested.
- F2: already closed with evidence — atomic rejection assertions pass.
- F3: already closed with evidence — finite and consumer regressions pass.
- F4: already closed with evidence — no provider or legacy-lowerer bypass.

## Decision

Phase 3 review is complete with no blocker. Isolation was `same_context`,
which is weaker than `separate_context`. The issue may be marked complete after
status synchronization and process review.
