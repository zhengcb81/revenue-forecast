"""WU-201 RED/audit tests: ARCH-01..05 forbidden-dependency edges."""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from architecture_boundaries import (  # noqa: E402
    check_import_graph,
    scan_module_imports,
)


def _graph(edges: dict[str, set[str]]) -> dict[str, set[str]]:
    return {k: set(v) for k, v in edges.items()}


def test_arch01_resolver_to_adapter_fails():
    graph = _graph({"resolver": {"catalog", "adapter.registry"}})
    problems = check_import_graph(graph, {"resolver": "resolver"})
    assert any("resolver" in p and "adapter" in p for p in problems)


def test_arch02_adapter_to_store_fails():
    graph = _graph({"adapter.xyz": {"store.CatalogStore"}})
    problems = check_import_graph(graph, {"adapter.xyz": "adapter"})
    assert any("adapter" in p and "store" in p for p in problems)


def test_arch03_calculator_to_network_fails():
    graph = _graph({"revenue_forecast": {"requests"}})
    problems = check_import_graph(graph, {"revenue_forecast": "calculator"})
    assert any("network" in p for p in problems)


def test_arch04_config_dynamic_import_fails():
    graph = _graph({"config": {"importlib"}})
    problems = check_import_graph(graph, {"config": "config"})
    assert any("dynamic" in p for p in problems)


def test_arch05_adapter_to_canonical_writer_fails():
    graph = _graph({"adapter.a": {"canonical_writer"}})
    problems = check_import_graph(graph, {"adapter.a": "adapter"})
    assert any("canonical writer" in p for p in problems)


def test_clean_graph_passes():
    graph = _graph({
        "resolver": {"catalog", "policy"},
        "adapter.a": {"pathlib", "json"},
        "revenue_forecast": {"math"},
        "config": {"yaml"},
        "scanner": {"adapter.a", "resolver"},
    })
    roles = {"resolver": "resolver", "adapter.a": "adapter",
             "revenue_forecast": "calculator", "config": "config"}
    assert check_import_graph(graph, roles) == []


def test_scan_module_imports_extracts_imports(tmp_path):
    source = tmp_path / "mod.py"
    source.write_text(
        "import os\nfrom pathlib import Path\nimport requests as rq\n",
        encoding="utf-8",
    )
    imports = scan_module_imports(source)
    assert {"os", "pathlib", "requests"} <= imports


def test_scan_module_imports_no_dynamic(tmp_path):
    source = tmp_path / "clean.py"
    source.write_text("import json\n", encoding="utf-8")
    assert "importlib" not in scan_module_imports(source)
