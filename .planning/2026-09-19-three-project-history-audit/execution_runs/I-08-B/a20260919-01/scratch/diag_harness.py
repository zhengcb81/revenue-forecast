"""Reproduce ONE positive case outside pytest, with the same harness code path."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(TREE / "scripts"))
sys.path.insert(0, str(TREE / "tests"))

import attestation_protocol as ap  # noqa: E402
from test_attestation_provider_protocol import (  # noqa: E402
    FakeProviderHarness,
)


class Probe(FakeProviderHarness):
    def runTest(self) -> None:  # pragma: no cover - unittest plumbing
        pass


probe = Probe()
probe.setUp()
try:
    probe.install_valid_domain()
    probe.use_fake_provider()
    print("PROVIDER ENV :", os.environ.get(ap.PROVIDER_ENV_VAR))
    print("MODE ENV     :", os.environ.get("I08B_FAKE_MODE"))
    print("ARGV         :", probe.provider_argv())
    print("FAKE EXISTS  :", os.path.exists(probe.provider_argv()[0]))
    request = probe.make_request()
    result = probe.raw_call(request)
    print("CODE         :", result.code)
    print("RETURNCODE   :", result.returncode)
    print("STDOUT_BYTES :", result.stdout_bytes)
    print("DETAIL       :", result.detail)
    print("RESPONSE     :", json.dumps(result.response, sort_keys=True)[:600])
    print("LOGGED CALLS :", probe.provider_calls())
finally:
    probe.tearDown()
