# {公司名称}收入预测工件 — 信任边界声明

工件版本：`forecast_version={版本标签}`（snapshot `{snapshot_id 前16位}…`）
信息截止日：{as_of_date}
编制日期：{日期}

> 本模板供所有 `/revenue-forecast` 会话交付时填充为 `TRUST_BOUNDARY.md`（随正式工件一起交付）。填充后删除本引用块。

## 1. 保证范围（本工件可证明的）

- **结构合法性**：输入通过引擎全部硬门，`--validate-only --verbose` 输出 `valid`。
- **哈希完整性**：publication receipt（`validated_input_sha256` / `validated_payload_sha256` / `receipt_sha256`）与输入、输出精确绑定；`fix_hashes.py --check` 0 drift；快照指纹自洽（`validate_snapshot` PASS）且确定性可复现。
- **语义重算**：概率合同、management target 判定、sensitivity 重跑均由引擎从冻结输入独立重算。
- **数值稳定性**：{如有修正：Phase 修正前后输出数值完全一致，变化仅限文本字段与 receipt 哈希。}

## 2. 不保证范围（引擎检查半径之外，依赖宿主信任）

- **工具调用确实发生**：`tool_call_id` / `verified_by` 为模型自填，无宿主签名事件日志。
- **搜索穷尽性**：研究覆盖与管理层沟通是否穷尽依赖代理自报。
- **来源正文在哈希前的真实性**：哈希只保证"内容与快照一致"，不保证"内容与真实世界来源一致"。
- **结论文本语义**：conclusion 措辞由代理撰写；lint 只做数字启发式告警。

## 3. P0 修正记录（{如适用；无修正则写"本工件无 P0 修正"})

| 项 | 修正内容 | 实证 |
|---|---|---|
| 17.1.1 | {…} | {grep/diff 证据} |
| … | | |

输入指纹变化：`input_sha256`（receipt 口径）{前值} → {后值}；数值输出零变化。

## 4. 已知环境性失败

- {本会话遇到的已知环境问题，如 F14 型 dayu HK 挂起、下载超时、锁竞争；写明处置与数据覆盖情况。}

## 5. 宿主验证状态

- 当前环境**无 trusted verifier / host-signed tool-event receipt**；本工件以 `formal_output_mode=formal` 交付，formal 保证范围仅限第 1 节。
- 若宿主引入事件签名机制，工件应在重新验证工具调用后升级保证强度。
