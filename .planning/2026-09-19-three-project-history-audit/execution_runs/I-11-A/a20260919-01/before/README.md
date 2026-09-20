# before/ ：本卡的"修改前"证据说明

I-11-A 是**设计/契约卡**：不修改任何产品代码、不修改配置、不写生产数据。
因此本目录没有"修改前的失败复现日志"（`review_and_handoff.md` 允许对纯函数/设计卡说明 NA），
"修改前"状态以**只读基线捕获**的形式保存，而不是以运行日志的形式保存：

| 本目录本应有 | 实际去向 | 原因 |
|---|---|---|
| 修改前的被测行为日志 | 不需要 | 本卡不改变任何被测行为；没有"改前失败/改后通过"的对象 |
| 修改前的输入 hash | `../evidence/I-11-A/state_before.json`、`../evidence/I-11-A/source_probe.json` | 三仓 HEAD / porcelain / 关键文件 sha256 / 三份原始披露的字节 hash 都在那里 |
| 修改前的生产状态 | `../evidence/I-11-A/state_before.json` | 与 `state_after.json` 完全一致，证明生产零改动 |

本卡的"运行前检查"是：在**未做任何写入**的前提下，用两条独立取文路径读取原始披露，
并用有理数复算基期恒等式（`../evidence/I-11-A/extract/arithmetic_oracle.json`，A1–A7）。
若这些恒等式在基期就不成立，本卡会停在 oracle S1/S2 而不是继续写命题。
