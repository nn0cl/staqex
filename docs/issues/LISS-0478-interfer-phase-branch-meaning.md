# LISS-0478: Interfer/phase/branch meaning preservation

| Field | Value |
|---|---|
| Status | **Phase 1 Red complete; Phase 2 Green approval required** |
| Phase | phase-1-red |
| Parent | WP-0113 |
| Design authority | [Meaning Preservation Specification](../specs/staqex-semantic-ir-meaning-preservation.md#residual-follow-up-design-liss-0478) |
| Depends on | LISS-0450 bounded Coin/when slice |
| Implementation permission | None |
| Next approval | Typed Phase 2 Green approval |

## Scope

Define canonical semantic roles for interference, phase, branch/control
relationships, operand identity, exactness, and provenance. Define explicit
unsupported finite projection behavior.

## Acceptance scenarios

- Branch/control identity survives semantic projection.
- Phase is not discarded or reinterpreted as classical probability.
- Unsupported finite projection retains source meaning and emits no artifact.
- Source-derived nodes remain inspectable without QPU support.

## Exclusions and stop conditions

No gate synthesis, numerical approximation, provider, QPU, or Hilbert-space
storage choice. Stop for ADR review if approximation or new representation is
required.

## Phase 1 candidate files

Representative `.sqx` fixtures, meaning-role assertions, negative projection
tests, and this Issue/spec/review record only.

## Phase 1 Red result

The Adjudicator approved `LISS-0478 Phase 1 Red` on 2026-08-30. Added the
representative fixture
`tests/fixtures/semantic_meaning/interfer_phase_branch.sqx` and
`tests/test_liss_0478_interfer_phase_branch_meaning_red.py`.

The packet covers the phase/interference meaning distinction, branch/control
and child identity, unsupported finite projection with no artifact, and
inspection without QPU support. The phase/interference meaning test is
intentionally Red because the current canonical projection classifies both
calls as generic `expression`; the other four contracts pass. No production
code was changed.

Verification: `./.venv/bin/pytest -q
tests/test_liss_0478_interfer_phase_branch_meaning_red.py` reports `1 failed,
4 passed`, and `git diff --check` passes. Phase 2 Green requires separate
Adjudicator approval.
