#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""收尾自查：四件产出的 BOM/LF/JSON 重解析 + 前站只读 sha 复核 + oracle 冻结 sha 复核。"""
import hashlib
import json
import os
import sys

PLAN = ".planning/2026-09-19-three-project-history-audit"
R = os.path.join(PLAN, "execution_runs")
HERE = os.path.join(R, "OPEN5-S5-IND-RULING", "a20260926-01")
WORK = os.path.join(HERE, "_work")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


EXPECTED_READONLY = {
    os.path.join(R, "I11A-OPEN5-ENVOWNER", "a20260924-01", "ruling.md"):
        "2636d463ed58ad0a4ee8a9488feffb14b033bfb4a7c4630c4dcc6d08cf19d5e1",
    os.path.join(R, "I11A-OPEN-IND", "a20260924-01", "ruling.md"):
        "8bc685a4964a7fe64f8590cc7ec0dc93824385b90b9063722ffd34808cab7f4b",
    os.path.join(R, "OPEN5-S5-ACCT-GRADING", "a20260926-01", "oracle.md"):
        "32c28419ef12bf614ea4cb4a5944e3214857dc628a4e3888ec96328992ef93ea",
    os.path.join(R, "OPEN5-S5-ACCT-GRADING", "a20260926-01", "acct_grading.json"):
        "3a5623afb19a19bdf9b83520595980810e41d14072131769639c00c5a69b0eda",
    os.path.join(R, "OPEN5-S5-ACCT-GRADING", "a20260926-01", "s5_acct_report.md"):
        "0bfbedaead34929cdd994e5e1a3660d642d6720a50a9f95c8041ff8f3cb9fd5c",
    os.path.join(R, "OPEN5-S4-DUAL-PATH-VERIFY", "a20260926-01", "dual_path_verify.json"):
        "218a4195bcd72637d8cd48e87c93a39414f392b04b16248d5275f5a48767e46a",
    os.path.join(R, "OPEN5-S4-DUAL-PATH-VERIFY", "a20260926-01", "s4_report.md"):
        "7987f5de4926f0e27e61c90127bd91b04679e496c11ec1eef33143cdcc283221",
    os.path.join(R, "OPEN5-S3-REACQUISITION", "a20260925-01", "provenance.json"):
        "3e44f7e97a74409acc2e1e57f7bc868d85e9e5ba0ef8048cf9212edba70a3d05",
    os.path.join(R, "OPEN5-PEND5A-HK-ACQUISITION", "a20260924-01", "provenance.json"):
        "d06df212d3c2fba7c91cb74dbcceb20a6bf4b1e163e0623a9d3168a507a3f9d1",
    os.path.join(PLAN, "OWNER_DECISIONS.md"): None,  # 只记录现值（未预先登记）
    os.path.join(HERE, "oracle.md"): "549cadfe0c66614b2687da12e094317db9601633718f204ce35ca17de71b07ee",
}


def main():
    fails = []
    files = ["oracle.md", "ind_ruling.json", "s5_ind_report.md", "handoff.json"]
    fmt = {}
    for fn in files:
        p = os.path.join(HERE, fn)
        b = open(p, "rb").read()
        bom = b.startswith(b"\xef\xbb\xbf")
        cr = b.count(b"\r")
        item = {"bytes": len(b), "bom": bom, "cr_count": cr, "sha256": hashlib.sha256(b).hexdigest()}
        if bom:
            fails.append({"bom": fn})
        if cr:
            fails.append({"cr_present": fn, "count": cr})
        if fn.endswith(".json"):
            try:
                json.loads(b.decode("utf-8"))
                item["json_reparse"] = "OK"
            except Exception as e:  # noqa: BLE001
                item["json_reparse"] = str(e)
                fails.append({"json": fn, "err": str(e)})
        fmt[fn] = item

    ro = {}
    for path, want in EXPECTED_READONLY.items():
        got = sha256_file(path)
        ok = (want is None) or (got == want)
        ro[os.path.relpath(path).replace("\\", "/")] = {"sha256": got, "expected": want, "ok": ok}
        if not ok:
            fails.append({"read_only_changed": path, "want": want, "got": got})

    out = {"files": fmt, "read_only": ro, "fails": fails}
    print(json.dumps(out, ensure_ascii=False))
    return 0 if not fails else 3


if __name__ == "__main__":
    sys.exit(main())
