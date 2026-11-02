# Local feedback and CI

`python tools/pre_push_gate.py` runs Ruff and twelve fixed existing source/ref,
complete-forecast, captured-evidence and forged-output checks. It does not repeat
the mypy checks already run by pre-commit. `local_fast_pass` certifies only that
fixed smoke; authors also run the tests relevant to their change.

`python tools/pre_push_gate.py --ci` runs Ruff, public-contract mypy and the
complete historical 41-file behavior set. GitHub Actions explicitly selects this
mode. No coverage was removed from CI to make local push faster. `CI_TESTS` is
that full set; `SMOKE_TESTS` retains its historical alias for other importers.
Neither mode dynamically expands a file dependency graph or checks whole-tree
cleanliness. A real child failure still fails the selected check.

Test subprocesses receive a temporary registry from existing fixtures, disable
dotenv and the host attestation provider, and clear inherited parent Git repository
context. They do not use the owner's configured signing service. The gate's
TemporaryDirectory is removed on success or failure; each author still restores
any separate test fixtures they create.
