# B03 实施与验证记录（2026-09-12）

> 状态：**已实施**（产品代码 1 文件 `resolver.py` + 新增验收 **13 用例**（+1 skip））。提交 **`5ab0779`**（company-wiki，`fcap` → `origin/master`）。
> 依据：设计 [b-design.md](../b-design.md) §B03（三级：固定句柄 + 读后复验 / 受控快照 / 显式失败）；计划 [b03-plan.md](b03-plan.md)；允许集 F4 `reader.py` + F2 `resolver.py` + F10（**仅新增**测试）。
> 本步交付的是 **S-10 推迟的"字节级硬门"**：B02 让**首选副本**按目录声明被服务、且消费者拿到的是**路径**；B03 让"取字节"这个动作本身只可能返回**已验证的字节**。

## 1. 交付物

| 交付 | 位置 | 内容 |
|---|---|---|
| 产品代码（改动） | `company-wiki/src/company_wiki/source_catalog/resolver.py` | 新增 `read_verified_bytes(...)` + `ByteReadResult` + `_read_verified_bytes` + `_inside_configured_roots`（**未改** `reader.py`，理由见 §5） |
| 验收用例（新增，F10） | `company-wiki/tests/contract/test_r4b03_stable_bytes.py` | 13 用例（+1 host skip），见 §3 |
| 计划 | [b03-plan.md](b03-plan.md) | 规则 R1–R6 与用例清单（实施与计划一致，偏差见 §5） |

## 2. 规则实现（逐条对应计划 §2）

| # | 规则 | 实现点 | 失败结果 |
|---|---|---|---|
| R1 | 云占位（召回属性）**拒读**，不触发水合 | `_read_verified_bytes` 的 `_needs_hydration(before)` 分支 | `unavailable` / `placeholder_not_hydrated` |
| R2 | **对"实际返回的字节"复算摘要**并与请求版本 `content_sha256` 比较（首选副本一视同仁） | 读入缓冲的同时 `digest.update(chunk)`，成功路径返回的正是该缓冲 | `unavailable` / `content_sha256_mismatch`（附短摘要） |
| R3 | 中断 / 类型不符 / 读中变化 ⇒ 显式失败；**读后**再 `stat` 比对 `size` 与 `mtime_ns` | `read_failed` / `not_regular_file` / `changed_during_read` 分支 | 同左 |
| R4 | 超上限（含**读取中增长**）⇒ 失败，**绝不**返回部分字节 | `_CANDIDATE_BYTES_CAP` 前后两处检查 | `unavailable` / `exceeds_candidate_cap` |
| R5 | 返回证据：`bytes_source="handle"`、`verified_sha256`（= `content_sha256` 字段）、`byte_size`、`read_at`；**不新增 `SourceHandle` 字段** | `ByteReadResult` | — |
| R6 | 取消**粘性**：读取中途取消也绝不返回字节 | 循环内 `budget.cancelled` 检查 | `unavailable` / `cancelled` |
| 附加 | **越界 locator（含 symlink 逃逸）零读**：按 realpath 比对配置 roots | `_inside_configured_roots`，在**读之前** | `not_found` / **`artifact_path_outside_allowed_root`**（见 §7 的词表说明） |

**错误值口径**：全部落在 `operation-contract.md` §2.4 的**五值**内（`not_found` / `not_indexed` / `unavailable` / `blocked` / `ambiguous`），**未新增状态**；预算与取消按合同要求作为**独立事实**（`reason`/字段），不是状态。

## 3. 验收结果（命令 → 实测）

复跑命令：

```
python -m pytest tests/contract/test_r4b03_stable_bytes.py -q
   -> 13 passed, 1 skipped
python -m pytest tests/contract/test_r4b03_stable_bytes.py \
    tests/contract/test_r4b01_field_owner_alignment.py \
    tests/contract/test_r4b02_candidate_selection.py \
    tests/contract/test_r4b04_reference_stability.py \
    tests/contract/test_r4b05_metadata_provenance.py \
    tests/contract/test_fc1204_complexity_ratchet.py -q
   -> 68 passed, 1 skipped
python -m ruff check src tests/unit tests/contract scripts
   -> All checks passed!
```

| 用例 | 覆盖 |
|---|---|
| `..._serves_verified_bytes_with_evidence` | 正例：字节、摘要、`bytes_source`、`read_at` 齐全 |
| `..._same_size_content_change_is_refused` | **S-10 的口子**：同长不同内容 ⇒ 拒绝（`content_sha256_mismatch`），`data is None` |
| `..._catalog_claim_does_not_override_the_bytes` | 目录仍服务该句柄，但**取字节**被拒（钉住"硬门在读路径"这一裁定） |
| `..._truncated_file_is_refused` | 截断 ⇒ 拒绝，不返回短字节 |
| `..._placeholder_is_refused_without_hydrating` | R1：拒读（合成属性） |
| `..._locator_outside_the_roots_is_not_found` | 越界 locator ⇒ `not_found`（字节正确也拒） |
| `..._missing_file_is_unavailable_not_a_crash` | 缺文件 ⇒ `read_failed` |
| `..._directory_in_place_of_the_file_is_refused` | 非普通文件 ⇒ `not_regular_file` |
| `..._size_ceiling_refuses_instead_of_serving_a_partial_buffer` | R4 |
| `..._cancelled_read_is_never_answered` | R6 |
| `..._budget_exhaustion_is_a_reason_not_a_sixth_status` | 预算 ⇒ `unavailable` + `budget_exceeded`（状态在五值内） |
| `..._every_refusal_stays_inside_the_contract_error_values` | 汇总：任何失败都不得越出五值、不得带字节或 `bytes_source` |
| `..._change_during_read_is_refused` | R3：读中变化（用包装句柄在同一次 `read()` 后改写文件） |
| `..._symlink_escape_is_refused_where_symlinks_exist` | 越界 symlink（**本机 skip**，见 §5） |

## 4. 与 S-10 的关系（本步闭合了它的一半）

S-10 的裁定原文："B02 段 3 的 hash 相等实现为**优先 + 逐候选诊断**，**字节硬门归 B03 读路径**"。本步即该硬门：
- **只经过本入口取字节**的调用方，不可能拿到与请求版本不符的字节；
- **仍自己 `open(handle.canonical_path)` 的调用方**不受本步保护——把消费者接到本入口是 **B07 的版本化读取合同**的交付（已在 docstring 与本节写明，不夸大）。

## 5. 边界与"没做"的事（如实登记）

1. **`reader.py`（F4）未改**：计划的 §6 已记录理由——该文件的职责是**目录**的只读底座（`mode=ro` / `query_only`），而字节级判定与 `_sha256_of_file`/`_verify_candidate`/`_needs_hydration`/预算同处 F2；拆开会产生跨文件私有依赖。计划允许"必要时落 F4"，本步判定为不需要。
2. **设计第 2 级（受控快照）无对象可读**：全库检索 `snapshot` 的命中都是 runtime policy / quality / 页级 / focus_cleanup 的 **DB 行**快照，**不存在"源字节的受控快照"**。设计原文是"读取**既有**受控快照"，而"新建快照"被明令禁止（写入路径 + 空间，需另批）。→ 该级**未实现**，`bytes_source="snapshot"` 保留为**不可达**取值；句柄不可固定时走 R3/R4 的**显式失败**，不静默降级。
3. **ACL 拒绝未单独合成**：本机（Windows）未构造 ACL 拒绝夹具；该情形与 `read_failed` 同一分支（`OSError`），**不声称已单独验证**。
4. **云占位为合成属性**：R1 用合成 `st_file_attributes` 触发（真实召回型占位需 G8 隔离副本/B08），**不声称真实云行为已验证**。
5. **symlink 用例在本机 skip**：宿主不支持创建 symlink（阶段 A 已登记同类限制）；用例写成"能建 symlink 才算"，在支持的环境会真实执行。
6. **不改 payload**：未新增 `SourceHandle` 字段、未改响应形状；`B-payload-hash` 仍**不可执行**（包内无冻结基线）。

## 6. 与复审流程的关系

- 本步的独立复审（`B.VR` b03）**尚未进行**；按 §11 每步一次，下一次复审将覆盖 B03（并抽样 B01 的处置）。
- **本轮的实施方式**：为了不与正在跑的 `B.VR`（B01）复审争用同一棵树，B03 先在 `0e28d99` 的**独立 worktree**（`%TEMP%\cw-b03-wt`）里实现并验证，复审结束后再以补丁形式落到主检出（`5ab0779`），落盘后**重新跑过** ruff + 棘轮 + 邻域用例。
- **教训（与 F-B01-8 同一条）**：worktree 隔离的是**代码**，不是**机器资源**——复审测量期间并行跑全量套件会给复审者制造假失败。后续步骤改为：复审先跑、实现等待。

## 7. CI 首次失败与更正（`5ab0779` → 本次更正；见 [findings.md](../findings.md) **F-B01-9**）

第一次推送后 CI **三份 Python 全红**（失败步骤 = `Contract tests`），三个原因**都是本步的**：

1. **reason 词表门**（`test_fc1301_reason_taxonomy.py`）：该门只扫描 `reason="x"` 关键字写法，我的 `not_found` 分支正好用了这种写法 ⇒ 必须已在 `observability.REASONS` 里。新增码要改 `observability.py` 并顶 `REASON_TAXONOMY_VERSION`，**两者都在 B 的允许集之外**。→ 改用**已注册**且语义相同的 `artifact_path_outside_allowed_root`（"path outside allowed roots"），并在代码里写明理由。**顺带登记的缺口**：解析器其余 reason 都是元组位置写法，词表门**看不见**（B02 的 `not_readable`/`hydration_required` 等同样未注册）→ 独立工作包（扩大扫描覆盖面 + 补齐注册），不夹在本步做。
2. **symlink 用例**：本机 skip，**Linux 上真跑** ⇒ 而 Linux 的**扫描层**不收录越界 symlink，没有候选，我的前置断言（必须服务一个句柄）**假设错了层**。→ 改为断言**性质**："越界字节永不交出"——扫描层拒收 **或** 读层拒读都算通过，只有交出字节算失败。
3. **（跨步影响）** B01 处置里我曾把 consumer hash 冻进仓库测试——**CI 证明那是错的**（该 payload 内嵌绝对 `path_ref`，hash 与机器相关：本机 `c773099b…` / CI Linux `ca3b7f5d…`）。该冻结已撤，改为只断言可移植部分。

**流程结论（已写入 findings）**：本地 `pre_push_gate` **不等于** CI（它不跑全量契约套件）⇒ 涉及新 reason 码、跨机器常量、平台相关行为的改动，推送前**必须本地跑 `pytest tests/contract`**。
