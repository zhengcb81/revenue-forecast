"""Build the ARMS F / G mutated cases.json for the M05-M08 batch (REM-21 / B5).

Reads the frozen cases.json (already copied into the arm scratch root) and rewrites
ONLY one negative case's declaration:
  * F: the first negative case's "expected" -> "ValueError"  (isinstance-superclass decoy)
  * G: the first negative case's "expected" key DELETED

Nothing else is touched; originals under execution_runs/<CARD>/ are never opened
for writing. Output is written back over the arm's own COPY.
"""
import hashlib
import json
import sys

TARGET_KEY_SUBSTR = "ValueError"


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump(path, doc):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def pick_first_negative(cases_doc):
    """First negative case (lowest id) whose frozen 'expected' is 'ModelRegistryError'."""
    candidates = [c for c in cases_doc["cases"]
                  if isinstance(c.get("expected"), str) and c["expected"].strip()]
    if not candidates:
        raise SystemExit("no case with a usable frozen declaration")
    candidates.sort(key=lambda c: str(c["id"]))
    return candidates[0]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    arm, path = sys.argv[1], sys.argv[2]
    doc = load(path)
    target = pick_first_negative(doc)
    tid = target["id"]
    before = target.get("expected")
    if arm == "F":
        target["expected"] = TARGET_KEY_SUBSTR
    elif arm == "G":
        del target["expected"]
    else:
        raise SystemExit("arm must be F or G")
    dump(path, doc)
    # re-read and confirm the mutation landed exactly once
    check = load(path)
    hit = [c for c in check["cases"] if c["id"] == tid][0]
    if arm == "F":
        assert hit["expected"] == TARGET_KEY_SUBSTR, hit
    else:
        assert "expected" not in hit, hit
    others_missing = [c["id"] for c in check["cases"] if "expected" not in c]
    print(json.dumps({
        "arm": arm,
        "mutated_case": tid,
        "expected_before": before,
        "expected_after": hit.get("expected", "<key deleted>"),
        "cases_total": len(check["cases"]),
        "cases_missing_expected": others_missing,
        "cases_json_sha256": sha256_file(path),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
