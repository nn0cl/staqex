# LISS-0510: Lexical scope and State shadowing implementation

| Field | Value |
|---|---|
| Status | **done — Phase 3 complete** |
| Phase | phase-3-refactor |
| Parent | WP-0092 |
| Design authority | [ADR 0216](../architecture/adr/0216-lexical-block-scope-and-state-shadowing.md) |
| Depends on | LISS-0480, LISS-0483 |
| Implementation permission | Phase 3 approved by Adjudicator |
| Next approval | None for this Issue |

## Scope

Implement lexical binding support for braced nested blocks while preserving
blackboard shaped source. Scientific display metadata must resolve through the
same binding environment as type checking.

## Acceptance scenarios

- An inner `State psi` shadows an outer `State psi` and is independently
  consumed.
- An inner `Float psi` shadows an outer `State psi` without changing the outer
  State binding.
- Two declarations named `psi` in one scope fail with a duplicate-declaration
  diagnostic.
- After an inner block ends, the outer `psi` resolves again.
- Consuming the inner State does not consume the outer State, and using the
  outer State twice still fails the ordinary linearity rule.
- Lexicon metadata reports the resolved binding identity and declaration span.

## Phase 1 candidate files

Tests and fixtures under `tests/`, plus this Issue and a trace. Production
parser/type-checker changes are Phase 2 only.

Phase 1 evidence: `tests/test_liss_0510_lexical_scope_red.py` contains four
acceptance tests.

## Phase 2 implementation

- `TypeChecker` now tracks declarations per main/block lexical scope and emits
  `DUPLICATE_DECLARATION` for ordinary same-scope duplicates while retaining
  the existing state-transform rebinding surface.
- `LexiconInspection.scoped_bindings` exposes scientific alias name, context,
  scope depth, deterministic binding identity, and declaration span.
- Metadata walks the existing `BlockExpr` surface; it does not introduce a
  second alias table or force extraction into functions/files.
- Lexicon inspection rejects syntax/basic type failures but does not confuse
  linearity or QSEM readiness diagnostics with source spelling invalidity.

Green evidence:

```text
PYTHONPATH=. .venv/bin/python -m pytest \
  tests/test_liss_0510_lexical_scope_red.py \
  tests/test_liss_0480_scientific_lexicon_contract_red.py \
  tests/test_liss_0483_observation_lexicon_conformance_red.py -q
17 passed
```

## Phase 3 refactor and verification

- Extracted duplicate-policy decisions into a named typechecker predicate.
- Replaced AST class-name string checks in lexicon context resolution with
  explicit AST type checks.
- Preserved the compatibility boundaries documented in Phase 2.

Verification:

```text
git diff --check
PYTHONPATH=. .venv/bin/python -m py_compile \
  compiler/staqex/typecheck.py compiler/staqex/scientific_lexicon_contract.py
PYTHONPATH=. .venv/bin/python -m pytest \
  tests/test_liss_0510_lexical_scope_red.py \
  tests/test_liss_0480_scientific_lexicon_contract_red.py \
  tests/test_liss_0483_observation_lexicon_conformance_red.py \
  tests/test_liss_0221_state_transforming_calls_move_red.py \
  tests/test_dirac_slice_a_red.py tests/test_dirac_slice_d_red.py -q
31 passed
```

Process review: no operating-contract deviation or operational problem found.

## Exclusions

No new alias inventory, Unicode source policy, public observation type,
provider/QPU integration, Rust implementation, or forced extraction into
functions/files.

## Design notes

Use the existing typed scope model where possible. Do not add a second symbol
table solely for scientific aliases. The same lexical environment must drive
type resolution, linearity diagnostics, and lexicon metadata.
