# RF 周跑的 FF 公开接口交接范围

当前状态 BLOCKED。RF 周跑需要 FF 已发布、可回查的同义验收结果。近一次本机记录 `20261122T083603Z` 为 not-ok。现有 RF 调度器启动 FF 仓内的 pytest，并设置真实下载开关和宿主 profile。Windows 查询 `revenue_weekly_t3` 返回“拒绝访问”，暂缺实际注册动作证据。此轮只核对已发布接口和保留的收据。

接口盘点基于 FF `711db1c1bd2d1eda56c6de8edbcc692f86ad4680` 和 RF `7409098d11da74761d8b0dec8df41f641a0c90be`。FF 的 [ff-job/1 协议](https://github.com/zhengcb81/filing-fetch/blob/711db1c1bd2d1eda56c6de8edbcc692f86ad4680/docs/ff-job-protocol.md) 与 [四项现行用例](https://github.com/zhengcb81/filing-fetch/blob/711db1c1bd2d1eda56c6de8edbcc692f86ad4680/tests/test_e2e_download.py) 提供对照。FF owner 复核公开接口盘点。

| 现有覆盖 | 已有公开接口能证明的部分 | 留在所属模块的证明 |
| --- | --- | --- |
| A 股年报、港股年报、美股年报，各一次从空隔离库实际采集 | 每个市场可用 `filing.acquire` 提交确期期次、`fetch_if_missing`、字节、时间和费用上限。公开 JobView 给出结果、download 计数、SourceRef 和费用状态 | FF 证明实际使用正确生产 provider 且此次确实下载一次。CWP 证明原件哈希、发布口径、来源和入库状态与原操作一致。原测试也核对临时根、工件边车和暂存清理 |
| 三家各自重用 | 独立 `reuse_only` 作业读取同一 SourceRef，应有零下载。该作业有独立的稳定键，原下载作业自己的幂等回放继续指向第一次结果 | 首次和重用的 owner 原件身份不变，原文件未被覆盖，没有新增下载记录，测试临时根完整清理 |
| 有意损坏已有原件 | 可归档原作业失败状态、下载数和费用状态。公开作业没有创建或破坏合成原件的操作 | FF/CWP 在 owner 隔离夹具中先判坏件不可复用，再对有明确上限的下载请求证明 provider 未启动、下载数零、原件没有被覆盖、无暂存残留 |
| 强停后的恢复 | 使用原 owner job ID 查状态。失联保留 unknown；按同一尝试只读 reconcile；仅在 FF 明确证明此前未启动和零下载时才有原生安全重试 | 测试运行自身需要一个持久引用，把四项验证和原作业绑定在一起。恢复态及费用不明需如实进入周跑结果 |

原 T3 用例使用每个采集请求 50 MiB、180 秒、provider 费用上限 0 美元的旧隔离配置。后续沿 owner 明确的实跑预算和现有计费回告执行。仅有预算上限不能推断真实费用。

`ff-job/1` 提供单作业真实结果，scheduled-refresh 收据证明调度结果，F4 收据可查原 action 和 attempt。它们都没有当前四项组合的同义公开验收。FF 已有离线矩阵可以回归下游合同，但其收据不能证明实跑了三个生产 provider。RF 在当前节点只记录缺口，保留既有周跑行为和旧收据读取。

## 最小公开收据

提案为 FF 在自己的公开入口按已存在的 `run_id` 返回一个 JSON 对象。命令形式可为 `python scripts/ff_t3_receipt.py get --run-id ID`，最终名称由 FF owner 绑定到原有收据发布机制。读取只查原运行，不提交采集。下面是一个运行完成的字段示例。

```json
{
  "schema_version": "ff-t3-assurance/1",
  "run_id": "t3-owner-run",
  "owner_revision": "git-commit-sha",
  "mode": "live",
  "state": "completed",
  "completed_at": "2026-11-25T09:00:00Z",
  "cases": {
    "cn_annual": {"outcome": "passed", "evidence_ref": "ff-t3/t3-owner-run/cn", "reason": null},
    "hk_annual": {"outcome": "passed", "evidence_ref": "ff-t3/t3-owner-run/hk", "reason": null},
    "us_annual": {"outcome": "passed", "evidence_ref": "ff-t3/t3-owner-run/us", "reason": null},
    "corrupt_original": {"outcome": "passed", "evidence_ref": "ff-t3/t3-owner-run/corrupt", "reason": null}
  }
}
```

- `mode` 为 `live` 或 `offline`。坏件反例继续使用 owner 合成夹具。组合为 `live` 时，三市场都要有实际生产 provider 证据。
- `state` 为 `running`、`completed`、`blocked` 或 `unknown`。未完成时 `completed_at` 可空，`cases` 可能部分可用。不存在的已请求收据返回明确 `missing` 状态。环境不可执行返回 `blocked`，实际失败写该项 `failed`。已开始但失联保持 `unknown` 并关联原 ID。
- 每项 `outcome` 为 `passed`、`failed` 或 `blocked`。已证明结果携带可回查 `evidence_ref`，没有实际证据时可空。失败或尚不可执行用安全 `reason` 说明。该引用在所属模块绑定原下载和重用、坏件和清理证明、原账本与费用；RF 不再读取内部夹具或物理路径。顺序无关，有效四项必须对应四个稳定用例键。
- RF 读到 `live`、`completed` 以及四项都通过时才回报本次实跑通过。离线结果、缺项、失联、未生成或执行失败在 RF 原台账展示原状态。额外诊断字段可随 owner 扩展，RF 只校验业务上实际消费的字段。原历史 RF 收据保持可读。

## 迁移时的交接和测试

1. 由 FF owner 在现有测试执行内发布一次小型持久收据，复用原始用例与原生保存的证据。至少给出稳定运行 ID、实际运行版本、实跑或离线标记、三市场采集和重用、坏件拒绝四项的状态及可追溯 owner 证据。已付和不明费用继续沿原作业记录。实际任务有四项结果时才能回告四项的通过情况。
2. 发布单个只读或原动作查回入口。RF 只消费该 owner 结果和失败码，不接触外部 pytest、物理目录、账本、假原件或 provider 配置。经原任务 ID 查回先于任何新运行。拒绝、失败或部分结果按既有周跑台账保留。预期是收据和状态“扁平透明”，不新增发布许可。
3. 先做 RF 侧无网络合同测试。覆盖已发布四项全部通过、遗漏一项、离线误标实跑、一个真实失败、重启查原作业、费用不明。一并验证已有 RF 周跑历史 ledgers 读取。
4. 按 FF owner 隔离配置各自做真实验收。全程读取实际四项 FF owner 证明，核对新旧周跑用途和日志差异，完成后清理测试资料。此时再核对 Windows 实际注册命令及服务部署版本。测试条件或系统访问缺失应明示。
