本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-02-B — 跨 CLI 保留阶段错误及已发生副作用

parent：I-02；status：planned；owner：company-wiki 来源系统实施者。

依赖：I-02-A、I-00-B。设计前置：D-W02。证据目录：`execution_runs/I-02-B/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [company-wiki/src/company_wiki/source_catalog/error_taxonomy.py:119](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/error_taxonomy.py:119>) `structured_error`：当前依 exception 类归一，未知 fatal；不能把 provider 结构先变字符串。 SHA256 `14e09c3d41c8584cb59c05ac47ef31c5d4a1e34103c70fb8f4e95e83588c5183`。
- [company-wiki/src/company_wiki/source_catalog/cli.py:1552](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/cli.py:1552>) `main exception handler`：统一出口 structured_error。 SHA256 `2f5c5740343697078d1e69b3a6a9ef9b0809277799c2d9c28a2d3e4048c4d512`。
- [company-wiki/src/company_wiki/source_catalog/acquisition_service.py:76](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/acquisition_service.py:76>) `SourceAcquisitionService.ensure`：失败 journal 为 adapter_or_staging/canonical_import_failed 字符串。 SHA256 `017ca75c1efec6986af058c068db86bbf9fed5edd2bd8ede94fd96a1a8e7f8c7`。
- [revenue-forecast/scripts/filing_fetch_client.py:235](<C:/Users/郑曾波/Projects/revenue-forecast/scripts/filing_fetch_client.py:235>) `resolve_filing`：已尝试保留 code/retryable，避免重复写一套。 SHA256 `9329f331d9f5071ba6c75726c9b381d6a16a1ec16d5d014e09d67a1b434d0173`。
- [revenue-forecast/scripts/source_preparation.py:110](<C:/Users/郑曾波/Projects/revenue-forecast/scripts/source_preparation.py:110>) `prepare_source`：非零子进程 stderr 末 800 字符包装 RuntimeError，main 再变 upstream。 SHA256 `5ec16eaf0fe480126b680f6e069717ebfc218ae39531372a380cfcc9b91bce46`。

**必读原证据**

- [audit_review/2026-09-18_real_company_skill_audit/runs/12_zijin_h1_download_authorized/run.json](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/runs/12_zijin_h1_download_authorized/run.json>)： CN 403 原失败日志：上游可重试与外层 fatal 的差别
- [.planning/2026-09-19-three-project-history-audit/reviews/filing/review.md](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/filing/review.md>)： I-04 错误/预算 owner 边界，避免并发改 FF
- [../company-wiki/src/company_wiki/source_catalog/error_taxonomy.py](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/error_taxonomy.py>)： 现有 N/N-1 及未知码 fail-closed 约束

**只允许修改**

- CW:src/company_wiki/source_catalog/error_taxonomy.py
- CW:src/company_wiki/source_catalog/acquisition_service.py
- CW:src/company_wiki/source_catalog/acquisition_journal.py（新字段仅 schema 批准后）
- CW:src/company_wiki/source_catalog/cli.py（错误出口）
- RF:scripts/source_preparation.py
- RF:scripts/filing_fetch_client.py（仅必要兼容）
- 跨进程隔离测试；FF 实现由 I-04 owner 提交，不在本卡抢写

**固定样本**

- 固定 request_id=execv2-w02b；先重放原 CN 403 原始结构，再使用本地 hermetic upstream CLI 返回固定 UTF-8 长错误（超过 800 字符）及嵌套 cause。
- 分别准备下载前失败、raw 已存后 scan 失败、DB busy、bad request、未知错误；服务 stub 不访问 provider。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W02B-P1 / positive**：各层透传合法 upstream_unavailable/retryable=true/request_id 与原因链。
  预期：code/布尔 retryability/request_id/cause 链语义不变；整份合法 JSON 可读；不把 provider 拒绝归因数据错误。
- **W02B-N1 / negative**：长 JSON/中文/嵌套 causes；结构化 stderr 超 800 字符。
  预期：保留结构字段和完整本地诊断引用；不得截断 JSON 再套字符串。
- **W02B-N2 / negative**：未知 code/畸形 JSON/错误标 retryable='true' 字符串。
  预期：按冻结契约拒绝/未知不可重试；不可信任任意字符串开放 retry。
- **W02B-N3 / negative**：raw 已存且 scan 失败。
  预期：外层仍报告实际一次下载/原件保存及失败阶段，不因未返回 handle 伪报 download_events=0。
- **W02B-N4 / negative**：可重试 DB busy 与不可重试身份/契约错并列。
  预期：DB 重试只由 I-04 deadline 控制；身份错不能 retry 到预算耗尽；本卡不改预算算法。

**按序执行**

1. 与 I-04 owner 先冻结信封字段与串联测试接口；未取得兼容决定就停止跨仓改 schema。
2. 保存原 CN 403 原始 payload 作为回归输入；按同一 argv 链做本地可控重放。
3. 替换丢失结构的包装，统一原因链/阶段/真实 side effects 字段，保留旧客户端可读字段。
4. 各层 stdout/stderr/退出码分别留存，与 request_id 对齐；业务失败即使外层 harness=0 仍判失败。

**失败停止与恢复界限**

- 不为证明 provider 恢复重发 CN 请求；真实可用性留 I-07。
- FF 契约未冻结则阻断接口改动，保留当前失败；恢复隔离消费者版本，不能改原运行日志。

入口：`CMD-W04`、`CMD-W05`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`layer-by-layer-errors.json`、`side-effects-ledger.json`、`raw-cli-logs/`。

**退出判据**：本地真实跨进程保持正确错误和副作用语义；真实 provider 是否恢复不在本卡结论内。
