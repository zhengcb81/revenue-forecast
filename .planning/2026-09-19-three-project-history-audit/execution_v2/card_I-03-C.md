本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-03-C — 把下载对象、资格与策略完整绑定到计划及授权

父项：I-03。状态：planned；实施结果：未执行。角色：company-wiki 来源负责人（filing 为消费者 reviewer）。

依赖：I-03-A、I-00-C。

执行门：前置卡的独立验收全部通过后方可执行；未定协议不得自行补选

### 现行源码锚点

- [src/company_wiki/source_catalog/gap_plan.py:214](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/gap_plan.py:214) — `_hash_gap`；SHA-256 `d18391b7fa7adf06bf882d013cd9ccae48b9fad24429c3ac66d61b68d907c79f`。
- [src/company_wiki/source_catalog/authorization.py:52](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/authorization.py:52) — `build_download_authorization`；SHA-256 `f858a369ed556d1b110be5ba7be7fa25ae3519fda94296cfe1c4f9e367d55f43`。
- [src/company_wiki/source_catalog/authorization.py:99](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/authorization.py:99) — `validate_download_authorization`；SHA-256 `f858a369ed556d1b110be5ba7be7fa25ae3519fda94296cfe1c4f9e367d55f43`。
- [src/company_wiki/source_catalog/close_gap.py:55](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/close_gap.py:55) — `CloseGapBinding`；SHA-256 `117c8166a6c26f3462574b787e0db79c419e00c8b18287f25738948032f475c3`。

### 允许改动

- 隔离 wiki gap_plan.py、authorization.py、close_gap.py 中绑定校验边界及对应 contract 测试；共享 schema 的变更严格限 I-03-A 签署字段

### 输入与独立预期

- I-03-A 的规范化字节定义和旧版本拒绝规则；计划 P0（ACME/US/annual/FY2025、a-new、https://fixture.invalid/a、2026-04-01、policy P）。URL 仅作为字符串，绝不访问。
- 一份授权 A0 指向 P0 哈希，provider=test、allowed_accessions=[a-new]、max_items=1、max_bytes=100、expires_at 为冻结测试时钟以后。字段值映射到实际 schema，不杜撰可执行 CLI。

### 按序动作

1. 在测试中按签署规范独立序列化固定 P0，固定预期 canonical bytes 与 SHA；生产函数和测试 expected 禁止共享同一个待测 hash helper。
2. 实现包含类别边界的规范 hash，避免字段拼接歧义；schema/policy/entity/market/kind/period/provider/id/url/日期/修订/资格字段按签署表绑定。
3. 为每个安全相关字段做单变量变异，保持 A0 不变，先验证计划 hash 变化，再验证授权拒绝；不只断言 hash 不同。
4. 验证无关 dict 顺序与获准候选重排不改变 canonical bytes；不能为去抖而丢掉影响资格的字段。
5. 校验授权 schema、hash 十六进制、provider、accession、过期时点和额度；缺失 provider/未知大小的政策严格取 I-03-A，不默认为已授权或无限额度。
6. 传到 close-gap 的 binding 校验同一值和版本；旧授权不自动补字段升级；运行 T-GAP 及对应新增授权用例。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| G-C1 | 只把 URL /a 改 /b，或 filing_date 2026-04-01 改 2026-04-02 | P1.hash != P0.hash；A0 授权 P1 被拒；provider fetch 次数=0 |
| G-C2 | 依次变 entity/market/kind/period/provider/id/amended/policy/资格字段，每次仅一项 | 每个安全变异触发对应绑定拒绝；不得借相同 accession 跨对象复用 A0 |
| G-C3 | 等价字段顺序/获准集合重排；request/状态分区改变 | 前者按规范同 hash；后者是否变 hash 由 I-03-A 固定，类别变更不得隐形 |
| G-C4 | 已用1件；已用90 bytes 加候选20 bytes；旧版本授权；过期1秒；缺provider | 前两者拒绝且fetch=0；旧版/过期/缺provider按签署规则拒绝或显式重新授权，不能默认通过 |

### 本卡追加证据

- 固定 canonical bytes 与独立 SHA；逐字段变异表；授权拒绝原因与 fetch spy=0；schema 迁移差异和 reviewer 收据

命令： T-GAP；执行前遵守上方预检，新增测试节点另绑定。

### 失败停止条件

- hash 仅变而授权仍通过；默认补关键字段；引用未批准 canonical 化；将迁移变成重新签发旧授权

### 恢复边界

- 回退隔离代码；旧授权保留原 hash 不改写；若旧授权不兼容则明确失效，不能降级验证

### 关闭标准

- 历史 URL/date 同 hash 反例关闭；每个安全字段既有 hash 断言又有授权拒绝断言；正例授权仍通过
