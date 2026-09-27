"""D1 independent experiment: the three candidate peak-RSS methods on this host.

Card clause 3 leaves the peak method to the ops reviewer.  The three options in
decision.md D1 are exercised here against the same fixture (F3, allocates ~256 MB
and holds it) so the choice is not taken on the implementer's word alone:

  option 1  psutil.Process(pid).memory_info().peak_wset   (OS lifetime peak)
  option 2  rss sampled live at a fixed interval, peak = max of the tree sum
  option 3  a private ctypes GetProcessMemoryInfo().PeakWorkingSetSize call

Observations recorded for the ruling:
  * is peak_wset already above rss at the FIRST sample (i.e. does it carry the
    interpreter start-up spike, which is not attributable to the measurement
    window)?
  * are option 1 and option 3 numerically identical for the same pid (i.e. does
    option 3 add any information over option 1)?
  * can the value still be read after the process exited?
  * does the 50 ms sampler observe the fixture's own pid?

Usage: python d1_peak_method_experiment.py <fixture.py> <out.json>
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

INTERVAL = 0.05  # the frozen candidate: 50 ms


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def ctypes_peak_wset(pid: int) -> int | None:
    """Option 3: the raw Win32 counter, read without psutil."""
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    k32 = ctypes.windll.kernel32
    handle = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not handle:
        return None
    try:
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(counters)
        # psapi.dll exports GetProcessMemoryInfo; on Win7+ the same symbol also
        # exists in kernel32 as K32GetProcessMemoryInfo.  Try both, record which
        # one answered.
        fn = None
        for dll, name in ((ctypes.windll.psapi, "GetProcessMemoryInfo"),
                          (ctypes.windll.kernel32, "K32GetProcessMemoryInfo")):
            try:
                fn = getattr(dll, name)
            except AttributeError:
                continue
            fn.argtypes = [wintypes.HANDLE,
                           ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD]
            fn.restype = wintypes.BOOL
            if fn(handle, ctypes.byref(counters), counters.cb):
                return int(counters.PeakWorkingSetSize)
            fn = None
        return None
    finally:
        k32.CloseHandle(handle)


def main() -> int:
    fixture = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    python = sys.executable

    import psutil

    doc: dict = {
        "host": {"platform": "windows", "psutil_version": psutil.__version__},
        "interval_seconds": INTERVAL,
        "fixture": str(fixture),
        "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    proc = subprocess.Popen(
        [python, "-X", "utf8", "-B", str(fixture)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace",
    )
    popen_pid = proc.pid

    # Read the envelope on a thread so sampling starts at spawn time, not after
    # the fixture printed its pid.
    envelope_holder: dict = {}

    def _read_envelope() -> None:
        try:
            envelope_holder["envelope"] = json.loads(proc.stdout.readline())
        except Exception as exc:  # noqa: BLE001
            envelope_holder["error"] = f"{type(exc).__name__}: {exc}"

    reader = threading.Thread(target=_read_envelope, daemon=True)
    reader.start()

    p = psutil.Process(popen_pid)
    t_start = time.perf_counter()
    samples: list[dict] = []
    while True:
        try:
            tree = [p, *p.children(recursive=True)]
        except psutil.Error:
            tree = [p]
        row: dict = {"t": round(time.perf_counter() - t_start, 4), "pids": [],
                     "rss_sum": 0, "rss_by_pid": {}, "peak_wset_by_pid": {},
                     "ctypes_peak_wset_by_pid": {}, "error": None}
        rss_sum = 0
        for item in tree:
            try:
                if not item.is_running():
                    continue
                mi = item.memory_info()
                rss_sum += int(mi.rss)
                row["pids"].append(item.pid)
                row["rss_by_pid"][str(item.pid)] = int(mi.rss)
                pw = int(getattr(mi, "peak_wset", 0) or 0)
                if pw:
                    row["peak_wset_by_pid"][str(item.pid)] = pw
                cp = ctypes_peak_wset(item.pid)
                if cp is not None:
                    row["ctypes_peak_wset_by_pid"][str(item.pid)] = cp
            except Exception as exc:  # noqa: BLE001 - record, do not hide
                row["error"] = f"{type(exc).__name__}: {exc}"
        row["rss_sum"] = rss_sum
        samples.append(row)
        if proc.poll() is not None:
            break
        time.sleep(INTERVAL)

    reader.join(timeout=5)
    stderr_tail = (proc.stderr.read() or "")[:400]
    rc = proc.wait()
    envelope = envelope_holder.get("envelope") or {}
    fixture_pid = int(envelope.get("pid") or -1)

    # Post-mortem read: is the value available after the process is gone?
    post_mortem: dict = {}
    try:
        psutil.Process(popen_pid).memory_info()
        post_mortem["psutil_after_exit"] = "readable"
    except Exception as exc:  # noqa: BLE001
        post_mortem["psutil_after_exit"] = f"{type(exc).__name__}: {exc}"
    cp_after = ctypes_peak_wset(popen_pid)
    post_mortem["ctypes_after_exit"] = cp_after if cp_after is not None else "OpenProcess failed (None)"

    alive_rows = [s for s in samples if s["pids"]]
    fixture_seen_alive = any(fixture_pid in s["pids"] for s in samples)

    def peak_of(mapping_attr: str) -> int | None:
        vals = [v for s in alive_rows for v in s[mapping_attr].values()]
        return max(vals) if vals else None

    first = samples[0]
    first_peak_vals = list(first["peak_wset_by_pid"].values())
    doc.update({
        "raw_returncode": rc,
        "popen_pid": popen_pid,
        "fixture_reported_pid": fixture_pid,
        "popen_pid_is_fixture_pid": popen_pid == fixture_pid,
        "envelope": envelope,
        "sample_count": len(samples),
        "sample_count_with_pids": len(alive_rows),
        "fixture_pid_seen_in_samples": fixture_seen_alive,
        "fixture_pid_sample_count": sum(1 for s in samples if fixture_pid in s["pids"]),
        "option2_tree_sum_peak_rss_gb": (round(
            max(s["rss_sum"] for s in alive_rows) / (1024 ** 3), 4) if alive_rows else None),
        "option1_peak_wset_max_gb": (round(peak_of("peak_wset_by_pid") / (1024 ** 3), 4)
                                     if peak_of("peak_wset_by_pid") else None),
        "option3_ctypes_peak_wset_max_gb": (round(peak_of("ctypes_peak_wset_by_pid") / (1024 ** 3), 4)
                                            if peak_of("ctypes_peak_wset_by_pid") else None),
        "first_sample_rss_sum_mb": round(first["rss_sum"] / (1024 ** 2), 3),
        "first_sample_peak_wset_max_mb": (round(max(first_peak_vals) / (1024 ** 2), 3)
                                          if first_peak_vals else None),
        "first_sample_peak_exceeds_rss_by_mb": (
            round((max(first_peak_vals) - first["rss_sum"]) / (1024 ** 2), 3)
            if first_peak_vals else None),
        "declared_allocated_mb": envelope.get("allocated_mb"),
        "post_mortem_read": post_mortem,
        "stderr_head": stderr_tail,
        "end_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "samples": samples,
    })

    pairs = []
    for s in samples:
        for pid, pw in s["peak_wset_by_pid"].items():
            cp = s["ctypes_peak_wset_by_pid"].get(pid)
            if cp is not None:
                pairs.append((pw, cp))
    doc["option1_vs_option3_pair_count"] = len(pairs)
    doc["option1_vs_option3_all_pairs_equal"] = bool(pairs) and all(a == b for a, b in pairs)
    doc["option1_peak_wset_monotone_nondecreasing"] = all(
        all(b["peak_wset_by_pid"].get(pid, v) >= v
            for pid, v in a["peak_wset_by_pid"].items())
        for a, b in zip(samples, samples[1:]) if a["peak_wset_by_pid"])

    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    brief = {k: v for k, v in doc.items() if k != "samples"}
    print(json.dumps(brief, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
