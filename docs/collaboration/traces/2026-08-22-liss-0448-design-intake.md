# LISS-0448 Design Intake

## [DESIGN CHECK]

- **Scope and expected behavior:** resolve the six SV-10/SV-11 failures for
  `Coin`/`Mix` without restoring the retired AST fallback or silently
  replacing mixture/branch meaning with a unitary Bell circuit.
- **Specifications and files inspected:** LISS-0448, WP-0111, the proposed
  canonical QASM `Coin`/`Mix` Spec, ADR 0211, ADR 0212, the QPU capability
  rejection contract, Scientific Semantic IR, QASM projection/emitter,
  SV-10/SV-11 suites, and the PR #557 CI log.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** the
  source-derived `ScientificSemanticIR` remains the authority. `SemanticNode`
  carries ideal `Coin`, `WhenExpr`/`Mix`, branch children, state role, and
  provenance. `CanonicalQpuProjection` is a target projection only. No new
  port, provider adapter, or user-visible namespace/class is proposed.
- **Applicable constraints:** physicist-first source fidelity; mixture is not
  a unitary operation; no AST fallback; no hidden finiteization; explicit
  `Realize` remains the only finite transition; rejection must be atomic and
  preserve ideal meaning; provider SDK, live QPU, S02, solver, and syntax work
  remain excluded.
- **Decisions, assumptions, and unresolved ambiguities:**
  1. Recommended direction is explicit finite-target rejection for the
     current static OpenQASM path, using the existing
     `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` /
     `mixture_projection_unavailable` contract.
  2. The existing Scientific Semantic IR already structurally visits
     `Coin`, `WhenExpr`, `Mix`, and branch children; Phase 1 must prove the
     fields and provenance through source-derived evidence rather than adding
     a parallel DTO.
  3. The old ADR 0036 pedagogical Coin→H/when→CX example is inconsistent with
     the later mixture/unitary boundary. It should be treated as an
     informational documentation correction, not as authority for a lossy
     implementation. If the Adjudicator requires that historical example to
     remain normative, the work must ABORT for architecture resolution.
  4. No new ADR is recommended: the rejection direction follows ADR 0211 and
     ADR 0212. The proposed LISS-0448 Spec must be accepted before Phase 1.
- **Included and omitted AI context:** included the issue/WP/spec, ADR 0211/
  0212, canonical IR/QASM implementation, and six failing cases. Omitted
  provider SDKs, credentials, live execution, S02 corpus, solver code, and
  unrelated language features.
- **Task routing (model/assistant/tool):** deterministic `rg`/source
  inspection for authority and failure evidence; `.venv/bin/pytest` and the
  spec harness for verification; independent read-only review before Phase 1
  Red when explicitly requested.
- **Input/output evidence contract when AI output is involved:** any review
  must return only prioritized findings, evidence paths/lines, a READY or NOT
  READY verdict, and reusable review lenses; no hidden reasoning.
- **Independent review lenses selected and why:**
  - source-to-domain fidelity: prevent Coin/Mix→unitary substitution;
  - canonical authority and implementation reality: prove parser-reachable
    IR ownership rather than DTO-only support;
  - projection conservation and authority reachability: preserve branch
    children, role, and provenance;
  - realization/fail-closed behavior: reject finite QASM without artifacts;
  - migration/regression safety: replace six stale expectations without
    restoring fallback;
  - phase/approval discipline: keep Phase 0, Red, Green, and Refactor gates
    distinct.
- **Verification plan:** Phase 1 Red will add the fixed LISS-0448 fixture and
  focused semantic/projection/rejection tests only. The accepted Green slice
  must make those tests pass and update SV-10/SV-11 to the accepted rejection
  contract. Full `tests/spec_verification/run_all.py`, the related `.venv`
  suite, `py_compile`, and `git diff --check` are required before completion.

## Design result

The recommended design is **canonical ideal mixture meaning plus explicit
static-QASM capability rejection**. The old six tests are not evidence that
the compiler should emit H+CX: they are evidence that the conformance harness
still asserts the retired fallback. No production code or tests were changed
in this intake.

## Phase and approval state

- Current phase: **Phase 1 Red**.
- User approved Phase 1 Red on 2026-08-22.
- Phase 0 design direction: canonical ideal mixture meaning plus explicit
  static-QASM capability rejection.
- Independent reviews 01–03 returned NOT READY; all findings were accepted and
  corrected in scope. Review 04 returned READY and closed the independent
  review loop as `COMPLETE`.
- Phase 1 artifacts: `tests/fixtures/canonical_coin_mix/mixture_semantics.sqx`
  and `tests/test_liss_0448_coin_mix_semantic_red.py`.
- Red verification: focused pytest **3 failed as expected**; no production
  files were changed. Spec harness is **158/161**, with the three exact
  rejection-provenance assertions intentionally red; the six stale H+CX
  expectations were converted to the accepted rejection contract.
- `git diff --check` passed.
- Review records: `docs/collaboration/reviews/2026-08-22-liss-0448-phase1-red-design-review-01.md`
  through `...-04.md`.
- Excluded: provider SDK, live QPU, credentials/network, S02, solver, syntax,
  and implicit finiteization.

## Phase 2 Green execution

- User approval: `承認する`, 2026-08-23.
- Scope: minimum production implementation only; reviewed tests were not
  changed during Green.
- Implementation: `Coin` is represented as a source-owned coin preparation;
  `WhenExpr` is represented on the quantum lane as a mixture relation; the
  canonical QPU projection rejects `WhenExpr` with the exact code
  `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` and reason
  `mixture_projection_unavailable` before target artifacts are emitted.
- Verification: focused and related semantic/QASM boundary tests **73 passed**;
  full spec verification **161/161 passed (100%)**; repository Python
  compilation and `git diff --check` passed.
- Phase 3 refactor and independent Green review are not approved.
