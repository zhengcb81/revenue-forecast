"""Replay one frozen real RF input offline in an isolated publication registry."""
from pathlib import Path
import argparse
import gzip
import json
import os
import socket
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from revenue_core import run_forecast, validate_document
from revenue_report import validate_published_forecast, render_markdown


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("v5", "v6"), default="v5")
    case = parser.parse_args().case
    receipt_dir = HERE / "receipts" if case == "v5" else HERE / case / "receipts"
    data = json.loads(gzip.decompress((receipt_dir / "input.json.gz").read_bytes()))
    saved = json.loads(gzip.decompress((receipt_dir / "forecast.json.gz").read_bytes()))
    original_connect = socket.socket.connect
    previous_registry = os.environ.get("REVENUE_PUBLICATION_REGISTRY")
    def deny(sock, address):
        raise RuntimeError("P2_OFFLINE_REPLAY_NO_NETWORK")
    scratch = None
    try:
        socket.socket.connect = deny
        with tempfile.TemporaryDirectory(prefix="rf-p2-replay-") as td:
            scratch = Path(td)
            os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(scratch / "registry.jsonl")
            validate_document(data)
            validate_published_forecast(saved, data)
            result = run_forecast(data)
            validate_published_forecast(result, data)
            assert result["consolidated_forecast"] == saved["consolidated_forecast"]
            claim = next(c for c in data["evidence_claims"] if "narrative_summary_use" in c)
            proof = claim["narrative_summary_use"]
            report = render_markdown(result)
            assert proof["entry"]["research_reason"] in report
            # Markdown normalizes multiline source text; verify each
            # original line without confusing formatting with omitted content.
            for line in proof["summary_claim"]["text"].splitlines():
                assert line.replace("|", "\\|") in report
            assert proof["narrative_ref"]["artifact_sha256"] in report
    finally:
        socket.socket.connect = original_connect
        if previous_registry is None:
            os.environ.pop("REVENUE_PUBLICATION_REGISTRY", None)
        else:
            os.environ["REVENUE_PUBLICATION_REGISTRY"] = previous_registry
    assert scratch is not None and not scratch.exists()
    print("P2 real-input offline replay PASS; zero model/download/parser calls; temporary registry removed")


if __name__ == "__main__":
    main()
