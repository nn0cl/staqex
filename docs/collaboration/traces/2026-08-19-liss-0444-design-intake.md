# LISS-0444 Architecture design intake trace

## [DESIGN CHECK]

- **Scope:** Create the reviewed design artifacts for a source-derived
  Scientific Semantic Core and explicitly request an implementation-reality
  audit from independent reviewers.
- **Artifacts inspected:** AST/parser/typecheck/HIR, Physics/Symbolic/Equation
  IR, Quantum Semantic IR, Algorithm Plan IR, evaluator, continuous lowering,
  LISS-0437–0443, language vision, ADR 0209–0210, open-work register, and the
  review perspectives ledger.
- **Finding:** Existing IR/DTO artifacts are not uniformly authoritative;
  `EquationNode` is caller-injected/string-based and Physics IR is a soft
  projection. The design therefore must not optimize for preserving those
  structures.
- **Decision recorded:** propose ADR 0211 and WP-0107 for one source-derived
  structural semantic authority, with explicit migration/replacement/retirement
  dispositions for competing paths.
- **Independent review lenses selected:** canonical authority and
  implementation reality; source-to-domain fidelity; architecture/boundary
  integrity; type/dimension closure; state/physics safety; realization
  honesty; migration safety; evidence hygiene; phase discipline.
- **Implementation status:** no implementation, Red tests, or phase transition
  authorized. Architecture approval is recorded; independent review remains
  required.
- **Approval update:** user approved the LISS-0444 / ADR 0211 architecture and
  design scope on 2026-08-19. This does not approve implementation, Phase 1
  Red, or any phase transition; independent design review is next.
- **Review request:** WP-0107 contains the exact reviewer request. Reviewers
  must verify parser reachability, structural retention, canonical ownership,
  consumer wiring, provenance, and maturity debt rather than accepting DTO
  existence as language support.

## Independent review outcome

- Iteration 1 accepted design-preserving corrections for structural invariants,
  projection conservation, simulator/`Realize` boundary, and the competing-path
  matrix requirement.
- Iteration 2 ran in fresh independent contexts and remained `NOT READY`:
  matrix/corpus/projection/fail-closed details are not yet populated, and two
  semantic decisions cannot be inferred safely from existing artifacts.
- Review terminal state: `ABORT` pending user/Architecture decision on (1) the
  exact/symbolic simulator result and non-finiteization contract, and (2) how
  static terminal `measure` relates to the existing dynamic-lane mid-circuit
  measurement model in the canonical IR.
- No implementation, Red tests, Phase 1 approval, or phase transition was
  performed. After those decisions, apply accepted documentation fixes and
  trigger a new independent review loop.

## Resume decision

- User approved both escalated boundaries on 2026-08-19.
- The decisions and concrete migration/corpus/artifact rules are recorded in
  ADR 0211, the Scientific Semantic Core Spec, WP-0107, and Review 02.
- A fresh independent review is now required; implementation and Phase 1 Red
  remain unapproved.

## Design review completion

- The resumed review loop completed as `COMPLETE` after fresh independent
  review. The design is internally coherent and no unresolved architecture
  decision remains.
- Phase 1 is only ready for a separate typed approval; it was not approved.
- Implementation, production migration, provider SDK/live QPU, and S02 work
  remain outside the completed review.
