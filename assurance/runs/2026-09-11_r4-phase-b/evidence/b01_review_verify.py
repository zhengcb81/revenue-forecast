"""Verify the B01 review's findings against the committed tree (read-only).

Checks the reviewer's four verifiable claims without changing any product file:

  C1 (P1)  which artifact does the CONSUMER actually read, and is the hash my
           acceptance case froze the same one?
  C2 (P2)  does config admission accept a quoted boolean for
           `reusable_for_filing`, and does bool() then invert the intent?
  C3 (P3)  is the `not reusable_root_ids or ...` escape reachable from resolve()?
  C4 (P3)  how many tests does the FC-1204 complexity ratchet file have?

Usage: python evidence/b01_review_verify.py
"""

from __future__ import annotations

import inspect
import json
import sys
import tempfile
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path(__file__).resolve().parents[4]
WIKI = REVENUE.parent / "company-wiki"
sys.path.insert(0, str(WIKI / "src"))

from company_wiki.source_catalog import cli  # noqa: E402
from company_wiki.source_catalog.config import load_catalog_config  # noqa: E402
from company_wiki.source_catalog.policy import export_policy  # noqa: E402
from company_wiki.source_catalog.policy_2x import export_policy_2x  # noqa: E402
from company_wiki.source_catalog.resolver import SourceResolver  # noqa: E402

SHIPPED = WIKI / "config" / "source_catalog.yaml"
FROZEN_IN_MY_CASE = "cf0ac2adf9714fe003eb1d1497d678877840e35a6a6c32bc65aa7e5d0c0e1626"

out: dict = {}


def c1_consumer_artifact() -> None:
    config = load_catalog_config(SHIPPED)
    v1_hash, v1_payload = export_policy(config)
    v2_hash, v2_payload = export_policy_2x(config)
    payload_fn = getattr(cli, "_policy_export_payload", None)
    consumer = None
    if payload_fn is not None:
        try:
            consumer = payload_fn(config)
        except TypeError:
            consumer = payload_fn()
        if isinstance(consumer, dict):
            consumer = {
                "policy_hash": consumer.get("policy_hash"),
                "reusable_roots": sorted(
                    root.get("root_id")
                    for root in (consumer.get("roots") or [])
                    if root.get("reusable_for_filing")
                ),
            }
    out["C1"] = {
        "export_policy_v1_hash": v1_hash,
        "export_policy_2x_hash": v2_hash,
        "consumer_payload_source": getattr(payload_fn, "__module__", None),
        "consumer_payload": consumer,
        "frozen_by_my_case": FROZEN_IN_MY_CASE,
        "my_case_froze_the_consumer_artifact": FROZEN_IN_MY_CASE
        in {v2_hash, (consumer or {}).get("policy_hash")},
        "v1_reusable_roots": sorted(
            r.get("root_id") for r in (v1_payload.get("roots") or [])
            if r.get("reusable_for_filing")
        ),
        "v2_reusable_roots": sorted(
            r.get("root_id") for r in (v2_payload.get("roots") or [])
            if r.get("reusable_for_filing")
        ),
        "consumer_source_line": (
            inspect.getsource(payload_fn).strip().splitlines()[:12] if payload_fn else None
        ),
    }


def c2_quoted_boolean() -> None:
    text = SHIPPED.read_text(encoding="utf-8")
    quoted = text.replace(
        "roots:", "roots:\n  - root_id: probe\n    kind: directory\n"
                  "    path: '${PROJECT_ROOT}'    \n    reusable_for_filing: \"false\"\n",
        1,
    ) if False else None
    # write a minimal standalone config instead of editing the shipped one
    body = (
        'schema_version: "1.0"\n'
        "catalog_dir: '${PROJECT_ROOT}/.source_catalog'\n"
        "reusable_root_kinds: [directory]\n"
        "roots:\n"
        "  - root_id: quoted_false\n"
        "    kind: directory\n"
        "    path: '${PROJECT_ROOT}'\n"
        '    reusable_for_filing: "false"\n'
    )
    with tempfile.TemporaryDirectory(prefix="b01-verify-") as tmp:
        path = Path(tmp) / "source_catalog.yaml"
        path.write_text(body, encoding="utf-8")
        admitted, spec_flag, effective = None, None, None
        try:
            config = load_catalog_config(path)
            admitted = True
            spec_flag = config.roots[0].reusable_for_filing
            from company_wiki.source_catalog.policy import _effective_reusable

            effective = _effective_reusable(config.roots[0], config)
        except Exception as exc:  # noqa: BLE001 - the probe reports the type
            admitted = f"{exc.__class__.__name__}: {exc}"
    out["C2"] = {
        "quoted_false_admitted": admitted,
        "parsed_flag_value": spec_flag,
        "effective_reusable": effective,
        "fail_open": effective is True,
        "shipped_config_untouched": quoted is None and text == SHIPPED.read_text(encoding="utf-8"),
    }


def c3_empty_set_escape() -> None:
    src = inspect.getsource(SourceResolver.resolve)
    select_src = inspect.getsource(SourceResolver._select_candidate)
    out["C3"] = {
        "resolve_rejects_when_set_empty": "not any(" in src and "no_reusable_root_location" in src,
        "escape_present": "not reusable_root_ids" in select_src,
        "select_candidate_callers": [
            name for name, obj in inspect.getmembers(SourceResolver, inspect.isfunction)
            if "_select_candidate" in inspect.getsource(obj)
        ],
    }


def c4_ratchet_test_count() -> None:
    import re

    text = (WIKI / "tests" / "contract" / "test_fc1204_complexity_ratchet.py").read_text(
        encoding="utf-8"
    )
    tests = re.findall(r"^def (test_\w+)", text, re.M)
    out["C4"] = {"complexity_ratchet_tests": tests, "count": len(tests)}


def main() -> int:
    c1_consumer_artifact()
    c2_quoted_boolean()
    c3_empty_set_escape()
    c4_ratchet_test_count()
    target = RUN / "evidence" / "b01-review-verify.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key in sorted(out):
        print("==", key)
        for name, value in out[key].items():
            print(f"   {name}: {json.dumps(value, ensure_ascii=False)[:220]}")
    print("wrote", target.relative_to(REVENUE).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
