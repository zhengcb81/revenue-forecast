# company-wiki 根历史、CW 恢复、WR 后继与早期专项独立审查

审查者：history_filing。2026-09-19。只写审计目录；未调用生产 worker、下载器、数据库迁移或清理。原始记录按当时版本裁决，不沿用过去 PASS，也不把后来的真实修复忽略掉。

## 覆盖与证据

- 本分区 46 Markdown 文件，15,473 原文块：14,966 个有语义判定的原文出现位置、507 个结构标签，零遗漏、零重复映射。它们不是 14,966 个缺陷。逐文件 SHA/行号/判定见 `coverage.json`、`item_ledger.jsonl`。
- 根 task_plan.md 4,417 行、findings.md 892 行、progress.md 1,348 行全文；CW 三恢复版本逐块映射保留原版本，1,008 同文本映射、86 差异块独立阅读，不能用后继 completed 覆盖旧 pending。
- 四早期专项 17 文件全文；根其它上下文 21 文件全文。docs/archive 17 文件交由 root 独立审查，见 `../wiki_archive/coverage.json`，未静默排除。
- 两份业务操作日志的 1,066 个事件和每个原文块审查工程遥测、前后状态、证据范围。879 条完全相同“测试问题保存”是历史混入测试日志的线索，不能当 879 次真实投研成功。当前 test_query 已检查 temp-root log，不据此断言今天仍污染生产。
- 污染审查业务正文不逐个核财务事实：26 组 3,886 条数量全部与 marker/header 相等，当前目标页无完整旧条目。此工程检查没有当年移出前后 hash，不能证明每项归属正确或当年零损失。额外 42 项证据判定见 `supplemental_item_ledger.jsonl`。
- 11 份 CW2.28 indexed attempt hash 均匹配；当前验收 helper 对该实际目录报 5 个 schema/gate 错误。10 份 WR 汇总收据及 3 份 raw pilot 样本重新核字段/算术，3 个显式收据 hash 链均匹配。

## 为什么测试通过仍在真实场景出错

### 1. “修复完成”经常换了验收对象

CW2.27 原目标是三家公司 discover→download→import→reuse 全链路、独立验收；早期汇总主要使用比亚迪及三公司 discover。后续 findings:407–418 的 journal 补证了中微真实下载/去重/复用，不能继续说中微没跑；宁德旧 provenance 不全仍是另一项。一个正确修复样本并不自动满足原三市场合同。

CW2.28 原 Phase3 要求的 10/100、故障注入、真实 worker restart，在 Phase3R 实际变成 limit3 和第二个 Store 打开；Phase4R 的 978/23,789 fingerprint、4 retryable 仍 PASS；Phase7 dirty 交付与 Phase9 failed/skip/xfail、Phase10 无独立 reviewer 的 candidate，也在上层汇总被写成 completed。candidate 本身是正确限制，问题是被汇总越级。

原根 findings:221–231、progress:277–315 同时出现“全部勾选/FINAL”和“CW2.28 Phase3–10 review_failed 未闭合”。这更像已知未完项被总状态遮住，并非所有问题都在后来首次回归。后继 WR 修好生命周期/回填调度的窄范围，不等于原所有 raw/source-ready/交付门已通过。

### 2. 真实成功后继存在，但范围与时间经常被放大

WR 7/27 的 3 passed/3 skipped、102 passed/4 skipped 不满足原 Windows 不 skip 门；7/29 后继的 139 测试、10 真实生命周期及 raw pilot 的 +36 normalized 确实支持当时 WR1–7 窄闭环，应保留为 `supported_scoped`。

三份 raw pilot 逐样本算术一致：

| 记录 | 汇总总耗时 | 29 样本首末跨度 | 另计 quick_check | normalized 增量 |
|---|---:|---:|---:|---:|
| WR1–7 7/29 | 37.1 分钟 | 29.023 分钟 | 6.860 分钟 | 36 |
| WR10.7 7/31 | 42.7 分钟 | 29.306 分钟 | 12.158 分钟 | 25 |
| WR10.13 8/2 | 44.5 分钟 | 29.751 分钟 | 13.522 分钟 | 2 |

不能把整个命令总耗时称为持续采样时长。最后一次吞吐通过用 `normalized>=15 OR pending_delta>0`，+2 就通过，与原 ≥15 或附机器可解释阻塞证据的门不是同一门。

WR10.7 明确 candidate、等待 next-login 是合理的；后继新 launcher session/PID 事件支持登录后启动。Step6 acceptance 所链接并 hash 匹配的 capture 却只有 tag0 一个 snapshot，worker_status 为 null；findings:24 说截断修复后 3 快照有效，没有把替代收据链接进验收。当前 capture 脚本确实改为完整 stdout，但精确 main AST 纯探针显示 30/60/120 标签实际累计等待 29/88/207 秒，不是登录锚点时刻。严格即时 UI 门仍证据不足，不代表 worker 从未启动。

“>900 秒 slow canary”实际是约 56 秒的缩时合同和真实 PDF 小于 60 秒的操作。它支持超时/存活机制，不支持真实超过 900 秒的运行声明。若允许缩时，应改门禁名称与范围，不沿用原实测承诺。

### 3. 测试通过了替身，生产执行的是额外分支

历史 fake normalizer 只收下 should_stop callback 而不执行，导致测试绿；生产执行 callback 才触发缺少 self.should_stop 的 AttributeError（findings:788–805、progress:1181）。后续使替身执行 callback 并真实重验是有效修复。

早期 pilot 将 stockwiki_writes=0 写死、无 quick_check/推进硬门，后继才引入真实读取。Strategy B 安踏已有 Dayu 年报复用样本是在 worker paused 下成功；5→30 秒 timeout 合同仅核 PRAGMA，不是活跃 writer 下用户端延迟实测。当前新 SectionQuery 默认 timeout 仍不是这条合同自动覆盖的路径。

### 4. 文件存在、已索引、可消费、事实可信是不同状态

CW 旧美团 raw/sidecar 完整而 catalog 无 source，严格只有 2/5 capture-ready；旧“4/5 文件可复用”掩盖了消费状态。今天 GP002 的 v2 root/adapter 注册错配由 wiki 主审另证，不能把相同外层错误都说成旧同一个 bug。

当前 SectionQueryService 新路径存在独立反例：failed 旧版本、错 source hash、缺 section/index 文件和不存在的 span 仍正常返回；加 completed 新版本后仍可取旧项。SQL 缺 current/status/version binding 和确定排序。`section_probe.py/json` 全在临时 SQLite，未访问生产。

早期 core-section 的 100% recall 基于少量已知文件/格式，不是盲评语料全集；页范围提取与 EvidenceSpan 的版本一致性、原文定位可重放才是买方消费所需。

### 5. 验收器及索引自身未成为强门

当前 CW receipt helper 和历史 Phase2 收据记录的源码 hash 一致。真实 Phase9 PASS 含失败/skip/xfail、Phase10 candidate 与 passed=null 不合 schema；但过去摘要写全部通过。纯临时目录反例进一步表明：旧 Phase0 PASS、新 index 指向 Phase0 FAIL、Phase1 PASS，validate_chain 仍返回空错误，因为使用“任意历史 PASS”，未绑定 index 的最新有效尝试。空 commands/invariants 也可通过形状校验。

因此“17 个验收器测试全绿”只能说明那 17 个构造例子，不能说明真实发布目录接受或错误链拒绝。应把真实 candidate 目录当输入重跑门禁，且 gate failure 不能被总结写回 PASS。

### 6. 安全与完整性的替代指标不够

当前 `_write_unhandled_exception_event` 的 message_redacted 只做 `str(exc)[:200]`。精确函数 AST 的合成 Authorization marker 探针仍完整输出 marker；没有读取或泄露真实 secret。按字段名字判断脱敏、测试仅禁止 API_key 键，都没有覆盖异常值。

archive/prune 的同日覆写与删除未绑定实际已归档 span 集合的风险由 root 当前静态和反例重证。历史 rows_written==rows_in_catalog 只证明数量，不证明逐主键/内容/恢复无损；due=false 只覆盖未到期。catalog-space 方案中的“旧 locator 继续有效”与直接 DELETE 旧 span 冲突，应先解决兼容存储。当前停止执行的状态应保留，不在本轮清理。

### 7. 活动文档与退休边界不同步

AGENTS/README 明确 source-only；CLAUDE.md:3–20 却仍自称全部 ingest/lint/query 必须遵从研究 Wiki 规则、原文直接公司根，148–172 还要求立即补 213 投资评估。README 四个历史文档链接指向已不存在 root 文件，实际在 docs/archive。边界冲突会把已经退休的旧“待办”重新引入 agent 行为。

旧研究 Wiki、估值、行业蒸馏、EventBus/Queue 重建愿景已退役，不能将这些未实现目标列为今天 company-wiki 必须补的功能。现存 source/provider/版本/索引义务则必须明确迁入当前计划，不能随旧方案取消被算作完成。

旧 dashboard_v2 的“健康88%、测试100%”实际仅测试1/1、gate66.7%；翌日 dashboard0/100 用另一指标。旧 cross_verify 按传播到13家公司称13来源高可信，缺独立 source hash，可能只是同源复制。数量与格式绿不能当研究准确性证据。

## 后续实施次序与验收要求（本轮不实施）

1. **冻结合同与版本。** 每个 claim 绑定原门槛、版本、数据集、代码/config/安装 hash、环境、消费者入口、尝试 ID；新增 supersedes，显式批准改 scope。完成状态由门禁产生，禁止摘要反向回填原历史。
2. **修复验收链。** latest index 唯一绑定、前置依赖、真实目录 schema、非空执行/不变量、stdout/stderr/exit hash、独立 reviewer 身份；加入旧 PASS+新 FAIL、缺文件、错 hash、candidate、skip、空 invariant 反例。
3. **统一 source-ready 消费。** SectionQuery 及 RF/FF 所有入口按 source/document/version/hash/当前状态/readiness 校验；坏版本、缺派生物、孤 span、重解析版本并存、跨目录原件验证必须拒绝或返回明确 gap，不普通成功。
4. **统一活动入口边界。** AGENTS、CLAUDE、README、SKILL、OPS、实际安装副本一致；source-only 与研究旧文档显式退役；Pause 原生拒绝与授权 PausedWorkerScope 临时逻辑分别说明，不能把有意授权分支误报 bypass。
5. **以真实入口重建最小业务验收矩阵。** CN/HK/US、已有公司根/Dropbox/Dayu原件、缺件下载、paused/忙库、最新/exact、身份冲突、partial/artifact无binding；至少一个持久数据样本经 resolver→byte read→capture→RF 输出完整链。每个fixture与live分开记分。
6. **重建运行窗口证据。** 单调时间锚点、原始采样时间、命令耗时/quick_check耗时分别报告；immediate login 使用预布置记录器，3快照缺任何一个不声称全通过；缩时与真实长时门分开。hash到修复后的receipt而不是仅改文档。
7. **完善隔离与信息处理。** 测试默认临时根，callback实际执行，禁生产日志；异常值真正脱敏并用合成marker测试。备份/归档/prune先验证逐主键hash、恢复、引用兼容和dry-run删除集合绑定。
8. **独立验收与观察再关闭。** 先原门矩阵，再真实样本、安装/加载版本，再观察窗口；故障保留原attempt，局部成功记 supported_scoped，剩余原Phase3–10单列。证据不足不是自动报产品坏，也不是完成。

所有新发现可直接追溯 supplemental ledger、纯探针 JSON 与原文行号。历史测试结果仅作为其时点证据，本轮没有声称重跑旧生产流程。
