# G6 —— reviewer 指派记录（**草案，待 owner 确认**）

> **这不是一份生效的 operator 记录。** 它是**草案**：由作者起草、供 owner 一句话确认或直接改写。
> 在 owner 确认之前，本 run 各轮复审的独立性证据**仍然只有**会话自报的 `reviewer_agent_id`（进程级自述，见各 `reviews/*.json` 的 `independence_statement`），**不**构成制度性独立证据。作者**不自行签发** operator 记录（phase A/B 的 G5/G6 都写明了这一条）。

## 1. 这份记录要解决的问题（G6）

四轮 B.DR 与各步 B.VR 的复审身份，仓内只有两类东西：① 复审者**自报**的会话 id；② **作者侧**登记的对应关系。两者都出自被审方一侧，因此**不能**独立证明"复审者不是作者、也不是同一模型/同一运营者"。G6 要补的正是这一环：一份**由 owner/operator 持有或确认**的指派记录。

## 2. 草案正文（请 owner 确认或改写后生效）

```text
指派记录（R4 phase A/B 审计 run）
确认人（owner/operator）：____           确认日期（UTC+8）：____
被审 run：revenue-forecast/assurance/runs/2026-09-11_r4-phase-a、-phase-b

我确认：
1. 下列复审轮次由我（或按我的指派）安排给被审文档/代码的**作者之外**的会话执行；
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

## 3. 确认之后怎么办（作者侧动作，已在等待）

1. owner 回一句「G6 确认」或直接改本文件（把确认人/日期填上、删掉"草案"字样）；
2. 作者把本文件重命名为 `operator-reviewer-assignment.md`，并在 `findings.md` 与 phase A/B 的 `checkpoint.json` 里把 G6 从"待办"改为"已确认（记录在案）"；
3. **不**改动任何既有复审记录的内容。

## 4. 边界（写清楚，避免误读）

- 本记录**只**证明"指派关系"，**不**证明"复审者与被审方模型不同"或"运营者不同"——那需要 owner 侧的运营事实。
- 若 owner 认为不需要这份记录，正确做法是把 G6 **长期登记为未闭**并继续以"自报 + 作者侧登记"披露，而**不是**把自报当成 operator 记录。
