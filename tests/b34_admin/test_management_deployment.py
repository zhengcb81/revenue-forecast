"""Controlled author checks for B34 deployment seams, not real-company acceptance."""

from pathlib import Path
import json
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import report_catalog_identity_cli as admin  # noqa: E402
import report_catalog_identity_resolver as bridge  # noqa: E402
from test_report_catalog_identity_resolver import _base_payload  # noqa: E402

ENT = "ENT_1b2a4d3e-0000-4a1b-8c2d-000000000001"
LISTING = "LST_2c3b5e4f-0000-4b2c-9d3e-000000000001"


def setup_bridge(tmp_path, *, workspace=True):
    code = tmp_path / "sw-code"
    code.mkdir()
    data = tmp_path / "sw-data"
    data.mkdir()
    script = code / "dashboard_identity_bridge_cli.py"
    # A real child process rejects implicit cwd/workspace selection. The response
    # is deliberately synthetic; this is not a StockWiki authority acceptance.
    script.write_text(
        "import json,sys,hashlib\nfrom pathlib import Path\n"
        + "assert Path.cwd()==Path("
        + repr(str(code))
        + ")\n"
        + "assert sys.argv[1:]=="
        + repr(
            ["resolve", "--entity-id", ENT, "--listing-id", LISTING]
            + (["--root", str(data)] if workspace else [])
        )
        + "\n"
        + "payload="
        + repr(_base_payload())
        + "\n"
        + "payload['lookup_receipt_sha256']=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()\n"
        + "print(json.dumps(payload,ensure_ascii=False))\n",
        encoding="utf-8",
    )
    values = {"python": sys.executable, "cli": str(script), "owner_root": str(code)}
    if workspace:
        values["sw_root"] = str(data)
    config = tmp_path / "bridge.json"
    config.write_text(json.dumps(values), encoding="utf-8")
    return config, data, values


def package_markers(root):
    for relative in [
        "delivery/w09/recorder/w09-rf-research-20261023/run.json",
        "delivery/w09/recorder/native-calls.jsonl",
        "delivery/w09/registry/publications.jsonl",
    ]:
        file = root / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("{}", encoding="utf-8")


@pytest.mark.parametrize("shape", ["blank", "relative", "missing", "file", "empty"])
def test_bad_admin_root_refused_before_bridge(tmp_path, monkeypatch, capsys, shape):
    file = tmp_path / "file"
    file.write_text("x")
    empty = tmp_path / "empty"
    empty.mkdir()
    value = {
        "blank": "",
        "relative": "relative",
        "missing": str(tmp_path / "missing"),
        "file": str(file),
        "empty": str(empty),
    }[shape]

    def forbidden(*args, **kwargs):
        raise AssertionError("bridge config read on invalid owner root")

    monkeypatch.setattr(admin, "load_bridge_config", forbidden)
    assert admin.main(["import-w09", "--entity-id", ENT, "--owner-root", value]) == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error_code"] in {
        "owner_root_invalid",
        "owner_root_absent",
        "owner_root_missing",
    }
    assert str(tmp_path) not in error["detail"]
    assert not (empty / "artifacts").exists()
    assert not (tmp_path / "missing").exists()


@pytest.mark.parametrize(
    "args",
    [
        ["--owner-root", "--entity-id"],
        ["--owner-root=", "--owner-root=x"],
        ["--owner-root=x", "--owner-root=y"],
    ],
)
def test_bad_root_option_grammar_named(tmp_path, capsys, args):
    assert admin.main(["resolve", "--entity-id", ENT, *args]) == 2
    assert json.loads(capsys.readouterr().err)["error_code"] == "owner_root_invalid"


def test_catalog_injection_conflict_precedes_all_lookup(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        admin, "load_bridge_config", lambda *a: pytest.fail("lookup started")
    )
    assert (
        admin.main(
            [
                "import-w09",
                "--entity-id",
                ENT,
                "--owner-root",
                str(tmp_path),
                "--catalog-file",
                str(tmp_path / "cat.jsonl"),
            ]
        )
        == 2
    )
    assert (
        json.loads(capsys.readouterr().err)["error_code"]
        == "owner_root_catalog_conflict"
    )


@pytest.mark.parametrize("first", [True, False])
def test_explicit_root_and_sw_workspace_reach_fixed_subprocess(tmp_path, capsys, first):
    config, _, _ = setup_bridge(tmp_path)
    owner = tmp_path / "rf-owner"
    owner.mkdir()
    package_markers(owner)
    args = [
        "resolve",
        "--entity-id",
        ENT,
        "--listing-id",
        LISTING,
        "--config",
        str(config),
    ]
    args = (
        ["--owner-root", str(owner), *args]
        if first
        else [*args, "--owner-root=" + str(owner)]
    )
    assert admin.main(args) == 0
    assert json.loads(capsys.readouterr().out)["entity_id"] == ENT
    assert not (owner / "artifacts").exists()


def test_explicit_admin_root_uses_core_managed_catalog_without_creating(
    tmp_path, monkeypatch, capsys
):
    config, _, _ = setup_bridge(tmp_path)
    owner = tmp_path / "rf-owner"
    owner.mkdir()
    package_markers(owner)
    observed = []

    def import_probe(catalog, **kwargs):
        observed.append((catalog.root, catalog.file))
        return {"controlled_wiring_only": True}

    monkeypatch.setattr(admin, "import_w09", import_probe)
    assert (
        admin.main(
            [
                "import-w09",
                "--entity-id",
                ENT,
                "--listing-id",
                LISTING,
                "--config",
                str(config),
                "--owner-root",
                str(owner),
            ]
        )
        == 0
    )
    assert observed == [
        (owner.resolve(), owner / "artifacts/report_catalog/catalog.jsonl")
    ]
    assert not (owner / "artifacts").exists()
    assert json.loads(capsys.readouterr().out)["controlled_wiring_only"]


def test_foreign_env_catalog_refused_before_bridge(tmp_path, monkeypatch, capsys):
    owner = tmp_path / "rf-owner"
    owner.mkdir()
    package_markers(owner)
    monkeypatch.setenv("REVENUE_REPORT_CATALOG", str(tmp_path / "other/catalog.jsonl"))
    monkeypatch.setattr(
        admin, "load_bridge_config", lambda *a: pytest.fail("lookup started")
    )
    assert admin.main(["resolve", "--entity-id", ENT, "--owner-root", str(owner)]) == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error_code"] == "catalog_path_forbidden"
    assert str(tmp_path) not in error["detail"]


@pytest.mark.parametrize("value", [None, "", "relative", False, {}, "MISSING", "FILE"])
def test_explicit_invalid_sw_workspace_never_falls_back(tmp_path, value):
    config, _, values = setup_bridge(tmp_path)
    file = tmp_path / "not-dir"
    file.write_text("x")
    values["sw_root"] = (
        str(tmp_path / "missing")
        if value == "MISSING"
        else str(file)
        if value == "FILE"
        else value
    )
    config.write_text(json.dumps(values), encoding="utf-8")
    with pytest.raises(bridge.IdentityBridgeError, match="bridge_config_invalid"):
        bridge.load_bridge_config(config)
    assert not (tmp_path / "missing").exists()


def test_explicit_sw_workspace_requires_fixed_public_cli(tmp_path):
    config, _, values = setup_bridge(tmp_path)
    other = Path(values["owner_root"]) / "other.py"
    other.write_text("raise AssertionError('never launched')")
    values["cli"] = str(other)
    config.write_text(json.dumps(values), encoding="utf-8")
    with pytest.raises(bridge.IdentityBridgeError, match="bridge_config_invalid"):
        bridge.load_bridge_config(config)


def test_legacy_missing_workspace_keeps_original_default(tmp_path):
    config, _, _ = setup_bridge(tmp_path, workspace=False)
    loaded = bridge.load_bridge_config(config)
    assert loaded.sw_root is None
    assert (
        bridge.resolve_identity(ENT, config=loaded, listing_id=LISTING)["entity_id"]
        == ENT
    )


def test_managed_catalog_resolve_cannot_escape_owner_root(tmp_path, monkeypatch):
    owner = tmp_path / "rf-owner"
    owner.mkdir()
    package_markers(owner)
    outside = tmp_path / "outside"
    outside.mkdir()
    original = Path.resolve

    def resolved(path, *args, **kwargs):
        if path == owner / "artifacts" / "report_catalog":
            return outside
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolved)
    with pytest.raises(admin.DeploymentError, match="managed catalog must stay inside"):
        admin._admin_owner_root(str(owner), catalog_file=None)


def test_marker_inspection_failure_stays_pathless(tmp_path, monkeypatch):
    owner = tmp_path / "rf-owner"
    owner.mkdir()
    marker = owner / "delivery/w09/recorder/w09-rf-research-20261023/run.json"
    original = Path.is_file

    def checked(path):
        if path == marker:
            raise PermissionError(str(marker))
        return original(path)

    monkeypatch.setattr(Path, "is_file", checked)
    with pytest.raises(admin.DeploymentError) as error:
        admin._admin_owner_root(str(owner), catalog_file=None)
    assert error.value.code == "owner_root_invalid"
    assert str(tmp_path) not in error.value.message
