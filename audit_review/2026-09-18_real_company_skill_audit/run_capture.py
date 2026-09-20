"""Audit-only CLI recorder. Never changes a production implementation/config."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--cwd', default=str(ROOT.parents[1]))
    parser.add_argument('--timeout', type=float, default=180)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    command = [sys.executable if item == '{python}' else item for item in command]
    target = ROOT / 'runs' / args.name
    target.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    timed_out = False
    with (target / 'stdout.txt').open('wb') as out, (target / 'stderr.txt').open('wb') as err:
        process = subprocess.Popen(command, cwd=args.cwd, env=env, stdout=out, stderr=err)
        try:
            code = process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
            else:
                process.kill()
            code = process.wait()
    record = dict(command=command, cwd=args.cwd, started_utc=started,
                  duration_seconds=round(time.monotonic()-begin,3), exit_code=code,
                  timed_out=timed_out,
                  outputs={name: hashlib.sha256((target/name).read_bytes()).hexdigest()
                           for name in ['stdout.txt','stderr.txt']})
    (target / 'run.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False))
    for name in ['stdout.txt','stderr.txt']:
        content = (target/name).read_text(encoding='utf-8', errors='replace')
        print(name + ': ' + content[:8000])
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
