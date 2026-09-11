# LISS-0520 Phase 2 Green trace

- Date: 2026-09-10 (Asia/Tokyo).
- Scope: Q01 minimum `.sqxa` writer/reader and provider-neutral Runtime
  loader.
- Approval: `Phase 2の.sqxa writer/readerとRuntime loaderの最小実装を承認`.
- Added `compiler/staqex/quantum_artifact.py` without changing the Red suite.
  The writer emits a canonical JSON artifact with a content hash; the reader
  validates schema and hash before exposing the payload; the loader accepts
  only `local-simulator` and rejects unsupported runtimes.
- AST, direct round-trip/tamper/runtime smoke checks, `git diff --check`, and
  document lifecycle checks passed. Local pytest is unavailable.
- Out of scope: provider SDK, live QPU, general QUBO automation, and circuit
  execution.
- Next gate: `LISS-0520 Phase 3 Refactor 承認`.
