"""Extract history without promoting extracted text to verified behavior."""
from __future__ import annotations
import ast
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PLAN=OUT.parents[1]
def read(path): return (ROOT/path).read_text(encoding="utf-8-sig")
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def primary_blocks(path, pattern):
    lines=read(path).splitlines()
    matches=[(i,re.search(pattern,line)) for i,line in enumerate(lines)]
    matches=[(i,m) for i,m in matches if m]
    for j,(i,m) in enumerate(matches):
        end=matches[j+1][0] if j+1<len(matches) else len(lines)
        # unit sections end at the next peer heading, not an arbitrary next unit
        if lines[i].startswith("#"):
            depth=len(lines[i])-len(lines[i].lstrip("#"))
            for k in range(i+1,end):
                if re.match(r"^#{1,"+str(depth)+r"} ",lines[k]): end=k; break
            text="\n".join(lines[i:end]).strip()
        else: text=lines[i]
        yield m.group(1),i+1,text

def receipt_summary(unit):
    directory=ROOT/"assurance/unified_completion/receipts"/unit
    records=[]
    for path in sorted(directory.glob("*.json")):
        try: obj=json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc: records.append({"path":str(path.relative_to(ROOT)),"error":str(exc)}); continue
        records.append({"path":str(path.relative_to(ROOT)),"sha256":digest(path),"kind":obj.get("kind"),"verdict":obj.get("verdict"),"base_triplet":obj.get("base_triplet"),"result_triplet":obj.get("result_triplet"),"canonical_hash":obj.get("canonical_hash"),"reviewed_object_sha256":obj.get("reviewed_object_sha256"),"commands":obj.get("commands",[]),"findings":obj.get("findings",[]),"scenario_results":obj.get("scenario_results",[])})
    return records

def main():
    scope=json.loads((PLAN/"inventory/scope_manifest.json").read_text(encoding="utf-8"))
    documents=[x for x in scope if x["repo"]=="revenue-forecast" and x.get("owner")=="revenue" and not x["scope"].startswith("excluded") and not x["path"].startswith(".review-")]
    (OUT/"document_scope.json").write_text(json.dumps(documents,ensure_ascii=False,indent=2),encoding="utf-8")
    text_by_path={x["path"]:Path(x["absolute_path"]).read_text(encoding="utf-8-sig") for x in documents}
    occurrences={}
    for path,body in text_by_path.items():
        for line,text in enumerate(body.splitlines(),1):
            for unit in set(re.findall(r"\b(?:CA|ZR|FC|WU)-\d{3,4}\b",text)):
                occurrences.setdefault(unit,[]).append({"file":path,"line":line,"text":text})
    (OUT/"unit_occurrences.json").write_text(json.dumps(occurrences,ensure_ascii=False,indent=2),encoding="utf-8")
    plans=[
      ("CA","audit_review/2026-08-13_three_repo_completion_rebaseline_plan/completion_assurance_registry.md",r"^### (CA-\d+)："),
      ("ZR","audit_review/2026-08-13_zijin_data_lake_remediation_plan/work_unit_registry.md",r"^\| (ZR-\d+) \|"),
      ("FC","audit_review/2026-08-09_full_completion_assurance_plan/work_unit_registry.md",r"^\| (FC-\d+) \|"),
      ("WU","audit_review/2026-08-09_data_lake_refactor_plan/task_plan.md",r"^### (WU-\d+)："),
    ]
    state=json.loads(read("assurance/unified_completion/state.json"))["units"]
    rows=[]
    for group,path,pattern in plans:
        for unit,line,claim in primary_blocks(path,pattern):
            card=Path("assurance/unified_completion/receipts")/unit/"00_wu_card.md"
            receipts=receipt_summary(unit)
            row={"item_id":unit,"source_file":path,"source_line":line,"original_claim":claim,"historical_state":state.get(unit,{}).get("status","see original dated registry"),"card_file":str(card) if (ROOT/card).is_file() else None,"card_text":read(card) if (ROOT/card).is_file() else None,"historical_evidence":receipts,"all_occurrences":occurrences.get(unit,[]),"conclusion":"superseded" if group in {"FC","WU"} else "insufficient_evidence","assessment_scope":"history applicability and evidence sufficiency; not a product-pass certification","current_evidence":["Read original obligation, card text and saved receipt metadata as distinct versions; later accepted state is not proof of original behavior.","Current unit state and receipt paths were independently enumerated without running production writers."],"reason":"旧编号已被冻结并由后继计划接管；保留原子义务与所有出处，superseded只说明执行入口替换，不表示原义务已兑现。" if group in {"FC","WU"} else "历史accepted和保存的局部命令不足以证明原始义务在当前三仓HEAD、配置、索引、安装态成立；必须以原始Mandatory证据逐项重放，不能从卡级后缩标准继承完成。","missing_evidence":["原始Mandatory证据覆盖当前生产入口的独立结果，含精确HEAD/config/sample/oracle与完整stdout/stderr/exit","原范围和后续执行卡每个差异的受批准处置及未完成后继状态"],"recommendation":"保留可用资产，按原始义务建立当前真入口验收；不批量重签历史receipt。"}
            rows.append(row)
    # Every root checklist entry remains separately addressable, including unchecked items.
    checklist=[]
    for path,body in text_by_path.items():
        if Path(path).name not in {"task_plan.md","IMPLEMENTATION_PLAN.md"}: continue
        heading=""
        for n,line in enumerate(body.splitlines(),1):
            if line.startswith("#"): heading=line
            if re.match(r"^\s*- \[[xX ]\]",line):
                checklist.append({"item_id":f"RF-CHECK-{len(checklist)+1:04d}","source_file":path,"source_line":n,"section":heading,"original_claim":line,"historical_state":"checked" if re.search(r"\[[xX]\]",line) else "unchecked","review_status":"pending_atomic_semantic_review","warning":"Extracted inventory only; not independently reviewed or closed."})
    (OUT/"checklist_inventory.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in checklist)+"\n",encoding="utf-8")
    (OUT/"unit_ledger.base.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    counts={g:sum(x["item_id"].startswith(g+"-") for x in rows) for g,*_ in plans}
    (OUT/"coverage.json").write_text(json.dumps({"document_count":len(documents),"document_lines":sum(x["lines"] for x in documents),"primary_units":counts,"primary_total":len(rows),"checklist_candidates":len(checklist),"checklist_semantic_pending":len(checklist),"caution":"Full unit enumeration is not full semantic audit. Manual dispositions are kept in item_ledger.jsonl; remaining granular checklist entries are explicit pending."},ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"documents":len(documents),"units":counts,"checklists":len(checklist)},ensure_ascii=False))
if __name__=="__main__": main()
