# ZR-806 工作单元卡（preflight）— G 收官：真实 T2 三 root/broker/artifact/mine/forecast 样本

- 领取时间：2026-08-22T20:50Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-806`（9784c18 close ZR-804+ZR-805 → ZR-806；本次恢复时发现 9784c18 声称镜像但 README 未落盘，已修复游标并重建 manifest）；锁 ZR-806（owner=zr806-implementer，nonce 71888c18…）。
- 依赖：ZR-510（chunk attribution）、ZR-609（紫金 pilot）、ZR-709（紫金五年旅程）——全部 accepted ✅。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 G 收官卡——把**真实 T2 样本**（三 root：companies/dayu/Dropbox；broker：券商研报 PDF；artifact：raw + source.json；mine：紫金矿业；forecast：五年预测消费）组织成"样本唯一/新鲜 + 用户旅程全绿 + 生产零写"的综合验证套件。AUD2-05 语义（样本缺失 → blocked，不自动换易样本）无测试钉死。现状缺口（RED G1~G3）：revenue 侧无真实 T2 样本套件；dropbox/dayu 引用均为 T1 合成 fixture（FC-505 tmp_path）；无样本唯一性/新鲜度断言。
2. **production entrypoint 是什么？** company-wiki `SourceResolver` 只读旅程（真实 catalog.sqlite3 + 三 root 生产路径，ZR-409 模式）+ raw 文件 `.source.json` 元数据消费（artifact 层）+ revenue F2 契约（mine/forecast 样本消费绑定）。
3. **RED？** grep `real_t2`/`unique sample`/`AUD2-05` → 零命中；dropbox/dayu 引用均为 T1 合成（FC-505）；无三 root 综合样本唯一/新鲜 + 旅程 + 零写指纹套件。现状实证（本卡探针）：紫金 FY2025/FY2024 → REUSED_EXACT；dayu 1548 HK FY2021 → REUSED_EXACT；Dropbox 688031/研报 → MISSING（fail-closed 诚实）。
4. **允许改哪些文件？** revenue：新 `tests/test_zr806_real_t2_samples.py`；receipts/ZR-806/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog/source root 写、下载、LLM。（预期 test-only，与 ZR-409/802 同型）
5. **下一单元解锁？** 阶段 H（ZR-901/CA-201 起）及 unlocked 的 ZR-903/ZR-906 等。本卡不做：动态调度（ZR-902/903）、最终 ratchet（ZR-906）、stage H CI 契约（ZR-901）。

## Acceptance criteria

- **C1 样本唯一/新鲜（杀 G2，AUD2-05）**：固定样本清单（companies 紫金 FY2025 cninfo:1225023658 + FY2024 cninfo:1222870413；dayu 1548 HK FY2021 hkexnews:10225111；Dropbox 688031 CN FY2024 cninfo:1223325316 + 至少 1 份券商研报 PDF）——每个样本 `content_sha256` 唯一（跨 root 集合去重）；`filing_date` ≤ 今天（新鲜）；任一样本缺失 → 测试 fail（blocked，不自动换样本）。
- **C2 三 root resolve 只读旅程（杀 G1）**：companies 紫金 FY2025/FY2024 → `REUSED_EXACT`（download=0）；dayu 1548 FY2021 → `REUSED_EXACT`（dayu-only，companies 无同 hash）；Dropbox 688031 → `MISSING` fail-closed（http URL 不伪造 handle）——旅程前后三 root 浅指纹一致 + catalog.sqlite3 关键表行数不变（零写）。
- **C3 artifact/mine/forecast 样本消费（杀 G3）**：紫金 FY2025 年报 `.source.json` 字段契约（fiscal_year=2025、entity=紫金矿业、security_id=601899、provider_document_id、content_sha256 与 PDF 文件实测一致、byte_size）；source 元数据 → revenue F2 消费链绑定（fiscal_year 对应 FY 语义、entity 名称可绑定 forecast company_name——不新增产品逻辑，仅钉死真实样本与契约的一致性）。
- **C4 质量门**：全量回归零回退（基线 803 passed + 106 subtests）、ruff clean、ratchet 绿（新文件 ≤10/函数）、skill-sync MATCH、独立 reviewer 复放。

## 边界

- T2 真实根只读：resolve 只读路径 + 浅指纹（ZR-409 模式：不断言 catalog-DIR 零写——后台 worker 并发写 catalog）；零网络、零下载、零 LLM；样本固定不轮换（确定性），样本失效 = blocked。
- 测试对真实路径硬编码（ZR-409 同型）：`C:\Users\郑曾波\Projects\company-wiki`、`C:\Users\郑曾波\Projects\dayu-agent\workspace\portfolio`、`%USERPROFILE%\Dropbox\Stock`——reviewer 同机复放。
