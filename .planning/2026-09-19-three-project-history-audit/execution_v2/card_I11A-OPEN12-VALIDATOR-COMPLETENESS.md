本卡按 owner 裁定新立（`OWNER_DECISIONS.md` **§二十八**，2026-09-25，选项式问答原话「**是，另立校验器专业卡（建议）**」）。先读[执行协议](START_HERE.md)、[共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)。状态 planned，运行 cwd 必须由 I-00-B 绑定。

## I11A-OPEN12-VALIDATOR-COMPLETENESS — 校验器完备性（`OPEN-12` 正解的执行卡）

Parent：I-11-A。依赖：I-11-A（已 `accepted_scoped`）。Owner：**统计 reviewer / 工程 reviewer**；独立 reviewer 复核。

**来源（回源，非转述）**：卡文 `execution_runs/I-11-A/a20260919-01/decision.md` **L408** 该行原文：

> `OPEN-12 | 独立复核指出的 P2-5/P2-6/P2-7/P2-8/P2-9 已在本 attempt 内处置（见 oracle §R2、mechanism_review §5 第 8/9 条、review.md §4）；是否需要为"校验器完备性"另立一张专业卡（统计/工程 reviewer） | PLAN owner / 统计 reviewer | 否 | I-11-C 是否复用同一校验器`

- 合并裁 `I11A-OPEN-MERGE/.../merge_ruling.md` **L362 (G3)** 逐字引上行，并注明「`OWNER_DECISIONS.md` 内未见针对 I-11-A OPEN-12 的裁定行」。
- **owner 已答「是」**（§二十八）⇒ 本卡即该「专业卡」；卡文该行的「否」以 §二十八 为准（**封盘件不回改，由本卡文承载更正**）。
- **`I-11-C 是否复用同一校验器`** = 卡文 L408 的「影响面」栏，**随本卡一并裁**。

### 本卡裁什么（唯一范围）
只裁 **`P2-5 / P2-6 / P2-7 / P2-8 / P2-9`** 这批**校验器完备性**问题。**逐条回源读原文**（不要按本卡转述办）：
1. `execution_runs/I-11-A/a20260919-01/decision.md` **L408** 该行（定义与影响面）
2. 同 attempt 的 **`oracle.md §R2`**（P2-5…P2-9 的处置记录）
3. 同 attempt 的 **`mechanism_review.md §5 第 8/9 条`**
4. 同 attempt 的 **`review.md §4`**（独立复核对 P2-5…P2-9 的发现原文）
5. `OWNER_DECISIONS.md` **§二十八**（你的授权来源与范围）

### 九步要点
1. **先冻结 `oracle.md`**（判据、变异清单、范围边界）**再跑第一次**；`expected` 手算、不由重跑生成。
2. 建 iso 隔离副本（只读源、记源 sha256）。
3. **统计/工程 reviewer 的实质工作**：逐条判定 **P2-5…P2-9 是否已在 `I-11-A` 本 attempt 内被真正处置**，以及**校验器是否完备** —— 判据是「**该族输入是否都能被校验器抓住**」，须给出**可失败用例**（能被现有校验器放行、但按规则应当被拒的输入）。
4. **红 → 绿 → 变异**：先用你构造的反例证明校验器**会漏**（红）；若判定需要补校验器，则补、再证明反例被抓住（绿）、并证明**变异会把新判据打红**。
   - 若你判定**校验器已完备**（P2-5…P2-9 处置到位）⇒ 给出**不漏的证据**（你构造的 N 个反例全部被拒），**同样要红：把校验器改弱后你的反例必须能通过**。
5. **`I-11-C 是否复用同一校验器` 一并裁**：给结论 + 理由 + 若复用需满足的条件。
6. **行不交界声明**写进 oracle（与 `I-11-A` 已签收面的关系）。
7. 产出 `changes.diff`（若需改代码，**只出 diff、不写真仓**，`src/`/`scripts/` 须逐条说明是否触碰）。
8. `handoff.json`：`status=review_pending`、`implementer_signed=false`、`unverified` 如实。
9. 只读自证 + 报父派独立复审。

### 写入边界
- **本 attempt 目录 + iso 副本**；**绝不**改 `I-11-A/a20260919-01` 任何字节（封盘）；**绝不**写 `.planning` 之外任何产品路径；禁止 git 写；**禁用 `git status`**；禁止联网。
- 结束前 `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` = **0**。

### 明确不做（执行纪律）
- **不解除 `OPEN-12`**（其 `RULED_WITH_BLOCKED_VALUE` 在本卡交付并裁定前维持）
- **不放行任何参数、不给阈值、不改 `threshold_basis`**
- **不解除任何 BLOCKED、不产生 `I-11-B` 的 ACCEPT、不产生 I-11-A 的再审**
- **不代签**；ACCEPT 只能由独立 reviewer 签

**退出**：你的判据（红/绿/变异）三者齐备 + `I-11-C 复用` 结论落地。
**恢复**：回退改动；保留你构造的全部反例与原始日志。
