# B02 的 CI 记录（独立于本机的第三方验证）

> 本机（Windows）的测量已写在 [b02-implementation.md](b02-implementation.md) §7；本页只登记 **GitHub Actions** 的结果，因为 CI 在 Linux 上**重新测量**覆盖率与复杂度棘轮，是本步最强的独立验证。
> 采集方式（只读 API）：`GET /repos/{owner}/{repo}/actions/runs`；下表时间与 id 为实测。

| 仓库 | 提交 | 内容 | 工作流 | 状态 | run id |
|---|---|---|---|---|---|
| company-wiki | `cab1fd6` | B02 rev1（资格先于排序 + 逐份尝试 + 预算/取消） | CI | **success** | 34691241045 |
| company-wiki | `350b67a` | B02 rev2（`B.VR` rev1 的 7 条处置） | CI | **success** | 34693496346 |
| company-wiki | `182846b` | B02 rev3（`B.VR` rev2 的 5 条处置） | CI | **success** | 34697070398 |
| revenue-forecast | `2ced153` | B 运行目录：B02 实施记录（rev1） | quality | **success** | 34691409601 |
| revenue-forecast | `7b34c12` | B 运行目录：`B.VR` rev1 记录 + rev2 证据 | quality | **success** | 34693783149 |
| revenue-forecast | `63422f1` | B 运行目录：`B.VR` rev2 记录 + rev3 证据 | quality | **success** | 34697489835 |
| revenue-forecast | `aeb55e3` | checkpoint 锚定（28 文件，`all_match=True`） | quality | **success** | 34697634266 |

**CI 覆盖到的与本步直接相关的门**（`company-wiki/.github/workflows/ci.yml`，三个 Python 版本 3.11/3.12/3.13 全部 success）：

1. `Ruff lint`（`src tests/unit tests/contract scripts`）；
2. `Contract tests`（含 8 个 `--ignore` 之外的**全部**契约测试）；
3. **`Branch coverage ratchet (FC-1204-a, fresh measurement)`** —— CI 自己跑 `pytest tests/ --cov … --cov-report=json` 再跑 `FC1204_COVERAGE_GATE=1`：**说明本步改动在 Linux 的全新测量下也过 TIER1 `service.py`=95 / TIER2 `resolver.py`=86 两档**（本机数字见 §7，两处独立测量互证）；
4. `Unique test symbols gate`（新增 27 个用例的函数名与全库不冲突）；
5. `Plan claim verifier`、`Mutation canaries`。

> 注：本页**不**声称 `B-payload-hash` 已执行（包内无冻结基线，见 [test-acceptance-map.md](../test-acceptance-map.md) §1c），也**不**声称在生产 catalog 上做过验证。
