from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]/'filing-fetch'
files=['task_plan.md','findings.md','progress.md','PLANNING_STATUS.md','CHANGELOG.md','SKILL.md','e2e/E2E_DESIGN.md','references/contract-ownership.md','references/identity.md','assurance/fc/FC-903/03_change_contract.md','assurance/fc/FC-903/REVIEWER_REPORT.md']
blocks=[]
for relative in files:
 lines=(REPO/relative).read_text(encoding='utf-8').splitlines(); current=[]; start=0; in_fence=False
 def flush():
  global current,start
  if current:
   text='\n'.join(current)
   if not re.fullmatch(r'[-| :]+',text.strip()):
    blocks.append({'source_file':str(REPO/relative),'relative':relative,'line_start':start,'line_end':start+len(current)-1,'original_text':text,'file_sha256':hashlib.sha256((REPO/relative).read_bytes()).hexdigest()})
   current=[]
 for n,line in enumerate(lines,1):
  if line.startswith('```'):
   if not in_fence:flush();start=n
   current.append(line);in_fence=not in_fence
   if not in_fence:flush()
   continue
  if in_fence:current.append(line);continue
  if not line.strip():flush();continue
  if re.match(r'^\s*(?:#+\s|[-*]\s|\d+\.\s|\|)',line):flush();start=n
  elif not current:start=n
  current.append(line)
 flush()
(HERE/'extracted_blocks.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf-8')
for b in blocks:print(b['relative'],b['line_start'],b['line_end'],b['original_text'].replace('\n',' ')[:120])
print('TOTAL',len(blocks))
