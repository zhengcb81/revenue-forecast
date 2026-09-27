"""Controlled acquisition helper (read-only w.r.t. product repos).

Usage: python -B dl.py <url> <out_path> [referer]
Downloads bytes with urllib (OpenSSL), prints a JSON receipt on stdout:
  {"url", "retrieved_utc", "http_status", "bytes", "sha256", "content_type", "final_url", "error"}
Nothing outside the given out_path is written.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ControlledForensicsStation/1.0"


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    url, out_path = sys.argv[1], sys.argv[2]
    receipt = {"url": url, "retrieved_utc": None, "http_status": None, "bytes": None,
               "sha256": None, "content_type": None, "final_url": None, "error": None}
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            receipt["http_status"] = resp.status
            receipt["content_type"] = resp.headers.get("Content-Type")
            receipt["final_url"] = resp.geturl()
    except urllib.error.HTTPError as e:
        receipt["http_status"] = e.code
        receipt["error"] = "HTTPError: %s" % e.reason
        try:
            data = e.read()
        except Exception:
            data = b""
    except Exception as e:  # noqa: BLE001
        receipt["error"] = "%s: %s" % (type(e).__name__, e)
        data = b""
    receipt["retrieved_utc"] = utc_now()
    if data:
        with open(out_path, "wb") as fh:
            fh.write(data)
        receipt["bytes"] = len(data)
        receipt["sha256"] = hashlib.sha256(data).hexdigest()
    print(json.dumps(receipt, ensure_ascii=False))
    return 0 if receipt["http_status"] == 200 and receipt["bytes"] else 1


if __name__ == "__main__":
    sys.exit(main())
