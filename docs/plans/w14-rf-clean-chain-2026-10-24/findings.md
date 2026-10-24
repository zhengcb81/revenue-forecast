# W14-RF-CLEAN-CHAIN 调查记录

源码基线 `599d17b89d8baee42ce203747496731ace2d0148`。实际问题、需求ID、写范围和输入接口以中央卡为准。bootstrap只新建独立工区/PWF，未实施产品、未运行测试、未调用模型或下载。

## A节点调查结论（2026-10-24，全部实测）

1. **旧pin全漂移**：runner CODE_PINS 四个 RF 文件 SHA（source_preparation/filing_fetch_client/company_wiki_source/isolated_lake）与当前 LF 源码全部不匹配；RED 基线 `tests/test_cross_repo_chain_e2e.py` 2 failed（runner 直接 exit 2 "binding drift"），非 skip。
2. **生产材料依赖**：旧 offline 链依赖本机 `company-wiki/companies/宁德时代/...pdf + .source.json + .source_catalog/security_master/cn.json`，异地不可复现。
3. **过时期望**：CWP 冻结版 a31300a7 的 `source_reader.py::_current_review` 把 prompt-injection review 当纯诊断（"never a read prerequisite"）；旧 S2 期望 exit-3 审查拒绝已不成立。当前合同下合成湖+合法 receipt 全链 exit 0 成功（`tests/test_preparation_e2e_success.py` 实测通过，5.8s）。
4. **联网与删除风险**：旧默认 `--live auto` 联网探测；`main()` 对已有 work-root 先 `rmtree_retry` 递归删除。
5. **editable 安装干扰（E02 反控对象）**：本机 `company_wiki` 为 pip editable 安装指向正在变化的 `Projects/company-wiki`；新链用显式 PYTHONPATH（scratch 冻结部署优先）压过它，import 探针+子进程 provenance 实证 26/26 子进程从 `deploy/cwp/src` 导入。
6. **错误路径真实形状**（冻结 FF/CWP 实测）：wrong period → FF `not_found/no_local_match`，RF 包装 exit 3 upstream；empty company_query → FF exit 2 `request_error` "company_query must be non-empty trimmed text"；未知公司 → `identity_error/missing`；共享别名 → `identity_error/ambiguous`（envelope 带 candidates）。S5 bogus pdoc → `not_found`。
7. **产品失败→非零**：以历史 RF `3b00b9384`（仍含审查门/旧记录形状）跑 S2 → S2 fail、exit 1、S4 清理仍 PASS；作为行为测试钉住"commit 是 provenance 而非固定 hash 许可"。
8. **单测抓到两个实现缺陷**（先写测试的价值）：同秒同进程两次 AttemptSpace 碰撞（加单调序号修复）；restore_report 的 removed 语义澄清（快照后创建又删除=无残留）。
9. **夹具**：pymupdf 生成 1027B 真 PDF（pypdf/pymupdf 双解析验证、可提取文本）+ 797B UTF-8 中文 TXT + manifest（单一事实源），合计 3.8KB ≤ 1MiB；合成身份"示例智造W14/990014"，明确非真实公司分析。
10. **TXT 消费语义**：TXT 作为同发行人的 companion 文档（quarterly_report/Q3），经同一公共 FF resolve→RF source_preparation→CWP source_reader 链实际读取（source_ref sha + manifest fiscal_period=Q3 绑定字节），非仅登记。
