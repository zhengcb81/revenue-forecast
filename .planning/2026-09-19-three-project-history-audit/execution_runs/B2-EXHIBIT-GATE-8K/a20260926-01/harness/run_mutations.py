"""B2 mutation runner: prove every frozen oracle criterion actually bites.

Each mutation is applied ONLY to the iso copy, run once, archived, and reverted.
Exit code = number of mutations whose observed result did NOT match the oracle
expectation (0 == all mutations behaved as predicted).

M0  restore both iso files to the product pre-image  -> both harnesses red
M1  dayu gate back to {"6-K"}                        -> dayu G1 red
M2  drop one shared exhibit-branch line (6-K path)   -> dayu G3/G4 red
M3  adapter gate widened to {"6-K","8-K"}            -> adapter A4 red
M4  adapter exhibit matcher made tautological        -> adapter A1 + A5 red
M5  adapter _INCLUDE_EXHIBITS = False                -> adapter A1 + A6 red
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
DAYU_ISO = ATTEMPT / "iso" / "dayu_repo" / "dayu" / "fins" / "downloaders" / "sec_downloader.py"
CW_ISO = (
    ATTEMPT / "iso" / "cw_repo" / "src" / "company_wiki" / "source_catalog" / "dayu_cli_adapter.py"
)
DAYU_PRODUCT = Path(
    r"C:\Users\郑曾波\Projects\dayu-agent\dayu-agent\dayu\fins\downloaders\sec_downloader.py"
)
CW_PRODUCT = Path(
    r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\dayu_cli_adapter.py"
)
HARNESS = ATTEMPT / "harness"
MUT = ATTEMPT / "mutations"
RESULTS = ATTEMPT / "results"

DAYU_NEW = """EXHIBIT_GATED_FORM_TYPES: frozenset[str] = frozenset({"6-K", "8-K"})"""
DAYU_NEW_GATES = """        if include_exhibits and form_type in EXHIBIT_GATED_FORM_TYPES:"""
DAYU_OLD_GATES = """        if include_exhibits and form_type == "6-K":"""

CW_FILTERS = """            if not lowered.endswith((".htm", ".html")):
                continue
            if "dex99" not in lowered and "ex99" not in lowered:
                continue
"""


def drop_line(text: str, needle: str) -> str:
    """Remove exactly one full line (tolerates CRLF or LF source files)."""
    for eol in ("\r\n", "\n"):
        if needle + eol in text:
            return text.replace(needle + eol, "", 1)
    raise RuntimeError(f"line not found for mutation: {needle.strip()[:60]}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_harness(script: str, out_tag: str) -> tuple[int, list[str], str]:
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(HARNESS / script), "check"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    (MUT / f"{out_tag}.stdout.txt").write_text(output, encoding="utf-8")
    failed: list[str] = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.startswith("{") and '"failed_names"' in line:
            try:
                failed = json.loads(line).get("failed_names", [])
            except json.JSONDecodeError:
                failed = []
    return proc.returncode, failed, output


def main() -> int:
    MUT.mkdir(parents=True, exist_ok=True)
    baseline = {"dayu": sha(DAYU_ISO), "cw": sha(CW_ISO)}
    # byte-exact IO: the dayu file is CRLF, the adapter file is LF; text-mode
    # read/write would silently normalize line endings and corrupt the diff.
    dayu_text = DAYU_ISO.read_bytes().decode("utf-8")
    cw_text = CW_ISO.read_bytes().decode("utf-8")
    dayu_preimage = DAYU_PRODUCT.read_bytes().decode("utf-8")
    cw_preimage = CW_PRODUCT.read_bytes().decode("utf-8")

    mutations = [
        {
            "id": "M0",
            "desc": "把两个 iso 文件还原为产品前像（等价于完全撤回本卡改动）",
            "targets": [("dayu", dayu_preimage), ("cw", cw_preimage)],
            "runs": ["dayu", "adapter"],
            "expect_failed_contains": {"dayu": ["G1_8k_exhibit_in_filenames"],
                                       "adapter": ["A1_8k_stages_primary_and_exhibit_only"]},
            "expect_green": {"dayu": ["G3_6k_list_byte_identical"],
                             "adapter": ["A4_6k_result_byte_identical_to_before"]},
        },
        {
            "id": "M1",
            "desc": "dayu 闸门改回 frozenset({'6-K'})（把 8-K 分支改回去）",
            "targets": [("dayu", dayu_text.replace(
                'frozenset({"6-K", "8-K"})', 'frozenset({"6-K"})', 1))],
            "runs": ["dayu"],
            "expect_failed_contains": {"dayu": ["G1_8k_exhibit_in_filenames"]},
            "expect_green": {"dayu": ["G3_6k_list_byte_identical"]},
        },
        {
            "id": "M2",
            "desc": "删掉共享 exhibit 分支里的一行（6-K 走到被改动的共享分支）",
            "targets": [("dayu", drop_line(
                dayu_text,
                "            filenames.extend(pick_form_document_files(index_header_documents, form_type))",
            ))],
            "runs": ["dayu"],
            "expect_failed_contains": {"dayu": ["G3_6k_list_byte_identical"]},
            "expect_green": {"dayu": ["G1_8k_exhibit_in_filenames"]},
        },
        {
            "id": "M3",
            "desc": "adapter 闸门放宽为 {'6-K','8-K'}（让 6-K 也走新复制逻辑）",
            "targets": [("cw", cw_text.replace(
                '_US_EXHIBIT_FORMS = frozenset({"8-K"})',
                '_US_EXHIBIT_FORMS = frozenset({"6-K", "8-K"})', 1))],
            "runs": ["adapter"],
            "expect_failed_contains": {"adapter": ["A4_6k_result_byte_identical_to_before"]},
            "expect_green": {"adapter": ["A1_8k_stages_primary_and_exhibit_only"]},
        },
        {
            "id": "M4",
            "desc": "adapter exhibit 判定恒真（任何 files[] 条目都算 exhibit）",
            "targets": [("cw", cw_text.replace(CW_FILTERS, "", 1))],
            "runs": ["adapter"],
            "expect_failed_contains": {
                "adapter": ["A1_8k_stages_primary_and_exhibit_only"]
            },
            "expect_green": {
                "adapter": ["A4_6k_result_byte_identical_to_before",
                            "A5_10k_result_byte_identical_to_before"]
            },
        },
        {
            "id": "M5",
            "desc": "adapter _INCLUDE_EXHIBITS = False",
            "targets": [("cw", cw_text.replace(
                "_INCLUDE_EXHIBITS = True", "_INCLUDE_EXHIBITS = False", 1))],
            "runs": ["adapter"],
            "expect_failed_contains": {"adapter": ["A1_8k_stages_primary_and_exhibit_only",
                                                   "A6_include_exhibits_flag_gates_8k"]},
            "expect_green": {},
        },
    ]

    report = {"baseline_sha256": baseline, "mutations": [], "mismatch": 0}
    harness_script = {"dayu": "dayu_gate_harness.py", "adapter": "adapter_copy_harness.py"}
    result_file = {"dayu": "dayu_gate_check.json", "adapter": "adapter_copy_check.json"}

    for mut in mutations:
        entry = {"id": mut["id"], "desc": mut["desc"], "runs": []}
        try:
            for which, text in mut["targets"]:
                path = DAYU_ISO if which == "dayu" else CW_ISO
                original = dayu_text if which == "dayu" else cw_text
                if text == original:
                    raise RuntimeError(f"{mut['id']}: mutation did not change {which} text")
                path.write_bytes(text.encode("utf-8"))
            for which in mut["runs"]:
                rc, failed, _out = run_harness(
                    harness_script[which], f"{mut['id']}_{which}"
                )
                shutil.copyfile(
                    RESULTS / result_file[which], MUT / f"{mut['id']}_{which}.json"
                )
                missing = [
                    name
                    for name in mut["expect_failed_contains"].get(which, [])
                    if name not in failed
                ]
                wrongly_red = [
                    name
                    for name in mut["expect_green"].get(which, [])
                    if name in failed
                ]
                ok = rc != 0 and not missing and not wrongly_red
                entry["runs"].append(
                    {
                        "harness": which,
                        "rc": rc,
                        "failed_names": failed,
                        "missing_expected_red": missing,
                        "unexpected_red": wrongly_red,
                        "ok": ok,
                    }
                )
                if not ok:
                    report["mismatch"] += 1
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {exc}"
            report["mismatch"] += 1
        finally:
            DAYU_ISO.write_bytes(dayu_text.encode("utf-8"))
            CW_ISO.write_bytes(cw_text.encode("utf-8"))
            entry["restored_sha256"] = {"dayu": sha(DAYU_ISO), "cw": sha(CW_ISO)}
            entry["restored_ok"] = (
                entry["restored_sha256"]["dayu"] == baseline["dayu"]
                and entry["restored_sha256"]["cw"] == baseline["cw"]
            )
            if not entry["restored_ok"]:
                report["mismatch"] += 1
        report["mutations"].append(entry)
        print(json.dumps({k: entry[k] for k in entry if k != "desc"},
                         ensure_ascii=False))

    report["finished_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (MUT / "mutations.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"mutations": len(report["mutations"]), "mismatch": report["mismatch"]},
                     ensure_ascii=False))
    return report["mismatch"]


if __name__ == "__main__":
    sys.exit(main())
