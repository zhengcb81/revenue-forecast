"""I-09-C continuously-reading consumer (card 按序动作 5).

Samples the registry in a tight loop while publisher processes run, recording
for every sample: byte size, line count, independent chain verification, and
the number of *committed* rows a consumer would accept.  It must never accept
a half line or an uncommitted row as a formal package (verified per sample).
Stops when <stop-file> appears or <max-seconds> elapse.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import append_jsonl, setup_paths  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--stop-file", required=True)
    parser.add_argument("--max-seconds", type=float, default=60.0)
    args = parser.parse_args()

    setup_paths()
    from contracts.evidence import canonical_sha256  # noqa: E402

    registry = Path(args.registry)
    stop = Path(args.stop_file)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    start = time.time()
    samples = 0
    errors = 0
    accepted_flips = []
    last_committed = -1

    while time.time() - start < args.max_seconds and not stop.exists():
        rec = {"t": time.time()}
        try:
            if registry.exists():
                text = registry.read_text(encoding="utf-8", errors="strict")
                rec["bytes"] = len(text.encode("utf-8"))
                lines = [ln for ln in text.splitlines() if ln.strip()]
                rec["lines"] = len(lines)
                ok = True
                reason = None
                committed = 0
                prev = None
                for i, line in enumerate(lines, start=1):
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        ok, reason = False, f"unparseable line {i} (half line visible)"
                        break
                    payload = {k: v for k, v in entry.items() if k != "line_sha256"}
                    if canonical_sha256(payload) != entry.get("line_sha256"):
                        ok, reason = False, f"line {i} hash mismatch"
                        break
                    if entry.get("prev_line_sha256") != prev:
                        ok, reason = False, f"line {i} chain break"
                        break
                    prev = entry.get("line_sha256")
                    if entry.get("state") == "committed":
                        committed += 1
                rec["chain_ok"] = ok
                if reason:
                    rec["chain_error"] = reason
                rec["committed_rows_visible"] = committed
                if committed != last_committed:
                    accepted_flips.append({"t": time.time(), "committed": committed})
                    last_committed = committed
            else:
                rec.update(bytes=0, lines=0, chain_ok=True, committed_rows_visible=0)
        except UnicodeDecodeError as exc:
            errors += 1
            rec.update(chain_ok=False, chain_error=f"partial read (decode): {exc}")
        except OSError as exc:
            errors += 1
            rec.update(chain_ok=False, chain_error=f"oserror: {exc}")
        append_jsonl(out, rec)
        samples += 1
        time.sleep(0.005)

    append_jsonl(
        out,
        {
            "final": True,
            "samples": samples,
            "errors": errors,
            "committed_transitions": accepted_flips,
            "stopped_by_file": stop.exists(),
            "elapsed": time.time() - start,
            "reader_pid": os.getpid(),
        },
    )
    print(f"reader_loop samples={samples} errors={errors} transitions={len(accepted_flips)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
