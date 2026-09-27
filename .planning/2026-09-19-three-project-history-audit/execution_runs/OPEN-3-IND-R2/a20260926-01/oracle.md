# `OPEN-3-IND-R2` · `a20260926-01` — 行业面复裁分部集合（oracle，**先冻结**）

- **卡 / attempt**：`OPEN-3-IND-R2` / `execution_runs/OPEN-3-IND-R2/a20260926-01`
- **role**：`industry_reviewer_ind_r2`（矿业/软件行业 reviewer，**非实现者**）｜ **父**：`session-19074bf0-0205-4315-af73-9db57597275a`
- **本卡 = `MERGE` 七条 `C3` 第 4 步（末步）**：行业面按 `OPEN3-E1-ACCT-RULING` **C4**（「会计面 `OPEN-3-ACCT-R2` 认定等级 → **行业面 `ruling_r2.md` 按 `supersedes` 复裁分部集合**（IND L197）」）对**分部集合**做复裁。
- **冻结时间**：2026-09-26（UTC 日期；本文件在任何判定动作之前写就并冻结；此后**不回改**，追加只允许 §5.2 形式的执行后实测补记）

---

## 0. 被裁对象与只读面

**要会签的对象（全程只读）**：

1. `execution_runs/OPEN-3-ACCT-R2/a20260926-01/`（`ruling_acct_r2.md` · `e1_regrading.json` · `_verification_raw.json` · `handoff.json`）
2. `execution_runs/OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01/`（`origin_bytes.bin` 62,953 B · `provenance.json` · `ruling_e1_bytes.md`）
3. `execution_runs/I11A-OPEN-IND/a20260924-01/ruling.md`（IND C 表 L227/L231-234/L240-241/L261/L360；L197/L198）
4. `execution_runs/I11A-OPEN11-IND/a20260924-01/`（行业面另一张卡，查其对 4 份语料/8-K 的引用）
5. `OWNER_DECISIONS.md` §三十 / §三十一（含 §二十七 #2、L543、§三十二、§三十四）
6. `execution_runs/OPEN3-E1-ACCT-RULING/a20260924-01/ruling.md`（上轮 `BLOCKED-PARTIAL` 与 R2 复裁条件 C1/C4/C5）
7. `execution_runs/OPEN3-E1-ACQUISITION/a20260924-01/`（4 份语料本体 + 取证 provenance，用于 C5-direction 的来源系谱核查）

**只读自证**：读前记录上述全部文件 sha256，收尾复算，**0 字节变更**方为合格。

**写入面 = 恰本目录**（`execution_runs/OPEN-3-IND-R2/a20260926-01/`）：`oracle.md` · `ind_probe.py` · `_probe_raw.json` · `ind_ruling_r2.json` · `ruling_ind_r2.md` · `handoff.json`。**`.planning` 之外 0 写入**（产品落点归父，本卡不碰 `company-wiki`/`dayu-agent` 任何字节）。

---

## 1. 五问判据（冻结；每问 = 结论 + 依据 + 反例 + 兼容影响 + 恢复规则）

### Q1 —— 分部集合（8-K + Exhibit 99.1）是否齐？
- **判据**：在 **origin 载体**（`origin_bytes/` 两件）上逐条定位行业面所需的分部集合要素，给**行号/字节区**：
  (i) 8-K Item 7.01 的**新两分部名称与生效期**（`Agents and Infra` / `Devices and Consumer`，FY2027 起）；
  (ii) 8-K Item 7.01 的**重述声明**（historical data on a basis consistent with the updated reporting structure）；
  (iii) Exhibit 99.1 的**重述后基期分部数据**（会计面 Q6 锚点 `$61,672 $64,441 $67,438 $74,576 $268,127` 一带）；
  (iv) Exhibit 99.1 的 **FY27Q1 outlook**（会计面 Q7 锚点 `$75.15 to $75.75 billion` / `$14.7 to $15.2 billion`）；
  (v) 旧三分部（PBP/IC/MPC）→ 新两分部的**桥接信息**是否存在（IND `ruling.md` L185 反例：无桥接表不得混用）。
- **判定档**：`齐（全部命中并给字节区）` / `部分齐（列缺什么）` / `不齐`。
- **注意**：判的是**分部集合内容是否齐**，不是证据等级（等级 = 会计面，已定 `E1=BLOCKED-PARTIAL`、`S=S1`）；C5 降级**不删除** origin 层已定位的事实，但引用须带 `quotes_status=void_pending_reanchor`。

### Q2 —— ⭐ `C5-direction`（错在 origin 还是语料）能否定？
- **判据（定方向的证据门槛，冻结）**：必须有**与 R2 取证会话/实现不同**的第三条独立路覆盖**争议点本身**（`amplifying/amplifies` 那句在 EX99.1，以及 `corpusA` 缺失的 8-K 签名页段）。
  - **可采**：IND 侧 `EXT-*` 条目（r.jina.ai 渲染等**另一会话、另一实现**）中**实际覆盖争议句/争议段**的逐字引文；行业面自己的抽取件若只是**重读盘上 origin 字节**，只能复核「origin 说什么」，**不能定向**。
  - **不可采**：`origin_bytes` 与 `_independent_…complete_submission.txt` 的互证（同 R2 一会话取回，ACCT 已裁不能自证）；A/B 两份语料的互证（ACCT 已实证共享同一错）；语法/文风推断（只作辅助观察，**不作定向依据**）。
  - **若定不了 ⇒ 判 `不确定`**，并写明缺什么（不为推进链抬高）。
- **反例（会推翻我的判定）**：若 IND `provenance` 的外部条目里其实**逐字覆盖**了争议句/签名页段且与某一边一致 ⇒ 方向可定，我须改判为定向并给方向。

### Q3 —— `S = S1` 是否可会签？
- **判据**：按 ACCT S 表四要件（同期间原文披露 + 锚文本可定位 + doc sha256 绑定 + ≥1 独立复核路径）与 IND C 表 ①/④ 的组合逐项复核；核**三项强制登记**（`external_retrieval_not_local=true` 永久、`kind=current_report→raw/other/`、`raw_sha256+stripped_sha256` 双登记）是否齐且与 IND L198/L360、§三十一 一致；核 **`S1 ≠ 放行`** 的表述是否保持。
- **判定档**：`会签（同意 S1 + 三登记）` / `推翻（给替代等级与依据）` / `有条件会签（列条件）`。

### Q4 —— IND C 表逐项是否同意？
- **判据**：逐行裁 ①`company_primary_disclosure`（内容类型）②不适用 ③不适用 ④`external_retrieval_not_local=true`（**永久**，IND L198/L360）；含 `kind=current_report → raw/other/` 的诚实登记（§三十一 #1/#2）。查 ACCT 对 ②/③ 的排除理由是否成立（存管处 SEC 但被引对象是公司自身披露；语料 4 件已降 E3 正落 ③）。

### Q5 —— 恢复链 RC1–RC5 的 IND 侧确认
- **判据**：逐条裁 ACCT 的 RC1（定方向）→ RC2（以 origin 重建 8 条引文、**Q1 保留 `(1)&#160;Agents` NBSP 形态**）→ RC3（旧语料追加式改 E3）→ RC4（落点/产品仓，父的第①件）→ RC5（新建 `OPEN-3-ACCT-R3`）是否同意；**是否还缺 IND 侧的步**（如：IND 侧 `ruling_r2.md` 的 `supersedes` 复裁是否已由本卡完成、IND 侧证据条目是否需新增 E3/divergence 追加登记、IND `BLOCKED-4/5` 的更新归谁）。
- **判定档**：`同意 RC1–RC5 + IND 侧补充步列表` / `不同意（给替代）`。

## 2. 方法纪律（冻结）

1. **先回源读**（逐字，不采信派单转述）；一切引用给**行号/字节区 + 逐字**。
2. **零联网**：本卡是行业面复裁、不重取 origin（`L543` 类比 + 派单明示「不需要网络」）⇒ **网络请求 = 0**。若发现确需外部取证 ⇒ **不自行联网**，写入 `blocked`/`不确定` 并说明所需取证（provenance 四件留给取证卡）。
3. **门 0（写权限自探）**：`写 + 回读 + 删除` 三步，原始输出存本目录 `gate0_raw.txt`（`oracle.md` 附录）。**被拒 ⇒ 停在原地报 `blocked`，禁止任何破坏性替代**（禁 `git apply`、禁 `>` 重定向覆盖产品文件、禁删后重写；`findings` R115 教训）。
4. **独立复算**：不采信 ACCT/R2 自报数字；关键事实（sha、`amplifying/amplifies`、签名页段、NBSP、注入脚本跨度、Q6/Q7 锚点、8 条引文形态）由我自己写的 `ind_probe.py` 在盘上字节重跑，原始输出落 `_probe_raw.json`。
5. **fail-closed**：Q2 定不了方向 / C 表证据不足 ⇒ 判 `不确定` 或 `blocked`，**不为推进而定级**。
6. **禁**：写五份计划文件（`task_plan`/`findings`/`progress`/`audit_report`/`delivery_validation`）；写 `.planning` 之外；git 写（`add/commit/push/checkout/stash/restore/reset`）；**禁用 `git status`**；改任何 `status/state/decision`。
7. **不授予（冻结清单）**：不解除 `OPEN-3`；不解除 `BLOCKED-NEEDS-ORIGIN-BYTES`/`B1`/`B2`；不放行任何参数（MSFT 四参数 + 新两分部参数 + `_PLACEHOLDER` 全维持未放行）；不产生 `ACCEPT`；不改 `E1/S` 定义（ACCT L190 对称）；不代签会计面；不回改任何上游载体。

## 3. 红绿变异清单（冻结；`rc` 约定：0 = 按预期表现）

| # | 变异 | 期望 | 
|---|---|---|
| G1 | 真实 origin EX99.1 句子在 4 语料中检索（`amplifying`/`amplifies` 各自计数） | 绿：origin/归档 `amplifying=1, amplifies=0`；语料 A/B `0/1`（复现 C5） |
| G2 | 8-K 签名页段（`/s/ Alice L. Jolla`）在 origin / corpusA / corpusB 计数 | 绿：origin 1、corpusB 1、corpusA 0（复现缺段） |
| G3 | Q1 锚点 `(1)` 后空白形态（NBSP/普通空格/无）四方计数 | 绿：origin = NBSP×2（`&#160;`），语料 = 无空白（复现空白保真缺陷，不降级） |
| G4 | 注入 `<script>` 在 origin 两件与 as-filed 归档的命中数与字节跨度 | 绿：origin 各 1、归档 0；跨度与登记一致（传输层注入判定） |
| G5 | Q6/Q7 锚点（重述基期分部数据、FY27Q1 outlook）在 origin 命中与字节区 | 绿：全部命中（分部集合内容层成立） |
| R1 | 把语料 `.md` 当 origin 载体做 G1 | 红：sha 不在 origin 登记表（拒） |
| R2 | 引文数字改一位（`$268,127→$268,126`）在 origin 检索 | 红：不命中（拒） |
| R3 | 仅空白变异（Q1 补一个空格）后 M1/M2 行为 | 绿差异化：M1 命中 / M2 拒（登记 M1 空白盲区） |
| R4 | sha256 复算任一 origin 件与登记表比对 | 红：翻转 1 字节即不符（拒） |

判别力结论：`discrimination_ok = G1–G5 全绿 且 R1–R4 全红/差异化`。

## 4. `blocked` / `不确定` 触发（冻结）

- **`blocked`**：门 0 三步任一失败；只读面被发现已变更（sha 不符）；需要联网才能完成的判定。
- **`不确定`**：Q2 无第三条独立路覆盖争议点（最可能落点）；Q1 某要素在 origin 上无法定位且无反证；C 表某行证据不足。
- 二者都**不**构成解锁；产出照写，结论如实。

## 5. 产出与边界

- 四件产出：`oracle.md`（本件，含门 0 原始输出）· `ind_ruling_r2.json` · `ruling_ind_r2.md` · `handoff.json`（`role=industry_reviewer_ind_r2`、`authorized_by`、`five_questions`、`c5_direction_ruling`、`s_level_signed`、`segment_set_ok`、`releases_nothing=true`、`written_files`、`git_diff_non_planning=0`）。
- **收尾**：只读面复哈希自证 + `git -c core.quotepath=false diff HEAD --name-only`（只读，**禁 `git status`**）数非 `.planning` 行数（要求 0）。

### 5.2 执行后实测补记（唯一允许的追加区；不改判据）

（执行完成后填写；只记实测，不动 §1–§4 任何判据。）

1. **门 0 = PASS**（写 + 回读 + 删除三步全过；原始输出 `gate0_raw.txt`；写入面仅本目录；产品仓未探未写）。
2. **执行顺序**：oracle 冻结（本件 §0–§5）→ 回源读毕 → `ind_probe.py`（T0/G1–G5/R1–R4）→ `ind_probe_b.py`（签名页变体/解码引文重跑/桥接扫描/空白形态）→ 裁定 → 收尾复哈希 + git 只读计数。
3. **写入面登记（如实）**：oracle 冻结时列 6 件，执行中在**同一目录**增补 `ind_probe_b.py`、`_probe_raw_b.json`（补充探针 B 的代码与原始输出），另 `gate0_raw.txt` 见 §2.3 ⇒ **实写 9 件，全部在本 attempt 目录内，`.planning` 之外 0**；判据（§1–§4）无任何改动。
4. **关键实测**（详见 `_probe_raw.json` / `_probe_raw_b.json`）：
   - G1 词形四方计数复现（origin_ex991 `amplifying=1@3681`、asfiled `@33446`、corpusA/B `amplifies=1@2540`）；
   - G2 签名页：origin/asfiled/corpusB 全有、corpusA 全缺 ⇒ 缺段方向 = 语料 A 侧；
   - G3 空白形态：origin = `&#160;`×2（解码 U+00A0）、corpusA = 无空白、**corpusB = 半角空格 + 硬换行**（oracle 预期「语料无空白」仅对 corpusA 成立，按细化登记，rc=0）；
   - G4 注入脚本 @28544/34147（→28650/34253），归档 0 命中，剥后 sha 复算一致；
   - G5 分部集合锚点全命中（Q6 [20291,20331]、Q7 [30770,30794]/[30827,30849] 等，见 ruling Q1 表）；
   - 引文独立重跑：M1 8/8、M2 7/8、M3 3/8（与 ACCT 自报逐数一致）；R1–R4 全红/差异化；`discrimination_ok = true`。
5. **Q2 执行结果**：签名页方向可定（corpusA 侧）、词形方向 `不确定`（fail-closed）——已按 §1-Q2 判据执行，未用语法推断定向（只登记为辅助观察）。
6. **收尾自证**：只读面 11 件复哈希全部 unchanged（`handoff.json → read_only_rehash`）；`git diff HEAD --name-only` 总 3,830 行、**非 `.planning` = 0**；网络请求 0；git 写 0；未用 `git status`。
