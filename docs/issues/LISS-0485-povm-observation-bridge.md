# LISS-0485: POVM observation bridge

| Field | Value |
|---|---|
| Status | **phase-1-red — failing acceptance tests added; Phase 2 approval required** |
| Phase | phase-1-red |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#liss-0485-povm-observation-bridge-design) |
| Related authority | [LISS-0037 / WP-0014](../work-plans/WP-0014-povm-measurement-contract.md), [LISS-0084](LISS-0084-general-mixed-states-channels-povms.md), ADR 0075 |
| Depends on | LISS-0481, LISS-0482, LISS-0484 |
| Implementation permission | Phase 1 test-only scope approved; no implementation permission |
| Next approval | Phase 2 Green approval |

## Architecture/spec approval

- The bridge boundary is accepted as a Semantic IR contract only.
- LISS-0084 remains authoritative for POVM effect representation and
  execution mathematics.
- No public POVM syntax, numerical effect evaluation, provider/QPU, AWS, or
  Rust implementation is authorized by this approval.

## Phase 1 Red result

- Added `tests/test_liss_0485_povm_observation_bridge_red.py`.
- The tests require request/effect-set identity, state domain, lane, sampling
  and collapse boundary, post-state/provenance evidence, and explicit
  rejection evidence without repair or fabricated outcomes.
- No POVM numerical or provider implementation was changed.

## Scope

Define the Semantic IR bridge for future POVM observations. Record POVM
identity, state domain, outcome carrier, effect validity, lane, capability,
collapse boundary, provenance, exactness, and dimensions.

## Acceptance scenarios

- A POVM request remains non-sampling until terminal measurement.
- A valid terminal POVM preserves effect-set identity and state lineage in its
  measurement-envelope contract.
- Incomplete, non-positive, or domain-mismatched effects reject explicitly and
  are never silently repaired.
- Unsupported targets preserve POVM intent and emit stable capability evidence
  without fabricating an outcome.
- Existing computational-basis pure/mixed measurement behavior is unchanged.

## Boundary decisions

- Define a source-derived POVM request metadata shape in Scientific Semantic
  IR; do not add mandatory public syntax yet.
- Represent `valid`, `incomplete`, `non_positive`, and `domain_mismatch` as
  evidence statuses; do not normalize or repair.
- Use `MeasurementEnvelope<T>` for terminal result metadata; repeated-shot
  estimation belongs to Host tomography and LISS-0084.
- LISS-0084 owns effect representation and execution mathematics; LISS-0485
  owns only the observation-algebra bridge.

## Exclusions and stop conditions

No general effect storage, Kraus/Choi execution, positivity algorithms,
tomography estimation, dynamic measurement, provider SDK, QPU, AWS, or Rust.
Stop for a new ADR if the bridge changes `State<T>` semantics, public POVM
syntax, or the LISS-0084 representation authority.

## Phase 1 candidate files

Normative bridge section, IR contract tests, invalid-effect evidence fixtures,
and review record only.
