# B04 实施与验证记录（2026-09-12）

> 状态：**已实施**（F10 验收 + findings；**产品代码零改动**——这是本步设计所允许的结果，见 §2/§3）。
> 入口：本页给结论与命令；原始记录见 [b04-test-run.txt](b04-test-run.txt)（本文档同目录）与 [checkpoint.json](../checkpoint.json)。

## 1. 交付物

| 交付 | 位置 | 内容 |
|---|---|---|
| 验收用例（新增，F10） | `company-wiki/tests/contract/test_r4b04_reference_stability.py`（sha256(16) `6039984dfb394e46`，12 713 B） | 4 个用例：L07 搬家正例、L07b locator 分层、L03 负例（版本全失效且存在另一修订）、**GAP 钉住**（scanner 改指行为） |
| 发现登记 | [findings.md](findings.md) **F-B04-1** | `scanner.py:1123` 的 `ON CONFLICT(root_id,relative_path) DO UPDATE SET source_id=…,document_id=…` 会**改指**同一位置行：被取代的修订失去唯一 locator，其引用**不可再解引用**。该文件不在 B 的 allowed 集（F3 只覆盖 `:1007-1099` 的 metadata 合并），故 B04 **只验证与登记**，修复登记为**独立工作包** |
| 行为结论 | 本页 §2 | 搬家不破坏引用（已成立）；"不取另一修订"（已成立）；"旧引用永远可解引用"（**不成立**，受 §3 限制） |

**产品代码改动：无。** B04 的设计（b-design §B04）要求的是"引用不因搬家失效"，而 B02 之后该行为**已经成立**；B04 的价值是把它**验收并钉住**，而不是制造无谓改动（计划阶段已就此写明：只有测试暴露真实缺陷时才动 F1/F2，见 [b04-plan.md](b04-plan.md) §2）。

## 2. 验收结果（命令 → 实测）

| 用例 | 场景 | 结果 |
|---|---|---|
| `test_r4b04_move_within_root_keeps_the_reference` | 同一 root 内把 PDF+sidecar 移到 `…/annual/renamed/`，重扫 | `REUSED_EXACT`；`document_id`/`source_id`/`content_sha256` **完全不变**；`download_required=false`；旧行 `location_status='missing'`、新行 `active`；`canonical_location_id` 与 `canonical_path` **变化**（引用不变、定位子变） |
| `test_r4b04_location_id_is_a_pure_function_of_the_locator` | 对每条 location 行复算 | `location_id == _location_id(root_id, relative_path)`；`document_id != location_id`；句柄同时带稳定身份与 locator 诊断 |
| `test_r4b04_version_gone_is_unavailable_not_the_other_revision` | 删掉本版本全部副本，同时树里存在**另一修订**（可读、同期间、不同 `provider_document_id`） | `matches == ()`、`MISSING`；另一修订的行确实 `active`，但**没有被当作本版本服务** |
| `test_r4b04_same_path_new_revision_repoints_the_location_row` | 同一相对路径覆盖为**新修订**（sidecar 同步改 hash/provider id）+ 重扫 | 行被改指到新 document（`document_id != 旧`、`active`）；**旧修订再无任何 `active` location**；请求旧版本 → `MISSING`，trace 含 `no_canonical_active_location`；请求新版本 → `REUSED_EXACT`（`content_sha256 = 新 hash`） |

复跑命令（本次实测）：

```
python -m pytest tests/contract/test_r4b04_reference_stability.py -q
   -> 4 passed
python -m pytest -q tests/contract/test_r4b04_reference_stability.py \
    tests/contract/test_r4b02_candidate_selection.py \
    tests/contract/test_source_catalog_determinism.py \
    tests/contract/test_source_catalog_sql_pushdown.py \
    tests/contract/test_zr403_dedupe_resolver_generalization.py \
    tests/contract/test_source_catalog_fail_closed.py \
    tests/contract/test_fc1201_root_hardcode_gate.py \
    tests/contract/test_future_root_config_only.py \
    tests/contract/test_fc1204_complexity_ratchet.py
   -> 69 passed
python -m ruff check src tests/unit tests/contract scripts
   -> All checks passed!
```

## 3. 边界（本步"没做"的，以及为什么）

- **没有**修改 `scanner.py`：它不在 allowed 集（F3 只到 `:1007-1099`；位置 upsert 在 `:1123`）。"旧引用在**同路径被覆盖**后仍可解引用"**做不到**——旧字节已被物理覆盖，任何"放宽资格"的取巧都会违反 O03 与 B02 的硬门（[b04-plan.md](b04-plan.md) §3）。
- **没有**给 `SourceHandle` 加 locator 字段：引用所需的稳定身份（`document_id` + `content_sha256` + `source_id`）已在句柄里，locator（`root_id` + 相对路径）由 `location_id` 派生；加字段会动对外 payload，而 `B-payload-hash` 仍不可执行。
- **没有**做真实四 root 的搬家演练（需 G8 隔离副本 + 真实字节；属 B09/B.AR）。
- 复现"旧引用死掉"的**缓解方案**（保留快照/墓碑记录）属**写面**，需独立工作包——与 R-6 的 6 处排序锚点、F-B04-1 同类处置。

## 4. 与设计的关系

b-design §B04 的三条验收（L03/L07）中：

1. "搬家 → 新行 + 旧行标记 + 在合格集合上重新定位" —— ✅ 已由 B02 机制 + 本步验收确认；
2. "找不到任何合格副本 → unavailable；不取另一修订" —— ✅ 已由 B02 的 source 组限定 + 本步 L03 负例确认；
3. "旧引用仍可解引用" —— ⚠️ **有条件成立**：只要该版本在别处仍有合格副本（另一 root / 另一路径）就成立；**同路径被新修订覆盖后不成立**（F-B04-1，scanner 行为，B 无权改）。
