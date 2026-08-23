# LISS-0448 CI Boundary Split Trace

## Intake

- Trigger: PR #557 CI failure review after browser-created Draft PR.
- Scope: six SV-10/SV-11 failures involving `Coin`/`Mix` QASM expectations.
- Approval: user approved separating the conflict into a new Issue/Phase;
  documentation/design intake only.
- Excluded: implementation, ADR acceptance, merge, provider SDK, live QPU,
  S02 numerical migration, and solver work.

## Evidence

- PR: https://github.com/nn0cl/staqex/pull/557
- CI run: https://github.com/nn0cl/staqex/actions/runs/32362042094
- Spec verification: 155/161; SV-10 and SV-11 six cases fail because the
  current canonical entry returns `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE`
  instead of using the retired AST fallback.
- Local reproduction: `python3 tests/spec_verification/run_all.py` produces
  the same six failures.

## Disposition

The failure is accepted as a design-boundary conflict, not treated as a reason
to restore hidden AST lowering. A new Issue/Spec/WP records the choice between
canonical `Coin`/`Mix` projection and an explicit unsupported-capability
contract. No production correction is applied in this trace.

## Next condition

Independent design review and an accepted Option A/B decision are required
before Phase 1 Red or implementation begins. PR #557 remains Draft and is not
merge-ready while its CI is red.
