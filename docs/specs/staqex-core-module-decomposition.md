# Staqex core module decomposition

| Field | Value |
|---|---|
| Status | accepted — Architecture approved 2026-09-11 |
| Owner | WP-0160 / LISS-0543–0550 |
| Path | Architecture Path followed by bounded Phase 3 refactor units |
| Implementation permission | not granted; each issue/phase requires separate approval |

## Goal

Reduce the cognitive and regression risk of the largest Python modules without
changing Staqex source meaning, public Python imports, diagnostics, deterministic
local execution, generated QASM, artifact identity, or provider boundaries.

This work is structural. It does not use module splitting as permission to fix,
extend, or reinterpret behavior.

## Current evidence

| Module | Lines | Main concentration |
|---|---:|---|
| `runtime/evaluator.py` | 6,926 | orchestration, execution plans, evolution, operators, calls, values, observation |
| `typecheck.py` | 4,668 | declaration checks, operator algebra, dimensions, inference, effects, evolution |
| `parser.py` | 3,669 | top-level/scientific declarations, statements, values, operators, recovery |
| `scientific_semantic_ir.py` | 2,008 | semantic model, runtime plan, QPU projection, realization, fingerprints |
| `backend/qasm/lower.py` | 1,520 | capability preflight, AST fallback, semantic lowering, resource rejection |
| `quantum_semantic_ir.py` | 1,372 | DTOs and verifier families |
| `hir.py` | 1,135 | HIR construction and linear verification |
| `ast_nodes.py` | 1,064 | all source AST DTO families |
| `finite_binder.py` | 1,027 | finite-domain normalization and verification |
| `pipeline.py` | 1,022 | compile orchestration and compatibility result surface |

The public import blast radius is material: `runtime.evaluator` is referenced
from 93 repository files and `pipeline` from 312. Compatibility facades are
therefore required.

## Architectural target

```text
public compatibility modules
  evaluator.py  typecheck.py  parser.py  scientific_semantic_ir.py
  pipeline.py   backend/qasm/lower.py
          |
          v
internal cohesive packages
  runtime/evaluation/
  typechecking/
  parsing/
  scientific_semantic/
  backend/qasm/lowering/
  syntax/
```

Public modules continue to own documented imports and re-export stable DTOs.
Internal packages own implementation families. Dependency direction is from
public orchestration/facade to internal services and shared pure DTOs; internal
modules must not import a public facade that imports them.

## Required invariants

1. Existing public symbols and import paths remain available unless a separate
   accepted migration explicitly removes them.
2. A fixed source and seed produce the same observable local result before and
   after each extraction.
3. Accepted QASM output is byte-identical; rejected input retains diagnostic
   code, source span, ordering, and atomic no-artifact behavior.
4. Scientific Semantic IR remains the compile-owned semantic authority.
   Extracted AST/DTO helpers cannot become an execution authority.
5. Kernel modules gain no provider SDK, network, filesystem, credential, or UI
   dependency.
6. Evaluation state has one owner. Extracted services receive explicit context
   or narrow callbacks; they do not duplicate mutable evaluator/typechecker/
   parser state.
7. No new import cycle is accepted. Import-cycle checks include lazy imports,
   not only top-level imports.
8. Each extraction is independently reviewable and preserves assertions.
9. Active Red status is explicit and issue-linked. A `_red.py` suffix alone is
   not test lifecycle authority.
10. The full blocking baseline must be green before a Phase 3 extraction is
    declared complete.

## Size guardrails

These are reviewability guardrails, not semantic requirements:

- New implementation modules should normally stay below 1,200 physical lines.
- A function above 150 lines or class above 1,200 lines requires a documented
  cohesion reason in its issue review.
- Compatibility facades contain public exports and thin orchestration, not a
  second copy of implementation logic.
- Line-count reduction alone is not acceptance evidence.

An exception requires Architecture approval; agents must not create vague
`utils.py`, `common.py`, or speculative provider abstractions to meet a number.

## Acceptance scenarios

### Scenario A — public imports survive extraction

Given the public-symbol manifest captured before an extraction, when the same
imports are executed afterwards, then each symbol resolves at its previous
path and has the documented callable or DTO contract.

### Scenario B — local execution meaning is preserved

Given the approved representative corpus and fixed seeds, when the old baseline
and extracted implementation execute it, then result status, probability/
amplitude evidence, measurement, diagnostics, and emitted text are equal under
their existing exactness policy.

### Scenario C — QPU projection remains atomic and identical

Given accepted and neighboring unsupported programs, when QASM lowering runs,
then accepted QASM and metadata are byte-identical and unsupported programs
retain the same ordered diagnostics with no partial artifact.

### Scenario D — state ownership stays explicit

Given an extracted evaluator, parser, or typechecker service, when static
dependency and mutation audits run, then it has one declared context owner and
does not retain an unsynchronized copy of mutable compilation/runtime state.

### Scenario E — regression authority is real

Given an issue recorded as done, when CI selects tests, then its acceptance
tests are blocking regardless of filename. A genuinely active Red exclusion
must name its open issue and current phase.

## Verification profile

Every implementation unit must run:

- public-symbol/import manifest comparison;
- focused characterization and nearest semantic-family tests;
- fixed-seed local execution snapshots where runtime code moves;
- accepted/rejected QASM golden comparison where lowering code moves;
- `tests/spec_verification/run_all.py` (currently 161/161);
- complete blocking pytest baseline established by LISS-0543;
- `compileall`, import-cycle audit, document lifecycle, coverage-ledger, and
  `git diff --check`.

## Explicit exclusions

- New language syntax or semantics.
- Fixing the currently observed 19 failures inside a structural extraction.
- Provider SDK changes, network calls, credentials, live QPU, or deployment.
- Rust migration or an intermediate rewrite.
- Public API removal, diagnostic renaming, QASM formatting changes, or broad
  performance optimization.

## Stop conditions

Return to Architecture review if an extraction requires changing public DTOs,
moving semantic authority, adding a dependency, changing diagnostic precedence,
or sharing mutable state across services. Return to Feature Path if a
characterization exposes a behavior defect that needs a new Red/Green fix.
