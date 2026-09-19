本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-05-B — 把工件选择与实际读取分开，消费者读取已验证字节

parent：I-05；status：planned；owner：RF source-preparation 实施者；wiki byte-reader reviewer。

依赖：I-05-A、I-06-B。设计前置：D-W05。证据目录：`execution_runs/I-05-B/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [revenue-forecast/scripts/company_wiki_source.py:147](<C:/Users/郑曾波/Projects/revenue-forecast/scripts/company_wiki_source.py:147>) `select_artifact_roles`：返回两个角色列表，函数没有读取文件/执行 producer；原名字不能作调用证据。 SHA256 `aeeb7b2a63047c73eac3a9806ac0c426e645e9aa87da85606cab78770b039ff0`。
- [revenue-forecast/scripts/source_preparation.py:118](<C:/Users/郑曾波/Projects/revenue-forecast/scripts/source_preparation.py:118>) `prepare_source`：当前把选择结果写 artifact_read/producer_events。 SHA256 `5ec16eaf0fe480126b680f6e069717ebfc218ae39531372a380cfcc9b91bce46`。
- [company-wiki/src/company_wiki/source_catalog/resolver.py:2012](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/resolver.py:2012>) `SourceResolver.read_verified_bytes`：原件已有读一次并验证返回 buffer 的入口；canonical_path 自行打开会绕开。 SHA256 `783460a9f21679b439073fc6b82f4d5a43f583423d59e9ee627b0c9f149be21a`。
- [company-wiki/src/company_wiki/source_catalog/artifact_handle.py:78](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/artifact_handle.py:78>) `validate_artifact`：当前检查时读文件 hash；后续 consumer 仍须绑定实际消费的 buffer。 SHA256 `3cc8fbf4f65380d17e2f0140390ef346f7cc17504854ff04b3ddf46498317b99`。

**必读原证据**

- [tests/test_fc904_artifact_selection.py](<C:/Users/郑曾波/Projects/revenue-forecast/tests/test_fc904_artifact_selection.py>)： selection helper 与 monkeypatch receipt 测试不能证明实际 IO
- [../company-wiki/src/company_wiki/source_catalog/resolver.py](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/resolver.py>)： read_verified_bytes 合同与当前 deny/placeholder/version 拒绝
- [../company-wiki/tests/contract/test_r4bar11_deny_binds_the_byte_entry.py](<C:/Users/郑曾波/Projects/company-wiki/tests/contract/test_r4bar11_deny_binds_the_byte_entry.py>)： 已有 denied root byte-entry 修复需保留
- [.planning/2026-09-19-three-project-history-audit/reviews/revenue/review.md](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/revenue/review.md>)： FC906d selection/metadata 修复的真实范围

**只允许修改**

- RF:scripts/company_wiki_source.py
- RF:scripts/source_preparation.py
- CW:src/company_wiki/source_catalog/artifact_handle.py（按 D-W05 绑定 artifact buffer）
- CW:src/company_wiki/source_catalog/resolver.py / reader.py（仅已批准 consumer 接线接口，保留 R4 修复）
- 对应独立 IO 观测与实际进程 tests

**固定样本**

- requested_roles=['normalized']，有效 normalized 有 sentinel 文本 ALPHA=17；其它 summary/sections/consumer_analysis 缺失。
- 选择后打开前把工件同路径换成 BETA=29 或更改原件；内容同长度时仍必须校验 hash；全部在 scratch。
- raw-only；denied root；offline placeholder；缺文件；路径越界分别测试。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W05B-P1 / positive**：读有效 normalized sentinel 并用于消费者输出/解析。
  预期：selected_roles 只能证明计划；独立 IO 记录与消费结果证明读取 ALPHA=17，事件 hash/字节数匹配实际 buffer；producer_invocations=[]。
- **W05B-P2 / positive**：raw-only 需求。
  预期：实际 verified raw read 后可用；不会调用 parser/LLM 或强制补其它角色。
- **W05B-N1 / negative**：只选中 role，没有实际 open/read 或 downstream 未使用内容。
  预期：artifact_read_events 不可伪填；该卡验收失败，即使 receipt fields/schema 都正确。
- **W05B-N2 / negative**：select 后替换为 BETA=29/同长度错 hash/缺文件。
  预期：不能把旧 hash 的成功事件配新 bytes；拒绝或重新核验到新版本并按策略阻断，不能沿旧 review 继续。
- **W05B-N3 / negative**：denied root/placeholder/越界 path/来源绑定错误。
  预期：拒绝实际读取，不 hydration、不 provider、不通过 raw canonical_path fallback 绕过门。

**按序执行**

1. 先冻结事件 schema 与 raw/artifact verified-read 接口；source hash 与 artifact hash 不混用。
2. 将 selection 明确为 selected_roles/recompute_plan；消费端实际读取合格 buffer 后才记录 read event，失败事件单列。
3. 用独立 observer + sentinel 对消费结果取证，不以 mocked helper 返回值证明读取。
4. 对 select/read 间替换以及 denied/placeholder 负例验证；保持既有 R4 防护，记录实际模块加载版本。

**失败停止与恢复界限**

- 消费者 API 尚无 artifact verified-buffer 时按 D-W05 实现批准的最小接线，不能复用原件 API 错传 ArtifactHandle。
- 任何 IO 触及非隔离路径停止；恢复 consumer 旧版本与不合格状态，禁止把未读角色标已读。

入口：`CMD-W09`、`CMD-W05`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`selection-vs-read-events.json`、`independent-io-trace.json`、`sentinel-consumption.json`、`read-race-cases.json`。

**退出判据**：实际消费的内容和事件可独立核对；只要求该消费者所需角色，不以全部角色齐全代替正确性。
