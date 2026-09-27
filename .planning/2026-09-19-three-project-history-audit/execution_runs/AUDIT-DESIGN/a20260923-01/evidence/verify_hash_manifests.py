"""AUDIT-DESIGN read-only verifier: recompute sha256 of every (path, sha256) pair
declared inside an attempt's own hash manifests, and report match/mismatch/missing.
Writes NOTHING outside its own output file (printed to stdout).
Usage: python -X utf8 -B verify_hash_manifests.py <attempt_dir> [more attempt dirs...]
"""
import hashlib
import json
import sys
from pathlib import Path

SHA_KEYS = ("sha256", "file_sha256", "sha_256", "sha", "hash", "pre_image_sha256", "prefix_sha256")
PATH_KEYS = ("path", "file", "filename", "relpath", "relative_path", "rel")
MANIFEST_NAME_HINTS = ("hash", "pin", "manifest", "binding", "handoff", "evidence_index", "final")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def walk(node, out):
    if isinstance(node, dict):
        sha = None
        for k in SHA_KEYS:
            v = node.get(k)
            if isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdefABCDEF" for c in v):
                sha = v.lower()
                break
        path = None
        for k in PATH_KEYS:
            v = node.get(k)
            if isinstance(v, str) and 0 < len(v) < 400 and ("\\" in v or "/" in v or "." in v):
                path = v
                break
        if sha and path:
            out.append((path, sha))
        for v in node.values():
            walk(v, out)
    elif isinstance(node, list):
        for v in node:
            walk(v, out)


def main() -> int:
    for arg in sys.argv[1:]:
        root = Path(arg)
        print(f"===== {root}")
        manifests = []
        for p in root.rglob("*.json"):
            if any(h in p.name.lower() for h in MANIFEST_NAME_HINTS) and "__pycache__" not in str(p):
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    continue
                pairs = []
                walk(data, pairs)
                if pairs:
                    manifests.append((p, pairs))
        for mp, pairs in manifests:
            ok = bad = missing = 0
            lines = []
            seen = set()
            for path, sha in pairs:
                if (path, sha) in seen:
                    continue
                seen.add((path, sha))
                cand = root / path.replace("/", "\\")
                if not cand.is_file():
                    cand2 = root / Path(path).name
                    if cand2.is_file():
                        cand = cand2
                    else:
                        missing += 1
                        if len(lines) < 8:
                            lines.append(f"    MISSING {path}")
                        continue
                actual = sha256_file(cand)
                if actual == sha:
                    ok += 1
                else:
                    bad += 1
                    if len(lines) < 8:
                        lines.append(f"    MISMATCH {path} recorded={sha[:16]} actual={actual[:16]}")
            print(f"  {mp.relative_to(root)}: pairs={len(seen)} ok={ok} mismatch={bad} missing={missing}")
            for ln in lines:
                print(ln)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
