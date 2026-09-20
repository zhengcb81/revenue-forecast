# recovery/ — I-05-A / a20260919-01

**NA 声明（review_and_handoff.md 允许 NA，但必须写明理由）。**

本卡是**纯读路径**的资格门修复，没有需要"异常后重启/重试后验证最终持久化"的状态迁移：

1. **没有持久状态迁移**：改动只影响 `SectionQueryService.list_sections` 的判定与
   `extract_sections_catalog` 的重算准入过滤。没有 schema、没有 migration、没有新表、
   没有在途事务、没有 lease/journal 行。
2. **崩溃恢复面**：查询路径是只读连接（`mode=ro`），进程被杀不留下需要恢复的状态；
   下一次调用从头重新判定。
3. **唯一的状态副作用**在 producer 侧，且是既有的 upsert（`ON CONFLICT(document_id,
   artifact_role, generator_name, generator_version) DO UPDATE`）：崩溃后重跑该 producer
   会重新写出同一行的路径/哈希/状态，不产生半成品；本卡**未改**这段 upsert。
4. **异常路径已被真实反例覆盖**（不是"未测"）：
   - 索引/切片文件缺失、内容被改、路径越界、span 失联：`after/review-attack-probes.json`
     的 m1/m2/m3 与 `after/artifact-mutation-matrix.json` 的 c1..c8
     （每 case 独立 catalog，拒绝后再次查询仍为同一拒绝，无状态残留）；
   - store/DB 层的异常不适用（只读连接不写）。
5. **本 attempt 的隔离回滚规则**见 `decision.md` §6：删除 `iso/fixed/` 即回到生产字节；
   attempt 内曾两次这样切换以生成 `before` 证据（`commands.json` C2/C5 顺序说明），
   每次都重算了文件哈希，未出现"半切换"状态。

因此 `recovery/` 无需额外的崩溃-重启证据；若 reviewer 认为需要，请指出具体要复现的
持久化边界，我会按 START_HERE 的隔离要求补做（不得在生产上重演）。
