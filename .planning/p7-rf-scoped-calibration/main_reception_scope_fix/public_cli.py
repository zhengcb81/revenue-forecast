from pathlib import Path
import hashlib,json,os,shutil,stat,subprocess,sys,tempfile,time
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
original=Path(r"C:/Users/郑曾波/.codex/worktrees/m3-acceptance-20261010/company-wiki/docs/plans/cross-market-rf-e2e-2026-10-08/phase6/main_auto_official_json/evidence/p7-rf-final-review/shared_root_minimal_input.json")
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
owned=Path(tempfile.mkdtemp(prefix="p7-rf-scope-cli-"))
environment_before=dict(os.environ)
env={k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
env.update(PYTHONDONTWRITEBYTECODE="1",PYTHONUTF8="1",REVENUE_PUBLICATION_REGISTRY=str(owned/"registry/publications.jsonl"))
receipt={"schema_version":"p7-rf-scope-public-cli/1","original_input_sha256":sha(original),"owned_temp":str(owned),"provider_calls":0,"model_calls":0,"new_cost_usd":0,"publication_registry_calls":0}
try:
    source=owned/"input.json"
    source.write_bytes(original.read_bytes())
    target=owned/"diagnostics.json"
    before=source.read_bytes()
    argv=[sys.executable,"-X","utf8","-B",str(root/"scripts/research_support_diagnostics.py"),"--input",str(source),"--output",str(target)]
    started=time.perf_counter()
    result=subprocess.run(argv,cwd=owned,env=env,text=True,encoding="utf-8",capture_output=True,timeout=60)
    (out/"public-cli.log").write_bytes((result.stdout+result.stderr).encode("utf-8"))
    receipt.update(argv=argv,exit_code=result.returncode,seconds=time.perf_counter()-started)
    assert result.returncode==0,result.stderr
    diagnostics=json.loads(target.read_text(encoding="utf-8"))
    assert diagnostics["input_sha256"]==hashlib.sha256(before).hexdigest()
    assert diagnostics["economic_truth_inferred"] is False
    cells=[]
    for segment in ("Segment A","Segment B"):
        for scenario in ("low","base","high"):
            cell=next(e for row in diagnostics["segments"] if row["segment"]==segment for e in row["entries"] if e["scenario"]==scenario and e["year"]=="2026")
            expected="supported" if segment=="Segment A" else "unsupported"
            assert cell["status"]==expected,cell
            assert cell["calibration_ids"]==(["reference_bridge"] if segment=="Segment A" else []),cell
            assert cell["claim_ids"]==(["claim_parameter_reference_lower","claim_parameter_reference_upper"] if segment=="Segment A" else []),cell
            if segment=="Segment B":
                assert "calibration_scope_not_covering:reference_bridge:Segment B" in cell["reasons"]
                assert f"parameter_without_referenced_range_calibration:0_{scenario}_2026" in cell["reasons"]
            cells.append({"segment":segment,**cell})
    receipt.update(status="accepted",cells=cells,diagnostics_sha256=sha(target),input_restored=(source.read_bytes()==before),output_created_only_inside_owned=True,registry_absent=not (owned/"registry").exists())
    assert source.read_bytes()==before
    assert sha(original)==receipt["original_input_sha256"]
finally:
    def retry(fn,p,err):
        assert Path(p).resolve().is_relative_to(owned.resolve())
        os.chmod(p,stat.S_IWRITE|stat.S_IREAD)
        fn(p)
    assert owned.resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
    shutil.rmtree(owned,onexc=retry)
    receipt.update(owned_temp_removed=not owned.exists(),environment_unchanged=environment_before==dict(os.environ),original_input_unchanged=sha(original)==receipt["original_input_sha256"])
    (out/"public-cli-receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in receipt.items() if k not in {"cells","argv"}},ensure_ascii=False,indent=2))
