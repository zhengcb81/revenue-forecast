# 三仓 E2E 与动态审核场景矩阵

## 1. 测试层级

| 层级 | 名称 | 数据/网络 | 运行频率 | 能证明什么 |
|---|---|---|---|---|
| T0 | unit/contract | temp 数据，无网络 | 每次提交 | 局部契约、错误分类、确定性 |
| T1 | isolated cross-process | temp 三根、真实三仓进程、spy provider | 每个 PR | 用户入口到 consumer 的真实接线 |
| T2 | production read-only | 真实 catalog/三根；生产 catalog 与 source roots 零写入；审计输出写隔离目录 | 本地每日 | 真实数据可解析、可复用、根未改变 |
| T3 | real-provider isolated download | 真实 provider，临时 wiki 写入 | 每周/发布前 | CN/HK/US 实际下载与第二次零下载 |
| T4 | production canary | 明确批准的最小 cohort | 发布窗口 | 真实 cutover、回滚、观测指标 |

T2/T3/T4 不能由 T0/T1 替代；T3/T4 未获授权时状态只能是 blocked，不能被 skip 当成 pass。

## 2. 权威 spy 与副作用预算

每个跨进程场景必须收集统一事件日志：

- `provider_discover_calls`
- `provider_fetch_calls`
- `canonical_write_calls`
- `external_root_write_calls`
- `parser_calls`
- `llm_calls`，按 role 分类
- `artifact_read_calls`，按 role 分类
- `resolution_outcome`
- `policy_hash`、`activation_epoch`、`triplet_hash`

计数必须来自事件/journal，不得由“是否返回 handle”等结果倒推。

## 3. Mandatory 场景

### A. 精确复用与多根

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| EX-01 | T1/T2 | companies-only、完整 provenance | exact reuse；discover/fetch/write=0 |
| EX-02 | T1/T2 | dayu-only、完整 provenance，companies 无同 hash | exact reuse；返回 dayu location；write=0 |
| EX-03 | T1/T2 | Dropbox-only、完整 sidecar，其他根无同 hash | exact reuse；返回 Dropbox location；download/parser/LLM=0 |
| EX-04 | T1 | 同一 bytes 跨三个根 | 一个 document；确定性 canonical location；不复制文件 |
| EX-05 | T1 | 同公司同年不同 provider_document_id | 按 request 精确选择；无歧义吞并 |
| EX-06 | T1 | amended 与原版并存 | revision 规则稳定；请求 amended 时返回更正版 |
| EX-07 | T1 | root 顺序/扫描顺序随机化 | 输出 handle/bundle hash 不变 |
| EX-08 | T1 | 新 `future_lake` root + sidecar adapter，仅改配置 | 无产品代码改动即可复用，证明真正泛化 |

### B. Dropbox 安全边界

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| DBX-01 | T1/T2 | 真实 Dropbox-only annual filing | REUSED_EXACT；canonical path 在允许 root 内 |
| DBX-02 | T1 | 无 sidecar 的“年报.pdf” | index 可选，但 filing reuse 拒绝；不得猜字段 |
| DBX-03 | T1 | sidecar hash 与 bytes 不同 | fail closed；sidecar/文件均不被改写 |
| DBX-04 | T1 | broker report 名称含“年报” | document_kind=broker_research；不得满足 filing |
| DBX-05 | T1 | path traversal、symlink/junction 越界 | 拒绝且记录 policy reason |
| DBX-06 | T1 | 文件已退休/撤销 | 不复用；不得因重扫自动恢复 |
| DBX-07 | T2 | 真实根 canary 前后指纹 | 三根 bytes/count/mtime 集合不变 |
| DBX-08 | T4 | Dropbox cohort rollback | rollback 后相同 request 回到旧行为；文件和 assertions 保留 |

### C. missing、下载与幂等

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| DL-01 | T1 | missing + allow_download=false | discover/fetch/write=0，明确 not_found/gap |
| DL-02 | T1 | missing + 过期/错误授权 | fetch=0，拒绝原因精确 |
| DL-03 | T1 | stale gap hash/policy hash | fetch=0；不可复用旧授权 |
| DL-04 | T1/T3 | CN missing + 有效授权 | 只下载允许候选到 companies；第二次 fetch=0 |
| DL-05 | T1/T3 | HK missing + 有效授权 | 同上，使用 dayu HK adapter |
| DL-06 | T1/T3 | US missing + 有效授权 | 同上，使用 SEC/dayu adapter |
| DL-07 | T1 | fetch 成功但 bytes/hash/sidecar 不合法 | 不 commit；staging 可审计清理；原 catalog 不变 |
| DL-08 | T1 | 两个并发相同下载请求 | single-flight；最多一次 provider fetch/canonical commit |
| DL-09 | T1 | commit 后进程中断 | 重启后幂等恢复；不产生重复文档/位置 |
| DL-10 | T1 | 外部根被设置为 write target | 配置加载即失败 |

### D. latest_as_of 闭环

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| LT-01 | T1/T3 | 本地已经是 provider 最新 | metadata discover 可为 1；fetch/write=0；返回本地 handle |
| LT-02 | T1/T3 | Dropbox 有旧期、provider 有新期 | 复用旧期 + 只下载缺失新期；返回最新 handle |
| LT-03 | T1 | companies/dayu/Dropbox 共同覆盖期间 | 合并 coverage；不得重复下载 |
| LT-04 | T1 | provider 重复候选 | 按 provider_document_id/revision 去重 |
| LT-05 | T1 | provider 不可用 | 不把“未知”当“无缺口”；返回可重试 GAP 并保留本地 reuse |
| LT-06 | T1 | as_of 之前/之后候选 | future 报告不得泄漏进响应 |
| LT-07 | T1 | not-yet-published | 明确 not_published；fetch=0 |
| LT-08 | T1/T3 | 下载完成后立即 re-resolve | 返回 capture-ready 最新 handle，不允许调用者再手工重试 |
| LT-09 | T1/T3 | 同一 latest 请求第二次执行 | provider fetch=0；canonical write=0 |
| LT-10 | T1 | 下载部分成功/部分失败 | 原子策略明确；不得谎报 complete |

### E. SourceBundle 与处理产物

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| AR-01 | T1/T2 | valid normalized/markdown/sections/summary | 相应 parser/LLM=0，真实读取 artifact |
| AR-02 | T1 | 仅 summary 缺失 | 只运行 summary producer；其他角色 hash 不变 |
| AR-03 | T1 | normalized generator version 变更 | 只使依赖 DAG 失效，不全量盲重算 |
| AR-04 | T1 | raw source bytes 改变 | 所有绑定旧 source hash 的 artifact 不复用 |
| AR-05 | T1 | artifact bytes 被篡改 | fail closed；不得只断言返回 dict |
| AR-06 | T1 | consumer_analysis model/prompt/input hash 改变 | analysis 不复用，基础 markdown 可继续复用 |
| AR-07 | T2 | 真实生产 bound artifacts | 每种 mandatory role 至少 1 个真实成功样本 |
| AR-08 | T2 | legacy_unbound artifact | 保留但 bundle 标记不可复用；不打开即信任 |
| AR-09 | T1 | duplicate document 跨 roots | artifact 按 document/content 共享，不按路径复制 |

### F. 身份、provenance 与安全

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| SAFE-01 | T1 | 同名异 ticker/market | identity conflict；download=0 |
| SAFE-02 | T1 | company name 被误存为 security_id | 不得 soft-match 成有效强身份 |
| SAFE-03 | T1 | published/retrieved/period_end 缺失 | 不 capture-ready；进入 remediation |
| SAFE-04 | T1 | source URL 非 HTTPS/不允许 provider | fail closed |
| SAFE-05 | T1 | prompt injection 检测未执行 | 不得自动写 `not_detected` |
| SAFE-06 | T1 | prompt injection 命中 | 数据仅作为 untrusted input；状态和处置有 receipt |
| SAFE-07 | T1 | retired assertion 与 active assertion 冲突 | fail closed/ambiguous，不选择“最新一行”掩盖冲突 |

### G. 控制平面、故障和可移植性

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| CTRL-01 | T1/T4 | flag=false + DB active row | resolver 必须忽略 active v2 row |
| CTRL-02 | T1 | activation epoch 不匹配 | resolver 不可见 |
| CTRL-03 | T1 | cohort 部分激活故障 | 整个事务回滚，无半激活 |
| CTRL-04 | T1/T4 | 真实 rollback | 同一 request 响应回退；assertions 不删除 |
| CTRL-05 | T1 | request 执行期间 policy 切换 | request snapshot 结果稳定 |
| OPS-01 | T1/T2 | scan completed_with_errors 超阈值 | canary 非零退出并阻断 release |
| OPS-02 | T1 | catalog lock/timeout | 有界重试、结构化错误、无死锁 |
| OPS-03 | T1 | 49GB catalog 的只读查询 | 满足 SLO，禁止全表 Python 扫描 |
| PORT-01 | T1 | Windows 中文用户名/路径 | JSON/subprocess 无 mojibake/UnicodeDecodeError |
| PORT-02 | T1 | 路径含空格、大小写差异 | 行为一致 |
| PORT-03 | T1 | Linux 当前 triplet | 同一 golden trace 通过 |

### H. Index 与真实文件生命周期

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| IDX-01 | T1/T2 | 合格 filing 已存在于配置 root，但 catalog 尚无记录 | 扫描后 exact reuse；provider fetch=0；源文件零改动 |
| IDX-02 | T1 | catalog location 指向已删除或离线文件 | 不返回假 handle；标记 stale location；其他有效 location 仍可复用 |
| IDX-03 | T1 | 文件在同一只读 root 内移动，bytes/sidecar 不变 | 同一 document identity；新增 location、旧 location 失效；绑定 artifacts 继续复用 |
| IDX-04 | T1 | index 后源文件 bytes 被替换但路径不变 | hash mismatch，旧 assertion/artifacts 不可复用；不得用 mtime/文件名掩盖 |
| IDX-05 | T1 | 零字节、截断、损坏或加密 PDF | fail closed；明确 remediation reason；parser/LLM 不得继续 |
| IDX-06 | T1 | 文件被锁定、权限拒绝或扫描中短暂离线 | 有界失败；不写半 assertion；重试/恢复后结果幂等 |
| IDX-07 | T1 | 首次无 sidecar 被拒，随后增加/修正 sidecar | 重扫只产生 shadow proposal；未经 review/activation 不得自动 active |
| IDX-08 | T1/T2 | 大 root 增量扫描中断后 resume，再运行一次 | 无重复 document/location/assertion；exact 选择稳定；真实 root 指纹不变 |

### I. 从用户入口出发的组合旅程

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| UJ-01 | T1/T2 | companies-only 最新 filing 且全部工件有效 | revenue 用户入口成功；download/parser/LLM=0；artifact_read>0 |
| UJ-02 | T1/T2 | dayu-only filing 只有 raw，无处理工件 | download=0；仅生成必需工件；第二次调用 producer=0 |
| UJ-03 | T1/T3 | Dropbox 只有旧期，provider 有一个新期 | 旧期复用、只下载新期到 companies、生成新期工件；第二次 fetch=0 |
| UJ-04 | T1 | 三根都缺失且 allow_download=false | 返回结构化 gap/not_found；discover/fetch/write/parser/LLM=0 |
| UJ-05 | T1/T3 | 三根都缺失且授权下载 | 一次用户调用完成下载→commit→scan→resolve→处理；第二次完整复用 |
| UJ-06 | T1/T2 | filing 已最新但 summary/analysis 版本陈旧 | download=0；只失效相应 DAG 子树；基础工件继续复用 |
| UJ-07 | T1 | 多根存在身份/期间冲突 | 用户入口 fail closed，返回可处置 reason；download/write=0 |
| UJ-08 | T1 | 同一请求需要 annual、semiannual、quarterly 的混合期间 | 逐项复用已存在报告，仅补齐真正缺口；结果逐项可追踪 |

### J. 动态审核系统自证

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| AUD-01 | T0/T1 | T2 报告超过 freshness window | release gate 非零退出；不得沿用旧绿色 |
| AUD-02 | T0/T1 | report/receipt 的 triplet 与当前 manifest 不同 | 拒绝证据并要求重跑 |
| AUD-03 | T1 | Dropbox-only/dayu-only 样本缺失或已重复到其他 root | T2 阻塞并告警；不得 skip/降级为 companies-only |
| AUD-04 | T1/T2 | source root 指纹在只读 canary 前后变化 | canary 失败并标记疑似外部写；保留前后证据 |
| AUD-05 | T1/T2 | scan error/interrupted、artifact binding 或 legacy-hit 指标恶化 | 超阈值即阻断；dashboard 展示具体 delta 和 owner |
| AUD-06 | T1/T3 | provider 凭据/网络缺失或被限流 | 状态为 blocked/infra_failure；不得生成绿色 T3 |
| AUD-07 | T0/T1 | receipt 被篡改、reviewer 与 implementer 同身份或命令日志缺失 | validator fail；不能进入 accepted |
| AUD-08 | T0/T1 | audit runner 超时、被杀或只写出半份报告 | 原子发布失败；旧报告不覆盖；release gate 阻断 |

### K. 迁移与回滚完整性

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| MIG-01 | T1 | schema/assertion/artifact migration dry-run | catalog bytes/row counts 不变；完整 proposal 与容量估算 |
| MIG-02 | T1 | 批迁移中途进程终止后 resume | 从 journal 安全继续；无漏行、重行和双绑定 |
| MIG-03 | T1 | 已完成 migration 再执行一次 | 结果和 hashes 不变；零重复 assertion/artifact binding |
| MIG-04 | T1/T4 | 最小 cohort migration 后 rollback | resolver 回到 before trace；新记录保留但不可见；不删除真实文件 |
| MIG-05 | T1/T2 | provenance 无法证明的历史记录 | 进入 unprovable/legacy_unbound；不得为提高覆盖率猜测绑定 |
| MIG-06 | T1 | 同 document 多 location、重复或冲突 assertion | 去重/冲突分桶确定；不以“最后一行”为赢家 |
| MIG-07 | T1 | 磁盘不足、锁冲突或 journal 写失败 | 当前 batch 原子失败；可恢复；原 catalog 仍通过 integrity |
| MIG-08 | T1/T2 | 1.x/2.x shadow query 与固定 corpus 对比 | 所有差异有规则和 reviewer；未解释差异阻断 cutover |

## 4. 真实样本注册表要求

- companies、dayu-only、Dropbox-only 各至少 2 个 capture-ready 样本；至少覆盖 CN/HK/US 中可实现的组合。
- “only”要求其他 root 不存在相同 document/content hash；否则不能证明该 root 功能。
- 样本只记录 hashed identifiers 和预期字段，不在 CI artifact 泄露真实绝对路径。
- 样本失效后自动阻断 canary，并要求 reviewer 替换；不得把 skip 视为 pass。
- 如 Dropbox 当前不存在合格唯一样本，必须由用户明确批准一个真实披露文件及 sidecar 进入专用 canary 子目录，或批准使用既有唯一文件；不得删除 companies 中重复文件来制造样本。

## 5. 场景完成定义

- 本矩阵共 95 个 mandatory scenario；任何新增生产能力必须先增加场景，再增加实现。
- 每个场景在机器 registry 中必须登记 owner、适用层级、fixture/sample ID、oracle、side-effect budget、timeout、freshness window 和生成证据路径。
- 多层级场景必须分别生成独立结果；例如 `T1/T2` 的 T1 通过不能把 T2 自动标为通过。
- 单个场景只有在行为断言、负向断言、副作用计数、输出契约和证据哈希全部通过时才为 `passed`。
- 由于授权或外部设施无法运行的真实层级只能是 `blocked`；closure gate 不接受 mandatory blocked。
