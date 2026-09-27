# B04 实施与验证记录（2026-09-12，含 `B.VR` b04 复审后的更正）

> 状态：**已实施**（F10 验收 + findings；**产品代码零改动**）+ `B.VR` b04 复审 = **accepted_with_findings**（2×P2 / 4×P3，更正已落盘）。
> 入口：本页给结论与命令；原始记录见 [b04-test-run.txt](b04-test-run.txt)（**绑定 `bc3590f`**）与 [../checkpoint.json](../checkpoint.json)。

## 1. 交付物

| 交付 | 位置 | 内容 |
|---|---|---|
| 验收用例（新增，F10） | `company-wiki/tests/contract/test_r4b04_reference_stability.py`（sha256(16) `6039984dfb394e46`，12 713 B；提交 `bc3590f`） | 4 个用例：L07 搬家正例、L07b locator 分层、L03 负例、**GAP 钉住**（scanner 改指行为） |
| 变异证据（新增） | [b04_mutation_check.py](b04_mutation_check.py) | 5 个变异（reviewer 用过的 M3/M4/M5/M6/M7）：**全部 KILLED**，跑完把产品文件还原到同一 sha256(16) |
| 发现登记 | [findings.md](findings.md) **F-B04-1**（已按复审更正）/ **F-B04-2**（新增） | F-B04-1：同路径覆盖 ⇒ 旧副本 active locator 消失 + **旧字节被物理销毁**；F-B04-2：只搬 PDF 不搬 sidecar ⇒ 掉出候选切片、`MISSING` 且 **trace 为空** |
| 行为结论 | 本页 §2/§4 | 搬家不破坏引用（成立）；"不取另一修订"（**成立，但由 pre-B02 的 provider 门保护**，见 §4.2）；"旧引用永远可解引用"（**有条件成立**，见 §4.3） |

**产品代码改动：无。** 依据（**已按复审更正**）：设计 §B04 的**目标 1、2** 在 B02 之后确实已成立，本步是合法的"只验收"步；**目标 3 不成立且在本步的 allowed 集（F1/F2）内无法修**（旧字节已被物理覆盖；改指发生在 `scanner.py:1123-1124` 对 `store.py` 唯一索引的 upsert 上，两者都在允许集之外）。原先写的"设计目标已在 B02 后成立"是**过度概括**（`B.VR` b04 的 P3 B-VR04-03），已改写。

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

## 4. 与设计的关系（**已按 `B.VR` b04 的 2×P2 更正**）

b-design §B04 的三条验收（L03/L07）中：

1. "搬家 → 新行 + 旧行标记 + 在合格集合上重新定位" —— ✅ 已由 B02 机制 + 本步验收确认；
2. "找不到任何合格副本 → unavailable；不取另一修订" —— ✅ 行为成立，**但归因必须更正**（P2 B-VR04-02）：本步 L03 用例的排除**完全来自 pre-B02 的 `provider_document_id` 强身份门**（`resolver.py:1074-1076`），**不是** B02 的 source 组限定——变异实验：删掉 provider 门 → L03 与 GAP 均失败；删掉 source 组限定 → B04 四个用例**全绿**（该限定只被 B02 自己的 `test_r4b02_other_source_group_is_never_served` 守住）。隔离实验还显示：请求**不带** `provider_document_id` 时，另一修订会被当作 `reused_equivalent` 服务出去。→ 原 §4 第 2 条把功劳记给 B02，**是错的**；
3. "旧引用仍可解引用" —— ⚠️ **有条件成立**：只要该版本在别处仍有合格副本（另一 root／另一路径）就成立（reviewer 复现：`reused_exact`、字节正确）；**同路径被覆盖且无他处副本时不成立**，且 allowed 集内无法修（F-B04-1，scanner/写面行为）。
4. 元数据级 API 不受该限制：`reader.resolve_handle(old_document_id, expected_content_sha256=old_sha)` 仍会作答（它只读 `documents`/`sources`，不看 `locations`）——所以"引用不可再解引用"的说法**不成立**，正确说法是"**需要 locator 的读路径**（resolve/bundle）没有可服务的副本"（P2 B-VR04-01，已改写 F-B04-1）。

**本步新增的两个发现**：F-B04-1（同路径覆盖 ⇒ locator 消失 + 旧字节销毁；补救 (ii) 快照 vs (iii) 合同级限制 → 待 owner 选，登记为 **S-12**）、F-B04-2（只搬 PDF 不搬 sidecar ⇒ 掉出候选切片、`MISSING` 且 **trace 为空**，静默）。

## 5. 变异证据（本步自证，补上复审指出的缺口）

`python evidence/b04_mutation_check.py --all` → **M3/M4/M5/M6/M7 全部 KILLED**（对应：删 provider 门 → L03+GAP 失败；`location_id` 改用绝对路径 → L07b 失败；location 的 `source_id` 变成路径相关 → 4 例全失败；scanner 不再标 `missing` → 4 例全失败；upsert 不再改指 `document_id` → GAP 用例失败），跑完三个产品文件**逐字节还原**（harness 断言前后 sha256(16) 相同）。
