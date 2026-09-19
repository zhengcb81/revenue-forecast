# I-00-A 冻结预期 (2026-09-19)
1. 三仓HEAD/分支/dirty可从git_*.txt复算；filing-fetch clean、company-wiki dirty=[.coverage, coverage.json]（用户原有，不得清理）。
2. 8个配置/控制文件sha256记录于baseline.json，任何后续卡开始时重算必须一致；不一致=漂移，先暂停受影响步骤。
3. SQLite：prod db 49,677,344,768字节、header 'SQLite format 3'、WAL=0；backup API probe integrity=ok。全量快照不在本卡执行（磁盘61G<2x47G需要）。
4. 隔离：iso venv python -I加载模块无editable finder；cwd与声明写目录=attempt目录；sys.path无三仓/dayu-agent路径；fallback_free=true。全局Miniconda python被否决（含__editable___dayu_agent钩子）。
5. worker desired_state=paused；本卡不启动任何scan/fetch/worker；PID15596已死但状态文件未清理，仅记录不清除。
