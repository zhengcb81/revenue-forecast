"""Collect download provenance for wheels in _dl/.

For every wheel file in the given directory:
  - local: bytes, sha256, mtime-UTC (retrieval finish time on this host)
  - upstream: PyPI JSON API project URL, exact file URL, declared sha256/size
  - purpose: fixed mapping by package name
Writes JSON (UTF-8, no BOM, LF) to --out. Exits non-zero if any local sha256
does not match the upstream digest.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.request

UA = {"User-Agent": "ControlledCapabilityStation/1.0"}
API = "https://pypi.org/pypi/{name}/json"

PURPOSE = {
    "rapidocr": "OCR engine (detection+recognition, pure-python wheel incl. models)",
    "onnxruntime": "OCR inference runtime for rapidocr (CPU EP)",
    "pypdfium2": "PDF page renderer (image pipeline for OCR)",
    "opencv-python": "image ops required by rapidocr (declared dependency)",
    "numpy": "numeric arrays (rapidocr/onnxruntime dependency)",
    "pillow": "image I/O (rapidocr dependency, PNG save/load)",
    "shapely": "geometry ops for text detection post-processing (rapidocr dep)",
    "pyclipper": "polygon clipping for text detection (rapidocr dep)",
    "pyyaml": "config loading (rapidocr dep)",
    "tqdm": "progress display (rapidocr dep)",
    "omegaconf": "config framework (rapidocr dep)",
    "antlr4-python3-runtime": "antlr runtime (omegaconf dep)",
    "requests": "HTTP helper (rapidocr dep)",
    "colorlog": "colored logging (onnxruntime dep)",
    "coloredlogs": "logging shim (onnxruntime dep)",
    "humanfriendly": "terminal utils (coloredlogs dep)",
    "flatbuffers": "serialization (onnxruntime dep)",
    "packaging": "version utils (onnxruntime dep)",
    "protobuf": "model/IR serialization (onnxruntime dep)",
    "sympy": "symbolic ops (onnxruntime dep)",
    "mpmath": "math backend (sympy dep)",
    "six": "py2/3 compat (rapidocr dep)",
    "urllib3": "HTTP client (requests dep)",
    "idna": "IDNA codec (requests dep)",
    "charset-normalizer": "charset detection (requests dep)",
    "certifi": "CA bundle (requests dep)",
}


def utc_iso(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def wheel_name(fn: str) -> str:
    # PEP 427: {distribution}-{version}(-{build})?-{python}-{abi}-{platform}.whl
    parts = fn.split("-")
    return parts[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dl", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    entries = []
    mismatches = []
    seen_projects = {}
    files = sorted(
        f for f in os.listdir(args.dl) if f.endswith(".whl") or f.endswith(".tar.gz")
    )
    for fn in files:
        path = os.path.join(args.dl, fn)
        local_sha = sha256_file(path)
        local_bytes = os.path.getsize(path)
        st = os.stat(path)
        proj = wheel_name(fn)
        if proj not in seen_projects:
            url = API.format(name=proj.replace("_", "-"))
            req = urllib.request.Request(url, headers=UA)
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    seen_projects[proj] = {"api_url": url, "json": json.loads(r.read())}
            except Exception as e:  # noqa: BLE001
                seen_projects[proj] = {"api_url": url, "error": f"{type(e).__name__}: {e}"}
        blob = seen_projects[proj]
        up = None
        data = blob.get("json")
        if data:
            for u in data.get("urls", []):
                if u.get("filename") == fn:
                    up = u
                    break
            if up is None:
                for rel in data.get("releases", {}).values():
                    for u in rel:
                        if u.get("filename") == fn:
                            up = u
                            break
                    if up:
                        break
        entry = {
            "file": fn,
            "local_path": path,
            "local_bytes": local_bytes,
            "local_sha256": local_sha,
            "retrieved_utc": utc_iso(st.st_mtime),
            "pypi_api_url": blob.get("api_url"),
            "project": data.get("info", {}).get("name") if data else None,
            "project_version": data.get("info", {}).get("version") if data else None,
            "upstream_url": up.get("url") if up else None,
            "upstream_sha256": up.get("digests", {}).get("sha256") if up else None,
            "upstream_bytes": up.get("size") if up else None,
            "upstream_upload_time": up.get("upload_time_iso_8601") if up else None,
            "metadata_error": blob.get("error") or (None if up else "filename not found in PyPI JSON"),
            "purpose": PURPOSE.get(norm(wheel_name(fn)).replace(" ", "-"), "dependency"),
        }
        if up and up.get("digests", {}).get("sha256") != local_sha:
            mismatches.append(fn)
            entry["sha256_match"] = False
        elif up:
            entry["sha256_match"] = True
        entry["over_200mb"] = local_bytes > 200 * 1024 * 1024
        entries.append(entry)

    doc = {
        "generated_utc": utc_now(),
        "count": len(entries),
        "total_bytes": sum(e["local_bytes"] for e in entries),
        "largest_single_bytes": max((e["local_bytes"] for e in entries), default=0),
        "any_over_200mb": any(e["over_200mb"] for e in entries),
        "sha256_mismatches": mismatches,
        "downloads": entries,
        "note": "retrieved_utc = local mtime of the wheel (pip download completion time, UTC)",
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(args.out, "r", encoding="utf-8") as f:
        json.load(f)
    print(json.dumps({k: doc[k] for k in ("count", "total_bytes", "largest_single_bytes",
                                          "any_over_200mb", "sha256_mismatches")},
                     ensure_ascii=False))
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
