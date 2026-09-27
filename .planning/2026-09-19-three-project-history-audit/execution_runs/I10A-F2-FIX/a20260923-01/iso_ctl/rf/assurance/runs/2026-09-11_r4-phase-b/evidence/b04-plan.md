# B04 落地计划（2026-09-12，实施前排布；**尚未实施**）

> 依据：[b-design.md](b-design.md) §B04（"路径留在诊断，引用不因搬家失效"）+ file-scope §3b（B04 = **F1 + F2**）+ `B.VR` rev1 的发现（"非首选副本不得未验证服务"已经实现，正好是 B04 的"不取另一修订"）。
> 纪律：本页只是**计划**；实施后才允许改成完成态，且必须带命令与实测输出。

## 1. 设计原文 → 现状对照

| 设计要求（§B04） | 当前现状（B02 rev2 之后） | B04 要做的事 |
|---|---|---|
| 引用 = `document_id` + `content_sha256` + locator；绝对路径与 `location_id` **只作诊断** | `SourceHandle` 带 `document_id`/`content_sha256`，`canonical_location_id`/`canonical_path` 是"当前选中副本"的诊断字段；`location_id` = `sha256(root_id + "\0" + relative_path)`（`scanner._location_id:79-80`）→ locator 可**派生**、不可反解 | 不需要给 `SourceHandle` 加字段（避免动对外 payload）；改为在**测试与文档**里把引用/定位子/诊断三层写清，并证明引用跨搬家不变 |
| 搬家 → 新 location 行；旧行按 `location_status` 标记（`moved`/`missing`） | 旧行由 scanner 标 `missing`（`scanner.py:1203`）；B02 的资格段 2 把非 `active` 行排除 → 解析会在合格集合上重新定位 | **L07 用例**：同 root 内搬家 + 重扫 → `REUSED_EXACT`，`document_id`/`content_sha256` 不变、`download_required=false`，而 locator/路径变化（= 引用不变、定位子变化） |
| 找不到任何合格副本 → `unavailable`；**不取另一修订** | B02 rev2 已实现：候选限定在文档自身 `source_id` 组内，非首选副本必须字节验证通过，否则不返回句柄 | **L03 负例**：把同版本副本全部移除后，即使目录里存在**另一修订**的可读副本，也必须 `MISSING`（且 trace 指明原因） |
| 旧引用仍可解引用（v0.1.1 / A-VR-02 指 `scanner.py:1123-1131` 的 `ON CONFLICT(root_id,relative_path) DO UPDATE SET source_id=…,document_id=…` 会**改指**同一行，使被取代修订不再可打开） | 该 upsert 落在 `:1120-1131`，**既不在 F3（`:1007-1099`）也不在 F1/F2** → 按 file-scope，B **无权修改** | **验证并登记**：用负例测出实际行为（覆盖同名新修订后旧引用还能否解引用），把结果写成 findings；若确实不可解引用，登记为**独立工作包**（与 R-6 的 6 处排序锚点同类处置），不在 B04 内"顺手改" |

## 2. 实施步骤（每步一个 commit 前的检查点）

1. **F10 新测试**（同一文件继续追加，或新增 `test_r4b04_*`）：L07 搬家正例、L03 负例、locator/引用分层断言。
2. 只在**测试暴露真实缺陷**时才动 F1/F2；否则 B04 的交付物就是"验收 + findings + 记录"，不制造无谓改动（避免复杂度/覆盖率与 payload 风险）。
3. 复跑：新用例、determinism/sql_pushdown/zr403/fail_closed、FC-1201 门、复杂度棘轮、`ruff`；**全量 + 覆盖率**（`FC1204_COVERAGE_GATE=1`，注意仓库里 `coverage.json` 是陈旧跟踪文件，必须先跑 `--cov`）。
4. 独立复审（`B.VR`，新会话）→ 处理意见 → 提交/推送/CI。

## 3. 风险与边界

- **不改** `scanner.py`（搬家行为由它决定，但它不在 B04 的 allowed 落点）。
- **不动** `SourceHandle` 字段（`B-payload-hash` 目前不可执行，任何字段增删都必须先冻结基线）。
- 若 L07 显示"旧引用不可解引用"，**不得**通过放宽资格（例如允许非 `active` 行、或允许未验证副本）来"修好"它 —— 那会直接违反 O03（位置变化不能洗掉安全拒绝）与 B02 rev2 的硬门。
