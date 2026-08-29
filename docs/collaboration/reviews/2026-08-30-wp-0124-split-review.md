# WP-0124 split and completion review

| Field | Value |
|---|---|
| Work plan | [WP-0124](../../work-plans/WP-0124-real-run-evidence.md) |
| New work plan | [WP-0126](../../work-plans/WP-0126-human-real-qpu-execution.md) |
| Scope | separate hardware-required work from offline pilot preparation |
| Isolation | same_context; weaker than separate_context |
| Date | 2026-08-30 |

## Review result

Accepted as a planning split. WP-0124 now owns only offline evidence,
checklist, and validation preparation. WP-0126/LISS-0475 owns the human-only
device selection, credentials, network submission, Job observation, and raw
result handoff. No real device was contacted.

## Findings and dispositions

- The hardware boundary was not a new provider or architecture decision;
  it was separated into a new human-operated work unit.
- Existing LISS-0467–0469 contracts are not reopened.
- WP-0125 and LISS-0470 now depend on the separated real-run task; operations
  remains conditional and deferred.

## Verification

- Existing offline pilot and validation contract evidence remains green:
  LISS-0467–0469 focused suites previously passed.
- New Issue/WP IDs were checked against repository records.
- `git diff --check` — passed.

## Process review

No operating-contract deviation or operational problem found. The split is
recorded in the work plans, Issue register, and Open Work Register; the
status-drift lesson was applied.
