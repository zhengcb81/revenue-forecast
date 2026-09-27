# 事故记录：`git apply` 删除了两个授权目标文件且本会话无法写回

- **卡**：`B2-PROMOTION / a20260926-01` ｜ **记录时点**：2026-09-26（晋升执行过程中）
- **性质**：**执行者失误 + 环境（沙箱）不可写**共同造成的**产品树完整性事故**；**晋升未完成**。

## 1. 时间线（本会话实测）

| # | 步骤 | 结果 |
|---|---|---|
| 1 | 冻结 `oracle.md` | 完成 |
| 2 | `preimage/` 落盘两文件并复算 | sha/字节 = `543d005c…`/74235、`bcbbbfd9…`/19775 **一致** |
| 3 | **零字节可写探针**：`FileMode.Open + FileAccess.Write` 开/关两文件（不写入任何字节） | **两个文件均 `Access denied`** ⇒ 预警「本会话不可写产品仓」 |
| 4 | `git apply --check -p1`（cwd=`C:\Users\郑曾波\Projects`，只读） | **rc=0** |
| 5 | `git apply -p1`（同 cwd） | **rc=128**，stderr：`error: unable to write file 'dayu-agent/dayu-agent/dayu/fins/downloaders/sec_downloader.py' mode 100644: No such file or directory` |
| 6 | 复测两文件 | **两个文件均已不存在**（`git apply` 先删除原文件、写回被拒） |
| 7 | 5 种还原手段（Copy-Item / WriteAllBytes / python copyfile / `git restore` / `git checkout-index`） | **全部被拒**（见 `rollback_procedure.md §3`） |

## 2. 关键判定

- **根因**：本会话 `workspace-write` 沙箱 **不允许对产品仓写入**（步骤 3 已在应用前实测到），而 `git apply` 在非仓库 cwd 下的写回路径**不是原子的**：它先移除/替换目标文件、再写新内容 ⇒ 写回失败 ⇒ **原文件被删、新文件未落盘**。
- **我的失误**：步骤 3 已经拿到「不可写」的明确证据，**仍执行了步骤 5 的 `git apply`**（卡面只规定 `--check` 失败才停，未把「应用阶段不可写」列为前置闸）⇒ 应把步骤 3 的探针结果**同样**当作停止条件。**若在步骤 3 停止，产品仓不会受损。**
- **未造成的损害**：未提交、未推送、未改 index（`git restore` 连 index.lock 都建不了）、未碰第三处文件、`revenue-forecast` 非 `.planning` diff = 0、复审目录 45 交付件字节零改动。
- **造成的损害**：`dayu/fins/downloaders/sec_downloader.py` 与 `company_wiki/source_catalog/dayu_cli_adapter.py` **在盘上缺失**；cw 的 `tests/contract` 三件套 collect 已报 `ModuleNotFoundError`（rc=2）。

## 3. 恢复

- **字节未丢失**：`preimage/` 两份副本已校验（sha 等于前像）；且两文件在各自 git 中被跟踪、`HEAD`/`index` 即前像。
- **执行者无写权限** ⇒ 还原须由**可写产品仓**的会话按 `rollback_procedure.md §2` 执行，复算 sha 必须回到 `543d005c…`/74235 与 `bcbbbfd9…`/19775。
- 还原后本卡状态 = **blocked（晋升未完成，两文件保持前像）**。

## 4. 给后续执行者的教训（写进卡面）

1. **可写性探针必须是「应用前置闸」**：探针被拒 ⇒ 直接判 `blocked`，**不跑 `git apply`**（`--check` 只验证 patch 能否应用，**不验证目标是否可写**）。
2. 非仓库 cwd 下的 `git apply` 失败**可能已删除目标文件** ⇒ 应用前后都必须立即复算 sha，并在失败时第一时间检查文件是否存在。
3. 推荐改为**逐仓 `git apply` + `--include` 定向 + 先 `--check`**，或干脆在可写会话执行。
