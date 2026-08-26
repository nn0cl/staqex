# LISS-0334: migrate `A06_topological_edge_memory` to real physical units (WP-0095 work unit 4)

## Metadata

- Local issue ID: LISS-0334
- Status/phase: **complete** (2026-08-05) — PR
  [#385](https://github.com/nn0cl/staqex/pull/385) merged, commit
  `780707a`
- Type: Feature Path (example content only, multi-file —
  `examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx`,
  `operators/hamiltonian_builder.sqx`, `README.md`; no Kernel/grammar
  change)
- Priority: P1
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 4
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md) (real
  ℏ, merged)
- Blocks: none within WP-0095 (each remaining migration is independent)
- Branch: `feature/liss-0334-a06-ssh-real-unit-migration`
- GitHub Issue / PR: [#385](https://github.com/nn0cl/staqex/pull/385)
  (merged, `780707a`)

## Design decision carried into this Issue (resolved before Plan approval)

`A06_topological_edge_memory` builds an SSH (Su-Schrieffer-Heeger)
tight-binding chain — a real, published physical model class (Su,
Schrieffer, Heeger 1979, cited in the README), unlike A05's abstract
QUBO. SSH hopping amplitudes are a real physical `Energy` quantity in
real materials (e.g. polyacetylene, typical scale ~eV). However, the
existing hop coefficients (`v_intra=0.5`, `w_inter=1.5`, a 1:3 ratio) are
not tied to any specific cited measurement — the README already
describes this example as "pedagogical," not a reproduction of a
specific paper's numeric SSH parameters. This was presented to the
Adjudicator as a design choice among three options and resolved before
Plan approval:

- **Adopted approach** (mirrors LISS-0332's treatment of A03's
  illustrative evolution duration, not a fresh literature derivation):
  convert the existing hop coefficients to real `Energy` values at an
  `eV` scale, preserving their existing 1:3 ratio unchanged, and
  document them as physically plausible in magnitude for a tight-binding
  system but **not** literature-traced to a specific measurement —
  consistent with the README's existing "pedagogical" framing.
- **Rejected**: a full literature derivation of real polyacetylene
  hopping/dimerization values (the A03 treatment) — rejected as
  disproportionate additional research effort for an example the README
  already discloses as pedagogical rather than literature-reproducing.
- **Rejected**: treating the coefficients as arbitrary non-physical units
  (the A05 treatment) — rejected because the SSH model's hopping
  amplitude is a genuinely real physical `Energy` quantity in real
  materials, unlike a QUBO cost weight; labeling it "arbitrary" would
  understate what the quantity physically represents.

## Intent

1. In `operators/hamiltonian_builder.sqx`, declare `Energy v = 0.5.eV to
   J` and `Energy w = 1.5.eV to J` inside `build_ssh_hamiltonian()`,
   replacing the bare `0.5`/`1.5` literals multiplying the `hop(i, j)`
   terms (ratio unchanged, confirmed live to compile and run across the
   module boundary).
2. In `main_topological_edge_memory.sqx`, replace `evolve psi under Hssh
   for 0.5` with a real `Time` duration (`fs`-scale, matching prior
   migrations' precedent).
3. Add a short comment in `hamiltonian_builder.sqx` and a new "Units and
   interpretation" README section stating the `eV` magnitudes are
   physically plausible for a tight-binding hopping amplitude but not
   traced to a specific cited measurement (contrast with A03; different
   honesty category from A05's arbitrary units).
4. Leave `SSHParams`/`band_gap`/`topological_index` (Float-typed,
   diagnostic-only "notebook quantities," never fed into `evolve`)
   unchanged — out of scope, no fail-closed check applies to them.

## Explicitly out of scope

- A literature-grounded derivation of real polyacetylene SSH parameters
  (rejected above).
- Reconciling `SSHParams` (currently unused by `build_ssh_hamiltonian()`,
  a pre-existing structural quirk) with the Hamiltonian builder — not
  part of this migration's scope.
- Any other example's migration (A10/A11/B04/B07/B08/B16/S01×5/
  quantum_matter_discovery).

## Acceptance reference

```gherkin
Feature: A06_topological_edge_memory uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated main_topological_edge_memory.sqx and hamiltonian_builder.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live in this session before finalizing the source: a minimal
reproduction of `build_ssh_hamiltonian()` returning an `Operator` built
from `Energy`-scaled `hop(i, j)` terms, called from `main()` with a real
`Time` duration, compiles and runs to a non-vacuum measurement
(`MeasurementEnvelope(value=4, ..., vacuum=False)`).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `S` — no Kernel change; two `.sqx` files' small edits, one
  README section addition.
- Route: direct implementation by this session.
- Assumptions: the `eV` magnitude and preserved 1:3 ratio are physically
  plausible for a tight-binding hopping amplitude; no specific literature
  measurement is claimed, per the design decision above.
- Confidence: high (syntax and cross-module behavior directly verified
  live).
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0334_a06_ssh_real_unit_migration_red.py`
      added. Commit `004c35b`: failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` on the bare `for 0.5` duration).
- [x] Phase 2 Green: `hamiltonian_builder.sqx`/`main_topological_edge_memory.sqx`
      rewritten with explicit `Energy`/`Time` values (ratio preserved).
      Commit `9ac57fb`: 1/1 passed. Confirmed via
      `test_applied_catalog_health_red.py`: A06 no longer appears in that
      test's failure list (only A10/A11 remain). **Bonus, unanticipated
      fix**: three other tests exercising A06's legacy "example10" source
      (`test_encapsulation_and_module_info.py::test_example10_runs`,
      `test_modern_oop_and_visibility.py::test_example10_no_module_info_required`,
      `test_oop_namespace_enum_struct.py::test_example10_ssh_linked_run`)
      also flipped from failing to passing — same root cause, not scope
      creep.
- [x] Phase 3 Refactor: README "Units and interpretation" section and two
      new Honesty-table rows added, contrasting explicitly with A03;
      reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1199 passed, 63 failed (-3
      vs. LISS-0333's 66, from the bonus fixes above; +1 vs. LISS-0333's
      1195 is this Issue's own new test, so net +4/-3 accounts for both);
      `python3 tests/spec_verification/run_all.py` → 135/145 (93.10%, +1
      vs. LISS-0333's 134/145 — the A06 SV case); `git diff --check` →
      clean.
- [x] WP-0095 work unit 4 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: `A06_topological_edge_memory`のSSH
タイトバインディングHamiltonianと evolve durationを、無次元の裸のリテラル
から実物理単位(`Energy`/`Time`、`eV`/`fs`)を持つ値へ移行した。A03の
文献値追跡でもA05の任意単位でもない、第三の誠実さの型（物理的に妥当な
オーダーだが特定文献の実測値ではない、README既存の"pedagogical"表現と
整合）を採用した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 既存の`v_intra:w_inter = 1:3`比率が実際のポリアセチレンの弱い二量化
  (典型的に10-20%程度)と整合しないことに気づいたが、この例が
  "pedagogical"と既に明記されていたため、文献値への修正ではなく比率を
  維持したまま単位のみeVスケールに変換する方針をAdjudicatorと合意した。
- Green中に、`test_encapsulation_and_module_info.py`等3つの無関係に
  見えたテストが実は同じA06のレガシーソース("example10")を経由していた
  ため、副次的に修正されたことを確認した — 意図しないスコープ拡大では
  なく、同一根本原因による副産物として明記した。

**人間がコードレビューで重点的に見るべきポイント**:
- README「Units and interpretation」の「物理的に妥当だが文献未追跡」と
  いう表現が、A03/A05との対比を含めて読者に誤解を与えないか。
- `SSHParams`が`build_ssh_hamiltonian()`に実際には渡されていない既存の
  構造上の乖離は、このIssueでは意図的にスコープ外としている。

## Non-goals

- Literature-grounded SSH/polyacetylene parameter derivation.
- Reconciling `SSHParams` with `build_ssh_hamiltonian()`.
- Remaining example migrations (A10/A11/B04/B07/B08/B16/S01×5/
  quantum_matter_discovery).

## Addendum (2026-08-05, LISS-0336)

Re-verification during [LISS-0336](LISS-0336-evolve-real-unit-canonicalization-bugs.md)
found this example was affected by the evolve-duration-canonicalization
bug (not the `_coalesce` epsilon bug, since this example's Hamiltonian
is built via the Fock/`hop()` path, not `compile_sparse_pauli`). Both
Kernel bugs are now fixed; this example was re-run under the fix and
confirmed to reach a non-vacuum measurement with a sensible, non-degenerate
marginal distribution across sites (not the `{0: 1.0}` identity
signature). No numeric coefficient/duration values in this example were
changed.
