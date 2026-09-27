#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 handoff.json（写后 json.load 重解析；shas 现算）。用法：
python -B build_handoff.py --git-total 3830 --git-nonplanning 0
"""
import argparse
import datetime
import hashlib
import json
import os

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


def entry(rel, base=HERE):
    p = os.path.join(base, rel)
    return {"path": rel, "bytes": os.path.getsize(p), "sha256": sha256_file(p)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-total", type=int, required=True)
    ap.add_argument("--git-nonplanning", type=int, required=True)
    a = ap.parse_args()

    rc = {}
    for m in ("baseline", "m1_weak", "m2_origin", "m3_nourl", "m4_noseg", "m5_langconflict"):
        with open(os.path.join(WORK, "expect_%s.json" % m), encoding="utf-8") as f:
            e = json.load(f)
        rc[m] = {"rc": e["rc"], "expectation_met": e["expectation_met"]}

    with open(os.path.join(HERE, "ind_ruling.json"), encoding="utf-8") as f:
        ruling = json.load(f)

    work_files = []
    for root, _dirs, files in os.walk(WORK):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, HERE).replace("\\", "/")
            work_files.append({"path": rel, "bytes": os.path.getsize(p), "sha256": sha256_file(p)})
    work_files.sort(key=lambda x: x["path"])

    deliverables = [entry(f) for f in ("oracle.md", "ind_ruling.json", "s5_ind_report.md")]

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    s5_quote = ruling["authorization"]["S5_definition_verbatim"]

    handoff = {
        "schema_version": "open5-s5-ind-handoff-1.0",
        "card": "OPEN-5",
        "step": "S5（行业半区 · 行业复裁）",
        "attempt": "OPEN5-S5-IND-RULING/a20260926-01",
        "role": "industry_reviewer_s5",
        "parent_agent_id": "session-19074bf0-0205-4315-af73-9db57597275a",
        "generated_utc": now,
        "authorized_by": {
            "S5_definition_verbatim": s5_quote,
            "dispatch": "父 agent 派单：OPEN-5 恢复路径 S5 的行业面那一半（会计半区已由 OPEN5-S5-ACCT-GRADING/a20260926-01 交付，"
                        "本工位不代签、不推翻）",
            "c_table_authority_verbatim": ruling["points"][0]["basis_verbatim"]["IND_L241"],
            "c_table_no_enable_verbatim": ruling["points"][0]["basis_verbatim"]["IND_L240"],
            "boundary_verbatim": ruling["authorization"]["boundary_verbatim"],
            "owner_rule_verbatim": ruling["authorization"]["owner_rule_verbatim"],
            "authorization_is_permission_not_action": ruling["authorization"]["owner_rule_verbatim"],
        },
        "c_table_adopted": ruling["c_table_adopted"],
        "c_table_registration": ruling["c_table_registration"],
        "attempt_levels_confirmed": ruling["attempt_levels_confirmed"],
        "points_summary": [
            {"id": p["id"], "topic": p["topic"], "verdict": p["verdict"]} for p in ruling["points"]
        ],
        "industry_face_status": ruling["industry_face_status"],
        "accounting_face_status": "GRADED（只读引用 OPEN5-S5-ACCT-GRADING/a20260926-01；本工位不代签、不改其任何字节）",
        "s4_status_read_only": ruling["s4_read_only"],
        "origin_excluded": ruling["origin"],
        "hk_parameters_released": False,
        "placeholder_maintained": True,
        "low_base_high": [None, None, None],
        "releases_nothing": True,
        "accept_produced": False,
        "open5_released": False,
        "does_not_claim_I11A_acceptance": True,
        "back_written_to_prior_stations": False,
        "mutations": {
            "script": "_work/s5_ind_grade.py",
            "expected_rc_sequence": [0, 0, 0, 2, 2, 2],
            "observed": rc,
            "all_expectations_met": all(v["expectation_met"] for v in rc.values()),
        },
        "verbatim_check": json.load(open(os.path.join(WORK, "verify_quotes.json"), encoding="utf-8")),
        "oracle": {
            "file": "oracle.md",
            "sha256": sha256_file(os.path.join(HERE, "oracle.md")),
            "bytes": os.path.getsize(os.path.join(HERE, "oracle.md")),
            "frozen_before_any_judgement": True,
            "modified_by_this_round": False,
            "addendum": None,
        },
        "written_files": {
            "deliverables": deliverables,
            "work_files_count": len(work_files),
            "work_files_total_bytes": sum(x["bytes"] for x in work_files),
            "work_files": work_files,
            "self_excluded": "handoff.json（自引用不计哈希）",
        },
        "git_diff_total": a.git_total,
        "git_diff_non_planning": a.git_nonplanning,
        "git_diff_non_planning_paths": [],
        "git_write_ops": 0,
        "git_status_used": False,
        "network_used": False,
        "writes_outside_planning": 0,
        "company_wiki_opened": False,
        "five_plan_files_written": False,
        "write_surface": "only .planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-S5-IND-RULING/a20260926-01/",
        "not_done": [
            "未代签会计面：不动 E1/E3/S1/S0、不动 usable_faces、不动 admissible、不重做会计四步、不改会计半区任一字节",
            "未放行港股参数：hk_parameters_released=false、_PLACEHOLDER 维持、low/base/high=[null,null,null]",
            "未解除 OPEN-5、未产生 I-11-B 的 ACCEPT、未新增 approved_frozen",
            "未改 NOT_USABLE、未下 S4 结论、未动 numeric_conflict、未把任何 not_readable 改成「已验证」",
            "未给 origin 赋级（M2 变异体中的 MUTANT 字样仅在 _work 测试产物内）",
            "未回改 S4 / S3 / S1 两站 / 封盘 I-11-A / 会计半区 / I11A-OPEN-IND / I11A-OPEN11-IND 任一字节",
            "未写五份计划文件、未写 .planning 之外任何路径（含 company-wiki，且未打开）",
            "零 git 写、未用 git status、未联网",
        ],
        "registered_for_owner": [
            "L240/L241 读法分歧：行业面采 α（新 attempt 产不出任何可读原文文本才叫『读不出原文』），β（仅指 origin 本体）已登记不采用；两者都不放行参数",
            "派单把 IND C 表出处写成 I11A-OPEN11-IND（实为 I11A-OPEN-IND L227–L234/L240-241/L261/L360），不回改、只登记",
            "attempt08 pdfminer 自抽工件跨进程 2 个 sha：登记为限制，非阻塞；行业面只要求引用绑定登记载体 sha256 + byte_range",
        ],
        "next_station": "两面（会计=完成、行业=PASS）均已出 ⇒ 仍只到 L166『通过后才谈港股命题与参数』；"
                        "参数放行、OPEN-5 解除、I-11-B ACCEPT 一概归有权方按 ENVOWNER §⑦ 另行处理",
        "file_format": {"encoding": "UTF-8", "bom": False, "line_ending": "LF",
                        "json_reparsed_after_write": True},
    }

    out = os.path.join(HERE, "handoff.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(handoff, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(out, "r", encoding="utf-8") as f:
        json.load(f)
    print("wrote", out, os.path.getsize(out))


if __name__ == "__main__":
    main()
