"""ZR-102 (phase C) — T1 hermetic three-process runner.

Builds a fully hermetic T1 environment and drives the REAL
revenue → filing → wiki subprocess chain against it:

* TEMPORARY roots — a temp copy of the company-wiki package + configs and a
  temp copy of the filing-fetch scripts live under one ``--work-dir``; the
  wiki ``companies`` / ``dayu`` / ``dropbox`` roots, the catalog, the staging
  area and the security master are all under that same temp dir.  The three
  subprocesses are the REAL code (revenue ``source_preparation.py`` /
  ``filing_fetch_client.py`` from the real revenue repo, ``fetch_filing.py``
  from the temp filing-fetch copy, the wiki CLI ``-m
  company_wiki.source_catalog.cli`` imported from the temp package copy).
* provider/LLM observed only at the boundary — ``config/source_acquisition.yaml``
  routes every market adapter to a generated spy executable; the CN
  ``json_command_v1`` spy logs every invocation (action/pid/argv/payload
  hash) to ``spies/spy.log`` and returns a deterministic candidate/receipt.
  ``COMPANY_WIKI_REAL_LLM=0`` + ``COMPANY_WIKI_NETWORK=blocked`` +
  ``PYTHON_DOTENV_DISABLED=1`` are injected into every chain subprocess;
  llm/parser counts come from the returned resolution envelopes (never
  fabricated).
* hop observation — a generated ``sitecustomize.py`` on ``PYTHONPATH`` logs
  every interpreter in the chain (pid + argv + argv hash + cwd) to
  ``hoplog/hops.jsonl`` so each hop's PID and argv are assertable.

Scenarios (frozen runbook §5):

  1 EXACT-REUSE          seeded capture-ready doc → reused handle,
                         download_calls=0, llm_calls=0, parser events 0.
  2 AUTHORIZED-DOWNLOAD  empty catalog + authorization → exactly one
                         provider DOWNLOAD (fetch), file under the temp
                         companies root, envelope download_events=1.
  3 SECOND-RUN IDEMPOTENCE rerun with the now-present file → reused,
                         provider download count stays 1.
  4 MISSING+UNAUTHORIZED gap, no authorization → fail closed: non-zero
                         exit, structured error, provider spy untouched.
  5 NEGATIVE-IDENTITY    mismatched-hash seed / wrong-entity request →
                         fail closed (no reuse, no download).
  6 GUARD                refuses to start (exit 2) when any resolved
                         root/config path escapes the temp work dir
                         (e.g. the real company-wiki / filing-fetch /
                         Dropbox / dayu paths).

Exit codes: 0 = every selected scenario PASSed; 1 = a scenario FAILed;
2 = guard refusal (scenario 6, or the internal guard tripped); 3 = runner
error.  A JSON summary is written to stdout (one object per scenario);
human progress goes to stderr.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

T1_DIR = Path(__file__).resolve().parent
REVENUE_ROOT = T1_DIR.parents[2]
PROJECTS_ROOT = REVENUE_ROOT.parent
WIKI_ROOT = PROJECTS_ROOT / "company-wiki"
FILING_ROOT = PROJECTS_ROOT / "filing-fetch"
WIKI_VENV_PY = WIKI_ROOT / ".venv" / "Scripts" / "python.exe"
REAL_DROPBOX = Path(os.environ.get("USERPROFILE") or "") / "Dropbox"
REAL_DAYU_AGENT = PROJECTS_ROOT / "dayu-agent"

# ---------------------------------------------------------------------------
# Frozen T1 fixture facts (ASCII-only on purpose; the whole chain runs UTF-8)
# ---------------------------------------------------------------------------

ENTITY = "Moutai Corp"
TICKER = "600519"
SECURITY_ID = "600519"
PDOC = "acc-2025-0001"
KIND = "annual_report"
FISCAL_YEAR = 2025
FILING_DATE = "2026-03-20"
AS_OF_DATE = "2026-12-31"
SOURCE_URL = "https://static.example.invalid/moutai/2025"
REVIEWER = "zr102-t1-runner"
SPY_NAME = "stockinfo-cninfo"
SPY_VERSION = "1.1.0"

BASE_REQUEST = {
    "schema_version": "1.2",
    "company_query": TICKER,
    "market": "CN",
    "document_kind": KIND,
    "as_of_date": AS_OF_DATE,
    "fiscal_year": FISCAL_YEAR,
}

S1_REQUEST = {
    **BASE_REQUEST,
    "mode": "exact",
    "provider": "cninfo",
    "provider_document_id": PDOC,
}

AUTHORIZATION = {
    "provider": "cninfo",
    "allowed_accessions": [PDOC],
    "max_items": 1,
    "max_bytes": 200000,
    "expires_at": "2030-01-01T00:00:00Z",
}

S2_REQUEST = {
    "schema_version": "1.2",
    "company_query": TICKER,
    "market": "CN",
    "document_kind": KIND,
    "as_of_date": AS_OF_DATE,
    "mode": "latest_as_of",
    "authorization": AUTHORIZATION,
}

S3_REQUEST = {**S1_REQUEST, "authorization": AUTHORIZATION}

# Wrong-entity request: identity resolves (master record exists) but no
# document exists for it.
S5B_REQUEST = {
    "schema_version": "1.2",
    "company_query": "600001",
    "market": "CN",
    "document_kind": KIND,
    "as_of_date": AS_OF_DATE,
    "fiscal_year": FISCAL_YEAR,
    "mode": "exact",
}

PDF_BODY = b"%PDF-1.7\nzr102-t1 provider spy downloaded bytes (CN annual report)\n"

POLICY_PAYLOAD = {
    "schema_version": "1.0",
    "flags": {
        "v2_scan_shadow": False,
        "v2_persist_assertions": False,
        "v2_resolve_shadow": False,
        "v2_resolve_active": False,
        "v2_bundle_active": False,
        "legacy_bridge_enabled": True,
    },
    "policy_hash": "a" * 64,
    "current_epoch": None,
    "active_cohorts": [],
    "updated_at": "2026-08-14T00:00:00Z",
}

# ---------------------------------------------------------------------------
# Generated-file templates (written into the temp work dir only)
# ---------------------------------------------------------------------------

SITECUSTOMIZE_TEMPLATE = """\
# ZR-102 T1 hop observer: logs every interpreter in the chain.
import hashlib
import json
import os
import sys


def _zr102_hop():
    try:
        path = os.environ.get("ZR102_HOP_LOG")
        if not path:
            return
        argv = list(sys.argv)
        argv_hash = hashlib.sha256(
            json.dumps(argv, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:16]
        entry = {
            "pid": os.getpid(),
            "ppid": getattr(os, "getppid", lambda: None)(),
            "argv": argv,
            "argv_hash": argv_hash,
            "cwd": os.getcwd(),
        }
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\\n")
    except Exception:
        pass


_zr102_hop()
"""

PROVIDER_SPY_TEMPLATE = '''\
"""ZR-102 T1 provider spy (json_command_v1) — generated into the temp work dir.

Speaks the wiki's json_command_v1 adapter protocol: ``discover`` returns one
deterministic candidate, ``fetch`` stages a fixed PDF into ``--staging-dir``
and returns its receipt.  Every invocation is appended to ZR102_SPY_LOG.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

NAME = {spy_name!r}
VERSION = {spy_version!r}
LOG = os.environ.get("ZR102_SPY_LOG") or ""
PDF_BODY = {pdf_body!r}
RETRIEVED_AT = "2026-07-18T12:00:00Z"
FILING_DATE = {filing_date!r}
PDOC = {pdoc!r}


def _log(action, payload, args):
    if not LOG:
        return
    try:
        entry = {{
            "action": action,
            "pid": os.getpid(),
            "cwd": os.getcwd(),
            "argv": list(args),
            "payload_sha256": hashlib.sha256(
                json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()[:16],
            "entity": payload.get("entity"),
            "market": payload.get("market"),
            "document_kind": payload.get("document_kind"),
            "fiscal_year": payload.get("fiscal_year"),
            "provider_document_id": payload.get("provider_document_id"),
        }}
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\\n")
    except Exception:
        pass


def _emit(obj, exit_code=0):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))
    sys.stdout.write("\\n")
    sys.stdout.flush()
    if exit_code:
        sys.exit(exit_code)


def _ok(extra):
    return {{
        "schema_version": "1.0",
        "status": "ok",
        "adapter": {{"name": NAME, "version": VERSION}},
        **extra,
    }}


def _fail(code, message):
    return {{
        "schema_version": "1.0",
        "status": "failed",
        "adapter": {{"name": NAME, "version": VERSION}},
        "error": {{"code": code, "retryable": False, "message": message}},
    }}


def main():
    args = sys.argv[1:]
    action = args[0] if args else ""
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {{}}
    _log(action, payload, args)
    if action == "discover":
        candidate = {{
            "candidate_id": "cninfo:" + PDOC,
            "provider": "cninfo",
            "provider_document_id": PDOC,
            "market": payload.get("market") or "CN",
            "title": "%s 2025 Annual Report" % (payload.get("entity") or "Unknown"),
            "source_url": {source_url!r},
            "document_kind": payload.get("document_kind") or "annual_report",
            "form_type": "annual_report",
            "filing_date": FILING_DATE,
            "fiscal_year": payload.get("fiscal_year") or 2025,
            "fiscal_period": "FY",
            "language": "zh-CN",
            "remote_size": len(PDF_BODY),
        }}
        _emit(_ok({{"candidates": [candidate]}}))
    elif action == "fetch":
        staging = None
        for i, item in enumerate(args):
            if item == "--staging-dir" and i + 1 < len(args):
                staging = Path(args[i + 1])
        if staging is None:
            _emit(_fail("staging_dir_missing", "no --staging-dir"), exit_code=1)
        staging.mkdir(parents=True, exist_ok=True)
        target = staging / "report.pdf"
        target.write_bytes(PDF_BODY)
        receipt = {{
            "candidate_id": payload.get("candidate_id"),
            "provider": payload.get("provider"),
            "provider_document_id": payload.get("provider_document_id"),
            "source_url": payload.get("source_url"),
            "staged_path": str(target),
            "content_sha256": hashlib.sha256(PDF_BODY).hexdigest(),
            "byte_size": len(PDF_BODY),
            "mime_type": "application/pdf",
            "retrieved_at": RETRIEVED_AT,
            "http_status": 200,
            "adapter_name": NAME,
            "adapter_version": VERSION,
        }}
        _emit(_ok({{"receipt": receipt}}))
    else:
        _emit(_fail("unknown_action", "action must be discover or fetch"), exit_code=1)


if __name__ == "__main__":
    main()
'''

DAYU_SPY_TEMPLATE = '''\
"""ZR-102 T1 dayu spy: refuses HK/US downloads (T1 is CN-only via the json spy)."""
import sys

sys.stderr.write(
    "zr102-t1 dayu spy: HK/US provider downloads are not part of the T1 CN "
    "scenarios; refusing instead of invoking any real dayu tooling.\\n"
)
sys.exit(1)
'''

SEED_MASTERS_TEMPLATE = '''\
"""ZR-102 T1: seed per-market security masters via the wiki SecurityMasterStore."""
import sys
from pathlib import Path

work = Path(sys.argv[1])
from company_wiki.source_catalog.security_identity import (
    SecurityMasterStore,
    SecurityRecord,
)

store = SecurityMasterStore(work / "wiki" / ".source_catalog" / "security_master")


def rec(market, name, ticker, sid, exchange, aliases=()):
    return SecurityRecord(
        canonical_name=name,
        market=market,
        exchange=exchange,
        ticker=ticker,
        security_id=sid,
        aliases=aliases,
        active=True,
        source_name="zr102-t1",
        source_url="https://example.invalid/master",
        source_record_id="rec-" + ticker,
        identifiers={},
    )


store.write_market(
    "CN",
    [
        rec("CN", "Moutai Corp", "600519", "600519", "SSE"),
        rec("CN", "OtherCorp", "600001", "600001", "SSE"),
    ],
    retrieved_at="2026-01-01",
    sources=("fixture",),
)
store.write_market(
    "HK",
    [rec("HK", "Sample HK Ltd", "00001", "00001", "SEHK")],
    retrieved_at="2026-01-01",
    sources=("fixture",),
)
store.write_market(
    "US",
    [rec("US", "Alphabet Inc.", "GOOGL", "GOOGL", "NASDAQ")],
    retrieved_at="2026-01-01",
    sources=("fixture",),
)
print("masters ok")
'''

SEED_REVIEW_TEMPLATE = '''\
"""ZR-102 T1: record prompt-injection review receipts via the CatalogStore API."""
import sys
from pathlib import Path

work = Path(sys.argv[1])
from company_wiki.source_catalog.config import load_catalog_config
from company_wiki.source_catalog.prompt_injection import (
    record_prompt_injection_review,
)
from company_wiki.source_catalog.service import SourceCatalog

cfg = load_catalog_config(work / "wiki" / "config" / "source_catalog.yaml")
catalog = SourceCatalog(cfg)
with catalog.store.transaction() as con:
    rows = con.execute(
        "SELECT document_id FROM documents WHERE source_status='active'"
    ).fetchall()
    for row in rows:
        record_prompt_injection_review(
            con,
            row[0],
            status="not_detected",
            reviewer="zr102-t1-runner",
            evidence_sha256="e" * 64,
            now="2026-08-14T00:00:00Z",
        )
print("reviewed %d" % len(rows))
'''


# ---------------------------------------------------------------------------
# Work-dir materialization
# ---------------------------------------------------------------------------


def _source_catalog_yaml(work: Path) -> str:
    return (
        "schema_version: '1.0'\n"
        'catalog_dir: "${PROJECT_ROOT}/.source_catalog"\n'
        "reusable_root_kinds: [company_raw, dayu_portfolio, directory]\n"
        "roots:\n"
        "  - root_id: company_raw\n"
        "    kind: company_raw\n"
        '    path: "${PROJECT_ROOT}/companies"\n'
        "    priority: 10\n"
        "  - root_id: dayu_portfolio\n"
        "    kind: dayu_portfolio\n"
        '    path: "${PROJECT_ROOT}/dayu/portfolio"\n'
        "    priority: 20\n"
        "  - root_id: dropbox_stock\n"
        "    kind: directory\n"
        '    path: "${PROJECT_ROOT}/dropbox/stock"\n'
        "    priority: 30\n"
    )


def _source_acquisition_yaml(work: Path) -> str:
    spy_cn = (work / "spies" / "provider_spy.py").as_posix()
    spy_dayu = (work / "spies" / "dayu_spy.py").as_posix()
    return (
        "schema_version: '1.1'\n"
        'staging_root: "${PROJECT_ROOT}/.source_catalog/staging"\n'
        "timeout_seconds: 300\n"
        "adapters:\n"
        "  cn:\n"
        "    name: 'stockinfo-cninfo'\n"
        "    version: '1.1.0'\n"
        "    interface: 'json_command_v1'\n"
        '    project_root: "${PROJECT_ROOT}/../spies"\n'
        "    config_root: null\n"
        f'    command: ["${{PYTHON_EXECUTABLE}}", "{spy_cn}"]\n'
        "  hk:\n"
        "    name: 'dayu-hkex-cli'\n"
        "    version: '1.0.0'\n"
        "    interface: 'dayu_cli_v1'\n"
        '    project_root: "${PROJECT_ROOT}/../spies"\n'
        '    config_root: "${PROJECT_ROOT}/../spies"\n'
        f'    command: ["${{PYTHON_EXECUTABLE}}", "{spy_dayu}"]\n'
        "  us:\n"
        "    name: 'dayu-sec-cli'\n"
        "    version: '1.0.0'\n"
        "    interface: 'dayu_cli_v1'\n"
        '    project_root: "${PROJECT_ROOT}/../spies"\n'
        '    config_root: "${PROJECT_ROOT}/../spies"\n'
        f'    command: ["${{PYTHON_EXECUTABLE}}", "{spy_dayu}"]\n'
    )


def _provider_spy_source() -> str:
    return PROVIDER_SPY_TEMPLATE.format(
        spy_name=SPY_NAME,
        spy_version=SPY_VERSION,
        pdf_body=PDF_BODY,
        filing_date=FILING_DATE,
        pdoc=PDOC,
        source_url=SOURCE_URL,
    )


def materialize_workdir(work: Path) -> None:
    """Create the temp wiki root (package copy + configs), the temp
    filing-fetch copy, the spies, the hop observer and the temp roots."""
    work = Path(work)
    wiki = work / "wiki"
    if wiki.exists():
        shutil.rmtree(wiki)
    if (work / "filing-fetch").exists():
        shutil.rmtree(work / "filing-fetch")
    shutil.copytree(
        WIKI_ROOT / "src" / "company_wiki",
        wiki / "src" / "company_wiki",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    (wiki / "config").mkdir(parents=True, exist_ok=True)
    (wiki / "config" / "source_catalog.yaml").write_text(
        _source_catalog_yaml(work), encoding="utf-8"
    )
    (wiki / "config" / "source_acquisition.yaml").write_text(
        _source_acquisition_yaml(work), encoding="utf-8"
    )
    shutil.copy2(
        WIKI_ROOT / "config" / "source_catalog_worker.yaml",
        wiki / "config" / "source_catalog_worker.yaml",
    )
    for sub in ("companies", "dayu/portfolio", "dropbox/stock"):
        (wiki / sub).mkdir(parents=True, exist_ok=True)

    shutil.copytree(FILING_ROOT / "scripts", work / "filing-fetch" / "scripts")
    shutil.copytree(FILING_ROOT / "config", work / "filing-fetch" / "config")

    (work / "filing_config.json").write_text(
        json.dumps(
            {"schema_version": "1.0", "company_wiki_root": str(wiki)},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    (work / "spies").mkdir(parents=True, exist_ok=True)
    (work / "spies" / "provider_spy.py").write_text(
        _provider_spy_source(), encoding="utf-8"
    )
    (work / "spies" / "dayu_spy.py").write_text(DAYU_SPY_TEMPLATE, encoding="utf-8")
    (work / "hoplog").mkdir(parents=True, exist_ok=True)
    (work / "hoplog" / "sitecustomize.py").write_text(
        SITECUSTOMIZE_TEMPLATE, encoding="utf-8"
    )
    (work / "seed_masters.py").write_text(SEED_MASTERS_TEMPLATE, encoding="utf-8")
    (work / "seed_review.py").write_text(SEED_REVIEW_TEMPLATE, encoding="utf-8")


def seed_companies(work: Path, *, good: bool) -> None:
    """Write the temp companies-root seed (pdf + acquisition sidecar)."""
    raw = work / "wiki" / "companies" / ENTITY / "raw" / "financial_reports" / "annual"
    raw.mkdir(parents=True, exist_ok=True)
    pdf = raw / "2025_annual.pdf"
    pdf.write_bytes(PDF_BODY)
    sha = hashlib.sha256(PDF_BODY).hexdigest()
    sidecar = {
        "market": "CN",
        "security_id": SECURITY_ID,
        "source_title": "%s %d Annual Report" % (ENTITY, FISCAL_YEAR),
        "fiscal_year": FISCAL_YEAR,
        "filing_date": FILING_DATE,
        "form_type": KIND,
        "document_kind": KIND,
        "provider": "cninfo",
        "provider_document_id": PDOC,
        "source_url": SOURCE_URL,
        "retrieved_at": "2026-07-18T00:00:00Z",
        # A poisoned (hash-mismatch) seed makes the scanner quarantine the
        # location: the document is never offered for reuse (fail closed).
        "content_sha256": sha if good else "0" * 64,
    }
    (raw / "2025_annual.pdf.source.json").write_text(
        json.dumps(sidecar, ensure_ascii=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Guard: every resolved root/config path must stay inside the temp work dir
# ---------------------------------------------------------------------------


def collect_config_paths(work: Path) -> dict[str, Path]:
    """The resolved data-root/config paths the chain will touch.  The
    interpreter (WIKI_VENV_PY) and the revenue code root are deliberately not
    data roots/configs and are excluded from the containment check."""
    wiki = work / "wiki"
    paths: dict[str, Path] = {
        "company_wiki_root": wiki,
        "catalog_dir": wiki / ".source_catalog",
        "staging_root": wiki / ".source_catalog" / "staging",
        "filing_fetch_root": work / "filing-fetch",
        "security_master": wiki / ".source_catalog" / "security_master",
        "runtime_policy": wiki / ".source_catalog" / "runtime_policy.json",
        "root_company_raw": wiki / "companies",
        "root_dayu_portfolio": wiki / "dayu" / "portfolio",
        "root_dropbox_stock": wiki / "dropbox" / "stock",
        "spies": work / "spies",
        "hoplog": work / "hoplog",
    }
    for label in ("cn", "hk", "us"):
        paths[f"adapter_{label}_project_root"] = work / "spies"
        paths[f"adapter_{label}_config_root"] = work / "spies"
    return paths


def validate_hermetic(work: Path, paths: dict[str, Path]) -> list[str]:
    """Return a list of violations; empty list == hermetic."""
    base = Path(work).resolve()
    violations: list[str] = []
    for label, raw in sorted(paths.items()):
        path = Path(raw)
        try:
            resolved = path.expanduser().resolve(strict=False)
        except (OSError, ValueError) as exc:
            violations.append(f"{label}: cannot resolve {path}: {exc}")
            continue
        try:
            resolved.relative_to(base)
        except ValueError:
            violations.append(f"{label} escapes the temp work dir: {resolved}")
    return violations


def assert_hermetic(work: Path) -> None:
    violations = validate_hermetic(work, collect_config_paths(work))
    if violations:
        _die_guard(
            "refusing to start: resolved root/config path escapes the temp "
            "work dir:\n  " + "\n  ".join(violations)
        )


# ---------------------------------------------------------------------------
# Environment + subprocess helpers
# ---------------------------------------------------------------------------

_LINT_ENV_KEYS = (
    "DEEPSEEK_API_KEY",
    "MINIMAX_API_KEY",
    "MIMO_API_KEY",
    "TAVILY_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)


def chain_env(work: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(work / "hoplog"), str(work / "wiki" / "src")]
    )
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env["COMPANY_WIKI_REAL_LLM"] = "0"
    env["COMPANY_WIKI_NETWORK"] = "blocked"
    env["PYTHON_DOTENV_DISABLED"] = "1"
    env["ZR102_HOP_LOG"] = str(work / "hoplog" / "hops.jsonl")
    env["ZR102_SPY_LOG"] = str(work / "spies" / "spy.log")
    for key in _LINT_ENV_KEYS:
        env.pop(key, None)
    return env


def _run(cmd, *, cwd, env, inp=None, timeout=120):
    return subprocess.run(
        list(map(str, cmd)),
        input=inp,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=timeout,
        cwd=str(cwd),
        env=env,
        check=False,
    )


def run_wiki_cli(
    work: Path, *args: str, timeout: float = 180
) -> subprocess.CompletedProcess:
    cmd = [
        str(WIKI_VENV_PY),
        "-B",
        "-m",
        "company_wiki.source_catalog.cli",
        "--config",
        str(work / "wiki" / "config" / "source_catalog.yaml"),
        *args,
    ]
    return _run(cmd, cwd=work / "wiki", env=chain_env(work), timeout=timeout)


def run_seed_script(work: Path, name: str) -> None:
    proc = _run(
        [str(WIKI_VENV_PY), "-B", str(work / name), str(work)],
        cwd=work,
        env=chain_env(work),
        timeout=120,
    )
    if proc.returncode != 0:
        raise T1RunnerError(f"{name} failed: {proc.stderr[-800:]}")


def run_chain(
    work: Path,
    request: dict,
    *,
    entry: str,
    allow_download: bool,
    timeout_seconds: float = 240,
    reset_observation: bool = True,
) -> subprocess.CompletedProcess:
    """Run the REAL three-process chain.  ``entry`` selects the revenue-hop
    script: ``source_preparation`` (full revenue entry, emits a
    RevenueSourceRecord) or ``filing_client`` (the revenue filing client,
    emits the capture-ready handle directly).  ``reset_observation`` clears
    the hop/spy logs first; scenario 3 keeps them so the cumulative provider
    download count is assertable across runs."""
    if reset_observation:
        (work / "hoplog" / "hops.jsonl").unlink(missing_ok=True)
        (work / "spies" / "spy.log").unlink(missing_ok=True)
    if entry == "source_preparation":
        cmd = [
            str(WIKI_VENV_PY),
            "-B",
            str(REVENUE_ROOT / "scripts" / "source_preparation.py"),
            "--company-wiki-config",
            str(work / "filing_config.json"),
            "--filing-fetch-root",
            str(work / "filing-fetch"),
        ]
    elif entry == "filing_client":
        cmd = [
            str(WIKI_VENV_PY),
            "-B",
            str(REVENUE_ROOT / "scripts" / "filing_fetch_client.py"),
            "--filing-fetch-root",
            str(work / "filing-fetch"),
            "--company-wiki-config",
            str(work / "filing_config.json"),
        ]
    else:
        raise T1RunnerError(f"unknown chain entry: {entry}")
    if allow_download:
        cmd.append("--allow-download")
    cmd.extend(["--timeout-seconds", str(timeout_seconds)])
    return _run(
        cmd,
        cwd=REVENUE_ROOT,
        env=chain_env(work),
        inp=json.dumps(request, ensure_ascii=False),
        timeout=timeout_seconds + 60,
    )


# ---------------------------------------------------------------------------
# Observation readers
# ---------------------------------------------------------------------------


def read_hops(work: Path) -> list[dict]:
    path = work / "hoplog" / "hops.jsonl"
    if not path.is_file():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def classify_hops(hops: list[dict], work: Path) -> dict[str, list[dict]]:
    """Classify hop entries by argv content and cwd.  Note: CPython rewrites
    ``sys.argv`` to ``["-m", ...]`` (dropping the interpreter and the module
    name) before sitecustomize runs for ``-m`` invocations, so the wiki CLI
    hops are recognised by their cwd (<work>/wiki) and ``--config
    .../source_catalog.yaml`` instead of the module name."""
    work = Path(work).resolve()
    wiki_cwd = str((work / "wiki").resolve()).replace("\\", "/").lower()
    roles: dict[str, list[dict]] = {}
    for hop in hops:
        joined = " ".join(hop.get("argv") or [])
        cwd = str(hop.get("cwd") or "").replace("\\", "/").lower()
        if "provider_spy.py" in joined:
            role = "provider-spy"
        elif "dayu_spy.py" in joined:
            role = "dayu-spy"
        elif "source_preparation.py" in joined:
            role = "revenue-entry"
        elif "filing_fetch_client.py" in joined:
            role = "filing-client"
        elif "fetch_filing.py" in joined:
            role = "filing"
        elif cwd == wiki_cwd and "source_catalog.yaml" in joined:
            role = "wiki"
        else:
            role = "other"
        roles.setdefault(role, []).append(hop)
    return roles


def read_spy(work: Path) -> list[dict]:
    path = work / "spies" / "spy.log"
    if not path.is_file():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def hop_assertion(work: Path) -> tuple[list[int], dict]:
    """Return (boundary pids, hop breakdown); raises when the three
    boundaries did not execute with distinct PIDs and argv hashes."""
    hops = read_hops(work)
    roles = classify_hops(hops, work)
    for required in ("filing-client", "filing", "wiki"):
        if not roles.get(required):
            raise T1ScenarioError(
                f"chain boundary {required!r} did not execute "
                f"(roles seen: {sorted(roles)})"
            )
    pids: list[int] = []
    for required in ("filing-client", "filing", "wiki"):
        first = roles[required][0]
        if not first.get("pid"):
            raise T1ScenarioError(f"{required} hop missing pid")
        if not first.get("argv_hash"):
            raise T1ScenarioError(f"{required} hop missing argv hash")
        pids.append(int(first["pid"]))
    if len(set(pids)) != 3:
        raise T1ScenarioError(f"chain boundary pids are not distinct: {pids}")
    breakdown = {
        role: [{"pid": h.get("pid"), "argv_hash": h.get("argv_hash")} for h in hs]
        for role, hs in sorted(roles.items())
    }
    return pids, breakdown


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------


class T1RunnerError(RuntimeError):
    pass


class T1ScenarioError(RuntimeError):
    pass


def _fail(exc: Exception) -> dict:
    return {"error": type(exc).__name__, "message": str(exc)}


def _summary(scenario: int, **fields) -> dict:
    return {"scenario": scenario, "outcome": "PASS", **fields}


def _boundaries(work: Path) -> tuple[list[int], dict]:
    return hop_assertion(work)


def _chain_files(work: Path) -> list[str]:
    companies = work / "wiki" / "companies"
    if not companies.is_dir():
        return []
    return sorted(
        str(p.relative_to(companies)) for p in companies.rglob("*") if p.is_file()
    )


def _spy_counts(work: Path) -> tuple[int, int, list[str]]:
    entries = read_spy(work)
    fetch = sum(1 for e in entries if e.get("action") == "fetch")
    actions = [e.get("action") for e in entries]
    return len(entries), fetch, actions


def scenario_1(work: Path, timeout: float) -> dict:
    materialize_workdir(work)
    assert_hermetic(work)
    seed_companies(work, good=True)
    run_seed_script(work, "seed_masters.py")
    if run_wiki_cli(work, "scan", timeout=timeout).returncode != 0:
        raise T1ScenarioError("temp catalog scan failed")
    run_seed_script(work, "seed_review.py")
    (work / "policy_payload.json").write_text(
        json.dumps(POLICY_PAYLOAD), encoding="utf-8"
    )
    if (
        run_wiki_cli(
            work,
            "runtime-policy",
            "apply",
            "--file",
            str(work / "policy_payload.json"),
            timeout=timeout,
        ).returncode
        != 0
    ):
        raise T1ScenarioError("runtime-policy apply failed")

    proc = run_chain(work, S1_REQUEST, entry="source_preparation", allow_download=False)
    details: dict = {
        "chain_exit": proc.returncode,
        "request": S1_REQUEST,
        "stderr_tail": proc.stderr[-600:],
    }
    if proc.returncode != 0:
        raise T1ScenarioError(f"exact-reuse chain exited {proc.returncode}")
    record = json.loads(proc.stdout)
    receipt = record.get("reuse_receipt") or {}
    details["reuse_receipt"] = receipt
    details["canonical_path"] = (record.get("company_wiki_trace") or {}).get(
        "canonical_path"
    )
    if receipt.get("download_calls") != 0:
        raise T1ScenarioError(f"download_calls != 0: {receipt.get('download_calls')}")
    if receipt.get("llm_calls") != 0:
        raise T1ScenarioError(f"llm_calls != 0: {receipt.get('llm_calls')}")
    if receipt.get("parser_calls") != 0:
        raise T1ScenarioError(f"parser_calls != 0: {receipt.get('parser_calls')}")
    if receipt.get("outcome") != "reused_existing":
        raise T1ScenarioError(f"outcome != reused_existing: {receipt.get('outcome')}")
    if receipt.get("prompt_injection_status") != "not_detected":
        raise T1ScenarioError(
            f"prompt_injection_status: {receipt.get('prompt_injection_status')}"
        )
    canonical = details["canonical_path"] or ""
    if not str(Path(canonical).resolve()).startswith(
        str((work / "wiki" / "companies").resolve())
    ):
        raise T1ScenarioError(
            f"canonical path outside temp companies root: {canonical}"
        )
    total, fetch, actions = _spy_counts(work)
    if total != 0:
        raise T1ScenarioError(f"provider spy invoked on reuse path: {actions}")
    pids, hops = _boundaries(work)
    return _summary(
        1,
        download_calls=receipt.get("download_calls"),
        llm_calls=receipt.get("llm_calls"),
        parser_calls=receipt.get("parser_calls"),
        provider_invocations=total,
        pids=pids,
        details=details,
        hop_breakdown=hops,
    )


def scenario_2(work: Path, timeout: float) -> dict:
    """AUTHORIZED-DOWNLOAD (latest_as_of → close-gap).  The runner drives the
    revenue filing client so the capture-ready handle + resolution envelope
    are directly assertable; the runner then records the prompt-injection
    review for the downloaded document so scenario 3 can pass the revenue
    policy gate (the chain itself never fabricates a review)."""
    materialize_workdir(work)
    assert_hermetic(work)
    run_seed_script(work, "seed_masters.py")
    if run_wiki_cli(work, "scan", timeout=timeout).returncode != 0:
        raise T1ScenarioError("temp catalog scan failed (empty roots)")
    (work / "policy_payload.json").write_text(
        json.dumps(POLICY_PAYLOAD), encoding="utf-8"
    )
    if (
        run_wiki_cli(
            work,
            "runtime-policy",
            "apply",
            "--file",
            str(work / "policy_payload.json"),
            timeout=timeout,
        ).returncode
        != 0
    ):
        raise T1ScenarioError("runtime-policy apply failed")

    proc = run_chain(
        work,
        S2_REQUEST,
        entry="filing_client",
        allow_download=True,
        timeout_seconds=timeout,
    )
    details: dict = {
        "chain_exit": proc.returncode,
        "request": S2_REQUEST,
        "stderr_tail": proc.stderr[-600:],
    }
    if proc.returncode != 0:
        raise T1ScenarioError(f"authorized-download chain exited {proc.returncode}")
    handle = json.loads(proc.stdout)
    envelope = handle.get("resolution_envelope") or {}
    details["handle"] = {
        k: handle.get(k)
        for k in ("capture_ready", "canonical_path", "provider", "provider_document_id")
    }
    details["envelope"] = envelope
    if handle.get("capture_ready") is not True:
        raise T1ScenarioError("handle is not capture_ready")
    if envelope.get("download_events") != 1:
        raise T1ScenarioError(
            f"download_events != 1: {envelope.get('download_events')}"
        )
    if envelope.get("outcome") != "downloaded_new":
        raise T1ScenarioError(f"outcome != downloaded_new: {envelope.get('outcome')}")
    if envelope.get("llm_calls") != 0:
        raise T1ScenarioError(f"llm_calls != 0: {envelope.get('llm_calls')}")
    total, fetch, actions = _spy_counts(work)
    if fetch != 1:
        raise T1ScenarioError(
            f"provider DOWNLOAD invocations != 1: {fetch} (actions={actions})"
        )
    canonical = str(handle.get("canonical_path") or "")
    if not canonical.startswith(str((work / "wiki" / "companies").resolve())):
        raise T1ScenarioError(
            f"downloaded file outside temp companies root: {canonical}"
        )
    files = _chain_files(work)
    if not any("raw" in f and "annual" in f for f in files):
        raise T1ScenarioError(f"no annual file under temp companies root: {files}")
    pids, hops = _boundaries(work)
    if not hops.get("provider-spy"):
        raise T1ScenarioError("provider boundary (spy) did not execute")

    # runner acts as the reviewer for the freshly downloaded document
    run_seed_script(work, "seed_review.py")
    return _summary(
        2,
        download_calls=fetch,
        llm_calls=envelope.get("llm_calls"),
        provider_invocations=total,
        provider_action_breakdown=actions,
        pids=pids,
        details=details,
        hop_breakdown=hops,
    )


def scenario_3(work: Path, timeout: float) -> dict:
    """SECOND-RUN IDEMPOTENCE: reuses the scenario-2 work dir (the file is
    now present).  Full revenue entry must produce a RevenueSourceRecord
    with zero downloads for THIS run and the provider download count must
    stay at 1 across the two runs."""
    before_total, before_fetch, _ = _spy_counts(work)
    proc = run_chain(
        work,
        S3_REQUEST,
        entry="source_preparation",
        allow_download=True,
        timeout_seconds=timeout,
        reset_observation=False,
    )
    details: dict = {
        "chain_exit": proc.returncode,
        "request": S3_REQUEST,
        "before_spy_total": before_total,
        "before_spy_fetch": before_fetch,
        "stderr_tail": proc.stderr[-600:],
    }
    if proc.returncode != 0:
        raise T1ScenarioError(f"idempotence rerun exited {proc.returncode}")
    record = json.loads(proc.stdout)
    receipt = record.get("reuse_receipt") or {}
    details["reuse_receipt"] = receipt
    if receipt.get("download_calls") != 0:
        raise T1ScenarioError(
            f"rerun reported downloads: {receipt.get('download_calls')}"
        )
    if receipt.get("llm_calls") != 0:
        raise T1ScenarioError(f"rerun llm_calls != 0: {receipt.get('llm_calls')}")
    if receipt.get("outcome") != "reused_existing":
        raise T1ScenarioError(f"rerun outcome: {receipt.get('outcome')}")
    after_total, after_fetch, actions = _spy_counts(work)
    details["after_spy_total"] = after_total
    details["after_spy_fetch"] = after_fetch
    if after_fetch != 1 or after_fetch != before_fetch:
        raise T1ScenarioError(
            f"second download observed: fetch {before_fetch} -> {after_fetch}"
        )
    pids, hops = _boundaries(work)
    return _summary(
        3,
        download_calls=receipt.get("download_calls"),
        llm_calls=receipt.get("llm_calls"),
        provider_invocations=after_total,
        provider_fetch=after_fetch,
        pids=pids,
        details=details,
        hop_breakdown=hops,
    )


def scenario_5(work: Path, timeout: float) -> dict:
    """NEGATIVE-IDENTITY: (a) a seeded document whose sidecar hash does not
    match its bytes is quarantined by the scanner and never reused; (b) a
    request for a different (valid) identity with no document fails closed.
    Both run without download authorization: the chain must fail closed and
    the provider spy must stay untouched.  The seeded poisoned file itself
    stays under the temp companies root (it is the fixture); nothing new may
    appear."""
    materialize_workdir(work)
    assert_hermetic(work)
    run_seed_script(work, "seed_masters.py")
    seed_companies(work, good=False)  # poisoned: content_sha256 mismatch
    if run_wiki_cli(work, "scan", timeout=timeout).returncode != 0:
        raise T1ScenarioError("temp catalog scan failed (poisoned seed)")
    seeded_files = _chain_files(work)
    if not seeded_files:
        raise T1ScenarioError("poisoned seed produced no indexed files")

    vectors: list[dict] = []
    for label, request in (
        ("hash_mismatch", S1_REQUEST),
        ("wrong_entity", S5B_REQUEST),
    ):
        proc = run_chain(
            work,
            request,
            entry="source_preparation",
            allow_download=False,
            timeout_seconds=timeout,
        )
        details: dict = {
            "vector": label,
            "chain_exit": proc.returncode,
            "stderr_tail": proc.stderr[-500:],
        }
        if proc.returncode == 0:
            raise T1ScenarioError(f"vector {label}: chain succeeded (must fail closed)")
        total, fetch, actions = _spy_counts(work)
        if total != 0:
            raise T1ScenarioError(
                f"vector {label}: provider spy invoked on fail-closed path: {actions}"
            )
        if _chain_files(work) != seeded_files:
            raise T1ScenarioError(
                f"vector {label}: files under temp companies root changed"
            )
        details["provider_invocations"] = total
        vectors.append(details)
    pids, hops = _boundaries(work)
    return _summary(
        5,
        download_calls=0,
        llm_calls=0,
        provider_invocations=0,
        pids=pids,
        details={"vectors": vectors, "requests": [S1_REQUEST, S5B_REQUEST]},
        hop_breakdown=hops,
    )


def scenario_4(work: Path, timeout: float) -> dict:
    """MISSING+UNAUTHORIZED: empty catalog, no download authorization →
    the chain fails closed (non-zero exit, structured not_found) and the
    provider spy is never invoked."""
    materialize_workdir(work)
    assert_hermetic(work)
    run_seed_script(work, "seed_masters.py")
    if run_wiki_cli(work, "scan", timeout=timeout).returncode != 0:
        raise T1ScenarioError("temp catalog scan failed (empty roots)")
    proc = run_chain(
        work,
        S1_REQUEST,
        entry="source_preparation",
        allow_download=False,
        timeout_seconds=timeout,
    )
    details: dict = {
        "chain_exit": proc.returncode,
        "request": S1_REQUEST,
        "stderr_tail": proc.stderr[-600:],
    }
    if "not_found" not in proc.stderr and "not_found" not in proc.stdout:
        raise T1ScenarioError(
            f"missing structured not_found error: {proc.stderr[-300:]}"
        )
    total, fetch, actions = _spy_counts(work)
    if total != 0:
        raise T1ScenarioError(f"provider spy invoked on unauthorized path: {actions}")
    if _chain_files(work):
        raise T1ScenarioError("unexpected files under temp companies root")
    pids, hops = _boundaries(work)
    return _summary(
        4,
        download_calls=0,
        llm_calls=0,
        provider_invocations=0,
        chain_exit=proc.returncode,
        pids=pids,
        details=details,
        hop_breakdown=hops,
    )


def scenario_6(work: Path) -> int:
    """GUARD: construct a config set pointing at the REAL company-wiki /
    filing-fetch / Dropbox / dayu paths and verify the runner refuses to
    start (exit 2 with a clear message)."""
    real = {
        "company_wiki_root": WIKI_ROOT,
        "catalog_dir": WIKI_ROOT / ".source_catalog",
        "staging_root": WIKI_ROOT / ".source_catalog" / "staging",
        "filing_fetch_root": FILING_ROOT,
        "security_master": WIKI_ROOT / ".source_catalog" / "security_master",
        "runtime_policy": WIKI_ROOT / ".source_catalog" / "runtime_policy.json",
        "root_company_raw": WIKI_ROOT / "companies",
        "root_dayu_portfolio": REAL_DAYU_AGENT / "workspace" / "portfolio",
        "root_dropbox_stock": REAL_DROPBOX / "Stock",
        "spies": REAL_DAYU_AGENT / "workspace" / "config",
        "hoplog": work,
    }
    for label in ("cn", "hk", "us"):
        real[f"adapter_{label}_project_root"] = (
            PROJECTS_ROOT / "StockInfoDLSimple" / "v2-clean-rewrite"
        )
        real[f"adapter_{label}_config_root"] = REAL_DAYU_AGENT / "workspace" / "config"
    violations = validate_hermetic(work, real)
    if not violations:
        raise T1ScenarioError("guard accepted real paths (must refuse)")
    _die_guard(
        "guard refused to start: resolved root/config path escapes the temp "
        "work dir:\n  " + "\n  ".join(violations)
    )
    return 2  # unreachable; _die_guard exits


def _die_guard(message: str) -> None:
    sys.stderr.write(message + "\n")
    sys.stdout.write(
        json.dumps(
            {"scenario": 6, "outcome": "GUARD_REFUSED", "message": message},
            ensure_ascii=False,
        )
        + "\n"
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="zr102_t1_runner",
        description=(
            "ZR-102 T1 hermetic three-process runner: real revenue → filing → "
            "wiki chain against temporary roots with provider/LLM spied at the "
            "boundary."
        ),
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=None,
        help="temp work dir (created when omitted; never deleted)",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        help="scenario to run (1..6); repeatable; default: 1 2 3 4 5",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=240.0,
        help="per-chain timeout (default 240)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    # The runner may be invoked from a UTF-8-reading parent (pytest) on a
    # GBK-locale Windows console; force UTF-8 stdio so paths never corrupt.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    work = args.work_dir
    if work is None:
        work = Path(tempfile.mkdtemp(prefix="zr102-t1-"))
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)

    if args.scenario:
        selected = []
        for item in args.scenario:
            for token in item.split(","):
                token = token.strip()
                if not token:
                    continue
                if token not in {"1", "2", "3", "4", "5", "6"}:
                    sys.stderr.write(f"unknown scenario: {token}\n")
                    return 3
                selected.append(int(token))
        selected = sorted(set(selected))
    else:
        selected = [1, 2, 3, 4, 5]

    summaries: list[dict] = []
    failed: list[int] = []
    s23_work: Path | None = None
    for scenario in selected:
        label = f"scenario_{scenario}"
        if scenario == 6:
            # guard: refuses via _die_guard (exit 2); kept here so --scenario 6
            # is the observable refusal and "all" skips it.
            scenario_6(work)
            continue
        if scenario == 2:
            # scenario 2 and 3 share one work dir (the downloaded file is the
            # idempotence fixture); run 2 exactly once even when 3 follows.
            if s23_work is None:
                s23_work = work / "s2"
            scenario_work = s23_work
        elif scenario == 3:
            if s23_work is None:
                sys.stderr.write(
                    "scenario 3 requires scenario 2's work dir; running 2 then 3\n"
                )
                s23_work = work / "s2"
            scenario_work = s23_work
        else:
            scenario_work = work / f"s{scenario}"
        try:
            summaries.append(
                {
                    "scenario": scenario,
                    **(globals()[label](scenario_work, args.timeout_seconds) or {}),
                }
            )
        except (T1ScenarioError, T1RunnerError) as exc:
            failed.append(scenario)
            summaries.append(
                {
                    "scenario": scenario,
                    "outcome": "FAIL",
                    "download_calls": None,
                    "llm_calls": None,
                    "pids": [],
                    "details": _fail(exc),
                }
            )
        except Exception as exc:  # noqa: BLE001 — keep the gate informative
            failed.append(scenario)
            summaries.append(
                {
                    "scenario": scenario,
                    "outcome": "ERROR",
                    "download_calls": None,
                    "llm_calls": None,
                    "pids": [],
                    "details": _fail(exc),
                }
            )

    sys.stdout.write(json.dumps(summaries, ensure_ascii=False, indent=2) + "\n")
    sys.stderr.write(f"work dir: {work}\n")
    if failed:
        sys.stderr.write(f"FAILED scenarios: {sorted(failed)}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
