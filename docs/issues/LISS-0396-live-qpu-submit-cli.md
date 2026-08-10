# LISS-0396: CLI surface for `submit_live_qpu` (`staqex submit-live-qpu`)

## Metadata

- Local issue ID: LISS-0396
- Status/phase: Green/Refactor complete (2026-08-10); awaiting Completion
  approval
- Type: Feature Path (Delivery — new `cli.py` subcommand wiring the
  already-shipped `submit_live_qpu` UseCase entrypoint; no Kernel change,
  no new port, no ADR)
- Priority: P2
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: ADR 0203's own named optional follow-up ("Wiring a CLI/REPL
  command for this entrypoint"); Adjudicator selected this direction
  explicitly (2026-08-10) after LISS-0395 completion, from an
  AskUserQuestion offering it alongside "stop here" and other options
- Parent: ADR 0202 (AWS Braket adapter) / ADR 0203 (`submit_live_qpu`
  entrypoint) — both **Accepted**, both unchanged by this Issue
- Depends on: LISS-0392 (`AwsBraketAdapter`, `RealAwsBraketClient`),
  LISS-0393 (`submit_live_qpu`), LISS-0194 (`CredentialPort` /
  `EnvCredentialAdapter`) — all **complete**
- Related: `compiler/staqex/cli.py`
- Blocks: none
- Branch: `feature/liss-0396-live-qpu-submit-cli`
- GitHub Issue / PR: (opened at Completion)

## Intent

Wire a new `staqex submit-live-qpu` subcommand that constructs a real
`AwsBraketAdapter` (credentials from `EnvCredentialAdapter`, i.e. the
process environment) and calls the already-shipped `submit_live_qpu`
entrypoint, printing the returned `ProviderJobId` on success. This is pure
Delivery-layer wiring: no new port, no change to `submit_live_qpu`,
`AwsBraketAdapter`, or `RealAwsBraketClient`. Status/result/cancel polling
(`QpuJobPort`) is **not** wired by this Issue — ADR 0203 named only "a CLI
command for this entrypoint" (the submit entrypoint specifically), and a
full job-lifecycle CLI is a separably-scoped, larger surface.

## Design verification performed before this Plan

1. **Confirmed `submit_live_qpu`'s exact signature and behavior**
   (`live_submit.py`): `(source, *, adapter, execution_settings=None,
   idempotency_key=None, target_profile="live-qpu") -> (ProviderJobId |
   None, diagnostics)`. Compile/QASM-emission failure returns `(None,
   diagnostics)` — mirrors `host.prepare_parametric_qasm`'s existing
   shape, matching the CLI's existing `_print_diags` convention used by
   every other `cmd_*` function. Adapter-level failures (missing
   credentials, missing/vulnerable SDK) propagate as exceptions from
   `adapter.submit(...)`, not as diagnostics.
2. **Confirmed `AwsBraketAdapter`'s credential check timing**
   (`adapters/aws_braket.py:152-166`): `_require_credentials()` runs
   inside `submit()`, not `__init__` — so a missing-credential failure
   only surfaces once `submit_live_qpu` actually reaches
   `adapter.submit(request)`, i.e. **after** compile and QASM emission
   already succeeded. The CLI command must therefore wrap the whole
   `_build_live_qpu_adapter(...)` + `submit_live_qpu(...)` sequence in one
   `try/except (BraketDependencyError, BraketCredentialError)`, not just
   adapter construction.
3. **Confirmed `RealAwsBraketClient.__init__`'s version gate is safe to
   call unconditionally** (`adapters/aws_braket.py:90-108`): it only reads
   installed package metadata (`importlib.metadata.version`) before
   raising `BraketDependencyError` when the SDK is absent or below
   1.117.0 (CVE-2026-9291) — no network call, no real SDK import, on the
   failure path. Confirmed this dev/CI environment does **not** have
   `amazon-braket-sdk` installed, so `staqex submit-live-qpu` run here
   deterministically exercises the real (non-fake) `BraketDependencyError`
   path — a genuine, not simulated, Red/Green test of "fails closed when
   the SDK is missing."
4. **Confirmed the credentials source**: `EnvCredentialAdapter()` (no
   args) reads `os.environ` directly (`credentials.py:24-33`, already
   shipped LISS-0194) — the CLI needs no new port or adapter, only to
   construct this existing class.
5. **Confirmed this Issue does not touch the standing autonomy
   constraint.** ADR 0202 Decision 5 / CLAUDE.md forbid **this agent**
   from autonomously invoking a real (non-mock) submission. A CLI
   subcommand is invoked by the human Adjudicator directly in their own
   terminal with their own AWS credentials already in their own
   environment — this agent building the wiring is authorship, not
   invocation; this agent will not run `staqex submit-live-qpu` against a
   real device in this session, matching every prior AWS Braket Issue in
   this lineage (LISS-0392/0393's own test suites never import the real
   SDK either).

## Explicitly out of scope

- **`QpuJobPort` status/wait/result/cancel CLI wiring** (a full
  job-lifecycle surface) — ADR 0203 named only the submit entrypoint;
  status polling is a separably-scoped, larger Issue if wanted later.
- **REPL integration** (`:submit-live-qpu` meta-command). A REPL is
  optimized for fast, throwaway local iteration against the CPU
  simulator; a command that can incur real cost on real hardware fits a
  single explicit CLI invocation (with a file or `-e` source spelled out
  up front) better than a REPL buffer someone might submit by habit.
  Deferred as a separate, explicitly optional future Issue if the
  Adjudicator wants it — not silently folded in here.
- **Cost/budget guardrails, shot-count caps, or a blocking confirmation
  prompt before submit.** ADR 0203 Decision 4 already places
  cost/budget guardrails as "the user's own responsibility, per ADR
  0202" — this Issue adds a one-line stderr notice before submitting
  (see Plan-locked decisions) but does not invent enforcement not asked
  for.
- **Provider selection beyond AWS Braket.** `--provider` is accepted for
  forward-compatible spelling but only `aws-braket` is implemented;
  anything else fails closed with a clear message. No provider registry
  is built for a single provider.
- Any change to `submit_live_qpu`, `AwsBraketAdapter`,
  `RealAwsBraketClient`, or `EnvCredentialAdapter`.

## Plan-locked decisions

1. New `cmd_submit_live_qpu(args) -> int` in `cli.py`:
   - Validates `args.provider == "aws-braket"`; anything else prints a
     clear stderr message and returns 1 without constructing anything.
   - Loads `source` via the existing `_load_source(args)` helper (file or
     `-e`, already shared by other commands).
   - Builds `execution_settings = {"shots": args.shots}` only when
     `--shots` was passed (omitted otherwise, so `AwsBraketAdapter`'s own
     `default_shots=100` applies — no duplicated constant in the CLI).
   - Prints one stderr notice ("submitting to AWS Braket device `<arn>`
     — this may incur real cost on real hardware") before calling
     `submit_live_qpu`.
   - Wraps adapter construction (`_build_live_qpu_adapter`, a small new
     helper: `AwsBraketAdapter(client=RealAwsBraketClient(),
     device_arn=args.device_arn, credentials=EnvCredentialAdapter())`)
     and the `submit_live_qpu(...)` call together in one
     `try/except (BraketDependencyError, BraketCredentialError) as exc`
     → print `f"submit-live-qpu: {exc}"` to stderr, return 1.
   - On `(None, diagnostics)` from `submit_live_qpu` (compile/QASM
     failure): `_print_diags(list(diagnostics))`, return 1.
   - On success: `print(f"provider={job_id.provider}
     id={job_id.opaque_id}")` to stdout, return 0.
2. New `argparse` subparser `submit-live-qpu`: reuses `add_src` (file /
   `-e` / `--seed` — `--seed` unused by this command but kept for
   `add_src` reuse consistency with every other subcommand; harmless no-op
   here), plus `--device-arn` (required), `--shots` (`int`, optional,
   default `None`), `--provider` (default `"aws-braket"`).
3. Add `"submit-live-qpu"` to `main()`'s explicit-subcommand set so a bare
   invocation isn't misrouted to the implicit `run` command.
4. No change to any other `cmd_*` function, port, or adapter.

## Draft test scenarios (Plan review only, not yet normative)

1. Unsupported `--provider` value fails closed with a clear message;
   exit code 1.
2. This dev/CI environment lacks `amazon-braket-sdk` — a real (non-fake)
   `staqex submit-live-qpu` invocation with valid source and a syntactic
   `--device-arn` fails closed via the real `BraketDependencyError` path,
   citing the CVE and the minimum version, exit code 1. (Genuine
   verification of the fail-closed behavior, not simulated.)
3. Successful submission (fake `BraketClientPort` + fake env credentials
   injected via monkeypatching `RealAwsBraketClient`/`EnvCredentialAdapter`
   at the `cli` module boundary): stdout is exactly
   `provider=aws-braket id=<opaque_id>`, exit code 0.
4. Missing AWS credentials (fake client installed, but env lacks
   `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`): fails closed with the
   existing `BraketCredentialError` message surfaced through the CLI;
   the fake client's `create_task` is never called (proves the credential
   gate runs before any submission attempt).
5. A source with a hard compile diagnostic (e.g. a `RETIRED_KEYWORD`)
   prints diagnostics via the existing `_print_diags` convention and
   exits 1, without a `provider=...` line ever being printed.
6. Full regression sweep unaffected outside these new/targeted assertions.

## AI planning record (size S)

- Status: Green/Refactor complete; awaiting Completion approval.
- Confidence: high — every behavior this Issue depends on
  (`submit_live_qpu`'s return shape, `AwsBraketAdapter`'s credential-check
  timing, `RealAwsBraketClient`'s version-gate safety, this environment's
  actual lack of the real SDK) was confirmed by reading the shipped source
  directly, not assumed.

## Exit criteria

- [x] Plan approval (2026-08-10).
- [x] Phase 1 Red (2026-08-10):
      `tests/test_liss_0396_live_qpu_submit_cli_red.py` — 4 of 5 tests
      failed for the stated reason (`submit-live-qpu` subcommand did not
      exist yet: argparse rejected it with exit code 2, or the
      `RealAwsBraketClient` patch target did not exist on `cli`); the 5th
      (hard compile diagnostic) needed its fixture corrected mid-Red —
      `"???"` turned out to still produce a non-`None` `compiled.unit`
      (`main=None`, lex errors only), so it fell through to a successful
      (fake) submission instead of the diagnostics path. Replaced with an
      unterminated block (`PARSE_ERROR`, confirmed `compiled.unit is
      None`) before writing any Green code — not a design misalignment,
      a test-fixture correction caught by running Red first.
- [x] Phase 2 Green (2026-08-10): new `cmd_submit_live_qpu`,
      `_build_live_qpu_adapter`, `submit-live-qpu` subparser, and
      `main()` dispatch-set entry. All 5 pass; no test logic edited (only
      the one fixture source string, before Green, per above).
- [x] Phase 3 Refactor: reviewed diff — matches the Plan's design exactly
      (`cli.py` +75 lines, additive only); no further changes needed.
- [x] Full regression sweep re-run: **1417 passed** (2026-08-10), up from
      1412 by exactly the 5 new tests.
- [ ] Completion approval.
