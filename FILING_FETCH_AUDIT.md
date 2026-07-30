# Filing Fetch 独立技能全面审查

审查日期：2026-07-26  
审查对象：`C:\Users\郑曾波\.agents\skills\filing-fetch` v1.0.0  
依赖边界：company-wiki `source_catalog`、StockInfoDLSimple/cninfo、dayu-agent、revenue-forecast 和 invest-* 消费端

## 一、直接结论

下载公司财报/监管文件的步骤确实已经被设计为独立技能：`filing-fetch`。

其目标架构是：

```text
consumer skill
  → filing-fetch thin client
  → company-wiki source catalog
  → resolve existing index
  → only after authorized miss: market adapter
      CN → StockInfoDLSimple/cninfo
      HK/US → dayu-agent
  → company-wiki canonical writer
  → companies/{entity}/raw/{kind}/...
```

这个所有权方向是正确的，而且 company-wiki 上游实现已经具备较强的 reuse-first、staging、hash、dedup、canonical write 和 provenance 保障。

但当前仍存在两个架构事实：

1. `filing-fetch` 自身是独立薄客户端；
2. revenue-forecast v3.10 又内置了一套约 2080 行 acquisition runtime。

因此整个生态目前仍是“双 owner”，尚未真正完成独立化。

综合评价：

| 维度 | 结论 |
|---|---|
| 独立技能定位 | 正确 |
| 业务泛化 | 强，无公司硬编码 |
| 上游复用 | 强，真正查询 company-wiki catalog |
| 下载路由 | 强，由 company-wiki 统一拥有 |
| canonical storage | 强，由 company-wiki writer 保证 |
| 客户端输入契约 | 弱至中 |
| 客户端输出验证 | 弱 |
| 授权可审计性 | 弱 |
| 错误/版本兼容 | 弱至中 |
| 测试完整性 | 中，正常路径较好，对抗路径不足 |
| 与 revenue/invest 协同 | 目标正确，但迁移未完成 |

当前适合作为受控环境中的 filing 获取入口，但在修复客户端边界前，不应把它返回的 `capture_ready` 仅凭布尔字段视为独立验证过的可信证明。

## 二、技能内容与模块设计

技能目录很小：

- `SKILL.md`
- `CHANGELOG.md`
- `config/company_wiki.json`
- `scripts/fetch_filing.py`：419 行
- `tests/test_fetch_filing.py`：561 行

### 做得好的部分

1. 目标单一：只负责 filing resolve/fetch，不进入收入、利润或估值模型。
2. 默认 read-only reuse；下载需要显式 `--allow-download`。
3. 使用结构化 subprocess 参数，`shell=False`。
4. 配置只支持明确 token，未知 token fail closed。
5. fuzzy query 会拒绝 ambiguous、missing、conflict、unverified 和 inactive identity。
6. 不复制 CN/HK/US adapter、canonical writer、hash、dedup 等上游业务逻辑。
7. 消费者只接收通用 handle，再转换为自己的 capture schema。

### 模块化不足

419 行本身不算过大，但一个文件同时负责：

- config 读取；
- request 规范化；
- identity orchestration；
- subprocess transport；
- upstream response parsing；
- filing resolution；
- CLI；
- error mapping。

建议拆为：

```text
scripts/
  filing_contracts.py     # request/response/error/version
  company_wiki_client.py  # subprocess transport and deadline
  filing_service.py       # resolve/ensure orchestration
  fetch_filing.py         # thin CLI only
```

拆分必须在对抗性测试建立后进行，不能边拆边改变 acquisition 语义。

## 三、泛化性

正式实现没有公司名称分支。测试使用 AMD、中微公司、小米等，只是 fixtures。

配置：

```json
{
  "schema_version": "1.0",
  "company_wiki_root": "${USER_PROFILE}/Projects/company-wiki"
}
```

没有用户绝对路径硬编码，根目录可移动。

泛化限制主要不是业务模型，而是运行环境：

- 假设 company-wiki Python package 能通过 `sys.executable -m` 从 root 启动；
- 没有 capability/version handshake；
- CLI 没有总 timeout 参数；
- 当前默认配置测试依赖本机真实 company-wiki。

## 四、实际 reuse-first 和下载安全

### Filing-fetch 自身

- 默认调用 `resolve`；
- `allow_download=True` 时直接调用 `ensure`；
- 客户端没有先执行一次单独、可观察的 `resolve`。

### Company-wiki 上游

上游 `ensure` 当前确实严格 reuse-first：

1. resolver 查询 catalog；
2. exact/equivalent 命中立即返回；
3. ambiguous 或 identity conflict 不下载；
4. 未授权时返回 missing；
5. 授权后按 market 选择 adapter；
6. discovery 后用 provider identity 再 resolve；
7. 仍缺失才 fetch；
8. fetch 只写 request-specific staging；
9. 校验 receipt、path containment、size、SHA-256、PDF magic、HTTP 状态；
10. canonical writer 做 exact-byte dedup；
11. 原子写入 `companies/{entity}/raw/{kind}/...`；
12. 写 immutable provenance；
13. 重新扫描并要求 exact provider identity 可 resolve。

本次实际运行 company-wiki 五个相关 contract test 文件，21/21 通过。

结论：当前 `ensure` 不是盲下。但这个保证只存在于上游实现和测试中，filing-fetch 没有验证上游 schema/capability。一旦上游契约漂移，客户端不能 fail closed。

## 五、关键缺陷

### High-1：显式身份路径绕过 verified/active gate

只有 `company_query` 会调用 identity resolver。调用者提供：

```json
{
  "entity": "...",
  "market": "...",
  "security_id": "..."
}
```

时，filing-fetch 不执行 verified/active identity。

已复现：

- 猜测 entity；
- `market="ZZ"`；
- 猜测 security ID；
- 客户端仍直接构造 resolve 请求。

上游可能最终拒绝部分非法值，但“每次先识别为唯一 verified active security”的技能承诺在客户端并未落实。

改进方向：public schema 1.1 统一使用 `company_query`，让上游 `resolve/ensure --company-query` 在同一原子命令中完成 identity；不得接受用户自报的 verified identity。

### High-2：capture-ready handle 没有被深验证

客户端目前只检查：

- resolution status；
- matches 恰好一个；
- `capture_ready is True`。

已复现：上游返回只有以下内容也会被接受：

```json
{"capture_ready": true}
```

没有验证：

- handle schema version；
- canonical path；
- path 是否在 company-wiki `companies` 内；
- 文件存在、非空和 byte size；
- snapshot/content SHA-256；
- HTTPS URL；
- published date 与 as-of；
- collector/capture trace；
- request ID；
- ensure status 与 resolution status 是否一致。

客户端不应复制 writer 业务逻辑，但必须验证消费边界的 typed handle，并对 canonical bytes 做必要的只读一致性检查。

### High-3：上游版本和 response schema 未校验

identity response 会检查 schema 1.0，但 resolve/ensure response 不检查 schema。

已复现：`schema_version="999.0"` 仍被接受。

此外：

- output schema `"1.0"` 在多处硬编码；
- 没有 `SKILL_VERSION`；
- 没有 input schema version；
- 没有 resolver/ensure compatibility matrix；
- 没有跨仓库 consumer contract fixture。

### High-4：下载授权不可审计

`--allow-download` 只是 boolean：

- 没有 user event ID；
- 没有授权者；
- 没有 normalized request hash；
- 没有 confirmed-gap receipt；
- 没有时间、scope、expiry；
- 没有 host verifier。

它只能证明某次函数调用传了 `True`，不能证明用户确实在看到缺口后授权。

如果目标是防止弱模型或不合规 agent 跳步，应要求：

1. read-only resolve 产生 missing receipt；
2. receipt 绑定 request ID；
3. user authorization 绑定同一 request hash；
4. ensure 重新 resolve 后才允许下载。

### Medium-1：request schema 不精确

- 未知字段静默忽略；
- 文档列出 explicit entity+market+security_id，但 read-only path 未强制完整；
- 日期、market、fiscal year 等主要依赖上游报错；
- bool/NaN timeout 等边界未严格处理；
- `document_kind: ...` 没有正式枚举或版本说明。

未知字段静默忽略尤其危险：较弱模型可能以为某个授权或过滤参数已经生效。

### Medium-2：identity orchestration 不够薄

company-wiki `resolve` 和 `ensure` 原生支持 `--company-query`，可以在一个进程内完成 identity + source action。

filing-fetch 却：

1. 单独调用 identify；
2. 自己解析 identity schema；
3. 自己构造 explicit source request；
4. 再调用 resolve/ensure。

这造成：

- 重复 identity contract；
- 两个 subprocess；
- 总 timeout 翻倍；
- identity snapshot 的 TOCTOU 窗口；
- 更多 response shape 分支。

### Medium-3：错误分类和退出码过于粗糙

所有 `FilingFetchError` 都返回 exit 2，包括：

- not found；
- ambiguous；
- config invalid；
- identity invalid；
- upstream contract error；
- capture provenance 缺失。

上游 stderr 的结构化 `{error_type, error}` 被压成自由文本。

自动化消费者无法可靠判断：

- 是否可以重试；
- 是否需要用户澄清；
- 是否需要授权；
- 是否是配置故障；
- 是否是上游 schema 不兼容。

### Medium-4：timeout 不是总 deadline

默认 900 秒是每个 subprocess timeout。当前 fuzzy path 至少两个调用，最坏时间约 1800 秒。

CLI 没有 `--timeout-seconds`，也没有 monotonic overall deadline。

### Medium-5：测试无法证明关键声明

现有 13/13 测试通过，compile、Ruff、ResourceWarning gate 通过，但 coverage 只有 76%。

主要问题：

1. `test_cli_main_guard_runs_and_resolves` 实际直接调用 `main()`，删除 `__main__` guard 后仍会通过；
2. 默认配置测试依赖本机真实 company-wiki，不是 hermetic；
3. 没有 request unknown-field 测试；
4. 没有 explicit identity bypass 测试；
5. 没有 response schema mismatch 测试；
6. 没有 shallow handle 绕过测试；
7. 没有 timeout/nonzero/invalid JSON 测试；
8. 没有真实 subprocess CLI happy/error contract；
9. 没有 revenue/invest consumer tests；
10. 没有与 company-wiki schema 的 conformance test。

### Low：发布卫生

- 当前目录没有 `.git`，未定位到 canonical repo；
- 存在 `.pytest_cache`、`.ruff_cache`、`__pycache__`、`.coverage` 和 `.benchmarks`；
- 没有正式 packaging/sync exclusion 检查；
- changelog 只有 v1.0.0。

## 六、SKILL.md 强制性审查

SKILL.md 的优点：

- 清楚说明 reuse-first；
- 清楚说明 market routing；
- 清楚说明默认只读和显式下载；
- 清楚说明 ambiguous 不自动选择；
- 清楚说明消费者自行转换 capture schema。

不足：

1. 没有 Required workflow 和 Hard failure gates；
2. 没有要求“先取得 missing receipt，再接受下载授权”；
3. 没有禁止 raw explicit identity 绕过；
4. 没有 input exact schema；
5. 没有 output exact schema；
6. 没有 authorization trust boundary；
7. 没有 error code/state machine；
8. 没有上游 version compatibility；
9. 没有 consumer integration 规则；
10. 没有 Windows PowerShell 示例；
11. 没有说明哪些保证由 filing-fetch 验证、哪些由 company-wiki 验证；
12. 没有正式测试/验收命令。

因此，对“弱模型不得偷步”的约束仍主要依赖文字自觉，而不是完整的结构化状态机。

## 七、建议目标架构

```text
request schema 1.1
  company_query + document selector
        │
        ▼
filing-fetch validate exact fields
        │
        ▼
company-wiki atomic resolve --company-query
        │
        ├── capture_ready → typed handle validation → return
        │
        ├── ambiguous/identity error → structured stop
        │
        └── missing → signed/host-bound gap receipt
                         │
                         ▼
                 explicit authorization
                         │
                         ▼
company-wiki atomic ensure --company-query --allow-download
  re-resolve → discover → re-resolve → stage → verify → canonical import
                         │
                         ▼
typed handle + acquisition receipt validation
                         │
                         ▼
consumer-specific capture conversion
```

核心原则：

- company-wiki 继续唯一拥有下载、市场路由、dedup 和 writer；
- filing-fetch 唯一拥有跨技能 request/response/error/authorization contract；
- revenue/invest 不再拥有 acquisition 实现；
- public 调用不接受用户自报 verified identity；
- formal download 必须能证明 missing → authorization → ensure 顺序；
- consumer 只接受版本兼容、typed、hash/路径一致的 handle。

## 八、测试与验收目标

建议最低标准：

- filing-fetch unit/contract coverage ≥ 90%；
- 默认配置测试 hermetic；
- actual subprocess `__main__` 测试；
- request、identity、resolve、ensure、handle、error、timeout 全部有正反例；
- company-wiki acquisition contract tests继续全绿；
- revenue `company_wiki_source` integration 全绿；
- invest/research 消费者共用同一 handle fixture；
- 无网络的 fake CLI contract tests；
- 可选受控真实环境 smoke test不得进入默认 CI；
- cache/coverage/pyc 不进入发布包。

## 九、最终判断

`filing-fetch` 的独立化方向是对的，而且比 revenue 内嵌 acquisition 更符合跨技能复用原则。真正需要重构的不是上游下载器，而是：

1. 把 filing-fetch 从“薄但弱校验的脚本”提升为版本化的跨技能契约层；
2. 让身份、缺口、授权、ensure 成为不可跳步的状态机；
3. 深验证 capture-ready handle；
4. 建立上游和消费者两端的 conformance tests；
5. 删除 revenue 内第二套 acquisition owner。

在这些工作完成后，filing-fetch 才能成为 revenue、invest-* 和 industry-research 共享且可信的唯一 filing 获取入口。
