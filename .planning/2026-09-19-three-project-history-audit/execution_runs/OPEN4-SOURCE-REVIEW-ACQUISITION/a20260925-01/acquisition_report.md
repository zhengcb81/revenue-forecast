# OPEN4-SOURCE-REVIEW-ACQUISITION · 受控取证报告（a20260925-01）

- **card**：`OPEN4-SOURCE-REVIEW-ACQUISITION` ｜ **role**：`controlled_acquisition` ｜ **gap**：G2 = `OPEN-4`
- **授权依据（逐字，`OWNER_DECISIONS.md` §二十七 第 1 行 / L558，2026-09-25）**：
  「**1** | **`G2=`OPEN-4`、`G3=`OPEN-12`** 至今未授权未派（合并裁列的授权缺口，**G1 已由 `OPEN-11` 补上**） | **「两条都授权（建议）」** | 派 `OPEN-4`（wiki 来源审核）与 `OPEN-12`（cutoff 后交易所公告取得方式）**受控取证**；**产物只落本计划目录**（同 §二十四 #3 形态）；**不解除任何 BLOCKED、不产生 ACCEPT**；两站交付后**仍须过 MERGE 七条**」
- **配套纪律（逐字，同节 L563–L564）**：「**三票 = 三个许可，不是三个结论**：**不解除 `OPEN-4`/`OPEN-12`/`OPEN-3`/`OPEN-5` 任何 BLOCKED**、**不产生 ACCEPT**、**不改任何 status**、**不授权晋升**。」「**#2 是对 §二十四 L498 的定向取代**，适用范围**仅限「origin 响应字节经 filing-fetch 取回」这一场景**；**其余取证产物仍只落本计划目录**。」⇒ 本工位**不属**该场景，产物只落本 attempt 目录。
- **被测载体**：`execution_runs/T2-SIM-OPEN4-WIKI/a20260922-01/ruling.md`（42,062 B，sha256 `37413f7812bbe4aa21948f0f474a2ceac2ad0f778f1a3c5eb4f6b3af7e1d98bb` = `outward_requests/RESPONSES.md` L5 登记值，逐字符合；owner §十九「全部接受」终确，`OWNER_DECISIONS.md` L437）

---

## 〇、三层分界（先读，决定本报告每一句的效力）

| 层 | 归属 | 本工位 |
|---|---|---|
| **取证层**：来源是否存在、可得、字节可核、引文可验 | 本工位（`controlled_acquisition`） | **只到此层** |
| **规则/审核层**：某条件是否「满足」、回执是否可用、是否可标 signed | **wiki 来源审核 owner**（+ 安全 reviewer 联席面） | **不代判** |
| **定级/放行层**：证据等级、参数放行、BLOCKED 解除 | **会计面 / owner** | **不触碰** |

> 本报告中的「**已证**」= 该条件检验所需的**检验物已取得且字节可核、引文可验**；「**未证**」= 检验物取不到或检验前提不成立。**两者都不等于「该条件已满足」**——那是审核层的判断。

---

## 一、被测「阻断值」是什么（先把 RULED_WITH_BLOCKED_VALUE 的原义摆正）

1. **`RULED_WITH_BLOCKED_VALUE` 的原义**（`I11A-OPEN-MERGE/.../merge_ruling.md` L53 状态取值域 + L125/L201 用法）：**规则面已裁、取值/证据面仍 BLOCKED** —— 例：`OPEN-3`「规则已裁；**证据（E1）BLOCKED**」（L125）。
2. **合并裁状态表不含 `OPEN-4`**：该表只有 OPEN-2 / OPEN-3 / OPEN-5 / OPEN-6（L57-L62）。**`OPEN-4` 在合并裁里是 §⑤ 的授权缺口 G2 行**（L361）。
3. **本工位所测的 OPEN-4 = D-W06 函 A / T2-1「wiki 来源审核」**，其阻断值形态正是「规则已裁、取值仍 BLOCKED」：
   - `4a` 审核方法 **APPROVE**、`4c` 双绑定与失效判定 **APPROVE**（ruling L61/L63）；
   - `4b` reviewer 身份绑定 **CONDITIONAL** —— ruling L62 逐字：「方向已定（角色+具名主体+进程凭据、不可伪造签名链、与函 B **同一套**信任根），但签名链的可核销落地**取决于函 B 信任根出裁且实测存在**，见 §5 条件 C4」；
   - ⇒ **被阻断的那个值 = 「来源审核回执能否被视为已签名/身份可核」**。本工位取证的对象就是该取值所需的来源证据。

### 1.1 ⚠ 编号空间不一致（登记，不代裁）

| 出处 | 该处 `OPEN-4` 指什么 |
|---|---|
| `OWNER_DECISIONS.md` §二十七 L558（本工位授权原文） | 「`OPEN-4`（**wiki 来源审核**）」 |
| `I11A-OPEN-MERGE/.../merge_ruling.md` L361（G2 行） | 「`pdf_leaf_1based` / `table_index_0based` … **schema owner**」（转引 `decision.md` L400） |
| `I-11-A/a20260919-01/decision.md` L400 | 「OPEN-4 \| 位置枚举 … \| schema owner \| 否 \| 跨卡页码复用」 |
| `I11A-OPEN-IND/.../ruling.md` L51 | 「OPEN-4（**位置枚举**，schema owner）」 |

⇒ **两套 OPEN-4 同号异物**（D-W06 函 A 的 T2-1 与 I-11-A 卡内 OPEN 表）。本工位按**授权原文（§二十七 L558「wiki 来源审核」）+ 父派单（T2-SIM-OPEN4-WIKI 为检验面）**执行，**不替父/owner 择一**；该不一致必须由父与 owner 核对（见 §五）。

### 1.2 ⚠ 题面「C1–C8」与源文件不符（登记，不代裁）

- 源文件逐字：`ruling.md` §5 只列 **C1–C6**（L147–L152）；`RESPONSES.md` L5 登记「**结论 CONDITIONAL（C1–C6）**」；`OWNER_DECISIONS.md` L437 转述「OPEN-4（CONDITIONAL：4a/4c APPROVE、4b 挂函 B 信任根、**C1–C6**）」。
- **C1–C8 属 T2-3(OPEN-5) 与 T2-2(OPEN-6)**（`RESPONSES.md` L6/L7 逐字）。
- 仓内出现的「C7/C8」字样是**别处引用**：`FIX-W06-GAPS/.../oracle.md` L165「C7-SCOPE (ruling C7 …)」与 `decision.md` L68 指向 `T2-SIM-OPEN5-RF` 的 C7；`oracle.md` L105 的「C8 pin gap」指向 `04_blocked_message_sweep.md`。
- ⇒ 本报告按 **C1–C6 逐条给状态**，并对 **C7/C8 各给一行 `NOT_IN_OPEN-4_SOURCE`**（fail-closed：不编造条件、不把 OPEN-5/6 的条件安到 OPEN-4 头上）。

---

## 二、C1–C8 逐条状态（取证层）

| 条 | 条件（源文件逐字要点） | 本工位取到了什么 | **取证层状态** | 阻断在哪 / 下一层归属 |
|---|---|---|---|---|
| **C1** 载体唯一性 | 唯一权威载体 = `documents.metadata_json["prompt_injection_review"]`；检验 = 写入只经 `record_prompt_injection_review`（grep CW 仓）+ 导出 JSON 带 non-authoritative 标注（ruling L147） | ① 载体常量字节：`corpus/CW_prompt_injection.py` **L5 `[199,254)`**「``documents.metadata_json["prompt_injection_review"]``:」、**L381 `[16274,16329)`** 唯一赋值点；② 写入点普查 `evidence/grep_census.txt`：赋值 **1 处**（pi:384）、`record_prompt_injection_review` 调用 **2 处**（`read_chain.py:223`、`source_lifecycle.py:168`）+ 定义（pi:263）；③ **`non-authoritative` 在 CW src = 0 命中** | **已证（主体）/ 子项未证**：载体与写入路径字节可核；「导出 JSON 非权威标注」**无任何对象可取**（产品 src 无导出面、无该字样） | 子项②（导出标注）缺对象 → 归**审核层**判断是否构成缺口；本工位不判 |
| **C2** 闭集冻结 | 闭集 `{not_reviewed, not_detected, detected_and_ignored}`；检验 = `PROMPT_INJECTION_REVIEW_STATUSES` 保持 frozenset，闭集外值被拒（ruling L148） | ① `corpus/CW_prompt_injection.py` **L66 `[3296,3341)`** `PROMPT_INJECTION_REVIEW_STATUSES = frozenset(`（L66–67）；② 闭集外值拒绝在码内：L107–110 `status must be one of …`，schema 门 L113–116；③ 产品测试 `test_record_without_binding_rejected` 等 17 个 `def test_*` 清单（`grep_census.txt` L11–L28） | **已证**（字节 + 行号可复算）。**行号漂移登记**：裁定引的 `:23–24` / `:53–56` 现为 `:66–67` / `:107–110`（文件已由 6,619 B 变 20,100 B，见 §四） | 无取证阻断；「闭集是否仍被冻结」的判定归**审核层** |
| **C3** 双绑定必填 | 晋级/消费回执必须同时带 `source_sha256`+`policy_hash`；检验 = record 两参非 None + INV-6 fail-closed（ruling L149） | ① `corpus/CW_prompt_injection.py` **L121 `[5460,5507)`** `_require_sha256(source_sha256, "source_sha256")`（L118–120 注释逐字：「P5-c: dual binding MANDATORY for every status (was optional=True …)」），policy_hash 同（L122）；② 读取侧 `_binding_mismatch`：`corpus/CW_prompt_injection_guard.py` **L220 `[9588,9617)`**，source 不符→`tampered`（L222–224）、policy 不符→`ignored`（L228–230）；③ INV-6 用例存在：`corpus/CW_test_prompt_injection_guard.py` **L309 `[10943,11003)`** `test_evaluate_legacy_unbound_receipt_is_tampered_not_hit`；④ `review-invalidation-matrix.json` L57–L64 `INV-6 … VERIFIED (existing test)` | **已证**（比裁定时更强：写入侧已强制，非仅「调用非 None」） | 无取证阻断；「是否满足 C3」归**审核层** |
| **C4** 身份绑定 + 单一信任根 | `reviewer` = 角色+具名主体+进程凭据，签名挂靠函 B/I-08-A 同一信任根；检验 = **函 B 出裁且信任根文件实测存在**之前不得标 signed（ruling L150） | ① 函 B 原文：`B_signature_trust_domain.md` **L7**（T2-9/OPEN-D1 归跨仓双方+owner 择定）、**L28**「**不存在可用于生产验证的信任根**」、**L240**「**信任根文件仍实测缺席**…与本函 P1『默认零可信签名者』的设计默认一致」；② 本工位存在性探针 `evidence/trust_root_probe.txt`：环境变量 `PROMPT_INJECTION_TRUST_ROOT` **未设**、**19 个 JSON 全部无 `signers`/`trust_root`**、CW src 仅 3 处引用加载函数；③ 产品现已是 fail-closed：`corpus/CW_prompt_injection.py` **L207–L210 `[8712,8774)`**「`disposal authorization unavailable: trust root not established`」 | **未证（阻断）**：检验前提「信任根文件实测存在」**实测为不存在** ⇒ 无法取得任何可证明签名链的来源证据 | ① 函 B `T2-9/OPEN-D1` **未出裁**（跨仓双方提选项 + owner 择定）；② 信任根**未建立**（环境/运维 owner 面）；③ 探针范围不含 OS keystore/机器级只读路径（本工位无该层权限）。**归审核层 + 环境/依赖 owner** |
| **C5** 失效语义落地 | 读取时 fail-closed、policy 内容变⇒全量重审、版本号单独变不失效、role_set/请求身份变不动回执；检验 = INV-1/2/3/6/7（既有）**+ 两条新正例**（ruling L151） | ① 既有 7 场景：`review-invalidation-matrix.json` **L77–L82** `total_scenarios:7 / verified:7 / all_fail_closed:true / no_faked_green_in_any_scenario:true`，逐条 INV-1…INV-7 齐（L6–L75）；② 事件记录 `review-execution-events.json` **L119–L120** `"total_events": 14, "execution_result": "14/14 PASS"`；③ **新正例①**：`I-06-B/a20260922-02/scripts/run_cases.py` **L1116** `"""M1 — OPEN-4 C5①: policy version-only change ⇒ still hit."""` + `evidence/green/M1.json` **L5–L6** `ruling_clause: "OPEN-4 condition C5① …"` / `verdict: "PASS"`；④ **新正例②**：同脚本 L1223 注册 + `evidence/green/M2.json` **L5–L6** `verdict: "PASS"`、L14–L16 两个不同 demand key | **已证（带限定）**：检验物齐全且字节可核。**限定**：M1/M2 是 `iso=fixed` **隔离副本**运行（非产品仓实跑），且 harness 工件系 I-06-B 卡产出的**二手**工件（本工位只读转录，未复跑） | 「这些用例是否算 C5 检验通过」归**审核层**；若需产品仓实跑证据 ⇒ 归**审核层/编排层**排复跑 |
| **C6** 覆盖留痕 | 覆盖旧收据前须在审核执行事件记录中留档**旧收据的 sha256**；检验 = 任一覆盖事件可查到前后两收据哈希（ruling L152） | ① 检验形态样例已取到：`review-execution-events.json`（4,889 B，sha `96170891…`）——**14 条事件逐条读毕，无「前后两收据哈希」字段**；② 现产品留痕形态：`corpus/CW_prompt_injection.py` **L360–L383** append-only 审计链 `prompt_injection_review_audit`（每写追加 `seq` 递增条目，含 `evidence_sha256/source_sha256/policy_hash/status`），**未见「旧收据整体 sha256」字段**；③ `grep old_receipt\|previous_receipt\|before_receipt` in CW src = **0 命中**（`grep_census.txt` L34–L35） | **未证（部分）**：样例与产品字节都取到了，但 **C6 字面要求的对象（覆盖前后两收据哈希）在两侧均不存在** ⇒ 该检验当前**无法从字节证成** | 缺口在**产品补字段**（实现面，归编排层/实现者）**或**审核层认定现审计链等价；判定归**审核层** |
| **C7** | — | **源文件 OPEN-4 无此条件**：`ruling.md` §5 只到 C6；`RESPONSES.md` L5「CONDITIONAL（C1–C6）」；L437 转述同 | **`NOT_IN_OPEN-4_SOURCE`（题面与源不符）** | 需父/owner 澄清题面所指（C7 属 OPEN-5 RF ruling）；本工位**不编造、不代裁** |
| **C8** | — | 同上（C1–C8 属 `RESPONSES.md` L6/L7 的 OPEN-5、OPEN-6 两行） | **`NOT_IN_OPEN-4_SOURCE`（题面与源不符）** | 同上 |

**取证层汇总**：C1 主体 / C2 / C3 / C5 = **已证**（4 条，其中 C1 子项②与 C5 带限定）；**C4 = 未证（阻断在信任根与函 B）**；**C6 = 未证（阻断在「旧收据哈希」对象不存在）**；C7/C8 = 不在本源条件集内。

---

## 三、逐字引文（全部带行号；corpus 副本另带实测字节区）

| id | 出处 | 行 / 字节区 | 引文 |
|---|---|---|---|
| Q1 | `corpus/CW_prompt_injection.py`（= 产品 `company-wiki/src/.../prompt_injection.py`） | L5 / `[199,254)` | 「``documents.metadata_json["prompt_injection_review"]``:」 |
| Q2 | 同上 | L66–L67 / `[3296,3341)` | 「`PROMPT_INJECTION_REVIEW_STATUSES = frozenset(` … `{\"not_detected\", \"detected_and_ignored\"})`」 |
| Q3 | 同上 | L118–L120 | 「`# FIX-W06-GAPS P5-c: dual binding MANDATORY for every status (was optional=True — an unbound receipt was accepted while the reader treats missing binding as tampered).`」 |
| Q4 | 同上 | L207–L210 / `[8712,8774)` | 「`disposal authorization unavailable: trust root not established`」 |
| Q5 | 同上 | L381–L383 / `[16274,16329)` | 「`metadata[PROMPT_INJECTION_REVIEW_AUDIT_KEY] = audit + [` … `dict(audit_entry, seq=len(audit) + 1)`」 |
| Q6 | `corpus/CW_prompt_injection_guard.py` | L87 / `[3971,4048)` | 「`CACHE_STATES = frozenset({\"hit\", \"ignored\", \"expired\", \"tampered\", \"absent\"})`」 |
| Q7 | `corpus/CW_prompt_injection_guard.py` | L220–L230 / `[9588,9617)` | 「`def _binding_mismatch(receipt …) ` … `receipt.get(\"policy_hash\") != policy_hash` ⇒ `status=\"not_reviewed\", cache_state=\"ignored\"`」 |
| Q8 | `corpus/CW_test_prompt_injection_guard.py` | L309 / `[10943,11003)` | 「`def test_evaluate_legacy_unbound_receipt_is_tampered_not_hit`」 |
| Q9 | `T2-SIM-OPEN4-WIKI/.../ruling.md` | L147 | 「**C1（载体唯一性）**：审核结论的唯一权威载体为 `documents.metadata_json[\"prompt_injection_review\"]`（schema_version `\"1.0\"`）。**检验**：产品代码中 review 结论的写入只经 `record_prompt_injection_review`（对 CW 仓 grep 可验）；任何导出 JSON 均带 non-authoritative 副本标注。」 |
| Q10 | 同上 | L150 | 「**C4（身份绑定 + 单一信任根）**：…**检验**：在函 B（`T2-9/OPEN-D1` 等）出裁且信任根文件实测存在之前，任何回执不得标称 signed、不得以「已签审核」名义晋级…」 |
| Q11 | 同上 | L151 | 「**C5（失效语义落地）**：…**加两条新正例**：① policy 版本号变、内容哈希不变 ⇒ 仍 `hit`（不失效）；② role_set / 请求身份变 ⇒ 原回执仍 `hit`、demand 按 OPEN-2 A 得新键。」 |
| Q12 | 同上 | L152 | 「**C6（覆盖留痕）**：…**检验**：任一覆盖事件可查到前后两收据哈希；缺失则该次审核事件无效。」 |
| Q13 | `outward_requests/B_signature_trust_domain.md` | L28 | 「**不存在可用于生产验证的信任根**。」 |
| Q14 | 同上 | L240 | 「**信任根文件仍实测缺席**——B1-F5 完整性复验对四生产锚的核验两处记「**trust 缺**」…与本函 P1「默认零可信签名者」的设计默认一致。」 |
| Q15 | `execution_runs/I-06-B/a20260919-01/after/review-invalidation-matrix.json` | L77–L82 | 「`\"total_scenarios\": 7, \"verified\": 7, \"all_fail_closed\": true, \"no_faked_green_in_any_scenario\": true`」 |
| Q16 | `execution_runs/I-06-B/a20260922-02/evidence/green/M1.json` | L5–L6 | 「`\"ruling_clause\": \"OPEN-4 condition C5① (two new positives unlocked for I-06-B)\", \"verdict\": \"PASS\",`」 |
| Q17 | `execution_runs/I-06-B/a20260922-02/evidence/green/M2.json` | L5–L6 | 「`\"ruling_clause\": \"OPEN-4 condition C5② + §4.3 domain split\", \"verdict\": \"PASS\",`」 |
| Q18 | `OWNER_DECISIONS.md` | L558 | 「派 `OPEN-4`（wiki 来源审核）…**受控取证**；**产物只落本计划目录**…**不解除任何 BLOCKED、不产生 ACCEPT**…」 |
| Q19 | `execution_runs/I11A-OPEN-MERGE/.../merge_ruling.md` | L361 | 「「`pdf_leaf_1based` / `table_index_0based` 是否需成为披露字段的规范枚举值｜**schema owner**」（`decision.md` L400）」 |
| Q20 | `outward_requests/RESPONSES.md` | L5 | 「函 A / T2-1(OPEN-4) / wiki 来源审核 owner（模拟·owner 终确）… **结论 CONDITIONAL（C1–C6）**」 |

（机器可读版本：`provenance.json` → `local_evidence[].verbatim_quotes`，共 17 条目、≥3 条引文/条目口径已满足。）

---

## 四、前提变化发现（取证层事实，不改判）

裁定写于 2026-09-22，其引用的两份产品字节**今日已漂移**（本工位实测）：

| 文件 | 裁定所记 | 今日实测（2026-09-25T22:16:20Z） | 结论 |
|---|---|---|---|
| `company-wiki/.../prompt_injection.py` | `7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618` / 6,619 B（ruling L83） | `88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33` / **20,100 B** | **前提变化**：FIX-W06-GAPS 修复面（P5-a/b/c、P6-A/B、C7 state_domain）已入产品 |
| `company-wiki/.../prompt_injection_guard.py` | `f900a13d…0b9c08` / 8,382 B（ruling L175） | `d71254782c10cd6d58c768eeb50e220de5e3d8047709e26f0604b5c59e67df0d` / **14,514 B** | **前提变化**（同上） |

**影响（如实登记，不代判）**：C1–C3 的检验锚点行号全部漂移（`:23–24→:66–67`、`:53–56→:107–110`、`:57–58→:111–112 + L353–L357 审计注记）；**C4 的待改点已被产品以 fail-closed 方式处理**（无信任根 ⇒ `detected_and_ignored` 一律拒），但**信任根本身仍不存在**，故 C4 仍未证；**C6 的「旧收据 sha256」字段仍不存在**。是否据此调整条件文本/重跑检验 = **审核层职权**。

---

## 五、尝试清单与第三方声明

- **联网尝试 = 0**：`web_fetch` 0 次、`web_search` 0 次、`filing-fetch`（含只读 reuse 探针）0 次。
- **是否经第三方代理：否**（0 次网络取回，故不存在代理渲染/转写字节）。
- **本地只读操作**：pwsh 读/哈希/探针 **37** 次、`read` 工具 **12** 次、`grep` 工具 **3** 次；哈希复算 **3** 轮（`22:01:45Z`、`22:13:11–12Z`、`22:16:20Z`）。
- **失败/中止 4 次（全记）**：①宽目录列举超时（`execution_runs` 根）②plan 全树列举超时 ③plan 全树 grep 因不可读目录 `os error 5` 失败 ④证据文件首写遇 PowerShell 引号转义解析错误 —— 全部改用定向/单引号方式重跑，**重跑结果以实测值落盘**（`evidence/trust_root_probe.txt` 即重跑产物）。
- **不联网的理由（fail-closed）**：OPEN-4 的 C1–C6 检验物全部是仓内对象；**不为凑「外部证据五要素」而发起无证据价值的请求**，也不拿二手网页当一手。

---

## 六、边界自证（本工位**没有**做的事）

1. **未写任何产品仓**：`company-wiki` / `filing-fetch` / `revenue-forecast`（仓根）写入 = **0**；`.planning` 之外创建/修改文件 = **0**。
2. **未执行任何 git 写操作**；**未使用 `git status`**（收尾只跑只读 `git diff HEAD --name-only`，非 `.planning` 计数 = **0**）。
3. **未判等级**：`level_claimed = null`（定级归会计面）。
4. **未解除 `OPEN-4`**：未改任何 status / handoff.status / decision / state；未产生 ACCEPT；未代签。
5. **未新增专业判断**：C1–C8 的「是否满足」一律不判，只交检验物与字节事实；两处不一致（OPEN-4 身份、题面 C1–C8）**只登记不择一**。
6. **未跑测试**：不执行 pytest/产品测试（会写缓存到产品仓）；C5 的 PASS 结论**只转录既有工件**，标注为二手、未复跑。
