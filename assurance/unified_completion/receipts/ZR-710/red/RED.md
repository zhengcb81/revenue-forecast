# ZR-710 RED 探针证据（2026-08-21）

探针（revenue-forecast, HEAD 8466b37）：
```
revenue_forecast.py:97-102:
  if args.output: args.output.write_text(rendered)      # 非原子
  if args.markdown: args.markdown.write_text(...)       # 非原子
publication_registry._append: open("a") + write + os.fsync（append 有 fsync 但无事务测试）

RED gaps:
  - G1: output/markdown 直接 write_text——进程中断留半文件（无 tmp+rename 原子替换）
  - G2: 故障注入（write/fsync/rename/registry append 每点失败）无孤儿/重复无测试
  - G3: 恢复幂等（同输入重跑 output 一致 + registry 每跑恰 1 条）无测试
```

结论（G1~G3 坐实）：发布写入非原子 + 事务无钉死。

GREEN 对照（实现后）：_atomic_write_text（tmp+fsync+os.replace）+ 故障注入无孤儿 + 幂等测试。
