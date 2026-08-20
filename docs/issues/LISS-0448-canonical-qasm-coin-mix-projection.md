# LISS-0448: Canonical QASM Projection for Coin/Mix Programs

| Field | Value |
|---|---|
| Status | **open** |
| Phase | **phase-0-design** |
| Type / priority | feature follow-up / P1 |
| Initial size | M |
| Current size | M |
| Owner | Staqex compiler maintainers |
| Parent / related | Related to [LISS-0446](LISS-0446-qasm-public-entry-canonical-sharing.md) and [LISS-0447](LISS-0447-residual-semantic-consumer-reconciliation.md) |
| WorkPlan | [WP-0111](../work-plans/WP-0111-canonical-qasm-coin-mix-projection.md) |
| GitHub | Not created |
| Branch | `codex/liss-0438-residual-reconciliation` (design intake only) |

## Problem

The current canonical QASM boundary intentionally rejects `Coin`/`Mix` source
programs when their meaning is not represented by the Scientific Semantic IR
QPU projection. Existing SV-10/SV-11 conformance cases still expect the retired
ordinary AST fallback to emit Bell-style OpenQASM. PR #557 records this as a
design-boundary CI failure rather than reintroducing an implicit fallback.

## Objective

Design and, after separate phase approval, implement a source-owned canonical
projection for the supported `Coin`/`Mix` subset, or formally revise the
conformance contract to classify that subset as an explicit capability
rejection. The result must preserve the same blackboard meaning and must not
silently finiteize or invent a QPU interpretation.

## Acceptance direction

- The chosen direction is recorded in an accepted Spec/ADR decision before
  production implementation.
- If supported, `Coin`/`Mix` semantics are represented in the canonical
  Scientific Semantic IR and projected to QPU IR without an AST fallback.
- If unsupported, SV-10/SV-11 assert the explicit capability rejection and the
  complete empty artifact envelope.
- No QASM, gate, allocation, or partial program is produced on rejection.
- The local spec verification gate is green with no hidden compatibility path.

## Exclusions and decision points

- No provider SDK, live QPU submission, credentials, or network integration.
- No S02 numerical migration, solver work, or syntax redesign.
- Do not change ADR 0211 or the explicit Realize/Limit policy implicitly.
- Architecture/User judgment is required if supporting `Coin`/`Mix` changes the
  canonical IR model, QPU capability boundary, or existing ADR contract.

## Current evidence

- PR [#557](https://github.com/nn0cl/staqex/pull/557) has the canonical
  consumer migration and deliberately retains fail-closed QASM behavior.
- CI Spec verification reports 155/161; the six failures are SV-10/SV-11
  `Coin`/`Mix` expectations.
- Repository-local `python3 tests/spec_verification/run_all.py` reproduces the
  same six failures.

## AI planning record

- Date: 2026-08-20
- Environment: Codex desktop, repository-local analysis
- Size: M; multiple QASM/IR/spec tests with one bounded semantic decision
- Route: local source inspection, deterministic spec verification, independent
  review before implementation
- Estimate: N/A until the canonical representation decision is accepted
- Confidence: medium; the current rejection is clear, but the correct
  `Coin`/`Mix` QPU meaning requires architecture review
