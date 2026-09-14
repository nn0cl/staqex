# LISS-0543 Phase 1 Red review packet

## Review Target

- Artifact: LISS-0543 active-Red lifecycle and refactor-baseline tests
- Current phase: Phase 1 Red
- Requested approval: acceptance of the 12 failing contracts
- Approval type: phase
- Approved scope: test lifecycle authority and generated refactor evidence;
  no production refactor or behavior correction
- Implementation allowed: no
- Post-review required: yes; separate Phase 2 Green / Implementation approval
- Execution batch ID: not applicable

## What Changed

- Eight tests define the machine-readable active-Red lifecycle, deterministic
  validation codes, and per-file pytest exclusion output.
- Four tests define deterministic public-import/runtime/QASM/diagnostic
  baseline output and atomic missing-input rejection.
- Two small `.sqx`/TOML fixtures define representative input; no production or
  CI file changed.

## Findings and dispositions

- Apply: use TOML schema version 1 and Python's standard-library `tomllib`; no
  dependency selection is needed.
- Apply: validation uses an explicit `--as-of` date so expiry tests are not
  wall-clock dependent.
- Apply: validated ignore output is one exact `--ignore=<path>` argument per
  entry; global suffix exclusions are forbidden.
- Apply: baseline output excludes timestamps, absolute paths, and current
  working directory so it can be compared byte-for-byte.
- Already closed with evidence: tests do not invoke network, provider SDK,
  credentials, or live QPU.
- Out of scope: classification and repair of each existing failure; a real
  behavior defect requires its own Feature Path Red/Green approval.

## Failure scenarios reviewed

- Done or unknown issue retains an exclusion.
- Excluded test is missing or registered more than once.
- Human review deadline is expired.
- CI still contains `--ignore-glob='*_red.py'`.
- Baseline input is missing and must not leave a partial artifact.
- Nondeterministic timestamp/path data enters baseline evidence.

## Remaining blockers

- Both production scripts are intentionally absent, so all 12 tests are Red.
- The current repository-wide 19 failures remain unresolved and cannot be
  classified or changed in Phase 1.
- Review isolation is `same_context`, which is weaker than
  `separate_context`; this author check does not replace Adjudicator review.

## Verification result

- Focused pytest: 12 failed, all from missing approved implementation scripts.
- `py_compile`: pass for both test files.
- `git diff --check`: pass.
- Full pytest and Spec Verification: not rerun because Phase 1 added only
  intentionally failing tests and fixtures; they remain required in Green.

## Next approval required

After Adjudicator accepts this Red contract set:
`LISS-0543 Phase 2 Green / Implementation 承認`.

## Evidence links

- Canonical specification:
  [core module decomposition](../../specs/staqex-core-module-decomposition.md)
- Issue: [LISS-0543](../../issues/LISS-0543-regression-authority-for-refactor.md)
- Representative trace:
  [core module decomposition trace](../traces/2026-09-11-core-module-decomposition-design.md)
