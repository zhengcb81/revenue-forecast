"""I-11-A: minimal, auditable PDF text extractor (pure standard library).

Why this file exists
--------------------
The card needs source-anchored raw values from the three bound filings. The
attempt's isolated venv has no PDF library and installing one needs the network,
which is forbidden. The global Miniconda interpreter has PyMuPDF but card rules
forbid running cards on the global interpreter. So this extractor implements the
subset of PDF needed to read text with the standard library only (re, zlib).

Scope / limits (stated up front, never silently widened)
-------------------------------------------------------
* Supports: classic xref objects (no ObjStm-only documents), FlateDecode streams,
  page /Contents streams plus Form XObjects reached with the Do operator,
  Type0/Identity-H fonts with a ToUnicode CMap, TrueType/Type1 fonts with
  WinAnsiEncoding or an explicit ToUnicode CMap, simple one-byte encodings.
* Does NOT do: cryptography, linearisation repair, LZW/JPX, CID fonts without
  ToUnicode, layout analysis beyond (y desc, x asc) line grouping, table detection.
* Text is emitted as positioned fragments; line grouping uses a y tolerance.

CLI:
    python -X utf8 -B tools\\pdf_text.py <pdf> <page_numbers_comma_separated> <out.json>
"""

from __future__ import annotations

import json
import os
import re
import sys
import zlib
from typing import Dict, Iterable, List, Optional, Tuple

OBJ_RE = re.compile(rb"(?<![0-9])(\d+)\s+(\d+)\s+obj\b")
STREAM_RE = re.compile(rb"stream\r?\n")


class Pdf:
    def __init__(self, data: bytes):
        self.data = data
        self.index: Dict[int, int] = {}
        for m in OBJ_RE.finditer(data):
            self.index[int(m.group(1))] = m.start()
        self._cache: Dict[int, bytes] = {}
        self._cmap_cache: Dict[int, Dict[int, str]] = {}

    def raw(self, num: int) -> Optional[bytes]:
        if num in self._cache:
            return self._cache[num]
        start = self.index.get(num)
        if start is None:
            return None
        end = self.data.find(b"endobj", start)
        body = self.data[start: end if end != -1 else start + (1 << 21)]
        self._cache[num] = body
        return body

    def stream(self, num: int) -> Optional[bytes]:
        body = self.raw(num)
        if body is None:
            return None
        m = STREAM_RE.search(body)
        if not m:
            return None
        s = m.end()
        e = body.find(b"endstream", s)
        if e == -1:
            return None
        payload = body[s:e]
        header = body[: m.start()]
        if b"/FlateDecode" in header:
            try:
                payload = zlib.decompress(payload)
            except zlib.error:
                try:
                    payload = zlib.decompressobj().decompress(payload)
                except zlib.error:
                    return None
        return payload

    def ref(self, num: int) -> Optional[bytes]:
        return self.raw(num)


def parse_cmap(text: str) -> Dict[int, str]:
    out: Dict[int, str] = {}

    def to_str(hexs: str) -> str:
        hexs = hexs.strip()
        if len(hexs) % 4 == 0:
            raw = bytes.fromhex(hexs)
            return raw.decode("utf-16-be", "replace")
        raw = bytes.fromhex(hexs)
        return raw.decode("latin-1")

    for block in re.findall(r"beginbfchar(.*?)endbfchar", text, re.S):
        for src, dst in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            out[int(src, 16)] = to_str(dst)
    for block in re.findall(r"beginbfrange(.*?)endbfrange", text, re.S):
        for m in re.finditer(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f]+>|\[[^\]]*\])", block):
            lo, hi, dst = int(m.group(1), 16), int(m.group(2), 16), m.group(3)
            if dst.startswith("<"):
                base = to_str(dst[1:-1])
                for i, code in enumerate(range(lo, hi + 1)):
                    out[code] = _shift(base, i)
            else:
                items = re.findall(r"<([0-9A-Fa-f]+)>", dst)
                for i, code in enumerate(range(lo, hi + 1)):
                    if i < len(items):
                        out[code] = to_str(items[i])
    return out


def _shift(base: str, delta: int) -> str:
    if not base:
        return base
    return base[:-1] + chr(ord(base[-1]) + delta)


WINANSI = "cp1252"


class Font:
    def __init__(self, pdf: Pdf, num: int):
        self.obj = pdf.raw(num) or b""
        text = self.obj.decode("latin-1")
        self.subtype = (re.search(r"/Subtype\s*/(\w+)", text) or [None, ""])[1]
        enc = re.search(r"/Encoding\s*/?(\w+)", text)
        self.encoding = enc.group(1) if enc else ""
        self.two_byte = self.subtype == "Type0" or self.encoding == "Identity-H"
        self.tounicode: Dict[int, str] = {}
        m = re.search(r"/ToUnicode\s+(\d+)\s+0\s+R", text)
        if m:
            cs = pdf.stream(int(m.group(1)))
            if cs:
                self.tounicode = parse_cmap(cs.decode("latin-1", "replace"))
        codespace: List[Tuple[int, int]] = []
        for lo, hi in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", text):
            pass
        self.codespace = codespace

    def decode(self, raw: bytes) -> str:
        if self.two_byte:
            if len(raw) % 2:
                raw = raw[:-1]
            codes = [int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw), 2)]
        else:
            codes = list(raw)
        out = []
        for c in codes:
            if c in self.tounicode:
                out.append(self.tounicode[c])
            elif not self.two_byte:
                out.append(bytes([c]).decode(WINANSI, "replace"))
            else:
                out.append("")
        return "".join(out)


TOKEN_RE = re.compile(
    rb"\[|\]|<<|>>|<[0-9A-Fa-f\s]*>|\((?:[^()\\]|\\.)*\)|/[^\s/\[\]<>()]+"
    rb"|[-+]?[0-9]*\.?[0-9]+|[\w'\"*]+"
)


def unescape_literal(raw: bytes) -> bytes:
    body = raw[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == 0x5C and i + 1 < len(body):
            nxt = body[i + 1]
            mapping = {0x6E: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12,
                       0x28: 0x28, 0x29: 0x29, 0x5C: 0x5C}
            if nxt in mapping:
                out.append(mapping[nxt])
                i += 2
                continue
            if 0x30 <= nxt <= 0x37:
                j = i + 1
                digits = b""
                while j < len(body) and len(digits) < 3 and 0x30 <= body[j] <= 0x37:
                    digits += bytes([body[j]])
                    j += 1
                out.append(int(digits, 8) & 0xFF)
                i = j
                continue
            out.append(nxt)
            i += 2
            continue
        out.append(ch)
        i += 1
    return bytes(out)


def hex_string(raw: bytes) -> bytes:
    body = re.sub(rb"[^0-9A-Fa-f]", b"", raw[1:-1])
    if len(body) % 2:
        body += b"0"
    return bytes.fromhex(body.decode("ascii"))


class Page:
    def __init__(self, pdf: Pdf, num: int):
        self.pdf = pdf
        self.num = num
        self.obj = pdf.raw(num) or b""
        txt = self.obj.decode("latin-1")
        self.fonts: Dict[str, int] = {}
        fm = re.search(r"/Font\s*<<(.*?)>>", txt, re.S)
        if fm:
            for name, ref in re.findall(r"/([^\s/]+)\s+(\d+)\s+0\s+R", fm.group(1)):
                self.fonts[name] = int(ref)
        self.xobjects: Dict[str, int] = {}
        xm = re.search(r"/XObject\s*<<(.*?)>>", txt, re.S)
        if xm:
            for name, ref in re.findall(r"/([^\s/]+)\s+(\d+)\s+0\s+R", xm.group(1)):
                self.xobjects[name] = int(ref)
        self.resources_of: Dict[int, Tuple[Dict[str, int], Dict[str, int]]] = {}
        self._font_cache: Dict[int, Font] = {}

    def font(self, name: str) -> Optional[Font]:
        num = self.fonts.get(name)
        if num is None:
            return None
        if num not in self._font_cache:
            self._font_cache[num] = Font(self.pdf, num)
        return self._font_cache[num]

    def fragments(self) -> List[Tuple[float, float, str]]:
        frags: List[Tuple[float, float, str]] = []
        contents = re.findall(r"/Contents\s+(\d+)\s+0\s+R", self.obj.decode("latin-1"))
        for c in contents:
            cs = self.pdf.stream(int(c))
            if cs:
                self._walk(cs, frags, depth=0)
        return frags

    def _walk(self, stream: bytes, frags, depth: int) -> None:
        if depth > 3:
            return
        tokens = TOKEN_RE.findall(stream)
        stack: List[bytes] = []
        font: Optional[Font] = None
        tm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        tlm = list(tm)
        leading = 0.0
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok in (b"BT",):
                tm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
                tlm = list(tm)
                stack = []
            elif tok == b"Tf":
                if len(stack) >= 2:
                    font = self.font(stack[-2][1:].decode("latin-1"))
            elif tok == b"TL":
                if stack:
                    leading = _num(stack[-1])
            elif tok in (b"Td", b"TD"):
                if len(stack) >= 2:
                    tx, ty = _num(stack[-2]), _num(stack[-1])
                    if tok == b"TD":
                        leading = -ty
                    tlm = _mul(tlm, _translate(tx, ty))
                    tm = list(tlm)
            elif tok == b"Tm":
                if len(stack) >= 6:
                    tlm = [_num(x) for x in stack[-6:]]
                    tm = list(tlm)
            elif tok == b"T*":
                tlm = _mul(tlm, _translate(0.0, -leading))
                tm = list(tlm)
            elif tok == b"Tj":
                if stack and font is not None:
                    frags.append((tm[4], tm[5], font.decode(_string(stack[-1]))))
            elif tok == b"'":
                tlm = _mul(tlm, _translate(0.0, -leading))
                tm = list(tlm)
                if stack and font is not None:
                    frags.append((tm[4], tm[5], font.decode(_string(stack[-1]))))
            elif tok == b"TJ":
                if font is not None:
                    # the array operand is flattened on the stack; its element
                    # strings are exactly the literal/hex tokens since the last
                    # unmatched "[" (a "]" pushed by this run is skipped below)
                    body = []
                    for prev in reversed(stack):
                        if prev == b"[":
                            break
                        if prev in (b"]", b"[", b"<<", b">>") or prev.startswith(b"/"):
                            continue
                        if prev.startswith(b"(") or prev.startswith(b"<"):
                            body.append(prev)
                    for s in reversed(body):
                        frags.append((tm[4], tm[5], font.decode(_string(s))))
            elif tok == b"Do":
                if stack:
                    name = stack[-1][1:].decode("latin-1")
                    sub = self.xobjects.get(name)
                    if sub is not None:
                        cs = self.pdf.stream(sub)
                        if cs:
                            sub_fonts = self._sub_fonts(sub)
                            if sub_fonts:
                                saved = dict(self.fonts)
                                self.fonts.update(sub_fonts)
                                self._walk(cs, frags, depth + 1)
                                self.fonts = saved
                            else:
                                self._walk(cs, frags, depth + 1)
            stack.append(tok)
            i += 1

    def _sub_fonts(self, objnum: int) -> Dict[str, int]:
        obj = self.pdf.raw(objnum) or b""
        txt = obj.decode("latin-1")
        out = {}
        fm = re.search(r"/Font\s*<<(.*?)>>", txt, re.S)
        if fm:
            for name, ref in re.findall(r"/([^\s/]+)\s+(\d+)\s+0\s+R", fm.group(1)):
                out[name] = int(ref)
        return out


def _num(tok: bytes) -> float:
    try:
        return float(tok)
    except ValueError:
        return 0.0


def _string(tok: bytes) -> bytes:
    if tok.startswith(b"<"):
        return hex_string(tok)
    return unescape_literal(tok)


def _translate(tx: float, ty: float) -> List[float]:
    return [1.0, 0.0, 0.0, 1.0, tx, ty]


def _mul(a: List[float], b: List[float]) -> List[float]:
    return [
        a[0] * b[0] + a[1] * b[2],
        a[0] * b[1] + a[1] * b[3],
        a[2] * b[0] + a[3] * b[2],
        a[2] * b[1] + a[3] * b[3],
        a[4] * b[0] + a[5] * b[2] + b[4],
        a[4] * b[1] + a[5] * b[3] + b[5],
    ]


def page_text(frags: Iterable[Tuple[float, float, str]], tol: float = 0.8) -> str:
    """Positional line grouping.

    `tol` is the vertical distance (PDF user units, 1/72 inch) within which two
    fragments are treated as the same rendered line. 0.8 pt is chosen because
    the largest intra-line baseline jitter observed in the bound CN/HK filings
    is <0.5 pt, while adjacent table rows are >=1.7 pt apart; both facts are
    re-measured by tools/pdf_extract.py and written to the evidence JSON.
    """
    items = [f for f in frags if f[2].strip()]
    lines: List[Tuple[float, List[Tuple[float, float, str]]]] = []
    for x, y, t in sorted(items, key=lambda f: (-f[1], f[0])):
        if lines:
            ys = [frag[1] for frag in lines[-1][1]]
            ref = sorted(ys)[len(ys) // 2]
            if abs(ref - y) <= tol:
                lines[-1][1].append((x, y, t))
                continue
        lines.append((y, [(x, y, t)]))
    out = []
    for _, bucket in lines:
        bucket.sort(key=lambda p: p[0])
        out.append("".join(t for _, _, t in bucket))
    return "\n".join(out)


def measured_positions(frags: Iterable[Tuple[float, float, str]]) -> Dict[str, float]:
    """Report the two quantities the 0.8 pt tolerance rests on."""
    items = sorted([f for f in frags if f[2].strip()], key=lambda f: (-f[1], f[0]))
    gaps = []
    for prev, cur in zip(items, items[1:]):
        gaps.append(abs(prev[1] - cur[1]))
    same_line = [g for g in gaps if g <= 0.8]
    other = [g for g in gaps if g > 0.8]
    return {
        "max_gap_within_tolerance": max(same_line) if same_line else 0.0,
        "min_gap_above_tolerance": min(other) if other else 0.0,
    }


def classic_page_numbers(pdf: Pdf) -> List[int]:
    nums = []
    for num in sorted(pdf.index):
        body = pdf.raw(num) or b""
        if re.search(rb"/Type\s*/Page[^s]", body):
            nums.append(num)
    return nums


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    path, pages_arg, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    data = open(path, "rb").read()
    pdf = Pdf(data)
    pages = classic_page_numbers(pdf)
    wanted = [int(p) for p in pages_arg.split(",") if p.strip()]
    result = {"pdf": path, "classic_pages": len(pages), "pages": []}
    for w in wanted:
        objnum = pages[w - 1]
        page = Page(pdf, objnum)
        text = page_text(page.fragments())
        result["pages"].append({"pdf_page": w, "page_object": objnum, "text": text})
        print("page %d (obj %d): %d chars" % (w, objnum, len(text)))
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
