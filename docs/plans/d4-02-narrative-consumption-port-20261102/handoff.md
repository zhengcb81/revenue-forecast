# D4-02 — RF 摘要实际采用端点：交接

状态：**已实现、已独审通过、待 ROOT 组合验收。** 所有写入只在 revenue-forecast。

## 基线与交付

| 项 | 值 |
|---|---|
| 基线 HEAD | `4a56e920`（`docs: reopen decoupling gaps after full entrypoint review`） |
| 交付 commit | `7688226d`（8 files / +761 −23；本 handoff 在该提交内，随后仅追加本行记录） |
| 工作树 | 只含本卡路径 + 既有定时产物（`assurance/runs/*`）与既有未跟踪目录（`.planning/`、`delivery/`、`output/`），未触碰 |
| 跨仓改动 | 0（CWP/FF/StockWiki/ET/AUDIT 未改；CWP `integration/`、ROOT runner 未改） |

修改路径：

- `scripts/source_narrative_context.py` — 采用入口接收可替换 reader 连接；拆出纯绑定；交接已验证 context
- `scripts/company_wiki_narrative_reader.py` — 连接适配：字符串型 reader command 明确拒绝（`blocked/invalid_reader_command`），不再按字符拆开
- `tools/build_auditable_case.py` — 新增 `--narrative-reader-command-json` 并透传
- `tools/run_narrative_consumption_e2e.py` — 新增 `--narrative-reader-command-json` 并透传
- `references/source_ports.md`、`references/evidence-role-calibration.md` — 端口与配方文档
- `tests/test_d4_narrative_consumption_port.py` — 新增 15 例行为测试

未改：`scripts/source_preparation.py`、`scripts/company_wiki_narrative_contracts.py`、任何历史 `assurance/runs`、RF/AUDIT 业务 PWF 状态。

## 逐项闭合

1. **同一可替换连接，从读到采用**：`consume_narrative_input` 新增 `reader_command`，原样转交公开 reader（`_command` 的 argv 契约、stdout/stderr/退出码/回执预算全部沿用）。此前 `scripts/source_narrative_context.py:171` 固定走 `python -m company_wiki.source_catalog.narrative_transport_cli`，现在只有省略连接时才走该默认。
2. **两个公开工具同步**：`build_auditable_case`、`run_narrative_consumption_e2e` 都新增 `--narrative-reader-command-json`（与 prepare 的同名参数同形），测试用真实子进程调用两个 CLI 并核对生产者调用次数，不是只测 helper。
3. **一次采用只读一次**：读与绑定在同一调用内完成，`bindings` 多选仍只读一次；测试断言生产者调用计数为 1。
4. **同一已验证 context 不再重复读取**：`consume_narrative_input(..., context=)` 直接绑定进程内已由公开 reader 验证的 context，绑定结果与「读后绑定」逐字段相等且调用计数不变。该交接面与 reader 连接互斥，并复核请求的 `narrative_ref`/`as_of_date`/`expected_source`（v1）/`expected_issuer`（v3）与 `read_receipt.status/replay_status`。
5. **source binding 未放松**：父来源仍按实收 SHA 绑定（`_captured_parent`），`company_wiki_trace.source_ref` 一致性、span 所属来源、信息日期、used parameter 与真实 segment 公式依赖全部保留；失败路径不改输入（`deepcopy` 断言）。

## 公开合同与兼容性

- `consume_narrative_input(data, *, request, bindings, source_id, catalog_config=None, timeout_seconds=30, verified_by=..., reader_command=None, context=None)`。`catalog_config` 由必填改为「读取时必填」；现有调用方全部传该参数，行为不变。
- 省略 `reader_command` 时仍是既有本地 CWP CLI 部署（默认 argv 断言在测试中固定）。
- 拒绝语义：交接面拒绝为 `ValueError`；读取失败仍为有界 `NarrativeTransportError`（status/reason 不变），未新增吞错或异步化。
- 两个工具的端口参数名与错误信息一致；两者都把 `--catalog-config` 归一化为绝对路径（相对路径此前在 `_command` 处报 `invalid_catalog_configuration`）。
- wire/契约未改：NarrativeContext v1/v3、请求/回执字段、CWP producer 均未动。

## 实际测试

运行解释器：`C:/Miniconda/python.exe`（PATH 上的默认 python 无 pytest）。

| 命令 | 结果 |
|---|---|
| `pytest tests/test_d4_narrative_consumption_port.py -q` | 15 passed |
| `pytest tests/test_decoupled_source_port.py tests/test_w04_public_consumer.py tests/test_du11_narrative_citation_consumption.py tests/test_du11_narrative_citation_projection.py tests/test_narrative_summary_usage.py tests/test_source_preparation_complete_result.py tests/test_architecture_dependency_uses.py tests/test_source_clock.py tests/test_du11_narrative_citation_e2e.py tests/test_company_wiki_narrative_reader.py tests/test_narrative_source_preparation_transport.py tests/test_w20_narrative_adoption_audit.py -q` | 271 passed, 1 skipped |
| `pytest tests/test_narrative_source_preparation_e2e.py -q` | 13 passed, 2 skipped |
| `pytest tests/test_research_evidence_roles.py -q` | 10 passed, 1 failed（**基线既有**，见下） |
| `ruff check`（本卡 5 个 py 文件） | All checks passed |
| `python tools/check_unique_test_symbols.py` | OK: 199 test file(s), no duplicate |

**基线既有失败（非本卡引入）**：`tests/test_research_evidence_roles.py::test_optional_diagnostic_separates_documentary_presence_and_unknown_magnitude` 断言 `confidence.calculation_version == "stable-fsum/1"`，实际为 `source-evidence/2`。已用 `git stash`（仅暂存本卡 4 个受跟踪文件）复跑确认为基线；该断言属 confidence 计算域，不在本卡写域，未修。

## 测试设计要点

- 生产者是临时目录内**独立命名**的单文件脚本（`independent_summary_producer.py`），以 `-I -S -B` 启动：`-I` 忽略 `PYTHONPATH`/用户 site，`-S` 不加载 site-packages。测试在 `PYTHONPATH` 上放置一个 `__init__` 会抛异常的 `company_wiki` 桩，生产者显式 `import company_wiki` 后记录 `ModuleNotFoundError`，同时断言 `sys.modules` 无 `company_wiki*`、`sys.path` 无 site-packages/本仓路径 —— 该断言非重言。
- 生产者回放仓内冻结的公开 wire，但把父来源重定向到 RF 自己的合成来源 fixture（`tests/fixtures/cwp_source_ref_v2.json`），因此父来源绑定、span 身份、摘要引用、lineage 字节范围都是真实可验的；所有字节仍由未改动的 RF reader 校验，显式端口读出的 context 与 `validate_narrative_response` 直接验证结果逐字段相等。
- 端口失败模式用 5 个独立进程覆盖：`exit 2 + stdout 有体`、`exit 2 + 空 stdout + 拒绝回执`、`exit 2 + traceback`、`exit 0 + 字节不符`、`exit 0 + 空回执`，全部命名拒绝且不落证据。
- 全程无 API/网络/原件/付费模型：模块级 autouse 断 `socket.connect`/`create_connection`/`urlopen`；生产者只读本地 fixture。

## 独立审查

- 第 1 轮（未参与实现的独立审查 agent）：**CHANGES_REQUESTED**。
  - F1 major：`context=` 交接只比对引用与信息日期，请求里的 `expected_source`/`expected_issuer` 被静默忽略（同一请求走读取路径会被拒）。**已修**：交接面先 `validate_narrative_request`，再按 wire 语义逐项复核来源/发行方约束，并要求 `read_receipt` 为 verified。
  - F4 minor：文档把 e2e 工具参数名写成 `--reader-command-json`。**已修**（两个工具统一 `--narrative-reader-command-json`）。
  - F5/F6/F8/F9/F10 已修：浅拷贝断言、缺「另一来源」与交接面拒绝用例、隔离断言重言、字符串命令被拆成字符、`context` 与连接同传静默优先。
  - F7 已修：两工具端口参数解析与 config 归一化一致。
  - F3 部分处理：交接面是进程内组合边界而非凭证（契约模块 `_context_from_verified` 可构造 context），已在 docstring/文档写明信任边界，并加 verified 回执守卫。
- 第 2 轮（同一独立审查线复审）：**APPROVED**。逐项复验 F1 的六个 `expected_source` 字段、v3 六个 issuer 键与 issuer 子集、`as_of_date=None`、互斥规则、字符串命令、两工具 CLI 真实调用，确认无回归；确认写域合规。复审提的 N1（拒绝异常类型写进文档）、N4（装配配方补新 flag）、N5（端口文档拆行）已按建议落实。

## 未完成 / 外限（交 ROOT）

1. **ROOT 组合待办**：`prepare` → 真实 `consume` → RF 正式校验 → 参数/公式/报告，用独立端点、无 CWP checkout/PYTHONPATH，本卡未做（D4-06 归 ROOT）。组合时两处命令都用 `--narrative-reader-command-json`（或 prepare 的 `narrative_reader_command`）指向同一端点。
2. **F2（既有，写域外）**：`scripts/source_preparation.py:431` 的 `external` 只由 `source_reader_command` 判定。只把**摘要** reader 换成外部端点、原文 reader 仍走本地默认时，不透明 catalog 句柄会被当本地文件校验而在读取前失败（`resolve(strict=True)`）。绕行：同时传 `source_reader_command`。该文件属 D3 写域，本卡未改，建议 ROOT 或 D3 线收口。
3. **F11（设计外限）**：两个 CLI 各自只读一次；`prepare` 返回的是消费回执而非可重验的 context，没有便携 context 载体，因此 `prepare` 后再 `build` 会对同一 artifact 各读一次。已在 `references/source_ports.md` 与 docstring 写明；进程内编排可用 `context=` 免二次读取。
4. **全套件未跑**：按卡片只跑本卡新增与受影响 RF 快测。另注：当前 HEAD 上 `tests/test_ca204_monthly_generalization.py`、`test_ca305_six_problems.py`、`test_zr1008_new_chain_cutover.py` 引用已不存在的 `test_zr709_zijin_journey`，整仓收集会失败；与本卡无关，未处理。
5. 本卡不构成真实摘要/缓存/RF 研究采用的业务验收；隔离合成端点不能替代后续真实业务链。
