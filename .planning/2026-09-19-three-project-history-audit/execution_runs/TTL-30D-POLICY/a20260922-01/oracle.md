# oracle.md — TTL-30D-POLICY / a20260922-01（冻结于任何运行之前，2026-09-22）

> **冻结纪律**：本文件在本 attempt 的**第一次任何运行（测试/探针/变异）之前**写定。全部预期**只**来自卡面原文
> 与 owner 终确生效件（下列来源逐条标注），**不**调用被测函数生成 expected。若实现与本 oracle 冲突 ⇒
> 实现改，oracle 不改（勘误除外，追加式）。当前已发生的动作仅为**只读取证**（读源码/裁定原文/grep 调用点），
> 未运行任何测试或探针。

## 0. 契约来源（全部为 owner 终确生效件 + 本卡卡面）

| 来源 | 载体 | 取用条款 |
|---|---|---|
| 卡面 TTL-30D-POLICY（本次派发） | 父派发原文 | TTL = 选项 A 30 天（86400×30）为 policy CAP；超帽 ⇒ **REJECT**（fail-closed）：`PromptInjectionGuardError("ttl_seconds exceeds policy cap of 2592000s")`；now-过去复活 ⇒ 缺陷须修（now < reviewed_at 不得算 fresh，按 tampered/clock-anomaly fail-closed）；零生产写、无 git |
| OWNER_DECISIONS.md §十九 | `.planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md:439` | 逐字：「**TTL 定值 = 选项 A：30 天（86400×30）为 policy 上限**——依 OPEN-6 C6 机制（TTL 上限由 policy_hash 绑定策略固定、调用方 now/ttl 只可收紧）落产品策略；调用方可收紧至 1d/1h 等；改值仅需 owner 一句话。」 |
| OPEN-6 裁定 C6 | `execution_runs/T2-SIM-OPEN6-SEC/a20260922-01/ruling.md:172` | 逐字：「**新鲜度不可由调用方放宽**：回执 TTL 上限由 `policy_hash` 绑定的策略固定；调用方传入的 `now`/`ttl` 只能收紧、不能放宽」；负例：「`ttl=∞` / `now=过去` 复活已过期回执 ⇒ 被拒或被策略上限截断」 |
| OPEN-6 现状核验 | 同上 `:215` | 「L168 `now_seconds - reviewed_at > ttl_seconds` 纯调用方比较、**无策略侧上限**」⇒ 现状=调用方可无限放宽 |
| OPEN-4 裁定 4c | `execution_runs/T2-SIM-OPEN4-WIKI/a20260922-01/ruling.md:63,116-127` | 双绑定 + 策略变更后旧回执失效：policy **内容**变 ⇒ 失效（`ignored` → `not_reviewed`），读取时失效；OPEN-4 明文「**TTL 的数值不由本裁定规范**」（`:137,:194`）⇒ 数值归本卡（§十九 选项 A） |
| 被测现状（只读取证） | `company-wiki/src/company_wiki/source_catalog/prompt_injection_guard.py` | `_freshness` L159-173：`now_seconds - reviewed_at > ttl_seconds`（L168），仅 `ttl_seconds < 0` 校验（L195-196），**无策略上限、无 now<reviewed_at 防护**；`readiness_graph.py` L96-103/L115/L132 原样透传 |

## 1. 冻结契约要点（逐条 → 期望）

1. **策略常量**：模块级 `POLICY_RECEIPT_TTL_CAP_SECONDS = 86400 * 30`（== 2592000），位于
   `prompt_injection_guard.py`，加入 `__all__`；docstring/注释声明其为 **policy_hash 覆盖的策略面**——
   改值 = 策略变更 ⇒ 旧回执按 OPEN-4 4c 失效（全量重审）。
2. **超帽 ⇒ REJECT（卡面钦定，fail-closed，严于「截断」）**：`evaluate_review` 输入校验序
   （sha256 格式 → ttl>=0 → **ttl<=cap**）在读 receipt **之前**；`ttl_seconds > cap` ⇒
   `PromptInjectionGuardError("ttl_seconds exceeds policy cap of 2592000s")`（**逐字**钉住）。
   `== cap` 合法（可收紧到 cap 本身；现产品测试全部用 `86400*30`，必须继续合法）。
3. **now 只可收紧**：`now < reviewed_at` ⇒ **绝不算 fresh**，fail-closed 为
   `status="not_reviewed", cache_state="tampered"`，reason 含 `reviewed_at`（clock-anomaly）；
   `now == reviewed_at`（age 0）⇒ fresh（`<` 边界，不 reject）。已过期回执 + 调用方传**过去 now**
   ⇒ 不复活（tampered，而非 hit）。该检查与 cap 检查**独立**（now-过去 + ttl 合法也必须 fail closed）。
4. **NaN/inf 宽度旁路（由「不能放宽」直接推导，预登记）**：`ttl=inf` ⇒ inf > cap ⇒ 同超帽 reject；
   `ttl=NaN` ⇒ 现状比较全为 False ⇒ 永不过期 = 无限放宽 ⇒ 须 reject（同一超帽错误路径：
   非有限数不能证明 ≤ cap，按超帽/非法 fail-closed；接受的错误文本只要求含 `ttl_seconds`）。
5. **透传继承**：`evaluate_readiness`/`_safety_verdict`（readiness_graph）原样透传 ⇒ 超帽调用在
   safety 阶段即抛同一异常（卡面：passthrough callers inherit the cap），**不**在 readiness 侧兜底改写。
6. **调用点审计（冻结于本文件；实测已 grep 全仓）**：产品测试**无任何 >cap 调用** ⇒ 零测试编辑；
   `==cap`（86400×30）与收紧值（1/60/3600/86400）全部保持合法。详见 §4。
7. **非目标**：不改 `_SAFETY_MAP` 文案、不改 `RULESET_HASH` 计算、不改 receipt 写入路径、
   不动 `llm_summarizer` 出口缺口（W05 已另卡）、零生产写、无 git。

## 2. 可失败用例（冻结判据；RED=旧代码失败 / GREEN=修复通过 / MUT=翻一个 guard 红对应用例）

| ID | 类 | 输入（frozen） | 冻结期望 |
|---|---|---|---|
| **TTL-C0** | 契约面 | `import prompt_injection_guard` | 存在 `POLICY_RECEIPT_TTL_CAP_SECONDS == 86400*30 == 2592000` 且在 `__all__` |
| **TTL-N1** | C6 负例 ttl=∞类 | 有效 receipt，`ttl_seconds=86400*365` | raise `PromptInjectionGuardError`，消息**逐字** `ttl_seconds exceeds policy cap of 2592000s` |
| **TTL-N2** | 超帽 1 秒 | `ttl_seconds=2592001` | 同上（逐字） |
| **TTL-N3** | 超帽 1 天 | `ttl_seconds=86400*31` | 同上（逐字） |
| **TTL-N9** | inf | `ttl_seconds=float("inf")` | raise `PromptInjectionGuardError`（超帽/非法 fail-closed） |
| **TTL-N8** | NaN 旁路 | `ttl_seconds=float("nan")` | raise `PromptInjectionGuardError`（NaN 不可证 ≤cap ⇒ fail-closed） |
| **TTL-P1** | 边界合法 | `ttl_seconds=2592000`（== cap），receipt fresh+bound | `cache_state="hit"`、`status="not_detected"`（**不** raise） |
| **TTL-P2** | 收紧 1d | receipt age=1d，`ttl_seconds=86400`（严格 > 边界：age>ttl） | `cache_state="expired"`（收紧生效，不 raise） |
| **TTL-N4** | 负值（现行为） | `ttl_seconds=-1` | raise，消息含 `must be >= 0` |
| **TTL-N5** | **now-过去复活（缺陷探针）** | receipt `reviewed_at=2026-01-01`，真 now=2026-08-02、ttl=30d ⇒ 本应 expired；调用方传 `now=2026-01-10T00:00:00Z`（过去）+ `ttl=86400*30` | **不复活**：`status="not_reviewed"`, `cache_state="tampered"`，reason 含 `reviewed_at`（**非** hit/expired） |
| **TTL-N6** | now-过去（本就 fresh 的回执） | `reviewed_at=2026-08-01`，`now=2026-07-01`（< reviewed_at），ttl=30d | 同 N5：tampered / not_reviewed（now<reviewed_at 一律不 fresh） |
| **TTL-P3** | age 0 边界 | `now == reviewed_at`，ttl=cap | `cache_state="hit"`（`<` 边界不 reject） |
| **TTL-P4** | 正常前向 now | `reviewed_at=2026-08-01`, `now=2026-08-02`, ttl=cap | `hit`（回归保持） |
| **TTL-P5** | policy 变（回归） | `policy_hash="c"*64`, ttl=cap | `cache_state="ignored"`（OPEN-4 4c 回归不破） |
| **TTL-G1** | 透传继承 | `evaluate_readiness(..., ttl_seconds=86400*365)` | raise 同一 `PromptInjectionGuardError`（透传继承 cap） |
| **TTL-G2** | 透传回归 | `evaluate_readiness(..., ttl_seconds=86400*30)` on 已 seed 源 | 正常返回 `ReadinessDecision`（`safety_cache_state="hit"`，不 raise） |
| **TTL-R1** | 产品回归 before | `tests/unit/test_prompt_injection_guard.py` + `tests/unit/test_readiness_graph.py` 全量（iso 拷贝、%TEMP% 运行） | 全绿（现状基线；`==cap` 调用合法） |
| **TTL-R2** | 产品回归 after | 同上，修复后 | 全绿（零测试编辑仍全绿） |

**预登记缺陷假设**（读码推导，先于测量冻结）：现状 L168 `now - reviewed_at > ttl`，当 `now < reviewed_at`
时差值为负 ⇒ 永不 > ttl ⇒ **fresh/hit** ⇒ 过去 now 可复活已过期回执（now 只能放宽不能收紧，违 C6）
⇒ N5/N6 在 before 上**预期 RED = 新发现缺陷**，按卡面「缺陷全修」修复后转 GREEN。

**RED/GREEN/MUT 计划**：
- RED（before=生产字节 iso 拷贝）：预期红 = C0, N1, N2, N3, N9, N8, N5, N6, G1；预期绿 = P1-P5, N4, G2, R1。
- GREEN（iso 修复）：全表绿（R2 全绿、零测试编辑）。
- **MUT-1**（移除超帽检查，其余不动）⇒ 必红：N1, N2, N3, N9, N8, G1；N5/N6 仍绿。
- **MUT-2**（移除 now<reviewed_at 检查，其余不动）⇒ 必红：N5, N6；N1-N3 仍绿。
- 一次只翻一个 guard；每轮全表留证入 `evidence/`。

## 3. 明确不在本 oracle 内（out of scope）

- 生产仓（CW/RF）任何写入、git 操作——落地由父复审后提交（既定模式）。
- `llm_summarizer` 出口未接 evaluate_review 的 W05 缺口（已另卡，wiki-audit.md:60 有据）。
- `scripts/reviewer_gate.py:26 evaluate_review`——**不同函数**（评审门，无 ttl 参数），仅入审计清单不入用例。
- 历史 attempt 证据脚本（I-06-B/I-06-A/FIX-W06-GAPS harness）——非产品调用点，只入审计清单。
- `RULESET_HASH` 计算改动 / 常量进哈希载荷——卡面只要求 docstring 声明策略面，不改哈希机制
  （自动失效 vs 声明式失效的差异如实记入 handoff.unproven）。

## 4. 调用点审计清单（冻结；grep `evaluate_review|ttl_seconds` 全仓 + RF 仓，2026-09-22）

| # | 调用点 | ttl 取值 | 判定 |
|---|---|---|---|
| 1 | `prompt_injection_guard.py:176 evaluate_review`（定义） | 入参校验 L195-196（仅 >=0） | **本卡实施点**（cap + past-now 落此） |
| 2 | `readiness_graph.py:96-103 _safety_verdict` ← `evaluate_readiness` 参数 L115、调用 L130-133 | 原样透传 | passthrough ⇒ **继承 cap，无需改** |
| 3 | `tests/unit/test_prompt_injection_guard.py`（10 处：L187/201/241/286=`86400*30`；L214/253/268=`3600`；L228=`86400`；L298=`60`；L302=`-1`） | 最大 = 86400×30 **== cap** | 合法；**无 >cap ⇒ 零测试编辑** |
| 4 | `tests/unit/test_readiness_graph.py`（`_args` L181 `TTL=86400*30` L34；L223 `ttl_seconds=1`） | == cap / 收紧 | 合法；**无 >cap ⇒ 零测试编辑** |
| 5 | `scripts/reviewer_gate.py:26 evaluate_review` + `tests/unit/test_reviewer_gate.py` | 无 ttl（不同函数） | N/A（同名异物） |
| 6 | `llm_summarizer.py:13` | 仅 docstring 提及 | 无调用 |
| 7 | revenue-forecast 仓 `evaluate_review(` | 0 命中；`ttl_seconds` 仅见 `assurance/unified_completion/uc/lock.py`、`casfile.py`（文件锁，异物异域） | N/A |
| 8 | 历史证据脚本（非产品）：`I-06-B/.../w06b_review_harness.py`（86400×30 / 3600）、`I-06-A/.../w06a2_cases.py`（86400 / 10**30 / 3600；10**30 为超帽**负例探针**）、`FIX-W06-GAPS/.../s_c7_state_domain.py`（3600） | 均 ≤ cap（w06a2 的 10**30 是探针非产品） | 非产品调用点；只报告不编辑 |
| 9 | 先例冲突记录 | `I-06-A/a20260922-02/iso/.../prompt_injection_guard.py:78 effective_receipt_ttl` = **clip** 语义（未晋升生产） | 与本卡 REJECT 语义并存冲突 ⇒ 记 decision/handoff，由父裁定归一 |

**审计结论**：产品测试 >cap 调用数 = **0** ⇒ 需要编辑的既有测试 = **0**（卡面第 3 条交付：audit first, report——已报告）。

## 5. 勘误（追加式；仍在第一次任何运行之前落笔，2026-09-22）

1. **TTL-N5 输入修正**（§2 原文的 now 取值与卡面钦定的修复检查 `now < reviewed_at` 不自洽——原写
   `now=2026-01-10 > reviewed_at=2026-01-01`，过不了 `now < reviewed_at` 检查；按卡面探针原文
   「`now_seconds - reviewed_at > ttl` with `now < reviewed_at` gives negative ⇒ NOT > ttl ⇒ fresh」重定为）：
   **reviewed_at=2026-08-01T00:00:00Z，调用方 now=2026-07-30T00:00:00Z（< reviewed_at，且对任何合法
   now≥2026-08-31 该回执已超 30d TTL ⇒ 本应 expired），ttl_seconds=86400×30** ⇒ 冻结期望不变：
   `status="not_reviewed"`, `cache_state="tampered"`, reason 含 `reviewed_at`（现行为预测=hit ⇒ RED=缺陷）。
2. **TTL-P2 输入澄清**（原行「age=1d 且 ttl=86400」在严格 `>` 判据下 age==ttl ⇒ 不过期，与期望 expired
   自相矛盾）：改为 **reviewed_at=2026-07-30T00:00:00Z, now=2026-08-02T00:00:00Z（age=3d）, ttl=86400**，
   age(259200) > ttl(86400) ⇒ 冻结期望 `cache_state="expired"`（收紧生效、不 raise）。
3. **新增 TTL-N7（结构性限制探针，预登记、非门禁）**：`now ∈ [reviewed_at, 合法 now)` 的窗口内过去 now
   （例：reviewed_at=2026-01-01, now=2026-01-10, ttl=30d，对合法 now=2026-09-22 已过期）——纯函数守卫
   **没有可信时钟**（OPEN-6 `:159/:168` 证据：now 为纯调用方入参；产品测试全用历史 now 值 ⇒ 引壁钟会
   打破全部确定性测试）⇒ 该变体在本卡修复范围**结构性不可判**。冻结处置：**必测必报**（不门禁）——
   实测现行为记入 decision 逐案表与 handoff.unproven（含不可判原因），**不得**当通过宣称；卡面钦定的
   `now < reviewed_at` 检查（N5/N6）照修不移。
4. **TTL-N8/N9 错误文本**：oracle 只冻结**异常类型** `PromptInjectionGuardError`（N1/N2/N3 仍逐字钉
   `ttl_seconds exceeds policy cap of 2592000s`）；NaN 实现可另给 `ttl_seconds must be a finite number`。
