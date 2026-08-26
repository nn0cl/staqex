# LISS-0339: migrate `B04_evolve_not_loops` to a real-unit duration (WP-0095 work unit 7)

## Metadata

- Local issue ID: LISS-0339
- Status/phase: **complete** (2026-08-06) — PR
  [#394](https://github.com/nn0cl/staqex/pull/394) merged, commit
  `084feb4`
- Type: Feature Path (example content only —
  `examples/basics/B04_evolve_not_loops/evolve_not_loops.sqx`; no Kernel
  change)
- Priority: P1
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 7
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md),
  [LISS-0336](LISS-0336-evolve-real-unit-canonicalization-bugs.md)
- Blocks: none within WP-0095
- Branch: `feature/liss-0339-b04-evolve-not-loops-real-unit-migration`
- GitHub Issue / PR: [#394](https://github.com/nn0cl/staqex/pull/394)
  (merged, `084feb4`)

## Design decision

`B04_evolve_not_loops` uses the "legacy bare single-Pauli-letter" evolve
form (`evolve psi under Z for pi / 2.0`) — confirmed by reading
`compiler/staqex/runtime/quantum_ops.py::pauli_u` (already read during
LISS-0337/LISS-0338) that this specific code path is **not ℏ-divided**:
it treats its duration argument as a raw rotation angle
(`U = e^{-i·kind·t}` for unit Pauli `kind`), unlike the
`Operator`-declared/qubit-Pauli-sum paths ADR 0195 actually changed. This
is the same situation as `spec_verification/suites/sv17_quantum_mechanics_syntax.py`'s
`sv17-evolve-under-x` case (fixed in LISS-0337): the fail-closed
duration check (ADR 0195, LISS-0330) applies uniformly to *all* evolve
forms regardless of whether ℏ is actually consumed, so a bare literal
duration like `pi / 2.0` now fails `EVOLVE_UNRESOLVED_UNIT_ERROR` even
though the underlying physics doesn't need canonicalizing.

**Adopted fix** (identical pattern to LISS-0337's `sv17` fix): declare
`Time dur = 1.5707963267948966.s` (the precomputed `pi/2` value, in
canonical seconds — scale 1.0, so it passes through
`to_canonical_magnitude` unchanged) immediately before the evolve call,
with a short comment explaining that this legacy path treats the value
as a rotation angle, not real physical time. `pi / 2.0` cannot be used
directly as a bare unit-suffixed literal, since the unit-suffix grammar
only attaches to a literal `LitInt`/`LitFloat`, not an arbitrary
expression (confirmed during LISS-0337/0338) — hence the precomputed
decimal.

## Intent

1. Replace `evolve psi under Z for pi / 2.0` with `evolve psi under Z
   for dur`, declaring `Time dur = 1.5707963267948966.s` above it.
2. Add a one-line comment noting the legacy bare-Pauli-letter evolve
   form treats its argument as an angle, not physical time (matching
   ADR 0195's Kernel-level requirement without implying this teaches
   real-unit physics — B04's own teaching purpose, axiom 4
   `evolve`-not-loops, is unaffected).

## Explicitly out of scope

- Any Kernel change (the legacy `pauli_u` path's own non-ℏ-division
  behavior is confirmed correct/intentional for that path, not a bug).
- Any other example's migration (B07/B08/S01×5/quantum_matter_discovery).
- Rewriting B04 to demonstrate the `Operator`-declared evolve form
  instead — that's a different teaching example's job (e.g. B08).

## Acceptance reference

```gherkin
Feature: B04_evolve_not_loops uses a real Time-typed duration

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated evolve_not_loops.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: `Time dur = 1.5707963267948966.s; state psi = |+>; state
psi = evolve psi under Z for dur; ...` compiles and runs to a non-vacuum
measurement, in both the packaged and B04's actual unpackaged
(no `package`/`pub fn main`) source style.

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `XS` — one example file, one-line change plus a duration
  declaration.
- Route: direct implementation by this session.
- Confidence: high (identical, already-verified pattern from
  LISS-0337's `sv17` fix).

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0339_b04_evolve_not_loops_real_unit_migration_red.py`
      added. Commit `bc27f5d`: failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` on the bare `for pi / 2.0`
      duration).
- [x] Phase 2 Green: `.sqx` rewritten. Commit `3803b04`: 1/1 passed.
- [x] Phase 3 Refactor: no further change needed (single-purpose
      migration); reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1207 passed, 57 failed
      (unchanged failure count vs. LISS-0338's 57, no new failures — +1
      is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → 158/161 (98.14%, +1 vs.
      LISS-0338's 157/161 — the B04 SV case); `git diff --check` →
      clean.
- [x] WP-0095 work unit 7 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: `B04_evolve_not_loops`の裸のPauli文字
evolve形式（`evolve psi under Z for pi/2.0`）を、実Time型の値
（秒単位、π/2の値そのまま）に置き換えた。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- この経路（`pauli_u`）はADR 0195のℏ除算を受けないことを、LISS-0337の
  `sv17`修正時に既に確認済みだったため、今回は新たな調査なしに同じ
  パターンをそのまま適用した。

**人間がコードレビューで重点的に見るべきポイント**:
- コメントが「これは回転角であり物理的な時間ではない」という区別を
  読者に正しく伝えているか。

## Non-goals

- Kernel changes to `pauli_u`.
- Remaining example migrations (B07/B08/S01×5/quantum_matter_discovery).
