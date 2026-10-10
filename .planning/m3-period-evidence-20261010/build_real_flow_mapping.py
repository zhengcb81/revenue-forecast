"""Read-only mapping of the 18 real mislabeled half-year flows to period_flow.

Reads the two frozen audit artifacts (never writes them), derives each flow's
real window from its explicit definition month range plus the document's
fiscal_year_end, and emits:
  - real_flow_mapping.json       (per-flow provenance rows)
  - period_flow_control_39.json  (minimal synthetic schema-3.9 control input)
then validates the control input with the current engine.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "scripts"))
sys.path.insert(0, str(WORKTREE / "tests"))

AUDIT = Path("C:/Users/郑曾波/Projects/revenue-forecast-audit/runs")
HK_ARTIFACT = AUDIT / "m3-20261009T184946-hk-00700/execution/native-reviewable-input-v2.json"
CN_ARTIFACT = AUDIT / "m3-20261009T184946-cn-688012/execution/forecast/native-input-v6.json"
OUT_DIR = Path(__file__).resolve().parent

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"])}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def window_from_definition(definition: str, period: str, fye: str) -> tuple[str | None, str | None, str]:
    """Derive (start, end, evidence) from an explicit month range in text.

    The year always comes from the strict ``FYyyyy`` period label (definitions
    sometimes omit it); months come from the English month-name range (HK) or
    the Chinese ``n–m 月`` range (CN).
    """
    from datetime import date
    from calendar import monthrange

    if not re.fullmatch(r"FY20\d{2}", period):
        return None, None, "unknown: period is not a strict FYyyyy label"
    year = int(period[2:])
    m1 = m2 = None
    english = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"(?:\s*[-–—]\s*|\s+to\s+)"
        r"(January|February|March|April|May|June|July|August|September|October|November|December)",
        definition,
    )
    if english:
        m1, m2 = MONTHS[english.group(1)], MONTHS[english.group(2)]
        months_evidence = f"{english.group(1)}-{english.group(2)}"
    else:
        chinese = re.search(r"(\d{1,2})\s*[-–—]\s*(\d{1,2})\s*月", definition)
        if chinese:
            m1, m2 = int(chinese.group(1)), int(chinese.group(2))
            months_evidence = f"月 {chinese.group(1)}-{chinese.group(2)}"
    if not (m1 and m2):
        return None, None, "unknown: no explicit month range in definition"
    start = date(year, m1, 1)
    end = date(year, m2, monthrange(year, m2)[1])
    evidence = (
        f"definition month range {months_evidence} + period label {period} + "
        f"fiscal_year_end {fye}"
    )
    return start.isoformat(), end.isoformat(), evidence


def collect_rows(path: Path, label: str) -> list[dict]:
    raw = path.read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    fye = doc["fiscal_year_end"]
    rows = []
    for parameter in doc["parameters"]:
        pid = parameter["parameter_id"]
        is_hk_half = bool(re.search(r"_h[12]_20\d{2}$", pid))
        is_cn_half = pid in {"h124", "h125", "h126"}
        if not (is_hk_half or is_cn_half):
            continue
        if "_factor_" in pid:
            continue  # ratio multipliers are not flows
        definition = parameter.get("definition", "")
        start, end, date_evidence = window_from_definition(definition, parameter["period"], fye)
        rows.append({
            "source_artifact": str(path),
            "source_artifact_sha256": hashlib.sha256(raw).hexdigest(),
            "company": doc["company_name"],
            "flow_id": pid,
            "kind": parameter["kind"],
            "value": parameter["value"],
            "unit": parameter["unit"],
            "currency": parameter.get("currency"),
            "scale": parameter.get("scale"),
            "period": parameter["period"],
            "original_time_basis": parameter["time_basis"],
            "original_has_period_dates": False,
            "definition": definition,
            "derived_period_start": start,
            "derived_period_end": end,
            "date_evidence": date_evidence,
            "date_status": "evidenced" if start else "unknown",
            "source_ids": parameter.get("source_ids", []),
            "claim_ids": parameter.get("claim_ids", []),
            "lane": label,
        })
    return rows


def build_control(rows: list[dict]) -> dict:
    from test_recognition_bridge import forecast_document
    from test_data_contract import apply_parameter_contract

    data = forecast_document()
    data["schema_version"] = "3.9"
    # The real flows are CNY million; align the synthetic fixture skeleton so
    # monetary currency/scale rules hold while rows keep their real values.
    data["currency"] = "CNY"
    data["unit"] = "million"
    for parameter in data["parameters"]:
        if parameter.get("unit") == "USD million":
            parameter["unit"] = "CNY million"
        if parameter.get("currency") == "USD":
            parameter["currency"] = "CNY"
    for claim in data["evidence_claims"]:
        if claim.get("unit") == "USD million":
            claim["unit"] = "CNY million"
    for row in rows:
        if row["date_status"] != "evidenced":
            continue  # unknown stays out; never fabricated
        pid = f"real_{row['flow_id']}"
        parameter = {
            "parameter_id": pid,
            "kind": "reported_fact",
            "value": row["value"],
            "unit": row["unit"],
            "period": row["period"],
            "definition": row["definition"],
            "scenario": None,
            "source_ids": ["filing"],
        }
        apply_parameter_contract(data, parameter, "revenue")
        parameter["time_basis"] = "period_flow"
        parameter["period_start"] = row["derived_period_start"]
        parameter["period_end"] = row["derived_period_end"]
        from revenue_core import text_sha256

        excerpt = f"Checked excerpt for {pid} (real flow {row['flow_id']})."
        data["evidence_claims"].append({
            "claim_id": f"claim_parameter_{pid}",
            "source_id": "filing",
            "target_type": "parameter",
            "target_id": pid,
            "support_type": "exact_value",
            "locator": "Revenue note",
            "excerpt": excerpt,
            "excerpt_sha256": text_sha256(excerpt),
            "content_sha256": "a" * 64,
            "verification_status": "opened_and_checked",
            "verified_by": "m3-period-flow-control",
            "verified_date": data["as_of_date"],
            "extracted_value": row["value"],
            "unit": row["unit"],
            "period": row["period"],
            "capture_receipt_sha256": data["sources"][0]["capture"]["receipt_sha256"],
        })
        parameter["claim_ids"] = [f"claim_parameter_{pid}"]
        data["parameters"].append(parameter)
    return data


def main() -> int:
    rows = collect_rows(HK_ARTIFACT, "HK-00700") + collect_rows(CN_ARTIFACT, "CN-688012")
    print(f"collected flows: {len(rows)}")
    assert len(rows) == 18, f"expected 18 real flows, got {len(rows)}"
    assert all(r["date_status"] == "evidenced" for r in rows), "some dates unknown"
    assert all(r["original_time_basis"] == "annual" for r in rows)

    mapping = {
        "schema_version": "m3-real-flow-mapping/1",
        "purpose": (
            "Read-only provenance mapping of the 18 real half-year flows mislabeled "
            "time_basis=annual (frozen root cause R20) onto the new schema-3.9 "
            "period_flow contract. Original artifacts were opened read-only; "
            "no original run or input was modified."
        ),
        "artifacts": [
            {"path": str(p), "sha256": sha256_file(p)}
            for p in (HK_ARTIFACT, CN_ARTIFACT)
        ],
        "flows": rows,
        "controls": {},
    }
    (OUT_DIR / "real_flow_mapping.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Positive control: re-typed flows validate as 3.9 period flows.
    control = build_control(rows)
    from revenue_core import validate_document

    validated = validate_document(control)
    flow_params = [
        p for p in control["parameters"] if p.get("time_basis") == "period_flow"
    ]
    print(f"control validated: {len(flow_params)} period_flow parameters")
    assert len(flow_params) == 18
    (OUT_DIR / "period_flow_control_39.json").write_text(
        json.dumps(control, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Negative control: the original mislabel fails closed on 3.9 with the
    # same values (annual basis + no dates is still legal for annual params —
    # so instead assert a reversed-window flow is rejected).
    from contracts.evidence import ForecastInputError
    from contracts.period_flow import validate_period_flow_fields

    bad = {
        "time_basis": "period_flow",
        "period": "FY2025",
        "period_start": "2025-07-01",
        "period_end": "2025-06-30",
    }
    try:
        validate_period_flow_fields("negative_control", bad, "12-31")
    except ForecastInputError as exc:
        print(f"negative control rejected: {exc}")
        mapping["controls"] = {
            "positive_39_validate": "PASS (18 period_flow parameters validated)",
            "negative_reversed_window": f"REJECTED: {exc}",
            "original_artifact_write": "none (read-only)",
        }
    else:
        raise AssertionError("negative control must fail")
    (OUT_DIR / "real_flow_mapping.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("controls recorded; mapping written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
