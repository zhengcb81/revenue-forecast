"""Hermetic upstream CLI for I-02-B (network-disabled provider boundary).

This shim stands in for the filing-fetch skill's ``fetch_filing.py`` entry in
the local test chain ONLY (A/samples/upstream_root/scripts/fetch_filing.py is
bind-copied from this file).  It never touches network or provider: every
payload below is a fixed structure replay, derived from the original
CN-403 failure document in
audit_review/2026-09-18_real_company_skill_audit/runs/12_zijin_h1_download_authorized/stderr.txt.

Case selection comes from env W02B_CASE (filing-fatch's own client argv cannot
carry extra flags without inventing product CLI shapes).

- Direct cases (n1_long / n2_unknown / n2_string / n2_malformed): emit a
  fixed provider error document and a fixed exit code.  This models the
  adapter/provider boundary straight above the RF client.
- Deep cases (p1_cw / n3 / n4a / n4b / exit_probe): spawn the REAL deep-layer
  runner (A/scripts/w02b_cw_ensure_runner.py under the attempt venv) as a
  subprocess, forward its stderr VERBATIM (structured forwarding posture per
  decision.md; the product FF implementation is I-04's owner scope), and
  mirror its exit code.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
# bind copy lives at A/samples/upstream_root/scripts/: HERE = ...,/scripts,
# parents[2] = A (attempt root).
ATTEMPT = HERE.parents[2]
RUNNER = ATTEMPT / "scripts" / "w02b_cw_ensure_runner.py"
SCRATCH_ENV = "W02B_SCRATCH"

CN403_REPLAY = {
    "schema_version": "1.0",
    "status": "failed",
    "adapter": {"name": "stockinfo-cninfo", "version": "1.1.0"},
    "error": {
        "code": "upstream_unavailable",
        "message": (
            "cninfo_api_discover failed: client_error: API client error "
            "(HTTP 403): Forbidden"
        ),
        "retryable": True,
        "type": "AdapterError",
    },
}

_LONG_CN_MESSAGE = (
    "外层披露存在多版本重述冲突：2025年第三季度报告中的营业收入与经审计的年度报表存在"
    "约1.2亿元的口径差异，涉及存货跌价准备转回时点、合同履约进度确认方法以及关联方采购价"
    "格公允性认定；监管问询函要求补充分季度收入确认明细、按客户唯一识别码归并的前五大债"
    "务人余额、与其披露的前五名供应商交叉核对的证据链，同时补充披露滚动预期信用损失模型"
    "的关键假设变化对期后回款比例的影响，以及在建工程转固时点与折旧政策变更对四季度毛利"
    "率环比波动的影响；发行人需在此后十个工作日内提交由具有证券期货业务资格的会计师事务所"
    "出具的专项核查意见，并就商誉减值测试中现金流预测所采用的折现率区间、永续增长率假设与"
    "可比公司选取口径提供可复核的工作底稿索引，任一项逾期未交都将触发再融资申请材料退回流"
    "程并同步在发行监管动态中公开披露。"
)
_NESTED_CAUSE_DIRECT = {
    "schema_version": "1.0",
    "status": "failed",
    "adapter": {"name": "fake-cninfo", "version": "1.1.0"},
    "error": {
        "code": "upstream_unavailable",
        "message": _LONG_CN_MESSAGE,
        "retryable": True,
        "type": "AdapterError",
        "cause_chain": [
            {
                "stage": "provider_http",
                "http_status": 403,
                "detail": "Forbidden: waf_rule=rest.quota.daily limit (中文细节·日配额)",
                "not_bad_data": "provider rejection, not attribution to bad data",
            },
            {
                "stage": "provider_retry",
                "attempts": 3,
                "detail": "重试三次后仍被封禁，等待窗口由 provider 控制",
            },
        ],
    },
    "request_id": "execv2-w02b",
}

_N2_UNKNOWN = {
    "schema_version": "1.0",
    "status": "failed",
    "adapter": {"name": "fake-cninfo", "version": "1.1.0"},
    "error": {
        "code": "weird_provider_code",
        "message": "provider returned an unclassified code",
        "retryable": True,
        "type": "AdapterError",
    },
    "request_id": "execv2-w02b",
}

_N2_STRING = {
    "code": "upstream_unavailable",
    "message": "retryability arrives as a string literal",
    "retryable": "true",
    "type": "AdapterError",
    "request_id": "execv2-w02b",
}

_N2_MALFORMED_STDOUT = '{"code": "upstream_unavailable", "retryable": tru'
_N2_MALFORMED_STDERR = (
    "cninfo-discover: FATAL: connection died mid-stream \xbf\xa7\xc2\xd2GBK"
)


def _emit_direct(doc) -> int:
    """Direct provider-boundary failure: one JSON doc on stdout, exit 1."""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(json.dumps(doc, ensure_ascii=False))
    sys.stdout.write("\n")
    return 1


def _emit_malformed() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(_N2_MALFORMED_STDOUT)
    sys.stdout.write("\n")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.write(_N2_MALFORMED_STDERR + "\n")
    return 2


def _run_deep(case: str) -> int:
    scratch = os.environ[SCRATCH_ENV]
    python = sys.executable
    completed = subprocess.run(
        [
            python,
            "-X",
            "utf8",
            "-B",
            str(RUNNER),
            "--case",
            case,
            "--scratch",
            scratch,
            "--staged",
            str(Path(scratch) / "staging" / "seed.bin"),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ATTEMPT),
        check=False,
    )
    # Structured forwarding (decision.md): find the LAST JSON object line of
    # the deep layer's stderr, forward it VERBATIM on stdout (filing-fetch's
    # client reads the error document from stdout), and pass everything else
    # through on stderr untouched (warnings never pollute the envelope
    # stream).
    lines = [line for line in (completed.stderr or "").splitlines()]
    json_index = None
    for index, line in enumerate(lines):
        if line.strip().startswith("{"):
            try:
                json.loads(line)
                json_index = index
            except json.JSONDecodeError:
                continue
    if json_index is None:
        sys.stderr.write(
            json.dumps(
                {
                    "error": "opaque deep-layer failure (no JSON envelope)",
                    "raw_stderr_head": (completed.stderr or "")[:200],
                    "child_exit": completed.returncode,
                }
            )
            + "\n"
        )
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(lines[json_index])
    sys.stdout.write("\n")
    sys.stdout.flush()
    non_json = "\n".join(line for i, line in enumerate(lines) if i != json_index)
    if non_json.strip():
        sys.stderr.write(non_json + "\n")
    return completed.returncode


def main() -> int:
    case = os.environ.get("W02B_CASE", "")
    direct = {
        "n1_long": lambda: _emit_direct(_NESTED_CAUSE_DIRECT),
        "n2_unknown": lambda: _emit_direct(_N2_UNKNOWN),
        "n2_string": lambda: _emit_direct(_N2_STRING),
        "n2_malformed": _emit_malformed,
    }
    if case in direct:
        return direct[case]()
    if case in {"p1_cw", "n3", "n4a", "n4b"}:
        return _run_deep(case)
    sys.stderr.write(json.dumps({"error": f"unknown W02B_CASE: {case}"}) + "\n")
    return 2


if __name__ == "__main__":
    sys.argv and None  # keep import side effects free
    raise SystemExit(main())
