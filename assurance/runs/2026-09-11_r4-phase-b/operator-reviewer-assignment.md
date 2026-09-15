# G6 —— reviewer 指派记录（**已由 owner 确认生效**，2026-09-15）

> **生效依据（可复核的出处，不是作者自签）**：owner 于 2026-09-15 在本会话中，针对作者提出的两个问题「① G6 草案要不要生效 ② 两个工作包要不要开工」回复「**都要**」。据此本记录生效。
> **作者不代签**：确认人是 owner；作者只把草案改名（`-DRAFT.md` → 本文件）并填入**确认依据与日期**，不代替 owner 作身份声明。措辞若需修改，owner 直接改本文件即可；撤回确认时改回 `-DRAFT` 并在 `findings.md` 里把 G6 改回**未闭**。

## 1. 这份记录要解决的问题（G6）

四轮 B.DR 与各步 B.VR 的复审身份，仓内只有两类东西：① 复审者**自报**的会话 id；② **作者侧**登记的对应关系。两者都出自被审方一侧，因此**不能**独立证明"复审者不是作者、也不是同一模型/同一运营者"。G6 要补的正是这一环：一份**由 owner/operator 确认**的指派记录。

## 2. 记录正文（生效版）

```text
指派记录（R4 phase A/B 审计 run）
确认人（owner/operator）：owner（GitHub zhengcb81；本机账号 郑曾波）
确认方式与日期：2026-09-15 会话内确认（对「① G6 草案要不要生效 ② 两个工作包要不要开工」
                回复「都要」⇒ 本记录生效 + 两个工作包开工）
记录人：作者会话；本文件的生效依据 = 上一行引用，可在会话记录与 git 历史中复核
被审 run：revenue-forecast/assurance/runs/2026-09-11_r4-phase-a、-phase-b

确认内容：
1. 下列复审轮次由 owner（或按 owner 指派）安排给被审文档/代码的**作者之外**的会话执行；
2. 复审者的身份以仓库内 reviews/<gate>-*.json 的 reviewer_agent_id 为准，这些 id
   由复审会话自己读取并写入，作者不得代填；
3. 复审会话的工作范围限于只读检查 + 各记录中 independence_statement 声明的命令类；
4. 本记录不追溯改变任何已出具复审的内容与结论，只补齐"指派"这一环。

轮次清单（按仓内记录）：
  B.DR rev1..rev6（设计复审，含 rejected 轮）  → reviews/B.DR*.json
  B.VR 各步（B01/B02/B03/B04/B05/B06/B07）      → reviews/B.VR-*.json
  B.VR-fc1307a / B.VR-zr903（2026-09-13 追加）  → reviews/B.VR-fc1307a.json、
                                                 reviews/B.VR-zr903.json
  G5-boundary-observation（2026-09-15 只读观测）→ reviews/G5-boundary-observation.json
  A07 / A08（阶段 A 的复审）                    → runs/2026-09-11_r4-phase-a/reviews/
```

## 3. 作者侧已完成的动作

1. 文件改名生效：`operator-reviewer-assignment.md`（原 `-DRAFT.md`），并填入确认依据与日期。
2. `findings.md` 的 G6 条目改为"**已由 owner 确认（记录在案）**"；checkpoint 在下次重建时带上。
3. **未**改动任何既有复审记录的内容。

## 4. 边界（写清楚，避免误读）

- 本记录**只**证明"指派关系"，**不**证明"复审者与被审方模型不同"或"运营者不同"——那需要 owner 侧的运营事实。
- 更强的证据形态是 owner 侧的原件（工作单/邮件/工单）；本文件**不是**原件，只是 owner 确认过的方向性记录。
- 若 owner 撤回确认：把本文件改回 `-DRAFT`，并在 `findings.md` 里把 G6 改回**未闭**——**不允许**保留"已确认"字样。
