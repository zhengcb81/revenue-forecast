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

## 2. 门：11 个用例各管什么

| 用例 | 管什么 |
|---|---|
| `test_b10_scan_is_not_vacuous` | 扫描必须真扫到东西；且**单一链**不得以字面 `json.loads(列)` 的形式出现（防"扫描空转也算通过"） |
| `test_b10_v1_adapter_delegates_to_the_single_chain` | v1 adapter 必须调用 `metadata_object`，且**不得**再出现 `loads`（第二份实现不许回来） |
| `test_b10_no_new_confirmed_direct_reader` | **棘轮 ①**：新增"参数里自带该列"的直接读取者 ⇒ 红 |
| `test_b10_baseline_has_no_stale_entry` | **不许腐烂**：基线里已不存在的站点必须删掉 ⇒ 否则红 |
| `test_b10_handoff_scan_is_not_vacuous` | 棘轮 ② 的防空转 |
| `test_b10_no_new_column_value_handoff` | **棘轮 ②**：新增"把该列的值交给某个调用"的位置 ⇒ 红（**堵住 parse-by-helper 绕过**，见 §3ter） |
| `test_b10_handoff_baseline_has_no_stale_entry` | 棘轮 ② 的不许腐烂 |
| `test_b10_gate_boundaries_stay_documented` | 门的**已知边界**必须留在产品代码里且不得被悄悄删掉（每条都注明是否**实测**过） |
| `test_b10_registered_adapters_are_complete_and_importable` | 每条 adapter 必须声明 version/semantics/byte_level/removal_condition，且**符号真的存在** |
| `test_b10_claim_level_adapters_never_read_bytes`（参数化 ×2） | claim-level adapter 内**不得**出现 `open/read_bytes/read_text/read_verified_bytes` |

## 3ter. **棘轮 ②：我自己找到的门洞，以及它暴露的漏报**

- **实测出的绕过**：`_parse(raw)`（泛型参数）+ 调用点 `_parse(row["metadata_json"])` —— 调用点的被调名**不是** `loads`，而 `loads` 的实参**不是**列名 ⇒ **两处都躲开**棘轮 ①。在 temp 副本上跑门：**7 passed（放行）**。
- **它同时暴露了漏报**：把"该列的值被交给调用"列出来后，发现**生产代码里已经有 3 处**是这个形状
  （`extraction_quality._artifact_metadata`、`scanner._previous_provenance_fields`、`scanner._merge_metadata_json`）——也就是说棘轮 ① 的"9 条 confirmed"**从来不是完备清单**。
- **修法**：新增**棘轮 ② `COLUMN_VALUE_HANDOFFS`（12 条，机器导出）**：扫描"调用的实参里出现对该列的 `[...]` 取值或 `.get(列)`"的位置。只认**取值**、不认 SQL 文本（后者占"提到列名"的绝大多数：37 处 → 取值 18 处 → 去重 12 个 `module::symbol`）。
- **验证**：① 修后同一个绕过探针 ⇒ **CAUGHT**（1 failed, 9 passed）；② 新增 **M8** 变异（正是这个形状）⇒ **KILLED by assertion**；③ 门从 7 用例增到 **11 用例**，全绿。
- **仍然存在的边界（写进产品代码、并被用例钉住）**：`GATE_BOUNDARIES` 记录四种形状——`intermediate_variable`（`raw = row["metadata_json"]` 再 `parse(raw)`，**实测仍放行**）、`subscript_inside_the_callee`（下标在**被调方内部**的赋值里）、`third_party_or_alternative_parser`（`json.JSONDecoder().decode` / orjson 等）、以及已闭合的 `closed_helper_at_call_site`。
  **口径**：这两条棘轮是**对两种常见语法形状的棘轮**，**不是**数据流分析、**不是**完备性证明——所以"没有新直接读取者"这句话只在**这两种形状**内成立。

## 3. 变异证明（[evidence/b10-mutations.json](b10-mutations.json)，harness [evidence/b10_mutations.py](b10_mutations.py)）

**8/8 KILLED，且全部 `killed_by=assertion`**（不是靠语法错误顺带弄红）；`repository_untouched=true`；副本内基线 **11 passed**。

| 变异 | 做了什么 | 结果 |
|---|---|---|
| M1 | v1 adapter 退回自己解析（第二份实现） | KILLED（assertion） |
| M2 | 在**未登记**的符号里新增一个直接读取者 | KILLED（assertion） |
| M3 | 把一个基线站点收敛掉但**不降基线** | KILLED（assertion） |
| M4 | 让 claim-level adapter 开始读字节 | KILLED（assertion，见 §4 的"M4 存活"事故） |
| M5 | 注册表条目丢掉 `removal_condition` | KILLED（assertion） |
| M6 | 注册表指向不存在的符号 | KILLED（assertion） |
| **M7** | 在 **`adapters/` 子目录**里新增一个直接读取者 | **KILLED（assertion）** —— 见 §4 第 4 条：这正是我第一版扫描**看不见**的位置 |
| **M8** | **parse-by-helper 绕过**（泛型 helper + 调用点给列值） | **KILLED（assertion）** —— 棘轮 ② 生效；修前同一形状**放行**（见 §3ter） |

## 3bis. 门自己的一个洞（我自己找到并修掉）

- **洞**：`_scan_confirmed_direct_readers()` 第一版用 `SOURCE.glob("*.py")`（**不递归**），而
  `src/company_wiki/source_catalog/` 下还有一个 **`adapters/` 子目录（8 个模块）** ⇒ 在那里新增一个直接读取者**不会**触发棘轮。
- **为什么会出现**：侦察工具用的是 `rglob`（覆盖了子目录、结论没受影响），但我在写门时把"目录里的模块"理解成了"目录下的模块"。
- **修法**：扫描改 `rglob`，键改为**相对路径**（`adapters/parity.py::symbol`）以免不同目录同名文件互相碰撞；并加 **M7** 变异把这个位置钉住。
- **验证**：修后 7/7 通过、M7 被 assertion 杀死；现基线（9 条）与递归扫描结果**完全一致**（`adapters/` 里确实没有直接读取者，但这不再是"运气"，而是**被测过**的）。

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
| Unit tests | `python -m pytest tests/unit -q --tb=short` | **787 passed**（55.7s）→ [evidence/b10-ci-step1-unit.txt](b10-ci-step1-unit.txt) |
| Contract tests | `python -m pytest tests/contract -q --tb=short --ignore=…（CI 的 8 条 ignore 原样）` | **1900 passed, 8 skipped**（793.96s）→ [evidence/b10-ci-step2-contract.txt](b10-ci-step2-contract.txt) |

**口径（不夸大）**：这两次跑是在本增量**倒数第二次**修订上收集的（当时门是 11 用例；1900 = 1896 + 4）。P1 修完后的**最终**修订（门 12 用例）**只单独重跑了该门文件**（**12 passed**、ruff clean、变异 8/8），**没有**重跑整套契约套件。因此"本地两步全绿"对 11 用例修订成立；12 用例修订的对应证据是门文件本身 + 变异表。

## 7. 独立复审 `B.VR-b10`（记录 [reviews/B.VR-b10.json](../reviews/B.VR-b10.json)）

**`APPROVE_WITH_FINDINGS`（0×P0 / 1×P1 / 2×P2 / 5×P3）**。复审锚定提交态（wiki `c4a69e0`、revenue `022f481`），**未**在仓库就地变异；它自己实测出 **8 种绕门形态**（每次 7 passed），并核实了两份 CI 日志末行。

| # | 级别 | 它证明的 | 处置 |
|---|---|---|---|
| `B-VR-B10-01` | **P1** | `read_chain` 把 `reader.bundle` 声明为 claim-level/"**never opens a file**"，实测它经 `build_source_bundle → artifact_handle.validate_artifact` 对 artifact 文件 `read_bytes()` 取 sha256（改坏 artifact ⇒ 判定翻成 `artifact_hash_mismatch`）；`resolve_handle` 才是真 claim-level | **已修**：条目改写为"对**文档版本**是 claim-level，但**不是**无文件访问"，新增 `reads_files` 字段（`bundle=True`、另两条 `False`），并加用例 `test_b10_registry_states_transitive_file_access_truthfully` **钉住**；同时把原用例改名为"**语法级**身体检查、**不覆盖**传递性文件访问"并在 docstring 写明这正是 P1 的缺口 |
| `B-VR-B10-02` | P2 | `CONFIRMED_DIRECT_READERS` 自称是 `documents.metadata_json` 的读取者基线，实际按裸字符串匹配 ⇒ 混入**同名 artifacts 列**（3 个键只读 artifacts、`normalizer.normalize_catalog` 一键两列），B10-3 的收敛清单被错划 | **未修（下次第一步）**：基线要按**表**区分（documents vs artifacts），并在键上标注来源表；这不改变已交付的门行为，但会改变 B10-3 要收敛的对象 |
| `B-VR-B10-03` | P2 | 棘轮可绕：**8 种新直读形态全部放行**（别名 import、`_parse(row["metadata_json"])`、`JSONDecoder().decode`、改名后再 loads、**往已入基线的类里加方法**（键塌缩成类名）、`source_catalog/` 之外的目录、`getattr(json,"loads")`、拼接键名）；2 个正控正确变红 | **部分已修**：`COLUMN_VALUE_HANDOFFS` 闭合了助手形状（M8 钉住），但**键按 `module::symbol` 塌缩**与"类内新增方法"仍未覆盖 ⇒ 与 `GATE_BOUNDARIES` 一起**如实登记**；"键要含类+方法"列入下次修 |
| `B-VR-B10-04` | P3 | `scanner.py::_previous_provenance_fields`（1405 `loads` ← 1739 `existing_document["metadata_json"]`）是 documents 列真读取者，却不在任何清单里 | **未修**：漏报方向，列入下次（与 -02 一起做） |
| `B-VR-B10-05` | P3 | 门会对别的表、仅名字以 `_metadata_json` 结尾的列**误报**（`row["acquisition_metadata_json"]` 即红） | **未修**：与 -02 同源，下次一起修 |
| `B-VR-B10-06` | P3 | `impl.md` §3 的"6/6 KILLED"与同节 M1..M7 表、§3bis 的"7/7"、committed JSON 的 7/7 **自相矛盾** | **已修**：本节与 §3 已更新为 **8/8 / 11→12 用例**；旧数字是我边写边改留下的**陈旧记录** |
| `B-VR-B10-07` | P3 | "catch sets equivalent" **不成立**：委派后 catch 集**更窄**（24 输入中 23 个相等，唯一不等是 `__bool__` 抛裸 `ValueError` 的合成对象；唯一调用点传 sqlite TEXT ⇒ 当前不可达） | **未修**：下次改为"**行为等价的范围**"措辞并加一个用例记录该不可达差异（不引入更宽的 catch） |
| `B-VR-B10-08` | P3 | `repository_untouched` 只覆盖 `src/**/*.py`，且指纹值受行尾（LF/CRLF）影响、**不能从 git 复现** | **未修**：下次扩到整个仓（或改用 `git status --porcelain` 作为判据），并说明该值环境相关 |

**注**：本节写于本轮收尾时，**未**对 `B-VR-B10-02/03(残余)/04/05/07/08` 做代码改动——它们已逐条登记为**下次开工的第一批**。修订后门为 **12 用例、8/8 变异 KILLED by assertion**、ruff clean。

## 8. 状态与下一步

**提交与 CI**（本轮小阶段收口，**已核对**）：

| 仓 | 提交 | 远端 CI |
|---|---|---|
| company-wiki | `b829b03`（增量本体）、`c4a69e0`（门补洞 + M7）、`d92bb33`（棘轮② + 边界）、**`e36b984`（P1 修正 + 钉住）** | **`e36b984` on `master` = success**；`fcap` 同步（`c4a69e0` 亦为 success，6/6 job） |
| revenue-forecast | `1dc4c3b`、`36084a3`、`cfe4ccc`、`022f481`、**`144345b`（复审记录 + 处置）** | **`144345b` = success（`main` 与 `fcap` 双绿）** |

**本地两个 CI 步骤**见 §5（unit 787；contract 1900 passed / 8 skipped，口径已注明）。**独立复审**见 §7（`APPROVE_WITH_FINDINGS`，P1 已修，其余 6 条登记为下次第一批）。

- 本增量 = **B10-1 + B10-2 + B10-4 的门部分**；**未**声明 B10 整体完成。
- **⚠️ 独立复审尚未执行**（`B.VR-b10` 未派）。因此本增量目前的状态是"**已实施 + 本地两步 CI 绿 + 远端 CI 绿 + 变异 7/7**"，**不是**"已通过"。
  唯一未过门的是**独立复审**——这正是**下一步的第一件事**（复审对象：`read_chain.py`、`service.py` 的委托、`tests/contract/test_b10_read_chain.py`、本记录与 `b10-mutations.json`）。
- 之后：**B10-3** 分批收敛 9 个 confirmed 站点（每批定点用例 + 契约套件；行为一变即停并上呈）→ **B10-5**（可回退版本 + 移除条件入库）。
- 边界不变：**不写**任何 catalog 数据、不改消费者仓、不动冻结常量。
