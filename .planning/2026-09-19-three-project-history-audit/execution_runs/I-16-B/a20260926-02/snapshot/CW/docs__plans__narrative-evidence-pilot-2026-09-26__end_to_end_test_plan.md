# 关键节点端到端测试与测试目录恢复方案

> 计划补充（2026-09-27）。只定义后续 G1–G4 放行测试；现在不执行下载、删除、Worker 灰度或生产写入。复用[大节点审查节奏](milestone_review_cadence.md)，不增加逐卡审查。

## 1. 强制边界

- 端到端测试从隔离输入走到该节点承诺的最终输出；不以单元测试拼接冒充端到端测试。
- 测试只操作本计划专属的运行根目录、临时 SQLite 和 fake provider。禁止将真实 `companies/`、生产 catalog、共享 derived/index、其他项目目录、正式 Worker 状态或全局 cache/log/lock 配成输出目标。
- 固定 fixture 是只读输入。真实年报、招股/再融资、IR、电话会议样本如需参加 E2E，先按样本 manifest 将其复制到本次运行的 `inputs/`，核对源 ID、字节数与冻结 SHA；执行期间只读该副本，不从生产目录直接解析或写回。
- 在线下载默认由 fake provider 模拟。只有 G0 冻结来源 URL、下载许可、provider API、限流和副作用边界，且获得该次 canary 授权后，才允许一个有界真实下载；输出、配置、日志、锁和缓存都必须重定向到本次运行根目录。无法证明重定向时禁止在线测试。
- 测试结果只保留短收据（运行 ID、代码/fixture 版本、命令与退出码、关键指标、前后清单摘要、清理结果）到本计划 `progress.md`；不保留下载正文、临时数据库、全部解析结果或重复日志。

## 2. 目录、基线和恢复协议

建议目录结构：

```text
tests/e2e/
  fixtures/                 # 小型合成输入、冻结 manifest、预期断言，只读
  .runtime/<run-id>/        # 每次新建；运行时副本、临时配置/数据库、下载和所有产物
    inputs/                 # 从许可样本复制来的文档
    sandbox/companies/      # 仿真的 company-wiki 公司目录
    state/                  # 临时 catalog、WAL/SHM、cache、lock、日志、outbox
    outputs/                # package/export、摘要、临时索引等
    run-manifest.json       # 运行 ID、允许路径、复制来源 SHA、创建路径清单
```

`.runtime/` 必须加入忽略规则且静止时为空。`fixtures/` 中的测试样本不得被执行器修改；大 PDF 不提交到 Git，运行时从显式 allowlist 复制，并用冻结 SHA 验证。每次运行使用不可复用的 run ID；目标目录已存在、含未知文件或路径经 junction/symlink 逃出运行根目录时，立即拒绝运行，绝不先清理旧目录。

每个 E2E runner 遵循同一生命周期：

1. **开始前快照**：记录 `tests/e2e/fixtures/` 与 `.runtime/` 的相对路径、类型、字节数、SHA-256、修改时间及 Windows 文件属性；记录运行根目录必须为空。只哈希本次 allowlist 样本，不遍历/重哈希 46 GiB 生产目录。
2. **写入隔离**：所有输出路径经 canonical path 检查，必须落在唯一 `.runtime/<run-id>/` 下；由 fake provider 拦截网络。真实 canary 下载也只落在 `sandbox/companies/{entity}/...`，不碰正式公司目录。调用 earnings-transcripts 时必须隔离其 CLI 配置、transcripts output、cache、log、lock；做不到即不运行真实 CLI。
3. **执行与故障恢复**：在 `try/finally` 中运行；结束或失败时先停止并等待子进程、关闭 SQLite、checkpoint 后关闭连接，再清除本次运行树。Worker 进程被强杀/机器中断时，由 run-manifest 驱动的 cleanup/resume 工具只认领本 run ID，先核进程和路径归属，再清理。
4. **只删本次新建物**：只删除前快照不存在、且 manifest 证明由本次 run 创建并仍处于运行根目录内的文件/目录；禁止按通配符清理 `companies/`、项目根、transcripts 仓库或共享 cache。测试原文副本、真实下载 TXT、翻译/摘要副本、临时库、WAL/SHM、锁、日志、索引及中间产物均属于本次运行物，测试结束一并删除。
5. **结束后核对**：关闭子进程后，先删除唯一 run-id 子树；再把 `.runtime/` 这个预先存在的父目录修改时间/属性恢复成开始前记录值；比较路径、类型、内容 SHA/长度、文件/目录修改时间和属性。`.runtime/` 回到原先空状态，fixture tree 完全不变。结果不相同、遗留进程/文件、路径越界或清理失败，均判该 G 节点失败并暂停后继放行；不得把删除遗留物的清理失败静默记为通过。

访问时间可能因只读读取而变化，不作为差异；路径、内容、长度、文件/目录修改时间与属性必须一致。基线文件一律不写，因此正常清理只删除本次新建的 run 目录，再恢复唯一受影响的 `.runtime/` 父目录元数据，不覆盖用户已有数据。若检测到基线文件被改写，先停住并报告，不自动覆盖；只有确认是测试执行器造成且存在本次运行前的校验副本时，才从该副本恢复测试目录中的该文件，并留下事故记录。任何生产/外部路径变化均不得由通用 cleanup 猜测或删除。

## 3. 各放行节点的端到端用例

| 节点 | 隔离端到端路径 | 关键断言 |
|---|---|---|
| **G1 来源到叙述证据包** | 年报/半年报/季报、招股及再融资、IR、英文 transcript、低价值格式文件的 manifest 样本副本 → resolver/分类 → 轻量解析 → 选择/coverage → 摘要草稿 → package → locator 从同一 raw 副本回读。transcript 使用 fake provider 覆盖 filing-fetch adapter；满足许可时另作一次有界、单文件 live canary。 | 探索卡和关键负例符合预期；源身份、角色、时点、语言、否定/限定词保留；定位回读同 SHA；标准财务表不被误写成业务摘要；TXT 不翻译；旧全量 normalized/span 零增量；未覆盖/解析失败不伪报完整。真实 canary 若运行，下载文件只存在于 run sandbox，结束删除且目录快照一致。 |
| **G2 检索与下游消费** | G1 冻结 package/export → 本仓检索/预览/resolve → StockWiki、revenue-forecast、invest-quick-scan 的只读合同 harness（旧/新/未知/撤回/历史时点 fixtures）。 | `source_id + locator` 可回到隔离 raw；导出哈希和版本正确；消费者只读、拒绝未知合同、不会把来源摘要当投资结论；无写入其他仓库；删除临时 export 与 fixture 派生物后恢复目录基线。 |
| **G3 Worker 受控并发** | 临时 source catalog/job store + fake provider + 1/2/4 文档负载 → claim → parse/select/summary → artifact prepare/visible → export；在 provider 返回、文件 fsync、DB commit、outbox ack、暂停/恢复和进程退出点注入故障。 | Windows 真子进程验证无重叠 claim/重复 accepted artifact；丢失/超时 job 可恢复；暂停后没有新网络/claim/激活；同 key 幂等；限流正确；测试结束无 child process、锁、WAL、outbox 或文件遗留。此处不对真实生产队列做演练。 |
| **G4 原文处置/物理删除** | 只在运行时复制的 scratch company tree 上走处置资格 → 引用检查 → intent → 删除副本 → receipt/恢复；分别在 intent 前、删除后、receipt 前中断并重跑。 | 低价值唯一来源、重复副本、混合业务材料、OCR/附件缺口、旧 locator 等反例按计划失败关闭；只删除 scratch 副本、不接触真实原文。故障后能恢复/识别；清理 run tree 后 fixture 与开始前清单完全一致。生产批次删除另执行既有 G4 逐路径许可和 receipt，本 E2E 通过不等于批准真实删除。 |

不为 G0 增加全链 E2E：G0 的目标是冻结接口/门槛，使用静态只读 contract fixtures。G1–G4 各集中执行一组覆盖范围明确的 E2E；日常小改只跑受影响的单测/contract test，只有影响 G 节点结论的输入或实现变化才重跑相应 E2E。

## 4. 放行收据

G1–G4 的现有大节点收据统一增加以下字段，而不是再设小节点签字：

- `run_id`、测试根 canonical path、代码 commit/dirty 状态、fixture manifest SHA、配置/parser/selector/summary/worker 版本；
- 测试命令、退出码、使用 fake/live provider、样本类型/数量、关键质量/空间/并发指标；
- 开始/结束文件树条目数与总字节、baseline equality 结果、遗留进程/文件数、cleanup 退出码；
- 失败和恢复记录、已授权的 live canary 范围、放行或 hold 范围。

真实 canary 生成的原始文档与全部临时派生文件在清理后不保留；收据保留来源标识和 hash 即可。若需保留文档作为新的固定 fixture，必须另行走来源许可/fixture manifest 审查，不能从 E2E 输出目录直接留下副本。
