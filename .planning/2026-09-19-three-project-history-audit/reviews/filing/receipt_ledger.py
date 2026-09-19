from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4]/'filing-fetch';rows=[]
def add(path,pointer,obj,verdict,reason,evidence):
 text=path.read_text(encoding='utf-8'); key=pointer.strip('/').split('/')[0];line=next((n for n,s in enumerate(text.splitlines(),1) if '"'+key+'"' in s),1)
 rows.append({'item_id':f'FFR-{len(rows)+1:03d}','source_file':str(path),'source_pointer':pointer,'line_start':line,'source_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_content':obj,'historical_status':'receipt_or_terminal_statement','verdict':verdict,'reason':reason,'current_independent_evidence':evidence,'recommendation':'保留旧字节；新证据独立绑定scope/版本/输入/命令及替代关系，不机械改旧hash。'})
for filename in ['11_implementer_receipt.json','12_reviewer_receipt.json']:
 path=REPO/'assurance/fc/FC-903'/filename;p=json.loads(path.read_text(encoding='utf-8'))
 for key,value in p.items():
  if key in ['scenario_results']:
   for i,item in enumerate(value):add(path,f'/{key}/{i}',item,'supported_scoped','4类shape/N-1局部功能均在本轮9个focused测试覆盖；不证明收据认证链或artifact真实可用。','tests/contracts.stdout.txt; scripts/filing_contracts.py:validate_resolution_envelope')
  elif key in ['commands','mutation_results']:
   for i,item in enumerate(value):add(path,f'/{key}/{i}',item,'historical_only','旧版本命令/mutation记录；本轮非原工作树重放，不能将当前280隔离通过移作历史执行认证。','REVIEWER_REPORT.md; tests/contracts.run.json')
  elif key in ['implementer_receipt_sha256','review']:
   add(path,'/'+key,value,'contradicted','当前receipt字节不匹配reviewer引用的implementer SHA；有review嵌回后继续修改的可能，但原签署字节未找到，不推定原因。','tests/pure_probes.json:fc903_binding')
  elif key in ['verdict','status','unresolved_findings']:
   add(path,'/'+key,value,'insufficient_evidence','accepted/independent_review/无未决不能覆盖当前收据链断裂、预算豁免及测试范围；局部功能证据仍保留。','review.md FF-05/06/10')
  elif key in ['side_effect_counts','side_effect_reconciliation']:
   add(path,'/'+key,value,'supported_scoped','本FC shape validator不写文件/目录/网络，当前隔离测试同样仅临时fixture；此结论不扩展到整个fetch编排。','scripts/filing_contracts.py:validate_resolution_envelope; tests/contracts.stdout.txt')
  elif key in ['codegraph']:
   add(path,'/'+key,value,'contradicted','implementer声称两个调用点，原reviewer与当前CodeGraph/源码均只一个_handle_from_resolution调用点；共享helper可被多路径到达不等于两个直接call site。','REVIEWER_REPORT.md:72; scripts/fetch_filing.py:_handle_from_resolution')
  elif key in ['codegraph_reachability']:
   add(path,'/'+key,value,'supported_scoped','单直接生产call site且消费返回值当前存在；不证明原全部diff审查。','scripts/fetch_filing.py:_handle_from_resolution')
  elif key in ['schema_version','fc_id','mode','reviewer_identity','written_by','written_at_utc']:
   add(path,'/'+key,value,'not_applicable','标识/作者/时间等元数据本身不构成产品通过；身份独立性不由自报字符串证明。','原JSON字段')
  else:
   add(path,'/'+key,value,'historical_only','旧triplet/命令清单/清洁状态/rollback/绑定hash等历史元数据，未将其转换成当前部署或通过；current真值需新证据。','原receipt与REVIEWER_REPORT；tests/receipt_git_history_trusted.stdout.txt')
path=REPO/'TERMINAL_NOTICE.json';p=json.loads(path.read_text(encoding='utf-8'))
for key,value in p.items():
 add(path,'/'+key,value,'superseded' if key in ['covers','superseded_by','status','note'] else 'not_applicable','关闭/接管标识说明旧计划未完整完成；117/117只登记历史，不能消除后续R4已知缺口。','PLANNING_STATUS.md:45–58; root跨仓review')
(HERE/'receipt_ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
print(len(rows))
