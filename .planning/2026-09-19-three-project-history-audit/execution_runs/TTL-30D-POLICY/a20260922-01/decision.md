# decision.md — TTL-30D-POLICY / a20260922-01（2026-09-22）

## 1. 裁定依据（全部 owner 终确生效件，逐字）

| 来源 | 条款 |
|---|---|
| OWNER_DECISIONS.md §十九（`:439`） | 「**TTL 定值 = 选项 A：30 天（86400×30）为 policy 上限**——依 OPEN-6 C6 机制（TTL 上限由 policy_hash 绑定策略固定、调用方 now/ttl 只可收紧）落产品策略；调用方可收紧至 1d/1h 等；改值仅需 owner 一句话。」 |
| OPEN-6 裁定 C6（`T2-SIM-OPEN6-SEC/a20260922-01/ruling.md:172`） | 「**新鲜度不可由调用方放宽**：回执 TTL 上限由 `policy_hash` 绑定的策略固定；调用方传入的 `now`/`ttl` 只能收紧、不能放宽」；负例「`ttl=∞` / `now=过去` 复活已过期回执 ⇒ 被拒或被策略上限截断」 |
| OPEN-6 现状核验（`:215`） | 「L168 `now_seconds - reviewed_at > ttl_seconds` 纯调用方比较、**无策略侧上限**」 |
| OPEN-4 4c（`T2-SIM-OPEN4-WIKI/a20260922-01/ruling.md:63,116-127`） | policy 内容变 ⇒ 旧回执读取时失效；`:137,:194` 明文「TTL 的数值不由本裁定规范」⇒ 数值归本卡 |

## 2. 实现决策

- **D-1 REJECT（卡面钦定），非 CLIP**：`ttl_seconds > cap` ⇒ `PromptInjectionGuardError("ttl_seconds exceeds policy cap of 2592000s")`（逐字钉住）。理由：卡面「pick REJECT (fail-closed, matches「只能收紧」strictly)」；C6 负例允许「被拒**或**截断」，取更严侧。**先例冲突**：`I-06-A/a20260922-02/iso` 曾实现 clip 版 `effective_receipt_ttl`（L78/L296），**未晋升、生产两者皆无**；若两卡都拟晋升，由父归一（见 handoff.unproven U-3）。
- **D-2 强制位置**：`evaluate_review` 输入校验序（sha256 → `<0` → **`>cap`** → `isfinite`），在 `_receipt_from_store` **之前**——与既有哈希校验同序，超帽即使 receipt 缺席也拒绝（输入非法先于查库）。`_freshness` 是唯一消费者且其 docstring 声明 ttl 已被政策有界 ⇒ 「(and _freshness chain)」由唯一入口覆盖；不重复校验、不 clamp。
- **D-3 过去 now**：`_freshness` 新增 `now_seconds < reviewed_at` ⇒ `not_reviewed/tampered`，reason=「receipt reviewed_at is after now (clock anomaly; now may only tighten freshness)」；`now == reviewed_at`（age 0）仍 fresh（严格 `<` 边界，oracle P3）。
- **D-4 NaN/inf**：`inf > cap` 自然被 cap 拒（精确 cap 文案）；`NaN` 两项比较全 False ⇒ 由 `math.isfinite` 拒（`ttl_seconds must be a finite number`）。oracle 对 N8/N9 只冻结异常类型。
- **D-5 零测试编辑**：审计（evidence/caller_audit.txt）证明产品测试 >cap 调用数 = 0（最大值恰 == cap 的 `86400*30` 4 处 + readiness `TTL` 1 处；收紧值 1/60/3600/86400；`-1` 负例）⇒ **不改任何产品测试**（卡面：只有存在 >cap 测试才须改——不存在，如实报告）。
- **D-6 readiness_graph 零改动**：L96-103/L115/L132 原样透传 ⇒ 自动继承 cap（G1 实测同文案 raise）。
- **D-7 不改 RULESET_HASH 计算**：卡面只要求 docstring 声明策略面。**如实差异**：`RULESET_HASH` 载荷仅 `_RULESET_PATTERNS`（L42-58），cap 常量**不在**哈希载荷内 ⇒ 改 cap 值**不会**自动翻转 policy_hash；失效是**声明式契约**（docstring：改值=策略变更 ⇒ 按 4c 全量重审）+ 运维纪律（owner 一句话改值时执行），非密码学自动失效。升级为自动失效需把 cap 纳入哈希载荷 ⇒ 会作废全部现存回执，超出本卡授权（oracle §3 out of scope），记 handoff U-2。
- **D-8 行尾**：生产与 iso 均为 LF-only（实测 0 CRLF）⇒ diff 干净，无行尾噪声。

## 3. 逐案表（oracle 冻结判据 × 四轮实测）

图例：✅=符合冻结期望；❌=不符合；观测=非门禁记录项。RED=iso 前（生产字节）、GREEN=iso 修复后、MUT-1=移除帽/有限性校验块、MUT-2=移除 past-now 检查（一次只翻一个 guard）。

| ID | 冻结期望（摘要） | RED (before) | GREEN (after) | MUT-1 | MUT-2 |
|---|---|---|---|---|---|
| TTL-C0 | 常量==86400\*30==2592000 且入 `__all__` | ❌ 缺失 | ✅ | ✅(常量保留) | ✅ |
| TTL-N1 | ttl=86400\*365 ⇒ raise，文案逐字 `ttl_seconds exceeds policy cap of 2592000s` | ❌ 无 raise，`hit` | ✅ 逐字 raise | ❌ **红** | ✅ |
| TTL-N2 | ttl=2592001 ⇒ 同上 | ❌ `hit` | ✅ | ❌ **红** | ✅ |
| TTL-N3 | ttl=86400\*31 ⇒ 同上 | ❌ `hit` | ✅ | ❌ **红** | ✅ |
| TTL-N9 | ttl=inf ⇒ raise PGError | ❌ `hit` | ✅ | ❌ **红** | ✅ |
| TTL-N8 | ttl=NaN ⇒ raise PGError | ❌ `hit`（永不过期旁路） | ✅ | ❌ **红** | ✅ |
| TTL-N4 | ttl=-1 ⇒ raise 含 `must be >= 0` | ✅ | ✅ | ✅ | ✅ |
| TTL-P1 | ttl==cap 合法 ⇒ fresh receipt `hit` | ✅ | ✅ | ✅ | ✅ |
| TTL-P2 | 收紧：age 3d > ttl 1d ⇒ `expired` | ✅ | ✅ | ✅ | ✅ |
| **TTL-N5** | **now<reviewed_at 复活探针 ⇒ tampered（绝不 hit）** | ❌ **`hit`「receipt fresh and bound」= 缺陷确认** | ✅ tampered，reason 含 `reviewed_at` | ✅ | ❌ **红** |
| **TTL-N6** | now<reviewed_at（本 fresh 回执）⇒ tampered | ❌ **`hit` = 缺陷确认** | ✅ tampered | ✅ | ❌ **红** |
| TTL-N7（非门禁） | 窗口内 past now（now≥reviewed_at）——结构性限制，必测必报 | 观测=`hit` | 观测=`hit`（未变，如预登记） | — | — |
| TTL-P3 | now==reviewed_at（age 0）⇒ hit | ✅ | ✅ | ✅ | ✅ |
| TTL-P4 | 正常前向 now ⇒ hit | ✅ | ✅ | ✅ | ✅ |
| TTL-P5 | policy_hash 变 ⇒ `ignored`（4c 回归） | ✅ | ✅ | ✅ | ✅ |
| TTL-G1 | readiness 透传 ttl=365d ⇒ 同文案 raise | ❌ 无 raise | ✅ 逐字 raise | ❌ **红** | ✅ |
| TTL-G2 | readiness ttl==cap ⇒ ReadinessDecision + `hit` | ✅ | ✅ | ✅ | ✅ |
| TTL-R1/R2 | 产品测试 before/after 全绿（**零测试编辑**） | ✅ 26 passed | ✅ 26 passed | ✅ 26 passed（**帽变异下产品测试测不出**⇒oracle 探针是唯一探测器） | — |

**门禁汇总**：RED before = **7/16 过、9 红**，红集 = 预登记 {C0,N1,N2,N3,N8,N9,N5,N6,G1} **逐项吻合**；GREEN after = **16/16**（+green_confirm 复测 16/16）；MUT-1 红集 = {N1,N2,N3,N8,N9,G1} = 冻结集；MUT-2 红集 = {N5,N6} = 冻结集。

## 4. 缺陷清单（发现即修，全部修复）

| ID | 缺陷 | 测量证据 | 修复 |
|---|---|---|---|
| DEF-1 | **无策略上限**（本卡主缺口）：调用方 ttl 无限放宽，`ttl=365d` 等被接受 | red_before N1/N2/N3/G1 无 raise、`hit`；OPEN-6 `:215` 证言 | `evaluate_review` 校验块：`> cap` ⇒ 逐字文案 raise；`isfinite` ⇒ NaN/inf 亦拒 |
| DEF-2 | **past-now 复活（新捕获，卡面预言命中）**：`now<reviewed_at` 差值为负 ⇒ 永不 expired ⇒ 过去 now 可复活任何回执 | red_before N5/N6/N7 **全 `hit`**（N5 构造=本应过期回执） | `_freshness` clock-anomaly 分支 ⇒ `tampered` fail-closed（N5/N6 翻绿）；N7 类结构性限制见 §5 |
| DEF-3 | **NaN/inf 宽度旁路**：NaN 比较全 False ⇒ 永不过期 | red_before N8/N9 `hit` | `inf` 被 cap 拒、`NaN` 被 `isfinite` 拒（N8/N9 翻绿） |

## 5. 边界与如实声明

1. **N7 结构性限制（预登记 oracle §5-3，非门禁）**：`now ∈ [reviewed_at, 合法 now)` 的窗口内过去 now（例 reviewed_at=2026-01-01、now=2026-01-10、对真 now=2026-09-22 已过期）在修复后**仍观测 `hit`**——守卫是纯函数、`now` 是唯一时间源（OPEN-6 `:159/:168` 证言），产品测试全用历史 now ⇒ 引入壁钟会打破全部确定性测试。该变体**本卡结构性不可判**，如实入 handoff.unproven U-1，不当通过宣称。
2. **声明式 vs 自动失效**（D-7）：cap 不在 RULESET_HASH 载荷内，改值失效为声明契约 + 运维纪律，非哈希自动翻转——如实入 U-2。
3. **CLIP 先例冲突**（D-1）：I-06-A iso 钳制版与本卡 REJECT 版并存，生产两者皆无；归一权在父 —— U-3。
4. **C11a rc=1 披露**：首次 diff 经 stdout 管道因 GBK 编码 `⇒` 失败（rc=1，19 行残片），改直写 UTF-8 后成功（rc=0）；残片已被完整文件覆盖，未隐藏（commands.json C11a）。
5. **`_SAFETY_MAP` 文案未改**：clock anomaly 落 `tampered` 桶，next_action=「verify source bytes and re-run…」仍指向重审（无死路），按 oracle §3 范围不动。
6. **零生产写 / 零 git**：prod guard sha256 收尾复验 = F900A13D…C08（与 before 一致）；本卡未执行任何 git 命令。

## 6. 哈希台账

| 对象 | sha256 |
|---|---|
| 生产 guard before | `F900A13D7C22FE3BD742485C6B603DE11B92A56D2414A2A046216CCD3B0B9C08` |
| **iso before**（拷贝时） | `F900A13D7C22FE3BD742485C6B603DE11B92A56D2414A2A046216CCD3B0B9C08`（== 生产） |
| **iso after**（修复后） | `142AE84838960D500528F2BD3BEE1742758152E0518E061A67ED3997CA6DD7DD` |
| 生产 guard after（收尾复验，零写证明） | `F900A13D7C22FE3BD742485C6B603DE11B92A56D2414A2A046216CCD3B0B9C08`（未变） |
| mutant m1 / m2 | `61cdab69ff6126fd92640966f4c60932790c16d82a0a81abc303e3c77305b779` / `f75eed61fc4575658dd9f89ff10179bdac4f91fab7f6a7d88d83a270a298d90f` |
| oracle.md（冻结=收尾） | `30C4B637DD174F2BCFD3C0A6778519F543C94B70C9A4E93F94EEC8551CA704C2` |
| changes.diff | `8271158BF034E6FEC60B65D48BEC173F5EE1A98AD1538D29A8DAEBCBD29FDBD3` |

## 7. 调用点审计结论（详表 = oracle §4 + evidence/caller_audit.txt）

- 产品定义点 1（guard L176）+ 透传点 1（readiness_graph L96-103←L115←L132）——透传继承，**readiness 零改动**；
- 产品测试 2 文件字面 `ttl_seconds=` 调用点共 **12 处**（test_prompt_injection_guard 10 + test_readiness_graph 2）：**最大值 == cap，>cap 计数 = 0 ⇒ 零测试编辑**；
- 同名异物 1（scripts/reviewer_gate.py 无 ttl）+ docstring 提及 1（llm_summarizer）= N/A；
- RF 仓 `evaluate_review(` 0 命中（`ttl_seconds` 全部属文件锁异域）；
- 历史证据脚本 3（I-06-B 86400\*30/3600、I-06-A 86400/10\*\*30/3600——10\*\*30 系超帽负例探针、FIX-W06-GAPS 3600）非产品调用点，只报告不编辑。
