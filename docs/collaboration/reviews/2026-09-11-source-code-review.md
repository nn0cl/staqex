# 2026-09-11 Source Code Review

## Review packet

- Scope: `compiler/staqex/`, root test suites, CI, executable examples, and the
  specifications that define the source-to-QPU and scientific-workflow
  boundaries.
- Canonical documents: `docs/specs/staqex-language-specification.md`,
  `docs/specs/staqex-scientific-semantic-consumer-migration.md`,
  `docs/specs/staqex-scientific-workflow-acceptance.md`,
  `docs/specs/staqex-multi-provider-qpu-execution-contract.md`,
  `docs/issues/LISS-0541-s02-quantum-baseline-comparison.md`, and
  `docs/issues/LISS-0542-sqxa-target-build.md`.
- Changed files: this review, its representative trace, and one process lesson;
  production code is unchanged.
- Isolation: `same_context`, as configured by
  `docs/collaboration/runtime-routing.toml`. This is weaker than
  `separate_context`; the findings below therefore remain subject to human
  adjudication before implementation.
- Verification: CI-equivalent pytest 77 passed / 2 deselected; full pytest
  2031 passed / 19 failed; Spec Verification 161/161 passed; `compileall`,
  document lifecycle, coverage-ledger consistency, and `git diff --check`
  passed before this document was written.
- Remaining blockers: P0 and P1 findings below. The repository is not ready to
  claim a fully green regression suite or a fail-closed deployable artifact
  contract until they are resolved.
- Next approval required: scope/Phase 0 acceptance for the proposed P0 repair
  work plan. This review does not grant implementation permission.

## Executive assessment

The implementation has a substantial and coherent provider-neutral core:
source parsing, semantic IR, local evaluation, static OpenQASM lowering,
artifact packaging, Host submission contracts, and scientific workflow
fixtures are all represented in code. Spec Verification is fully green, and
the main architectural boundary—Kernel meaning versus Host/provider
transport—is visible.

The largest immediate risk is not missing feature breadth but false confidence
from the regression gate. CI ignores every `*_red.py` file. That excludes 440
of 457 test files, including tests whose associated issues are marked complete,
and hides 19 current failures. Two further fail-closed boundaries can be
violated with small inputs: S02 comparison accepts non-finite/empty lineage and
negative costs as a successful match, and the `.sqxa` loader accepts a manifest
whose declared version, kind, and identity contradict its payload. These are
repairable locally and should precede broader feature work.

## Findings by priority

| ID | Priority | Area | Finding | Disposition |
|---|---:|---|---|---|
| CR-001 | P0 | CI / regression authority | CI excludes 440 `*_red.py` files and reports green while the complete local suite has 19 failures. | Apply first |
| CR-002 | P0 | S02 assay integrity | `FrozenAssaySnapshot.__post_init__` is defined at module scope, so revision validation and defensive freezing never execute. | Apply first |
| CR-003 | P1 | S02 comparison | NaN objectives/tolerance, negative cost, and empty identities can produce `status="matched"`. | Apply after CR-001/002 |
| CR-004 | P1 | `.sqxa` integrity | Loader verifies only format and payload hash; contradictory manifest version/kind/identity is accepted. | Apply after CR-001 |
| CR-005 | P1 | Semantic migration | Completed semantic-authority issues still have failing contracts or stale expectations, so migration completion is not machine-verifiable. | Reconcile under CR-001 |
| CR-006 | P2 | Maintainability | Parser/typechecker/evaluator and QASM lowering concentrate too many responsibilities and use silent fallback catches at semantic boundaries. | Decompose incrementally |
| CR-007 | P2 | Reproducibility / quality gates | There is no Python project/dependency manifest or lock, and CI has no lint, type, coverage, or dependency audit gate. | Plan after correctness repair |
| CR-008 | P2 | Documentation | Multi-provider contract still says `.sqxa` implementation is unauthorized although LISS-0542/WP-0159 are done. | Correct with implementation work |

## Detailed findings

### CR-001 — CI does not exercise the repository's regression authority

`.github/workflows/ci.yml:296-303` ignores `*_red.py` globally. The naming was
introduced for AT-TDD Phase 1, but the files remain named `*_red.py` after Green
and Phase 3. Today 440 of 457 test files match that suffix. The CI-equivalent
command therefore runs only 77 passing tests and deselects two named tests,
while the unfiltered suite reports 2031 passing and 19 failing tests.

The failures are not confined to open work. LISS-0234, LISS-0476, LISS-0477,
LISS-0485, and LISS-0486 are recorded complete/done, yet their contract files
fail. Other failures expose changed diagnostics or DTO contracts. A branch can
therefore merge while violating an accepted contract, and neither issue status
nor CI currently identifies whether a failure is intentional Red, stale test,
or product regression.

Required repair:

1. Add explicit test-state metadata independent of filenames, or rename a Red
   file when Green is approved.
2. Build a machine-readable allowlist containing only genuinely active Red
   tests, each linked to an open issue and expiry/phase.
3. Make all completed-issue tests blocking.
4. Reconcile the 19 failures one contract family at a time; do not weaken tests
   merely to make the suite green.
5. Add a CI check that rejects a completed issue whose tests remain excluded.

### CR-002 — S02 snapshots are not actually frozen or revision-validated

In `compiler/staqex/s02_assay_profile.py:34-50`, `__post_init__` is indented at
module scope rather than as a method of `FrozenAssaySnapshot`. Dataclasses only
invoke a class method, so the intended positive-revision check and conversion
to `MappingProxyType` never run. Callers can construct revision zero/negative
snapshots and mutate the supplied metadata and records after construction.

This breaks the module's stated frozen-snapshot/provenance boundary and can
change scientific input after validation. The current D01 tests do not detect
the constructor defect; three of them instead fail because the test expects
attribute records while production deliberately exposes mappings.

Required repair: first decide and specify the public record DTO (typed record
or immutable mapping), then add constructor tests for revision bounds, nested
input aliasing, metadata mutation, and raw-to-curated identity preservation.
Move `__post_init__` into the class and copy/freeze all accepted mutable input
at the agreed depth.

### CR-003 — invalid S02 comparison evidence can be reported as matched

`compiler/staqex/s02_quantum_baseline_comparison.py:52-57` treats every
non-`None` cost as complete, and lines 260-266 compare objectives without
checking finiteness or tolerance validity. Lineage fields also default to empty
strings. A reproduced input with NaN classical/quantum objectives, NaN
tolerance, a negative execution cost, and empty identities returned:

```text
status=matched gap=nan cost=-1.0 snapshot=''
```

Because comparisons with NaN are false, `objective_gap > tolerance` does not
quarantine the result. This can turn malformed evidence into an apparent
classical/quantum match.

Required repair: validate all required identities as non-empty and role-correct;
require finite objectives and a finite, non-negative tolerance; require every
cost component to be finite and non-negative; preserve all comparison lineage
(`candidate_set_id` and `baseline_revision` included) in the result. Invalid
evidence must return a dedicated fail-closed diagnostic, not `matched`.

### CR-004 — `.sqxa` manifest and payload may contradict each other

`compiler/staqex/sqxa.py:96-121` validates `manifest.format` and the hash of the
payload, but it does not validate manifest version, artifact kind, duplicated
source/semantic identities, execution policy, provenance, or target against
the payload. A file changed to manifest version `999`, kind `targeted`, and a
forged source identity still loaded as a portable artifact using the payload:

```text
portable sha256:src 999 targeted sha256:forged
```

The hash did not detect this because it covers only the payload. Consumers that
read `artifact.manifest` and consumers that read top-level artifact properties
can therefore make different trust decisions. `_contains_secret` additionally
uses key-name heuristics; it is a useful guard but cannot by itself prove the
contractual statement that secrets never enter artifacts.

Required repair: define one authoritative signed/hashed envelope, reject
unsupported versions, validate every duplicated manifest field against the
payload, validate portable/targeted schema requirements, and test tampering for
each duplicated field. Document secret scanning as defense-in-depth; the main
guarantee must come from typed allowlisted schema fields and Host-only secret
flow.

### CR-005 — semantic migration status and executable contracts disagree

The full suite exposes unresolved boundaries across symbolic-IR authority,
AST/DTO QASM retirement, interfer meaning, POVM rejection, and evaluator
authority. Representative failures include a non-explicit compile still
exposing `symbolic_ir`, QASM emission succeeding without canonical projection,
missing `povm_observation_rejections`, and an evaluator contract expecting a
stored canonical identity that is absent. Several source-language tests also
now fail on duplicate declaration or approximation-obligation diagnostics.

Some assertions may be stale after later accepted design decisions, but that
is itself a contract-governance defect: completed issue status, tests, and
current specification do not identify one executable truth. Re-read each
family's current canonical spec before changing code or tests, and record one
of: implementation regression, superseded test with replacement evidence, or
still-open feature.

### CR-006 — core modules are difficult to review safely

The Python implementation is about 49,644 lines. The evaluator is 6,926 lines,
the typechecker 4,668, parser 3,669, scientific semantic IR 2,008, and QASM
lowering 1,520. These files combine dispatch, validation, compatibility,
diagnostic selection, and execution/lowering policy. Several fallback paths
catch broad exception groups and silently continue, for example evaluator
scalar capture and static operator resolution.

No broad catch is automatically wrong, and several are intentional capability
probes. The risk is that fallback versus rejection is encoded locally and is
hard to audit against the atomic-failure contract. Add named result types or
diagnostics around each semantic fallback, then extract cohesive families only
with characterization tests. Avoid a large mechanical rewrite.

### CR-007 — environment and quality verification are not reproducible

No `pyproject.toml`, requirements file, lockfile, `setup.cfg`, `tox.ini`, or
`pytest.ini` was found. CI installs only the latest `pip` and `pytest`; optional
provider dependencies are discovered at runtime. CI also does not run lint,
type checking, coverage thresholds, packaging installation, or dependency
vulnerability/license checks.

Required repair: define supported Python versions and a minimal installable
project manifest, separate core/dev/provider extras, pin CI through a reviewed
lock or constraints strategy, and add gates progressively. Start with import/
package installation and deterministic lint/type scopes rather than attempting
to type-check the entire legacy codebase at once.

### CR-008 — current documentation contains a stale authorization statement

`docs/specs/staqex-multi-provider-qpu-execution-contract.md` calls the `.sqxa`
design a proposal whose implementation is not authorized, while LISS-0542 and
WP-0159 record Phase 3 final review complete. The provider pilot remains gated,
but the provider-neutral artifact implementation is no longer merely proposed.
Update the sentence without implying live-provider approval.

## Architecture and quality observations

- Positive: AWS Braket SDK access remains in the Host adapter, and Kernel
  source does not import provider SDKs. The `.sqx` → semantic meaning → QASM /
  `.sqxa` → Host adapter boundary is visible.
- Positive: the loader checks target route and capability expiry before
  constructing a provider, and local tests cover malformed and timezone-naive
  expiry values.
- Positive: Spec Verification is fast, deterministic, and fully green at
  161/161.
- Caution: a green spec-text verifier is not a substitute for executable
  regression because the two suites currently disagree.
- Caution: completion records are rich but duplicated across issue/work-plan
  prose. Machine-readable lifecycle state is needed for test gating.

## Full-suite failure inventory

The 19 failures group as follows:

- Language/runtime expression behavior (8): bounded `evolve until`, empty
  binder identities (3), Dirac identifier sugar (2), operator algebra, and
  pipeline currying.
- Semantic authority and meaning preservation (7): LISS-0476, LISS-0477,
  LISS-0478 (2), LISS-0485, and LISS-0486 (2).
- Observation diagnostic compatibility (1): tomography reports
  `OBSERVATION_CAPABILITY_UNSUPPORTED` while the test expects
  `OBSERVATION_UNSUPPORTED`.
- S02 assay DTO contract (3): tests expect attribute-based records while the
  implementation returns mappings.

This inventory is triage evidence, not a decision that production code is
wrong in every case.

## Recommended repair order

1. **WP-A / P0 — Restore regression authority.** Introduce active-Red metadata,
   reconcile all 19 failures, and make completed contracts blocking in CI.
2. **WP-B / P0 — Repair S02 snapshot immutability.** Settle the D01 DTO contract,
   fix constructor validation/freezing, and add aliasing/mutation tests.
3. **WP-C / P1 — Harden scientific comparison evidence.** Add finite numeric,
   non-negative cost, required-lineage, and result-lineage contracts.
4. **WP-D / P1 — Harden `.sqxa` envelope validation.** Make manifest/payload
   identity coherent and versioned before wider provider use.
5. **WP-E / P1 — Close semantic migration contradictions.** Resolve each
   completed LISS test against its canonical spec and update status atomically.
6. **WP-F / P2 — Establish reproducible packaging and quality gates.** Add
   project metadata, dependency groups, and staged lint/type/security checks.
7. **WP-G / P2 — Decompose semantic hot spots.** Characterize then extract
   evaluator/typechecker/parser/QASM responsibilities in bounded units.
8. **Documentation sync.** Correct stale `.sqxa` authorization language as part
   of WP-D, without authorizing provider pilot or live QPU execution.

Each work plan should retain the repository's Phase 0 → Red → Green → Refactor
gates. WP-A must land first because all later completion claims depend on a
trustworthy regression gate.

## Review disposition

- Apply: CR-001 through CR-008 in the order above.
- Already closed with evidence: provider SDK isolation, target-route/expiry
  preflight, and Spec Verification integrity.
- Out of scope: actual provider credentials, network submission, and real-QPU
  behavior; these were not exercised and must not be inferred from local tests.
- Blockers: CR-001 and CR-002 block a clean-regression claim; CR-003 and CR-004
  block a fail-closed scientific/deployable-artifact claim.

## Evidence links

- Representative trace:
  [2026-09-11 source-code-review trace](../traces/2026-09-11-source-code-review.md)
- CI definition: [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)
- S02 assay implementation:
  [`compiler/staqex/s02_assay_profile.py`](../../../compiler/staqex/s02_assay_profile.py)
- S02 comparison implementation:
  [`compiler/staqex/s02_quantum_baseline_comparison.py`](../../../compiler/staqex/s02_quantum_baseline_comparison.py)
- `.sqxa` implementation:
  [`compiler/staqex/sqxa.py`](../../../compiler/staqex/sqxa.py)
