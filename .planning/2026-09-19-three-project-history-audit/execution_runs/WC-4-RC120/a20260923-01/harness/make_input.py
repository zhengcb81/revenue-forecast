"""Write the shared valid CLI input for WC-4 probes (attempt-local only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "rf"
RGMDIR = ATTEMPT / "evidence" / "rgm"

sys.path.insert(0, str(ISO / "scripts"))
sys.path.insert(0, str(ISO / "tests"))

from test_recognition_bridge import forecast_document  # noqa: E402


def main() -> int:
    RGMDIR.mkdir(parents=True, exist_ok=True)
    target = RGMDIR / "input_valid.json"
    doc = forecast_document()
    target.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
