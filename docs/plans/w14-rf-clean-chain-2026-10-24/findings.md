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

## C节点独立审查发现与修复（2026-10-24）

三并行 agent：运行时重放核验=APPROVE；静态审查=REQUEST_CHANGES（F1-F18）；反掩盖审查=REQUEST_CHANGES（8项）。合并去重后全部内部发现已修复：

**MAJOR**
- 静态F1 收据 fixture SHA 手写打错（e75502≠e75902）→ 由脚本按 manifest 派生重生成，并新增 `test_delivery_receipt_fixture_shas_match_manifest` 永久校验。
- 静态F2 `production_writes` 硬编码 0 → 改为实测：三仓 HEAD+`git status --porcelain` 运行前后快照（deploy.repo_activity），summary 记 before/after/changed；测试改断言 measured。
- 静态F3 清理前后 hash 未落盘 → cleanup() 报告携带 initial/remaining 全量 sha inventories + added/removed/changed diff；S4 另落 `s4/restore.json` 夹具前后哈希。
- 静态F4 交接文件缺失 → handoff.json/review.md/json 在最终提交补齐（本项为交付待办）。
- 反掩盖F1 provider spy 无正控+docstring 谎称 read 计数 → sitecustomize 加 install.jsonl（每子进程安装标记+接线状态），S4/_finish 固化到 evidence；新增 `test_provider_counter_spy_fires_on_real_loopback_request`（真实 loopback HTTP 触发 provider 事件）；docstring 改为只声明 provider。
- 反掩盖F2 work/evidence 目录重叠可删收据 → main() 重叠即 exit 2（先于分配），新增 overlap 用法错误测试。

**MINOR**
- 静态F5/F6 deploy git FileNotFoundError/TimeoutExpired→DeployError；export_tree 用 GIT_* 净化 env。
- 静态F7/反掩盖F3 RF/FF/CWP 执行根断言 → test_e01 断言全部 .py 子进程 argv0 在部署根内 + source_preparation/fetch_filing/source_reader_cli/source_catalog 孙进程存在。
- 静态F8 源仓零写入只比 HEAD → 并入 F2 的 porcelain 实测。
- 静态F9/反掩盖F7 断网仅 connect 级 → 补 getaddrinfo/sendto 拦截+记录；边界（子进程外挂程序可绕过）写入 handoff 已知边界。
- 静态F10 COMPANY_WIKI_BUDGET_CONFIG 等路径重定向变量 → chain_env 显式移除并在 child_env 记录（removed_path_redirect_names）。
- 静态F11 同 F2 重叠校验。
- 静态F12 早退路径不清理 → _finish 统一：S4 未跑则清 attempt 并落 early_cleanup.json。
- 静态F13/反掩盖F6 探针测试空断言 → 改名为 healthy_probe 测试，只接受 rc==0+frozen 绑定；失败分支由 missing-commit 测试覆盖。
- 静态F14 死代码 → 删 file_hash_evidence/read_json/cwp_config/scrub_credentials；restore_report 并入 cleanup 报告（inventory+diff 字段）。
- 静态F15 handoff 对账 → reviewed_code_commit/attempt计数在最终交接修正。
- 静态F16 离线场景 skip 仍 exit 0 → compute_exit_code：非S1场景必须 pass 否则 exit 1；新增映射单测。
- 静态F17 收据无 runner/support SHA → summary.runner_code_sha256（runner+5模块）。
- 静态F18/反掩盖杂项 → 收据记 runner_cwd、lake_build 记 scan PID、key 扫描扩到 .txt、S3 加 catalog 内容级 sha 比对（catalog_content_sha）、allocate 冲突按用法错误处理、语义投影注释澄清、历史失败测试钉住预期失败名集合。

**保留为已知边界（不改代码）**：run_cmd 超时不杀进程树（Windows 孙进程可能残留）；语义投影当前按布尔 check 比较；三测试文件重复小工具函数；两回放 policy_hash 路径派生不同（投影外预期）。
