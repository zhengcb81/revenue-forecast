# 测试命令注册表实施计划

## 1. 为什么必须冻结命令

“跑过测试”如果没有固定命令、工作目录、环境和 collected 数量，就很容易被弱模型缩减成一个新单测。Phase 1 必须建立机器可读 command registry，后续 receipt 只能引用 command ID。

## 2. Registry 字段

```yaml
schema_version: "1.0"
commands:
  - id: wiki.unit.full
    owner_repo: company-wiki
    cwd_ref: repo_root
    argv: ["python", "-m", "pytest", "..."]
    environment_allowlist: []
    forbidden_environment: []
    timeout_seconds: 0
    tier: T0
    required_for: ["FC-..."]
    expected_min_collected: 0
    forbidden_markers: ["skip", "xfail"]
    writes: ["temp_only"]
    network: false
    output_schema: test-command-result-v1
```

实际值必须从三个稳定仓库的现有 CI、测试配置和脚本中只读盘点后填写；本计划不臆造尚未核实的命令或阈值。

## 3. Phase 1 冻结步骤

1. 分别枚举三仓 CI workflow、pyproject/pytest 配置、测试脚本和开发文档。
2. 对每条候选命令记录真实工作目录、Python 版本、依赖安装方式、marker、timeout、网络和写入行为。
3. 在稳定 base triplet 上运行一次，记录 collected/passed/skipped/duration 基线；失败命令不能被登记为“required green”，必须先形成现状 finding。
4. 合并重复命令，但保留 unit、contract、integration、acceptance、T1、T2、T3、mutation、coverage、lint、type、compile、architecture 的独立 ID。
5. 添加 collection guard：collected 数下降、mandatory ID 未收集、unexpected skip/xfail、进程数不足或 evidence file 缺失均失败。
6. 添加 workspace guard：命令前后检查 dirty files、root/catalog fingerprint 和未授权网络/写入。
7. 由三仓 owner 和独立 reviewer 审核后冻结 registry hash，写入 compatibility manifest。

## 4. 必需命令族

| 命令族 | Owner | 最低内容 | 适用门 |
|---|---|---|---|
| `wiki.*` | company-wiki | lint、compile、unit、contract、integration、acceptance、coverage、type、architecture、mutation | 所有修改 wiki 的 FC |
| `filing.*` | filing-fetch | lint、compile、完整 tests、isolated E2E、real-tool、real-download、coverage、type | 所有修改 filing 的 FC |
| `revenue.*` | revenue | lint、compile、tests、tools tests、engine/source preparation E2E、coverage、type、mutation | 所有修改 revenue 的 FC |
| `triplet.t1.*` | revenue | 真实三进程、95 场景 registry、side-effect journal | Phase 5–15 |
| `production.t2.*` | revenue | 真实 catalog/roots 只读、隔离 audit output、fingerprint | 经权限可运行的 FC/每日 gate |
| `provider.t3.*` | filing/revenue | CN/HK/US 临时 wiki、首次下载+二次零下载 | Phase 8/10/11/15 |
| `canary.t4.*` | release owner | 最小 cohort apply/rollback、同请求 before/after | Phase 2/5/14/15 |
| `closure.*` | revenue | receipt、freshness、triplet、scenario、policy、release ledger | 每 Phase/最终关闭 |

## 5. 命令选择规则

- Focused：该 FC 的所有新/受影响测试，允许 marker，但必须记录完整 node IDs。
- Repo：owner repo 的完整 required command 族，不允许 `-k` 缩减。
- Affected sibling：根据 CodeGraph/contract impact 选择，若不确定则三仓都跑。
- Cross-repo：所有映射 scenario IDs + 通用 contract/collection guards。
- Real：按 registry 指定 T2/T3/T4；缺权限/样本/网络只能 blocked。
- Regression：任何 FC 修改公共 contract、schema、manifest、scenario registry 或 runner 时，三仓完整命令族全部必跑。

## 6. 命令变更审计

- 修改 argv、marker、timeout、expected collected、环境变量或写权限视为治理变更，必须有独立 FC/receipt。
- collected 数下降默认失败；只有测试明确合并/退役且 scenario coverage 不降、reviewer 接受时才能更新基线。
- 失败后禁止添加 retry 掩盖确定性错误；只能对登记为 transient 的外部调用使用有界 retry，并保留每次尝试。
- CI 与本地 runner 必须读取同一 registry；workflow 中不得再复制另一套命令。
- registry 的任何未审修改使此前依赖它的未发布 receipts 失效并要求重跑。

