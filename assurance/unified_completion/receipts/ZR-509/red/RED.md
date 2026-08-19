# ZR-509 RED 探针证据（2026-08-19）

探针（company-wiki, wiki HEAD 8e2bf3f）：
```
grep html_capture src/company_wiki → 0 命中
```
+ announcement_collector.py 仅处理 PDF 公告（URL 策略/下载/receipt，无 HTML 身份门）。
+ golden corpus：wrong strategy HTML（audit sources/2026_strategy.html，hash b2d215df…）注册为空实体负例（供 ZR-509/502 错归测试）。

结论（G1~G3 坐实）：
- **G1 无 HTML 身份门**：官方 HTML 捕获无 title/entity/period 校验机制。
- **G2 空实体网页不 fail-closed**：wrong strategy HTML（无公司名）无检测，若被捕获将作为无身份文档入库。
- **G3 无共享保存/索引契约**：HTML 捕获的身份判定无结构化输出。

GREEN 对照（实现后）：parse_html_identity 提取 title/entities/period；validate_html_capture 身份门（ok/missing_title/no_entity/entity_mismatch/invalid_period）；wrong strategy 形状 → no_entity fail-closed；输出 JSON 可序列化 + 确定性。
