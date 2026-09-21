"""I-08-C / r3 pre-freeze DERIVATION PROBE for oracle case E4.

Purpose: independently re-derive E4's expected outcome (oracle line 54:
`verification_context_sha256` mutated -> ForecastInputError "verification
context mismatch") from the production sources, BEFORE appending the r3 freeze.

This probe is NOT the frozen evidence run and its stdout is NOT test evidence.
It exists so the r3 expectation is anchored in a reproducible independent check
rather than in a green pytest run. The frozen E4 assertion is afterwards made by
the pytest node `test_e4_verification_context_mutation_rejected` in
`test_i08c_consumer_rejection.py` (the frozen artifact).

READ-ONLY with respect to production: `REVENUE_PUBLICATION_REGISTRY` is
redirected to a temp dir because formal `run_forecast` registers publications.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

_tmp = tempfile.mkdtemp(prefix="i08c_e4_")
os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(Path(_tmp) / "publications.jsonl")

from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
from revenue_core import run_forecast  # noqa: E402
from revenue_publication import (  # noqa: E402
    VerificationContext,
    expected_publication_gates,
    validate_publication_receipt,
)
from revenue_report import validate_forecast_output  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

out: dict[str, object] = {}

S = run_forecast(forecast_document())
receipt = S["publication_receipt"]
out["S.receipt.attestation_status"] = receipt["attestation_status"]
out["S.receipt.formal_output_mode"] = receipt["formal_output_mode"]
out["S.receipt.gate_ids"] = receipt["gate_ids"]
out["S.receipt.has_verification_context_sha256"] = "verification_context_sha256" in receipt
out["S.receipt.verification_context_sha256"] = receipt["verification_context_sha256"]

# production-produced context, for confirmation only (NOT used to build expectations)
correct = VerificationContext(S["input_sha256"], expected_publication_gates(S), receipt["engine_version"])
out["production.context_sha256"] = correct.context_sha256()

# --- E4(a): mutate verification_context_sha256 only ---------------------------
a = copy.deepcopy(S)
a["publication_receipt"]["verification_context_sha256"] = "0" * 64
try:
    validate_publication_receipt(a)
    out["E4a.receipt_layer"] = "ACCEPTED"
except ForecastInputError as exc:
    out["E4a.receipt_layer"] = f"RAISED ForecastInputError: {exc}"
except Exception as exc:  # noqa: BLE001
    out["E4a.receipt_layer"] = f"RAISED {type(exc).__name__}: {exc}"

# --- E4(b): mutate + recompute every NON-SECRET self-hash ---------------------
b = copy.deepcopy(S)
r = b["publication_receipt"]
r["verification_context_sha256"] = "0" * 64
r["validated_payload_sha256"] = canonical_sha256(
    {k: v for k, v in b.items() if k not in ("result_sha256", "publication_receipt")}
)
r["receipt_sha256"] = canonical_sha256({k: v for k, v in r.items() if k != "receipt_sha256"})
b["result_sha256"] = canonical_sha256({k: v for k, v in b.items() if k != "result_sha256"})
try:
    validate_publication_receipt(b)
    out["E4b.receipt_layer"] = "ACCEPTED"
except ForecastInputError as exc:
    out["E4b.receipt_layer"] = f"RAISED ForecastInputError: {exc}"
except Exception as exc:  # noqa: BLE001
    out["E4b.receipt_layer"] = f"RAISED {type(exc).__name__}: {exc}"

# --- E4(c): production context_sha256 equals an independent reconstruction ----
# Mirrors scripts/revenue_publication.py:85-93: context_sha256 hashes
# VerificationContext.to_dict(), whose field is `executed_gate_ids` (NOT the
# receipt's `gate_ids`).  First probe revision used the wrong key and reported
# equal=False; corrected here before the r3 freeze.
independent = canonical_sha256(
    {
        "validated_input_sha256": S["input_sha256"],
        "executed_gate_ids": list(expected_publication_gates(S)),
        "validator_version": receipt["engine_version"],
    }
)
out["E4c.production_context_sha256"] = correct.context_sha256()
out["E4c.independent_reconstruction"] = independent
out["E4c.equal"] = correct.context_sha256() == independent

# --- strong dispatcher on E4(a) ----------------------------------------------
try:
    validate_forecast_output(a)
    out["E4a.dispatcher"] = "ACCEPTED"
except ForecastInputError as exc:
    out["E4a.dispatcher"] = f"RAISED ForecastInputError: {exc}"
except Exception as exc:  # noqa: BLE001
    out["E4a.dispatcher"] = f"RAISED {type(exc).__name__}: {exc}"

# --- controls: no mutation ----------------------------------------------------
try:
    validate_publication_receipt(S)
    out["control.receipt_layer"] = "ACCEPTED"
except Exception as exc:  # noqa: BLE001
    out["control.receipt_layer"] = f"RAISED {type(exc).__name__}: {exc}"

print(json.dumps(out, indent=2, sort_keys=True, ensure_ascii=True))
