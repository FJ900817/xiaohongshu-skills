from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from schema_validation import load_json,validate_instance
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description='Validate a user Task Card.')
 p.add_argument('file',type=Path); p.add_argument('--allow-unapproved',action='store_true'); a=p.parse_args()
 try: obj=load_json(a.file)
 except Exception as e: print(f'FAIL Task Card | $ | cannot read JSON: {e}'); return 1
 errors=validate_instance('task-card.schema.json',obj)
 if not a.allow_unapproved and (obj.get('status')!='approved' or obj.get('approval',{}).get('state')!='approved'): errors.append(('$.approval','Task Card must be human-approved before Keyword/Writing.'))
 for field,reason in errors: print(f'FAIL Task Card | {field} | {reason}')
 if not errors: print('PASS Task Card')
 return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
