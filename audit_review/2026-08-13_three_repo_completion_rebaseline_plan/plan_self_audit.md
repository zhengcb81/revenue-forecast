# 计划自身对抗式审计

> 审计对象：本目录内容文件与其冻结annex。  
> 审计目的：证明这是可执行、不可用文字假绿的下一步计划，而不是对现有缺陷的再次摘要。

## 1. 结构和唯一性

| 检查 | 结果 | 解释 |
|---|---:|---|
| CA定义 | 25/25唯一 | CA-001～004、101～109、201～206、301～306 |
| 未定义CA精确引用 | 0 | 目录内所有`CA-NNN`均有定义 |
| CA直接自依赖 | 0 | 逐卡解析`依赖`字段 |
| ZR定义 | 92/92唯一 | 冻结annex registry |
| 未定义ZR精确引用 | 0 | 本目录引用都能在annex找到 |
| 旧场景 | 95/95唯一 | 来源hash `21e920...d3c5` |
| 新场景 | 102/102唯一 | 来源hash `e08cbe...ac8a` |
| 合计场景 | 197唯一、交集0 | 每个required tier未来必须单独result |
| 零字节文件 | 0 | manifest生成前内容文件全非空 |
| 临时/锁/备份文件 | 0 | 无`.tmp/.lock/.bak/~`残留 |
| 相对Markdown链接 | 0 | 文件导航使用明确文件名和manifest；不存在破链 |

冻结的architecture、ZR registry、scenario matrix、weak-model runbook和旧95场景hash均已重算匹配。输入30个文件的path/size/mtime/hash完整记录在`input_snapshot.md`。

## 2. 旧计划无遗漏检查

- 71 FC逐项有分类和successor，不以phase汇总代替单项。
- `legacy_fc_status_registry.md`机器复核为71行/71唯一，I=31、C=26、S=9、P=5，所有精确successor均已定义。
- R0～R9十个release waves逐项迁移；R9明确pending且强门4/4 RED。
- FC-1501～1505全部由更强CA closure链替代。
- 31 I、26 C、9 S、5 P合计71；current verified complete明确为0，避免与旧66/71混用。
- “可保留资产”与“当前完成状态”分离：前者允许already-satisfied复验，后者不继承。
- terminal状态统一为`closed_superseded_incomplete`；只有CA-306能由旧owner写入，不在本轮并发改旧文件。

## 3. 用户痛点无遗漏检查

| 痛点 | 是否有根因 | 是否有原子单元 | 是否有正/负/故障测试 | 是否有终验 |
|---|---:|---:|---:|---:|
| 真只读/DB锁 | 是 | ZR-201～206 | READ-01～12/live WAL | CA-302/303 |
| Dropbox/dayu/future root | 是 | ZR-401～409 | 物理排他+policy/path负例 | CA-302 |
| 配置/runtime全请求一致 | 是 | ZR-401/404/405、CA-003 | hash/None/v1-v2分叉mutation | CA-303 |
| 最新期间/修订/最小下载 | 是 | ZR-406～408/805 | amendment/多gap/授权/并发 | CA-302 |
| 旧MD/摘要/切片/标签复用 | 是 | ZR-301～307 | valid/partial/legacy/source-change | CA-302 |
| 真worker/优先处理 | 是 | ZR-507/508/706 | demand dedupe/crash/privacy | CA-302 |
| prompt/隐私/egress | 是 | ZR-302/303/501/507 | malicious content+egress spy | CA-302/303 |
| 券商研报/表格/多实体 | 是 | ZR-501～510 | BR-01～26、七PDFgolden | CA-302 |
| 官方网页保存/索引 | 是 | ZR-509/510 | 错entity 200页+有效页二次复用 | CA-302 |
| revenue schema/generator | 是 | ZR-701～703 | REV-01～04/真实engine | CA-302 |
| validate-only/draft/publication | 是 | ZR-704/705/710 | 写syscall/互换/故障注入 | CA-302 |
| 逐矿/地区/储量/收入 | 是 | ZR-601～611/707/711 | MINE-01～24+第二矿企 | CA-302 |
| backtest/confidence | 是 | ZR-708/712/713 | gaming/metamorphic/rolling-origin | CA-302 |
| 真实E2E/Windows | 是 | ZR-801～806 | 三进程/T2/T3/Unicode/long path | CA-301/302 |
| 动态审核 | 是 | ZR-901～905、CA-201～206 | missed/stale/half/alert mutations | CA-301/305 |
| 硬编码/复杂度/R9 | 是 | ZR-104/906/907、CA-303/304 | AST/caller/CC/R9强门 | CA-305 |

## 4. 防弱模型跑偏检查

- 每个单元要求production entrypoint RED，helper测试不能宣称full-chain。
- 允许/禁止文件、side-effect budget、独立oracle、rollback和stop condition为卡片必填。
- 明列19类常见错误实现及对应kill gate；包括root特判、假的只读、v1结果贴v2 hash、非排他Dropbox、事件字符串当worker、产量×价格伪收入、marker coverage和R9改skip。
- T0/T1/T2/T3/T4不可替代；样本/网络/凭据缺失只能blocked，不能skip/pass。
- implementation最多到independent_review；只有closure validator能accepted。
- reviewer必须clean checkout、不同身份、重算hash、重跑fault/mutation和rollback。
- plan/registry/schema/migration等共享资源single writer；发现并发漂移立即停线。

## 5. 渐进重构安全性

计划没有回避全面重构，但把它拆成可回滚顺序：

1. 先修证据系统，确保后续不会假绿。
2. Reader先上线，不同时迁数据/删旧链。
3. lifecycle/RootPolicy只做additive shadow；同请求固定RuntimeContext。
4. roots按companies→dayu→Dropbox→future小cohort。
5. legacy artifact先分类、再最小迁移；不可证明不绑定。
6. broker和mine model先shadow，不自动替代正式forecast。
7. revenue source/publication新链小cohort，执行真实rollback。
8. 连续动态周期zero-hit后才分批R9；每批全矩阵。

因此即使实施中发现目标架构需要较大重构，也有明确before/shadow/diff/cohort/rollback/delete门，不依赖一次大合并成功。

## 6. 动态保证不是“脚本存在”

- PR验证精确candidate triplet，任一仓变更fan-out。
- Daily/Weekly/Monthly分别有真实tier、unique sample、freshness和atomic报告。
- scheduler不存在、停跑、报告过期、半写、告警失败、旧绿复制全部是release-blocking mutation。
- closure要求7 Daily、2 Weekly、1 Monthly、1 alert drill的自然时间；不能人工豁免。
- 动态报告本身受Closure 2.0校验，避免审计机制变成新的不受审计旁路。

## 7. 计划没有做的事

- 没有修改三个产品仓的代码、配置、测试、CI、数据库、索引或roots。
- 没有重跑CodeGraph；当前并发期索引重建留给CA-003独占窗口。
- 没有更新旧计划的checkbox/status；terminal notice留给CA-306和旧owner。
- 没有下载、处理或外发任何文档。
- 没有把观察HEAD当未来implementation triplet。

## 8. 剩余不可消除的不确定性

1. 三仓仍在变化；未来开始必须重基线，当前行号和数据计数会漂移。
2. sandbox/Windows环境造成部分测试噪声；计划用短ASCII控制组和变量组区分。
3. 历史Dropbox摘要是否实际经外部网络、当时是否授权，catalog不足以证明；必须做独立egress/receipt审计，不能在计划中定罪或洗白。
4. 逐矿2026～2030收入并非公开资料普遍披露；成功定义是可勾稽模型估计或明确gap，不是强造数字。
5. 软件无法提供“以后绝不再出现任何缺陷”的数学保证；本计划能关闭所有已知痛点，并通过动态审核、mutation和新鲜度门让同类回归被持续发现和阻断。

## 9. 自审结论

计划具备：明确目标、当前证据、旧任务逐项迁移、原子DAG、真实测试矩阵、弱模型护栏、渐进rollback、动态运营和不可伪造closure。没有发现未定义ID、自依赖、场景重复、冻结hash漂移或产品误实施。

状态：**计划可交接；产品实施全部pending。**
