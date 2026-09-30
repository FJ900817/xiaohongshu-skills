from __future__ import annotations
import argparse,sys
from pathlib import Path
from schema_validation import load_json,validate_instance
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description='Validate an approved Keyword Plan.'); p.add_argument('file',type=Path); p.add_argument('--task-card',type=Path); p.add_argument('--allow-unapproved',action='store_true'); a=p.parse_args()
 try: obj=load_json(a.file)
 except Exception as e: print(f'FAIL Keyword Plan | $ | cannot read JSON: {e}'); return 1
 errors=validate_instance('keyword-plan.schema.json',obj)
 if sum(k.get('role')=='main' for k in obj.get('keywords',[]))!=1: errors.append(('$.keywords','exactly one main keyword is required'))
 if not a.allow_unapproved and (obj.get('status')!='approved' or obj.get('approval',{}).get('state')!='approved' or any(k.get('approval_state')!='approved' or k.get('status')!='locked' for k in obj.get('keywords',[]))): errors.append(('$.approval','plan and all keyword choices must be human-approved and locked'))
 if a.task_card:
  task=load_json(a.task_card)
  if obj.get('task_id')!=task.get('task_id'): errors.append(('$.task_id','does not match Task Card.task_id'))
 for field,reason in errors: print(f'FAIL Keyword Plan | {field} | {reason}')
 if not errors: print('PASS Keyword Plan')
 return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
