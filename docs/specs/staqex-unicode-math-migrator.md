# Staqex Unicode math migrator (LISS-0069 Slice B historical)

> Superseded for canonical source output by [ADR 0191](../architecture/adr/0191-ascii-quantum-notation-and-lexical-boundary.md).
> Treat this document and its golden corpus as historical migration records;
> new source and formatter output must remain ASCII.

| Field | Value |
|---|---|
| Status | **Slice B complete** through Phase 3 Refactor (2026-07-28) |
| Authority | ADR 0106; [`staqex-unicode-math-source.md`](staqex-unicode-math-source.md); migration matrix M-P02–M-P04 |
| Depends on | LISS-0069 Slice A **complete** (dual-accept lexer/parser) |
| Last updated | 2026-07-28 |

This companion freezes the **Slice B** migrator contract. It does not authorize
Phase 1 Red until plan approval.

## 1. Goals

1. Deterministic rewrite of ASCII Dirac / tensor / adjoint spellings to the
   Unicode forms accepted by Slice A.
2. Golden corpus under `tests/fixtures/migration/` proving round-trip intent.
3. Comments and non-math tokens preserved (no silent reformat of unrelated code).
4. Dual-accept remains: migrator output must still parse; ASCII input remains Valid.

## 2. Rewrite rules (Normative for Slice B)

| ID | Input (ASCII) | Output (canonical) | Notes |
|---|---|---|---|
| R-KET | `\|label>` | `\|label⟩` | Same label payload; do not touch `\|>` |
| R-TENSOR | `*|*` | `⊗` | Exact three-character operator only |
| R-ADJ-SIMPLE | `adjoint(Primary)` | `Primary†` | Primary = IDENT / Pauli atom / parenthesized op-expr TBD in Red |
| R-BRA | — | — | **Out of Slice B** — no ASCII bra spelling to migrate yet |

### Explicit non-rewrites

- Pipeline `\|>` must never become a ket close.
- Nested / multi-arg `adjoint` forms may remain as `adjoint(...)` if Red cannot
  prove a safe postfix peel (document skipped cases in fixtures as `skip`).
- Pauli ASCII atoms `X`/`Y`/`Z`/`I` — **never** rewritten (M-P01).
- `state` sugar — **never** rewritten (M-P05).
- String/comment contents — **never** rewritten.

## 3. Library API (proposed)

```text
compiler/staqex/migrate_unicode_math.py

migrate_unicode_math_source(source: str) -> str
```

- Pure function; no I/O.
- UTF-8 str in / str out.
- Idempotent on already-canonical Unicode forms (second pass = no change).
- CLI (`staqex migrate`) is **Slice C** — see
  [`staqex-unicode-math-migrate-cli.md`](staqex-unicode-math-migrate-cli.md).

## 4. Golden corpus layout

```text
tests/fixtures/migration/v0.1/   # ASCII (or mixed) inputs
tests/fixtures/migration/v1/     # expected Unicode outputs (same basenames)
```

Minimum fixtures for Red:

| Basename | Covers |
|---|---|
| `ket_basic.staqex` | R-KET |
| `tensor_bind.staqex` | R-TENSOR |
| `adjoint_simple.staqex` | R-ADJ-SIMPLE |
| `pipeline_preserved.staqex` | `\|>` untouched beside kets |
| `comments_preserved.staqex` | `//` and inline comments unchanged |
| `idempotent_unicode.staqex` | already-Unicode input stable |

## 5. Acceptance envelopes (Slice B)

### EARS

When the migrator is given ASCII ket `\|0>`, it shall emit `\|0⟩` and shall not
alter surrounding whitespace except as required by the token rewrite.

When the migrator is given `*|*`, it shall emit `⊗`.

When the migrator is given `adjoint(X)` where `X` is a simple primary, it shall
emit `X†`.

When the migrator is given `x \|> y`, it shall leave the pipeline operator
unchanged.

### Gherkin

```gherkin
Feature: Unicode math migrator

  Scenario: Ket close migrates
    Given fixture "ket_basic.staqex" under v0.1
    When migrate_unicode_math_source runs
    Then the result equals the v1 golden
    And compile_source(result).ok is true

  Scenario: Pipeline is not a ket
    Given source containing both "|>" and "|0>"
    When migrate_unicode_math_source runs
    Then "|>" remains
    And "|0>" becomes "|0⟩"
```

## 6. Verification plan

- Phase 1 Red: failing tests that load goldens and call the missing API.
- Phase 2 Green: implement rewriter; all goldens match; dual-accept compile ok.
- After Green: SV 160/160 still PASS (examples not force-rewritten).
- Phase 3 Refactor: readability only.

## 7. Out of scope (Slice B)

- CLI entry point (Slice C)
- Formatter / CST emit (LISS-0072)
- Full NFC source normalization pass (may land as follow-up if not needed for
  token rewrite)
- Bra–ket `inner` sugar (A.1 / LISS-0073)
- Rewriting the entire `examples/` tree in-repo
