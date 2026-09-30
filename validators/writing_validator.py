from __future__ import annotations
import argparse
from pathlib import Path
from schema_validation import load_json,validate_instance
def main():
 p=argparse.ArgumentParser(description='Validate a Writing Result and locked keyword consumption.'); p.add_argument('file',type=Path); p.add_argument('--task-card',type=Path); p.add_argument('--keyword-plan',type=Path); a=p.parse_args()
 try: obj=load_json(a.file)
 except Exception as e: print(f'FAIL Writing Result | $ | cannot read JSON: {e}'); return 1
 errors=validate_instance('writing-result.schema.json',obj)
 if obj.get('status')!='draft': errors.append(('$.status','new Writing Result must start as draft'))
 if a.task_card:
  task=load_json(a.task_card)
  if task.get('status')!='approved' or task.get('approval',{}).get('state')!='approved': errors.append(('$.task_id','upstream Task Card is not approved'))
  if obj.get('task_id')!=task.get('task_id') or obj.get('note_type')!=task.get('note_type'): errors.append(('$.task_id','does not match Task Card'))
 if a.keyword_plan:
  plan=load_json(a.keyword_plan)
  if plan.get('status')!='approved' or plan.get('approval',{}).get('state')!='approved': errors.append(('$.keyword_plan_ref','Keyword Plan is not approved'))
  if obj.get('keyword_plan_ref')!=plan.get('plan_id'): errors.append(('$.keyword_plan_ref','does not reference supplied Keyword Plan'))
  for k in plan.get('keywords',[]):
   if k.get('approval_state')=='approved' and 'body' in k.get('placement',[]) and k.get('phrase','') not in obj.get('body',''): errors.append(('$.body',f'approved keyword {k.get("keyword_id")} missing; return a Keyword Revision Request instead of changing its role/placement'))
   if k.get('approval_state')=='approved' and 'title' in k.get('placement',[]) and k.get('phrase','') not in obj.get('title',''): errors.append(('$.title',f'approved title placement for {k.get("keyword_id")} missing; request keyword revision'))
 for field,reason in errors: print(f'FAIL Writing Result | {field} | {reason}')
 if not errors: print('PASS Writing Result')
 return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
