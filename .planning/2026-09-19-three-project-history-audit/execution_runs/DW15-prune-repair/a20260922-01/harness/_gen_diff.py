import difflib, pathlib, sys
att = pathlib.Path(sys.argv[1])
header = [
    "# DW15-REPAIR changes.diff: iso/baseline (pristine copy of production) -> iso/fixed\n",
    "# Byte-verified: the two 146-file trees differ in exactly these 2 files.\n",
    "\n",
]
out = []
for name in ("prune_retired_evidence.py", "archive_retired_evidence.py"):
    rel = f"company_wiki/source_catalog/{name}"
    before = (att / "iso" / "baseline" / rel).read_text(encoding="utf-8").splitlines(keepends=True)
    after = (att / "iso" / "fixed" / rel).read_text(encoding="utf-8").splitlines(keepends=True)
    out.extend(difflib.unified_diff(
        before, after,
        fromfile=f"iso/baseline/{rel}", tofile=f"iso/fixed/{rel}"))
    out.append("")
target = att / "changes.diff"
target.write_text("".join(header) + "".join(out), encoding="utf-8")
print("changes.diff bytes:", target.stat().st_size)
