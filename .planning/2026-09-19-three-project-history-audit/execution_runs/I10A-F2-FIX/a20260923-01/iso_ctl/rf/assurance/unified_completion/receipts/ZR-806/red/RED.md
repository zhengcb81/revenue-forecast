# RED.md — ZR-806 真实 T2 三 root/broker/artifact/mine/forecast 样本（阶段 G 收官）

## 探针（全部在 revenue 仓当前 triplet 实跑）

- **G1 无真实 T2 三 root 综合样本套件**：`grep real_t2|t2_sample|unique sample|样本唯一` tests/ → 零命中；dropbox/dayu 引用均为 T1 合成 fixture（test_dropbox_full_chain_fc505.py 用 tmp_path 合成 PDF；test_company_wiki_source.py 为合成 collector 名称）；无一条测试把 companies/dayu/Dropbox 三 root 真实路径组织进单一旅程。
- **G2 样本唯一/新鲜零断言（AUD2-05 未钉死）**：`grep AUD2-05` 全仓 → 零命中；无 content_sha256 跨 root 唯一性断言、无 filing_date ≤ today 新鲜度断言、无"样本缺失 → blocked（不自动换样本）"测试。
- **G3 真实 artifact/mine/forecast 样本消费无绑定测试**：revenue tests 无任何测试读取 companies/紫金矿业 raw `.source.json` 并断言字段契约（fiscal_year/entity/content_sha256 与文件一致）；无真实样本 → F2 消费链绑定。

## 现状实证（resolve 只读探针，本卡领取前）

| 样本 | 结果 |
|---|---|
| companies 紫金 FY2025（cninfo:1225023658） | REUSED_EXACT（download=0） |
| companies 紫金 FY2024（cninfo:1222870413） | REUSED_EXACT |
| dayu 1548 HK FY2021（hkexnews:10225111） | REUSED_EXACT（dayu-only，companies 无同 hash） |
| Dropbox 688031 CN FY2024（cninfo:1223325316） | MISSING（http URL → capture_incomplete，fail-closed 诚实） |
| Dropbox 券商研报（无强身份） | MISSING（不伪造 handle） |

## 结论

G1~G3 全部为真实缺口（`still_missing`）；实施 = 新测试套件钉死样本唯一/新鲜 + 三 root 只读旅程 + artifact/mine/forecast 消费 + 零写指纹，零产品改动。
