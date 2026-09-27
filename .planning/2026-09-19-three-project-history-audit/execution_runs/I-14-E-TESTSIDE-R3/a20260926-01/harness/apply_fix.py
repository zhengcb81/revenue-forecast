"""I-14-E-TESTSIDE: deterministic apply / mutate / revert of the test-side fix.

Modes
  fix     : apply the frozen fix (oracle.md §2.1) to the iso test file
  mutate  : apply the fix, then replace the exported formula with the hard-coded
            0.5 s constant (mutation M1, oracle.md §3.E)
  revert  : restore the byte-identical original (from before/test_file_original.py)

Every mode fails loudly if its anchor text is not found exactly once, so a
silent no-op cannot masquerade as an applied change.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
TEST = ATTEMPT / "iso" / "tests" / "contract" / "test_source_catalog_worker_bootstrap.py"
ORIGINAL = ATTEMPT / "before" / "test_file_original.py"

# ---------------------------------------------------------------- helpers ---

HELPERS_ANCHOR = "def _launcher_events(project: Path) -> list[dict[str, object]]:"
HELPERS_ANCHOR_TAIL = '    return [json.loads(line) for line in text.splitlines() if line.strip()]\n'

HELPERS = '''

# ---------------------------------------------------------------------------
# I-14-E-TESTSIDE — test-side timing fix (frozen in oracle.md §2, owner §二十五 A)
# ---------------------------------------------------------------------------

_WARMUP_PROBE_PS1 = r"""
param(
    [Parameter(Mandatory = $true)][string]$PythonExe,
    [Parameter(Mandatory = $true)][string]$ProjectRoot,
    [Parameter(Mandatory = $true)][string]$LogDir,
    [double]$DeadlineSeconds = 60
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $ProjectRoot
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$ConfigPath = Join-Path $ProjectRoot 'config/source_catalog.yaml'
$WorkerConfigPath = Join-Path $ProjectRoot 'config/source_catalog_worker.yaml'
$CatalogDir = Join-Path $ProjectRoot '.source_catalog'
$Marker = Join-Path $CatalogDir 'fake_worker_count.txt'
if (Test-Path -LiteralPath $Marker) { Remove-Item -LiteralPath $Marker -Force }
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$Arguments = @(
    '-m', 'company_wiki.source_catalog.cli',
    '--config', $ConfigPath,
    'worker',
    '--worker-config', $WorkerConfigPath
)
# Exactly the supervisor's own clock: $StartedAt immediately before Start-Process
# (source_catalog_worker.ps1:327-333), same argv/cwd/redirects.
$StartedAt = Get-Date
$Child = Start-Process `
    -FilePath $PythonExe `
    -ArgumentList $Arguments `
    -WorkingDirectory $ProjectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $LogDir 'warmup_stdout.log') `
    -RedirectStandardError (Join-Path $LogDir 'warmup_stderr.log') `
    -PassThru
$ChildPid = $Child.Id
$found = $false
while (((Get-Date) - $StartedAt).TotalSeconds -lt $DeadlineSeconds) {
    if (Test-Path -LiteralPath $Marker) { $found = $true; break }
    Start-Sleep -Milliseconds 5
}
$t0 = ((Get-Date) - $StartedAt).TotalSeconds
try {
    if (-not $Child.HasExited) { $Child.Kill(); $null = $Child.WaitForExit(10000) }
} catch { }
if (-not $found) {
    Write-Output ('ERR ' + $t0.ToString([cultureinfo]::InvariantCulture))
    exit 2
}
Write-Output ('OK ' + $t0.ToString([cultureinfo]::InvariantCulture))
exit 0
"""


def _measure_startup_bandwidth(tmp_path: Path, project: Path) -> float:
    """t0 = launch -> first side effect, measured with the watchdog's own clock.

    The warm-up child is started exactly the way the supervisor starts a child
    (same PowerShell clock, same argv, same working directory, same redirects),
    probed every 5 ms for ``.source_catalog/fake_worker_count.txt``, then killed.
    The marker is deleted afterwards so the asserted run starts from the same
    clean state as before the change.
    """
    script = tmp_path / "tside_warmup_probe.ps1"
    script.write_text(_WARMUP_PROBE_PS1, encoding="utf-8")
    completed = subprocess.run(
        [
            "powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
            "Bypass", "-File", str(script),
            "-PythonExe", sys.executable,
            "-ProjectRoot", str(project),
            "-LogDir", str(tmp_path / "tside_warmup_logs"),
        ],
        cwd=str(project),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    lines = [line.strip() for line in (completed.stdout or "").splitlines() if line.strip()]
    line = lines[-1] if lines else ""
    if completed.returncode != 0 or not line.startswith("OK "):
        raise AssertionError(
            "startup-bandwidth warm-up failed: rc=%r stdout=%r stderr=%r"
            % (completed.returncode, (completed.stdout or "")[-400:],
               (completed.stderr or "")[-400:])
        )
    marker = project / ".source_catalog" / "fake_worker_count.txt"
    if marker.exists():
        marker.unlink()
    return float(line[3:].split()[0])


def _exported_hang_timeout(t0_seconds: float) -> float:
    """建议1 + semantic upper bound, both derived in oracle.md §2.1.

    lower: max(2.0, 4*t0) covers the worst tail the source card measured
           (2.486 s) as long as t0 >= 0.6215 s; every cpu8 sample was >= 0.642 s.
    upper: t0 + 3.0 keeps >= 2 s of margin before behaviour #1's 5 s sleep ends,
           because the watchdog MUST still fire (otherwise the node loses its
           ``child_unresponsive`` event and fails with StopIteration instead).
    """
    return min(max(2.0, 4.0 * t0_seconds), t0_seconds + 3.0)


def _record_timing_trace(node: str, t0_seconds: float, hang_timeout_seconds: float) -> None:
    """Optional evidence sink; the fix does not depend on it being set."""
    path = os.environ.get("CW_TSIDE_TRACE_FILE")
    if not path:
        return
    payload = {
        "node": node,
        "t0_seconds": round(t0_seconds, 4),
        "hang_timeout_seconds": round(hang_timeout_seconds, 4),
        "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\\n")
'''
# NOTE: the literal ``\\n`` above becomes a real backslash-n in the generated
# source, i.e. the JSONL separator written by _record_timing_trace.

# Anchors inside the node under test (must each appear exactly once) ----------
CALL_ANCHOR = """    completed = _run_real_worker_launcher(
        project,
        timeout=15,
        worker_hang_timeout_seconds=0.5,
        child_poll_milliseconds=100,
    )

    assert completed.returncode == 0, completed.stderr
    events = _launcher_events(project)
    unresponsive = next(
        event for event in events if event["status"] == "child_unresponsive"
    )"""

CALL_FIX = """    # I-14-E-TESTSIDE (oracle.md §2.1): derive -WorkerHangTimeoutSeconds from
    # this run's own measured startup bandwidth instead of a hard-coded 0.5 s.
    t0_seconds = _measure_startup_bandwidth(tmp_path, project)
    hang_timeout_seconds = _exported_hang_timeout(t0_seconds)
    _record_timing_trace("child_without_runtime", t0_seconds, hang_timeout_seconds)

    completed = _run_real_worker_launcher(
        project,
        timeout=15,
        worker_hang_timeout_seconds=hang_timeout_seconds,
        child_poll_milliseconds=100,
    )

    assert completed.returncode == 0, completed.stderr
    events = _launcher_events(project)
    unresponsive = next(
        event for event in events if event["status"] == "child_unresponsive"
    )"""

CALL_MUTANT = """    # I-14-E-TESTSIDE MUTATION M1 (oracle.md §3.E): the exported formula is
    # reverted to the hard-coded 0.5 s constant; everything else is unchanged.
    t0_seconds = _measure_startup_bandwidth(tmp_path, project)
    hang_timeout_seconds = 0.5
    _record_timing_trace("child_without_runtime", t0_seconds, hang_timeout_seconds)

    completed = _run_real_worker_launcher(
        project,
        timeout=15,
        worker_hang_timeout_seconds=hang_timeout_seconds,
        child_poll_milliseconds=100,
    )

    assert completed.returncode == 0, completed.stderr
    events = _launcher_events(project)
    unresponsive = next(
        event for event in events if event["status"] == "child_unresponsive"
    )"""


def _replace_once(text: str, old: str, new: str, what: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"anchor {what!r} found {count} times (expected exactly 1)")
    return text.replace(old, new, 1)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "fix"
    if mode == "revert":
        shutil.copyfile(ORIGINAL, TEST)
        print(f"reverted -> sha256={sha(TEST)}")
        return 0

    if not ORIGINAL.exists():
        shutil.copyfile(TEST, ORIGINAL)
        print(f"pristine original saved -> {ORIGINAL} sha256={sha(ORIGINAL)}")

    # The product test file is CRLF: read/write BYTES and translate every anchor
    # to the file's own newline so unchanged regions stay byte-identical.
    text = ORIGINAL.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"

    def nl(block: str) -> str:
        return block.replace("\n", newline)

    helpers = nl(HELPERS)
    tail = nl(HELPERS_ANCHOR_TAIL)
    text = _replace_once(text, tail, tail + helpers, "helper-insert")
    call = nl(CALL_MUTANT if mode == "mutate" else CALL_FIX)
    text = _replace_once(text, nl(CALL_ANCHOR), call, "call-site")
    TEST.write_bytes(text.encode("utf-8"))
    print(f"mode={mode} applied -> sha256={sha(TEST)} bytes={TEST.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
