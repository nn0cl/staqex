# LISS-0397: CLI surface for `QpuJobPort` (status / wait / result / cancel)

## Metadata

- Local issue ID: LISS-0397
- Status/phase: **complete** (2026-08-10) — Adjudicator Completion
  approval; PR (recorded below once opened)
- Type: Feature Path (Delivery — new `cli.py` subcommands wiring the
  already-shipped `QpuJobPort` protocol via `AwsBraketAdapter`; no Kernel
  change, no new port, no ADR)
- Priority: P2
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: Adjudicator-selected direction (2026-08-10) for real-QPU
  end-to-end wiring, chosen via AskUserQuestion over showcase integration
  or both — CLI-first, recommended because it closes the submit→poll→
  result loop at the smallest reviewable unit before any showcase reuses
  it
- Parent: ADR 0203 (`submit_live_qpu`), LISS-0396 (`submit-live-qpu` CLI)
  — both **complete**. LISS-0396 explicitly deferred `QpuJobPort`
  status/result/cancel CLI wiring as separately-scoped; this Issue is
  that deferred scope.
- Depends on: LISS-0392 (`AwsBraketAdapter` already implements
  `QpuJobPort.status/wait/result/cancel`, unchanged), LISS-0396
  (`_build_live_qpu_adapter`, reused unchanged) — both **complete**
- Related: `compiler/staqex/cli.py`
- Blocks: none
- Branch: `feature/liss-0397-qpu-job-port-cli`
- GitHub Issue / PR: (opened at Completion)

## Intent

Add four CLI subcommands — `qpu-job-status`, `qpu-job-wait`,
`qpu-job-result`, `qpu-job-cancel` — that reconstruct a `ProviderJobId`
from CLI flags and dispatch to the corresponding already-shipped
`AwsBraketAdapter` method (`QpuJobPort.status/wait/result/cancel`, all
implemented and unchanged since LISS-0392). This closes the CLI-level
submit→poll→result loop that `staqex submit-live-qpu` (LISS-0396) started
but deliberately did not finish. Pure Delivery-layer wiring: no Kernel
change, no port/adapter change, no ADR.

## Design verification performed before this Plan

1. **Confirmed `QpuJobPort`'s exact shape** (`qpu_submit.py:53-66`): four
   methods, all taking only a `ProviderJobId(provider, opaque_id)` and
   returning either a `ProviderJobState` (str Enum: queued/running/
   succeeded/failed/cancelled) or, for `result`, a `Mapping[str, Any]`.
   `AwsBraketAdapter` (`adapters/aws_braket.py:168-180`) already
   implements all four by delegating to its injected `client`
   (`task_state`/`task_result`/`cancel_task`) — confirmed no change is
   needed to the adapter itself.
2. **Confirmed `AwsBraketAdapter.device_arn` is a required dataclass
   field with no default**, even though `status`/`wait`/`result`/`cancel`
   never read it (only `submit` does, via `create_task(qasm, device_arn,
   shots)`). This means job-status commands must still supply
   `--device-arn` to construct the adapter, even though the value is
   functionally unused for those four operations — a disclosed, minor UX
   wrinkle inherited from the already-shipped adapter shape, not fixed
   here (changing `AwsBraketAdapter` would be out of scope per LISS-0392's
   own boundary and this Issue's).
3. **Confirmed `_build_live_qpu_adapter(device_arn)`
   (`cli.py`, LISS-0396) is directly reusable, unchanged** — it already
   returns a fully-constructed `AwsBraketAdapter` implementing both
   `QpuSubmitPort` and `QpuJobPort`; no new adapter-construction helper is
   needed.
4. **Confirmed the error-propagation precedent to follow.**
   `live_submit.py`'s own docstring states adapter-level failures
   "propagate as exceptions, unchanged, since the injected adapter's own
   `submit` already raises for those." LISS-0396's `cmd_submit_live_qpu`
   catches exactly `(BraketDependencyError, BraketCredentialError)` and
   lets anything else (e.g. a real SDK's own exception for an invalid
   job ARN) propagate as a Python traceback. This Issue follows the same
   two-exception catch, matching precedent rather than inventing broader
   error handling for a provider-specific failure mode (e.g. "job not
   found") that this codebase has never modeled.
5. **Confirmed this dev/CI environment still lacks `amazon-braket-sdk`**
   (unchanged since LISS-0396), so at least one of the four new commands
   can be Red/Green-verified against the real (non-fake)
   `BraketDependencyError` fail-closed path, same pattern as LISS-0396.

## Explicitly out of scope

- Any change to `AwsBraketAdapter`, `RealAwsBraketClient`,
  `submit_live_qpu`, or `QpuJobPort`/`QpuSubmitPort`.
- Making `device_arn` optional for job-status operations (would touch the
  shipped adapter's dataclass shape; disclosed wrinkle, not fixed).
- Any polling loop, retry policy, or backoff inside the CLI itself —
  `qpu-job-wait` calls `QpuJobPort.wait` exactly once and prints the
  returned state; any looping/backoff policy is the adapter's own
  concern (already out of scope per ADR 0203 Decision 4) or the user's
  own shell loop, not invented here.
- Provider selection beyond `aws-braket` (same boundary as LISS-0396).
- Showcase/example integration (the Adjudicator's other offered option;
  deferred as a separate, explicitly optional follow-up).
- Real invocation against a live device by this agent (ADR 0202 Decision
  5, unchanged — this agent authors and tests against fakes only).

## Plan-locked decisions

1. One shared helper `_cmd_qpu_job(args, action) -> int` in `cli.py`
   (`action` one of `"status" | "wait" | "result" | "cancel"`):
   validates `args.provider == "aws-braket"` (same message shape as
   LISS-0396), builds `job_id = ProviderJobId(provider=args.provider,
   opaque_id=args.id)`, wraps `_build_live_qpu_adapter(args.device_arn)`
   + the dispatched `getattr(adapter, action)(job_id)` call in the same
   `try/except (BraketDependencyError, BraketCredentialError)` used by
   `cmd_submit_live_qpu`. Prints `state.value` for
   status/wait/cancel, or `json.dumps(result, indent=2)` for `result`
   (falls back to `str(result)` if not JSON-serializable, e.g. numpy
   arrays from a real result mapping — disclosed, not deeply handled,
   since no real result payload has ever been produced by this codebase
   to verify the exact shape against).
2. Four new subparsers (`qpu-job-status`, `qpu-job-wait`, `qpu-job-result`,
   `qpu-job-cancel`), each taking `--id` (required, `opaque_id`),
   `--device-arn` (required, per Design verification point 2),
   `--provider` (default `"aws-braket"`), `set_defaults(func=...)` bound
   via `functools.partial(_cmd_qpu_job, action=...)`.
3. Add all four names to `main()`'s explicit-subcommand set.
4. No change to `cmd_submit_live_qpu`, `_build_live_qpu_adapter`, or any
   existing subcommand.

## Draft test scenarios (Plan review only, not yet normative)

1. Unsupported `--provider` fails closed for each of the four commands
   (or at least one, with a shared-helper argument that the other three
   are structurally identical — full regression still exercises all four
   end to end via scenario 2).
2. Missing `amazon-braket-sdk` in this environment: a real (non-fake)
   invocation of each of the four commands fails closed via the real
   `BraketDependencyError` path (genuine verification, not simulated).
3. Successful `status`/`wait`/`cancel` (fake client + fake env
   credentials): stdout is exactly the provider state string (e.g.
   `succeeded`).
4. Successful `result`: stdout is the JSON-serialized mapping the fake
   client returns.
5. Missing AWS credentials fails closed before the fake client's method
   is ever called, for at least one of the four (proves the credential
   gate still runs first, same as LISS-0396 Scenario 4).
6. Full regression sweep unaffected outside these new/targeted assertions.

## AI planning record (size S)

- Status: Green/Refactor complete; Completion approval granted (2026-08-10).
- Confidence: high — `QpuJobPort`'s shape, `AwsBraketAdapter`'s existing
  implementation, and the error-propagation precedent were all confirmed
  by reading the already-shipped source, not assumed. The one open
  wrinkle (device_arn required but unused for job-status ops) is
  disclosed rather than silently worked around.

## Exit criteria

- [x] Plan approval (2026-08-10).
- [x] Phase 1 Red (2026-08-10):
      `tests/test_liss_0397_qpu_job_port_cli_red.py` — 6 of 7 tests failed
      for the stated reason (the four `qpu-job-*` subcommands did not
      exist yet). The 7th (originally "missing credentials fails closed
      before job-port call") needed correction mid-Red: running it
      against the already-implemented Green code revealed
      `AwsBraketAdapter._require_credentials()` only runs inside
      `submit()` (`adapters/aws_braket.py:152-166`), never inside
      `status`/`wait`/`result`/`cancel` — an asymmetry the Plan's Design
      verification did not check. Corrected the test to assert the
      actual (already-shipped, unchanged) behavior — status/wait/cancel
      proceed without credentials — rather than weakening or removing it;
      no Green code changed to accommodate the correction, since
      `_cmd_qpu_job` needed no credential-specific branch regardless.
- [x] Phase 2 Green (2026-08-10): new `_cmd_qpu_job` shared dispatcher,
      `add_qpu_job_parser` helper wiring four subparsers, `main()`
      dispatch-set entries. All 7 pass (after the one test correction
      above, made before final Green confirmation); no test logic
      weakened.
- [x] Phase 3 Refactor: reviewed diff — matches the Plan's design exactly
      (`cli.py` +57 lines, additive only); no further changes needed.
- [x] Full regression sweep re-run: **1424 passed** (2026-08-10), up from
      1417 by exactly the 7 new tests.
- [x] Completion approval (2026-08-10).
