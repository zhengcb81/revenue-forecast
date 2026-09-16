# B10 增量 1 实施记录：读取链注册表 + v1 adapter 收敛 + 收敛门（含变异证明）

> 计划：[packages/b10-plan.md](../packages/b10-plan.md) §3 · 侦察基线：[packages/b10-recon.md](../packages/b10-recon.md)
> 范围：**B10-1（注册表 + 机器导出基线）、B10-2（实现级重复收敛）、B10-4 的门部分（claim-level adapter 声明与"从不读字节"守卫）**
> **未做**：B10-3 的 9 个 confirmed 站点批量收敛（分批进行；每批定点用例 + 契约套件，行为一变即停）

## 1. 产品改动（wiki，2 改 + 1 新 + 1 新测试）

| 文件 | 改动 |
|---|---|
| `src/company_wiki/source_catalog/read_chain.py` | **新增**：`READ_CHAIN_VERSION="1"`、`SINGLE_READ_CHAIN=…store.metadata_object`、`LEGACY_READ_ADAPTERS`（3 条：`service._read_shared_metadata`、`reader.ReadOnlyCatalogReader.resolve_handle`、`…bundle`，每条带 `version`/`semantics`/`byte_level`/`removal_condition`）、`CONFIRMED_DIRECT_READERS`（9，机器导出）、`HEURISTIC_READER_CANDIDATES`（9，**只报告不强制**） |
| `src/company_wiki/source_catalog/service.py` | `_read_shared_metadata` 由"第二份实现"改为 `return metadata_object(raw)`（**单一链**）；import 增补 `metadata_object`。行为等价已实测（8 个病理输入逐一相等，含深嵌套 `RecursionError` 路径与非对象 JSON） |
| `tests/contract/test_b10_read_chain.py` | **新增** 7 用例（见 §2） |

**"无法兼容则停切换"落到实处**：`reader.resolve_handle`/`bundle` 是**声明级**（比对 catalog 声称的 `content_sha256`，从不打开文件），与字节级链**语义不同** ⇒ **不**把它们悄悄改指向链，而是**具名 v1 adapter** + 移除条件；门会拒绝任何"未经声明就把 claim-level 变成读字节"的改动。

## 2. 门：7 个用例各管什么

| 用例 | 管什么 |
|---|---|
| `test_b10_scan_is_not_vacuous` | 扫描必须真扫到东西；且**单一链**不得以字面 `json.loads(列)` 的形式出现（防"扫描空转也算通过"） |
| `test_b10_v1_adapter_delegates_to_the_single_chain` | v1 adapter 必须调用 `metadata_object`，且**不得**再出现 `loads`（第二份实现不许回来） |
| `test_b10_no_new_confirmed_direct_reader` | **棘轮**：新增"参数里自带该列"的直接读取者 ⇒ 红 |
| `test_b10_baseline_has_no_stale_entry` | **不许腐烂**：基线里已不存在的站点必须删掉 ⇒ 否则红 |
| `test_b10_registered_adapters_are_complete_and_importable` | 每条 adapter 必须声明 version/semantics/byte_level/removal_condition，且**符号真的存在** |
| `test_b10_claim_level_adapters_never_read_bytes`（参数化 ×2） | claim-level adapter 内**不得**出现 `open/read_bytes/read_text/read_verified_bytes` |

## 3. 变异证明（[evidence/b10-mutations.json](b10-mutations.json)，harness [evidence/b10_mutations.py](b10_mutations.py)）

**6/6 KILLED，且全部 `killed_by=assertion`**（不是靠语法错误顺带弄红）；`repository_untouched=true`；副本内基线 **7 passed**。

| 变异 | 做了什么 | 结果 |
|---|---|---|
| M1 | v1 adapter 退回自己解析（第二份实现） | KILLED（assertion） |
| M2 | 在**未登记**的符号里新增一个直接读取者 | KILLED（assertion） |
| M3 | 把一个基线站点收敛掉但**不降基线** | KILLED（assertion） |
| M4 | 让 claim-level adapter 开始读字节 | KILLED（assertion，见 §4 的"M4 存活"事故） |
| M5 | 注册表条目丢掉 `removal_condition` | KILLED（assertion） |
| M6 | 注册表指向不存在的符号 | KILLED（assertion） |

## 4. 我自己犯的两处错 + 一处**事故**（全部登记）

1. **M4 一开始存活**：我的 `_function_node` 取**第一个**同名定义 ⇒ 检查到的是 `reader.py` 里的 **Protocol 桩**，而不是真正的实现（真实现同样叫 `resolve_handle`）。这与 `FC-1301` 那次被复审判 P0 的错误**完全同类**（同名函数取第一个定义）。修法：`_function_nodes` 返回**所有**定义并逐一检查；空集合本身即失败。修后 M4 被 assertion 杀死。
2. **`HEURISTIC_READER_CANDIDATES` 第一版是凭记忆写的**：里面 4 个符号（`_selection_metadata`/`_document_metadata`/`_existing_metadata` 等）**根本不存在**。改为**机器导出的真实值**，并在代码注释里写明"第一版是凭记忆写的"。**纪律**：证据优先于记忆。
3. **事故：变异 harness 与 pre-push 门并发，把门弄红了（正确的那种红）**。
   - 发生了什么：第一版 harness **就地**修改 wiki 工作树；当时 revenue 的 pre-push 门正在跑（它要执行 wiki 测试）⇒ 门读到了**半变异**的工作树，报 `SyntaxError: expected 'except' or 'finally' block`（`section_query.py:110`，正是 M2 注入点）并**挡住推送**。
   - 事实澄清：**没有**任何文件被损坏——harness 的还原是成功的（每个文件 restore 后 sha256 相符；`section_query.py` 事后 import 正常；`git status` 只剩我有意改的 3 个文件）。**门的行为是对的**：它不该在半变异的树上放行。
   - 修法：harness 改为在**系统 temp 的副本**上做变异（只复制 `src/company_wiki` + 该测试 + `pytest.ini`），并用 `src/**/*.py` 的指纹前后相等来**证明**仓库未被触碰（`repository_untouched=true`）。现在它可以与任何东西并发运行。
   - 另加纪律：**变异/改树类工具运行时不得并发推送**——这次是"验证者不该有能力弄坏同一棵树的另一个读者"。

## 5. 本地两个 CI 步骤（与 CI 完全相同的命令）

| 步骤 | 命令 | 结果 |
|---|---|---|
| Unit tests | `python -m pytest tests/unit -q --tb=short` | **787 passed**（62.25s）→ [evidence/b10-ci-step1-unit.txt](b10-ci-step1-unit.txt) |
| Contract tests | `python -m pytest tests/contract -q --tb=short --ignore=…（CI 的 8 条 ignore 原样）` | **1896 passed, 8 skipped**（745.04s）→ [evidence/b10-ci-step2-contract.txt](b10-ci-step2-contract.txt) |

## 6. 状态与下一步

- 本增量 = **B10-1 + B10-2 + B10-4 的门部分**；**未**声明 B10 整体完成。
- 待办：**独立复审**（拟编号 `B.VR-b10`）→ 处置 → 远端 CI 全绿 → 再做 **B10-3** 的分批收敛（9 个 confirmed 站点）与 **B10-5**（可回退版本 + 移除条件入库）。
- 边界不变：**不写**任何 catalog 数据、不改消费者仓、不动冻结常量。
