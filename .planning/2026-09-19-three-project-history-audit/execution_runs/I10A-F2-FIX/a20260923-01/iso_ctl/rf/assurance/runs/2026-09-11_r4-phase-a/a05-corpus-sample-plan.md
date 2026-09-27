# A05 真实语料样本选择计划（corpus sample plan）—— 待 owner 逐项确认

> 依据：执行计划 §A05「独立 Data-Agent 从真实资料挑报告和版本，标公司/期间/页码/原 hash；缺 URL 保留 unknown 与本地导入 provenance」→ 交付 `corpus-manifest` + 独立 oracle。
> 现状：**A05 未执行**。本轮只交付**选择规则 + 精确清单模板 + 待批只读命令**；真正的挑选需要一次**只读**生产 catalog 访问（[command-manifest-readonly.json](command-manifest-readonly.json)），且样本清单须 owner 逐项确认（门 G7）。

## 1. 为什么需要"真实样本"而不是随手挑几份

A05 的产物是后续 A06 基线、B08/B09 真实读取与 B.VR/AR 的**共同输入**。矩阵对它有硬要求：

- 缺下载 URL / 捕获日志时，**保留 unknown 与本地导入 provenance**，**不得合成补位**（"真实资料缺失 blocked，不 synthetic 补位"）；
- 同一 `document_id` 的不同版本必须**能区分同字节副本与真实修订**（A04 R5/R4）；
- oracle 必须**独立于被测提取器**（handbook §4：不导入被测提取器来造期望）。

## 2. 选择规则（将被写成 `corpus-manifest.json`）

| 维度 | 规则 | 目的 |
|---|---|---|
| 覆盖面 | 四个已批准 root **每个至少 1 份**；`company_raw` 至少 2 份（含 1 份多版本） | 覆盖 L02/L04 的"每 root 真实成功/缺口单列" |
| 版本集 | 至少 1 个 `document_id` 有 **≥2 个不同 `source_hash`**（真实修订）+ **≥2 个同 hash 副本**（exact copy） | L03/L07/L01 的真实数据基础 |
| 元数据面 | 至少 1 份**字段完整**、1 份**缺字段**、1 份**字段冲突** | L08 |
| 缺 URL 面 | 至少 1 份**只有本地导入 provenance、无 https_url** | L09（preview vs 正式输入的分离） |
| 能力面 | 至少 1 份**原文 ready 但文本/sections 缺失** | L10 |
| 规模面 | 单份 ≤ 50 MB（避免超大样本掩盖超时问题）；另登记 1 份**超大文件的存在性**（只登记不读） | L06 的"超大文件"要能分层测 |
| 隐私面 | 全部样本来自 `privacy_class: public` 的 root（owner 2026-09-03 决定的现状），**不引入 private 样本** | 与 A02 C3 现状一致 |

**每个样本必填字段**：`root_id` / `document_id` / `source_id` / `content_sha256` / `relative_path` / `reporting_period` / `as_of_date` / `original_url`（缺失即 `unknown` + 本地导入说明）/ `locator`（页码/表格锚点若有）/ `picked_by`（独立 Data-Agent ID）/ `picked_at` / `why`（覆盖哪个矩阵 ID）。

## 3. 独立 oracle 的要求（A05 的后半段）

1. 由**独立 subagent**（非本合同作者）执行挑选与标注，产物写入本目录 `corpus/`；
2. oracle 只使用**真实字节 + 独立计算**（页数/表格数/期间/单位用手工或 Decimal 复核），**不调用被测提取器**；
3. 每份样本给出：**期望识别结果**（公司/期间/文档类型）与其**依据片段**（原文位置）；
4. 无法判定的字段写 `unknown` 并说明为何不可判（不得猜测）。

## 4. 已知限制（必须随 manifest 一起披露）

- 生产 catalog 为 **49,677,344,768 B**；本步**只做定点查询**，禁止全库扫描（`--limit` 与本文件 §2 的规模面共同约束）。
- `dropbox_stock` root 的样本可能涉及云占位文件（OneDrive/Dropbox 占位）→ 若命中占位，**记为 L06 的真实样本**，不强行下载。
- 真实 URL 可能已失效：**保留原 URL 与其抓取时间**，不替换为"看起来对"的新 URL。

## 5. 交付顺序

1. owner 确认本文件与 [command-manifest-readonly.json](command-manifest-readonly.json)（门 G7 + G8 的隔离方式）；
2. 独立 Data-Agent 按 §2 挑选 → `corpus/corpus-manifest.json` + `corpus/oracle.json`；
3. A06 用该 manifest 冻结 L01–L12 的"真实本地"基线；
4. B08/B09 复用同一 manifest（同一批真实字节，不重复下载）。
