# `OPEN6B-R2-INVENTORY-BRIDGE` · 恢复路径 (a) 取证报告（**不签署、不改裁、不解除**）

- 工位：`evidence_acquirer_r2`（证据取证工位，**非签署人**）
- 载体（新建、唯一写入面）：`execution_runs/OPEN6B-R2-INVENTORY-BRIDGE/a20260926-01/`
- 授权原文（`OPEN6B-TOLERANCE-RULING/a20260926-01/ruling_6b.md` **L95**，sha256 `e5d1efce…`）：
  > `(a) 取得**存货桥闭合证据**（在产品 / 在途 / 寄售 / 并购范围明细，OPEN-11 R6 条件2）解释 154 千克，恒等式按新口径重述后，在 0 < τ ≤ 1 单位内按 A-6.3(2) 选基础签署`
- 判据：同目录 `oracle.md`（**先冻结**，含门 0 原始输出）
- **一句话结论：路径 (a) 未达成 —— `bridge_closed = false`，`residual_explained_kg = null`（差 154 千克），判 `blocked`（合格结果），下一步建议 (c)（见 §⑤ 的限定条件）**

---

## ① 三步执行记录

### 步 0 · 门 0（真实写探针，**不采信父代理**）

在本目标目录内「建临时文件 → 回读 → 删除」三步全成功：

```
== [1] mkdir ==
created: …\execution_runs\OPEN6B-R2-INVENTORY-BRIDGE\a20260926-01
== [2] write ==
write OK bytes=92
== [3] read back ==
readback: GATE0-PROBE a20260926-01 utc=2026-09-26T13:24:43Z nonce=1fa5aee7-265f-4aee-8021-b5a22dd47ceb
readback_equals_written: True
== [4] sha256 ==
sha256: 788dfc9fb4be4a93061c7b0907328a48a61015fab0abab275d22e5241ee79392
== [5] delete ==
probe_exists_after_delete: False
== GATE0 RESULT: write=True read=True delete=True ==
```

`gate0_passed = true`；探针已删除，无残迹。**未触发**「无写权限 ⇒ 立即停手」分支，**未使用任何破坏性替代**（无 `git apply`、无 `>` 重定向、无删后重写）。
基线：`git -c core.quotepath=false diff HEAD --name-only` ⇒ 总 3830 行、**非 `.planning` = 0**。

### 步 1 · 回源读（逐字，不采信派单转述）

| 源 | 关键逐字 | sha256（本工位现算） |
|---|---|---|
| `ruling_6b.md` L66/L104 | `Q3 · R2 … → 不补登，NOT_SIGNED (insufficient_evidence)`；`R2 … 实测 154 千克 … NOT_SIGNED` | `e5d1efce3821c252d0da18b7cd5734192993328f03da6c918eaa42db417ee3df` |
| `ruling_6b.md` L148 | `R2 金 1,734 + 82,743 − 83,161 = 1,316 ; 期末 1,470 ⇒ Δ = +154 千克` | 同上 |
| `ruling_6b.md` L79–L81 | 可容带 `0 < τ ≤ 1 单位`、覆盖带 `τ ≥ 154 千克`、**交集为空** | 同上 |
| `ruling_6b.md` L94–L97 | 三条互斥恢复路径 (a)/(b)/(c)；(a) 为本卡授权 | 同上 |
| `ruling_6b.md` L110 | `整条 BLOCKED-6b 的状态由 owner / 编排层在 R2 解决后重判` | 同上 |
| `I11A-OPEN11-IND/ruling.md` **L192**（R6 条件2） | `2. 存货桥闭合证据（在产品/在途/寄售、并购范围；state_reason L244 点名；R3 实测差 154 千克尚未解释）；` | `c02e255f67f76be9c0a38569454b64cd93f8469d9fc5244e6da2ce7cfc3bb95d` |
| `hypotheses.json` `H-CN-ZIJIN-VOL-03` | `scope = 控股并表矿山，不含非控股企业`；`falsifier_candidates = 并购范围变化 / 在途寄售库存`；`alternative_explanations = 本期销量高于产量主要来自并购标的的期初库存` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` |
| `OWNER_DECISIONS.md` §二十四 / §二十七 | 取证授权 + 「授权是许可不是动作」+ fail-closed（不造绿色样例） | `917d30efafe22065c875f8c62e2ee4a06eb60bdf6737f1b2dd1cd14405c4fdab` |
| `OPEN6H4-IND-COUNTERSIGN` Q1/Q4 | `FY2025 恰为并购并表年（藏格 2025-04-30、阿基姆 2025-04-16、瑞果多 2025-10-10 交割）`（`ruling_h4_ind.md` L177/L196/L197） | `0aef8925dac9cf2004f46af398494c40c291bb38dfa7e7e4af897010a3d7de6b` |
| `progress.md` L1244 | 网络口径（允许 `web_search`/`web_fetch`，外部证据须四件、不得冒充本地可核） | `0f7b5808f71679512a19ec16a60b7b316e0eb837093d70f3f3a75acf700b98ee` |

### 步 2 · 取证（四条线，全部回源到年报原文行号）

见 `not_closed.json → four_lines`（每条线的检索范围、命中原文、行号、`quantified_kg`、`gap_kg`）。要点：

| 线 | 查到什么（原文级） | 数量 | 差多少 |
|---|---|---|---|
| **L1 在产品** | 存货分类附注四类别（原材料/在产品/产成品/周转材料），在产品 2025 年末账面余额 **18,597,301,620 元**（2024：14,916,924,011 元）；存货政策句 `存货包括原材料、在产品、产成品和周转材料等。`（`CN-ZIJIN-2025.txt` L14789–L14851、L11652；FY2024 同附注 `evidence/CN-ZIJIN-2024.full.txt` L13027–L13063） | **无（人民币金额，全集团所有金属混合）** | **154 千克** |
| **L2 在途** | **披露中不存在该科目**：`寄售|在途物资|发出商品` 在 FY2025/FY2024 全文 **0 命中**；「在途」只命中**资金**在途；`于2025年12月31日和2024年12月31日，本集团无存货所有权受到限制的情况。`（L15031 / FY2024 L13180） | **无（查无此项）** | **154 千克** |
| **L3 寄售** | 「寄售」两期 **0 命中**。最接近的**黄金租赁**（`短期借款 8,240,133,800 / 6,935,043,150`；注1 明示租入后**当即在上海金交所卖出、到期买回归还**，属融资、不构成本集团自有黄金存货，L22066–L22144）；另 `将本集团生产的及外购的精矿加工而成冶炼金…`（L26340）说明外购精矿只进**冶炼行**、不进矿山产金行 | **无（只有人民币金额）** | **154 千克** |
| **L4 并购范围** | **三宗 FY2025 非同一控制下企业合并**：紫金金岭（Akyem）购买日 **2025-04-16**、藏格矿业 **2025-04-30**、RG 金矿（Raygorodok）**2025-10-10**（L28816–L28845）；**购买日可辨认资产中「存货」**：271,074,320 / 502,160,256 / **1,381,036,350** 元（L29018–L29024）；并购当年金产量归属：阿基姆 **5,088 千克**、瑞果多 **1,236 千克**（L2644–L2647、L2692–L2695）；FY2024 唯一黄金并购 La Arena（2024-12-03）**不构成业务**⇒ 无购买日资产负债表（`evidence/CN-ZIJIN-2024.full.txt` L22517） | **无（人民币金额；无任何千克/吨）** | **154 千克** |

**方向性**：L4 的机制（并购取得的黄金存货进入期末库存、却不计入本期「生产量」）与残差**正号一致** ⇒ 机制可能成立；但**数量从未披露** ⇒ 按 `oracle.md` C1 **不可量化即不闭合**。

### 步 3 · 判（闭合 / 未闭合）

**未闭合 ⇒ 落 `not_closed.json`**（`oracle.md` §5 触发 **B1 + B2**）。

---

## ② 闭合计算（含跨年结构检验）

### 2.1 目标恒等式与实测

```
原口径   期末 = 期初 + 生产量 − 销售量 + ε
FY2025 金：1,470 =? 1,734 + 82,743 − 83,161 = 1,316  ⇒ ε = +154 千克   （本工位复算，与 ruling_6b L148 逐字一致）
新口径   期末 = 期初 + 生产量 − 销售量 + Σ Aᵢ
        ⇒ 需要 Σ Aᵢ = 154 千克（容许 ±1 千克，A-6.2 上限 g = 1 千克）
实测     Σ Aᵢ = **无任何满足 C1 的项**  ⇒ |154 − ΣAᵢ| = 154 千克 > 1 千克 ⇒ C4 不成立
```

| 判据 | 结果 | 依据 |
|---|---|---|
| C1 可量化 | **FAIL** | 四条线全部只有人民币金额 / 定性叙述 / 查无此项 |
| C2 来源可核 | 就已找到的项 PASS | 本地行号 + 逐字引文 + sha256 齐；外部四件齐（`provenance.json`）但**无量** |
| C3 方向 | PASS | 并购取得存货 → 期末高于桥值（正号） |
| C4 残差进帽 | **不可评估 / 实际 154 > 1** | ΣAᵢ = null |
| C5 同口径 | PASS | 命中项均来自控股并表口径表与合并附注 |

⇒ `bridge_closed = false`，`residual_explained_kg = null`，`suggested_tau_basis = null`。

### 2.2 跨年结构检验（本工位自算；**非引用对照表**）

同一张「②产销量情况分析表」**两年 × 8 行 = 16 个**检验（FY2025 期初取 FY2024 披露期末；FY2024 期初由该表同比% 反推，标 `derived`）：

| 年 | 行 | 残差 |
|---|---|---|
| FY2025 | **矿山产金** | **+154 千克** |
| FY2025 | 铜 / 锌 / 银 / 铁精矿 / 冶炼金 / 冶炼产铜 / 冶炼产锌 | +1 / 0 / −1 / 0 / +1 / +1 / 0 |
| FY2024 | **矿山产金** | **+93 千克**（期初 1,152 由 `+50.52%` 唯一反推：1,734/1,152 = 1.505208） |
| FY2024 | 铜 / 锌 / 银 / 铁精矿 / 冶炼金 / 冶炼产铜 / 冶炼产锌 | +1 / 0 / 0 / 0 / 0 / −1 / 0 |

- **16 个检验中 14 个落在 ±1 单位（A-6.2 帽内）**；只有**「矿山产金」连续两年超帽**：FY2024 **+93**、FY2025 **+154**（两年合计 **+247 千克**）。
- 两年**恰好都是黄金并购交割年**：FY2024 La Arena（2024-12-03）、FY2025 阿基姆（2025-04-16）+ 藏格（2025-04-30）+ 瑞果多（2025-10-10）。
- ⇒ 结论：**机制（并购并表取得的黄金存货）与观测方向一致且跨年可复现；但数量在任何一年都未被披露** ⇒ 机制可解释、**数量不可闭合**。
- 补充量级上界（**reviewer 自算，按 `oracle.md` §4.3-4 不得作为承重证据**）：两宗黄金并购购买日存货合计 271,074,320 + 1,381,036,350 = 1,652,110,670 元 ÷ 810.17 元/克（FY2025 金锭不含税单价，L3960）≈ **2,039 千克（上界，假设存货 100% 为黄金，实际必然更低）** ⇒ 154 千克落在 [0, 2039] 内，**可能但未知**。

---

## ③ 红绿变异（判别力；协议见 `oracle.md §⑥`；`python -c` 内联，未落盘脚本）

**判据实现**：`closes(items)` = C1 ∧ C2 ∧ C3 ∧ C4 ∧ C5（`TARGET=154, CAP=1`）。

| 变异 | 期望 | rc | 实际检出点 |
|---|---|---|---|
| **绿 `g1_real_bundle`**（154 千克 + 完整本地锚 + 同口径） | **closes = true** | **0** | 通过 |
| `m1_qualitative_only`（只有定性、无量） | false | **0** | `C1:item0_not_quantified` |
| `m2_unanchored_number`（有 154 无锚） | false | **0** | `C2:item0_no_anchor` |
| `m3_rounding_scale`（舍入级 0.3088 千克） | false | **0** | `C3`（0 不是正流入） |
| `m3b_rounding_1kg`（帽内最大 1 千克） | false | **0** | `C4:residual=153` |
| `m4_external_no_provenance`（外部件缺 UTC/sha） | false | **0** | `C2:item0_external_e2` |
| `m5_wrong_direction`（−154 千克） | false | **0** | `C3:item0_wrong_direction` |
| `m6_scope_mismatch`（摘要口径项） | false | **0** | `C5:item0_scope_mismatch` |
| `m7_short_by_12kg`（只解释 142） | false | **0** | `C4:residual=12` |

**判据在真实证据上的实判**（不是构造样本）：

```
REAL_all_four_lines_as_found      closes=False  why=C1:no_items
REAL_L4_acquired_inventory_yuan   closes=False  why=C1:item0_not_quantified   (2,154,270,826 元 ≠ 千克)
```

⇒ **绿 rc = 0，8 个红变异 rc 全 = 0，`ALL_MUTANTS_DETECTED = true`**；且判据对**真实四线证据**给出 `false` —— 判别力与结论一致。

---

## ④ 下一步：该走 (b) 还是 (c)

**建议：(c)**，理由三条（均可复核）：

1. 残差是**结构性、跨年、金行专属**（+93 / +154 千克，是 1 千克披露粒度的 93–154 倍），**不是舍入** ⇒ A-6.3(2)(i)「来源披露舍入粒度」根本无法为 τ≥154 承重；
2. 四条线**给不出任何数量** ⇒ 即使走 (b) 也无法选值：A-6.3 四要件缺「**可核基础**」，任何 `τ ≥ 154` 都是无基础放大（`ruling_6b.md` §6.1-3 已拒同型方案）；
3. 因此 **(a) 已实证不可达、(b) 目前同样无法完成**，(c)「结构差无法解释」与实测最吻合。

**必须同时提请注意的限定（我不执行）**：`hypotheses.json` **L315 `revert_rule`** 的两个字面触发条件实测**均不成立** ——
① `销售量 > 生产量 + 期初库存`：`83,161 ≤ 878,180+…` 金为 `83,161 ≤ 84,477`（未超）；② `与库存量同比变动方向相反`：方向**一致**（库存下降）。
⇒ 执行 (c) 需要 **owner / 编排层**先确认「**无法凑平 ⇒ 口径不一致**」这一支是否适用，或先修订 `revert_rule`；**该写入属实现者/编排层，本工位一字节不写**（`ruling_6b.md` L97 已划界）。

**(b) 何时才成立**：同时满足 ① owner 按 **DEC-14** 修订 A-6.2（含 I-11-A / I-11-C 校验器同步），**且** ② 另行取得可核的黄金存货**数量**（公司披露 / 申报文件 / 可核第三方），使 τ 有 A-6.3 基础。缺任一条，(b) 都会退化为「为解锁而签」。

**何时可重开 (a)**：任一年出现下列之一即可按 `oracle.md §3.2` 重评 —— 按金属拆分的期末存货数量（千克）、并购标的购买日存货**重量**明细、产销量表新增「在产品/在途/寄售」数量列。

---

## ⑤ 给会计 reviewer 的**会签提请**（`ruling_6b.md` L18 后半「行业 reviewer 会签」的对应一步）

> 提请对象：`accounting_reviewer`（`OPEN6B-TOLERANCE-RULING/a20260926-01` 裁定人）
> 提请性质：**证据移交 + 会签请求**，**不是**签署、**不是**解锁

1. **请确认**：路径 (a) 已按 L95 执行并**未达成** —— 证据见本目录 `not_closed.json`（四条线各查到什么、各差 154 千克）、`provenance.json`（外部四件 + 本地 sha）。
2. **请确认**：`R2 = H-CN-ZIJIN-VOL-03` 维持 **`NOT_SIGNED (insufficient_evidence)`**；`τ` **本工位未签、不建议任何数值**（`suggested_tau_basis = null`）。
3. **请裁定/会签** §④ 的下一步指向：**首选 (c)**，并请就 `revert_rule` 字面触发条件未成立这一点给出会计面意见（是否可按「无法凑平」支执行）；**若选择 (b)**，请同时说明 A-6.2 修订后 τ 的**可核基础**从何而来（当前四条线均给不出数量）。
4. **请复核**本工位自算的跨年结构检验（16 个「行×年」检验、14 个帽内、仅金行连续两年 +93/+154）—— 若该复算有误，请指出行号与算式，本工位在**新版本**更正（不回改既有文件）。
5. **本工位明示不做的**：不签 τ、不写 `tolerance_signed.json`、不改 `ruling_6b.md`、不产生 `ACCEPT`、不解除 `BLOCKED-6b/6a/6c`、不改 `threshold_basis` / `threshold_review_status`、不执行 (c) 的写入、不代 owner 修订 A-6.2。

---

## ⑥ 交付自检

- **写入面**：仅 `execution_runs/OPEN6B-R2-INVENTORY-BRIDGE/a20260926-01/`（`oracle.md`、`not_closed.json`、`provenance.json`、`ruling_r2_path_a.md`、`handoff.json`、`evidence/CN-ZIJIN-2024.full.txt`）。
- **产品仓只读**：`company-wiki` 两份 PDF 仅只读取文，`pdftotext` 输出**只落本目录**；**未写产品仓任何字节**（未触发 filing-fetch 分支）。
- **零 git 写**：无 `add/commit/checkout/stash/restore/reset`；**未执行 `git status`**；收尾用 `git -c core.quotepath=false diff HEAD --name-only` 计数（非 `.planning` 必须 = 0）。
- **只读确认**：`OPEN6B-TOLERANCE-RULING`（`ruling_6b.md` sha `e5d1efce…` 前后一致）、`OPEN6-TOLERANCE-TABLE`、`I11A-OPEN11-IND`、`I-11-A`、`I-10-A`、`OWNER_DECISIONS.md` 全程未改。
- **网络**：`web_search` 工具故障（EXT-04，如实登记）；`web_fetch` 成功 3 次（EXT-01/02）+ 1 次 content-type 拒绝（EXT-03）；pwsh 直连 HTTPS 被拒（EXT-05）——**均落 `provenance.json`**，外部一律标 `external_retrieval_not_local`，**不冒充本地可核**。
