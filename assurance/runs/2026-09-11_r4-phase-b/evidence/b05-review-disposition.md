# B05 复审处置记录（`B.VR` B05 = **rejected**：2×P1 / 5×P2 / 3×P3）

> 审查记录：[../reviews/B.VR-b05.json](../reviews/B.VR-b05.json)（第六个独立会话；被审提交 `6909e78`/`bdd99dc`/`9db3394`）。
> 本页只写**处置状态与实测**；每条的复现命令与观察在审查记录里。

## 1. reviewer 复现通过的部分（作者数字大多为真）

- 共享列可加性：B05 前 `prefer_new` 确实整列替换并抹掉 `prompt_injection_review` + 注入的未知键；B05 后只**新增** `r4_provenance`，无键被删/改类型；`json_extract($.acquisition.fiscal_year)`、文档级 `LIKE '%acquisition%'`、收据读取均在。
- 逐列规则矩阵 (i)–(vii) **全部复现**。
- 全量 2706 passed / 7 skipped / 1 failed，唯一失败与作者在 `bc3590f` 树上的对照一致 ⇒ 环境残留（reviewer 自己也没杀 PID 2696）。
- 覆盖率与门：`scanner.py` 91.31 %（底 90.5，余量 +0.81）、`service.py` 95.20 %、`resolver.py` 87.93 %；两张棘轮表在其自测下全绿。

## 2. P1 处置（**已修，含回归用例**）

| # | 事实 | 修复 | 回归用例 |
|---|---|---|---|
| **B-VR05-01** | 冲突保留**依赖扫描顺序**：根顺序对调后 `conflicts` 从 2 变 0；同一 `scan()` 内对 `document_kind` 先记后抹；第三份"一致副本"会把候选清单永久抹掉（`_merge_columns` 逐捕获重算 + `fields.update()`） | ① `_merge_metadata_json` 改为**逐字段合并**：已记录的 `sources`/`conflicts` **只增不减**（一致副本只追加来源，不抹候选）；② 新增 `aligned_columns`：合并后把容器里**已存在的声明键**对齐到**合并后的列值**，容器不再与列自相矛盾（否则下一次扫描会拿被拒绝的值当"已声明"） | `test_r4b05_conflict_record_survives_scan_order_and_agreement`（两种根顺序的冲突记录**逐字段相同**且都 `blocked`；第三份一致副本不抹记录） |
| **B-VR05-02** | **声明值可被静默覆盖**：A（声明 `annual_report`）→ B（`prefer_new`、不声明）替换容器 → C（声明 `quarterly_report`）被判"声明压派生"直接胜出，`conflicts=[]`——根因是**声明性从"当前存储容器"重算**，而不是绑定到它标注的值 | ① 每条来源记录新增 `declared` 标志，**声明随值记录**；② 存储侧的"是否声明"优先读**已记录**的来源（`_previous_provenance_fields` + `_recorded_source`），只有 B05 之前的行才回退到读容器；③ **INSERT 也写 provenance**（否则首次捕获的声明从未落盘，第一次合并后就丢） | `test_r4b05_declaration_is_bound_to_the_value_it_labels`（A→B→C：最终 `document_kind` 仍为 `annual_report`、`conflicts` 两条、读侧 `blocked`） |

## 3. P2/P3 处置状态（**未全部完成**，逐条如实）

| # | 级别 | 状态 | 说明 |
|---|---|---|---|
| B-VR05-03 | P2 | **未解决，需 owner 裁范围** | `blocked/conflicts/provenance` 目前**没有消费者**：`resolver.resolve` 不读它们（请求被保留的 kind → `reused_equivalent` 且无冲突痕迹；请求落选 kind → 静默 `MISSING` 且 trace 为空）。设计要求**响应级** `blocked`，但响应级载体是 `resolver.py`（**F2**，不在 B05 的 allowed 对 F3+F1 内）→ 登记为**范围问题（S-13）**：由 B06/B07 承接，还是把 F2 加进 B05？ |
| B-VR05-04 | P2 | **未解决** | "声明"与"分类器实际读到的值"脱钩：sidecar 里 `document_kind='10-K'`（映射不到已知 kind、分类器忽略）仍算声明 → 假冲突/假 `blocked`。修法：声明判定应建立在**分类器实际消费的输入**上（或只认映射成功的值） |
| B-VR05-05 | P2 | **部分修复** | 来源现在会累积（逐字段只增不减）；保留值的归属改读**已记录来源**（不再一律 null）。仍未覆盖：刚补空的值仍由本轮记录、变异 M6（归属翻转）在 F10 里是否已被新用例杀死**未复测** |
| B-VR05-06 | P2 | **已修（待复核）** | "6 个验收用例"是**错的**（实为 5）；本轮新增 2 个 P1 回归后为 **7**，记录一律以实测为准 |
| B-VR05-07 | P2 | **已修** | `published_date` 的**补空**分支现在也要求来源**声明**该列（`fill_requires_declared`），文件名派生的猜测不再成为存储值 |
| B-VR05-08 | P3 | **已修（记录侧）** | 覆盖率门的命令必须写成**两步**（先 `--cov` 再 `FC1204_COVERAGE_GATE=1`）；`b02_verify.py` 已有"陈旧 coverage.json → SKIPPED + 年龄"的新鲜度处理 |
| B-VR05-09 | P3 | **部分修复** | 本轮同步了来源记录形状（新增 `declared`）与用例数；`evidence/b05-implementation.md` §2 的"扁平形状/沿用上一条记录"等表述**仍需逐句核对**（下一轮做） |
| B-VR05-10 | P3 | **未解决（登记）** | "不写原文"只对**值**成立：注入的 canary **键名**会原样出现在 `fields` 里；低熵值的 12 位 hash 可暴力反推（reviewer 从 `b2b2f104d32c` 还原出 `2025`）。候选处置：(a) 字段名做白名单/规范化；(b) 对低熵值改用**加盐**摘要或干脆只记"来源+时间" |

## 4. 复跑（本轮修复后实测）

```
python -m pytest tests/contract/test_r4b05_metadata_provenance.py -q                       -> 7 passed
python -m pytest tests/contract/test_source_catalog_canonical_writer.py \
                 tests/contract/test_source_catalog_pipeline.py -q                         -> 21 passed
python -m ruff check src tests/unit tests/contract scripts                                  -> All checks passed
```
全量与棘轮/覆盖率的**本轮数字见 [b05-implementation.md](b05-implementation.md)**（以该文件所载实测为准；本页不重复以免两处不一致）。

## 5. 下一步

1. 修 B-VR05-04（声明与分类器输入对齐）、补 B-VR05-05 的变异复测、逐句核对 B-VR05-09 的文档；
2. 就 **B-VR05-03（响应级 `blocked` 由谁交付）** 与 **S-10/S-11/S-12** 一并请 owner 裁；
3. 之后送 `B.VR` B05 rev2（新会话），复核 P1 修复与未决 P2 的处置。
