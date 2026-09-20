"""I-14-C r2: apply the r1 card diff's '+' side to a copy of the pristine tree.

Used to rebuild `iso/product_r1` (the code the r1 review actually saw) so that the
F-I14C-02 env-var leak can be reproduced against the r1 rule itself, not merely
against the pristine tree that has no redactor at all.

The splice is verified: each written file's sha256 must equal the hash recorded for
the r1 fixed tree, otherwise the reconstruction is refused.

    python apply_card_diff.py --diff <attempt>/changes.diff \
        --cw <company-wiki> --out <attempt>/iso/product_r1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

R1_FIXED_HASHES = {
    "src/company_wiki/source_catalog/worker.py":
        "39971d059d6fc3f5a4e89f560c93ac6f08057da7719230180436a8ae2237deac",
    "src/company_wiki/source_catalog/observability.py":
        "afbaa68fd14b9d48817a2f896c8d4920eeec8ef1fb90ab8a30b11aa308059b06",
    "src/company_wiki/source_catalog/cli.py":
        "af3aa91a4039a2b38fe024acdc3e576218c361695fc84d239c4c69ef20bf5b9d",
}


def parse_diff(text: str) -> dict[str, list[dict]]:
    files: dict[str, list[dict]] = {}
    current: str | None = None
    hunk: dict | None = None
    for line in text.splitlines():
        if line.startswith("+++ b/"):
            current = line[len("+++ b/"):]
            files.setdefault(current, [])
            hunk = None
        elif line.startswith("@@") and current is not None:
            hunk = {"minus": [], "plus": []}
            files[current].append(hunk)
        elif hunk is not None and line.startswith("---"):
            continue
        elif hunk is not None and line.startswith("-"):
            hunk["minus"].append(line[1:])
        elif hunk is not None and line.startswith("+"):
            hunk["plus"].append(line[1:])
        elif hunk is not None and line.startswith(" "):
            hunk["minus"].append(line[1:])
            hunk["plus"].append(line[1:])
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff", required=True)
    parser.add_argument("--cw", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--python", required=True)
    args = parser.parse_args(argv)

    diff_text = Path(args.diff).read_text(encoding="utf-8")
    files = parse_diff(diff_text)
    out = Path(args.out).resolve()
    cw = Path(args.cw).resolve()
    if out.exists():
        shutil.rmtree(out)
    (out / "src").mkdir(parents=True)
    shutil.copytree(cw / "src", out / "src", dirs_exist_ok=True)
    for cache in out.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)

    report: dict = {"out": str(out), "files": [], "all_ok": True}
    for rel, hunks in files.items():
        target = out / rel
        text = target.read_text(encoding="utf-8")
        status = "ok"
        for index, hunk in enumerate(hunks):
            minus_block = "\n".join(hunk["minus"])
            plus_block = "\n".join(hunk["plus"])
            if text.count(minus_block) != 1:
                status = f"REFUSED-anchor-count@hunk{index}"
                break
            text = text.replace(minus_block, plus_block)
        body = text.encode("utf-8")
        digest_lf = hashlib.sha256(body).hexdigest()
        digest_crlf = hashlib.sha256(body.replace(b"\n", b"\r\n")).hexdigest()
        expected = R1_FIXED_HASHES.get(rel)
        if digest_crlf == expected:
            newline_form = "crlf"
        elif digest_lf == expected:
            newline_form = "lf"
        else:
            newline_form = ""
            status = "HASH-MISMATCH"
        if status == "ok":
            data = body if newline_form == "lf" else body.replace(b"\n", b"\r\n")
            target.write_bytes(data)
        report["files"].append({"path": rel, "status": status,
                                "newline_form": newline_form,
                                "sha256_lf": digest_lf, "sha256_crlf": digest_crlf,
                                "expected_r1_sha256": expected})
        report["all_ok"] = report["all_ok"] and status == "ok"

    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
