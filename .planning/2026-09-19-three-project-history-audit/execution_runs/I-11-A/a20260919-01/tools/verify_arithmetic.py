"""I-11-A: recompute the frozen arithmetic identities A1-A7 with exact rationals.

Rule (oracle §5): operands are the RAW strings as they appear in the filing text,
parsed by this script; every operand must also be locatable in the archived
extraction outputs, otherwise the identity is reported as `source_not_located`.
No derived value is ever used as an operand.

Usage: python -X utf8 -B tools/verify_arithmetic.py <out.json>
"""

from __future__ import annotations

import json
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPT = os.path.dirname(HERE)
EV = os.path.join(ATTEMPT, "evidence", "I-11-A", "extract")

ZIJIN_P1 = os.path.join(EV, "P1_zijin_pages.json")
MSFT_TABLES = os.path.join(EV, "P1_msft_tables.json")

# operand definitions: (label, raw string, evidence file, page or table index)
IDENTS = [
    {
        "id": "A1",
        "claim": "Zijin FY2025 four-segment EXTERNAL sales revenue sums to consolidated revenue",
        "operands": [
            ("mineral_products", "109,977,556,345", "CN-ZIJIN-AR2025", 327),
            ("smelting_products", "165,858,644,874", "CN-ZIJIN-AR2025", 327),
            ("trading", "29,212,610,830", "CN-ZIJIN-AR2025", 327),
            ("other", "44,030,270,803", "CN-ZIJIN-AR2025", 327),
        ],
        "result_operand": ("consolidated", "349,079,082,852", "CN-ZIJIN-AR2025", 327),
    },
    {
        "id": "A2",
        "claim": "Zijin FY2025 (external + internal) segment totals minus eliminations equals consolidated revenue",
        "operands": [
            ("mineral_total", "138,271,672,956", "CN-ZIJIN-AR2025", 327),
            ("smelting_total", "189,683,879,295", "CN-ZIJIN-AR2025", 327),
            ("trading_total", "170,521,025,777", "CN-ZIJIN-AR2025", 327),
            ("other_total", "85,572,651,236", "CN-ZIJIN-AR2025", 327),
            ("eliminations", "-234,970,146,412", "CN-ZIJIN-AR2025", (327, 328)),
        ],
        "result_operand": ("consolidated", "349,079,082,852", "CN-ZIJIN-AR2025", 327),
    },
    {
        "id": "A3",
        "claim": "Zijin FY2024 four-segment EXTERNAL sales revenue sums to FY2024 consolidated revenue",
        "operands": [
            ("mineral_products", "74,089,365,354", "CN-ZIJIN-AR2025", 328),
            ("smelting_products", "181,141,823,725", "CN-ZIJIN-AR2025", 328),
            ("trading", "29,386,475,085", "CN-ZIJIN-AR2025", 328),
            ("other", "19,022,292,989", "CN-ZIJIN-AR2025", 328),
        ],
        "result_operand": ("consolidated", "303,639,957,153", "CN-ZIJIN-AR2025", 328),
    },
    {
        "id": "A4",
        "claim": "Zijin FY2025 production/sales table: sales exceed production for all four products",
        "operands": [
            ("gold_production_kg", "82,743", "CN-ZIJIN-AR2025", 44),
            ("gold_sales_kg", "83,161", "CN-ZIJIN-AR2025", 44),
            ("copper_production_t", "878,180", "CN-ZIJIN-AR2025", 44),
            ("copper_sales_t", "884,943", "CN-ZIJIN-AR2025", 44),
            ("zinc_production_t", "348,556", "CN-ZIJIN-AR2025", 44),
            ("zinc_sales_t", "352,470", "CN-ZIJIN-AR2025", 44),
            ("silver_production_kg", "429,382", "CN-ZIJIN-AR2025", 44),
            ("silver_sales_kg", "430,254", "CN-ZIJIN-AR2025", 44),
        ],
        "result_operand": None,
    },
    {
        "id": "A5",
        "claim": "MSFT FY2026 three reportable segments sum to consolidated revenue",
        "operands": [
            ("PBP", "139,996", "US-MSFT-10K-FY2026", 74),
            ("IC", "137,791", "US-MSFT-10K-FY2026", 74),
            ("MPC", "54,052", "US-MSFT-10K-FY2026", 74),
        ],
        "result_operand": ("total", "331,839", "US-MSFT-10K-FY2026", 74),
    },
    {
        "id": "A6",
        "claim": "MSFT FY2026 product/service disaggregation sums to consolidated revenue",
        "operands": [
            ("server_products_and_cloud_services", "129,425", "US-MSFT-10K-FY2026", 76),
            ("m365_commercial", "101,997", "US-MSFT-10K-FY2026", 76),
            ("xbox", "21,790", "US-MSFT-10K-FY2026", 76),
            ("linkedin", "19,817", "US-MSFT-10K-FY2026", 76),
            ("windows_and_devices", "17,084", "US-MSFT-10K-FY2026", 76),
            ("search_advertising", "15,176", "US-MSFT-10K-FY2026", 76),
            ("m365_consumer", "9,175", "US-MSFT-10K-FY2026", 76),
            ("dynamics", "9,006", "US-MSFT-10K-FY2026", 76),
            ("enterprise_and_partner_services", "8,260", "US-MSFT-10K-FY2026", 76),
            ("other", "109", "US-MSFT-10K-FY2026", 76),
        ],
        "result_operand": ("total", "331,839", "US-MSFT-10K-FY2026", 76),
    },
    {
        "id": "A7",
        "claim": "MSFT FY2025 segment and product decompositions each sum to FY2025 consolidated revenue",
        "operands": [
            ("PBP", "120,810", "US-MSFT-10K-FY2026", 74),
            ("IC", "106,265", "US-MSFT-10K-FY2026", 74),
            ("MPC", "54,649", "US-MSFT-10K-FY2026", 74),
        ],
        "result_operand": ("total", "281,724", "US-MSFT-10K-FY2026", 74),
        "second_sum": {
            "operands": [
                ("server_products_and_cloud_services", "98,435", "US-MSFT-10K-FY2026", 76),
                ("m365_commercial", "87,767", "US-MSFT-10K-FY2026", 76),
                ("xbox", "23,455", "US-MSFT-10K-FY2026", 76),
                ("linkedin", "17,812", "US-MSFT-10K-FY2026", 76),
                ("windows_and_devices", "17,314", "US-MSFT-10K-FY2026", 76),
                ("search_advertising", "13,878", "US-MSFT-10K-FY2026", 76),
                ("m365_consumer", "7,404", "US-MSFT-10K-FY2026", 76),
                ("dynamics", "7,827", "US-MSFT-10K-FY2026", 76),
                ("enterprise_and_partner_services", "7,760", "US-MSFT-10K-FY2026", 76),
                ("other", "72", "US-MSFT-10K-FY2026", 76),
            ],
            "result_operand": ("total", "281,724", "US-MSFT-10K-FY2026", 76),
        },
    },
]


def to_frac(raw: str) -> Fraction:
    return Fraction(raw.replace(",", ""))


def locate(needle: str, corpus: str) -> bool:
    """Locate a raw figure string in an extraction output.

    Accepted spellings: the literal string, the comma-free spelling, and (for
    signed figures) the unsigned magnitude -- because PDF table cells render
    negative amounts in parentheses, which the layout reconstruction places
    outside the number. The sign is carried by the operand definition itself and
    is never inferred from the text.
    """
    if not corpus:
        return False
    if needle in corpus:
        return True
    plain_needle = needle.replace(",", "").lstrip("-")
    plain_corpus = corpus.replace(",", "")
    return plain_needle in plain_corpus


def locate_in(corpora, doc: str, where, needle: str) -> bool:
    pages = where if isinstance(where, (tuple, list)) else (where,)
    for page in pages:
        if locate(needle, corpora.get(doc, {}).get(page, "")):
            return True
    return False


def load_corpora():
    corpora = {}
    with open(ZIJIN_P1, encoding="utf-8") as fh:
        z = json.load(fh)
    corpora["CN-ZIJIN-AR2025"] = {p["pdf_page"]: p["text"] for p in z["pages"]}
    with open(MSFT_TABLES, encoding="utf-8") as fh:
        m = json.load(fh)
    tables = {h["table_index"]: "\n".join(" | ".join(c["text"] for c in r) for r in h["rows"])
              for h in m["revenue_tables"]}
    corpora["US-MSFT-10K-FY2026"] = tables
    return corpora


def main() -> int:
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(EV, "arithmetic_oracle.json")
    corpora = load_corpora()
    report = {"method": "exact rationals via fractions.Fraction; operands parsed from raw strings",
              "identities": [], "summary": {}}
    n_pass = n_fail = 0
    for ident in IDENTS:
        entry = {"id": ident["id"], "claim": ident["claim"], "operands": [], "problems": []}
        total = Fraction(0)
        for label, raw, doc, page in ident["operands"]:
            located = locate_in(corpora, doc, page, raw)
            total += to_frac(raw)
            entry["operands"].append({
                "label": label, "raw": raw, "document": doc, "page_or_table": page,
                "located_in_evidence": located,
                "value": str(to_frac(raw)),
            })
            if not located:
                entry["problems"].append("operand %s (%s) not located in %s page/table %s"
                                         % (label, raw, doc, page))
        entry["computed_sum"] = str(total)
        if ident.get("second_sum"):
            second = Fraction(0)
            for label, raw, doc, page in ident["second_sum"]["operands"]:
                located = locate_in(corpora, doc, page, raw)
                second += to_frac(raw)
                entry["operands"].append({
                    "label": "FY2025::" + label, "raw": raw, "document": doc,
                    "page_or_table": page, "located_in_evidence": located,
                    "value": str(to_frac(raw)),
                })
                if not located:
                    entry["problems"].append("operand FY2025::%s (%s) not located" % (label, raw))
            entry["second_computed_sum"] = str(second)
            label, raw, doc, page = ident["second_sum"]["result_operand"]
            entry["second_result_operand"] = {
                "raw": raw, "located_in_evidence": locate_in(corpora, doc, page, raw),
                "value": str(to_frac(raw)),
            }
            entry["second_difference"] = str(second - to_frac(raw))
        if ident["result_operand"] is not None:
            label, raw, doc, page = ident["result_operand"]
            located = locate_in(corpora, doc, page, raw)
            entry["result_operand"] = {"label": label, "raw": raw, "document": doc,
                                       "page_or_table": page, "located_in_evidence": located}
            entry["difference"] = str(total - to_frac(raw))
            if not located:
                entry["problems"].append("result operand %s not located" % raw)
        else:
            pairs = [(entry["operands"][i]["label"], Fraction(entry["operands"][i]["value"]),
                      Fraction(entry["operands"][i + 1]["value"]))
                     for i in range(0, len(entry["operands"]), 2)]
            entry["production_minus_sales"] = [
                {"product": a.split("_")[0], "sales_minus_production": str(c - b),
                 "sign_ok": c > b} for a, b, c in pairs]
            entry["difference"] = "n/a (sign test, not a sum)"
        if entry["problems"]:
            entry["verdict"] = "rejected"
            n_fail += 1
        else:
            if ident["result_operand"] is not None:
                ok = entry["difference"] == "0"
                if ident.get("second_sum"):
                    ok = ok and entry["second_difference"] == "0"
                entry["verdict"] = "pass" if ok else "fail"
            else:
                entry["verdict"] = "pass" if all(p["sign_ok"] for p in entry["production_minus_sales"]) else "fail"
            n_pass += 1 if entry["verdict"] == "pass" else 0
        report["identities"].append(entry)
    report["summary"] = {"identities": len(IDENTS), "pass": n_pass, "rejected": n_fail,
                         "fail": len(IDENTS) - n_pass - n_fail}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    for e in report["identities"]:
        line = "%s %s difference=%s" % (e["id"], e["verdict"], e.get("difference"))
        print(line.encode("ascii", "replace").decode("ascii"))
        for p in e["problems"]:
            print("   PROBLEM:", p.encode("ascii", "replace").decode("ascii"))
    print(json.dumps(report["summary"], sort_keys=True))
    print("wrote", out_path)
    return 0 if report["summary"]["fail"] == 0 and report["summary"]["rejected"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
