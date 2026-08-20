# ZR-704 工作单元卡（preflight）— F1：validate-only 纯只读门（REV-05，success/failure 零残留）

- 领取时间：2026-08-21T00:00Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-704`，ZR-503 accepted + closure→ZR-704（phase=F_revenue_mining）；锁 ZR-704（owner=zr704-implementer）。
- 依赖：ZR-501（✅ validate-only draft mode）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F1 第四卡：**validate-only 纯只读门（REV-05）**。REV-05 要求 success/failure 都无 sign/registry/network/subprocess/write；文件树和 registry hash 不变。ZR-501 已实现 validate-only 零写（draft mode 不注册），但 REV-05 更严格：failure 路径也零残留 + registry hash content-addressed chain 不变。
2. **production entrypoint 是什么？** `revenue_forecast.py --validate-only`（CLI，draft mode）+ publication_registry registry hash。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 failure 路径零残留无测试**：输入非法（ForecastInputError）时 validate-only 退出是否留下临时文件或 registry 变更未验证。
   - **G2 registry hash 不变无测试**：validate-only 前后 publication_registry 的 content-addressed chain 二进制一致无钉死。
   - **G3 恶意输入路径无测试**：malformed JSON 输入 validate-only 的零残留未验证。
4. **允许改哪些文件？** revenue：新测试 `tests/test_zr704_validate_only_gate.py`（REV-05 门测试）；可能少量产品代码（如 failure 路径清理）；revenue receipts/ZR-704/**。禁止：改 validator 语义、改 publication_registry 契约、真实 catalog 写、下载、LLM。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-705（REV-06~08 draft/formal 分离互换）。本卡不做：draft/formal 互换攻击测试（ZR-705）、publication 事务（ZR-710）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-503 accepted（closure.next→ZR-704 via F_revenue_mining）。
- [x] triplet 冻结：revenue（ZR-503 closure 提交后）、wiki `26a6b22…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：validate-only draft mode 不注册（ZR-501 实现）；failure 路径零残留无测试；registry hash 不变无钉死。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（REV-05 门测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 success path 零残留（REV-05 成功）**：validate-only 合法输入后（a）tmp 目录空（无输出/markdown 文件）、（b）registry file 不存在或为空、（c）registry hash chain 前后二进制一致。
  - **C2 failure path 零残留（REV-05 失败）**：validate-only 非法输入（ForecastInputError）后（a）tmp 目录空、（b）registry file 不存在或为空、（c）registry hash chain 前后一致；exit code == 2。
  - **C3 malformed JSON 零残留（REV-05 边界）**：validate-only 畸形 JSON 输入后同 C2 零残留。
  - **C4 恶意 registry 干扰（REV-05 防御）**：validate-only 在 registry 已存在旧条目时仍不修改 registry（hash 不变）。
  - 质量门：revenue tests/ 全量无回归；ruff clean；ratchet 绿。
- **Stop conditions / handoff**：改 validator 语义、改 publication_registry 契约、真实 catalog 写、下载、LLM → 立即停止。

## Annex：REV-05 判定矩阵

| 场景 | 期望 |
|---|---|
| validate-only 合法输入 | exit 0；无文件；registry hash 不变 |
| validate-only 非法输入 | exit 2；无文件；registry hash 不变 |
| validate-only 畸形 JSON | exit 2；无文件；registry hash 不变 |
| validate-only + registry 已有旧条目 | exit 0/2；registry hash chain 不变 |
