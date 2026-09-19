from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
ROOT=Path('C:/Users/郑曾波/Projects/company-wiki')
inventory=json.loads((HERE.parents[1]/'inventory/company-wiki.json').read_text(encoding='utf-8'))
specials=('portfolio-reuse-fix','portfolio-reuse-automatic','core-section-extraction','catalog-space-remediation')
files=[]
for f in inventory['selected']:
 p=f['path'].replace('\\','/')
 if '/' not in p or p.startswith('docs/archive/') or any(p.startswith('docs/plans/'+s+'/') for s in specials):files.append(p)
blocks=[]
for relative in files:
 raw=(ROOT/relative).read_bytes();lines=raw.decode('utf-8-sig').splitlines();current=[];start=0;fence=False
 def flush():
  global current,start
  if current:
   text='\n'.join(current)
   if not re.fullmatch(r'[-| :]+',text.strip()):blocks.append({'source_file':str(ROOT/relative),'relative':relative,'line_start':start,'line_end':start+len(current)-1,'original_text':text,'file_sha256':hashlib.sha256(raw).hexdigest()})
   current=[]
 for n,line in enumerate(lines,1):
  if line.startswith('```'):
   if not fence:flush();start=n
   current.append(line);fence=not fence
   if not fence:flush()
   continue
  if fence:current.append(line);continue
  if not line.strip():flush();continue
  if re.match(r'^\s*(?:#+\s|[-*]\s|\d+\.\s|\|)',line):flush();start=n
  elif not current:start=n
  current.append(line)
 flush()
(HERE/'scope.json').write_text(json.dumps({'files':files,'blocks':blocks},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':len(files),'blocks':len(blocks)},ensure_ascii=False))
