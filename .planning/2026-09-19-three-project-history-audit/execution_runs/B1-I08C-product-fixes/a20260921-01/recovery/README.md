# recovery/ — NOT APPLICABLE, with the reason and the nearest real case

`review_and_handoff.md` lists `recovery/` as part of the minimum deliverable
directory and allows a pure-function card to state NA with a reason. This card's
reason, and the nearest thing to a recovery case that IS exercised:

## Why NA

This fix performs **no stateful product operation**: no transaction, no lock, no
migration, no registry write, no long-running process of its own. It changes
validation logic and adds a bounded provider subprocess call. There is therefore
no partially-applied state for a restart to recover, and no "restart after an
exception" scenario to demonstrate.

The attempt is also structurally incapable of leaving production state behind:
`REVENUE_PUBLICATION_REGISTRY` is redirected into the attempt (or into pytest's
tmp dir) for **every** bound command, so a formal `run_forecast` cannot append to
`artifacts/registry/publications.jsonl`. Measured after the fact in
`after/production_status.txt`: the registry is byte-unchanged at
`bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`.

## The nearest real case, which IS exercised (fail-closed, not recovery)

The provider handshake is the only place this card can fail at run time. Every
failure path was required to **fail closed** and to leave **no partial record**,
and each is measured rather than asserted in the abstract:

| failure | expected consequence | evidence |
|---|---|---|
| provider path exists but cannot be spawned (a bare `.py` on Windows) | no capability, `unattested`, no record | `before/b1_unfixed_r3.stdout.txt` → `test_rem01_b_to_d_file_existence_is_not_signing_capability[bare_py]` (GREEN on the fixed tree) |
| provider absent / plain `.txt` / `sys.executable` | no capability, `unattested`, no record | same node family, `[plain_txt]` and `[sys_executable]` |
| provider answers but its key is not trusted | no capability, `unattested`, no record, recorded code `provider_key_untrusted` | `test_rem01_f_untrusted_provider_is_not_host_signed` |
| provider returns a signature that does not match the request | no record, publication stays `unattested` | `request_publication_attestation` catches `ForecastInputError` and returns `None` with a recorded diagnostic |

The invariant a reviewer should check is the one the frozen test
`test_rem01_b_to_d_file_existence_is_not_signing_capability` asserts on every
variant: **after any handshake failure the artifact carries
`attestation_status == "unattested"` and NO `publication_attestation` key at
all.** A partial or empty record is never attached, so there is nothing for a
later reader to half-trust.

## What is genuinely not covered

A real crash in the middle of a *publication transaction* (registry written,
output not written) is I-09-A's scope, not this card's — `decision.md` §7.2
records it as not closed.
