# Staqex active-Red remediation specification

| Field | Value |
|---|---|
| Status | Proposed |
| Owner | WP-0161 / LISS-0551–0559 |
| Trigger | LISS-0543 final-review completion blocker |
| Scope | 19 exact pytest nodes captured 2026-09-11 |

## Purpose

Move each active-Red node from the test-infrastructure issue to the smallest
meaningful open owner, then reconcile it against the newest accepted language,
semantic-authority, and scientific-data contracts. Completed historical issues
remain closed. No test is deleted, broadly ignored, or made weaker merely to
obtain a green suite.

## Classification authority

Each node receives exactly one of these dispositions:

- **fixture migration**: preserve the assertion while updating invalid source
  setup to the current lexical/scope contract;
- **superseded expectation**: replace an older assertion only when a later
  accepted specification provides direct contrary authority and equivalent
  positive/negative coverage remains;
- **product regression**: preserve the accepted assertion and repair the
  implementation through Red/Green/Refactor;
- **architecture conflict**: stop at Phase 0 until the Adjudicator chooses the
  authoritative contract.

The `_red.py` filename is not evidence for any disposition. The observed
exception or diagnostic alone is also insufficient; the accepted specification
and later decisions determine the result.

## Node ownership matrix

| Nodes | Count | Initial classification | Successor |
|---|---:|---|---|
| bounded evolve-until, empty Sigma/Pi identity, paper inner/outer, operator inner/outer, pipeline associativity | 8 | fixture migration first; residual finite-projection diagnostics separated | LISS-0551, then LISS-0552 if still failing |
| non-explicit `symbolic_ir` absence | 1 | superseded expectation candidate after LISS-0489 compatibility view | LISS-0553 |
| raw QASM unit without canonical projection | 1 | product regression candidate | LISS-0554 |
| interfer nodes selected by `kind == "Call"` | 2 | superseded AST-shape expectation candidate; meaning evidence still required | LISS-0555 |
| missing POVM rejection collection | 1 | product regression candidate | LISS-0556 |
| evaluator stores `semantic_ir` and raises `ValueError` | 2 | runtime-plan ownership/API compatibility conflict | LISS-0557 |
| tomography diagnostic `OBSERVATION_UNSUPPORTED` | 1 | superseded diagnostic-name candidate | LISS-0558 |
| S02 assay records expose immutable typed fields | 3 | product regression candidate | LISS-0559 |

## Cross-cutting acceptance scenarios

### R1 — ownership can outlive infrastructure completion

Given the 19 exact nodes, when LISS-0543 is marked done, then every exclusion
names a distinct open successor issue whose phase matches the manifest. The
lifecycle checker remains green and no completed issue is reopened.

### R2 — fixture repair does not hide a product failure

Given a source fixture invalidated by the accepted lexical shadowing rules,
when only its setup is migrated, then its original semantic assertion remains.
Any residual diagnostic becomes explicit evidence for LISS-0552 rather than an
additional fixture edit.

### R3 — later accepted contracts supersede narrowly

Given an old assertion and a later accepted contract, when the assertion is
updated, then the test cites the newer authority and still proves canonical
identity, provenance, fail-closed behavior, or diagnostic stability. Output
equality alone is not replacement evidence.

### R4 — regressions restore the boundary, not a compatibility shortcut

Given QASM, POVM, evaluator, or assay regression evidence, when Green is
implemented, then semantic authority remains compile-owned, no artifact or
scientific record is fabricated, and no adapter or provider gains business
logic.

## Execution order

1. Approve this architecture and hand off manifest ownership; close LISS-0543.
2. Run LISS-0551 before LISS-0552 so invalid fixtures cannot distort the
   finite-projection diagnosis.
3. LISS-0553, 0554, 0555, 0556, 0557, 0558, and 0559 may proceed independently,
   each on its own branch and phase approvals.
4. Remove a manifest node immediately after its accepted contract passes; an
   issue is done only when none of its nodes remain excluded.

## Explicit exclusions

- Live QPU, provider SDK, AWS credentials, network, deployment, and Rust work.
- New language syntax or broad semantic redesign.
- Reopening LISS-0012, 0013, 0031, 0056, 0234, 0476–0478, 0485, 0486, or 0517.
- Editing historical evidence to make current implementation appear correct.
- Combining these fixes with LISS-0544–0550 source decomposition.

## Verification profile

- direct execution of every owned active-Red node;
- nearest accepted successor-contract suites for each Issue;
- complete blocking pytest with only validated exact-node deselections;
- Spec Verification 161/161;
- lifecycle, document-lifecycle, coverage-ledger, compile, and diff checks;
- no manifest owner with terminal status and no expired review date.

