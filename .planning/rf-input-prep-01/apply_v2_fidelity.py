"""Apply the v2 fidelity fixes to build_mdb_input.py.

Two changes, both driven by independent self-check findings:
  * table excerpts become exact slices of the checked FY2025 10-K text
    (previously hand-rendered reading order, not verbatim substrings);
  * an explicit revenue_basis (operations=total, as_reported, fiscal_year) is
    declared on the reported parameter and every historical observation.
"""

from __future__ import annotations

from pathlib import Path

PATH = Path(__file__).resolve().parent / "build_mdb_input.py"


def main() -> int:
    text = PATH.read_text(encoding="utf-8")

    anchor = 'ENVELOPE = ROOT / "requests" / "mongodb-envelope.json"\n'
    if anchor not in text:
        raise SystemExit("anchor for TEXT path not found")
    text = text.replace(
        anchor,
        anchor
        + 'FILING_TEXT = ROOT / "mdb-fy2025-10k.txt"\n'
        + '_FILING = FILING_TEXT.read_text(encoding="utf-8")\n'
        + "\n"
        + "\n"
        + "def _slice(start: str, end: str) -> str:\n"
        + '    """Exact verbatim slice of the checked filing text."""\n'
        + "    begin = _FILING.index(start)\n"
        + "    finish = _FILING.index(end, begin) + len(end)\n"
        + '    return _FILING[begin:finish]\n',
    )

    # Replace the two hand-rendered table excerpts with verbatim slices.
    start = text.index('    "total_table": (')
    end = text.index('    "disagg_basis": (')
    replacement = (
        '    "total_table": _slice(\n'
        '        "Subscription\\n| $ | 1,943,864", "1,284,040 | 100 |"\n'
        "    ),\n"
        '    "disagg_table": _slice(\n'
        '        "Subscription product categories and services:", "1,284,040 |"\n'
        "    ),\n"
    )
    text = text[:start] + replacement + text[end:]

    # Declare the reporting basis on the reported parameter and history.
    text = text.replace(
        '        "reported_fact",\n'
        '        HISTORY_TOTAL[2025],\n'
        '        "FY2025",\n'
        '        "revenue",\n'
        '        "Consolidated total revenue for fiscal year ended 2025-01-31, as reported (ASC 606).",\n'
        '        "As-reported consolidated total revenue; equals the sum of the three disclosed revenue categories.",\n'
        '        ["claim_reported_total_2025"],\n',
        '        "reported_fact",\n'
        '        HISTORY_TOTAL[2025],\n'
        '        "FY2025",\n'
        '        "revenue",\n'
        '        "Consolidated total revenue for fiscal year ended 2025-01-31, as reported (ASC 606).",\n'
        '        "As-reported consolidated total revenue; equals the sum of the three disclosed revenue categories.",\n'
        '        ["claim_reported_total_2025"],\n'
        '        revenue_basis=REPORTING_BASIS,\n',
    )
    text = text.replace(
        '        parameters.append(record)',
        '        if revenue_basis is not None:\n'
        '            record["revenue_basis"] = dict(revenue_basis)\n'
        '        parameters.append(record)',
    )
    text = text.replace(
        "        *,\n        scenario: str | None = None,\n        unit_label: str | None = None,\n",
        "        *,\n        scenario: str | None = None,\n        unit_label: str | None = None,\n        revenue_basis: dict | None = None,\n",
    )
    text = text.replace(
        "            {\n"
        '                "year": year,\n'
        '                "value": HISTORY_TOTAL[year],\n'
        '                "source_ids": [sid],\n'
        '                "claim_ids": [cid],\n'
        "            }",
        "            {\n"
        '                "year": year,\n'
        '                "value": HISTORY_TOTAL[year],\n'
        '                "source_ids": [sid],\n'
        '                "claim_ids": [cid],\n'
        '                "revenue_basis": dict(REPORTING_BASIS),\n'
        "            }",
    )
    text = text.replace(
        'SLUG = {ATLAS: "atlas", OTHER: "other_subscription", SERVICES: "services"}\n',
        'SLUG = {ATLAS: "atlas", OTHER: "other_subscription", SERVICES: "services"}\n'
        "\n"
        "# Reporting basis declared for the reported total and every historical\n"
        "# observation: consolidated total (no continuing/discontinued split) and\n"
        "# as-reported (no restatement), full fiscal years of the January year-end.\n"
        "REPORTING_BASIS = {\n"
        '    "operations": "total",\n'
        '    "statement_status": "as_reported",\n'
        '    "period_kind": "fiscal_year",\n'
        "}\n",
    )
    # Fail closed if any excerpt is not a verbatim substring of the checked text.
    text = text.replace(
        'def main() -> int:\n    envelope =',
        'def _assert_verbatim() -> None:\n'
        "    for key, excerpt in EXCERPTS.items():\n"
        "        if excerpt not in _FILING:\n"
        '            raise AssertionError(f"excerpt {key} is not a verbatim slice of the filing text")\n'
        "\n"
        "\n"
        "def main() -> int:\n"
        "    _assert_verbatim()\n"
        "    envelope =",
    )

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("patched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
