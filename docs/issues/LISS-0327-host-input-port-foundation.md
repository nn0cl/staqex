# LISS-0327: `HostInputPort` foundation (ADR 0194, Follow-up item 1)

## Metadata

- Local issue ID: LISS-0327
- Status/phase: **complete** (2026-08-05) — PR
  [#366](https://github.com/nn0cl/staqex/pull/366) merged, commit
  `b1ce2bd`
- Type: Feature Path (Kernel — new `compiler/staqex/host_input_port.py`
  and `compiler/staqex/host_input_binding.py`; `Evaluator.__init__` gains a
  constructor parameter; `host.py`'s `submit_source`/`_submit_compiled`
  gain a `settings["inputs"]` passthrough. No grammar/parser/AST change.)
- Priority: P2
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [ADR 0194](../architecture/adr/0194-host-input-port-and-selection-predicate-semantics.md)
  Follow-up item 1
- Depends on: [ADR 0194](../architecture/adr/0194-host-input-port-and-selection-predicate-semantics.md)
  (Accepted — this Issue implements Decisions 1–2 only, the port and its
  validation, not the predicate logic)
- Blocks: [LISS-0328](LISS-0328-selection-projector-predicate-execution.md)
  (real `project ... onto feasible(...)` execution, ADR 0194 Follow-up item
  2 — depends on this port existing)
- Branch: `feature/liss-0327-host-input-port`
- GitHub Issue / PR: none yet

## Intent

Implement ADR 0194 Decisions 1–2, the port foundation only — no predicate
logic (that is LISS-0328's scope):

1. **`HostInputPort`** (`compiler/staqex/host_input_port.py`): a `Protocol`
   with `get(name: str) -> Any | None`, plus `MappingHostInputAdapter`
   (wraps a plain `dict`), matching `MeasureSinkPort`/
   `TextIOMeasureSinkAdapter`'s existing shape exactly
   (`compiler/staqex/measure_sink_port.py`).
2. **`Evaluator` constructor injection**: `Evaluator.__init__` gains
   `host_input: HostInputPort | None = None`, stored as `self.host_input`.
   Matches the existing `measure_sink`/`rng_port` injection pattern
   (`runtime/evaluator.py:195-221`) — no behavior change for any program
   that doesn't reference it.
3. **`host.py` passthrough**: `submit_source`/`_submit_compiled` read an
   optional `settings["inputs"]: dict[str, Any]`, wrap it in
   `MappingHostInputAdapter` when present, and pass it to `Evaluator(...)`
   as `host_input=`. When `settings` has no `"inputs"` key, `host_input`
   stays `None` — fully backward compatible with every existing caller.
4. **`compiler/staqex/host_input_binding.py`** (mirroring
   `parametric_binding.py`'s shape): two new diagnostic codes,
   `HOST_INPUT_BINDING_MISSING` and `HOST_INPUT_BINDING_VALUE_ERROR`, and a
   `validate_matrix_binding(name, value, n, *, dtype, symmetric=True) ->
   list[Diagnostic]` function checking: the value is present (not `None`);
   it is an `n×n` sequence-of-sequences; every element matches `dtype`
   (`bool`, or finite non-negative `float`/`int`); and `value[i][j] ==
   value[j][i]` for every pair when `symmetric=True`. Diagonal entries are
   never validated (never read by any consumer).

## Explicitly out of scope

- Any `feasible(...)` predicate logic, or any change to the `project`
  runtime op's dispatch — that is LISS-0328's scope entirely. This Issue
  adds a port and a validator that nothing calls yet.
- Any change to `Param<T>`/`parametric_binding.py` — confirmed unrelated
  (QPU-circuit-parameter-specific, never reaches the local evaluator).
- Adding `HostInputPort` to `CLAUDE.md`'s "External Resources Must Be
  Ports" list — ADR 0194 Follow-up item 3, a separate documentation-only
  change requiring its own stated reason and AI work trace.
- Any S02-specific naming or hardcoded matrix content (Class E discipline)
  — this port is general-purpose, like `RngPort`/`MeasureSinkPort`.

## Acceptance reference

New Phase 1 scenarios (no existing spec section covers this yet — this
Issue's own Red test is the acceptance evidence, per the established
pattern for infrastructure-only Issues):

```gherkin
Feature: HostInputPort foundation

  Scenario: an injected host input is readable by name
    Given an Evaluator constructed with host_input bound to {"m": <value>}
    When code queries self.host_input.get("m")
    Then it returns <value>

  Scenario: no host_input injected behaves exactly as today
    Given an Evaluator constructed without host_input
    When any existing program runs
    Then behavior is unchanged (self.host_input is None)

  Scenario: a valid n×n symmetric boolean matrix passes validation
    Given a 3×3 symmetric Bool matrix
    When validate_matrix_binding is called with dtype=bool, n=3
    Then no diagnostics are returned

  Scenario: a missing binding fails closed
    When validate_matrix_binding is called with value=None
    Then HOST_INPUT_BINDING_MISSING is returned

  Scenario: a non-square or asymmetric matrix fails closed
    When validate_matrix_binding is called with a 3×2 matrix, or a 3×3
      matrix where value[0][1] != value[1][0]
    Then HOST_INPUT_BINDING_VALUE_ERROR is returned naming the violation

  Scenario: settings["inputs"] passes through host.run_source unchanged
    Given settings={"target": "local", "seed": 0, "inputs": {"m": [[True]]}}
    When run_source is called
    Then the Evaluator constructed internally has host_input.get("m") == [[True]]
```

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `S` — two small new modules following an exact existing pattern
  (`measure_sink_port.py`), one constructor parameter, one settings-key
  passthrough. No grammar, no typecheck rule, no new AST.
- Route: direct implementation by this session.
- Assumptions: `n` (matrix width) is supplied by the caller at validation
  time (LISS-0328 will read it from the actual bound selection pattern's
  tuple length at runtime) — this Issue's validator takes `n` as a plain
  parameter and does not itself discover it.
- Confidence: high — the port shape is a direct structural copy of
  `MeasureSinkPort`, verified by direct reading before drafting this Issue.
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0327_host_input_port_red.py` added (7
      scenarios — the six above; the sixth split into a
      construction-injection test and a settings-passthrough test).
      Commit `feee837`: 3/7 failed for the documented reason
      (`Evaluator.__init__` didn't accept `host_input`; `host.py` had no
      `settings["inputs"]` passthrough). The other 4 (all of
      `validate_matrix_binding`'s scenarios plus `MappingHostInputAdapter`
      itself) already passed in the same commit, since those two modules
      were written as ordinary new standalone code with no existing stub
      to fail against — noted here rather than silently treated as
      pre-existing Red, per this session's honesty norm for partial-Red
      states (LISS-0322 precedent).
- [x] Phase 2 Green: `Evaluator.__init__` gained `host_input:
      HostInputPort | None = None`; `host.py::_submit_compiled` reads
      `settings.get("inputs")` and passes a `MappingHostInputAdapter`
      through. Commit `33736a3`: 7/7 passed; no existing test's behavior
      changed (verified via full regression); `Param<T>`/
      `parametric_binding.py` untouched.
- [x] Phase 3 Refactor: no further change — reviewed for unused
      imports/dead branches via `python3 -W error -c "import ..."` on all
      four touched/added modules, none found. Reviewer empathy summary
      below.
- [x] Full regression: `pytest tests/ -q` → 1243 passed; `python3
      tests/spec_verification/run_all.py` → 161/161; `git diff --check` →
      clean.
- [x] ADR 0194's Follow-up item 1 checked off.

## Reviewer empathy summary

**何を目的として何を変更したか**: ADR 0194で決定した`HostInputPort`を
実装した。`Evaluator`にコンストラクタ注入(`host_input`引数、
`measure_sink`/`rng_port`と同じ形)し、`host.py`の`settings["inputs"]`
から`MappingHostInputAdapter`を構築して渡す配線を追加した。バリデーション
(`validate_matrix_binding`)は形状/dtype/対称性をチェックしfail-closedで
2つの新診断コードを返す。`.sqx`側の新構文は一切追加していない。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `test_settings_inputs_passes_through_to_evaluator_construction`は、
  `host.py`内部で使われる`Evaluator`名前空間を一時的に差し替える
  (`tests/test_simulator_resource_execution_wiring_red.py`の既存の
  `_patched`パターンを踏襲)ホワイトボックステスト。`_submit_compiled`の
  内部実装詳細に依存しており、将来のリファクタで壊れやすい。
- `validate_matrix_binding`の対称性チェックは`O(n^2)`の全走査(効率化は
  していない)。ADR 0192のfixture規模(候補8〜16、選択2〜4)では問題に
  ならない前提。

**人間がコードレビューで重点的に見るべきポイント**:
- ホワイトボックステスト(`Evaluator`名前空間の一時差し替え)が、この
  種の配線検証として適切な境界か。
- `host_input`が`None`のままの既存プログラムに対する後方互換性(既存
  テスト1243件全通過で確認済みだが、念のため)。

## Non-goals

- `feasible(...)` predicate execution (LISS-0328).
- `CLAUDE.md` port-list documentation update (ADR 0194 Follow-up item 3).
