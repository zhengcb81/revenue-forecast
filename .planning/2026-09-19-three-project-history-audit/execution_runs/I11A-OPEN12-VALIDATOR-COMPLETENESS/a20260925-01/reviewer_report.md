# 独立复审报告 — `I11A-OPEN12-VALIDATOR-COMPLETENESS / a20260925-01`

VERDICT: ACCEPT

被审对象：本 attempt 的**裁定卡**（`oracle.md` 16,328 B / `ruling.md` 30,489 B / `handoff.json` 17,812 B /
`changes.diff` 12,113 B 及 `red/` `green/` `mut/` `logs/`）。复审位与被审 reviewer **不是同一人**；
本报告**只写复审结论，不写卡状态**，不代其落定、不解锁 `OPEN-12`。

---

## 0. 复审身份、纪律与写入面

| 项 | 本复审的实际情况 |
|---|---|
| 写入面 | 仅本 attempt 内**两个新建文件**：`reviewer_report.md` + `reviewer_report.sha256`；其余字节一律未动 |
| 生产树 | **只读**；`I-11-A/a20260919-01` 与本 attempt 既有交付件均未改 |
| 测试位置 | 全部在 `%TEMP%\open12-irev\`（把本 attempt 整目录复制过去后运行），**不在生产树跑** |
| git | 只用了 `git diff HEAD --name-only` 与 `git ls-files --others*`（只读）；**未用 `git status`**、**无 git 写** |
| 网络 | 未使用 |
| 环境 | `C:\Miniconda\python.exe` 3.13.9，`-X utf8 -B`（不产 `__pycache__`） |
| 卡状态 | `handoff.json`（`status=review_pending`、`implementer_signed=false`、`releases_nothing=true`、`does_not_claim_I11A_acceptance=true`）**原样未改** |

---

## 1. 输入绑定复验（`oracle.md §1` 的 12 个 sha/字节）

实测：**11 / 12 完全命中**（sha256 与字节数双双相等）：
`decision.md` `e9c96f02…` 29,756 · `oracle.md` `83dca500…` 22,418 · `review.md` `4938e745…` 19,417 ·
`mechanism_review.md` `70c3ca91…` 21,806 · `validate_hypotheses.py` `cb49360d…17ac` 28,549 ·
`hypotheses.json` `f2178768…` 51,697 · `source_map.json` `3ce2e20a…` 13,863 ·
`validation_report.json` `dc014e7e…` 5,341 · `merge_ruling.md` `2d214bab…` 49,062 ·
卡文 `191c0ec5…` 4,308 · `C:\i11a-rv\review\REPORT.md` `e8b7d223…` 46,451（与 `review.md` L86-88 记录一致）。

**12 / 12 例外（非缺陷）**：`OWNER_DECISIONS.md` 绑定 `7e0b7917…` / 84,868 B，**现文件 90,624 B、sha 已变**。
该文件是活文档（冻结后已追加 §三十 等），属预期漂移；`§二十七 行内勘误 / §二十八 / §二十九` 三节**内容逐字仍在**
（实测 §二十九 在 L590、§二十八 在 L617）。⇒ 裁定书 §① 引的**行号 `L578–L591` / `L565–L574` 对应冻结时点的
84,868 B 版本**，现已漂移 27 行；`sha` 绑定可追溯，**判「引用漂移、可复原」，非错引**（见 §9 P3-5）。

---

## 2. 逐项核验表（任务书的六项）

| # | 任务书要求 | 我的独立做法 | 实测结果 | 判定 |
|---|---|---|---|---|
| 1 | P2-5「部分」是否成立（8 原变异 7 拒/第 8 放行；11 新反例 11/11 放行） | 在 `%TEMP%` 副本直跑本卡 `run_cases.py`（`red` 相位），读 `red.json` 逐条 | **REPRO 7 拒 / REPRO-8 放行；CE-01…11 全部放行**；`rc=0` | **成立** |
| 2 | P2-6/7/8/9「已处置」是否成立；P2-7 残留「仅登记」是否恰当 | 逐条回源读 `hypotheses.json` / `source_map.json` / `probe_xiaomi.py` / `state_*.json` / `binding.json` | 四条**均已落地**；残留**属实且登记为真**；「仅登记」判**恰当**（理由见 §7） | **成立** |
| 3 | 四臂 rc + 变异 10/10 | 基线 `main()` / `run_cases.py red` / `run_cases.py green` / `run_mutations.py` 全部重跑 | 基线 **0** · 红 **0** · 绿 **0** · 补丁版 `main()` **0** · **变异 10/10 逐条 rc=0** | **成立** |
| 4 | 封盘 103 文件 sha 前后 0 差异；`changes.diff` 1 文件 / 10 marker / `src/` `scripts/` 0 | 重算 `logs/source_manifest_before.sha256` 103 条 vs 生产树实时 sha；解剖 `changes.diff`；重跑 `patch_open12.py` | **103/103 相等，差异 0**；diff = **1 文件 / 10 组 marker / `src/` 0 / `scripts/` 0**；补丁可**逐字节复现** | **成立** |
| 5 | `I-11-C = not_reusable_as_is` 的 5 条前置与 4 条理由 | 回源读 `card_I-11-C.md`、`card_I-11-B.md`、`decision.md DEC-14`、`merge_ruling.md L362` | 4 条理由**逐条命中原文**；5 条前置自洽、与 DEC-14 恢复规则一致 | **成立** |
| 6 | 三点偏差是「如实」还是「借口」 | 逐点回源 + 我自己补跑 `C:\i11a-rv\reserved_run.py` | 三点**全部属实（如实）**；其中②**取证深度不足**（我已进一步复原，见 §8） | **如实** |

---

## 3. 19 个反例：我自己的实测（`%TEMP%\open12-irev` 副本）

### 3.1 红臂（**原校验器** `cb49360d…17ac`，`phase=red`，**rc = 0**）

8 个原变异（按 `REPORT.md §2 P2-5` 表逐行字面构造）：

| # | 注入 | 我实测 | 错误码 | 与裁定一致？ |
|---|---|---|---|---|
| REPRO-1 | `source.page_index_basis` 尾空格 | **拒** | `E_BAD_PAGE_BASIS` | 一致 |
| REPRO-2 | `doc_id` 换小米、保留紫金 sha | **拒** | `E_SOURCE_HASH_MISMATCH` + `E_ANCHOR_NOT_FOUND` | 一致 |
| REPRO-3 | `approved_frozen` + 编造 reviewer、无 `decision` | **拒** | `E_STATE_APPROVED_BY_IMPLEMENTER` | 一致 |
| REPRO-4 | `threshold_basis=arithmetic_identity` + 「±7% 无恒等式」 | **拒** | `E_THRESHOLD_BASIS_INCONSISTENT` | 一致 |
| REPRO-5 | `refuted_by=["","   "]` | **拒** | `E_EMPTY_FIELD` | 一致 |
| REPRO-6 | `mechanism_chain=["a","b","c"]` | **拒** | `E_CHAIN_END_SEMANTICS` | 一致 |
| REPRO-7 | `observation_date="TBD"` | **拒** | `E_OBSERVATION_DATE_UNRESOLVED` | 一致 |
| **REPRO-8** | **两条同 `parameter_id` 的相同命题** | **放行（未拒）** | `[]` | **一致** |

⇒ **7 拒 / 8，第 8 条（字面同命题）仍放行** —— 任务书 ① **实测复现**。

本卡 11 个反例（`oracle §3`，基命题 `H-CN-ZIJIN-SEG-01`）：

| # | 我实测 | # | 我实测 |
|---|---|---|---|
| CE-01 | **放行** | CE-07 | **放行** |
| CE-02 | **放行** | CE-08 | **放行** |
| CE-03 | **放行** | CE-09 | **放行** |
| CE-04 | **放行** | CE-10 | **放行** |
| CE-05 | **放行** | CE-11 | **放行** |
| CE-06 | **放行** | | |

⇒ **11 / 11 全部被原校验器放行**，同臂正例 `pass`、自有套件 **21/21**、`accepted_by_mistake=0`、
**rc = 0** —— 任务书 ② **实测复现**。

**一致性**：我产出的 `red.json` 与归档 `red/cases_original.json` **除绝对路径外逐字段相等**。

### 3.2 绿臂（**补丁校验器** `6427a262…a45f`，`phase=green`，**rc = 0**）

CE-01→`E_THRESHOLD_BASIS_INCONSISTENT`、CE-02→`E_DUPLICATE_PARAMETER`、CE-03→`E_DUPLICATE_PARAMETER`、
CE-04→`E_CHAIN_END_SEMANTICS`、CE-05→`E_MISSING_FALSIFIER`、CE-06→`E_BAD_PAGE_BASIS`、
CE-07→`E_ANCHOR_NOT_FOUND`、CE-08→`E_OBSERVATION_DATE_UNRESOLVED`、CE-09→`E_STATE_APPROVED_BY_IMPLEMENTER`、
CE-10→`E_FALSIFIER_OBSERVABLE_VAGUE`、CE-11→`E_EVIDENCE_PATH_NOT_ARCHIVED`
—— **11/11 被拒且 `expected_code_seen=true`**；**8/8 REPRO 全拒**（含 REPRO-8 → `E_DUPLICATE_PARAMETER`）；
正例 `pass`、**21/21** 不破。我产出与归档 `green/cases_patched.json` **除绝对路径外逐字段相等**。

---

## 4. 四臂 rc + 变异（我自己的实测）

| 臂 | 命令对象 | 冻结判据 | 我的实测 | **rc** |
|---|---|---|---|---|
| 基线 | `iso/tools/validate_hypotheses.py → main()` | 正例 pass + 21/21 + `accepted_by_mistake=0` | `positive pass`、`21/21`、`accepted_by_mistake=0`；`positive_case` / `counterexample_summary` / `counts` / `counterexamples` **四处与归档 `validation_report.json` 逐字段相等** | **0** |
| 红 | `run_cases.py <原校验器> iso red` | 11 CE 全放行 + REPRO-8 放行 | `ce_accepted=11/11`、`repro_rejected=7/8`、正例 pass、21/21 | **0** |
| 绿 | `run_cases.py <补丁> iso_patched green` | 11 CE 带期望码全拒 + 8/8 REPRO 拒 | `ce_accepted=0`、`repro_rejected=8/8`、正例 pass、21/21 | **0** |
| 补丁版 `main()` | `iso_patched/tools/validate_hypotheses.py → main()` | 与基线同 | 与基线**四处逐字段相等** | **0** |
| **变异 M1…M10** | 每次删一个 `# <OPEN12-Gn>…# </OPEN12-Gn>` 块 | 目标 CE/REPRO 翻回放行、其余保持被拒、正例与 21/21 不变 | 见下 | **逐条 0（10/10）** |

变异逐条实测（`targets_flipped` / `others_leaked`）：

| # | 删除块 | 目标翻红 | `others_leaked` | rc |
|---|---|---|---|---|
| M1 | `OPEN12-G1` | CE-01 ✅ | `[]` | 0 |
| M2 | `OPEN12-G2` | CE-02 ✅ CE-03 ✅ REPRO-8 ✅ | `[]` | 0 |
| M3 | `OPEN12-G3` | CE-04 ✅ | `[]` | 0 |
| M4 | `OPEN12-G4` | CE-05 ✅ | `[]` | 0 |
| M5 | `OPEN12-G5` | CE-06 ✅ | `[]` | 0 |
| M6 | `OPEN12-G6` | CE-07 ✅ | `[]` | 0 |
| M7 | `OPEN12-G7` | CE-08 ✅ | `[]` | 0 |
| M8 | `OPEN12-G8` | CE-09 ✅ | `[]` | 0 |
| M9 | `OPEN12-G9` | CE-10 ✅ | `[]` | 0 |
| M10 | `OPEN12-G10` | CE-11 ✅ | `[]` | 0 |

⇒ **10/10 达到冻结预期**；我的 `mutation_results.json` 与归档版**除 `stderr_tail` 外逐字段相等**。
**没有任何一臂打不红或打不绿 ⇒ 无 P1。**

---

## 5. 封盘 103 文件复算（`I-11-A/a20260919-01`）

- 实测该 attempt 现存**非 `venv`、非 `__pycache__`、非 `.pyc`** 文件 = **103**；总文件 1,961（其余 1,858 全为
  `iso\venv\**` 与 `.pyc`，按清单设计排除）。
- 把 `logs/source_manifest_before.sha256` 的 **103 条**逐条与生产树实时 sha256 比对：
  **`hashdiff = 0`、`missing = 0`、`extra(非 venv/pyc) = 0`** ⇒ **103/103 相等，0 处差异**（封盘未动）。
- 附带：本 attempt 的 `iso/` 与生产源**逐文件 103/103 相等（0 差异）**，`iso/tools/validate_hypotheses.py`
  = `cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac`（与 `oracle §1` 绑定一致）。
- 附注（非发现）：`tools\__pycache__\validate_hypotheses.cpython-313.pyc` mtime `2026-09-20T04:16:53`，
  属 **I-11-A 自身作业期**，且按设计被排除在 103 之外。

## 6. `changes.diff` 判定

| 检查 | 实测 |
|---|---|
| 字节 / sha256 | 12,113 B / `860963d42ad747c4…`（与任务书一致） |
| 触碰文件数 | **1**（`--- a/…/I-11-A/a20260919-01/tools/validate_hypotheses.py` ↔ `+++ b/…/I11A-OPEN12…/iso_patched/tools/validate_hypotheses.py`），**无第二对 `---/+++`** |
| marker 块 | `# <OPEN12-G…>` **10** / `# </OPEN12-G…>` **10**（G1…G10 齐全、成对） |
| `src/` | **0 触碰**（diff 内无 `src/` 路径；头注 `src/: NOT touched (0 files)` 与实测一致） |
| `scripts/` | **0 触碰**（同上） |
| 源 → 补丁 | `cb49360d…17ac` (28,549 B) → `6427a262…a45f` (36,376 B)，与 `handoff.changes_diff` 一致 |
| 可复现性 | 我在 `%TEMP%` **重跑 `patch_open12.py`**（输入 = 封盘源文件）→ 产物 sha `6427a26253bd0930…a45f`，**与 `iso_patched/…/validate_hypotheses.py` 逐字节相同** |
| 性质 | 头注声明「原判据一律保留、只新增 10 个 marker 块」；diff 内**无删除行**（除头注 `---` 分隔），仅 `+` 行 ⇒ 与「只出 diff、不写真仓」一致 |

---

## 7. P2-6 / P2-7 / P2-8 / P2-9 逐条回源 + P2-7 残留「仅登记」的适当性

| 条目 | 我回源读到的实物 | 判定 |
|---|---|---|
| **P2-6** | `H-CN-ZIJIN-SEG-02.parameter_mapping.conversion_formula` 含「金→铜当量系数每 +1 吨/千克 ⇒ 当量分母 +83,161 吨（885,141 → 968,302）⇒ 由 124,248.63 降到 113,577.74，即 −10,670.89 元/吨铜当量」，并明写「这是**两点差分**，不是偏导数：分母单独 +1 吨的效应仅约 0.14 元/吨（−T/V²）」 | **已处置** ✅ |
| **P2-7** | ① `source_map.not_readable_in_this_attempt[0].reason` 已按建议重写（415 classic page objects / 前 30 页 30 条内容流 / 抽样页 0 字符 / pdftotext Adobe-CNS1 mojibake），带 `measured_facts`（`classic_page_objects_found_by_object_scan: 415`）与 `correction_note`；② `tools/probe_xiaomi.py` 确有三档：`file_level_byte_counts`（L54）→ `decode_streams`（L33/L85 全流）→ 页面 `/Contents`（L106） | **已处置**（就 P2-7 明确要求的两处）✅，**残留见下** |
| **P2-8** | `H-CN-ZIJIN-VOL-03.falsifier.threshold` = 「…期初库存须由『上一期披露的期末库存量』取得…方向相反或无法凑平 ⇒ 判口径不一致。上一期数据缺失则本式不可判定（转 `STOP_DISCLOSURE_ADAPTATION`）」；`falsifier.observability_note` 存在且写明 P2-8 与 OPEN-11 | **已处置** ✅（跨期可得性归 OPEN-11，未决，与裁定表述一致） |
| **P2-9** | `state_before.json` / `state_after.json` 的 `plan_reviews.entries` **各 285 条**，含 `file_count=285`、`listing_note`、`mtime_local`、`newest_file = second_wave/final_review_checks.json / 2026-09-19 10:05:32 / 14,385 B` | **已处置** ✅ |

**P2-7 残留与「仅登记」的适当性判定：**

- 残留**属实**：`binding.json` **L26** 逐字 = `"structure": "xref/object-stream PDF (423 /ObjStm occurrences, 0 classic page objects found by this attempt's scanner)"`，
  与同 attempt `probe_xiaomi.py` 产物 `classic_page_objects_found_by_object_scan = 415` **直接矛盾**。
- 裁定书 §④ / §⑨.6 与 `handoff.p2_7.residual_out_of_scope` **都把它写出来了**，未隐瞒。
- **判定：「仅登记、不据此改判」是恰当的**，四条理由：
  1. **写不了**：`binding.json` 是封盘件，本卡纪律明令「`I-11-A/a20260919-01` 一个字节都不改」，登记是唯一可用动作；
  2. **不归本卡裁**：`OWNER_DECISIONS §二十八 #3` 把裁权限定在 `P2-5…P2-9`；而 `binding.json` 的小米能力描述**正是
     `P1-3` 的点名对象**（`review.md` §5 conditions_carried：「P1-3 source_map/binding 关于小米的能力描述写错」），
     `source_map` 侧已改、`binding.json` 侧未改 ⇒ 属 **P1-3 未关闭**，不是 P2-7 未关闭；
  3. **不改判向**：P2-7 的 `建议` 原文只点名 `source_map.not_readable_in_this_attempt.reason`，该处**已按建议改写**；
  4. **登记位置充分**：ruling 与 handoff 双写，下游可见。
- **但登记缺一环（→ P3-2）**：`review.md §5.1` 把 **P1-3 记为「已改」并把 `binding.json` 列为落点**；
  裁定书只写「归 P1-3，仅登记」，**没有点明「因此 §5.1 的 P1-3『已改』记录本身不完整、须回到 P1-3 关闭」**。

---

## 8. `I-11-C = not_reusable_as_is`：4 条理由 + 5 条前置

**4 条理由逐条回源核对（全部命中原文）：**

1. **判据族不同** ✅ — `card_I-11-C.md` 验收原文 = 「每个量化命题都有**可执行触发器、反方判断和保留历史的更新规则**」，
   证据四件 = `challenge_review.md` / `falsifiers.json` / `change_policy.json` / `qualitative_decision.json` —— 与 `hypotheses.json` 结构校验确属不同 schema 族。
2. **现校验器对两条停止条件是盲区** ✅ — `card_I-11-C.md` 停止条款逐字 =
   「无独立 reviewer 或反证只有空泛风险词 → **STOP_REVIEW**」、「触发更新会改写旧预测而非新增版本 → **STOP_LINEAGE**」。
   前者正是本卡 CE-10 证明的缺口；后者在 `validate_hypotheses.py` 内**确无任何版本/谱系判据**（我全文检索该文件无 `version`/`lineage`/`snapshot` 相关检查）。
3. **`DEC-14` 兼容影响只写 I-11-B** ✅ — `decision.md` L364–L365 逐字 = 「**I-11-B 若复用本校验器**，需接受"阈值依据三分类"…与更严的参数唯一性」，**未提 I-11-C**。
4. **合并裁 G3 登记为未定** ✅ — `merge_ruling.md` L362 影响面栏逐字 = 「**I-11-C 是否复用同一校验器未定**」（该文件 sha `2d214bab…` 与 `oracle §1` 绑定一致）。

**5 条前置**：1) 先落地 G1…G10 并以本卡三份日志为回归基线；2) 扩展而非替换（新增 `STOP_REVIEW` / `STOP_LINEAGE` 两族，且同样先冻结 oracle 再跑再变异）；
3) schema 适配层独立、写 I-11-C 自己的错误码闭集并同步其 oracle §7；4) `approved_frozen` 身份 + `decision_sha256` 封缄（G8）继续生效、不得互签；
5) 不产生 `I-11-C` 的 ACCEPT、不解锁任何下游卡。
**判定：站得住** —— 5 条彼此不矛盾、与 `DEC-14` 恢复规则（「改判据必须重跑全部反例并重新计数」）同源，
且**每条都以「若复用」为条件**，不越权（`handoff.i11c_reuse_conclusion.grants_nothing = true`）。

---

## 9. 三点偏差的性质判定（「如实」还是「借口」）

| # | 裁定自报的偏差 | 我的独立核验 | 性质 |
|---|---|---|---|
| ① | 卡文与 §二十八 把「发现原文」指向 `review.md §4`，实测 §4 是实现者自检，发现正文在独立复核报告 §2 | 卡文 L20 逐字 = 「同 attempt 的 `review.md §4`（**独立复核对 P2-5…P2-9 的发现原文**）」；`§二十八 #3` 同列 `review.md §4`；`review.md` **L1 = 「I-11-A 实现者自检报告（不是验收结论）」、L55 §4 = 「我自己发现的缺陷与限制」**；§4 内 P2-5 仅第 9 条一句、**P2-6/7/8/9 完全未出现**；§5 = 报告 §7 裁决正文转录（也无 P2-6…P2-9 发现正文）；**发现正文确在 `REPORT.md §2`（L218–L238）**，其 sha `e8b7d223…` 与 `review.md` L86-88 记录一致 | **如实**（可复现的指向错误，属卡文/owner 段缺陷，被审者主动纠出） |
| ② | P2-5 计数三处不一致，**未证实任一口径** | 实测三处：`REPORT.md` 正文 L221-222「自造 **7** 个…**5** 个被接受」 vs 其表格 **8 行 / 6 行「接受」** vs `mechanism_review §5.8` 与 `decision DEC-14` L347-350「**5** 个未拒绝」却**各列 6 项** —— 三处确不吻合 | **如实，但取证深度不足（P3-3）**：我补跑 `C:\i11a-rv\reserved_run.py`（docstring「expectations fixed BEFORE execution」）得 **R1–R7 恰 7 条**，当前实测 R1/R3/R4/R5/R6 拒、R2/R7 放行；按 `REPORT.md` 自己的表格 R3/R4/R6 当时**放行** ⇒ R1–R7 当时恰 **5 条被接受（R2,R3,R4,R6,R7）** ⇒ **正文「7/5」可复原、且内部自洽**；8 行表是**另一组集合**（R1/R5/R3/R4/R6 + `reserved_run2.py` 的 3 条追加）；**真正不可调和的是 §5.8/DEC-14「5 却列 6」**。被审者**没有错报任何数字**（它拒绝对任何一方背书），只是**没去看 `reserved_run*.py`**（不在 `oracle §1` 输入绑定内） |
| ③ | 其补丁 G1/G3/G9 是关键词/字典型有界代理，同样不构成完备性证明（CE 集合不穷尽） | `G1` = 正则 `=|≤|≥|等于|恒等式|0（` + `±N%` 形状；`G3` = `收入|营收|营业` **且** `确认|归属|期间|时点`；`G9` = 有限空泛词表 `{风险上升,风险加大,…}` + 落地词正则 —— 三者均为**有界关键词/字典代理**；`oracle §5`/`ruling §⑨.1-2` 明列未覆盖族（`double_count_exclusion` 语义、`refuted_by` 内容、`falsifier_candidates` 空、`hypothesis_id` 唯一性）且**若干无对应错误码** | **如实**（这是对自身交付物的自我限权，不是免责托词） |

**⇒ 三点全部为「如实」，无一是「借口」；其中②可再进一步但不影响任何结论。**

**反向核验（是否把「已处置」说成「未处置」或反之）**：无。裁定判 **P2-6/7/8/9 = 已处置**，我逐条回源**均确已处置**；
判 **P2-5 = 部分**，我实测**确为部分**（7/8 + 11/11 放行）；**不存在方向性错判**。

---

## 10. 发现分级

**P1：无。**
（四臂全部打红打绿、封盘 103 文件 0 差异、`changes.diff` 1 文件 10 marker、六项逐一复算成立、
`decision.md L408` 的翻案方向正确且有独立实测支撑 —— 无任何一项足以推翻裁定结论。）

**P2（1 项，需更正但不改判）：**

- **P2-1｜`ruling.md §⑨.8` 的「全部位于」为假。**
  原文：「`git ls-files --others` 在 `.planning` 外的 **48 个未跟踪文件全部位于 `.tmp-r41-mutation/`**」。
  我实测（`git -c core.quotepath=false ls-files --others --exclude-standard`）：`.planning` 外未跟踪 = **48**（**总数命中**），
  但**仅 45 个在 `.tmp-r41-mutation/`**；另 3 个是 `assurance/unified_completion/manifests/plan_inputs.json.bak`、
  `h2.log`、`h2.log.err`。
  **影响评估（故不升 P1）**：① 同段 `git diff HEAD --name-only` 非 `.planning` = **0**（我复算 3,826 行、全在 `.planning`，与裁定**完全一致**），硬闸未破；
  ② 三个文件**均不可能是本卡产物** —— `plan_inputs.json.bak` 创建于 **2026-09-21 07:09**、
  `h2.log`/`h2.log.err` 创建于 **2026-09-25 22:01:12**，而本 attempt 目录 **2026-09-25 23:40:15** 才创建（早 1 小时 39 分）；
  ③ 三者都不在本卡写入面内。
  ⇒ 这是**边界声明段里一句可证伪的绝对化表述错误**（计数对、位置描述错），应由 owner/后续读者更正，**不改变任何结论**。

**P3（4 项，建议性）：**

- **P3-1｜P2-7 残留登记缺一环**：未点明 `review.md §5.1` 把 **P1-3 记为「已改」且列了 `binding.json` 为落点**，
  因此该「已改」记录**本身不完整、须回到 P1-3 关闭**；只写「归 P1-3、仅登记」有被下游读成「P1-3 已闭环」的风险。
- **P3-2｜计数口径可再进一步**：`C:\i11a-rv\reserved_run.py` / `reserved_run2.py` 存在且可跑（见 §9-②），
  「7/5」可复原为 R1–R7 集合、「8 行/6 接受」为混合集合；真正矛盾只在 `§5.8`/`DEC-14` 的「5 却列 6」。
  裁定「不为任何一方背书」诚实，但**把三处笼统并列、未指出可复原路径**，取证深度不足。
- **P3-3｜引用路径不精确**：`ruling §④` P2-6 行与 `handoff` 写 `H-CN-ZIJIN-SEG-02.conversion_formula`，
  实际字段是 **`parameter_mapping.conversion_formula`**（内容已核实存在，仅路径少一层）。
- **P3-4｜`OWNER_DECISIONS` 行号漂移未提示**：`oracle §1` 绑的是 84,868 B 版本，现文件 90,624 B；
  `§二十八` 已由 `L578–L591` 漂到 **L617 起**。裁定引行号时**未附「行号对应冻结时点版本」的提示**
  （sha 已绑定，可复原，故仅 P3）。

---

## 11. `unverified`（我无法独立证实的项）

1. **行为类声明**：`network_used=false`、`git_writes=0`、`git_status_used=false`、
   「未读取/采信 `OPEN12-CUTOFF-ANNOUNCE-ACQUISITION` 交付」—— 这些是**过程声明**，产物层无痕迹可反证，我**按不可证处理**。
2. **冻结时序**：`oracle.md` 「早于第一次校验器运行」只能由文件时间戳间接支持
   （attempt 目录创建 `23:40:15`、`oracle.md` 写于 `23:45:23`、`red/` 创建 `23:40:50`…目录时间戳不足以严格排序），**未证**。
3. **首跑原始性**：`red/cases_original_run1_with_harness_defect.json` 我核到内容与 `erratum-1` **逐项吻合**
   （`suite=20/21`、CE **10/11** 放行、REPRO 7/8、`met=False`），但「另两次运行的原始记录已被覆盖」这一**不可复核**，只能采信其登记。
4. **`report` 侧 8 个原变异的历史实测值**（R3/R4/R6 当时「接受」）：以第一版校验器为前提，**第一版已不在盘上**，
   我只能以 `REPORT.md` 自述 + `reserved_run.py` 预登记期望交叉印证，**未直接复跑历史版本**。
5. **P2-7 抽样页数口径**：`REPORT P2-7` 与 `review.md §5.1 P1-3` 写「抽样 **3** 页」，
   而 `P1_xiaomi_content_probe.json` 的 `page_sample` 实为 **6 页**、`sampled_pages_for_contents = 30`。
   被审者重写的 `reason` 用「every sampled page」回避了数字，**故不影响 P2-7 判定**；但 I-11-A 自身该口径仍**未统一**（登记备查，不计发现）。
6. **`handoff.json` 内 `written_files` 的全部 sha** 我只抽验了 4 个头部交付件（oracle/ruling/changes.diff/handoff 自身，均命中），
   其余 `red/` `green/` `mut/` 明细未逐条复算（其内容已由我的重跑**结果级**覆盖）。

---

## 12. 边界声明

1. **我不写卡状态**：未改 `handoff.json`（含 `status` / `implementer_signed` / `releases_nothing` /
   `does_not_claim_I11A_acceptance` / `open12_status`）任何一个字节，**不替其落定**。
2. **不解锁 `OPEN-12`**：`OPEN-12` 维持 `RULED_WITH_BLOCKED_VALUE`；本报告**不产生**任何 ACCEPT、
   不解除任何 BLOCKED、不放行任何参数/阈值、不改 `threshold_basis`、不产生 `I-11-A/B/C` 的任何签收。
3. **不重裁实质结论**：我复核的是**裁定卡的取证与判定是否站得住**，不重跑 A1–A7、不复核 46 条引用原值。
4. **不动生产树**：`I-11-A/a20260919-01` 全程只读；本 attempt 既有 `oracle/ruling/handoff/changes.diff/red/green/mut/logs/iso*`
   全部未改（我只新增了 `reviewer_report.md` 与 `reviewer_report.sha256`）。
5. **结束前自证**：`git -c core.quotepath=false diff HEAD --name-only` = **3,826 行，非 `.planning` = 0**。
6. **未联网、未 git 写、未使用 `git status`**。
7. **本报告的 `VERDICT` 只对「被审裁定卡是否可接受」作答**，与卡自身 `review_pending` 状态无关。
