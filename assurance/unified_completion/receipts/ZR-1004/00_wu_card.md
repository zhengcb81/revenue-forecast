# ZR-1004 工作单元卡（preflight）— I：companies→dayu→Dropbox→future root 小 cohort

- 领取时间：2026-08-23T04:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1004`（ZR-1003 closure → ZR-1004）；锁 ZR-1004（owner=zr1004-implementer，nonce 532b90c1…）。
- 依赖：ZR-1003（shadow assertions，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 I 第四卡——小 cohort（registry："companies→dayu→Dropbox→future root 小 cohort；每 root T2/UJ；external write=0；同 request rollback 恢复"）。现状缺口（RED）：ZR-806 有三 root 样本旅程（无 future_lake）；无"每 root 单独 T2/UJ 分组 + external write=0 + 同 request rollback 恢复"综合验收。
2. **production entrypoint 是什么？** company-wiki `SourceResolver`（真实 catalog 只读，ZR-806/409 模式）+ 四 root 生产路径（companies/dayu/Dropbox/future_lake）。
3. **RED？** grep zr1004 → 零命中；ZR-806 覆盖三 root（无 future_lake）、无 per-root 分组断言、无同 request rollback 恢复语义。
4. **允许改哪些文件？** revenue：新 `tests/test_zr1004_small_cohort.py`；receipts/ZR-1004/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog/root 写、下载、LLM。
5. **下一单元解锁？** ZR-1005（legacy artifact 分桶）。本卡不做：真实 cohort 切换（部署）、broker cohort（ZR-1006）。

## Acceptance criteria

- **C1 四 root cohort 旅程**：companies（紫金 FY2025/FY2024 exact）、dayu（1548 exact）、dropbox（688031 fail-closed MISSING 诚实）、future_lake（ZR-409 fixture 根）——每 root 独立 T2/UJ 断言。
- **C2 external write=0**：旅程前后四 root 浅指纹 + catalog 行数不变（ZR-806 模式）。
- **C3 同 request rollback 恢复**：同一 resolve request 失败后重试恢复（dropbox MISSING 后同一 request 再次 resolve → 仍 MISSING 结构化一致——诚实幂等）；companies exact 重复 request → 同 source 身份（幂等复用）。
- **C4 质量门**：全量回归零回退（基线 889 passed + 106 subtests）、ruff clean、ratchet 绿、skill-sync MATCH、独立 reviewer 复放。产品代码零改动。

## 边界

- T2 真实根只读（ZR-409/806 模式：resolve 只读 + 浅指纹）；零网络、零下载、零 LLM；future_lake 为仓库内 fixture 根（ZR-409）。
