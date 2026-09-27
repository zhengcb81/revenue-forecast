# CA-306 工作单元卡（preflight）— J：旧计划 terminal closure 与唯一入口切换（终局卡）

- 领取时间：2026-08-31T18:55Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-306`（CA-305 closure → CA-306）；锁 CA-306（owner=ca306-implementer，nonce 7283370f…）。
- 依赖：CA-305（六问题 ledger，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 J 终局卡——旧计划 terminal closure 与唯一入口切换（registry："旧计划单一 owner 添加只读 terminal notice：closed_superseded_incomplete，指向新 closure ledger；保留所有历史 receipt/hash；关闭 R9/FC150x 旧领取入口；71 FC、R0~R9、FC150x 全部有最终 successor 结果；旧历史不改写；根 audit_review/README.md 始终是唯一可领取入口"）。现状缺口（RED）：6 个旧计划目录均未关闭。
2. **production entrypoint 是什么？** `legacy_disposition`（71 FC/10 waves/5 closure items successor 完整性）；`state.json`（全部 mandatory accepted）；`audit_review/README.md`（唯一控制面 + current_next/phase 镜像）；6 个旧计划目录（只读历史，snapshot 稳定）。
3. **RED？** glob tests/**/*ca306* → 零命中；无 terminal closure 组合验收；旧目录无 TERMINAL_NOTICE。
4. **允许改哪些文件？** revenue：新 `tests/test_ca306_terminal_closure.py`；receipts/CA-306/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、旧计划目录写入（notice 为部署/owner 动作）、registry 写、下载、LLM。
5. **下一单元解锁？** 无（终局卡）——CA-306 closure 后全部 117 卡闭环。本卡不做：实际写旧目录 TERMINAL_NOTICE（旧计划 owner 部署动作）。

## Acceptance criteria

- **C1 notice 契约**：closed_superseded_incomplete + ledger 指针 + owner/when；notice 是加法不改写。
- **C2 历史不可变**：6 个旧计划目录存在且 snapshot 稳定（文件集 + hash 不变；不移动/删除/重写）。
- **C3 disposition 完整**：71 FC + 10 waves + 5 closure items 全有 successors；ld.verify fresh。
- **C4 领取项关闭**：FC-150x → CA successors 全 accepted（R9 via CA-304 accepted；CA-306 自身验收中）；全部 mandatory units accepted。
- **C5 唯一入口**：根 README 唯一控制面（current_next/current_phase 镜像）；无其他目录声明入口。
- **C6 质量门（卡级）**：相邻回归（CA-305）零回退、revenue 全量零回归（基线 1019+106）、ruff clean、独立 reviewer 复放。产品代码零改动、旧目录零触碰。

## 边界

- 只读校验 + tmp；零网络/下载/LLM；TERMINAL_NOTICE 实际写入为旧计划 owner 部署动作（本卡验收契约）。
