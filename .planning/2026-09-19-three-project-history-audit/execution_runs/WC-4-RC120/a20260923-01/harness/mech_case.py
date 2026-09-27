"""WC-4 mechanism probe: where does rc=120 come from?

Runs a *snippet that contains no revenue-forecast code* (pure CPython) as a
child process under three stdout sinks and records the raw child return code.

  sink=pipe_noreader : write end of a pipe whose read end is closed (the F12 arm)
  sink=pipe_reader   : pipe with a live reader (baseline)
  sink=file          : stdout redirected to a regular file (baseline)

The harness only ever reads Popen.returncode (GetExitCodeProcess) and never
rewrites it.  Snippets are written to this card's own scratch dir (%TEMP% is
NOT used for artifacts; only for the runner's own temp dir is fine).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
OUT = ATTEMPT / "evidence" / "mech" / "mech_cases.json"

SNIPPETS = {
    # M0: the F12 shape in pure CPython — small buffered write, normal exit 0.
    "M0_buffered_write_exit0": "import sys\nsys.stdout.write('valid\\n')\nraise SystemExit(0)\n",
    # M1: same, but an in-domain exit code 2 is requested by the program.
    "M1_buffered_write_exit2": "import sys\nsys.stdout.write('valid\\n')\nraise SystemExit(2)\n",
    # M2: fix shape A — explicit flush, error text on stderr, stdout swapped
    # for a devnull file before exit (rc normalized to 2 on the failure path).
    "M2_flush_catch_devnull": (
        "import sys, os\n"
        "rc = 2\n"
        "sys.stdout.write('valid\\n')\n"
        "try:\n"
        "    sys.stdout.flush()\n"
        "except (OSError, ValueError) as exc:\n"
        "    sys.stderr.write('error: stdout flush failed: %r\\n' % (exc,))\n"
        "    sys.stderr.flush()\n"
        "    sys.stdout = open(os.devnull, 'w')\n"
        "raise SystemExit(rc)\n"
    ),
    # M3: fix shape B — same, but swap for a no-op Python object instead of a
    # devnull file.
    "M3_flush_catch_dummy": (
        "import sys\n"
        "rc = 2\n"
        "sys.stdout.write('valid\\n')\n"
        "try:\n"
        "    sys.stdout.flush()\n"
        "except (OSError, ValueError) as exc:\n"
        "    sys.stderr.write('error: stdout flush failed: %r\\n' % (exc,))\n"
        "    sys.stderr.flush()\n"
        "    class _Null:\n"
        "        def write(self, data):\n"
        "            return len(data)\n"
        "        def flush(self):\n"
        "            return None\n"
        "    sys.stdout = _Null()\n"
        "raise SystemExit(rc)\n"
    ),
    # M4: success path with the M2 fix code — must stay 0 (normal path).
    "M4_success_path_devnull_not_taken": (
        "import sys, os\n"
        "rc = 0\n"
        "sys.stdout.write('valid\\n')\n"
        "try:\n"
        "    sys.stdout.flush()\n"
        "except (OSError, ValueError) as exc:\n"
        "    rc = 2\n"
        "raise SystemExit(rc)\n"
    ),
}


def run(snippet: str, sink: str) -> dict:
    with tempfile.TemporaryDirectory(dir=str(ATTEMPT / "evidence" / "mech")) as td:
        script = Path(td) / "snippet.py"
        script.write_text(snippet, encoding="utf-8")
        base = [sys.executable, "-B", str(script)]
        if sink == "pipe_noreader":
            r_fd, w_fd = __import__("os").pipe()
            p = subprocess.Popen(base, stdout=w_fd, stderr=subprocess.PIPE,
                                 stdin=subprocess.DEVNULL)
            __import__("os").close(w_fd)
            __import__("os").close(r_fd)
            _, err = p.communicate(timeout=60)
        elif sink == "pipe_reader":
            p = subprocess.run(base, capture_output=True, stdin=subprocess.DEVNULL,
                               timeout=60)
            err = p.stderr
        elif sink == "file":
            outp = Path(td) / "out.txt"
            with outp.open("wb") as fh:
                p = subprocess.run(base, stdout=fh, stderr=subprocess.PIPE,
                                   stdin=subprocess.DEVNULL, timeout=60)
            err = p.stderr
        else:
            raise ValueError(sink)
        return {
            "raw_returncode": p.returncode,
            "stderr": (err or b"").decode("utf-8", "replace")[:800],
        }


def main() -> int:
    results = {}
    for name, snippet in SNIPPETS.items():
        sinks = ["pipe_noreader", "pipe_reader", "file"]
        if name.startswith("M2") or name.startswith("M3"):
            sinks = ["pipe_noreader", "pipe_reader"]
        results[name] = {sink: run(snippet, sink) for sink in sinks}
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(
        {k: {s: v["raw_returncode"] for s, v in d.items()}
         for k, d in results.items()},
        ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
