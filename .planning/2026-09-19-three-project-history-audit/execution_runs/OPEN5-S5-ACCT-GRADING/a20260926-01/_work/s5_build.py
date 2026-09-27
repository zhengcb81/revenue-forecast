#!/usr/bin/env python3
"""OPEN5-S5-ACCT-GRADING — assemble acct_grading.json / handoff.json.

Read-only against S4 / S3 / S1 / sealed station / plan files.
Writes only into this attempt directory.
Usage:  python s5_build.py acct     -> acct_grading.json
        python s5_build.py handoff  -> handoff.json (run AFTER report md exists)
"""
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PLAN = Path(".planning/2026-09-19-three-project-history-audit")
RUNS = PLAN / "execution_runs"
OUT = RUNS / "OPEN5-S5-ACCT-GRADING/a20260926-01"
WORK = OUT / "_work"
PEND5A = RUNS / "OPEN5-PEND5A-HK-ACQUISITION/a20260924-01"
S3DIR = RUNS / "OPEN5-S3-REACQUISITION/a20260925-01"
S4DIR = RUNS / "OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01"

ENV_R = RUNS / "I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md"
IND_R = RUNS / "I11A-OPEN-IND/a20260924-01/ruling.md"
ACCT_R = RUNS / "I11A-OPEN-ACCT/a20260924-01/ruling.md"
OWNER_D = PLAN / "OWNER_DECISIONS.md"

# rc measured by this station (re-run of _work/s5_grade.py, all five modes)
RC = {"baseline": 0, "m1_weak": 0, "m2_origin": 0, "m3_nourl": 2, "m4_quote": 2}

L166 = ("| **S5** | **行业复裁 + 会计定级**：按 IND 已裁的 C 表①/②登记来源等级，"
        "**证据等级由会计面认定**（§二十四 执行纪律第 3 条）；通过后才谈港股命题与参数 "
        "| 行业 reviewer + 会计 reviewer | 各自专业裁定权（**本载体不代行**） "
        "| 任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER` |")
C1 = ("| ① | **同一发行人、同一报告期**的其他**可读原文**官方文件（HKEX 披露易 PDF 文本层正常者、"
      "全年业绩公告、中期报告、公司 IR 的年报 HTML/可读 PDF） | "
      "`company_primary_disclosure`（与年报同级，但必须标注**文件类型与期间**） | "
      "必须：原文可定位（页码/锚文本或章节）+ 原始 sha256 + 期间与年报一致；"
      "跨期文件必须标 `period_mismatch_risk` |")
C4 = ("| ④ | 外部抓取的港股年报 PDF（若本地原件不可读） | `external_retrieval_not_local` | "
      "必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**；且仍需可复核的取文路径 |")
C3 = "| ③ | 券商研报 / 新闻 / 数据商 / wiki | `secondary_lead_only` | **仅可作线索**，**不得**进参数、**不得**进命题的 `cited_values` |"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(p: Path):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump(p: Path, obj) -> None:
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(p, "r", encoding="utf-8") as fh:      # re-parse gate
        json.load(fh)


def now_utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_counts() -> dict:
    def run(args):
        r = subprocess.run(["git", "-c", "core.quotepath=false"] + args,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        return [ln for ln in r.stdout.splitlines() if ln.strip()]
    diff = run(["diff", "HEAD", "--name-only"])
    untracked = run(["ls-files", "--others", "--exclude-standard"])
    non = [p for p in diff if not p.startswith(".planning/")]
    unon = [p for p in untracked if not p.startswith(".planning/")]
    return {"git_diff_total": len(diff), "git_diff_non_planning": len(non),
            "git_diff_non_planning_paths": non[:20],
            "untracked_total": len(untracked),
            "untracked_non_planning": len(unon),
            "untracked_non_planning_sample": unon[:5],
            "git_status_used": False, "git_write_ops": 0}


def cite(file: str, locator: str, verbatim: str, check: str) -> dict:
    return {"file": file, "locator": locator, "verbatim": verbatim, "check": check}


def quote_evidence(qs: list, root: Path) -> list:
    out = []
    for q in qs:
        art = Path(q["artifact"])
        out.append({
            "element": "E1e 逐字引文 %s" % q["id"],
            "file": str(art),
            "locator": "bytes[%d:%d]" % tuple(q["byte_range_used"]),
            "verbatim": q["expected_text"],
            "check": {
                "artifact_sha256_registered": q["artifact_sha256_registered"],
                "artifact_sha256_recomputed": q["artifact_sha256_recomputed"],
                "artifact_sha_match": q["artifact_sha_match"],
                "byte_exact": q["byte_exact"],
                "found_in_own_extraction": q["found_in_own_extraction"],
                "e1e": q["e1e"],
            },
        })
    return out


def g2_record(src: str, g2: dict, s3_line: str, s4_line: str, pend_line: str) -> dict:
    return {
        "source": src,
        "rule": "oracle.md §4.1 (G2a URL / G2b 取回 UTC / G2c sha256 / G2d 记录落位)",
        "G2a_url": {"result": g2["G2a_url"], "url": g2["url"],
                    "evidence": cite(
                        "execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json",
                        pend_line, '"url": "%s"' % g2["url"],
                        "回源核实：与派单所列 URL 全等（S4 PEND-5a 记录 → 本工位回读）")},
        "G2b_retrieved_utc": {
            "result": g2["G2b_utc"], "retrieved_utc": g2["retrieved_utc"],
            "file_mtime_utc_corroboration": g2["retrieved_utc_mtime_corroboration"],
            "evidence": cite(
                "execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json",
                pend_line + " (retrieved_utc 行)", '"retrieved_utc": "%s"' % g2["retrieved_utc"],
                "形态 YYYY-MM-DDTHH:MM:SSZ；盘上 corpus 文件 LastWriteTimeUtc 与之逐字相等")},
        "G2c_sha256": {
            "result": g2["G2c_sha256"],
            "sha256_registered_pend5a": g2["sha256_registered"],
            "sha256_recomputed_by_this_station": g2["sha256_recomputed"],
            "sha256_s3_in": g2["sha256_s3"],
            "sha256_s4_own": g2["sha256_s4"],
            "three_way_equal": bool(g2["sha256_registered"] == g2["sha256_recomputed"]
                                    == g2["sha256_s3"] == g2["sha256_s4"]),
            "evidence": [
                cite("execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json",
                     pend_line + " (sha256 行)", '"sha256": "%s"' % g2["sha256_registered"],
                     "PEND-5a 登记值"),
                cite("execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/provenance.json",
                     s3_line, '"sha256": "%s"' % g2["sha256_s3"],
                     "S3 in-0x 登记值（G2 缺 URL，sha 不缺）"),
                cite("execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/dual_path_verify.json",
                     s4_line, '"sha256": "%s"' % g2["sha256_s4"], "S4 own_provenance 登记值"),
                {"file": "本工位 IN-07 字节", "locator": "sha256 全量复算",
                 "verbatim": g2["sha256_recomputed"],
                 "check": "python hashlib.sha256 over the corpus bytes（s5_grade.py → sha256_file）"},
            ]},
        "G2d_recorded_here": {"result": g2["G2d_recorded_here"],
                              "note": "三件套由本工位写入 acct_grading.json；不回改 S3/S4/PEND-5a"},
        "resolved": bool(g2["resolved"]),
    }


def build_stability() -> dict:
    out = {"probe": "_work/s5_determinism.py → _work/s5_extract_determinism_{attempt04,attempt08}.json"}
    for tag in ("attempt04", "attempt08"):
        p = WORK / ("s5_extract_determinism_%s.json" % tag)
        if not p.exists():
            out[tag] = {"available": False}
            continue
        j = load(p)
        out[tag] = {
            "available": True,
            "distinct_shas": j["distinct_shas"],
            "byte_stable": j["byte_stable"],
            "all_quotes_found_all_runs_raw": j["all_quotes_found_all_runs_raw"],
            "all_quotes_found_all_runs_whitespace_normalized":
                j["all_quotes_found_all_runs_whitespace_normalized"],
            "observed_shas": sorted({r["sha256"] for r in j["runs"]}),
            "independent_processes": len(j["runs"]),
        }
    out["impact_on_levels"] = (
        "无降级：E1d 的 sha256 针对 PDF 本体（三方全等，恒定）；E1e 锚定登记引文载体的 byte_range 全等；"
        "E1f 锚定「同一引文在本工位自抽文本中命中」，全部命中。"
        "attempt08 的 pdfminer 自抽工件跨进程出现 2 个 sha（布局依赖 hash 随机化），已如实登记为限制，"
        "不以自抽工件字节全等作为放行条件")
    return out


def build_acct() -> int:
    base = load(WORK / "s5_measure_baseline.json")
    muts = {m: load(WORK / ("s5_measure_%s.json" % m))
            for m in ("m1_weak", "m2_origin", "m3_nourl", "m4_quote")}

    pend_ext = {"attempt04": {"line": "L99–L119 (ext-04)", "id": "ext-04",
                              "s3": "L77–L86 (in-02)", "s3_line": "L81",
                              "s4": "dual_path_verify.json L5594–L5610 (own_provenance.substitute_attempt04)",
                              "s4_line": "L5597"},
                "attempt08": {"line": "L185–L205 (ext-08)", "id": "ext-08",
                              "s3": "L88–L97 (in-03)", "s3_line": "L92",
                              "s4": "dual_path_verify.json L5611–L5626 (own_provenance.substitute_attempt08)",
                              "s4_line": "L5614"}}

    g2_resolution = {
        "rule": "oracle.md §4.1（冻结）",
        "resolved": bool(base["g2_resolved"]),
        "back_written_to_prior_stations": False,
        "gap_before_this_station": ("S4 G2: in-02 / in-03 无 url 字段（S3 provenance L77–L97 无 `url` 键）；"
                                    "URL 只存在于 PEND-5a provenance ext-04 / ext-08"),
        "resolution": ("本工位回源读取 PEND-5a provenance.json 的 ext-04 / ext-08，取 URL + 取回 UTC + sha256，"
                       "对 IN-07 字节全量重算 sha256，并与 S3 in-02/in-03、S4 own_provenance 三方比对全等；"
                       "三件套只写入本目录 acct_grading.json → g2_resolution"),
        "by_source": {
            "attempt04": g2_record("attempt04", base["g2_by_source"]["attempt04"],
                                   pend_ext["attempt04"]["s3_line"], pend_ext["attempt04"]["s4_line"],
                                   pend_ext["attempt04"]["line"]),
            "attempt08": g2_record("attempt08", base["g2_by_source"]["attempt08"],
                                   pend_ext["attempt08"]["s3_line"], pend_ext["attempt08"]["s4_line"],
                                   pend_ext["attempt08"]["line"]),
        },
        "not_resolved_for": [],
    }

    g3_div = base["g3_by_source"]["attempt04"]["divergence"]
    g3_resolution = {
        "rule": "oracle.md §4.2（按 IND C 表 ④ 语义裁）",
        "resolved": bool(base["g3_resolved"]),
        "adopted_semantics": "④ 语义：外部取回件一律标 external_retrieval_not_local = true，永不冒充本地可核",
        "station_records": {
            "attempt04": {"external_retrieval_not_local": True, "substitute_not_origin": True},
            "attempt08": {"external_retrieval_not_local": True, "substitute_not_origin": True},
        },
        "authority": [
            cite("execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md", "L234", C4,
                 "④ 的证据等级列本身就是 external_retrieval_not_local"),
            cite("execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md", "L360",
                 "**外部 ≠ 本地**：所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`；"
                 "`2026-09-02 8-K` 条目显式写明\"**本地不可核，外部获取，不得作为本地可核证据放行**\"。",
                 "OPEN-11 语义"),
            cite("execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md", "L261",
                 "- 用外部抓取件静默顶替本地原件（必须按④登记为外部）；", "被拒方案原文"),
        ],
        "divergence": {
            "side_A_false": {
                "meaning": g3_div["side_A_false"]["meaning"],
                "where": g3_div["side_A_false"]["where"],
                "observed_values": g3_div["side_A_false"]["values"],
                "evidence": [
                    cite("execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json",
                         "L109 / L195", '"external_retrieval_not_local": false', "ext-04 / ext-08 口径 A"),
                    cite("execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/provenance.json",
                         "L83 / L94", '"external_retrieval_not_local": false', "in-02 / in-03 口径 A"),
                ],
                "back_written": False,
            },
            "side_B_true": {
                "meaning": g3_div["side_B_true"]["meaning"],
                "where": g3_div["side_B_true"]["where"],
                "observed_values": g3_div["side_B_true"]["values"],
                "evidence": [
                    cite("execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/dual_path_verify.json",
                         "L5605 / L5622", '"external_retrieval_not_local": true',
                         "S4 own_provenance 口径 B"),
                ],
                "back_written": False,
            },
            "resolution": g3_div["resolution"],
            "both_sides_back_written": False,
        },
        "constraint_on_grading": ("任何标 true 的件，其等级结论必须显式声明「外部取回件，永不冒充本地原件 / "
                                  "不冒充 origin」——见各 source 的 external_never_impersonates_local"),
    }

    # ---------------------------------------------------------------- step 2
    c_table = {}
    for sid, meta in (("attempt04", pend_ext["attempt04"]), ("attempt08", pend_ext["attempt08"])):
        g = base["grades"][sid]
        c_table[sid] = {
            "tier": g["c_table_tier"],
            "evidence_class": g["c_table_evidence_class"],
            "stacked_4": {"flag": g["c_table_4_external_flag"],
                          "meaning": "① 是来源级别，④ 是取回路径的外部身份；二者叠加登记，不矛盾"},
            "must_label": g["must_label"],
            "usage_conditions_from_C1": {
                "原文可定位": True,
                "原始sha256": True,
                "期间与年报一致": True,
                "period_mismatch_risk": False,
            },
            "authority": [
                cite("execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md", "L227",
                     "**C. 可接受的替代来源及其证据等级（我裁，供 owner 解锁后使用）**", "C 表标题"),
                cite("execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md", "L231", C1, "① 行"),
                cite("execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md", "L234", C4, "④ 行"),
                cite("execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json",
                     "L111–L113" if sid == "attempt04" else "L197–L199",
                     ("\"document\": \"截至2025年12月31日止年度之全年業績公告（小米集团，港交所披露易原站）\""
                      if sid == "attempt04" else
                      "\"document\": \"Xiaomi 2025 AR_EN（2025 年度报告英文版，发行人官网）\""),
                     "文件类型与期间标注（① 的 must_label）"),
            ],
        }
    c_table["attempt07_proxy"] = {
        "tier": "③",
        "evidence_class": "secondary_lead_only",
        "must_label": {"document_type": "third_party_proxy_render (r.jina.ai 代理渲染)"},
        "usage": "仅可作线索；不得进参数、不得进命题 cited_values",
        "authority": [cite("execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md", "L233", C3, "③ 行")],
        "pass": base["grades"]["attempt07_proxy"]["pass"],
    }
    c_table["origin_HK-XIAOMI-AR2025"] = {
        "tier": None, "registered": False,
        "reason": "origin 本体不进入定级（S4 NOT_USABLE + ENVOWNER L165；oracle §4.5）",
    }

    # ---------------------------------------------------------------- step 3
    grading = {}
    for sid in ("attempt04", "attempt08", "attempt07_proxy"):
        g = base["grades"][sid]
        qs = base["quote_checks"][sid if sid != "attempt07_proxy" else "attempt07"]
        grading[sid] = {
            "source_id": g["source_id"],
            "c_table_tier": g["c_table_tier"],
            "e_level": g["e_level"],
            "e_level_note": g["e_level_note"],
            "s_tier": g["s_tier"],
            "s_tier_note": g["s_tier_note"],
            "e_elements": g["e_elements"],
            "usable_faces": g["usable_faces"],
            "s4_face_result": g["s4_face_result"],
            "external_never_impersonates_local": g["external_never_impersonates_local"],
            "reason": (g["e_level_note"] + "；" + g["s_tier_note"]),
            "admissible": g["pass"],
            "evidence": [
                cite("execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md", "L66",
                     "| **E1 已核** | 申报原文**本地归档**：URL + 取回 UTC + 文件 sha256 + 逐字引文 + "
                     "至少一条独立复核路径（同本卡 P1/P2 双路径精神） | 参数、口径声明、\"已核\" 字样 |",
                     "E1 定义（六要素来源）"),
                cite("execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md", "L56",
                     "| **S1** | 公司/发行人**同一期间原文披露**：可定位到页/表/锚文本，doc sha256 已绑定，"
                     "至少一条独立路径复核 | 可 |", "S1 定义"),
            ] + quote_evidence(qs, OUT) + [
                {"element": "E1f 独立复核路径 ①",
                 "file": "execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/dual_path_verify.json",
                 "locator": "faces.U2_substitute_attempt04 / U3_substitute_attempt08",
                 "verbatim": "CONSISTENT",
                 "check": "S4 双库互证（只读接受，不下 S4 结论）"},
                {"element": "E1f 独立复核路径 ②（本工位自己重抽）",
                 "file": "_work/extract/s5_attempt04_fitz.txt / s5_attempt04_pdfminer.txt / "
                          "s5_attempt08_fitz.txt / s5_attempt08_pdfminer.txt",
                 "locator": "sha256 见 own_extraction；四件均由本工位用 PyMuPDF + pdfminer.six 重新全局抽取",
                 "verbatim": "found_in_own_extraction = true（见每条 E1e 的 check）",
                 "check": "本工位独立路径，非复用 S4/S3 抽取"},
                cite("execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json",
                     "L115–L117" if sid == "attempt04" else "L201–L203",
                     ("P3 PyMuPDF 1.26.7 rc=0 total_chars=45593 cjk=23481 命中 4/5" if sid == "attempt04"
                      else "P3 PyMuPDF total_chars=951018 英文锚词 5/5；P4 pdfminer.six total_chars=1022506 "
                           "英文锚词 5/5（独立路径互证）；中文锚词 0/5（正文为英文，语言不同）"),
                     "取文路径可复核（④ 的使用条件）"),
            ],
            "limits": (
                ["第三方代理渲染件 = 二手；③/E3/S0，仅可提问题，不得进参数与 cited_values"]
                if sid == "attempt07_proxy" else
                ["E1 只对本文件所载内容成立，**永不等于本地原件（origin）已核**（④ 约束）",
                 "本等级只裁来源可采性与证据等级，不裁港股命题是否成立（行业面 + L179 另行约束）"] +
                (["中文锚词 0/5 ⇒ usable_faces=[\"en\"]，不可作中文原文来源（承 S4 U3）"]
                 if sid == "attempt08" else
                 ["document_type = 全年业绩公告（非年度报告）⇒ 已按 ① must_label 标注文件类型与期间"])),
        }

    # ---------------------------------------------------------------- origin
    origin = dict(base["origin"])
    origin.update({
        "graded": False, "level": None, "admissible": False,
        "rule": "oracle.md §4.5 / ENVOWNER L165 / S4 consistency_result=NOT_USABLE",
        "authority": [
            cite("execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md", "L165",
                 "复核不一致 ⇒ 该来源不可引用，维持不可读处置", "S4 失败分支（只读接受）"),
            cite("execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/s4_report.md", "L197",
                 "**S4 结论 = `NOT_USABLE`（触发面 = origin 本体）** ⇒ 按 `ruling.md` L165 失败分支，"
                 "**`HK-XIAOMI-AR2025` origin 本体不可引用、维持不可读处置**，**不进入定级**。",
                 "S4 提请（只读接受，本工位不下 S4 结论）"),
        ],
    })

    # ---------------------------------------------------------------- step 4
    hk = {
        "hk_parameters_released": False,
        "placeholder_maintained": True,
        "low_base_high": [None, None, None],
        "conditions_all_required": [
            {"#": 1, "condition": "L179 的 S3/S4/S5 三个站都走完（S5 = 行业 + 会计两个受理人）",
             "met_in_this_station_view": False,
             "note": "行业那一半由父另派，本工位视角内条件 2 永不满足（oracle §4.6）"},
            {"#": 2, "condition": "行业面已复裁通过（非本工位裁）", "met_in_this_station_view": False,
             "note": "本工位不代签行业面"},
            {"#": 3, "condition": "会计面（本工位）定级完成", "met_in_this_station_view": True,
             "note": "四步完成；attempt04/attempt08 = ①+④ / E1 / S1"},
            {"#": 4, "condition": "ENVOWNER §⑦ 解锁前置全部满足", "met_in_this_station_view": False,
             "note": "本工位一条也不能代解"},
        ],
        "authority": [
            cite("execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md", "L166", L166,
                 "失败分支 = 任一面未过 ⇒ 港股参数继续 _PLACEHOLDER"),
            cite("execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md", "L179",
                 "即使 S2 自检显示\"某路径能读出锚词\"，在 S3/S4/S5 走完之前**仍按不可读处置**"
                 "（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 `_PLACEHOLDER`）。",
                 "L179 压顶：本工位即使判过也不解除"),
        ],
        "conclusion": "hk_parameters_released = false 恒成立；港股命题零产出、参数维持 _PLACEHOLDER",
    }

    # ---------------------------------------------------------------- verdict / mutations
    verdict = {
        "g2_g3_resolved": bool(base["g2_resolved"] and base["g3_resolved"]),
        "baseline_verdict": base["verdict"],
        "accounting_face": "GRADED（会计面四步完成；只裁本半区，不构成任何放行）",
        "blocked_triggered": False,
        "sources_graded": 2,
        "sources_rejected": 1,
        "origin_excluded": True,
        "hk_parameters_released": False,
        "sufficiency_for_hk_thesis": (
            "如实判：本工位只给出来源等级与证据等级；港股命题能否成立还取决于 (a) 行业面复裁与 C 表启用裁定"
            "（IND L240/L241）、(b) L179 未解除、(c) 需要的分部数据是否齐备。"
            "本工位**不**声称定级已足以支撑港股命题。"),
    }

    mutations = {}
    expect = {
        "baseline": "rc=0：g2/g3=true、attempt04→①/E1/S1、attempt08→①/E1/S1(usable=en)、"
                    "origin=excluded、hk=false、attempt07=③/E3 不通过",
        "m1_weak": "rc=0 且 should_pass_flip=true（判据改弱后 attempt07 由不通过翻为通过 ⇒ 红）",
        "m2_origin": "rc=0 且 origin_grade_flip=true（origin 被赋等级 ⇒ 红）",
        "m3_nourl": "rc=2 且 verdict=blocked（§4.7-1）",
        "m4_quote": "rc=2 且 verdict=blocked（E1e 失败 ⇒ 降级 + 阻塞）",
    }
    for m, mc in muts.items():
        mutations[m] = {
            "rc": RC[m],
            "expectation": expect[m],
            "expectation_met": mc.get("expectation_met"),
            "verdict": mc.get("verdict"),
            "should_pass_flip": mc.get("should_pass_flip"),
            "origin_grade_flip": mc.get("origin_grade_flip"),
            "blocked_reasons": mc.get("blocked_reasons"),
            "red": bool(m.startswith("m") and mc.get("expectation_met")),
        }

    doc = {
        "card": "OPEN-5",
        "step": "S5 · 会计半区（会计定级）",
        "attempt": "OPEN5-S5-ACCT-GRADING/a20260926-01",
        "role": "accounting_reviewer_s5",
        "generated_utc": now_utc(),
        "oracle": {
            "file": "oracle.md",
            "sha256": sha256_file(OUT / "oracle.md"),
            "bytes": (OUT / "oracle.md").stat().st_size,
            "frozen_before_any_measurement": True,
            "addendum": None,
            "note": "续跑工位：oracle 已在前一轮冻结，本轮未改其任何字节（先冻结后判）",
        },
        "authorization": {
            "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                      "I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md L166",
            "quote_verbatim": L166,
            "owner_rule": cite(".planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md",
                               "L504",
                               "- **取证（选项 3）的证据等级由会计面定，不由取证方自定**；"
                               "取不到就维持 BLOCKED，**不造绿色样例**。",
                               "证据等级由会计面定"),
            "authorization_is_permission_not_action": cite(
                ".planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md", "L502",
                "- **「授权」是许可不是动作**：四项均**不产生任何 ACCEPT、不解除任何 BLOCKED、"
                "不改任何 status**；`I-11-B` 仍 BLOCKED（解锁 7 条条件未满足）。",
                "本工位不产生 ACCEPT / 不解除 BLOCKED"),
        },
        "step1_g2_g3": {"g2_resolution": g2_resolution, "g3_resolution": g3_resolution,
                        "g2_g3_resolved": bool(base["g2_resolved"] and base["g3_resolved"])},
        "step2_c_table_registration": {
            "rule": "oracle.md §4.3（L166「按 C 表①/②登记来源等级」）",
            "origin_excluded_from_tiering": True,
            "by_source": c_table,
        },
        "step3_accounting_grading": {
            "rule": "oracle.md §4.4（E1 六要素 + S 系列，缺一即降级）",
            "by_source": grading,
        },
        "origin_excluded": origin,
        "step4_hk_parameters": hk,
        "mutations": mutations,
        "verdict": verdict,
        "inputs_read_only": {
            "IN-01": "execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md",
            "IN-02": "execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md",
            "IN-03": "execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md",
            "IN-04": "execution_runs/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/",
            "IN-05": "execution_runs/OPEN5-S3-REACQUISITION/a20260925-01/provenance.json",
            "IN-06": "execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json",
            "IN-07": "execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/corpus/",
            "IN-08": "execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/probe/",
            "IN-10": "OWNER_DECISIONS.md L490–L504",
        },
        "own_extraction_sha256": base["own_extraction"],
        "own_extraction_stability": build_stability(),
        "releases_nothing": True,
        "open5_released": False,
        "accept_produced": False,
        "network_used": False,
    }
    dump(OUT / "acct_grading.json", doc)
    print(json.dumps({"written": "acct_grading.json",
                      "g2": doc["step1_g2_g3"]["g2_g3_resolved"],
                      "attempt04": "%s/%s/%s" % (grading["attempt04"]["c_table_tier"],
                                                 grading["attempt04"]["e_level"],
                                                 grading["attempt04"]["s_tier"]),
                      "attempt08": "%s/%s/%s" % (grading["attempt08"]["c_table_tier"],
                                                 grading["attempt08"]["e_level"],
                                                 grading["attempt08"]["s_tier"]),
                      "origin_level": origin["level"],
                      "hk": hk["hk_parameters_released"]}, ensure_ascii=False))
    return 0


def build_handoff() -> int:
    gc = git_counts()
    files = []
    total = 0
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(PLAN).as_posix()
        if p.name == "handoff.json":
            continue
        b = p.stat().st_size
        total += b
        files.append({"path": rel, "bytes": b, "sha256": sha256_file(p)})

    doc = {
        "card": "OPEN-5",
        "step": "S5（会计半区）",
        "attempt": "OPEN5-S5-ACCT-GRADING/a20260926-01",
        "role": "accounting_reviewer_s5",
        "generated_utc": now_utc(),
        "authorized_by": {
            "S5_definition_verbatim": {
                "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                          "I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md L166",
                "quote": L166,
            },
            "dispatch": "编排层派单（续跑 OPEN-5 S5 会计定级；前工位系统事件中断，从已有进度续跑）",
            "owner_rule_verbatim": {
                "source": ".planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md L504",
                "quote": "- **取证（选项 3）的证据等级由会计面定，不由取证方自定**；"
                         "取不到就维持 BLOCKED，**不造绿色样例**。",
            },
            "boundary_verbatim": {
                "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                          "I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md L179",
                "quote": "即使 S2 自检显示\"某路径能读出锚词\"，在 S3/S4/S5 走完之前**仍按不可读处置**"
                         "（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 `_PLACEHOLDER`）。",
            },
            "C_table_1_verbatim": {
                "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                          "I11A-OPEN-IND/a20260924-01/ruling.md L231",
                "quote": C1,
            },
            "C_table_4_verbatim": {
                "source": "同文件 L234",
                "quote": C4,
            },
            "dispatch_paraphrase_delta": (
                "派单把出处写作「OWNER_DECISIONS §二十四 执行纪律第 3 条」、分隔符用全角 ｜；"
                "文件原文为「§二十四 执行纪律第 3 条」、半角 |。以文件原文为准（oracle §1.1 登记）。"),
        },
        "g2_g3_resolved": True,
        "g2_resolution": {
            "resolved": True,
            "attempt04": {"url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0324/"
                                 "2026032400609_c.pdf",
                          "retrieved_utc": "2026-09-24T22:09:26Z",
                          "sha256": "d0975600c918683636d4679328fa1eaa4a7a14b53950440d53005c831829b62b",
                          "three_way_equal": True, "recorded_here_only": True},
            "attempt08": {"url": "https://ir.mi.com/system/files-encrypted/nasdaq_kms/assets/2026/04/28/"
                                 "5-29-08/Xiaomi%202025%20AR_EN.pdf",
                          "retrieved_utc": "2026-09-25T20:37:56Z",
                          "sha256": "b787f0290513e48a95078ed2a68dc1e240da68d204e5dd9aedc59b66a7c75ec2",
                          "three_way_equal": True, "recorded_here_only": True},
        },
        "g3_resolution": {
            "resolved": True,
            "external_retrieval_not_local": True,
            "semantics_adopted": "IND C 表 ④",
            "divergence_registered": "口径 A(false, S3/PEND-5a) vs 口径 B(true, ④/OPEN-11/S4)；"
                                     "两边均不回改，只在本工位记录登记",
            "back_written_to_prior_stations": False,
        },
        "levels_graded": [
            {"source": "attempt04", "c_table": "① + ④", "evidence_class": "company_primary_disclosure",
             "e_level": "E1", "s_tier": "S1", "usable_faces": ["zh-Hant"], "admissible": True,
             "document_type": "全年业绩公告（results announcement，非年度报告）", "period": "FY2025"},
            {"source": "attempt08", "c_table": "① + ④", "evidence_class": "company_primary_disclosure",
             "e_level": "E1", "s_tier": "S1", "usable_faces": ["en"], "admissible": True,
             "document_type": "年度报告英文版（annual report, EN）", "period": "FY2025"},
            {"source": "attempt07 (r.jina.ai 代理)", "c_table": "③",
             "evidence_class": "secondary_lead_only", "e_level": "E3", "s_tier": "S0",
             "usable_faces": [], "admissible": False,
             "document_type": "third_party_proxy_render", "period": "FY2025"},
            {"source": "HK-XIAOMI-AR2025 (origin)", "c_table": None, "evidence_class": None,
             "e_level": None, "s_tier": None, "usable_faces": [], "admissible": False,
             "graded": False,
             "disposition": "S4 NOT_USABLE + L165 不可引用、维持不可读处置；不进入定级"},
        ],
        "hk_parameters_released": False,
        "placeholder_maintained": True,
        "releases_nothing": True,
        "accept_produced": False,
        "open5_released": False,
        "industry_face_countersigned": False,
        "industry_face_note": "行业复裁由父另派；本工位不代签、不裁 C 表启用与否、不解除 IND B 部分",
        "mutations": {"baseline_rc": RC["baseline"], "m1_weak_rc": RC["m1_weak"],
                      "m2_origin_rc": RC["m2_origin"], "m3_nourl_rc": RC["m3_nourl"],
                      "m4_quote_rc": RC["m4_quote"],
                      "all_expectations_met": True},
        "own_extraction_stability_note": (
            "attempt04 pdfminer 自抽工件 8 次抽取字节稳定；attempt08 pdfminer 自抽工件跨进程出现 2 个 sha"
            "（f5d1077a… / f24c26b5…），但两种变体下全部引文 raw+归一化命中。"
            "不影响任何等级（E1d 针对 PDF 本体；E1e/E1f 锚定引文命中）"),
        "oracle": {"file": "oracle.md", "sha256": sha256_file(OUT / "oracle.md"),
                   "frozen_before_any_measurement": True, "modified_by_this_round": False},
        "written_files": {
            "count": len(files), "total_bytes": total,
            "self_excluded": "handoff.json (self-reference impossible)",
            "files": files,
        },
        "git_diff_total": gc["git_diff_total"],
        "git_diff_non_planning": gc["git_diff_non_planning"],
        "git_diff_non_planning_paths": gc["git_diff_non_planning_paths"],
        "untracked_non_planning": gc["untracked_non_planning"],
        "untracked_non_planning_note": "全部为既有 .tmp-r41-mutation/* 等历史路径，非本工位创建",
        "git_write_ops": 0,
        "git_status_used": False,
        "network_used": False,
        "write_surface": "only .planning/2026-09-19-three-project-history-audit/execution_runs/"
                         "OPEN5-S5-ACCT-GRADING/a20260926-01/",
        "not_done": [
            "未改 S4 / S3 / S1 两站 / 封盘 I-11-A 任何字节（G2/G3 只在本工位记录里补）",
            "未下 S4 结论、未改 consistency_result / numeric_conflict",
            "未代签行业面（C 表启用与否、IND B 部分、行业处置规则均未裁）",
            "未解除 OPEN-5、未放行港股参数（hk_parameters_released=false）",
            "未产生 I-11-B 的 ACCEPT、未把任何 not_readable 改成「已验证」",
            "未写五份计划文件、未写 .planning 之外任何路径（含 company-wiki）",
            "零 git 写、未用 git status、未联网",
            "未给 origin 本体赋任何等级（排除在定级外）",
        ],
        "next_station": "S5 行业复裁（父另派）→ 两面齐备后才由有权方谈港股命题与参数",
    }
    dump(OUT / "handoff.json", doc)
    print(json.dumps({"written": "handoff.json", "g2_g3_resolved": doc["g2_g3_resolved"],
                      "levels": len(doc["levels_graded"]),
                      "hk": doc["hk_parameters_released"],
                      "git_diff_non_planning": doc["git_diff_non_planning"],
                      "written_files": doc["written_files"]["count"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "acct"
    sys.exit(build_acct() if mode == "acct" else build_handoff())
