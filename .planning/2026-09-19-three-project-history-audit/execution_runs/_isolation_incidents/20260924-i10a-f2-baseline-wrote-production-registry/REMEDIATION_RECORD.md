# D-1 remediation record (owner-authorized truncation)

- authorized_by: OWNER answer 2026-09-24, option (a)「截断回 60 行」
- executed_at_utc: 2026-09-24T21:41:35.194073Z
- PRE : 50229 B / 65 lines / sha256 `18310faea83bad23e68f6713b2c5cce2ad6a3d89f6d8a6b8a02419659335ad55`
- POST: 46369 B / 60 lines / sha256 `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`
- readonly_before=True  readonly_after=False
- pre-image preserved: `.planning/2026-09-19-three-project-history-audit/execution_runs/_isolation_incidents/20260924-i10a-f2-baseline-wrote-production-registry/publications.jsonl.pre_truncation_20260924` (sha `18310faea83bad23e68f6713b2c5cce2ad6a3d89f6d8a6b8a02419659335ad55`)
- verification: 65->60 lines, prefix byte-identical, tail5 (registered_at in 2026-09-24T20:02 window) removed, no incident line survived — all OK
- scope: ONLY this gitignored file touched; `git diff HEAD --name-only` must still show 0 non-.planning paths (re-check below)
