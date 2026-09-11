# Staqex documentation — current entry

## Scientific Workflow implementation status

[完成形設計案](architecture/scientific-workflow-complete-design.md)、
[受入仕様案](specs/staqex-scientific-workflow-acceptance.md)、
[WP-0131ロードマップ](work-plans/WP-0131-scientific-workflow-program.md)を追加した。
全科学分野を対象とし、実測S02を最優先にする。設計案・ロードマップと、個別に完了した
bounded実装単位を区別する。以下の現行Normative文書を置換しない。

S02では、assay batch cycle、再現性証拠、provider-neutralな量子・古典baseline比較を
ローカルPython APIとoffline fixtureで実装済みです。lineage、candidate、decode／feasibility、
objective、cost、runtime rejectionを検証します。これは実機実行や量子優位の主張ではなく、
AWS Braketなどのprovider接続はHost adapter側の別境界です。

実装進捗の現在値は[open-work register](architecture/open-work-register.md)、科学workflowの
全体計画は[WP-0131](work-plans/WP-0131-scientific-workflow-program.md)、受入境界は
[scientific workflow acceptance](specs/staqex-scientific-workflow-acceptance.md)を参照してください。

Read this page first. Detailed ADRs, Issues, Work Plans, and Traces are source
records, not parallel introductions to the project.

## Current normative documents

- [Language specification](specs/staqex-language-specification.md) — grammar,
  surface, and executable language contract.
- [Architecture overview](architecture/README.md) — current boundaries and
  implementation generations.
- [Current decision register](architecture/current-decision-register.md) —
  compressed map of the decisions developers need most often.
- [Decision theme register](architecture/decision-theme-register.md) — proposed
  `DEC-*` theme-based current reading surface.
- [Open-work register](architecture/open-work-register.md) — the single current
  list of open, deferred, and recently completed work.
- [Adjudicator language vision](architecture/adjudicator-language-vision.md) —
  physicist-first design priority.
- [Agent quickstart](architecture/agent-quickstart.md) — work intake and phase
  rules.
- [Documentation compression policy](architecture/documentation-canonicalization-policy.md)
  — how current pages and source records relate.

## Where historical detail lives

ADR, Issue, Work Plan, and Trace records are retained in the current tree only
when they carry an active decision, open obligation, acceptance boundary, or
required review evidence. Compressed records removed from the current tree are
recoverable from the baseline tag recorded in the
[compression map](architecture/documentation-compression-map.md).

Use the current register and decision pages for implementation work. Follow a
source pointer only when the exact historical reasoning or approval evidence is
needed.
