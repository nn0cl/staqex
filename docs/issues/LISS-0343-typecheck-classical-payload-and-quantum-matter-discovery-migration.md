# LISS-0343: fix Classical `+`/`-` payload-collapse bug, then migrate `quantum_matter_discovery` to real units (WP-0095 work unit 11)

## Metadata

- Local issue ID: LISS-0343
- Status/phase: **complete** (2026-08-06) — PR
  [#402](https://github.com/nn0cl/staqex/pull/402) merged, commit
  `fbf0f58`
- Type: mixed — Kernel bug fix
  (`compiler/staqex/typecheck.py`) + Feature Path example content
  (`examples/showcase/quantum_matter_discovery/**`)
- Priority: P1
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 11 — `quantum_matter_discovery`, chosen over the 5 locked
  S01 files (Adjudicator selection, 2026-08-06: those need their own
  lock-boundary check first)
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md)
- Blocks: none within WP-0095
- Branch: `feature/liss-0343-typecheck-classical-payload-and-quantum-matter-discovery`
- GitHub Issue / PR: [#402](https://github.com/nn0cl/staqex/pull/402)
  (merged, `fbf0f58`)

## Design decision

### Part A — Kernel bug (discovered during this Issue's design intake)

`quantum_matter_discovery`'s `IsingCouplings.J`/`.h` must become `Energy`
(same real-unit requirement as every other qubit-Pauli-sparse-path
example in WP-0095). Doing so requires `field_scale(p) -> Float { return
p.J + p.h }` and `named_coeff_sum(p) -> Float { return p.J + p.h }` to
become `-> Energy`. Live probing during design intake found this fails
today: `typecheck.py::_infer_binop`'s "Classical ⊕ Classical" branch for
`+`/`-` hardcodes its result payload to the literal string `"Float"`
regardless of the actual operand payload, even though the *dimension*
(`left.dim`) is tracked correctly. So `Energy + Energy` type-checks as
`Classical<Float>` with an `Energy` dimension attached — a function
declared `-> Energy` that returns such a sum fails
`RETURN_TYPE_MISMATCH`. Confirmed via a minimal repro
(`add_energy(a: Energy, b: Energy) -> Energy { return a + b }` — fails
before the fix, compiles and runs after).

This is the fifth instance this WP-0095 program has found of the same
systemic category: a code path parallel to the runtime `evolve` formula
that was never updated when real-unit dimensioned quantities were
introduced (see LISS-0336, LISS-0337, LISS-0338, LISS-0341 for the prior
four).

**Adopted fix**: in the Classical `+`/`-` branch, compute the result
payload as: whichever operand's payload is *not* a bare numeric type
(`Int`/`Float`/`Bool`/`String`/`Any`) wins (preserving `Energy`,
`Time`, etc.); if both operands are bare numeric, fall back to the
existing legacy convention (`Float`, matching e.g. `Int + Int ->
Float`, which is relied upon elsewhere — see below). This is
deliberately **not** the shared `_promote()` helper as-is: `_promote`'s
own `if a == b: return a` shortcut would return `"Int"` for `Int + Int`
(since `_promote("Int","Int") == "Int"`), which regresses the existing
legacy convention.

**Regression found and resolved during this fix's own verification**:
applying `_promote(left.payload, right.payload)` directly broke
`tests/test_function_signatures_red.py::test_class_method_has_explicit_return_type_and_final_expression`
— a `Box` class method `fn doubled() -> State<Float> { return
dirac(this.x + this.x) }` where `this.x: Int`. The *existing*, already-
passing test expects `Int + Int` to type-infer as `Float` (so
`dirac(...)` produces `State<Float>`, matching the declared return
type) — i.e. that test encodes the legacy "classical addition of two
non-dimensioned numerics promotes to Float" convention as intended
behavior, not as a bug. The adopted fix (custom bare-numeric-vs-
dimensioned check, not raw `_promote`) satisfies both: `Energy + Energy
-> Energy` (the actual bug) and `Int + Int -> Float` (the pre-existing,
relied-upon convention) simultaneously. Confirmed via full regression
sweep: `pytest tests/ -q` returns to the pre-fix baseline (56 failed,
1211 passed — unchanged from LISS-0342's exit state), with no new
failures.

### Part B — `quantum_matter_discovery` real-unit migration

Same qubit-Pauli sparse-path pattern as B07/B08/B16
(LISS-0340/0341/0342): `IsingCouplings.J`/`.h` (`Float` → `Energy`,
ratio preserved) and `QuenchSchedule.duration` (`Float` → `Time`).
Unlike those single-file examples, this is a multi-file showcase slice,
so the struct-typed fields propagate through two free functions per
struct (`field_scale`/`named_coeff_sum` for `IsingCouplings`;
`schedule_duration` for `QuenchSchedule`) whose return types must be
retyped in lockstep — this is exactly what surfaced the Part A bug.

`build_ising_hamiltonian(J: Float, h: Float) -> Operator` in
`physics/ising_hamiltonian.sqx` is confirmed unimported by
`main_quantum_matter_discovery.sqx` (dead scaffolding, unrelated to the
wired `ising_hamiltonian(p: ...) -> Operator` overload actually used) —
left untouched, out of scope. `domain/model.sqx` and
`provenance/honesty.sqx` are likewise confirmed unimported — left
untouched.

This is the same "physically plausible, not literature-traced" honesty
category as A06/A10/A11 (transverse-field Ising model class is real;
the specific `J`/`h` magnitudes are illustrative, not pinned to a
published system).

## Intent

**Part A** (`compiler/staqex/typecheck.py`):
1. `_infer_binop`'s Classical `+`/`-` branch: replace the hardcoded
   `"Float"` result payload with a check that preserves a non-bare-
   numeric operand payload (Energy/Time/...) and otherwise falls back to
   the existing `"Float"` convention for bare Int/Float operands.

**Part B** (`examples/showcase/quantum_matter_discovery/`):
1. `domain/couplings.sqx`: `IsingCouplings.J`/`.h`: `Float` → `Energy`;
   `field_scale(p) -> Float` → `-> Energy`.
2. `physics/ising_hamiltonian.sqx`: `named_coeff_sum(p) -> Float` →
   `-> Energy`; `ising_hamiltonian(p) -> Operator` signature unchanged.
3. `protocol/quench.sqx`: `QuenchSchedule.duration`: `Float` → `Time`;
   `schedule_duration(s) -> Float` → `-> Time`.
4. `main_quantum_matter_discovery.sqx`: `IsingCouplings(1.0, 0.5)` →
   `IsingCouplings(1.0.eV to J, 0.5.eV to J)`; `QuenchSchedule(0.7)` →
   `QuenchSchedule(0.7.fs)`; `Float scale`/`Float coeff_sum` → `Energy`;
   `Float duration` → `Time`.

## Explicitly out of scope

- The sibling Classical `*`/`/` branches in `_infer_binop` (lines
  ~3322–3326), which likely have the identical hardcoded-payload issue
  — flagged for a future Issue, not fixed here (no live repro currently
  forces this path; do not fix speculatively).
- The pre-existing, separately documented Float relational-comparison
  mistyping (`>`/`<`/`>=`/`<=` returning `Classical<Float>` instead of
  `Classical<Bool>`), documented in LISS-0338's "Related, not blocking".
- `build_ising_hamiltonian` (unused), `domain/model.sqx`,
  `provenance/honesty.sqx` (unimported) — untouched.
- The 5 locked S01 files.
- Any other Kernel change.

## Acceptance reference

```gherkin
Feature: Classical Energy + Energy preserves its payload type

  Scenario: a function returning Energy computed via + type-checks and runs
    Given a function `add_energy(a: Energy, b: Energy) -> Energy { return a + b }`
    When it is compiled
    Then it does not raise RETURN_TYPE_MISMATCH

  Scenario: the legacy Int + Int -> Float convention is preserved
    Given a class method returning State<Float> via dirac(this.x + this.x) where x: Int
    When it is compiled
    Then it does not raise RETURN_TYPE_MISMATCH

Feature: quantum_matter_discovery uses real physical units

  Scenario: the migrated showcase slice compiles and runs to a real terminal measurement
    Given the migrated quantum_matter_discovery example (all 4 touched files)
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR, RETURN_TYPE_MISMATCH, or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live (isolated repros, not yet applied to the real files):
`Energy + Energy` compiles/runs after the typecheck.py fix;
`Int + Int` inside `dirac()` still type-checks against a declared
`State<Float>`; the full `quantum_matter_discovery` retyping plan above
(struct fields + function return types + call-site literals) compiles
and reaches a non-vacuum measurement when probed piece by piece.

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `S` — one small, targeted Kernel fix (single branch in one
  function) plus a 4-file example migration with struct-field/function-
  return-type propagation (more surface than the single-file B04/B07/
  B08/B16 migrations, but still mechanical once the Kernel fix lands).
- Route: direct implementation by this session.
- Confidence: high — both the Kernel fix and the migration plan were
  live-verified in isolation before this Issue was drafted; the fix's
  own regression was found and resolved before Red begins.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0343_typecheck_classical_payload_and_quantum_matter_discovery_migration_red.py`
      added (3 cases). Confirmed failing for the documented reasons with
      the `typecheck.py` fix temporarily reverted:
      `test_energy_plus_energy_preserves_energy_payload` →
      `RETURN_TYPE_MISMATCH` (`add_energy` returns `Classical<Float>`,
      declared `Classical<Energy>`);
      `test_quantum_matter_discovery_compiles_and_runs_to_a_real_terminal_measurement`
      → `EVOLVE_UNRESOLVED_UNIT_ERROR`.
      `test_int_plus_int_still_promotes_to_float_legacy_convention`
      passed even before the fix (regression guard, not a new-behavior
      assertion — it exists to catch exactly the raw-`_promote`
      regression found during this Issue's design intake).
- [x] Phase 2 Green: `typecheck.py`'s Classical `+`/`-` branch fixed
      (bare-numeric-vs-dimensioned payload check, not raw `_promote`);
      `quantum_matter_discovery`'s 4 files rewritten per Intent above.
      All 3 Red tests pass.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1215 passed, 55 failed (-1
      vs. the established 56-failed baseline, no new failures — **bonus
      fix**: `test_showcase_s1_thin_slice_red.py::test_s1_spine_compiles_and_runs`
      flipped from failing to passing; the locked S01 disaster-response
      spine independently hit the same Classical `+`/`-` payload-collapse
      bug this Issue fixes. Not otherwise touched — still work unit 12+.);
      `python3 tests/spec_verification/run_all.py` → 161/161 (100%, Gate:
      PASS, unchanged); `git diff --check` → clean.
- [x] WP-0095 work unit 11 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: `typecheck.py`の`_infer_binop`で
Classical同士の`+`/`-`が結果のpayload型を常に文字列`"Float"`に
ハードコードしていたバグを修正した（次元`dim`自体は正しく伝播していた
ため、これまで見過ごされていた）。これにより`Energy + Energy`が
`Classical<Float>`（Energy次元付き）として型推論され、`-> Energy`と
宣言した関数が`RETURN_TYPE_MISMATCH`で失敗していた。その後、
`quantum_matter_discovery`ショーケースの`IsingCouplings.J`/`.h`
（`Float` → `Energy`）と`QuenchSchedule.duration`（`Float` → `Time`）を
実単位化し、構造体フィールドの型変更が伝播する2つの自由関数
（`field_scale`/`named_coeff_sum`/`schedule_duration`）の戻り値型も
合わせて変更した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 修正方針として共有ヘルパー`_promote()`をそのまま使うと`Int + Int`が
  `"Int"`型推論されてしまい（`_promote`自身の`if a==b: return a`
  ショートカットのため）、既存の合格していたテスト
  （`test_class_method_has_explicit_return_type_and_final_expression`、
  `Int`同士の加算が`Float`に昇格することを前提にしている）を壊すことを
  実際に検証で発見した。`_promote`を直接使わず、「非ベア数値型
  （Energy/Timeなど）が片方でもあればそちらを優先し、両方ベア数値なら
  従来通りFloatにフォールバックする」という専用ロジックを`_infer_binop`
  内に直接書くことで両立させた。
- `*`/`/`の姉妹ブランチ（同ファイル内、行約3322-3326）にも同種の
  ハードコード疑いがあるが、今回はライブ実証で踏まれる経路が
  なかったため、意図的に修正していない（将来のIssue候補として
  design decisionに明記）。
- ボーナス修正として、ロック済みのS01 disaster-responseスパイン
  テストが偶然同じバグの影響を受けていて、今回の修正で合格するように
  なった。S01自体の実単位移行（work unit 12+）はまだ行っていない。

**人間がコードレビューで重点的に見るべきポイント**:
- `_infer_binop`内の新しい`_bare_numeric`判定ロジックが、将来
  追加されうる他の物理量型（例：`Frequency`, `Mass`など）に対しても
  正しく「非ベア数値」として扱われるか（`TYPE_DIMS`相当の判定に
  依存していないか、`Int`/`Float`/`Bool`/`String`/`Any`の固定集合との
  比較で十分か）。
- `quantum_matter_discovery`の`build_ising_hamiltonian`（未使用）、
  `domain/model.sqx`、`provenance/honesty.sqx`（未import）を意図的に
  未変更のまま残したことが、他のいかなる箇所からも将来的に
  importされないことの確認。

## Non-goals

- Sibling `*`/`/` Classical-payload branches (deferred, not fixed).
- Float relational-comparison mistyping (deferred, not fixed).
- The 5 locked S01 files (work unit 12+).
