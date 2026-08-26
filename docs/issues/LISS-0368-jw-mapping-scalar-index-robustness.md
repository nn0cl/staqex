# LISS-0368: Jordan-Wigner mapping accepts named orbital indices and compound coefficient sums

## Metadata

- Local issue ID: LISS-0368
- Status/phase: **complete** (2026-08-08) — PR
  [#455](https://github.com/nn0cl/staqex/pull/455) merged, commit
  `0682e1a`
- Type: Kernel bug fix (`compiler/staqex/second_quantization.py`); no
  example content
- Priority: P3
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, found via a second general-purpose
  architectural audit (requested after LISS-0367) for the same "narrow
  AST-shape dispatch" bug category found repeatedly earlier this
  session
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0368-jw-mapping-scalar-index-robustness`
- GitHub Issue / PR: [#455](https://github.com/nn0cl/staqex/pull/455)
  (merged, `0682e1a`)

## Design decision

A second architectural audit (same category as LISS-0357/0358/0367:
narrow AST-shape dispatch rejecting a semantically-equivalent
but differently-shaped expression) found two gaps in
`second_quantization.py`'s Jordan-Wigner mapping, both live-verified
before drafting this Issue:

1. **`_orbital_index`**: only accepted a literal integer index
   (`create[0]`, or `create(0)` via the legacy Call form) — a named
   integer local carrying the identical value (`Int site = 0;
   create[site]`) was rejected with `SECOND_QUANTIZATION_MAPPING_
   UNSUPPORTED: Jordan-Wigner mapping requires a static integer
   orbital index`, even though `_scalar_value` (a few lines above,
   same file) already resolves named scalars through the `scalars`
   dict for coefficients — the same lookup mechanism, just not applied
   here. Confirmed live: `create[0] * annihilate[0]` (with the whole
   term correctly K-scaled) succeeds; `Int site = 0; create[site] *
   annihilate[site]` (identical value, named-var form) fails.
2. **`_scalar_value`**: only recognized `OpLit`, `OpVar`, and `OpBin`
   with `op == "*"` as a scalar coefficient — a compound coefficient
   combined with `+`/`-` (`(a + b) * create[0] * annihilate[0]`, both
   `a`/`b` known scalars) returned `None`, so `_expand` fell through
   to treating `(a + b)` as if it were itself a fermionic
   sub-expression, hit a bare `OpVar` case `_expand` doesn't handle,
   and raised `SECOND_QUANTIZATION_MAPPING_UNSUPPORTED: OpVar is not
   covered by the Jordan-Wigner mapping slice`. Confirmed live: a
   single-variable coefficient (`Float e0 = ...; e0 * create[0] *
   annihilate[0]`) succeeds; the identical numeric value split into a
   sum of two named scalars (`(a + b) * create[0] * annihilate[0]`)
   fails. **Notable**: `tests/test_liss_0367_fermion_operator_scalar_
   prefix_parse_red.py::test_compound_coefficient_then_atom_still_
   parses` already uses exactly this `(a + b) * create[0] *
   annihilate[0]` shape, but only asserts `compiled.ok` (parse
   success) — it was never run/mapped, so this execution-time gap
   was not caught by that Issue's own regression guard.

**Adopted fix**: both are minimal, additive generalizations mirroring
already-correct sibling logic in the same file:
- `_orbital_index` gains an `OpVar`/`Var`-in-`scalars` branch,
  mirroring `_scalar_value`'s existing named-scalar lookup, before
  falling back to the same fail-closed error for a genuinely
  non-static index.
- `_scalar_value`'s `OpBin` case is widened from `op == "*"` to
  `op in {"*", "+", "-"}`, mirroring `_expand`'s own already-correct
  handling of `+`/`-` between two Pauli sub-expressions (this file's
  own established convention that `-` is always the binary form,
  documented at `_expand`'s `-` case).

Threading `scalars` into `_orbital_index` required updating its 4
call sites inside `_expand` (both the `OpIndexed` and legacy `Call`
forms, for both `create` and `annihilate`) — mechanical, no behavior
change beyond passing the already-available `scalars` argument through.

## Explicitly out of scope

- The `finite_binder.py::_contains_second_quantized` `adjoint(...)`
  recognition gap raised as a fourth candidate during the same audit —
  the audit's own repro attempt for it failed for unrelated syntax
  reasons and was not independently confirmed; not pursued in this
  Issue pending a correctly-verified repro.
- The `parser.py::_type_first_bind` `Float[M…] row = h[i]` struct/
  class-field-then-index gap found in the same audit — a different
  file/layer, tracked separately as LISS-0369.

## Acceptance reference

```gherkin
Feature: Jordan-Wigner mapping accepts named orbital indices and compound coefficient sums

  Scenario: a named integer local as an orbital index is accepted
    Given `Int site = 0; FermionOperator<Orbitals> H = K * create[site] * annihilate[site]`
    When compiled and run
    Then it does not raise SECOND_QUANTIZATION_MAPPING_UNSUPPORTED

  Scenario: a compound (sum-of-named-scalars) coefficient is accepted
    Given `Float a = ...; Float b = ...; FermionOperator<Orbitals> H = (a + b) * create[0] * annihilate[0]`
    When compiled and run
    Then it does not raise SECOND_QUANTIZATION_MAPPING_UNSUPPORTED

  Scenario: the existing literal-index and single-variable-coefficient forms are unaffected
    Given `create[0] * annihilate[0]` and `Float e0 = ...; e0 * create[0] * annihilate[0]`
    When compiled and run
    Then both behave exactly as before (regression guard)
```

## Verification plan for this design intake (not shipped as a test)

Both gaps confirmed live before drafting this Issue (each fails
identically pre-fix with the documented error); the fix's target
behavior (both new forms succeed, with the same measured outcome as
the equivalent already-working form) confirmed live before
implementing. Full `pytest tests/ -q` sweep after the fix, diffed
against the current baseline (0 failed, 1312 passed — `main` is fully
green), confirming no regression. `spec_verification` expected
unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — two small, targeted generalizations in one file, each
  mirroring an already-correct sibling pattern in the same module;
  both gaps and their fixes live-verified before drafting.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0368_jw_mapping_scalar_index_robustness_red.py`
      added (4 cases). Confirmed 2 of 4 failing with the fix reverted
      (`SECOND_QUANTIZATION_MAPPING_UNSUPPORTED`, matching each
      documented finding exactly); the other 2 (regression guards for
      the literal-index and single-variable-coefficient forms)
      correctly already passed.
- [x] Phase 2 Green: `second_quantization.py::_orbital_index` gained
      an `OpVar`/`Var`-in-`scalars` branch (mirroring `_scalar_value`'s
      existing lookup); `_scalar_value`'s `OpBin` case widened from
      `op == "*"` to `op in {"*", "+", "-"}` (mirroring `_expand`'s own
      `+`/`-` handling). All 4 tests pass.
- [x] Phase 3 Refactor: no further code change needed; reviewer
      empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1316 passed, 0 failed
      (unchanged — `main` stays fully green; +4 this Issue's own new
      tests); `python3 tests/spec_verification/run_all.py` → 161/161
      (100%, Gate: PASS, unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: LISS-0367に続く2回目のアーキテクチャ
監査で発見した、Jordan-Wigner写像の2つの狭いAST形状依存ギャップを
修正した。`_orbital_index`はリテラル整数添字のみを受理し、同じ値を
持つ名前付き整数変数（`Int site = 0; create[site]`）を拒否していた
——同じファイル内の`_scalar_value`が既に係数に対して行っている
名前付きスカラー検索と同一のメカニズムを、添字にも適用した。
`_scalar_value`は`*`のみをOpBin係数として認識し、`(a + b)`のような
`+`/`-`を含む複合係数を拒否していた——`_expand`が既にPauli部分式間の
`+`/`-`を正しく処理している規約をそのままミラーした。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `_scalar_value`のdocstringが「a product/unary-minus of these」と
  書いていたため、単項マイナス表現の可能性を検討したが、`_expand`の
  既存`-`ケースが常に二項形式（lhs - rhs）を前提としていることを
  確認した上で、同じ前提を`_scalar_value`側にも一貫して適用した
  （このファイル全体の既存規約に従っただけで、新しい仮定は導入して
  いない）。
- `_orbital_index`への`scalars`引き渡しが、`_expand`内の4箇所の
  呼び出し全て（`OpIndexed`/legacy `Call`形式 × `create`/
  `annihilate`）で機械的に必要だったことを確認し、漏れなく更新した。
- LISS-0367の回帰テスト`test_compound_coefficient_then_atom_still_
  parses`が、まさに本Issueで修正した複合係数の形（`(a + b) *
  create[0] * annihilate[0]`）をパース成功のみ検証していて実行時
  ギャップを見逃していたことを、本Issueの調査で発見した——LISS-0367
  自体の訂正は不要（パースは実際に成功していたため主張は正しい）だが、
  実行時の別ギャップが同じ式形状に存在していたことを記録した。

**人間がコードレビューで重点的に見るべきポイント**:
- 特になし（既存の兄弟ロジックへの局所的・加算的な拡張、副作用なしを
  回帰テストで確認済み）。

## Non-goals

- The `adjoint(...)` binder-recognition candidate (unverified, not
  pursued here).
- The `parser.py` struct-field-index gap (tracked as LISS-0369).
