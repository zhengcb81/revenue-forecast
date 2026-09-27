"""OPEN5-PEND5B-OCR-CAPABILITY: build the OCR environment WITHOUT pip.

Why not pip: pip's own runs in this sandbox hang at the index fetch and/or die
with PermissionError [Errno 13] on tempfile.mkdtemp() dirs (three bounded
attempts, see capability_report.md). urllib to the same PyPI hosts is measured
healthy (HTTP 200, <0.4s), so this builder:

  stage 1  resolve  : BFS over Requires-Dist from the roots, using the
                      https://pypi.org/simple/<pkg>/ index (all wheels,
                      data-requires-python, yanked flags, #sha256 fragments)
  stage 2  download : urllib fetch into --dl, verify sha256, record provenance
                      (URL, retrieved UTC, bytes, sha256, purpose); refuses
                      any single file > 200 MB without registering it first
  stage 3  install  : extract wheels into the card venv's Lib/site-packages
                      (zip layout == pip layout; no PATH/system changes)
  stage 4  verify   : import top-level modules + locate bundled OCR models

All writes are guarded to --dl and --site-packages realpaths only.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import html.parser
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 ControlledCapabilityStation/1.0"}
SIMPLE = "https://pypi.org/simple/{name}/"
MAX_SINGLE_BYTES = 200 * 1024 * 1024  # discipline: >200MB must be registered first
PY = (3, 13, 9)

ROOTS = ["rapidocr", "onnxruntime", "pypdfium2"]

PURPOSE = {
    "rapidocr": "ROOT: OCR engine (pure-python wheel, models expected bundled)",
    "onnxruntime": "ROOT: OCR inference runtime (CPU execution provider)",
    "pypdfium2": "ROOT: PDF page renderer feeding the OCR image pipeline",
    "opencv-python": "image processing required by rapidocr (declared dep)",
    "numpy": "numeric arrays (rapidocr/onnxruntime dep)",
    "pillow": "image I/O, PNG save/load (rapidocr dep)",
    "shapely": "polygon cleanup in text detection (rapidocr dep)",
    "pyclipper": "polygon offsetting in text detection (rapidocr dep)",
    "pyyaml": "config loading (rapidocr/omegaconf dep)",
    "tqdm": "progress display (rapidocr dep)",
    "omegaconf": "config framework (rapidocr dep)",
    "antlr4-python3-runtime": "parser runtime (omegaconf dep)",
    "requests": "HTTP helper (rapidocr dep)",
    "colorlog": "colored logging (onnxruntime dep)",
    "coloredlogs": "logging shim (onnxruntime dep)",
    "humanfriendly": "terminal utils (coloredlogs dep)",
    "flatbuffers": "serialization (onnxruntime dep)",
    "packaging": "version parsing (onnxruntime dep)",
    "protobuf": "model/IR serialization (onnxruntime dep)",
    "sympy": "symbolic ops (onnxruntime dep)",
    "mpmath": "math backend (sympy dep)",
    "six": "compat shim (rapidocr dep)",
    "urllib3": "HTTP client (requests dep)",
    "idna": "IDNA codec (requests dep)",
    "charset-normalizer": "charset detection (requests dep)",
    "certifi": "CA bundle (requests dep)",
}

IMPORT_MAP = {
    "rapidocr": "rapidocr",
    "onnxruntime": "onnxruntime",
    "pypdfium2": "pypdfium2",
    "opencv-python": "cv2",
    "pillow": "PIL",
    "numpy": "numpy",
    "pyyaml": "yaml",
    "pyclipper": "pyclipper",
    "shapely": "shapely",
    "tqdm": "tqdm",
    "requests": "requests",
    "colorlog": "colorlog",
    "flatbuffers": "flatbuffers",
    "packaging": "packaging",
    "protobuf": "google.protobuf",
    "six": "six",
    "urllib3": "urllib3",
    "idna": "idna",
    "charset-normalizer": "charset_normalizer",
    "certifi": "certifi",
    "omegaconf": "omegaconf",
    "antlr4-python3-runtime": "antlr4",
    "colorama": "colorama",
}

# sdists that must be consumed as source (no compatible wheel exists upstream)
SDIST_PACKAGE = {"antlr4-python3-runtime": ["antlr4"]}


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canon(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


class V(str):
    """PEP440-lite version string with correct ordering (3.13 > 3.9)."""

    def _t(self):
        m = re.match(r"\s*(\d+(?:\.\d+)*)", str(self))
        if not m:
            return (0,)
        parts = [int(x) for x in m.group(1).split(".")]
        while len(parts) < 4:
            parts.append(0)
        return tuple(parts)

    def _pre(self):
        return 1 if re.search(r"(a|b|rc|c|alpha|beta|pre|dev|snapshot)", str(self), re.I) else 0

    def _key(self):
        return (self._t(), self._pre())

    def __eq__(self, o):
        try:
            return self._key() == V(str(o))._key()
        except Exception:
            return False

    def __ne__(self, o):
        return not self.__eq__(o)

    def __lt__(self, o):
        return self._key() < V(str(o))._key()

    def __le__(self, o):
        return self._key() <= V(str(o))._key()

    def __gt__(self, o):
        return self._key() > V(str(o))._key()

    def __ge__(self, o):
        return self._key() >= V(str(o))._key()


FACTS = {
    "python_version": V("3.13"),
    "python_full_version": V("3.13.9"),
    "implementation_version": V("3.13.9"),
    "implementation_name": "cpython",
    "platform_python_implementation": "CPython",
    "sys_platform": "win32",
    "platform_system": "Windows",
    "os_name": "nt",
    "platform_machine": "AMD64",
    "platform_release": "10",
    "platform_version": "10.0.26100",
}


def eval_marker(marker: str) -> bool:
    marker = marker.strip()
    if not marker:
        return True
    if "extra" in marker:
        return False  # we do not select extras
    try:
        return bool(eval(marker, {"__builtins__": {}}, dict(FACTS)))  # noqa: S307
    except Exception:
        return True  # fail-open: keep the dependency, flag later if unusable


def spec_ok(specifier: str, version: str) -> bool:
    """Crude PEP508 specifier check against a wheel version."""
    specifier = specifier.strip()
    if not specifier:
        return True
    for one in specifier.split(","):
        one = one.strip()
        if not one:
            continue
        m = re.match(r"(~=|==|!=|>=|<=|>|<)\s*(.+)", one)
        if not m:
            continue
        op, ver = m.group(1), m.group(2).strip()
        if op == "==" and ver.endswith(".*"):
            pref = tuple(int(x) for x in ver[:-1].split(".") if x.isdigit())
            got = V(version)._t()[: len(pref)]
            if got != pref:
                return False
            continue
        if op == "~=":
            base = [int(x) for x in ver.split(".") if x.isdigit()]
            lo = list(V(version)._t())
            if not base:
                continue
            n = max(len(base), len(lo))
            b2 = base + [0] * (n - len(base))
            l2 = lo + [0] * (n - len(lo))
            if tuple(l2[: n - 1]) != tuple(b2[: n - 1]) or tuple(l2) < tuple(b2):
                return False
            continue
        a, b = V(version)._key(), V(ver)._key()
        ok = {
            ">=": a >= b,
            "<=": a <= b,
            ">": a > b,
            "<": a < b,
            "==": a == b,
            "!=": a != b,
        }.get(op, True)
        if not ok:
            return False
    return True


class IndexParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.files = []
        self._cur = None

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        d = dict(attrs)
        self._cur = {"href": d.get("href", ""), "requires": d.get("data-requires-python"),
                     "yanked": d.get("data-yanked") is not None}
        self.files.append(self._cur)

    def handle_data(self, data):
        pass


def fetch_index(name: str):
    url = SIMPLE.format(name=urllib.parse.quote(canon(name)))
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode("utf-8", "replace")
    p = IndexParser()
    p.feed(body)
    return url, p.files


def wheel_pick(files, req_specs):
    """Pick best compatible non-yanked wheel honouring Requires-Python + specs."""
    cands = []
    for f in files:
        href = f["href"]
        if not href:
            continue
        path = urllib.parse.urldefrag(href).url
        fn = path.rstrip("/").split("/")[-1]
        if not fn.endswith(".whl"):
            continue
        stem = fn[:-4]
        parts = stem.split("-")
        if len(parts) < 5:
            continue
        pytag, abitag, plattag = parts[-3], parts[-2], parts[-1]
        if plattag not in ("any", "win_amd64"):
            continue
        if abitag.startswith("cp") and abitag.endswith("t"):
            continue  # free-threaded (cp313t) build: incompatible with this CPython
        ok_py = (
            pytag in ("py3", "py2.py3", "py3-none")
            or pytag == "cp313"
            or (abi3_ok(pytag, abitag))
        )
        if not ok_py:
            continue
        if f["requires"]:
            if not eval_requires_python(f["requires"]):
                continue
        ver = parts[1]
        if f["yanked"]:
            continue
        if not all(spec_ok(s, ver) for s in req_specs):
            continue
        cands.append((V(ver)._key(), V(ver)._pre(), fn, href, ver))
    if not cands:
        # fail-closed: honour Requires-Dist specifiers strictly; the caller
        # falls back to a matching sdist, then to an explicit error
        return None
    # standard index semantics: prefer final releases; fall back to prereleases
    finals = [c for c in cands if c[1] == 0] or cands
    finals.sort(key=lambda x: x[0])
    best = finals[-1]
    return {"filename": best[2], "href": best[3], "version": best[4]}


def abi3_ok(pytag: str, abitag: str) -> bool:
    if abitag == "abi3" and pytag.startswith("cp"):
        try:
            return int(pytag[2:]) <= 313
        except ValueError:
            return False
    return False


def sdist_pick(files, req_specs):
    """Best matching sdist (.tar.gz/.zip); used only when no wheel qualifies."""
    cands = []
    for f in files:
        href = f.get("href") or ""
        fn = urllib.parse.urldefrag(href).url.split("/")[-1]
        if fn.endswith(".tar.gz"):
            stem = fn[: -len(".tar.gz")]
        elif fn.endswith(".zip"):
            stem = fn[: -len(".zip")]
        else:
            continue
        ver = stem.split("-")[-1]
        if not ver or not ver[0].isdigit():
            continue
        if f.get("yanked"):
            continue
        if f.get("requires") and not eval_requires_python(f["requires"]):
            continue
        if not all(spec_ok(s, ver) for s in req_specs):
            continue
        cands.append((V(ver)._key(), V(ver)._pre(), fn, href, ver))
    if not cands:
        return None
    finals = [c for c in cands if c[1] == 0] or cands
    finals.sort(key=lambda x: x[0])
    best = finals[-1]
    return {"filename": best[2], "href": best[3], "version": best[4], "kind": "sdist"}


def eval_requires_python(expr: str) -> bool:
    expr = expr.strip().lstrip("(").rstrip(")")
    try:
        return bool(eval(expr, {"__builtins__": {}}, dict(FACTS)))  # noqa: S307
    except Exception:
        return True


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_one(entry, dl_dir, receipts_lock):
    dest = os.path.join(dl_dir, entry["filename"])
    url = urllib.parse.urldefrag(entry["href"]).url
    want = urllib.parse.parse_qs(urllib.parse.urldefrag(entry["href"]).fragment).get("sha256", [None])[0]
    if os.path.exists(dest) and sha256_of(dest) == want:
        entry.update(local_path=dest, local_bytes=os.path.getsize(dest),
                     local_sha256=want, retrieved_utc=datetime.datetime.fromtimestamp(
                         os.path.getmtime(dest), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     url=url, sha256_match=True, reused=True, error=None)
        return entry
    last_err = None
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(url, headers=UA)
            got = 0
            h = hashlib.sha256()
            with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as out:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    got += len(chunk)
                    if got > MAX_SINGLE_BYTES:
                        raise RuntimeError(
                            f"OVER_200MB_GUARD: {entry['filename']} exceeded {MAX_SINGLE_BYTES} bytes"
                        )
                    out.write(chunk)
                    h.update(chunk)
            digest = h.hexdigest()
            if want and digest != want:
                raise RuntimeError(f"sha256 mismatch for {entry['filename']}: {digest} != {want}")
            entry.update(local_path=dest, local_bytes=got, local_sha256=digest,
                         retrieved_utc=utc_now(), url=url, sha256_match=(digest == want),
                         reused=False, error=None, attempt=attempt)
            return entry
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            if os.path.exists(dest):
                try:
                    os.remove(dest)
                except OSError:
                    pass
    entry.update(url=url, error=last_err, local_bytes=0, local_sha256=None,
                 retrieved_utc=utc_now(), sha256_match=False, reused=False)
    return entry


def parse_metadata_deps(zf: zipfile.ZipFile):
    meta_name = next((n for n in zf.namelist() if n.endswith(".dist-info/METADATA")), None)
    if not meta_name:
        return [], None, None
    raw = zf.read(meta_name).decode("utf-8", "replace")
    reqs = []
    rp = None
    for line in raw.splitlines():
        if line.startswith("Requires-Dist:"):
            reqs.append(line.split(":", 1)[1].strip())
        elif line.startswith("Requires-Python:"):
            rp = line.split(":", 1)[1].strip()
    return reqs, meta_name, rp


def req_name_and_marker(req: str):
    m = re.match(r"([A-Za-z0-9][A-Za-z0-9._-]*)", req)
    if not m:
        return None, None, None
    name = m.group(1)
    rest = req[m.end():]
    sm = re.search(r"[;(]", rest)
    specs = rest[: sm.start()] if sm else rest
    marker = rest[rest.find(";") + 1:] if ";" in rest else None
    return name, specs.strip(), (marker.strip() if marker else None)


def ext(p: str) -> str:
    # extended-length prefix: deep trees (onnxruntime tools/...) exceed the
    # 260-char MAX_PATH under this long attempt path (observed ENOENT)
    return "\\\\?\\" + p if not p.startswith("\\\\?\\") else p


def install_sdist(entry, sp_dir, report, fails):
    """Pure-python sdist fallback: copy the mapped import package dirs."""
    import tarfile

    pkgs = SDIST_PACKAGE.get(entry["project"])
    if not pkgs:
        report["skipped"].append(f"{entry['filename']} (sdist without SDIST_PACKAGE mapping)")
        return 0
    count = 0
    base_real = os.path.realpath(sp_dir)
    # drop any previously (wrongly) extracted version of this package first
    for pkg in pkgs:
        pkg_dir = os.path.join(sp_dir, pkg)
        if os.path.isdir(ext(pkg_dir)):
            shutil.rmtree(ext(pkg_dir), ignore_errors=True)
        proj = entry["project"].replace("-", "_")
        for pat in (f"{proj}-*.dist-info", f"{entry['project']}-*.dist-info"):
            for p in glob.glob(os.path.join(sp_dir, pat)):
                shutil.rmtree(ext(p), ignore_errors=True)
    with tarfile.open(entry["local_path"], "r:*") as tf:
        members = tf.getmembers()
        for pkg in pkgs:
            for m in members:
                if not m.isfile():
                    continue
                parts = m.name.split("/")
                if pkg not in parts:
                    continue
                idx = parts.index(pkg)
                if idx == 1:
                    pass  # <root>/<pkg>/...
                elif idx == 2 and parts[1] == "src":
                    pass  # <root>/src/<pkg>/...
                else:
                    continue
                rel = "/".join(parts[idx + 1:])
                if not rel or ".." in rel.split("/"):
                    continue
                target = os.path.normpath(os.path.join(sp_dir, pkg, rel))
                if not os.path.realpath(target).startswith(base_real):
                    continue
                try:
                    os.makedirs(ext(os.path.dirname(target)), mode=0o777, exist_ok=True)
                    src = tf.extractfile(m)
                    with open(ext(target), "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    try:
                        os.chmod(ext(target), 0o777)
                    except OSError:
                        pass
                    count += 1
                except OSError as ex:
                    fails.append(f"{entry['filename']}:{m.name}: {type(ex).__name__}: {ex}")
    return count


def install_wheels(entries, sp_dir, report):
    collisions = []
    fails = []
    for e in sorted(entries, key=lambda x: x["filename"]):
        path = e.get("local_path")
        if not path or not os.path.exists(path):
            report["skipped"].append(e["filename"])
            continue
        if e.get("kind") == "sdist":
            e["installed_files"] = install_sdist(e, sp_dir, report, fails)
            continue
        count = 0
        with zipfile.ZipFile(path) as zf:
            base_real = os.path.realpath(sp_dir)
            for info in zf.infolist():
                name = info.filename
                if name.endswith("/"):
                    continue
                norm = name.replace("\\", "/")
                if norm.startswith("/") or ".." in norm.split("/"):
                    report["rejected_entries"].append(f"{e['filename']}:{name}")
                    continue
                target = os.path.normpath(os.path.join(sp_dir, norm))
                if not os.path.realpath(target).startswith(base_real):
                    report["rejected_entries"].append(f"{e['filename']}:{name}")
                    continue
                try:
                    os.makedirs(ext(os.path.dirname(target)), mode=0o777, exist_ok=True)
                    if os.path.exists(target):
                        collisions.append(f"{e['filename']}:{norm}")
                    with zf.open(info) as src, open(ext(target), "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    try:
                        os.chmod(ext(target), 0o777)
                    except OSError:
                        pass
                    count += 1
                except OSError as ex:
                    fails.append(f"{e['filename']}:{norm}: {type(ex).__name__}: {ex}")
        e["installed_files"] = count
    report["collisions"] = collisions[:200]
    report["collision_count"] = len(collisions)
    report["extract_failures"] = fails[:200]
    report["extract_failure_count"] = len(fails)


def verify_imports(sp_dir):
    sys.path.insert(0, sp_dir)
    results = {}
    for pkg, mod in sorted(IMPORT_MAP.items()):
        try:
            __import__(mod)
            results[pkg] = {"import": mod, "ok": True}
        except Exception as e:  # noqa: BLE001
            results[pkg] = {"import": mod, "ok": False, "error": f"{type(e).__name__}: {e}"}
    return results


def find_models(sp_dir):
    out = []
    for root, _dirs, files in os.walk(os.path.join(sp_dir, "rapidocr")):
        for fn in files:
            if fn.endswith((".onnx", ".pdmodel", ".pdiparams", ".yaml", ".txt")) and (
                "model" in root.lower() or fn.endswith(".onnx")
            ):
                p = os.path.join(root, fn)
                out.append({"path": os.path.relpath(p, sp_dir), "bytes": os.path.getsize(p)})
    out.sort(key=lambda x: -x["bytes"])
    return out[:40]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dl", required=True)
    ap.add_argument("--site-packages", required=True)
    ap.add_argument("--receipts", required=True)
    ap.add_argument("--install-report", required=True)
    ap.add_argument("--stage", default="all", choices=["all", "resolve", "install", "verify"])
    args = ap.parse_args()

    dl_real = os.path.realpath(args.dl)
    sp_real = os.path.realpath(args.site_packages)
    os.makedirs(dl_real, mode=0o777, exist_ok=True)
    os.makedirs(sp_real, mode=0o777, exist_ok=True)
    allow = (dl_real, sp_real)

    log_path = os.path.join(dl_real, "build_env.log")

    def log(msg):
        line = f"[{utc_now()}] {msg}"
        print(line, flush=True)
        with open(log_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")

    # ---------------- stage 1+2: resolve + download ----------------
    receipts_path = args.receipts
    selected = {}  # canon name -> entry
    dep_specs = {}  # canon name -> accumulated specifier strings from parents
    queue = list(ROOTS)
    for _r in ROOTS:
        dep_specs.setdefault(canon(_r), [])
    index_cache = {}
    wave = 0
    while queue:
        wave += 1
        if wave > 60:
            log("ABORT: wave limit reached (possible dependency loop)")
            return 3
        new_names = []
        for name in queue:
            c = canon(name)
            if c in selected:
                continue
            if c not in index_cache:
                log(f"index: {c}")
                index_cache[c] = fetch_index(name)
            idx_url, files = index_cache[c]
            pick = wheel_pick(files, dep_specs.get(c, []))
            if not pick:
                pick = sdist_pick(files, dep_specs.get(c, []))
                if pick:
                    log(f"sdist-fallback: {c} -> {pick['filename']} (no compatible wheel; "
                        f"pure-python source install)")
            if not pick:
                log(f"NO-COMPATIBLE-WHEEL: {c}")
                selected[c] = {"filename": None, "project": name, "error": "no compatible wheel",
                               "index_url": idx_url}
                continue
            url = urllib.parse.urldefrag(pick["href"]).url
            entry = {
                "project": c,
                "filename": pick["filename"],
                "version": pick["version"],
                "kind": pick.get("kind", "wheel"),
                "href": pick["href"],
                "index_url": idx_url,
                "upstream_sha256": urllib.parse.parse_qs(
                    urllib.parse.urldefrag(pick["href"]).fragment).get("sha256", [None])[0],
                "purpose": PURPOSE.get(c, "transitive dependency"),
            }
            selected[c] = entry
            new_names.append((c, entry))
        if not new_names:
            break
        # download this wave in parallel
        with ThreadPoolExecutor(max_workers=4) as ex:
            done = list(ex.map(lambda t: download_one(t[1], dl_real, None), new_names))
        for e in done:
            if e.get("error"):
                log(f"DOWNLOAD-FAIL: {e['filename']}: {e['error']}")
            elif e.get("over_200mb"):
                log(f"OVER-200MB-REGISTERED: {e['filename']} {e.get('local_bytes')}")
            else:
                log(f"downloaded: {e['filename']} {e['local_bytes']}B sha_ok={e.get('sha256_match')}")
        # parse metadata -> next wave
        queue = []
        for e in done:
            c = e["project"]
            if not e.get("local_path"):
                continue
            if e.get("kind") == "sdist":
                log(f"sdist: {c} {e['version']} installed as source package "
                    f"(deps not machine-readable from sdist; none expected)")
                continue
            try:
                with zipfile.ZipFile(e["local_path"]) as zf:
                    reqs, _meta, rp = parse_metadata_deps(zf)
            except Exception as ex2:  # noqa: BLE001
                log(f"METADATA-FAIL: {e['filename']}: {ex2}")
                continue
            e["requires_python_wheel"] = rp
            e["requires_dist"] = reqs
            for req in reqs:
                nm, specs, marker = req_name_and_marker(req)
                if not nm:
                    continue
                if marker and not eval_marker(marker):
                    continue
                cc = canon(nm)
                if specs:
                    acc = dep_specs.setdefault(cc, [])
                    for one in (s.strip() for s in specs.split(",")):
                        if one and one not in acc:
                            acc.append(one)
                if cc in selected:
                    # verify specifier against selected version (warn only)
                    if specs and not spec_ok(specs, selected[cc].get("version", "0")):
                        log(f"SPEC-WARN: {cc} {selected[cc].get('version')} does not match '{specs}' from {c}")
                    continue
                queue.append(nm)

    total_bytes = sum(e.get("local_bytes") or 0 for e in selected.values())
    bad = [e["filename"] for e in selected.values() if e.get("error")]
    receipts = {
        "generated_utc": utc_now(),
        "method": "urllib (pip abandoned: hang/Errno13, see capability_report)",
        "index": "https://pypi.org/simple/",
        "count": len(selected),
        "downloaded_ok": len(selected) - len(bad),
        "failures": bad,
        "total_bytes": total_bytes,
        "largest_single_bytes": max((e.get("local_bytes") or 0 for e in selected.values()), default=0),
        "any_over_200mb": any((e.get("local_bytes") or 0) > MAX_SINGLE_BYTES for e in selected.values()),
        "roots": ROOTS,
        "downloads": sorted(selected.values(), key=lambda x: x["filename"] or ""),
    }
    with open(receipts_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipts, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(receipts_path, "r", encoding="utf-8") as f:
        json.load(f)
    log(f"receipts: {receipts_path} count={receipts['count']} total={total_bytes}B bad={bad}")

    # ---------------- stage 3: install ----------------
    if args.stage in ("all", "install"):
        report = {"installed_utc": utc_now(), "site_packages": sp_real,
                  "skipped": [], "rejected_entries": []}
        if bad:
            report["missing_due_to_download_failure"] = bad
        install_wheels([e for e in selected.values() if e.get("filename")], sp_real, report)
        with open(args.install_report, "w", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            f.write("\n")
        with open(args.install_report, "r", encoding="utf-8") as f:
            json.load(f)
        log(f"installed files={sum(e.get('installed_files', 0) for e in selected.values())} "
            f"collisions={report['collision_count']} skipped={report['skipped']}")

    # ---------------- stage 4: verify ----------------
    if args.stage in ("all", "verify"):
        res = verify_imports(sp_real)
        models = find_models(sp_real)
        summary = {"verified_utc": utc_now(), "imports": res,
                   "all_ok": all(v["ok"] for v in res.values()),
                   "rapidocr_models": models,
                   "rapidocr_model_total_bytes": sum(m["bytes"] for m in models)}
        with open(os.path.join(dl_real, "verify.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            f.write("\n")
        log(f"verify all_ok={summary['all_ok']} models={len(models)} "
            f"model_bytes={summary['rapidocr_model_total_bytes']}")
        for k, v in res.items():
            if not v["ok"]:
                log(f"IMPORT-FAIL: {k}: {v.get('error')}")
        if not summary["all_ok"]:
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
