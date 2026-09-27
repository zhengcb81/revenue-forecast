"""Build the B2 iso: copy the two target files + their import closure, record pre-images.

Read-only against product repos; writes ONLY under this attempt directory.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PRODUCT_DAYU = Path(r"C:\Users\郑曾波\Projects\dayu-agent\dayu-agent\dayu")
PRODUCT_CW = Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki")

TARGETS = [
    PRODUCT_DAYU / "fins" / "downloaders" / "sec_downloader.py",
    PRODUCT_CW / "source_catalog" / "dayu_cli_adapter.py",
]

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_manifest(root: Path) -> dict:
    entries = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and ".pyc" != path.suffix:
            entries[str(path.relative_to(root)).replace("\\", "/")] = [
                sha256(path),
                path.stat().st_size,
            ]
    return entries


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def main() -> int:
    ISO.mkdir(parents=True, exist_ok=True)

    preimage = {
        "recorded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": "pre-image of the two product files that this card changes (read-only copies)",
        "targets": [],
    }
    for target in TARGETS:
        stat = target.stat()
        preimage["targets"].append(
            {
                "product_path": str(target),
                "sha256": sha256(target),
                "bytes": stat.st_size,
                "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(
                    timespec="seconds"
                ),
            }
        )

    copy_tree(PRODUCT_DAYU, ISO / "dayu_repo" / "dayu")
    copy_tree(PRODUCT_CW, ISO / "cw_repo" / "src" / "company_wiki")

    preimage["iso_trees"] = {
        "iso/dayu_repo/dayu": tree_manifest(ISO / "dayu_repo" / "dayu"),
        "iso/cw_repo/src/company_wiki": tree_manifest(ISO / "cw_repo" / "src" / "company_wiki"),
    }
    preimage["iso_tree_counts"] = {
        key: len(value) for key, value in preimage["iso_trees"].items()
    }

    # sanity: iso copies must be byte-identical to the product pre-image
    for rel in (
        Path("fins") / "downloaders" / "sec_downloader.py",
    ):
        src = PRODUCT_DAYU / rel
        dst = ISO / "dayu_repo" / "dayu" / rel
        assert sha256(src) == sha256(dst), rel
    cw_rel = Path("source_catalog") / "dayu_cli_adapter.py"
    assert sha256(PRODUCT_CW / cw_rel) == sha256(ISO / "cw_repo" / "src" / "company_wiki" / cw_rel)

    out = ATTEMPT / "iso" / "preimage.json"
    out.write_text(json.dumps(preimage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"iso built at {ISO}")
    print(f"preimage -> {out}")
    for item in preimage["targets"]:
        print(f"  {item['sha256']} {item['bytes']:>8} {item['product_path']}")
    print("tree counts:", preimage["iso_tree_counts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
