"""Audit-only runner. Never calls provider, live catalog or worker commands."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4] / 'filing-fetch'
OUT = HERE / 'tests'
OUT.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
env.pop('FILING_FETCH_E2E_DOWNLOAD', None)
env.pop('FC805_REAL_DOWNLOAD', None)
env.pop('FILING_FETCH_LIVE', None)
commands = {
 'contracts': [sys.executable, '-B', '-m', 'pytest', '-p', 'no:cacheprovider', '-q', '-rA',
 'tests/test_fetch_filing.py', 'tests/test_latest_mode.py', 'tests/test_policy_containment_fc501.py',
 'tests/test_fc802_gap_orchestration.py', 'tests/test_bundle_compat.py', 'tests/test_bundle_fidelity.py',
 'tests/test_fc903_bundle_contract.py', 'tests/test_fc905b_envelope_fields.py',
 '-k', 'not test_cli_stdin_accepts_utf8_chinese_query', '--basetemp', str(OUT / 'pytest_tmp')],
 'plan_verifier': [sys.executable, '-B', 'tools/verify_plan_claims.py', '--plan', 'task_plan.md', '--progress', 'progress.md', '--json'],
}
for name, command in commands.items():
 started = datetime.datetime.now(datetime.timezone.utc).isoformat()
 done = subprocess.run(command, cwd=REPO, env=env, capture_output=True, timeout=120)
 (OUT / (name + '.stdout.txt')).write_bytes(done.stdout)
 (OUT / (name + '.stderr.txt')).write_bytes(done.stderr)
 result = dict(command=command, cwd=str(REPO), started=started, exit_code=done.returncode,
               stdout_sha256=hashlib.sha256(done.stdout).hexdigest(), stderr_sha256=hashlib.sha256(done.stderr).hexdigest())
 (OUT / (name + '.run.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
 print(name, done.returncode, done.stdout.decode('utf-8', errors='replace')[-600:])
