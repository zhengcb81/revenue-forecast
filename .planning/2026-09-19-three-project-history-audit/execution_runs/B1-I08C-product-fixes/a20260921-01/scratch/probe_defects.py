"""B1-I08C pre/post behavioural probe (defect reproduction, both trees).

Usage:  python -B probe_defects.py <repo-root> <out-file>

Prints one deterministic line per defect mechanism so the same command can be
run against the unfixed iso tree and the fixed iso tree and diffed.  Expectations
are frozen in oracle.md section 2/4 BEFORE this probe is first run.
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

import revenue_core  # noqa: E402
from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
from revenue_publication import validate_publication_receipt  # noqa: E402
from revenue_report import render_markdown, validate_forecast_output  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

RESULTS: list[str] = []


def emit(key: str, value: object) -> None:
    RESULTS.append(f"{key} = {value!r}")


def canonical(value):
    return canonical_sha256(value)


def rehash(pkg):
    receipt = pkg["publication_receipt"]
    receipt["validated_payload_sha256"] = canonical(
        {k: v for k, v in pkg.items() if k not in ("result_sha256", "publication_receipt")}
    )
    receipt["receipt_sha256"] = canonical(
        {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    )
    pkg["result_sha256"] = canonical({k: v for k, v in pkg.items() if k != "result_sha256"})
    return pkg


def verdict(fn):
    try:
        fn()
        return "ACCEPTED"
    except ForecastInputError as exc:
        return f"REJECTED:{exc}"
    except Exception as exc:  # noqa: BLE001 - probe
        return f"ERROR:{type(exc).__name__}:{exc}"


def main() -> int:
    scratch = OUT.parent
    scratch.mkdir(parents=True, exist_ok=True)
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(scratch / "probe_registry.jsonl")
    os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
    os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)

    emit("repo_root", str(ROOT))
    emit("revenue_core_sha256", _sha(ROOT / "scripts" / "revenue_core.py"))
    emit("revenue_publication_sha256", _sha(ROOT / "scripts" / "revenue_publication.py"))
    emit("revenue_report_sha256", _sha(ROOT / "scripts" / "revenue_report.py"))

    # --- honest unattested package -----------------------------------------
    honest = revenue_core.run_forecast(forecast_document())
    emit("U_attestation_status", honest["publication_receipt"]["attestation_status"])
    emit("U_has_publication_attestation", "publication_attestation" in honest["publication_receipt"])

    # --- P1: label-only forgery (REM-01a) -----------------------------------
    flipped = copy.deepcopy(honest)
    flipped["publication_receipt"]["attestation_status"] = "host_signed"
    rehash(flipped)
    emit("P1_label_flip_receipt_layer", verdict(lambda: validate_publication_receipt(flipped)))
    emit("P1_label_flip_strong_dispatcher", verdict(lambda: validate_forecast_output(flipped)))

    # --- P2: file existence == capability (REM-01b) -------------------------
    for name, path in (
        ("plain_txt", scratch / "provider_plain.txt"),
        ("bare_py", scratch / "provider_bare.py"),
        ("sys_executable", Path(sys.executable)),
    ):
        if name == "plain_txt":
            path.write_text("hello", encoding="utf-8")
        elif name == "bare_py":
            path.write_text("print('nope')\n", encoding="utf-8")
        os.environ["REVENUE_ATTESTATION_PROVIDER"] = str(path)
        try:
            cap = revenue_core.attestation_capability()
            pkg = revenue_core.run_forecast(forecast_document())
            st = pkg["publication_receipt"]["attestation_status"]
            has = "publication_attestation" in pkg["publication_receipt"]
            emit(f"P2_{name}_capability", cap)
            emit(f"P2_{name}_label", st)
            emit(f"P2_{name}_has_record", has)
        finally:
            os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)

    # --- P3: segments[0].base_revenue coverage gap (REM-03) -----------------
    forged = copy.deepcopy(honest)
    original = float(forged["segments"][0]["base_revenue"])
    forged["segments"][0]["base_revenue"] = original + 1000.0
    rehash(forged)
    emit("P3_receipt_layer", verdict(lambda: validate_publication_receipt(forged)))
    emit("P3_strong_dispatcher", verdict(lambda: validate_forecast_output(forged)))
    try:
        table = render_markdown(forged)
        emit("P3_forged_base_renders", f"{original + 1000.0:,.2f}" in table)
    except Exception as exc:  # noqa: BLE001 - probe
        emit("P3_forged_base_renders", f"ERROR:{type(exc).__name__}:{exc}")

    # --- P4: REM-02 documentation marker ------------------------------------
    doc = validate_publication_receipt.__doc__ or ""
    emit("P4_docstring_says_not_security_boundary", "NOT a security boundary" in doc)
    emit(
        "P4_exports_PublicationReceiptOnlyWarning",
        hasattr(__import__("revenue_publication"), "PublicationReceiptOnlyWarning"),
    )

    text = "\n".join(RESULTS) + "\n"
    OUT.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


def _sha(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "ABSENT"


if __name__ == "__main__":
    raise SystemExit(main())
