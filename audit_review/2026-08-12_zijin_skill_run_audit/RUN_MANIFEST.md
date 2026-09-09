# 紫金矿业 revenue-forecast 封存运行清单

## 封存边界

- 最终 draft 运行完成：`2026-08-13T00:19:14+01:00`。
- 运行命令：`python -B audit_review/2026-08-12_zijin_skill_run_audit/build_zijin_draft.py`。
- 模式：`draft`；未调用 CLI `--validate-only`；未尝试 formal publication。
- 运行先后执行纯 `validate_document`、两次 `run_forecast(..., mode='draft')`、native renderer 尝试和隔离摘要生成。
- 两次 draft 的 canonical 结果一致；紧邻调用的 publication registry before/after 完全相同。
- 本清单认证的是下列时刻的文件快照，不认证随后仍在发生的其他 agent 提交或工作树编辑。

## 仓库状态

| 仓库 | 调查开始时 HEAD | 封存后观测 HEAD | 说明 |
|---|---|---|---|
| revenue-forecast | `fb77fe1b982d378d7c7af2e98d79f842ee8be930` | `17e6354230442878d37a489b9258924e4bd45ce6` | 运行期内有其他 agent 提交；封存运行后的 `scripts/` Python 树与该时刻工作树 hash 见下文 |
| filing-fetch | `b7ef9cca0747b108184f00e3e519aeb046be9d2b` | `b7ef9cca0747b108184f00e3e519aeb046be9d2b` | HEAD 未变；CI/测试存在其他 agent 的未提交改动 |
| company-wiki | `460d2730719acb6e4fdf59886c568c847d10d028` | `22689703b5020f2f4937afc7e065362953201288` | 运行期内有其他 agent 提交；CI、依赖、coverage/test 等仍有环境侧改动 |

封存运行完成后于 `2026-08-13T00:20:04+01:00` 计算的 `scripts/**/*.py` 聚合 SHA-256 为：

`9ed9af9b9cb63d9cfc1e9cbea085dad1207afccb028ecc4c8018951b6350fa1e`

聚合算法：按相对路径排序，将每项写成 `relative/path|file_sha256`，以 LF 连接后再做 SHA-256；共 31 个 Python 文件。

## 运行时关键实现文件

| 文件 | SHA-256 |
|---|---|
| `scripts/contracts/constants.py` | `961ede5bcb3778e01041c090a0a1067aa141b9590cff0082148f3b4db8b7bf89` |
| `scripts/contracts/document.py` | `3f32887d64b35e376be34210a8c1192c786a9306fdd64796ebdf80d1c0f3e4d3` |
| `scripts/contracts/evidence.py` | `bc5e4c5305fad22f9c028fd989536d6529ef868698fb0adfcd9363b3e096208e` |
| `scripts/revenue_core.py` | `b17d03bf2e8f3d2e14eb34722dd8fef50bc0a3a47292d89fa99efcaabfcf1f2e` |
| `scripts/revenue_report.py` | `17ba5a36b7720b98643f3bd60325b6912c1988f0f34ade8dd44321b477b65e84` |
| `scripts/forecast/segments.py` | `eac8371ba986327c4203dbecd3f6c186a73a6680f9f12fe356395901af5dce9f` |
| `scripts/model_registry.py` | `1f2639e1d44df6794a1478e7c3ed3400b5cf9d70cc994d3804e933bd6b020a86` |
| `scripts/forecast/calc.py` | `d503cdad69bad4461ea51eb9c5713a313183a9ad9f9b1bf9e41a9c13e559408e` |
| `scripts/analysis/confidence.py` | `16a00a3ef598bc616d5d92c29500f0f08cbb8413d530cbba58f6a3ab513febb5` |
| `scripts/research/coverage.py` | `ae6519cc18fea823dcc9d5e47956a2aea6da3270f1041b28d7bf1b783cd4b470` |
| `scripts/research/drivers.py` | `45e3d58853c6757a0a49701d495ffb9e3e9cb0dafc2e819432cdd28af6e90e18` |
| `scripts/research/targets.py` | `28c6d0fa9cf6d5f18e33b89e75abe6c1358c22e57785995e5c7f10420953a7cc` |

## 输入、结果与验证产物

| 产物 | 文件 SHA-256 | 说明 |
|---|---|---|
| `outputs/input_v1.json` | `409949d1a62666db49b46cb65b44bf8482839f831b88bab0c93716bb8ff0cae4` | 漂亮打印后的完整输入文件 |
| `outputs/draft_result.json` | `36dea23832d01896318da4605037db3e835b849d1d6bfb7b99587cd19285c014` | 漂亮打印后的完整 draft 结果 |
| `outputs/draft_report.md` | `cd7798b1be1de02b171e14e6bdcae929b5f85aca5c4a70a637be24382660ee81` | 从强校验结果派生的隔离摘要 |
| `outputs/validation_receipt.json` | `cf098df8dabb3fcfb4d0321db93e836b4e000053e07561f6007271e96fca4822` | draft、确定性与 registry 回执 |
| `outputs/post_run_checks.json` | `25653ed9f8fa9c6ebb34642c9d5130d5dde4dff3ccaaeb23ba9fa3c35a337732` | 独立反算；绑定相同 canonical/file hash 的最终重跑 |
| `build_zijin_draft.py` | `567d7a8254e77b0438bf6c5d18ec771ba8a7e6b9e1c4ae999d2b0fdf1eddca3b` | 本审计隔离构造/验证器，不是产品实现修改 |

回执中的 canonical JSON 哈希与漂亮打印文件哈希不同是预期行为：

- input canonical SHA-256：`5a6a8b3a3ee3172dd6af027c78b65f85601c56f46eb29d9d9e1ab3c9051c1067`
- result canonical SHA-256：`a8e64f78a174a36f21f1becdee3ba3b51005e02e064bd02a2e1949433ca3f8ca`
- 两次 draft 的引擎 canonical SHA-256：`28d04fda8663a9e5d3af3f3b479b5346814552bff2e6c2902c188cb89c178437`

最终紧邻运行的 publication registry：

- before：1,423,114 bytes；`5b3c73067cb49ac7ab2f64cd860acb1fec7af53e024d9ad22ad897bbf8c0be4e`
- after：1,423,114 bytes；`5b3c73067cb49ac7ab2f64cd860acb1fec7af53e024d9ad22ad897bbf8c0be4e`

## 来源快照

| 来源 | SHA-256 | 状态 |
|---|---|---|
| FY2025 canonical annual-report PDF | `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d` | 物理文件与 catalog/source sidecar 一致；本轮复用、零下载 |
| FY2024 canonical annual-report PDF | `004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89` | 物理文件与 catalog/source sidecar 一致；本轮复用、零下载 |
| `sources/2025_results.html` | `08bbc18f4dcb2bce1cd0af21075ae10155fe69beeb178e73768a3fa410d648fe` | isolated capture；未入共享 catalog |
| `sources/2026_norton_commissioning.html` | `a9662471d15bf8ac287c179d3ae67cf3e35465b39425637119f25e1152f00b12` | isolated capture；未入共享 catalog |
| `sources/2026_strategy.html` | `b2d215df1c6f2049a6d07c4cfe340b7a247efcaa94ba916695fc10173a25b420` | 实际为无关学校工程页面；保留作 source-identity 负例，明确未进入模型 |

## 封存后的环境漂移

在封存运行结束后，其他 agent 于 `2026-08-13T00:23:10+01:00` 又开始编辑 `scripts/revenue_report.py`：其工作树 SHA-256 变为 `a34cbd35d30937e2118f26cd03b17f1b726f654b46ba87e66ff00505954b990c`，整个 Python 树聚合 hash 于 `00:24:09+01:00` 变为 `dd1695add80b7507bf7500049a283c5ccf52d4d253192abd3d9242b569fd42fd`。这项后续修改不属于封存运行，也没有被本审计评价或覆盖。

因此，报告中“native renderer 对合法 draft 报 `publication_receipt gate_ids mismatch`”是对运行时 `revenue_report.py` 哈希 `17ba...65e84` 的真实行为记录；不能自动外推到该文件随后正在形成的版本。预测计算与强输出验证发生在 renderer 之前，仍由上面的 input/result/engine 哈希独立封存。

## 写入与归因限制

- 本审计创作的持久文件均在 `audit_review/2026-08-12_zijin_skill_run_audit/`。
- 本审计未创作产品代码/配置改动，未调用显式 ingest/index/metadata/worker-priority 写接口。
- reuse-only 路径会经过具有隐含写能力的 catalog 初始化；后台 worker 同时写 catalog。只能用目标级 journal/文件/artifact 证明零下载、零新 artifact，不能声明整个 catalog byte-for-byte 未变化。
- 工作树中的其他产品改动均视为环境侧/其他 agent 所有；本审计未清理、提交、回滚或据为己有。
