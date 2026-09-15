# WP-0140: CityGML・graph・SOSA/SensorThings接続

| Field | Value |
|---|---|
| Status | done |
| Phase | phase-3-final-review-complete |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0523](../issues/LISS-0523-geographic-sensor-adapter-profile.md) |
| Depends on | [WP-0132](WP-0132-scientific-metadata-graph.md) |
| Blocks | WP-0141 |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A Proposed; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), X01 |
| Implementation permission | Phase 2 correction approved and implemented; Phase 3 final review reapproved |
| Current Next Issue | none for this bounded profile |

## Scope

一つの都市/センサーoffline profileをmappingし、geometry/LoD/topologyとObservationを結ぶ。

## Out of scope

GIS/センサー標準の再実装、実機tasking、全CityGML属性のsource化。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

X01のGiven/When/Thenを適用する。具体的検証: 方向付き多重edge、FOI/property/procedure、phenomenon/result time、CRS欠落/正当値、未解釈拡張を検証。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Phase 0 profile decisions

- Profile: `geosensor-x01-v1`; one offline city/sensor mapping, not a GIS or
  sensor-standard implementation.
- Fixture: in-memory records for one city object, one road object, two directed
  parallel edges, one sensor/procedure/property chain, and one observation.
  Each record has namespaced identity, revision, source hash, and profile version.
- Mapping: CityGML object/geometry/LoD map to Entity/FOI/Space; graph node/edge
  maps to typed Relation with direction/multiplicity/weight; SOSA/SensorThings
  roles map to Observation/Instrument/Procedure/ObservableProperty/FOI while
  preserving external IDs and source fields.
- Time: phenomenon, result, and ingest time remain separate. Unknown scale or
  precision is retained and never normalized silently.
- CRS: valid CRS/frame is preserved; absent CRS becomes `unknown` and is
  rejected or marked review-required for spatial computation; malformed CRS is
  quarantined. No coordinate inference is allowed.
- Extensions: unparsed fields remain hash-addressed raw evidence and cannot
  authorize execution. Geometry never implies road passability or routing.
- Numeric policy: mapping is exact at the record layer; fixture-specific
  comparison tolerances, if needed, are declared by the test and do not permit
  coordinate transformation.
- Technology: no GIS reader, RDF/graph database, SensorThings client, or other
  external dependency is selected. A concrete adoption requires a separate
  technology decision and minimal real-file evidence.

### Phase 1 Red inventory

The fixed Red suite will cover five acceptance groups: positive preservation,
unknown/missing handling, malformed input quarantine, non-inference of routing
semantics, and rejection of direct Graph/DTO execution injection. Tests belong
under `tests/` and use only fixed in-memory fixtures and fake ports.

## Phase 0 acceptance record

- `LISS-0523 Phase 0 acceptance 承認` received 2026-09-16.
- The Phase 1 Red inventory above is the only next authorized work; no
  production adapter or external dependency is authorized.

## Phase 1 Red result

- Six X01 contract nodes were added without production changes.
- The focused pytest suite reports **6 failed** due to the intentionally
  missing `geospatial_metadata` implementation module.
- Active-Red ownership is synchronized to `LISS-0523` / `WP-0140`.
- Next gate: `LISS-0523 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Six Red nodes were accepted unchanged on 2026-09-16.
- Review packet: `docs/collaboration/reviews/2026-09-16-liss-0523-phase1-red-review.md`.
- Next gate: `LISS-0523 Phase 2 Green / Implementation 承認`.

## Phase 2 Green result

- Added the provider-neutral `geospatial_metadata` profile implementation.
- It preserves X01 identity, geometry/LoD, directed parallel relations,
  observation roles and time fields, and keeps unknown/malformed state explicit.
- Focused X01 plus existing Metadata Graph regression: **14 passed**.
- All six Active-Red nodes passed and were removed from the lifecycle manifest.
- Next gate: `LISS-0523 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- CRS and raw-extension handling were split into focused helpers without
  changing the accepted contract.
- X01 and existing Metadata Graph regression: **14 passed**.
- Next gate: `LISS-0523 Phase 3 最終レビュー 承認`.

## Phase 3 final review finding

- Source hash is required by the accepted profile but is not observable in the
  implementation or asserted by the positive test.
- This is a bounded correction within Phase 2 scope; LISS-0523 is not done.
- Review packet: `docs/collaboration/reviews/2026-09-16-liss-0523-phase3-final-review.md`.

## Phase 2 Green correction result

- `LISS-0523 Phase 2 Green / Implementation 再承認` was received on
  2026-09-16.
- `source_hash` is now a required, validated lowercase SHA-256 value on each
  mapped record and is retained in its mapping evidence. The positive fixture
  asserts record-level and evidence-level observability.
- X01 plus existing Metadata Graph regression: **14 passed**; compile, diff,
  and lifecycle checks passed.
- The correction does not add provider, routing, execution, Semantic IR,
  QPU, tasking, or network behavior.
- Evidence: `docs/collaboration/reviews/2026-09-16-liss-0523-phase2-source-hash-correction.md`.
- Next gate: none for this bounded profile.

## Phase 3 final review re-review

- `LISS-0523 Phase 3 最終レビュー 再承認` was received on 2026-09-16.
- The source-hash correction satisfies the previously identified blocker;
  record and mapping-evidence values are both observable and asserted.
- X01 plus Metadata Graph regression: **14 passed**; compile, lifecycle, and
  diff checks passed.
- Review packet: `docs/collaboration/reviews/2026-09-16-liss-0523-phase3-final-review-rerun.md`.
- Process review: no operating-contract deviation or operational problem found.
- WP completion is limited to the offline provider-neutral X01 profile and does
  not imply external GIS/sensor, AWS, QPU, or scientific execution support.

## Risk / stop conditions

geometryから通行可否を推測。地理座標とlocal frameの無言混合。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとX01の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0140-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。
