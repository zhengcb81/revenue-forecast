# B02 / B04 的 CI 记录（独立于本机的第三方验证）

> 本机（Windows）的测量已写在 [b02-implementation.md](b02-implementation.md) §7 与 [b04-implementation.md](b04-implementation.md)；本页只登记 **GitHub Actions** 的结果，因为 CI 在 Linux 上**重新测量**覆盖率与复杂度棘轮，是这两步最强的独立验证。
> 采集方式（只读 API）：`GET /repos/{owner}/{repo}/actions/runs`；下表时间与 id 为实测。

| 仓库 | 提交 | 内容 | 工作流 | 状态 | run id |
|---|---|---|---|---|---|
| company-wiki | `cab1fd6` | B02 rev1（资格先于排序 + 逐份尝试 + 预算/取消） | CI | **success** | 34691241045 |
| company-wiki | `350b67a` | B02 rev2（`B.VR` rev1 的 7 条处置） | CI | **success** | 34693496346 |
| company-wiki | `182846b` | B02 rev3（`B.VR` rev2 的 5 条处置） | CI | **success** | 34697070398 |
| company-wiki | `da5e0f5` | B02 rev4（`B.VR` rev3 的 7 条处置：可证伪表述 + 谓词/理由 + 3 个回归） | CI | **success** | 34700254033 |
| company-wiki | `1d8b1f7` | B02 rev5（文字收口：差异清单单点维护 + 审计检索产品文件；**仅注释/docstring**） | CI | **success** | 34701684837 |
| company-wiki | `bc3590f` | **B04**（新验收文件 `test_r4b04_reference_stability.py`，4 用例；**产品代码零改动**） | CI | **success** | 34702604627 |
| company-wiki | `6909e78` | **B05 子步 1**（抽取 `_merge_document_row`；与下一行同一次推送，CI 只跑 tip） | CI | **未单独触发** | — |
| company-wiki | `bdd99dc` | **B05 子步 2**（保留键 `r4_provenance` + 读-改-写；3 用例） | CI | **success** | 34707677701 |
| company-wiki | `9db3394` | **B05 子步 3**（逐列规则 + 读侧 `blocked`；6 用例） | CI | **success** | 34709578267 |
| revenue-forecast | `2ced153` | B 运行目录：B02 实施记录（rev1） | quality | **success** | 34691409601 |
| revenue-forecast | `7b34c12` | B 运行目录：`B.VR` rev1 记录 + rev2 证据 | quality | **success** | 34693783149 |
| revenue-forecast | `63422f1` | B 运行目录：`B.VR` rev2 记录 + rev3 证据 | quality | **success** | 34697489835 |
| revenue-forecast | `aeb55e3` | checkpoint 锚定（28 文件，`all_match=True`） | quality | **success** | 34697634266 |
| revenue-forecast | `01f6059` | B 运行目录：`B.VR` rev3 记录 + rev4 证据（含变异 harness） | quality | **success** | 34700568220 |
| revenue-forecast | `5cca0b4` | checkpoint 锚定（31 文件，`all_match=True`） | quality | **success** | 34700707748 |
| revenue-forecast | `c2d6555` | B 运行目录：`B.VR` rev4 记录 + rev5 单点化（含 `b02_anchors.py`） | quality | **未单独触发**（与下一行同一次推送，CI 只跑推送 tip） | — |
| revenue-forecast | `38abbdd` | checkpoint 锚定（33 文件，`all_match=True`） | quality | **success** | 34701950839 |
| revenue-forecast | `90fbb9e` | CI 记录补 rev5 两行 | quality | **success** | 34702387242 |
| revenue-forecast | `2b480cb` | B04 验收记录 + F-B04-1 + 台账回填 | quality | **success**（与下一行同一推送） | 34702769951 |
| revenue-forecast | `3078a34` | checkpoint 锚定（35 文件，`all_match=True`） | quality | **success** | 34702769951 |
| revenue-forecast | `d15f04e` | B04 复审更正（F-B04-1 改写 / F-B04-2 / 变异 harness） | quality | **success** | 34704727273 |
| revenue-forecast | `d63fc21` | checkpoint 锚定（38 文件，`all_match=True`） | quality | **success** | 34704899066 |
| revenue-forecast | `41d06de` | B05 三子步记录 + F-B05-1/F-B05-2 | quality | **success** | 34709826139 |
| revenue-forecast | `cab7b74` | checkpoint 锚定（39 文件，`all_match=True`） | quality | **success** | 34710000495 |

**CI 覆盖到的与本步直接相关的门**（`company-wiki/.github/workflows/ci.yml`，三个 Python 版本 3.11/3.12/3.13 全部 success）：

1. `Ruff lint`（`src tests/unit tests/contract scripts`）；
2. `Contract tests`（含 8 个 `--ignore` 之外的**全部**契约测试）；
3. **`Branch coverage ratchet (FC-1204-a, fresh measurement)`** —— CI 自己跑 `pytest tests/ --cov … --cov-report=json` 再跑 `FC1204_COVERAGE_GATE=1`：**说明本步改动在 Linux 的全新测量下也过 TIER1 `service.py`=95 / TIER2 `resolver.py`=86 两档**（本机数字见 §7，两处独立测量互证）；
4. `Unique test symbols gate`（新增用例的函数名与全库不冲突）；
5. `Plan claim verifier`、`Mutation canaries`。

> 取数纪律：表中的 run id 与状态**逐条取自只读 API 响应**（`GET /repos/{owner}/{repo}/actions/runs?per_page=N`，按 `head_sha` 对齐），不是凭记忆填写——本页早先一版曾把两个 run id 写错（凭印象转录），已按 API 实际值更正；采集不到的行标注"登记时的状态"，不猜。
> 注：本页**不**声称 `B-payload-hash` 已执行（包内无冻结基线，见 [test-acceptance-map.md](../test-acceptance-map.md) §1c），也**不**声称在生产 catalog 上做过验证。
