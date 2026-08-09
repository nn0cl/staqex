# LISS-0392: AWS Braket Host adapter (QpuSubmitPort / QpuJobPort)

## Metadata

- Local issue ID: LISS-0392
- Status/phase: **Green/Refactor complete** (2026-08-10) — proceeding
  without a mid-work pause per Adjudicator "続ける" (2026-08-10),
  following ADR 0202 Accept; awaiting Completion approval
- Type: Feature Path (Host adapter — new external optional dependency;
  no Kernel change)
- Priority: P2
- Initial planning size: `L`
- Owner / agent: Claude Code
- Program: [ADR 0202](../architecture/adr/0202-aws-braket-provider-adapter.md)
  (Accepted 2026-08-10, PR [#498](https://github.com/nn0cl/staqex/pull/498))
- Parent: ADR 0202
- Depends on: `compiler/staqex/qpu_submit.py` (shipped) / `credentials.py`
  (shipped) — reused unchanged.
- Blocks: none
- Branch: `feature/liss-0392-aws-braket-adapter`
- GitHub Issue / PR: none yet

## Intent

Implement the Host adapter ADR 0202 selected: `QpuSubmitPort`/`QpuJobPort`
backed by AWS Braket, with a real (lazy-imported, version-gated) client
wrapper and full test coverage against an injected fake client — no real
network call, no real credentials, ever, from this agent or from CI.

## Dependency Adoption Checklist — resolved (this Issue's Plan)

Per ADR 0202 Decision 4's **Open** items, resolved via research before
Green:

- **Security posture:** **CVE-2026-9291** (CVSS 7.1, High) — insecure
  deserialization via `pickle.loads()` in job-results processing
  (`job.result()` / `load_job_result()` / `load_job_checkpoint()`).
  Affects `amazon-braket-sdk` >= 1.10.0, < 1.117.0. **Fixed in 1.117.0.**
  Source: [GitHub Security Advisory GHSA-g697-2xrc-gc46](https://github.com/amazon-braket/amazon-braket-sdk-python/security/advisories/GHSA-g697-2xrc-gc46).
  This directly affects the exact method (`result()`) this adapter's
  `QpuJobPort.result` implementation wraps — the real client wrapper
  **must** runtime-check the installed version and refuse (fail closed)
  below `1.117.0`, as defense in depth beyond the version pin alone.
- **Version pin:** `amazon-braket-sdk>=1.117.0,<2` (latest confirmed
  1.125.0, 2026-08-03, via PyPI). License Apache-2.0 (compatible — this
  repo is dual Apache/MIT licensed). Requires Python >=3.11 (this repo's
  environment already exceeds that).
- **No project dependency manifest exists yet** (no `pyproject.toml` /
  `requirements.txt` at repo root) — `amazon-braket-sdk` is therefore not
  "added" to anything by this Issue; it is documented as an **optional**
  runtime dependency the real client wrapper lazy-imports, with a clear
  actionable error if absent or too old. Installing it (or not) remains
  the user's own choice.
- **Minimal real-file test:** deliberately **not performed** by this
  agent (ADR 0202 Decision 3/5) — all tests exercise a fake client.
- **Boundary fit:** confirmed — new module under
  `compiler/staqex/adapters/`, outside the Kernel package; Kernel code
  never imports this module or `amazon-braket-sdk`.

## Explicitly out of scope

- Any real submission, by this agent, ever (ADR 0202 Decision 5, standing).
- Wiring this adapter into `JobResult`/`dynamic_trace`
  (`physical_execution_claimed` semantics) or `submit_source` — this
  Issue ships the adapter as a standalone, injectable Host component;
  end-to-end wiring is future follow-up.
- `QpuArtifact` → Braket-native circuit object translation beyond passing
  the OpenQASM3 string through — Braket's own `Circuit.from_ir`-equivalent
  parsing is the real SDK's responsibility, not reimplemented here.
- Result-schema deep mapping beyond a provider-neutral passthrough
  `Mapping[str, Any]` (matches `QpuJobPort.result`'s existing shape).

## Plan-locked decisions

1. **`BraketClientPort` Protocol** (minimal, adapter-owned): `create_task`,
   `task_state`, `task_result`, `cancel_task` — the smallest surface the
   adapter needs, not a full SDK re-export.
2. **`RealAwsBraketClient`**: checks the installed `amazon-braket-sdk`
   version via `importlib.metadata.version` (no heavy import needed for
   this check) **before** lazy-importing the SDK itself; refuses
   (`BraketDependencyError`) if absent or `< 1.117.0`, citing
   CVE-2026-9291 in the error message.
3. **`AwsBraketAdapter`** implements `QpuSubmitPort` + `QpuJobPort`,
   depends on an injected `BraketClientPort` + the existing
   `CredentialPort` (required credential names configurable, default
   `("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")`) — missing credentials
   fail closed with a `CREDENTIAL_MISSING`-shaped diagnostic, mirroring
   `CredentialGatedMockSubmit` exactly.
4. **Tests only use a `FakeBraketClient`** implementing `BraketClientPort`
   — no real network, no real credentials, no real package import
   required for the test suite to pass.

## AI planning record (size L)

- Status: Green/Refactor complete; awaiting Completion approval.
- Confidence: high for the adapter logic (mirrors `CredentialGatedMockSubmit`'s
  already-shipped, reviewed pattern); medium for the exact real-SDK
  method names in `RealAwsBraketClient` (`AwsDevice`, `AwsQuantumTask`,
  `.run`/`.state`/`.result`/`.cancel`) — written from public
  documentation knowledge, **not verified against a live import or
  execution** (this agent never imported the real SDK, per standing
  constraint). Isolated behind the lazy-import + version-gate boundary
  so a naming mismatch there cannot affect the tested (fake-client) path
  at all — only the real path, which is untested by design and requires
  the user's own verification before real use.

## Exit criteria

- [x] Plan drafted, proceeding per Adjudicator "続ける" direction
      (2026-08-10).
- [x] Dependency Adoption Checklist resolved via research (see table
      above): CVE-2026-9291 found (CVSS 7.1, fixed in 1.117.0), version
      pin `>=1.117.0,<2` recorded; no project manifest exists yet, so
      nothing was "added" — documented as an optional, lazy-imported
      dependency instead.
- [x] Phase 1 Red (2026-08-10):
      `tests/test_liss_0392_aws_braket_adapter_red.py` — all 5 tests
      failed for the stated reason (`ModuleNotFoundError`, the adapter
      module did not exist yet).
- [x] Phase 2 Green (2026-08-10): new
      `compiler/staqex/adapters/aws_braket.py` — `BraketClientPort`
      Protocol, `RealAwsBraketClient` (version-gated, lazy-imported,
      never touched by tests), `AwsBraketAdapter` (credential-gated,
      delegates to injected client). All 5 tests pass against
      `FakeBraketClient`; no test edited to force it. Confirmed
      `amazon-braket-sdk` is not installed in this environment and the
      test suite does not require it.
- [x] Phase 3 Refactor: reviewed the new files — clean, mirrors
      `CredentialGatedMockSubmit`'s shape; no changes needed.
- [x] Full regression sweep re-run: **1396 passed** (2026-08-10), up
      from 1391 by exactly the 5 new tests.
- [ ] Completion approval.
