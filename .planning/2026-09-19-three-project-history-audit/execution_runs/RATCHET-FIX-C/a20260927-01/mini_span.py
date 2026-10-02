import sys, sqlite3, shutil
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
sys.path.insert(0, r"C:\Users\郑曾波\Projects\company-wiki\src")

def build(root: Path):
    import company_wiki.source_catalog as cat
    from company_wiki.source_catalog.store import retire_document
    if root.exists(): shutil.rmtree(root)
    project = root/"project"; src = root/"sources"; src.mkdir(parents=True)
    (src/"a.txt").write_text("第一节 释义\n\n释义：本报告使用的术语与定义说明。\n\n第三节 公司业务概要\n\n主营业务：公司主要从事半导体设备的研发、生产与销售。\n", encoding="utf-8")
    c = cat.SourceCatalog(cat.CatalogConfig(project_root=project, catalog_dir=project/".source_catalog", roots=(cat.RootSpec("external", src, "directory"),)))
    c.scan(); c.normalize()
    conn = sqlite3.connect(f"file:{c.config.database_path}?mode=ro", uri=True)
    n_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    n_spans = conn.execute("SELECT COUNT(*) FROM evidence_spans").fetchone()[0]
    conn.close()
    print("docs", n_docs, "spans", n_spans, "db", c.config.database_path)

if __name__ == "__main__":
    build(Path(sys.argv[1]))
