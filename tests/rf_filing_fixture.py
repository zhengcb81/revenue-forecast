"""Disposable filing-fetch wire producer for RF-owned offline tests."""

from pathlib import Path


def write_filing_reply(root: Path, stdout: bytes, *, exit_code: int = 0, stderr: bytes = b"") -> Path:
    script = root / "scripts" / "fetch_filing.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    calls = root / "calls.log"
    script.write_text(
        "import json, sys\nfrom pathlib import Path\n"
        "assert isinstance(json.load(sys.stdin), dict)\n"
        f"with Path({str(calls)!r}).open('a', encoding='utf-8') as stream:\n"
        "    stream.write('called\\n')\n"
        f"sys.stdout.buffer.write({stdout!r})\n"
        f"sys.stderr.buffer.write({stderr!r})\n"
        f"raise SystemExit({exit_code!r})\n",
        encoding="utf-8",
    )
    return calls
