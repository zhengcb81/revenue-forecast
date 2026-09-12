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

## 3. P2/P3 处置状态（**P2 已全部处理；P3 两条留在记录里**）

| # | 级别 | 状态 | 说明 |
|---|---|---|---|
| B-VR05-03 | P2 | ✅ **已定案（不扩 B05）** | 响应级 `blocked` **并入 B06/B07**（owner 2026-09-12 晚按建议通过，见 [owner-scope-decisions](../owner-scope-decisions-2026-09-12.md) S-13）；B05 只交付字段级事实 + 读侧 `metadata_status`。B06/B07 的验收里必须补"冲突 ⇒ 响应级 `blocked`" |
| B-VR05-04 | P2 | ✅ **已修（`9826b3c`）** | "声明"不再只看键存在，而是**要求扫描器实际使用的值就是该键的值**（`_declared_columns(container, values)`）；`document_kind: "10-K"` 这类被分类器忽略的值不再算声明 → 不再产生假冲突/假 `blocked`。回归用例 `test_r4b05_unmapped_metadata_value_is_not_a_declaration` |
| B-VR05-05 | P2 | ✅ **已修（`9826b3c`）** | 一致副本作为**追加来源**记录；保留值的归属从**已记录来源**读回（不再写 null）。回归用例 `test_r4b05_agreeing_captures_accumulate_and_keep_their_attribution`（并写明：内容寻址下同字节=同一 `source_id`，两条记录以 `role` 区分） |
| B-VR05-06 | P2 | ✅ **已修** | 用例数以实测为准（现 **9**），提交信息/记录/checkpoint 全部对齐 |
| B-VR05-07 | P2 | ✅ **已修（`b6a8442`）** | `published_date` 的补空也要求来源声明（`fill_requires_declared`） |
| B-VR05-08 | P3 | ✅ **已修（记录侧）** | 覆盖率门写成**两步**（先 `--cov` 再 `FC1204_COVERAGE_GATE=1`），`b02_verify.py` 对陈旧 `coverage.json` 报 SKIPPED + 年龄 |
| B-VR05-09 | P3 | ⚠️ **部分** | 形状与用例数已同步；`evidence/b05-implementation.md` §2 的个别表述（扁平形状、35 vs 30 复杂度）在下一版随文案一并核对——**已知未清** |
| B-VR05-10 | P3 | ⚠️ **未解决（登记，暂不实施）** | "不写原文"只对**值**成立（注入的 canary **键名**会作为 `fields` 名出现）；低熵值的 12 位 hash 可暴力反推。候选处置：(a) 字段名白名单/规范化；(b) 低熵值改用加盐摘要或只记来源+时间。owner 已指示简化流程 → **登记为待办**，不阻塞后续步骤 |

## 3b. 本轮 P2 修复的实测（`9826b3c`）

```
python -m pytest tests/contract/test_r4b05_metadata_provenance.py -q            -> 9 passed
python -m pytest tests/contract/test_source_catalog_canonical_writer.py \
                 tests/contract/test_source_catalog_pipeline.py -q              -> 21 passed
python -m pytest tests/ -q --cov=... --cov-branch --cov-report=json              -> 2710 passed, 7 skipped,
     1 failed：test_pytest_temp_worker_governance_fixture_is_autouse_safe（环境残留 worker；pre-change 树同样失败）
FC1204_COVERAGE_GATE=1 python -m pytest tests/contract/test_fc1204_coverage_ratchet.py -q  -> 2 passed
覆盖率：scanner.py 91.12 %（冻结底 90.5）、service.py 95.20 %
```
另：两个新用例原先钉住"条目数恰好 2"，在全量套件里因"一次扫描可能多次合并同一文档"而不稳 → 已改为断言**行为**（候选都在、verdict 为 `blocked`、一致副本不抹记录、归属不写 null），单跑与全量都通过。

## 5. 下一步（按 owner 的简化指示：**每步一轮复审**，不再逐修订开轮）

1. **B05 收敛**：P2 已全部处理；余下 B-VR05-09（个别文案）与 B-VR05-10（字段名/低熵 hash）作为**已知待办**随下一步带过；
2. 不再单独开 `B.VR` B05 rev2 —— P1/P2 的修复由**本页证据 + 下一步（B01/B03）复审抽样**覆盖（owner 2026-09-12 晚指示：减少审批与轮次）；
3. B06/B07 的验收**必须**包含 **S-13**：字段冲突 ⇒ 响应级 `blocked`（本次 owner 已批）；
4. 随后 B01 → B03 → B06 → B07。
