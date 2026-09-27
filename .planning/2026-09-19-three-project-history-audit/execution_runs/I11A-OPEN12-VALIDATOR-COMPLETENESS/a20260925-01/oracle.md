# I11A-OPEN12-VALIDATOR-COMPLETENESS oracle（在第一次运行校验器之前冻结）

card_id: `I11A-OPEN12-VALIDATOR-COMPLETENESS` · attempt_id: `a20260925-01`
role: **统计/工程 reviewer（非实现者，`handoff.implementer_signed=false`）**
授权: `OWNER_DECISIONS.md` §二十八（2026-09-25，原话「**是，另立校验器专业卡（建议）**」）
冻结时刻: 本文件写入时刻**早于**本 attempt 的**第一次**校验器运行（含正例、反例套件、变异）。
本文件冻结后只允许以 `erratum-*` 追加式附录修订，正文一字不改。

---

## 0. 本卡裁什么、不裁什么

**裁（唯一范围）**：`P2-5 / P2-6 / P2-7 / P2-8 / P2-9` 这批独立复核发现是否已在 `I-11-A/a20260919-01`
本 attempt 内**处置到位**，其中核心判据只有一条：

> **完备性判据**：对「校验器应当抓住的那一族输入」，**该族输入是否都能被 `tools/validate_hypotheses.py` 抓住**。
> 「已处置的那 8 个具体变异被拒」**不等于**「该族完备」；本卡分别取证。

**不裁（照抄卡文与 §二十八执行纪律）**：不解除 `OPEN-12`（其 `RULED_WITH_BLOCKED_VALUE` 维持）、
不放行任何参数、不给阈值、不改 `threshold_basis`、不解除任何 BLOCKED、不产生 `I-11-B` 的 ACCEPT、
不重裁 `I-11-A` 已签收（`accepted_scoped`）内容、不代签、不写五份计划文件、不联网、禁 git 写、禁 `git status`。

---

## 1. 输入绑定（冻结前已读；sha256 为实测值，如实登记）

| 文件 | sha256 | 字节 |
|---|---|---|
| `execution_runs/I-11-A/a20260919-01/decision.md`（L408 = OPEN-12 原始定义） | `e9c96f02118514b8596620b3c0e235a797747fcd3bcf59d1a0fd20aa70166951` | 29,756 |
| `execution_runs/I-11-A/a20260919-01/oracle.md`（§R2） | `83dca500732f9365bbca865b4098729657d994af6ad40b282c26237c9906a890` | 22,418 |
| `execution_runs/I-11-A/a20260919-01/review.md`（§4/§5/§5.1） | `4938e745adc3f32582cc6fd70e3e69197385035d0270807d955d2a7c7776daed` | 19,417 |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/mechanism_review.md`（§5 第 8/9 条） | `70c3ca91c16bacedb719fbe8033ee169a490017e9da3099906879e222f8c6d26` | 21,806 |
| `execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py`（被裁对象） | `cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac` | 28,549 |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 51,697 |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/source_map.json` | `3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf` | 13,863 |
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/validation_report.json`（归档基线） | `dc014e7e7a5699f5692d60d3e7cf76b782d1c64ef7668d5104e077290cb7c9b8` | 5,341 |
| `execution_runs/I11A-OPEN-MERGE/a20260924-01/merge_ruling.md`（L362 = G3） | `2d214bab861be4ff30ebb7118705d23183fb2eec3e58f987d52287d0bab2e5c1` | 49,062 |
| `OWNER_DECISIONS.md`（§二十七 行内勘误、§二十八） | `7e0b7917cb7b0cbe2158e48abc1f073b8157aafe082c115afb5fb593cace80de` | 84,868 |
| `execution_v2/card_I11A-OPEN12-VALIDATOR-COMPLETENESS.md`（本卡合同） | `191c0ec5099bb893bf91b50a4acc573ed69c2e072872b0f44becf90f4d811090` | 4,308 |
| 独立复核报告 `C:\i11a-rv\review\REPORT.md`（P2-5…P2-9 原文所在；与 `review.md` L86-88 记录的 sha 一致） | `e8b7d223e83c91128545e2b25b28b97ecba50cf2a5855e7366fabcaba16cafaf` | 46,451 |

**冻结前已做的输入读取（如实披露，同 I-11-A oracle §0.1 的做法）**：我读了 `hypotheses.json` 的
8 条命题全文（state / source / parameter_mapping / falsifier / mechanism_chain 末环 / 顶层字段），
用于**手算**下表的 expected；**我没有在冻结前运行过 `validate_hypotheses.py` 的任何部分**
（既没跑正例、也没跑反例套件、也没跑变异）。

---

## 2. 判据（三条，冻结）

- **J1 完备性（红→绿）**：构造反例集合 `CE-01…CE-11`（见 §3）。**若当前校验器放行其中任何一条
  「按冻结规则应当被拒」的输入 ⇒ 处置不完整（红）**；补丁后该条必须被拒（绿）。
- **J2 判别力（变异）**：仅当 `CE` 在补丁版上全部被拒时，必须逐一**删掉补丁中的每一条新判据**，
  对应 `CE` 必须由「拒」翻回「放行」（变异红）。**没有变异证明的绿一律不算数。**
- **J3 不破坏正例与既有套件**：补丁版上，正例 `validate(hypotheses)=[]`，且原 21 条反例套件
  `21/21 rejected、0 accepted`（基线值取自归档 `validation_report.json`：`cases=21,
  rejected_as_expected=21, accepted_by_mistake=0`、`positive_case.verdict=pass`）。
  任一被打破 ⇒ 我的补丁判为过度收紧，不能交付。

**每条 `CE` 的两条 expected 都是手算的**（依据：逐行读 `validate_hypotheses.py` L117–L303 的判定路径），
不由任何一次重跑生成；跑出来的结果与本表不符 ⇒ 按 erratum 记录，不回改本表。

---

## 3. 预注册反例 `CE-01…CE-11`（冻结后不得增删）

基命题统一取 `H-CN-ZIJIN-SEG-01`（实现者自己的套件也以它为 base；正例下它单独通过）。

| # | 注入（只改这一处） | 规则锚点（回源） | 期望：当前校验器 | 期望：补丁版 | 置信 |
|---|---|---|---|---|---|
| CE-01 | `falsifier.threshold = "相对偏离不超过 ±10%（纯幅度阈值）"`，`threshold_basis` 仍 `arithmetic_identity` | `oracle.md` R2-1 `E_THRESHOLD_BASIS_INCONSISTENT`「`arithmetic_identity` 但阈值文本不是等式 → 拒绝」 | **放行（红）**：原判据 `re.search(r"0\|差\|等于\|=\|≤", thr)` 会命中 "10%" 里的 `0` | 拒 `E_THRESHOLD_BASIS_INCONSISTENT` | 强 |
| CE-02 | 追加第二条命题，**除 `hypothesis_id` 外与基命题逐字相同**（同 `parameter_id`、同 driver/期间、同 claim、同 observation） | `oracle.md` §3.3「一个命题对应唯一 `parameter_id`」+ 独立复核 `REPORT.md` L233 预登记「期望被拒」 | **放行（红）**：`same_driver=True 且 same_prop=True` ⇒ L206 条件为假，不报错 | 拒 `E_DUPLICATE_PARAMETER` | 强 |
| CE-03 | 追加第二条命题：`model_id`/`driver_name`/`effective_period` 与基命题**完全相同**，但 `parameter_id` 改名、`claim` 加后缀 | `oracle.md` §3.3 **O-11**「同 model_id+同 driver_name+同 effective_period ⇒ **必须同** `parameter_id`」 | **放行（红）**：只按 `parameter_id` 建索引，不同 id 不进重复检查 | 拒 `E_DUPLICATE_PARAMETER` | 强 |
| CE-04 | `mechanism_chain` 末环 = `"项目档案信息确认流程闭环交付"`（≥8 字、含「确认」「交付」，但无收入/期间语义；前两环保持原样） | `oracle.md` R2-1 `E_CHAIN_END_SEMANTICS`「末环不含收入确认/期间归属语义 → 拒绝」+ §3.3 | **放行（红）**：`CHAIN_END_MARKERS` 命中「确认」 | 拒 `E_CHAIN_END_SEMANTICS` | 强 |
| CE-05 | `falsifier.observable = "   "`、`falsifier.source_route = "   "`（纯空白，其余不动） | `oracle.md` §7 `E_MISSING_FALSIFIER`「falsifier 五要素缺一 → 拒绝」+ §3.4 五要素 | **放行（红）**：`if not fz.get(k)` 对非空空白串为真 | 拒 `E_MISSING_FALSIFIER` | 强 |
| CE-06 | **顶层** `page_index_basis = "printed_page_1based"`（`source.page_index_basis` 保持 `pdf_leaf_1based`） | `oracle.md` §7 `E_BAD_PAGE_BASIS`「`page_index_basis != pdf_leaf_1based` 而给的是打印页码 → 拒绝」+ O-4 | **放行（红）**：顶层字段只查存在（L126-128），值从不校验 | 拒 `E_BAD_PAGE_BASIS` | 强 |
| CE-07 | **顶层** `anchor_text = "这段文字不在原文中"`（`source.anchor_text` 保持合法） | `oracle.md` §7 `E_ANCHOR_NOT_FOUND` + O-4「以锚文本同时给出定位串」 | **放行（红）**：只校验 `source.anchor_text`（L274） | 拒 `E_ANCHOR_NOT_FOUND` | 强 |
| CE-08 | `falsifier.observation_date = "2026-13"` | `oracle.md` R2-1 `E_OBSERVATION_DATE_UNRESOLVED`「不含 YYYY-MM 级日期锚点 → 拒绝」+ `review.md` §5.1「观察日可解析」 | **放行（红）**：正则 `r"\d{4}[-/年]\d{1,2}"` 只查形状 | 拒 `E_OBSERVATION_DATE_UNRESOLVED` | 强 |
| CE-09 | `state="approved_frozen"`、`reviewer="Independent Reviewer (external)"`（30 字符、非黑名单）、`decision.decision_sha256="x"` | `oracle.md` §7 `E_STATE_APPROVED_BY_IMPLEMENTER`「`approved_frozen` 且 `reviewer` 非独立 → 拒绝」+ R2-1「`decision.decision_sha256` … 要求封缄」 | **放行（红）**：黑名单 + 长度≥8 + sha 非空三项全过 | 拒 `E_STATE_APPROVED_BY_IMPLEMENTER`（sha 必须 64 位 hex） | 边界（R2-1 字面只写「未填」；本条按 §7 字面 + 封缄语义判） |
| CE-10 | `falsifier.observable = "市场风险上升（若风险加大则命题失效）"` | `oracle.md` §3.4 第 1 条「`observable`：一个具体观测量（**不是"风险上升"这类词**）」 | **放行（红）**：无任何具体性检查 | 拒 `E_FALSIFIER_OBSERVABLE_VAGUE`（新码） | 强 |
| CE-11 | `evidence_path = "evidence/I-11-A/extract/NOT_ARCHIVED.json"` | `oracle.md` §2 **O-3**「该路径的 sha256/argv/输出文件已归档到本 attempt」+ §3 追加强制字段 `evidence_path` | **放行（红）**：顶层字段只查存在 | 拒 `E_EVIDENCE_PATH_NOT_ARCHIVED`（新码） | 中 |

**预期汇总（手算）**：当前校验器 **11/11 放行** ⇒ J1 红成立 ⇒ 处置不完整；
补丁版 **11/11 拒绝 + 正例 pass + 21/21 不破** ⇒ J1/J3 绿。

## 3.1 预注册「独立复核原 8 个变异」的复现（REPRO-1…8）

按 `REPORT.md` §2 P2-5 表逐行字面构造，用来检验 `review.md` §5.1 P2-5 行的自述
「reviewer 指出的未拒绝变异**全部**固化并现已被拒」：

| # | 注入 | 期望：当前校验器（手算） |
|---|---|---|
| REPRO-1 | `source.page_index_basis = "pdf_leaf_1based "`（尾空格） | 拒 `E_BAD_PAGE_BASIS` |
| REPRO-2 | `source.doc_id = "HK-XIAOMI-AR2025"` 但保留紫金 `doc_sha256` | 拒 `E_SOURCE_HASH_MISMATCH`（+`E_ANCHOR_NOT_FOUND`） |
| REPRO-3 | `state=approved_frozen` + `reviewer="Independent Reviewer (external)"`，**不加** `decision` | 拒 `E_STATE_APPROVED_BY_IMPLEMENTER`（因 `decision_sha256` 缺） |
| REPRO-4 | `threshold_basis="arithmetic_identity"` + `threshold="±7% 无恒等式"` | 拒 `E_THRESHOLD_BASIS_INCONSISTENT` |
| REPRO-5 | `refuted_by = ["", "   "]` | 拒 `E_EMPTY_FIELD` |
| REPRO-6 | `mechanism_chain = ["a","b","c"]` | 拒 `E_CHAIN_END_SEMANTICS` |
| REPRO-7 | `observation_date = "TBD"` | 拒 `E_OBSERVATION_DATE_UNRESOLVED` |
| REPRO-8 | 两条**同 `parameter_id` 的相同命题**（`REPORT.md` L233 字面） | **放行（红）** ← 与 §5.1 自述冲突的关键预测 |

---

## 4. 变异清单 `M1…M10`（每条 = 在**补丁版**上删除对应新判据块，回到原实现）

| # | 删除的补丁块 | 预期被它托住而翻红的 CE |
|---|---|---|
| M1 | `OPEN12-G1` 阈值等式判据 | CE-01 放行 |
| M2 | `OPEN12-G2`（G2a 同命题重复 + G2b 同 driver 不同 id） | CE-02、CE-03 放行 |
| M3 | `OPEN12-G3` 末环严格收入语义 | CE-04 放行 |
| M4 | `OPEN12-G4` falsifier 空白 strip | CE-05 放行 |
| M5 | `OPEN12-G5` 顶层 `page_index_basis` 值校验 | CE-06 放行 |
| M6 | `OPEN12-G6` 顶层 `anchor_text` 校验 | CE-07 放行 |
| M7 | `OPEN12-G7` 观察日月份域校验 | CE-08 放行 |
| M8 | `OPEN12-G8` `decision_sha256` 64-hex | CE-09 放行 |
| M9 | `OPEN12-G9` observable 具体性判据 | CE-10 放行 |
| M10 | `OPEN12-G10` `evidence_path` 归档判据 | CE-11 放行 |

**变异判据（J2）**：任一 `M*` 下，**至少**其对应 CE 由「拒」翻回「放行」；同时正例仍 pass、21/21 仍 21/21。
做不到 ⇒ 我的补丁是假判据（等价于没改），判 `insufficient_evidence`。

---

## 5. 范围边界

- 被裁对象只有 `I-11-A/a20260919-01/tools/validate_hypotheses.py`（sha 见 §1）与其判据所依的
  `oracle.md §3/§7/R2`。**P2-6/P2-7/P2-8/P2-9 不是校验器问题**（分别是措辞、探针口径、阈值可观测性、
  证据粒度），其处置判定按「**回源核对改动是否落地 + 是否存在可机器化的漏**」两条分别取证，见 `ruling.md` §④。
- 本卡**不**对 `I-11-B`、`I-11-C` 的任何参数、阈值、状态做判断；`I-11-C 是否复用同一校验器`只给
  「结论 + 理由 + 复用条件」，不产生 ACCEPT、不解除任何 BLOCKED。
- 补丁**只出 `changes.diff`，不写真仓**；`src/`、`scripts/` **一律不触碰**（本卡 diff 只涉及
  `.planning/.../execution_runs/...` 内的 iso 副本）。
- 我不采信 `OPEN12-CUTOFF-ANNOUNCE-ACQUISITION/a20260925-01` 的任何交付（错题作答，不解答本卡问题）。

## 6. 行不交界声明（与 `I-11-A` 已签收面的关系）

- `I-11-A` 已由独立 reviewer 签 `accepted_scoped`（`review.md` §5 逐字转录）。**本卡不重裁该签收**：
  我不复算 A1–A7、不复核 46 条引用原值、不评价 STOP_EVIDENCE、不改任何 `decision.md`。
- 本卡的产出**只落在** `execution_runs/I11A-OPEN12-VALIDATOR-COMPLETENESS/a20260925-01/` 与其中的
  iso 副本；`I-11-A/a20260919-01` **一个字节都不改**（封盘只读），结束前用 sha256 复核。
- 本卡对 `P2-5…P2-9` 的「已处置 / 部分 / 未处置」判定，**只回答 `OPEN-12` 这一行问的问题**，
  不回溯改变 `accepted_scoped`，也不产生 `I-11-B`/`I-11-C` 的任何解锁。

## 7. 退出判据

1. `oracle.md`（本文件）已先冻结；
2. J1 红（CE 放行清单）+ J1 绿（补丁后 11/11 拒）+ J2 变异 M1…M10 逐条翻红；
3. `I-11-C 复用`结论落地（结论 + 理由 + 条件）；
4. `handoff.json`：`status=review_pending`、`implementer_signed=false`、`releases_nothing=true`、
   `does_not_claim_I11A_acceptance=true`；`git diff` 非 `.planning` = 0。

---

## erratum-1（追加式，正文 §3 表一字不改；记录首次 RED 运行与冻结 expected 的两处不符）

**首次 RED 运行**（`red/cases_original_run1_with_harness_defect.json`，原样保留）结果
`positive=pass、suite=20/21、CE 10/11 放行、REPRO 7/8 拒`、`rc=1`，与 §3/§2 手算有两处出入：

1. **`suite=20/21` 是我 runner 的缺陷，不是校验器的问题**：`main()` 对
   `E_LISTED_VALUE_NOT_IN_EVIDENCE` 这一条会喂入**附加了伪造 `CE-DOC` 条目的 source_map 深拷贝**
   （`validate_hypotheses.py` L416-425），我的 `suite_results()` 漏复制该特例。
   已按 `main()` 原样补齐；**校验器本体的基线独立取证见 `red/baseline_run.log`（`main()` 直跑：
   `positive pass / 21 / 21 / accepted_by_mistake=0 / rc=0`），且重跑产出与归档
   `validation_report.json` 的 `positive_case`、`counterexample_summary`、`counts`、`counterexamples`
   四处逐字段相等。**
2. **`CE-03` 首跑被拒（`E_DUPLICATE_PARAMETER`），但被拒的原因不是它锚定的 O-11 正向**：
   基命题 `H-CN-ZIJIN-SEG-01` 带 3 条 `additional_parameters`，我的副本逐字继承 ⇒
   这 3 个 additional `parameter_id` 与命题 A 撞车、而 `claim` 又被我加了后缀 ⇒
   命中的是**旧**判据（L197-209，`same_prop=False`），**完全没有测到**「同 driver/期间 ⇒ 必须同
   `parameter_id`」这一正向。
   **修正（只隔离、不放宽）**：CE-03 的注入改为「主 `parameter_id` 改名 + **清空
   `additional_parameters`** + `claim` 加后缀」。这样除被测的 O-11 正向外没有任何 pid 交集。
   CE 集合仍为 11 条，未增删，其余 10 条的 RED 结果与 §3 手算**逐条一致**。

**修正后重跑**（`red/cases_original.json`、`logs/red_run.log`，`rc=0`）：
`positive=pass`、`own suite=21/21`、**`CE 11/11 放行`**、`REPRO-1…7 全拒 + REPRO-8 放行`
——与 §3/§3.1 手算完全一致，J1 的「红」成立。
（另：我在 runner 的 `red` 相位写反了一个布尔条件——期望「CE 全部放行」却写成「全部被拒」——
纯属我的脚本笔误，已改；该笔误不影响任何被测判定，两次 RED 的**原始判定数据**均已保留。）

