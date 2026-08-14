# ZR-102 工作单元卡（preflight）— hermetic 三进程 T1 runner

- 领取时间：2026-08-14T06:20Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-102`；units.ZR-101.status=accepted + closure.next=ZR-102。
- 依赖：ZR-002、ZR-003（均 accepted ✅）。Registry 依赖列=ZR-002,ZR-003。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** T1 阶梯（runbook §5）：临时三 roots + 真实三进程（revenue→filing→wiki）+ provider/LLM 边界 spy。旧 FC-1002 用源码字符串断言 spawn 链，未提供真实三进程+spy+临时 roots 的机器证据。本卡建新 runner，不做第二套断言。
2. **production entrypoint 是什么？** revenue `scripts/source_preparation.py`（真实 subprocess）；filing `scripts/fetch_filing.py`（真实 subprocess）；wiki CLI `python -m company_wiki… resolve/close-gap`（真实 subprocess，`--config` 指向临时配置）。
3. **哪个 current-triplet 行为是 RED？** 不存在满足三条（三真实 subprocess、临时三 roots、provider/LLM 边界 spy）的 runner；旧 FC-1002 测试即 RED（字符串级 spawn 断言）。
4. **允许改哪些文件？** revenue `assurance/unified_completion/t1/**`（runner+fixtures+spy）、`assurance/unified_completion/tests/test_zr102_*.py`、receipts/ZR-102/**、state.json。禁止：三仓产品代码/配置/CI、真实 sibling/root 的任何写入、真实 provider/LLM/网络。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-103~105（依赖 ZR-102）。本卡不修 chain 行为（发现的链上缺陷登记 findings + successor，例如 ZR-204/205/405）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-101 accepted（机器状态 2026-08-14T06:1xZ；closure.next=ZR-102）。
- [x] triplet 冻结：revenue `fdc34866269444004972ef6f2aaa344fd94b3dc3`（ZR-101 closure，领取时重读）；filing `83c638e…`；wiki `b661755…`。
- [x] 配置注入可行性（预研）：revenue config 支持 `${USER_PROFILE}/${COMPANY_WIKI_ROOT}` token 展开（config/company_wiki.json 含 adapter command 数组）→ 可生成临时 config 指向临时 roots + spy adapter；wiki CLI 有 `--config`；filing config/company_wiki.json 含 company_wiki_root。
- [x] 边界 spy 定义：provider=临时 spy 可执行（记录调用参数/次数，返回伪造成功 JSON）；LLM=`COMPANY_WIKI_REAL_LLM=0` + 从 receipt/信封计 llm_calls（无真实 LLM）。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（assurance）。
- **Current-state drift verdict**：`still_missing`——无 T1 runner。
- **Acceptance criteria**：runner 在纯临时目录跑通 exact-reuse 场景（companies 根命中→filing 校验→revenue 消费；download=0/parser=0/llm=0）；授权下载场景 provider spy 恰好被调 1 次、二次运行 0 次；缺失+未授权场景 provider spy 0 次；三进程 PID 边界由 runner 记录且互异；runner 硬拒绝任何真实 sibling/root 路径；负例（缺 hash/错实体）fail closed。
- **Stop conditions / handoff**：真实 roots 被触达、真实 provider/LLM/网络调用 → 立即停止。
