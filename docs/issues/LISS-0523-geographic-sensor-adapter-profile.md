# LISS-0523: CityGML・graph・SOSA/SensorThings接続

| Field | Value |
|---|---|
| Local ID | LISS-0523 |
| Status | done |
| Phase | phase-3-final-review-complete |
| Type / priority | feature / P1 |
| Initial/current size | M / M |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0515 |
| Blocks | LISS-0524 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0140](../work-plans/WP-0140-geographic-sensor-adapter-profile.md), AIP-WP-0140-2026-09-08-001 |
| Acceptance notes | X01; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217/acceptance review; profile/technology if needed; distinct Phase 1, Phase 2/Implementation, Phase 3 approvals |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

## Phase 0 acceptance/profile review

### [DESIGN CHECK]

- Scope: `geosensor-x01-v1`という一つのoffline地理・センサーprofileに限定
  し、CityGML object、方向付きnode/edge、SOSA/SensorThings観測を
  Canonical Scientific Metadata Graphへ写像する。
- Authority: ADR 0217-AがMetadata identity/trust/adapter mappingを承認済み。
  ADR 0211のsource-derived Semantic IR権威と、X01受入仕様を変更しない。
- Boundary: adapterは外部ID、schema/version、元field、hash、mapping結果を
  保持する。道路の通行可否、危険度、経路選択、座標系の推定はUseCase/Domain
  の別契約であり、このprofileは決定しない。
- Required evidence: topology/geometry/LoD、FOI/property/procedure、
  phenomenon/result/ingest time、CRS/frame状態、source/provenance、未知拡張、
  positive/negative rejection envelope。
- Omitted context: 全CityGML属性、Tasking/live sensor、GIS/graph DB、SDK、
  QPU、S01 rolling replan、parser/source syntax、Semantic IR実行。
- Applied lessons: metadata authorityと実行authorityを分離し、外部adapterの
  concrete実装を追加せずにmapping証拠を先に固定する。unknown/invalidを0や
  既定座標へ補完しない。

### Fixed profile decision

| Item | Decision |
|---|---|
| Profile identity | `geosensor-x01-v1`、fixtureとmapping schemaを版管理 |
| Input boundary | fake `GeospatialObservationSourcePort`相当のin-memory records。外部reader/SDKは使用しない |
| CityGML mapping | city/building/road object → Entity/FOI、geometry/LoD → Space、source object ID/versionを保持 |
| Graph mapping | node/edge → typed Relation。方向、多重edge、weight、validity、endpoint identityを保持 |
| Observation mapping | SensorThings/SOSAのThing/Location/Sensor/Datastream/ObservedProperty/Observation/FOIを、Entity/Space/Instrument/Procedure/ObservableProperty/Observation/FOIへ写像 |
| Time mapping | phenomenon/result/ingest timeを別fieldで保持。scale/precision/unknownを保持しUTCへ補完しない |
| CRS/frame | 正当なCRS/frameは保持。欠落は`unknown`として保管し、空間演算が必要なbindingはreject/review-required。形式不正はquarantine |
| Extensions | 未解釈拡張はraw hash・source span・profile version付きで保管し、実行可能fieldへ昇格しない |
| Tolerance | Graph mappingは数値近似を行わない。geometry検査の許容値はfixtureごとに明示し、座標変換の許可とは別管理 |
| Technology | 特定GIS/ontology/graph DB/SDK/versionは未選定。Technology approvalを別途要求 |

### Acceptance matrix for Phase 1 Red

1. Positive: city/road object、方向付き平行edge、sensor、observationをmapping
   すると、object identity、LoD、geometry、relation direction/multiplicity、
   FOI/property/procedure、3種類のtime、source hashが全て観測できる。
2. Positive: CRS欠落、not-applicable property、未解釈拡張は、それぞれ
   `unknown`/理由/hash付きrawとして保持され、入力を破壊しない。
3. Negative: 存在しないrelation endpoint、同一namespace/revisionで異なる
   content、型不正のgeometry/CRSはquarantineまたはrejectし、Graphを成功扱いしない。
4. Negative: geometryだけを与えても、road passability、traffic status、
   routing decisionを生成しない。Tasking/live actuationも生成しない。
5. Negative: Graph/DTOを直接Semantic IRや実行計画へ注入できず、実行意味が
   必要な場合は通常のbinding/source/IR境界へ戻る。

### Phase 0 result

- `WP-0140 / LISS-0523 Phase 0 acceptance/profile review`を実施し、上記profile、
  fixture、boundary、diagnostic、technology除外を確定した。
- Phase 1 Redは上記5群に対応する固定fixtureとテストだけを追加する。実装、
  外部依存、ネットワーク、live sensorは含めない。
- Review packet: `docs/collaboration/reviews/2026-09-16-liss-0523-phase0-acceptance-review.md`
- Next approval: `LISS-0523 Phase 0 acceptance 承認`。承認後にPhase 1 Redを別途要求する。

## Phase 0 acceptance result

- Adjudicator approval: `LISS-0523 Phase 0 acceptance 承認`, received
  2026-09-16.
- The `geosensor-x01-v1` profile, fixed in-memory fixture boundary, mapping
  contract, unknown/quarantine policy, and non-inference boundary are accepted.
- No technology selection, external dependency, Phase 1 test, or implementation
  permission is inferred from this acceptance.
- Next approval: `LISS-0523 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0523 Phase 1 Red 承認`, received 2026-09-16.
- Added only `tests/test_liss_0523_geospatial_sensor_profile_red.py` with six
  focused nodes covering positive mapping, unknown/evidence retention,
  malformed input, non-inference, and non-execution authority.
- Pytest result: **6 failed** because `compiler.staqex.geospatial_metadata`
  does not exist yet; no production code or existing assertion was changed.
- Direct runner result: all six nodes were collected and reported as failures.
- Active-Red ownership is recorded in `docs/testing/active-red-tests.toml`.
- Next approval: `LISS-0523 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review result

- Adjudicator approval: `LISS-0523 Phase 1 Red テストレビュー承認`, received
  2026-09-16.
- All six Red nodes were accepted unchanged. The review confirmed that they
  remain limited to the accepted X01 mapping and non-execution boundaries.
- Review evidence: `docs/collaboration/reviews/2026-09-16-liss-0523-phase1-red-review.md`.
- No implementation permission is inferred from this review.
- Next approval: `LISS-0523 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0523 Phase 2 Green / Implementation 承認`,
  received 2026-09-16.
- Added `compiler/staqex/geospatial_metadata.py` as a provider-neutral,
  immutable descriptive X01 profile. It validates record identity, geometry,
  CRS state, relation endpoints, and profile version while retaining raw
  extension evidence.
- The profile explicitly has no routing, tasking, Semantic IR, or QPU
  execution authority. No external dependency or network path was added.
- Focused X01 suite and existing Metadata Graph regression: **14 passed**.
- Active-Red entries were removed after all six exact nodes passed.
- Next approval: `LISS-0523 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0523 Phase 3 Refactor 承認`, received
  2026-09-16.
- CRS validation and raw-extension evidence construction were extracted into
  focused helpers; geometry and relation validation remain explicit.
- Assertions and behavior are unchanged. X01 plus Metadata Graph regression:
  **14 passed**; compile, diff, and lifecycle checks passed.
- Reviewer empathy summary: the module now separates profile validation,
  source-evidence construction, and snapshot assembly so boundary changes are
  easier to audit.
- Next approval: `LISS-0523 Phase 3 最終レビュー 承認`.

## Phase 3 final review result

- Adjudicator approval: `LISS-0523 Phase 3 最終レビュー 承認`, received
  2026-09-16.
- Verification passed: X01 plus existing Metadata Graph regression **14
  passed**, with compile, diff, and lifecycle checks successful.
- Blocker: the accepted profile requires observable source hash evidence, but
  the implementation exposes only source ID/profile and the positive test does
  not assert a record-level source hash.
- Review packet: `docs/collaboration/reviews/2026-09-16-liss-0523-phase3-final-review.md`.
- Next approval after correction: `LISS-0523 Phase 2 Green / Implementation 再承認`.

## Phase 2 Green correction result

- Adjudicator reapproval: `LISS-0523 Phase 2 Green / Implementation 再承認`,
  received 2026-09-16.
- The fixed X01 records now require a lowercase 64-character SHA-256 source
  hash. The value is preserved on both `GeospatialRecord.source_hash` and
  `MappingEvidence.source_hash`, and the positive contract test asserts both
  observations.
- Focused X01 suite plus existing Metadata Graph regression: **14 passed**.
- The correction is limited to source-evidence observability. Routing,
  tasking, Semantic IR, QPU projection, external dependencies, and network
  behavior remain unchanged.
- Correction evidence: `docs/collaboration/reviews/2026-09-16-liss-0523-phase2-source-hash-correction.md`.
- Next approval: none for this bounded issue; commit/PR operations remain separate.

## Phase 3 final review re-review result

- Adjudicator approval: `LISS-0523 Phase 3 最終レビュー 再承認`, received
  2026-09-16.
- The source-hash blocker is resolved. Record-level and mapping-evidence
  observability are both tested.
- X01 plus existing Metadata Graph regression: **14 passed**; compile, test
  lifecycle, document lifecycle, and diff checks passed.
- Review packet: `docs/collaboration/reviews/2026-09-16-liss-0523-phase3-final-review-rerun.md`.
- Process review: no operating-contract deviation or operational problem found.
- This completion covers only the provider-neutral offline X01 profile. It does
  not claim GIS/SOSA client, live sensor, AWS, QPU, or scientific-execution
  validation.
