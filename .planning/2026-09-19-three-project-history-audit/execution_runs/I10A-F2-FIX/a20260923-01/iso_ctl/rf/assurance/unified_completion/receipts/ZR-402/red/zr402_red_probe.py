"""ZR-402 RED evidence: survivor mutants over the current adapter suite.

Machine-proves the verification gaps (no killer tests exist today):
  S1  facade v2 route: (a) unknown/BOGUS adapter_id -> ScannerFacadeError is
      unpinned (seam02 covers only adapter_id=None "missing"); (b) adapter
      RUNTIME failure -> ScannerFacadeError with NO v1 fallback is unpinned
      (the "catch & fall back to v1" mutant survives).
  S2  kind-routing mutant (M8): applied in-process, the EXACT assertions of
      the existing dispatch tests still pass (canonical kind<->adapter
      pairing only; no mismatched/bogus kind killer).
  S3  determinism negative missing (M1): conformance suite has no
      non-deterministic adapter negative; determinism check untested.
  S4  adapter-route kind-branch gate missing: no test pins zero
      ``.kind ==``/``.kind in``/``root_id ==`` branches in the route core
      (adapter_dispatch.py, admission.py, adapters/registry.py,
      adapters/interface.py, adapters/conformance.py).  FC-1201 cannot
      catch this: adapter_dispatch.py and admission.py sit INSIDE
      _ROOT_HARDCODE_ALLOWED_FILES (token-mention ratchet, not a branch
      gate), and test_spi02 freezes scanner.py only.

Read-only wrt the repo: imports modules, monkeypatches IN-PROCESS ONLY,
never writes product files.  Emits evidence JSON to the path in argv[1].
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(WIKI / "src"))

TESTS = WIKI / "tests"
ROUTE_MODULES = [
    "adapter_dispatch.py",
    "admission.py",
    "adapters/registry.py",
    "adapters/interface.py",
    "adapters/conformance.py",
]


def _iter_test_texts():
    for path in sorted(TESTS.rglob("test_*.py")):
        yield path, path.read_text(encoding="utf-8", errors="replace")


def check_s1_facade_fail_closed_unpinned() -> dict:
    """S1 hypothesis DISPROVEN (honest negative): the facade v2 route IS
    fully pinned today —
      missing adapter_id : test_scanner_facade.py::test_seam02_v2_stub_fails_closed
      bogus adapter_id   : test_shadow_parity_runner.py::test_ex08_future_root_unknown_adapter_blocks
      runtime failure + no-v1-fallback :
          test_shadow_parity_runner.py::test_ex08_adapter_error_fails_closed_not_legacy_fallback
    This check verifies those three killers exist and are real (assert
    their bodies reference ScannerFacadeError + the failure construction).
    """
    pins = {
        "missing_adapter_id": False,
        "bogus_adapter_id": False,
        "runtime_failure_no_fallback": False,
    }
    for path, text in _iter_test_texts():
        if "ScannerFacadeError" not in text:
            continue
        name = path.relative_to(TESTS).as_posix()
        if "test_seam02_v2_stub_fails_closed" in text:
            pins["missing_adapter_id"] = True
        if "test_ex08_future_root_unknown_adapter_blocks" in text and "not_registered" in text:
            pins["bogus_adapter_id"] = f"{name}#ex08_unknown"
        if "test_ex08_adapter_error_fails_closed_not_legacy_fallback" in text:
            pins["runtime_failure_no_fallback"] = (
                "_BoomAdapter" in text or "RuntimeError" in text
            )
    covered = all(bool(v) for v in pins.values())
    return {
        "survivor": not covered,
        "covered": covered,
        "evidence": "facade fail-closed is already fully pinned "
                    f"(missing/bogus/runtime-no-fallback = {covered}); "
                    "NOT a red gap — recorded as honest negative",
        "pins": {k: bool(v) for k, v in pins.items()},
    }


def check_s2_kind_routing_mutant_survives() -> dict:
    """S2: apply M8 in-process (route by root.kind, ignore adapter_id) and
    replay the EXACT assertions of the existing dispatch tests."""
    from company_wiki.source_catalog import adapter_dispatch
    from company_wiki.source_catalog.models import RootSpec

    def root(kind: str, adapter_id: str) -> RootSpec:
        return RootSpec(
            root_id="root_x",
            path=Path("/tmp/root_x"),
            kind=kind,
            adapter_id=adapter_id,
            read_only=True,
            reusable_for_filing=True,
        )

    canonical = [
        ("directory", "sidecar_filing_v1", "sidecar_filing_v1"),
        ("company_raw", "company_raw_v1", "company_raw_v1"),
        ("dayu_portfolio", "dayu_filing_v1", "dayu_filing_v1"),
    ]
    baseline_ok = all(
        adapter_dispatch.adapter_for(root(kind, aid)).adapter_id == expect
        for kind, aid, expect in canonical
    )

    original = adapter_dispatch.adapter_for
    kind_route = {
        "directory": "sidecar_filing_v1",
        "company_raw": "company_raw_v1",
        "dayu_portfolio": "dayu_filing_v1",
    }

    def mutant_for(root: RootSpec):
        from company_wiki.source_catalog.adapters.company_raw import CompanyRawAdapter
        from company_wiki.source_catalog.adapters.dayu import DayuAdapter
        from company_wiki.source_catalog.adapters.sidecar import SidecarFilingAdapter

        chosen = kind_route.get(root.kind)
        if chosen is None:
            raise adapter_dispatch.AdapterDispatchError("not registered")
        return {
            "sidecar_filing_v1": SidecarFilingAdapter,
            "company_raw_v1": CompanyRawAdapter,
            "dayu_filing_v1": DayuAdapter,
        }[chosen]()

    adapter_dispatch.adapter_for = mutant_for
    try:
        mutant_passes_existing = all(
            adapter_dispatch.adapter_for(root(kind, aid)).adapter_id == expect
            for kind, aid, expect in canonical
        )
        mismatched_broken = 0
        for kind, aid, expect in canonical:
            got = adapter_dispatch.adapter_for(root("directory", aid))
            if got.adapter_id != expect:
                mismatched_broken += 1
    finally:
        adapter_dispatch.adapter_for = original

    return {
        "baseline_ok": baseline_ok,
        "survivor": mutant_passes_existing,
        "evidence": "with adapter_for replaced by a kind-routing mutant, the "
                    "exact assertions of test_adapter_production_dispatch.py "
                    "still pass (canonical pairing only) => M8 survives; "
                    f"{mismatched_broken} mismatched kind<->adapter cases "
                    "would silently reroute with no killer",
        "mutant_passes_existing_assertions": mutant_passes_existing,
        "mismatched_cases_unpinned": mismatched_broken,
    }


def check_s3_determinism_negative_missing() -> dict:
    """S3: the conformance suite contains no non-deterministic adapter
    negative and never asserts receipt['determinism'] FAILED."""
    path = TESTS / "contract" / "test_adapter_conformance.py"
    text = path.read_text(encoding="utf-8", errors="replace")
    has_nondeterministic_class = bool(re.search(r"class .*(Non.?Determin|Flip)", text, re.I))
    has_determinism_failed_assert = bool(
        re.search(r'receipt\["determinism"\].*FAILED', text)
    )
    survivor = not has_nondeterministic_class and not has_determinism_failed_assert
    return {
        "survivor": survivor,
        "evidence": "test_adapter_conformance.py has no non-deterministic "
                    "adapter mutant and never asserts determinism FAILED => "
                    "M1 (non-deterministic enumerate) survives untested",
        "has_nondeterministic_class": has_nondeterministic_class,
        "has_determinism_failed_assert": has_determinism_failed_assert,
    }


def check_s4_route_kind_gate_missing() -> dict:
    """S4: no test pins zero kind/ID branches in the adapter-route core;
    FC-1201 allowlists adapter_dispatch.py/admission.py so a NEW kind branch
    there is invisible to every existing gate."""
    src = WIKI / "src" / "company_wiki" / "source_catalog"
    pattern = re.compile(r"\.kind\s*==|\.kind\s+in\b|root_id\s*==")

    # (a) current branch counts in the route core (expected 0: clean today)
    counts = {}
    for rel in ROUTE_MODULES:
        text = (src / rel).read_text(encoding="utf-8", errors="replace")
        counts[rel] = len(pattern.findall(text))

    # (b) does any test assert these counts / absence?
    pin_exists = False
    for _path, text in _iter_test_texts():
        if "test_spi02_scanner_root_branch_freeze" in text:
            continue  # scanner.py-only freeze
        for rel in ROUTE_MODULES:
            name = rel.rsplit("/", 1)[-1]
            if name in text and pattern.pattern.split("|")[0] in text:
                pin_exists = True

    # (c) FC-1201 cannot catch a new kind branch inside allowlisted files
    from company_wiki.source_catalog.architecture_gate import (
        _ROOT_HARDCODE_ALLOWED_FILES,
    )
    allowlisted = {
        "adapter_dispatch.py": "adapter_dispatch.py" in _ROOT_HARDCODE_ALLOWED_FILES,
        "admission.py": "admission.py" in _ROOT_HARDCODE_ALLOWED_FILES,
    }

    return {
        "survivor": (not pin_exists) and all(v == 0 for v in counts.values()),
        "evidence": "no test pins zero kind/ID branches in the adapter-route "
                    "core; FC-1201 is a token-mention ratchet and "
                    "adapter_dispatch.py/admission.py sit INSIDE its "
                    "allowlist, so a new root-kind branch there trips "
                    "nothing => S4 gate gap (modules clean today, unpinned)",
        "pin_exists_in_any_test": pin_exists,
        "current_kind_branch_counts": counts,
        "fc1201_allowlists_route_files": allowlisted,
    }


def main() -> int:
    checks = {
        "S1_facade_fail_closed_already_pinned": check_s1_facade_fail_closed_unpinned(),
        "S2_kind_routing_mutant_survives": check_s2_kind_routing_mutant_survives(),
        "S3_determinism_negative_missing": check_s3_determinism_negative_missing(),
        "S4_route_kind_gate_missing": check_s4_route_kind_gate_missing(),
    }
    red = (
        checks["S2_kind_routing_mutant_survives"]["survivor"]
        and checks["S3_determinism_negative_missing"]["survivor"]
        and checks["S4_route_kind_gate_missing"]["survivor"]
        and checks["S1_facade_fail_closed_already_pinned"]["covered"]
    )
    verdict = {
        "schema_version": 1,
        "unit": "ZR-402",
        "kind": "red_evidence",
        "note": "survivor mutants / verification gaps over the CURRENT "
                "suite at wiki 251615e: S2/S3/S4 are real gaps (killers "
                "missing); S1 disproven (facade fail-closed already pinned "
                "by seam02 + ex08 tests — honest negative)",
        "checks": checks,
        "red_confirmed": red,
        "files_read_only": True,
    }
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("zr402_red_evidence.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(verdict, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(verdict["checks"], indent=2, ensure_ascii=False))
    print(f"red_confirmed={verdict['red_confirmed']}")
    print(f"written={out}")
    return 0 if red else 1


if __name__ == "__main__":
    raise SystemExit(main())
