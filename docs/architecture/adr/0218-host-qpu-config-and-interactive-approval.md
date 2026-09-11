# ADR 0218: Host QPU configuration and interactive submission approval

## Status

**Accepted** (2026-09-10) — user-directed Host execution policy.

## Decision

1. Live AWS Braket CLI execution reads non-secret runtime settings from a TOML
   file, by default `$XDG_CONFIG_HOME/staqex/qpu.toml` or
   `~/.config/staqex/qpu.toml`. `--config` and explicit CLI values override
   the default path and config values.
2. The file may contain provider, device ARN, shots, and a positive declared
   cost ceiling. It must not contain AWS credentials or approval prose.
3. Credentials continue to come from the Host environment and AWS standard
   credential chain through `CredentialPort`.
4. Immediately before the provider adapter is constructed or submission is
   attempted, the CLI displays the target, shots, and cost ceiling and asks
   for `y`/`yes`. Any other response, including EOF, cancels without a
   provider call.
5. This interactive confirmation is the Host-side human approval boundary;
   it does not make the agent an autonomous submitter and does not authorize
   live execution by itself.

## Consequences

- Deployment-specific target settings stay outside the repository.
- Secrets remain outside config and JobRequest data.
- CI and fake tests can verify both approval outcomes without provider access.
- A cost ceiling is a declared guard; provider price estimation and billing
  enforcement remain outside this slice.

## Verification

The Host config loader and CLI tests cover config resolution, invalid values,
approval denial, and approval acceptance with an injected fake client. No SDK,
credential, network, or real-QPU call is used by these tests.
