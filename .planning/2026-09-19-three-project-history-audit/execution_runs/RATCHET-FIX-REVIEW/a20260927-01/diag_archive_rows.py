"""B3 diagnostic: why did the archive harness export 0 rows?

Read-only. Mirrors tests/contract/test_source_catalog_archive_retired.py setup
and counts catalog rows at each step.  GUARDED: company-wiki's scan/normalize
uses multiprocessing on Windows, and an unguarded __main__ is re-imported and
re-executed by every spawn child (which is exactly what corrupted the first
diagnostic run: the parent printed spans=0 while a child re-ran the whole
script and printed spans=6).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(WIKI / "src"))

ANNUAL = (
    "第一节 释义\n\n释义：本报告使用的术语与定义说明，包括公司与关联方的界定，以及财务指标的计量口径说明。\n\n"
    "第三节 公司业务概要\n\n主营业务：公司主要从事半导体设备的研发、生产与销售，产品覆盖刻蚀、薄膜沉积、清洗等关键工艺环节。\n\n"
    "第四节 经营情况讨论与分析\n\n经营情况：报告期内公司营业收入稳步增长，主要得益于先进制程设备出货量提升与国产替代进程加速。\n"
)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="rfrv-diag-"))
    import company_wiki.source_catalog as module
    from company_wiki.source_catalog.store import retire_document

    project = tmp / "project"
    source_root = tmp / "sources"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "a.txt").write_text(ANNUAL, encoding="utf-8")
    cat = module.SourceCatalog(module.CatalogConfig(
        project_root=project,
        catalog_dir=project / ".source_catalog",
        roots=(module.RootSpec("external", source_root, "directory"),),
    ))
    pid = __import__("os").getpid()
    print(f"pid={pid} tmp={tmp}")

    def counts(tag: str) -> None:
        q = lambda sql: cat.store.fetchone(sql)[0]  # noqa: E731
        retired = cat.store.fetchone(
            "SELECT COUNT(*) FROM documents WHERE source_status='retired'")[0]
        print(f"  [{tag}] documents={q('SELECT COUNT(*) FROM documents')} "
              f"spans={q('SELECT COUNT(*) FROM evidence_spans')} "
              f"retired_docs={retired}")

    counts("after construct")
    cat.scan()
    counts("after scan")
    cat.normalize()
    counts("after normalize")
    doc = cat.store.fetchone("SELECT document_id FROM documents")
    print("  document_id =", doc["document_id"])
    retire_document(cat.store, document_id=doc["document_id"],
                    reason="test", created_by="test")
    counts("after retire")
    n = cat.store.fetchone(
        "SELECT COUNT(*) FROM evidence_spans WHERE document_id IN "
        "(SELECT document_id FROM documents WHERE source_status='retired')")[0]
    print(f"  spans matching the archive _SELECT predicate: {n}")
    print(f"  VERDICT: {'NON-EMPTY (harness valid)' if n else 'EMPTY (harness invalid)'}")
    return 0 if n else 3


if __name__ == "__main__":
    raise SystemExit(main())
