# LISS-0393: `submit_live_qpu` Host entrypoint

## Metadata

- Local issue ID: LISS-0393
- Status/phase: **complete** (2026-08-10) — Adjudicator Completion
  approval; PR [#501](https://github.com/nn0cl/staqex/pull/501)
- Type: Feature Path (Host orchestration — no Kernel change, no new
  external dependency, no real submission)
- Priority: P2
- Initial planning size: `M`
- Owner / agent: Claude Code
- Program: [ADR 0203](../architecture/adr/0203-live-qpu-submit-entrypoint.md)
  (Accepted 2026-08-10, PR [#500](https://github.com/nn0cl/staqex/pull/500))
- Parent: ADR 0203
- Depends on: `qpu_submit.py` (shipped); `backend/qasm/emitter.py` (shipped);
  `backend/qasm/dynamic_emitter.py` (LISS-0391, complete);
  `adapters/aws_braket.py` (LISS-0392, complete, used only via its
  `BraketClientPort`-fake test double here — never the real client)
- Blocks: none
- Branch: `feature/liss-0393-live-qpu-submit-entrypoint`
- GitHub Issue / PR: [#501](https://github.com/nn0cl/staqex/pull/501)

## Intent

Implement the new, separate Host entrypoint ADR 0203 defined: compile
source, emit QASM3 (Static or Dynamic-lane, auto-selected), submit
through an injected `QpuSubmitPort`, return `ProviderJobId` immediately
— never `Job`/`JobResult`.

## Explicitly out of scope

- Any real submission, by this agent, ever (ADR 0202 Decision 5, standing).
- Any change to `submit_source`/`submit_path` (ADR 0203 Decision 1).
- CLI/REPL surface (ADR 0203 §4, optional follow-up).
- Polling/retry/backoff policy (`QpuJobPort`, unaffected).

## Plan-locked decisions

1. **New module** `compiler/staqex/live_submit.py` — keeps this
   orchestration out of the already-large `host.py`, and out of the
   Kernel proper (imports `QpuSubmitPort`/`QpuArtifact`/etc. from
   `qpu_submit.py`, both QASM emitters, `pipeline.compile_source`).
2. **Signature:**
   `submit_live_qpu(source, *, adapter, execution_settings=None,
   idempotency_key=None, target_profile="live-qpu") ->
   tuple[ProviderJobId | None, tuple[dict, ...]]` — mirrors
   `prepare_parametric_qasm`'s existing `(payload | None, diagnostics)`
   shape for compile/emission failures (consistent with this codebase's
   established pattern), rather than raising for that class of failure.
   Adapter-level failures (e.g. `BraketCredentialError`) continue to
   propagate as exceptions, unchanged, since `AwsBraketAdapter.submit`
   already raises for those and this entrypoint does not swallow them.
3. **Dynamic-vs-Static QASM selection:** automatic — if the compiled
   unit contains a `dynamic qpu` block, use `emit_dynamic_qpu_qasm3`
   (LISS-0391); otherwise use `QASM3Emitter().emit_unit` (existing
   Static path). No caller flag needed for this Issue's scope.
4. **`content_hash`:** SHA-256 hex digest of the emitted QASM text —
   no existing convention found in the codebase (confirmed by grep); a
   straightforward, honest choice for an audit/idempotency field, not a
   security boundary.
5. **Tests use only a fake `QpuSubmitPort`** — no real network, no real
   credentials, no real `amazon-braket-sdk` import (mirrors LISS-0392).

## Acceptance reference

No single existing spec file owns `qpu_submit.py`'s Host surface;
recorded here and in `docs/architecture/open-work-register.md` instead of
a new spec file for this scope.

## Exit criteria

- [x] Plan drafted, proceeding per Adjudicator "続けて" (2026-08-10).
- [x] Phase 1 Red (2026-08-10):
      `tests/test_liss_0393_live_qpu_submit_entrypoint_red.py` — 5 of 6
      tests failed for the stated reason (`ModuleNotFoundError`); the
      6th (`test_submit_source_is_unaffected`) passed immediately,
      confirming the regression guard had nothing to regress against yet.
- [x] Phase 2 Green (2026-08-10): new `compiler/staqex/live_submit.py`
      (`submit_live_qpu`) — compiles source, auto-selects Static
      (`QASM3Emitter`) vs. Dynamic-lane (`emit_dynamic_qpu_qasm3`) QASM
      emission by unit shape, builds `QpuArtifact`/`QpuSubmitRequest`
      (SHA-256 `content_hash`), delegates to the injected
      `QpuSubmitPort`. All 6 tests pass; no test edited to force it.
      Confirmed `compiler/staqex/host.py` has zero diff (`submit_source`/
      `submit_path` byte-for-byte unaffected, per ADR 0203 Decision 1).
- [x] Phase 3 Refactor: reviewed the new file — clean, no changes needed.
- [x] Full regression sweep re-run: **1402 passed** (2026-08-10), up from
      1396 by exactly the 6 new tests.
- [x] Completion approval (2026-08-10); PR [#501](https://github.com/nn0cl/staqex/pull/501).
