"""I-14-C r3: timing table for the credential redactor on long `_`-separated keys.

Reproduces the r2 review finding F-I14C-07: the r2 key expression
``(?:[A-Za-z0-9]+[_-])*<atom>(?:[_-][A-Za-z0-9]+)*`` has nested quantifiers over the
`_`/`-` separated segments, so its cost grows super-linearly in the segment count, and
``redact_and_truncate`` feeds it the WHOLE message before truncating.

Each measurement runs in its own subprocess with a hard timeout, so a hang is recorded as
TIMEOUT instead of killing the benchmark.

    python bench_redact.py --src <iso>/<tree>/src --label <tree> --out <attempt>/r3/bench_<tree>.json

Child mode:  python bench_redact.py --one <k> --src <tree>/src
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

KS = [200, 500, 1000, 2000, 4000, 8000, 16000, 40000]
TIMEOUT_SECONDS = 20

# adversarial shapes: a long run of `_`-separated one-char segments before the separator
SHAPES = {
    "underscore-segments": lambda k: ("a_" * k) + "=",
    "dash-segments": lambda k: ("a-" * k) + "=",
    "segments-no-separator": lambda k: ("a_" * k)[:-1],
    "segments-then-atom": lambda k: ("a_" * k) + "token=ZZZ",
    "quoted-never-closed": lambda k: ("a_" * k) + '="' + ("b" * 500),
    "long-single-token": lambda k: ("a" * k) + "=",
    "many-empty-pairs": lambda k: "k=" * k,
    # the remaining regex path (`authorization` / `bearer`) must be stressed too
    "auth-words": lambda k: "authorization: " * k,
    "bearer-words": lambda k: "bearer " * k,
    "url-with-token": lambda k: "url=https://x/" + ("a" * k) + "?token=ZZZ",
}


def child(k: int, shape: str, src: str) -> int:
    sys.path.insert(0, str(Path(src).resolve()))
    from company_wiki.source_catalog.observability import redact_text

    text = SHAPES[shape](k)
    start = time.perf_counter()
    out = redact_text(text)
    elapsed = time.perf_counter() - start
    print(json.dumps({"k": k, "shape": shape, "seconds": elapsed,
                      "in_len": len(text), "out_len": len(out),
                      "changed": out != text}))
    return 0


def benchmark(src: str, label: str, out_path: Path,
              timeout: float = TIMEOUT_SECONDS) -> dict:
    here = Path(__file__).resolve()
    rows = []
    for shape in SHAPES:
        for k in KS:
            argv = [sys.executable, "-X", "utf8", "-B", str(here),
                    "--one", str(k), "--shape", shape, "--src", src]
            start = time.perf_counter()
            try:
                proc = subprocess.run(argv, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, timeout=timeout)
                payload = json.loads(proc.stdout.decode("utf-8", "replace").strip()
                                     or "{}")
                payload["wall_seconds"] = time.perf_counter() - start
                payload["status"] = "ok" if proc.returncode == 0 else "child-error"
                if proc.returncode != 0:
                    payload["stderr"] = proc.stderr.decode("utf-8", "replace")[:300]
            except subprocess.TimeoutExpired:
                payload = {"k": k, "shape": shape, "status": "TIMEOUT",
                           "seconds": None, "wall_seconds": time.perf_counter() - start}
            payload["label"] = label
            rows.append(payload)
    report = {"label": label, "src": src, "timeout_seconds": timeout, "rows": rows}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    summary = {}
    for row in rows:
        summary.setdefault(row["shape"], {})[row["k"]] = (
            "TIMEOUT" if row["status"] == "TIMEOUT" else round(row["seconds"], 4))
    print(json.dumps({"label": label, "summary": summary}, indent=2, ensure_ascii=True))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src")
    parser.add_argument("--label")
    parser.add_argument("--out")
    parser.add_argument("--timeout", type=float, default=TIMEOUT_SECONDS)
    parser.add_argument("--one", type=int)
    parser.add_argument("--shape", default="underscore-segments", choices=sorted(SHAPES))
    args = parser.parse_args(argv)
    if args.one is not None:
        return child(args.one, args.shape, args.src)
    benchmark(args.src, args.label, Path(args.out), args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
