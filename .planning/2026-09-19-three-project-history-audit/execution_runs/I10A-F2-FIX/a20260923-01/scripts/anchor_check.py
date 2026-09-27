import hashlib, json, subprocess, sys, time
from pathlib import Path
att = Path(sys.argv[1]); root = att.parents[4]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
frozen = {
 "scripts/forecast/calc.py": "bc4f33d92738029ae1e146e6323a23e818c3abeb7cdf173c9bcfa4c462b02f79",
 "scripts/forecast/segments.py": "95555509bc8a30affe1bcde3bb658ee4e3211d3b91f0ac6b1038dfc6d79765dd",
 "scripts/model_registry.py": "62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081",
 "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
}
rows = []
for rel, want in frozen.items():
    rf = root / rel; iso = att / "iso" / "rf" / rel
    rows.append({"file": rel, "frozen_sha256": want,
                 "production_sha256": sha(rf), "production_bytes": rf.stat().st_size,
                 "production_matches_frozen": sha(rf) == want,
                 "iso_sha256": sha(iso), "iso_bytes": iso.stat().st_size,
                 "iso_matches_frozen": sha(iso) == want})
git = subprocess.run(["git", "diff", "HEAD", "--name-only"], cwd=root,
                     capture_output=True, text=True, encoding="utf-8")
paths = [p.strip('"').replace("\\\\", "\\") for p in git.stdout.splitlines()]
non_planning = [p for p in paths if not p.startswith(".planning/")]
untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root,
                           capture_output=True, text=True, encoding="utf-8")
u = [p.strip('"') for p in untracked.stdout.splitlines()]
out = {
 "artifact": "anchor_check",
 "checked_at_local": time.strftime("%Y-%m-%dT%H:%M:%S"),
 "anchors": rows,
 "git_diff_HEAD_name_only_total": len(paths),
 "git_diff_HEAD_name_only_non_planning": non_planning,
 "git_diff_HEAD_non_planning_count": len(non_planning),
 "git_untracked_non_planning": sorted({p.split("/")[0] for p in u if not p.startswith(".planning/")}),
 "registry_layer_byte_identical": rows[2]["iso_matches_frozen"] and rows[3]["iso_matches_frozen"] and
     rows[2]["iso_sha256"] == rows[2]["production_sha256"] and rows[3]["iso_sha256"] == rows[3]["production_sha256"],
}
(att / "evidence" / "anchor_check.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps({k: out[k] for k in ("git_diff_HEAD_non_planning_count", "registry_layer_byte_identical", "git_untracked_non_planning")}, ensure_ascii=False))
print(json.dumps([(r["file"], r["production_matches_frozen"], r["iso_matches_frozen"]) for r in rows]))
